
import math
import sqlite3
from contextlib import contextmanager
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "portfolio.db"


class PortfolioLedger:
    """Track simulated BTC and USDT balances and deduplicate fills."""

    def __init__(self, database_path=DATABASE_PATH, initial_usdt=1000.0):
        if (
            isinstance(initial_usdt, bool)
            or not isinstance(initial_usdt, (int, float))
            or not math.isfinite(initial_usdt)
            or initial_usdt < 0
        ):
            raise ValueError(
                "initial_usdt must be a finite non-negative number"
            )

        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database(initial_usdt)

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self, initial_usdt):
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS balances (
                    asset TEXT PRIMARY KEY,
                    amount REAL NOT NULL CHECK (amount >= 0)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS applied_fills (
                    fill_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
                    quantity REAL NOT NULL CHECK (quantity > 0),
                    price REAL NOT NULL CHECK (price > 0),
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Initialize balances only when they do not already exist.
            connection.execute(
                """
                INSERT OR IGNORE INTO balances (asset, amount)
                VALUES ('USDT', ?)
                """,
                (initial_usdt,),
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO balances (asset, amount)
                VALUES ('BTC', 0)
                """
            )

    def get_applied_fill(self, fill_id):
        """Return an applied fill record, or None if it does not exist."""
        if not isinstance(fill_id, str) or not fill_id.strip():
            raise ValueError("fill_id must be a non-empty string")

        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT fill_id, symbol, side, quantity, price, applied_at
                FROM applied_fills
                WHERE fill_id = ?
                """,
                (fill_id.strip(),),
            ).fetchone()

        return dict(row) if row is not None else None

    def has_fill(self, fill_id):
        """Return whether a fill ID has already been applied."""
        if not isinstance(fill_id, str) or not fill_id.strip():
            raise ValueError("fill_id must be a non-empty string")

        with self._connection() as connection:
            row = connection.execute(
                "SELECT 1 FROM applied_fills WHERE fill_id = ?",
                (fill_id.strip(),),
            ).fetchone()

        return row is not None

    def get_balances(self):
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT asset, amount FROM balances ORDER BY asset"
            ).fetchall()

        return {row["asset"]: row["amount"] for row in rows}

    def apply_fill(self, fill_id, symbol, side, quantity, price):
        """Apply one simulated BTC/USDT fill exactly once."""

        if not isinstance(fill_id, str) or not fill_id.strip():
            raise ValueError("fill_id must be a non-empty string")

        if symbol != "BTC/USDT":
            raise ValueError("Only BTC/USDT is supported")

        if side not in ("BUY", "SELL"):
            raise ValueError("side must be BUY or SELL")

        for name, value in (("quantity", quantity), ("price", price)):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(
                    f"{name} must be a finite positive number"
                )

        quote_amount = quantity * price
        if not math.isfinite(quote_amount):
            raise ValueError("Fill value must be finite")

        # All database changes for this fill are in one transaction.
        with self._connection() as connection:
            existing = connection.execute(
                """
                SELECT symbol, side, quantity, price
                FROM applied_fills
                WHERE fill_id = ?
                """,
                (fill_id,),
            ).fetchone()

            # A repeated ID is safe only if its data matches the original.
            if existing is not None:
                same_fill = (
                    existing["symbol"] == symbol
                    and existing["side"] == side
                    and math.isclose(
                        existing["quantity"],
                        quantity,
                        rel_tol=1e-12,
                    )
                    and math.isclose(
                        existing["price"],
                        price,
                        rel_tol=1e-12,
                    )
                )

                if not same_fill:
                    raise ValueError(
                        "Conflicting data for an already-applied fill_id"
                    )

                # Identical duplicate: do not change balances again.
                return False

            rows = connection.execute(
                "SELECT asset, amount FROM balances"
            ).fetchall()

            balances = {
                row["asset"]: row["amount"] for row in rows
            }

            usdt = balances.get("USDT", 0.0)
            btc = balances.get("BTC", 0.0)

            if side == "BUY":
                if usdt < quote_amount:
                    raise ValueError(
                        "Insufficient simulated USDT balance"
                    )

                new_usdt = usdt - quote_amount
                new_btc = btc + quantity

            else:  # SELL
                if btc < quantity:
                    raise ValueError(
                        "Insufficient simulated BTC balance"
                    )

                new_usdt = usdt + quote_amount
                new_btc = btc - quantity

            if not math.isfinite(new_usdt) or not math.isfinite(new_btc):
                raise ValueError("Resulting balance must be finite")

            if new_usdt < 0 or new_btc < 0:
                raise ValueError("Resulting balance cannot be negative")

            connection.execute(
                "UPDATE balances SET amount = ? WHERE asset = 'USDT'",
                (new_usdt,),
            )
            connection.execute(
                "UPDATE balances SET amount = ? WHERE asset = 'BTC'",
                (new_btc,),
            )
            connection.execute(
                """
                INSERT INTO applied_fills
                    (fill_id, symbol, side, quantity, price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (fill_id, symbol, side, quantity, price),
            )

        return True
