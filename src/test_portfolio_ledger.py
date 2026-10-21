
import tempfile
from pathlib import Path

from src.portfolio_ledger import PortfolioLedger


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "test_portfolio.db"
        ledger = PortfolioLedger(database_path, initial_usdt=1000.0)

        balances = ledger.get_balances()
        assert balances["USDT"] == 1000.0
        assert balances["BTC"] == 0.0
        print("PASS: initial simulated balances.")

        applied = ledger.apply_fill(
            fill_id="fill-buy-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.01,
            price=100.0,
        )
        assert applied is True

        balances = ledger.get_balances()
        assert abs(balances["USDT"] - 999.0) < 1e-9
        assert abs(balances["BTC"] - 0.01) < 1e-9
        print("PASS: BUY fill updates balances.")

        # A duplicate fill must not change balances again.
        applied = ledger.apply_fill(
            fill_id="fill-buy-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.01,
            price=100.0,
        )
        assert applied is False

        balances = ledger.get_balances()
        assert abs(balances["USDT"] - 999.0) < 1e-9
        assert abs(balances["BTC"] - 0.01) < 1e-9
        print("PASS: duplicate fill ignored.")

        assert ledger.has_fill("fill-buy-001") is True
        assert ledger.has_fill("unknown-fill") is False
        print("PASS: has_fill detects existing and missing fills.")
        # Reusing a fill ID with different data must be rejected.
        balances_before_conflict = ledger.get_balances()

        try:
            ledger.apply_fill(
                fill_id="fill-buy-001",
                symbol="BTC/USDT",
                side="BUY",
                quantity=0.02,
                price=100.0,
            )
        except ValueError as exc:
            assert "Conflicting data" in str(exc)
            assert ledger.get_balances() == balances_before_conflict
            print("PASS: conflicting duplicate fill rejected.")
        else:
            raise AssertionError(
                "Conflicting duplicate fill should have been rejected"
            )
        # Sell half of the simulated BTC.
        ledger.apply_fill(
            fill_id="fill-sell-001",
            symbol="BTC/USDT",
            side="SELL",
            quantity=0.005,
            price=120.0,
        )

        balances = ledger.get_balances()
        assert abs(balances["USDT"] - 999.6) < 1e-9
        assert abs(balances["BTC"] - 0.005) < 1e-9
        print("PASS: SELL fill updates balances.")

        # Verify balances survive creating a new ledger instance.
        restarted_ledger = PortfolioLedger(
            database_path, initial_usdt=1000.0
        )
        recovered_balances = restarted_ledger.get_balances()

        assert abs(recovered_balances["USDT"] - 999.6) < 1e-9
        assert abs(recovered_balances["BTC"] - 0.005) < 1e-9

        print("PASS: portfolio balances recovered after restart.")


        # Selling more BTC than available must fail.
        try:
            ledger.apply_fill(
                fill_id="fill-sell-002",
                symbol="BTC/USDT",
                side="SELL",
                quantity=0.01,
                price=100.0,
            )
        except ValueError:
            print("PASS: insufficient BTC balance rejected.")
        else:
            raise AssertionError("Overselling BTC was incorrectly accepted.")

    print("\nAll portfolio ledger tests passed.")
    print("Temporary database used; no exchange API request or trade.")

def test_invalid_fill_inputs():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "portfolio_test.db"
        ledger = PortfolioLedger(db_path, initial_usdt=1000.0)

        invalid_cases = [
            ("bad-nan", "BTC/USDT", "BUY", float("nan"), 100.0),
            ("bad-inf", "BTC/USDT", "BUY", 0.01, float("inf")),
            ("bad-zero", "BTC/USDT", "BUY", 0.0, 100.0),
            ("bad-symbol", "ETH/USDT", "BUY", 0.01, 100.0),
        ]

        for fill_id, symbol, side, quantity, price in invalid_cases:
            try:
                ledger.apply_fill(
                    fill_id=fill_id,
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=price,
                )
            except ValueError:
                print(f"PASS: invalid fill rejected ({fill_id}).")
            else:
                raise AssertionError(
                    f"Invalid fill was accepted: {fill_id}"
                )


if __name__ == "__main__":
    main()
    test_invalid_fill_inputs()

