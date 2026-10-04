
from dataclasses import dataclass
from typing import Literal

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

    def analyze(self, df: pd.DataFrame, symbol: str = "BTC/USDT") -> MarketResearchReport:
        required_columns = {"timestamp", "open", "high", "low", "close", "volume"}
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"Market data is missing columns: {sorted(missing_columns)}"
            )

        if df.empty or len(df) < 2:
            raise ValueError("At least two candles are required.")

        data = df.copy()
        data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
        data = data.sort_values("timestamp").reset_index(drop=True)

        if data[["close", "volume"]].isna().any().any():
            raise ValueError("Close and volume must not contain missing values.")

        if (data["close"] <= 0).any() or (data["volume"] < 0).any():
            raise ValueError("Prices must be positive and volume cannot be negative.")

        latest_price = float(data["close"].iloc[-1])
        previous_price = float(data["close"].iloc[-2])

        hourly_return_pct = (latest_price / previous_price - 1) * 100

        returns = data["close"].pct_change().dropna()
        volatility_pct = float(returns.std() * 100) if len(returns) > 1 else 0.0

        # Initial transparent market classification, not an autonomous trade rule.
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
