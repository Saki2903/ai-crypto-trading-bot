
import pandas as pd
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path)

    # Calculate hourly percentage returns
    returns = df["close"].pct_change() * 100
    returns = returns.dropna()

    
    positive_hours = (returns > 0).sum()
    negative_hours = (returns < 0).sum()
    zero_hours = (returns == 0).sum()

    print("\nReturn Direction Analysis")
    print("-" * 40)
    print(f"Positive hours: {positive_hours}")
    print(f"Negative hours: {negative_hours}")
    print(f"Zero-return hours: {zero_hours}")
    print(f"Total observations: {len(returns)}")
    print("BTC/USDT — Hourly Return Statistics")
    print("-" * 40)
    print(f"Number of observations: {len(returns)}")
    print(f"Mean return: {returns.mean():.5f}%")
    print(f"Median return: {returns.median():.5f}%")
    print(f"Standard deviation: {returns.std():.5f}%")
    print(f"Minimum return: {returns.min():.5f}%")
    print(f"Maximum return: {returns.max():.5f}%")

    print("\nEducational analysis only; not a trading signal.")


if __name__ == "__main__":
    main()