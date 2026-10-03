
import pandas as pd
from pathlib import Path


def main():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "data" / "raw" / "btc_usdt_1h.csv"
    )

    df = pd.read_csv(file_path, parse_dates=["timestamp"])

    print("Total rows:", len(df))
    print("Duplicate timestamps:", df["timestamp"].duplicated().sum())
    print("Missing values per column:")
    print(df.isna().sum().to_string())

    price_columns = ["open", "high", "low", "close"]

    print("\nInvalid non-positive prices:")
    print((df[price_columns] <= 0).sum().to_string())

    print("\nOHLC consistency errors:")
    invalid_ohlc = (
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        | (df["low"] > df[["open", "close", "high"]].min(axis=1))
    )
    print(int(invalid_ohlc.sum()))

    print("\nTimestamp order:", "Ascending" if df["timestamp"].is_monotonic_increasing else "NOT ascending")


if __name__ == "__main__":
    main()