
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "order_state.db"

ORDER_STATUSES = (
    "PENDING",
    "OPEN",
    "PARTIALLY_FILLED",
    "FILLED",
    "CANCELED",
    "REJECTED",
    "UNKNOWN",
)

# Only these status transitions are allowed.
STATUS_TRANSITIONS = {
    "PENDING": {
        "OPEN", "PARTIALLY_FILLED", "FILLED",
        "CANCELED", "REJECTED", "UNKNOWN",
    },
    "OPEN": {
        "PARTIALLY_FILLED", "FILLED", "CANCELED", "UNKNOWN",
    },
    "PARTIALLY_FILLED": {"FILLED", "CANCELED", "UNKNOWN"},
    "FILLED": set(),
    "CANCELED": set(),
    "REJECTED": set(),
    "UNKNOWN": {
        "OPEN", "PARTIALLY_FILLED", "FILLED",
        "CANCELED", "REJECTED",
    },
}


def _validate_finite_number(value, field_name, *, allow_zero=False):
    """Validate a finite numeric value; booleans are not numbers here."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a finite number")

    try:
        finite = math.isfinite(value)
    except (OverflowError, TypeError):
        finite = False

    if not finite:
        raise ValueError(f"{field_name} must be a finite number")

    if value < 0 or (value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{field_name} must be {qualifier}")


class OrderStateStore:
    """Persist simulated order state in a local SQLite database."""

    def __init__(self, database_path=DATABASE_PATH):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        """Open a database connection and always close it afterward."""
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self):
        """Create the table and migrate older databases safely."""
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    local_order_id TEXT PRIMARY KEY,
                    client_order_id TEXT UNIQUE NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL
                        CHECK (side IN ('BUY', 'SELL')),
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    filled_quantity REAL NOT NULL DEFAULT 0
                        CHECK (
                            filled_quantity >= 0
                            AND filled_quantity <= quantity
                        ),
                    status TEXT NOT NULL
                        CHECK (
                            status IN (
                                'PENDING', 'OPEN', 'PARTIALLY_FILLED',
                                'FILLED', 'CANCELED', 'REJECTED', 'UNKNOWN'
                            )
                        ),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(orders)"
                ).fetchall()
            }

            # Existing databases may not have this column yet.
            if "filled_quantity" not in columns:
                connection.execute(
                    """
                    ALTER TABLE orders
                    ADD COLUMN filled_quantity REAL NOT NULL DEFAULT 0
                    CHECK (
                        filled_quantity >= 0
                        AND filled_quantity <= quantity
                    )
                    """
                )

    def save_order(
        self,
        local_order_id,
        client_order_id,
        symbol,
        side,
        quantity,
        status="PENDING",
    ):
        """Save a new order. Duplicate IDs are rejected by SQLite."""
        for field_name, value in (
            ("local_order_id", local_order_id),
            ("client_order_id", client_order_id),
            ("symbol", symbol),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        if not isinstance(status, str) or status not in ORDER_STATUSES:
            raise ValueError("Invalid order status")

        _validate_finite_number(quantity, "quantity")

        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO orders (
                    local_order_id,
                    client_order_id,
                    symbol,
                    side,
                    quantity,
                    filled_quantity,
                    status
                )
                VALUES (?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    local_order_id,
                    client_order_id,
                    symbol,
                    side,
                    quantity,
                    status,
                ),
            )

    def update_order_status(self, local_order_id, new_status):
        """Change status only through permitted transitions."""
        if not isinstance(new_status, str) or new_status not in ORDER_STATUSES:
            raise ValueError("Invalid order status")

        with self._connection() as connection:
            row = connection.execute(
                "SELECT status FROM orders WHERE local_order_id = ?",
                (local_order_id,),
            ).fetchone()

            if row is None:
                raise ValueError("Order not found")

            current_status = row["status"]

            if new_status == current_status:
                return

            if new_status not in STATUS_TRANSITIONS[current_status]:
                raise ValueError(
                    f"Invalid status transition: "
                    f"{current_status} -> {new_status}"
                )

            connection.execute(
                """
                UPDATE orders
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE local_order_id = ?
                """,
                (new_status, local_order_id),
            )

    def update_filled_quantity(self, local_order_id, filled_quantity):
        """Set cumulative filled quantity without allowing it to decrease."""
        _validate_finite_number(
            filled_quantity,
            "filled_quantity",
            allow_zero=True,
        )

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT quantity, filled_quantity, status
                FROM orders
                WHERE local_order_id = ?
                """,
                (local_order_id,),
            ).fetchone()

            if row is None:
                raise ValueError("Order not found")

            total_quantity = row["quantity"]
            previous_filled = row["filled_quantity"]
            current_status = row["status"]

            if filled_quantity < previous_filled:
                raise ValueError("filled_quantity cannot decrease")

            if filled_quantity > total_quantity:
                raise ValueError(
                    "filled_quantity cannot exceed order quantity"
                )

            if filled_quantity == previous_filled:
                return

            if current_status in ("FILLED", "CANCELED", "REJECTED"):
                raise ValueError(
                    f"Cannot update fills for {current_status} order"
                )

            if filled_quantity == total_quantity:
                new_status = "FILLED"
            elif filled_quantity > 0:
                new_status = "PARTIALLY_FILLED"
            else:
                new_status = current_status

            if (
                new_status != current_status
                and new_status not in STATUS_TRANSITIONS[current_status]
            ):
                raise ValueError(
                    f"Invalid status transition: "
                    f"{current_status} -> {new_status}"
                )

            connection.execute(
                """
                UPDATE orders
                SET filled_quantity = ?,
                    status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE local_order_id = ?
                """,
                (filled_quantity, new_status, local_order_id),
            )

    def get_order(self, local_order_id):
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM orders WHERE local_order_id = ?",
                (local_order_id,),
            ).fetchone()

        return dict(row) if row else None

    def list_orders(self):
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM orders
                ORDER BY created_at, local_order_id
                """
            ).fetchall()

        return [dict(row) for row in rows]
