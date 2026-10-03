
import ccxt
import pandas as pd
from pathlib import Path


def main():
    exchange = ccxt.binance({"enableRateLimit": True})

    symbol = "BTC/USDT"
    timeframe = "1h"
    limit = 100

    print(f"Downloading {limit} candles for {symbol}...")

    candles = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit,
    )

    columns = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    df = pd.DataFrame(candles, columns=columns)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], unit="ms", utc=True
    )

    output_path = (
        Path(__file__).resolve().parent.parent
        / "data" / "raw" / "btc_usdt_1h.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Rows downloaded: {len(df)}")
    print(f"Saved to: {output_path}")
    print(df.head(3).to_string(index=False))
    print("\nLatest candles:")
    print(df.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()