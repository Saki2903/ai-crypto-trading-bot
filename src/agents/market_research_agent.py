
from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


@dataclass
class MarketResearchReport:
    symbol: str
    latest_price: float
    hourly_return_pct: float
    volatility_pct: float
    market_view: Literal["BULLISH", "BEARISH", "NEUTRAL"]
    evidence: list[str]


class MarketResearchAgent:
    """Analyses market data and reports evidence without placing trades."""

    def analyze(
        self,
        df: pd.DataFrame,
        symbol: str = "BTC/USDT",
        timeframe: str = "1h",
    ) -> MarketResearchReport:
        # 1. Validate required columns and minimum data.
        required_columns = {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Market data is missing columns: {sorted(missing_columns)}"
            )

        if df.empty or len(df) < 2:
            raise ValueError("At least two candles are required.")

        data = df.copy()

        # 2. Parse timestamps once and reject invalid or missing values.
        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            format="mixed",
            utc=True,
            errors="raise",
        )

        if data["timestamp"].isna().any():
            raise ValueError("Timestamps must not contain missing values.")

        if data["timestamp"].duplicated().any():
            raise ValueError("Duplicate timestamps are not allowed.")

        # 3. Validate timeframe.
        timeframe_durations = {
            "1m": pd.Timedelta(minutes=1),
            "5m": pd.Timedelta(minutes=5),
            "15m": pd.Timedelta(minutes=15),
            "30m": pd.Timedelta(minutes=30),
            "1h": pd.Timedelta(hours=1),
            "4h": pd.Timedelta(hours=4),
            "1d": pd.Timedelta(days=1),
        }

        if timeframe not in timeframe_durations:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        # 4. Sort timestamps before checking candle intervals.
        data = data.sort_values("timestamp").reset_index(drop=True)

        expected_interval = timeframe_durations[timeframe]
        actual_intervals = data["timestamp"].diff().dropna()

        if not actual_intervals.eq(expected_interval).all():
            raise ValueError(
                f"Unexpected candle interval; expected {timeframe}."
            )

        # 5. Reject missing, infinite, or invalid market values.
        price_columns = ["open", "high", "low", "close"]
        numeric_columns = price_columns + ["volume"]

        if data[numeric_columns].isna().any().any():
            raise ValueError("OHLC prices and volume must not contain missing values.")

        try:
            numeric_values = data[numeric_columns].to_numpy(dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "OHLC prices and volume must contain numeric values."
            ) from exc

        if not np.isfinite(numeric_values).all():
            raise ValueError(
                "OHLC prices and volume must contain only finite values."
            )

        if (data[price_columns] <= 0).any().any():
            raise ValueError("OHLC prices must be positive.")

        if (data["volume"] < 0).any():
            raise ValueError("Volume cannot be negative.")

        # 6. Validate OHLC candle consistency.
        if (
            (data["high"] < data[["open", "low", "close"]].max(axis=1)).any()
            or (
                data["low"]
                > data[["open", "high", "close"]].min(axis=1)
            ).any()
        ):
            raise ValueError("Invalid OHLC candle: high or low is inconsistent.")

        # 7. Calculate latest return and historical volatility.
        latest_price = float(data["close"].iloc[-1])
        previous_price = float(data["close"].iloc[-2])

        hourly_return_pct = (latest_price / previous_price - 1) * 100

        returns = data["close"].pct_change().dropna()
        volatility_pct = (
            float(returns.std() * 100)
            if len(returns) > 1
            else 0.0
        )

        # 8. Provide a transparent market classification.
        # This classification is research evidence, not a trading instruction.
        if hourly_return_pct > 0.25:
            market_view = "BULLISH"
        elif hourly_return_pct < -0.25:
            market_view = "BEARISH"
        else:
            market_view = "NEUTRAL"

        evidence = [
            f"Latest candle close: {latest_price:.2f}",
            f"Most recent candle return: {hourly_return_pct:.3f}%",
            f"Historical hourly return volatility: {volatility_pct:.3f}%",
            f"Candles analysed: {len(data)}",
        ]

        return MarketResearchReport(
            symbol=symbol,
            latest_price=latest_price,
            hourly_return_pct=hourly_return_pct,
            volatility_pct=volatility_pct,
            market_view=market_view,
            evidence=evidence,
        )
