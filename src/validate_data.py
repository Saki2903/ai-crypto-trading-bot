
import pandas as pd
from pathlib import Path


def main():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "data" / "raw" / "btc_usdt_1h.csv"
    )

    df = pd.read_csv(file_path, parse_dates=["timestamp"])

    print("=== BASIC DATA CHECKS ===")
    print("Total rows:", len(df))
    print("Duplicate timestamps:", df["timestamp"].duplicated().sum())

    print("\nMissing values per column:")
    print(df.isna().sum().to_string())

    price_columns = ["open", "high", "low", "close"]

    print("\nInvalid non-positive prices:")
    print((df[price_columns] <= 0).sum().to_string())

    invalid_ohlc = (
        (df["high"] < df[["open", "close", "low"]].max(axis=1))
        | (df["low"] > df[["open", "close", "high"]].min(axis=1))
    )

    print("\nOHLC consistency errors:", int(invalid_ohlc.sum()))

    print("\n=== TIME CHECKS ===")
    print(
        "Timestamp order:",
        "Ascending" if df["timestamp"].is_monotonic_increasing
        else "NOT ascending"
    )

    time_gaps = df["timestamp"].diff().dropna()
    hourly_gaps = (time_gaps != pd.Timedelta(hours=1)).sum()
    print("Unexpected hourly intervals:", int(hourly_gaps))

    print("\n=== VOLUME CHECKS ===")
    print("Negative volume rows:", int((df["volume"] < 0).sum()))
    print("Zero volume rows:", int((df["volume"] == 0).sum()))
    print("Missing volume values:", int(df["volume"].isna().sum()))


if __name__ == "__main__":
    main()