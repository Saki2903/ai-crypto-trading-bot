
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"
    chart_path = project_dir / "data" / "processed" / "btc_usdt_1h_close.png"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp"], df["close"], label="BTC/USDT Close")
    plt.title("BTC/USDT — 1-Hour Closing Price")
    plt.xlabel("Timestamp (UTC)")
    plt.ylabel("Price (USDT)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=30)
    plt.tight_layout()

    plt.savefig(chart_path, dpi=150)
    print(f"Chart saved to: {chart_path}")

    plt.show()


if __name__ == "__main__":
    main()