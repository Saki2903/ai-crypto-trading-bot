
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent

    csv_path = (
        project_dir
        / "data"
        / "processed"
        / "sma_backtest_equity.csv"
    )

    output_path = (
        project_dir
        / "data"
        / "processed"
        / "sma_equity_curve.png"
    )

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    plt.figure(figsize=(12, 6))

    plt.plot(
        df["timestamp"],
        df["STRATEGY_EQUITY"],
        label="SMA Strategy",
    )

    plt.plot(
        df["timestamp"],
        df["BUY_HOLD_EQUITY"],
        label="Buy and Hold",
    )

    plt.title("Strategy vs Buy-and-Hold Equity Curve")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Portfolio Value (Initial Capital = 1.0)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(output_path, dpi=150)
    print("Chart saved to:", output_path)

    plt.show()


if __name__ == "__main__":
    main()
