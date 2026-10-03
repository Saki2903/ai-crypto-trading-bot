
import pandas as pd
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    # Percentage change from the previous candle's close
    df["return_pct"] = df["close"].pct_change() * 100

    print("First 10 candles with returns:")
    print(
        df[["timestamp", "close", "return_pct"]]
        .head(10)
        .to_string(index=False)
    )

    valid_returns = df["return_pct"].dropna()

    print("\nReturn summary:")
    print(f"Valid return observations: {len(valid_returns)}")
    print(f"Average hourly return: {valid_returns.mean():.5f}%")
    print(f"Largest hourly gain: {valid_returns.max():.5f}%")
    print(f"Largest hourly loss: {valid_returns.min():.5f}%")

    print("\nNote: These are historical observations, not a profit forecast.")


if __name__ == "__main__":
    main()