"""Temporary-database tests for safe fill recovery inspection."""

import tempfile
from pathlib import Path

from src.fill_processor import FillProcessor
from src.order_state_store import OrderStateStore
from src.portfolio_ledger import PortfolioLedger


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        journal = FillProcessor(root / "journal.db")
        ledger = PortfolioLedger(
            root / "portfolio.db",
            initial_usdt=1000.0,
        )
        orders = OrderStateStore(root / "orders.db")

        # Create one consistent simulated order and fill.
        orders.save_order(
            local_order_id="order-recovery-001",
            client_order_id="client-recovery-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.01,
            status="OPEN",
        )
        journal.record_fill(
            "fill-recovery-001",
            "order-recovery-001",
            "BTC/USDT",
            "BUY",
            0.01,
            60000.0,
        )
        assert journal.mark_processing("fill-recovery-001") is True
        assert ledger.apply_fill(
            "fill-recovery-001",
            "BTC/USDT",
            "BUY",
            0.01,
            60000.0,
        ) is True
        orders.update_filled_quantity("order-recovery-001", 0.01)

        result = journal.inspect_recovery(
            "fill-recovery-001", ledger, orders
        )
        assert result == "ALREADY_APPLIED"
        print("PASS: matching applied fill identified.")

        # Missing ledger fill must remain unresolved without mutation.
        journal.record_fill(
            "fill-recovery-missing",
            "order-recovery-001",
            "BTC/USDT",
            "BUY",
            0.001,
            61000.0,
        )
        assert journal.mark_processing("fill-recovery-missing") is True

        balances_before = ledger.get_balances()
        event_before = journal.get_fill("fill-recovery-missing")

        result = journal.inspect_recovery(
            "fill-recovery-missing", ledger, orders
        )

        assert result == "UNRESOLVED"
        assert ledger.get_balances() == balances_before
        assert journal.get_fill("fill-recovery-missing") == event_before
        print("PASS: missing ledger fill remains unresolved without mutation.")

        # Inconsistent order state must remain unresolved.
        orders.save_order(
            local_order_id="order-recovery-inconsistent",
            client_order_id="client-recovery-inconsistent",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.01,
            status="OPEN",
        )
        journal.record_fill(
            "fill-recovery-inconsistent",
            "order-recovery-inconsistent",
            "BTC/USDT",
            "BUY",
            0.005,
            62000.0,
        )
        assert journal.mark_processing("fill-recovery-inconsistent") is True

        balances_before = ledger.get_balances()
        event_before = journal.get_fill("fill-recovery-inconsistent")

        result = journal.inspect_recovery(
            "fill-recovery-inconsistent", ledger, orders
        )

        assert result == "UNRESOLVED"
        assert ledger.get_balances() == balances_before
        assert journal.get_fill("fill-recovery-inconsistent") == event_before
        print("PASS: inconsistent order state remains unresolved without mutation.")

        # A journal database read failure must fail safely.
        balances_before = ledger.get_balances()
        event_before = journal.get_fill("fill-recovery-001")

        original_get_fill = journal.get_fill

        def simulated_read_failure(fill_id):
            if fill_id == "fill-recovery-001":
                raise OSError("simulated database-read failure")
            return original_get_fill(fill_id)

        journal.get_fill = simulated_read_failure
        try:
            result = journal.inspect_recovery(
                "fill-recovery-001", ledger, orders
            )
        finally:
            journal.get_fill = original_get_fill

        assert result == "UNRESOLVED"
        assert ledger.get_balances() == balances_before
        assert journal.get_fill("fill-recovery-001") == event_before
        print("PASS: database-read failure remains unresolved without mutation.")

        print("No exchange API request or live trade performed.")


if __name__ == "__main__":
    main()
