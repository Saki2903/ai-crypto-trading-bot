import sqlite3
import tempfile
from pathlib import Path
import time

from src.order_state_store import OrderStateStore


def main():
    # Use a temporary database so every test run starts clean.
    with tempfile.TemporaryDirectory() as temp_dir:
        database_path = Path(temp_dir) / "test_orders.db"
        store = OrderStateStore(database_path)

        store.save_order(
            local_order_id="test-order-001",
            client_order_id="test-client-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.001,
            status="PENDING",
        )

        print("PASS: simulated order saved.")

        # Test partial fills using a separate order.
        store.save_order(
            local_order_id="partial-test-001",
            client_order_id="partial-client-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.001,
            status="OPEN",
        )

        store.update_filled_quantity("partial-test-001", 0.0004)
        partial_order = store.get_order("partial-test-001")

        assert partial_order["filled_quantity"] == 0.0004
        assert partial_order["status"] == "PARTIALLY_FILLED"

        print("PASS: partial fill quantity and status updated.")
        # Verify partial-fill data survives a store restart.
        restarted_partial_store = OrderStateStore(database_path)
        recovered_partial = restarted_partial_store.get_order(
            "partial-test-001"
        )

        assert recovered_partial is not None
        assert recovered_partial["filled_quantity"] == 0.0004
        assert recovered_partial["status"] == "PARTIALLY_FILLED"

        print("PASS: partial-fill state recovered after restart.")

        # Reject filled quantity greater than total order quantity.
        try:
            store.update_filled_quantity("partial-test-001", 0.002)
        except ValueError:
            print("PASS: overfilled quantity rejected.")
        else:
            raise AssertionError(
                "Overfilled quantity was incorrectly accepted."
            )

        # Reject a filled quantity smaller than the previous fill.
        try:
            store.update_filled_quantity("partial-test-001", 0.0002)
        except ValueError:
            print("PASS: decreasing filled quantity rejected.")
        else:
            raise AssertionError(
                "Decreasing filled quantity was incorrectly accepted."
            )


        # Create a new store instance using the same database.
        restarted_store = OrderStateStore(database_path)
        order = restarted_store.get_order("test-order-001")

        assert order is not None, "Order was not recovered."
        assert order["client_order_id"] == "test-client-001"
        assert order["symbol"] == "BTC/USDT"
        assert order["status"] == "PENDING"
        assert order["side"] == "BUY"
        assert order["quantity"] == 0.001
        print("PASS: order recovered from the same database.")

                # Verify order status can be updated.
        restarted_store.update_order_status(
            "test-order-001", "OPEN"
        )

        updated_order = restarted_store.get_order("test-order-001")

        assert updated_order["status"] == "OPEN"
        print("PASS: order status updated.")


        # Verify updated_at changes when order status changes.
        order_before = restarted_store.get_order("test-order-001")
        timestamp_before = order_before["updated_at"]

        time.sleep(1.1)

        restarted_store.update_order_status(
            "test-order-001", "PARTIALLY_FILLED"
        )

        order_after = restarted_store.get_order("test-order-001")
        timestamp_after = order_after["updated_at"]

        assert timestamp_after > timestamp_before, (
            "updated_at did not change after status update."
        )
        print("PASS: updated_at changed after status update.")

        
        # Verify a filled order cannot return to OPEN.
        restarted_store.update_order_status(
            "test-order-001", "FILLED"
        )

        try:
            restarted_store.update_order_status(
                "test-order-001", "OPEN"
            )
        except ValueError:
            print("PASS: FILLED order cannot be reopened.")
        else:
            raise AssertionError(
                "FILLED order was incorrectly reopened."
            )

        # Verify invalid status is rejected.
        try:
            restarted_store.update_order_status(
                "test-order-001", "INVALID_STATUS"
            )
        except ValueError:
            print("PASS: invalid update status rejected.")
        else:
            raise AssertionError(
                "Invalid update status was incorrectly accepted."
            )

        # Verify missing order ID is rejected.
        try:
            restarted_store.update_order_status(
                "missing-order-001", "OPEN"
            )
        except ValueError:
            print("PASS: missing order ID rejected.")
        else:
            raise AssertionError(
                "Missing order ID was incorrectly accepted."
            )
        
        # Verify duplicate client order IDs are rejected.
        restarted_store.save_order(
            local_order_id="duplicate-test-001",
            client_order_id="duplicate-client-001",
            symbol="BTC/USDT",
            side="BUY",
            quantity=0.001,
            status="PENDING",
        )

        try:
            restarted_store.save_order(
                local_order_id="duplicate-test-002",
                client_order_id="duplicate-client-001",
                symbol="BTC/USDT",
                side="BUY",
                quantity=0.001,
                status="PENDING",
            )
        except sqlite3.IntegrityError:
            print("PASS: duplicate client order ID rejected.")
        else:
            raise AssertionError(
                "Duplicate client order ID was incorrectly accepted."
            )
        # Reject invalid quantities.
        for quantity in [0, -1, float("nan"), float("inf"), True]:
            try:
                restarted_store.save_order(
                    local_order_id=f"invalid-qty-{quantity}",
                    client_order_id=f"invalid-client-{quantity}",
                    symbol="BTC/USDT",
                    side="BUY",
                    quantity=quantity,
                )
            except (ValueError, sqlite3.IntegrityError):
                print(f"PASS: invalid quantity {quantity!r} rejected.")
            else:
                raise AssertionError(
                    f"Invalid quantity was accepted: {quantity!r}"
                )

        # Reject invalid order status.
        try:
            restarted_store.save_order(
                local_order_id="invalid-status-001",
                client_order_id="invalid-status-client-001",
                symbol="BTC/USDT",
                side="BUY",
                quantity=0.001,
                status="UNKNOWN_STATUS",
            )
        except ValueError:
            print("PASS: invalid order status rejected.")
        else:
            raise AssertionError("Invalid order status was accepted.")
    print("\nAll order state store tests passed.")
    print("No exchange API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
 