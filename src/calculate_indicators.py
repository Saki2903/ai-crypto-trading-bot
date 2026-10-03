
import pandas as pd
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    # Calculate Simple Moving Averages
    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["SMA_20"] = df["close"].rolling(window=20).mean()

    print("BTC/USDT — Moving Average Analysis")
    print("-" * 45)

    print(
        df[["timestamp", "close", "SMA_10", "SMA_20"]]
        .tail(10)
        .to_string(index=False)
    )

    print("\nIndicator validation:")
    print("Total candles:", len(df))
    print("SMA_10 available:", int(df["SMA_10"].notna().sum()))
    print("SMA_20 available:", int(df["SMA_20"].notna().sum()))

    print("\nEducational analysis only; not a trading signal.")


if __name__ == "__main__":
    main()