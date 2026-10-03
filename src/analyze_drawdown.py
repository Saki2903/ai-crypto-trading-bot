
import pandas as pd
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    # Calculate the running highest closing price
    df["running_peak"] = df["close"].cummax()

    # Calculate percentage decline from the running peak
    df["drawdown_pct"] = (
        (df["close"] / df["running_peak"]) - 1
    ) * 100

    max_drawdown = df["drawdown_pct"].min()
    worst_row = df.loc[df["drawdown_pct"].idxmin()]

    print("BTC/USDT Historical Price Drawdown")
    print("-" * 40)
    print(f"Rows analyzed: {len(df)}")
    print(f"Maximum drawdown: {max_drawdown:.5f}%")
    print(f"Peak close before worst drawdown: {worst_row['running_peak']:.2f}")
    print(f"Lowest close in worst drawdown: {worst_row['close']:.2f}")
    print(f"Timestamp of lowest close: {worst_row['timestamp']}")

    print("\nNote: Historical price drawdown only.")
    print("This is not a trading strategy or portfolio result.")


if __name__ == "__main__":
    main()