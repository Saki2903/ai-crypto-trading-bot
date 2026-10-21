
import math
import sqlite3
from pathlib import Path


class FillProcessor:
    """Manage a local recovery journal for simulated fill events."""

    VALID_STATUSES = (
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
    )

    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        connection = self._connect()
        try:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS fill_events (
                        fill_id TEXT PRIMARY KEY,
                        local_order_id TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        side TEXT NOT NULL
                            CHECK (side IN ('BUY', 'SELL')),
                        quantity REAL NOT NULL
                            CHECK (quantity > 0),
                        price REAL NOT NULL
                            CHECK (price > 0),
                        status TEXT NOT NULL
                            CHECK (
                                status IN (
                                    'PENDING',
                                    'PROCESSING',
                                    'COMPLETED',
                                    'FAILED'
                                )
                            ),
                        error_message TEXT,
                        created_at TEXT NOT NULL
                            DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL
                            DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        finally:
            connection.close()

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} must be a non-empty string"
            )
        return value.strip()

    @staticmethod
    def _validate_positive_number(value, field_name):
        if isinstance(value, bool):
            raise ValueError(
                f"{field_name} must be a positive finite number"
            )

        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(
                f"{field_name} must be a positive finite number"
            ) from exc

        if not math.isfinite(number) or number <= 0:
            raise ValueError(
                f"{field_name} must be a positive finite number"
            )

        return number

    def record_fill(
        self,
        fill_id,
        local_order_id,
        symbol,
        side,
        quantity,
        price,
    ):
        fill_id = self._validate_text(fill_id, "fill_id")
        local_order_id = self._validate_text(
            local_order_id,
            "local_order_id",
        )
        symbol = self._validate_text(symbol, "symbol")
        side = self._validate_text(side, "side").upper()

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        quantity = self._validate_positive_number(
            quantity,
            "quantity",
        )
        price = self._validate_positive_number(price, "price")

        connection = self._connect()
        try:
            with connection:
                existing = connection.execute(
                    """
                    SELECT
                        local_order_id,
                        symbol,
                        side,
                        quantity,
                        price
                    FROM fill_events
                    WHERE fill_id = ?
                    """,
                    (fill_id,),
                ).fetchone()

                if existing is not None:
                    same_event = (
                        existing["local_order_id"] == local_order_id
                        and existing["symbol"] == symbol
                        and existing["side"] == side
                        and existing["quantity"] == quantity
                        and existing["price"] == price
                    )

                    if not same_event:
                        raise ValueError(
                            "Conflicting data for existing fill_id"
                        )

                    return False

                connection.execute(
                    """
                    INSERT INTO fill_events (
                        fill_id,
                        local_order_id,
                        symbol,
                        side,
                        quantity,
                        price,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
                    """,
                    (
                        fill_id,
                        local_order_id,
                        symbol,
                        side,
                        quantity,
                        price,
                    ),
                )

            return True
        finally:
            connection.close()

    def get_fill(self, fill_id):
        fill_id = self._validate_text(fill_id, "fill_id")

        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT
                    fill_id,
                    local_order_id,
                    symbol,
                    side,
                    quantity,
                    price,
                    status,
                    error_message,
                    created_at,
                    updated_at
                FROM fill_events
                WHERE fill_id = ?
                """,
                (fill_id,),
            ).fetchone()

            if row is None:
                return None

            return dict(row)
        finally:
            connection.close()

    def mark_processing(self, fill_id):
        fill_id = self._validate_text(fill_id, "fill_id")

        connection = self._connect()
        try:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE fill_events
                    SET
                        status = 'PROCESSING',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE fill_id = ?
                      AND status = 'PENDING'
                    """,
                    (fill_id,),
                )
                return cursor.rowcount == 1
        finally:
            connection.close()

    def mark_completed(self, fill_id):
        fill_id = self._validate_text(fill_id, "fill_id")

        connection = self._connect()
        try:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE fill_events
                    SET
                        status = 'COMPLETED',
                        error_message = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE fill_id = ?
                      AND status = 'PROCESSING'
                    """,
                    (fill_id,),
                )
                return cursor.rowcount == 1
        finally:
            connection.close()

    def mark_failed(self, fill_id, error_message):
        fill_id = self._validate_text(fill_id, "fill_id")
        error_message = self._validate_text(
            error_message,
            "error_message",
        )

        connection = self._connect()
        try:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE fill_events
                    SET
                        status = 'FAILED',
                        error_message = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE fill_id = ?
                      AND status = 'PROCESSING'
                    """,
                    (error_message, fill_id),
                )
                return cursor.rowcount == 1
        finally:
            connection.close()

    def inspect_recovery(self, fill_id, ledger, order_store):
        """Inspect recovery state without changing any database."""
        try:
            event = self.get_fill(fill_id)
            if event is None or event["status"] != "PROCESSING":
                return "UNRESOLVED"

            order = order_store.get_order(event["local_order_id"])
            if order is None:
                return "UNRESOLVED"

            if (
                order["symbol"] != event["symbol"]
                or order["side"] != event["side"]
                or order["quantity"] < event["quantity"]
                or order["filled_quantity"] < event["quantity"]
            ):
                return "UNRESOLVED"

            applied = ledger.get_applied_fill(fill_id)
            if applied is None:
                return "UNRESOLVED"

            matches = (
                applied["symbol"] == event["symbol"]
                and applied["side"] == event["side"]
                and applied["quantity"] == event["quantity"]
                and applied["price"] == event["price"]
            )
            if not matches:
                return "UNRESOLVED"

            return "ALREADY_APPLIED"
        except Exception:
            return "UNRESOLVED"

    def list_unresolved_fills(self):
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT
                    fill_id,
                    local_order_id,
                    symbol,
                    side,
                    quantity,
                    price,
                    status,
                    error_message,
                    created_at,
                    updated_at
                FROM fill_events
                WHERE status IN ('PENDING', 'PROCESSING')
                ORDER BY created_at, fill_id
                """
            ).fetchall()

            return [dict(row) for row in rows]
        finally:
            connection.close()
