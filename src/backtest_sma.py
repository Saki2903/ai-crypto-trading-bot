
import pandas as pd
from pathlib import Path


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    # Calculate indicators
    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["SMA_20"] = df["close"].rolling(window=20).mean()

    # Previous candle's indicator values
    df["SMA_10_PREV"] = df["SMA_10"].shift(1)
    df["SMA_20_PREV"] = df["SMA_20"].shift(1)

    # Bullish crossover: enter signal
    df["BUY_SIGNAL"] = (
        (df["SMA_10_PREV"] <= df["SMA_20_PREV"])
        & (df["SMA_10"] > df["SMA_20"])
    )

    # Bearish crossover: exit signal
    df["SELL_SIGNAL"] = (
        (df["SMA_10_PREV"] >= df["SMA_20_PREV"])
        & (df["SMA_10"] < df["SMA_20"])
    )

    print("SMA Crossover Signal Analysis")
    print("-" * 45)

    signals = df.loc[
        df["BUY_SIGNAL"] | df["SELL_SIGNAL"],
        ["timestamp", "close", "SMA_10", "SMA_20",
         "BUY_SIGNAL", "SELL_SIGNAL"]
    ]

    if signals.empty:
        print("No crossover signals found in this dataset.")
    else:
        print(signals.to_string(index=False))

    print("\nSignal summary:")
    print("Total candles:", len(df))
    print("Buy signals:", int(df["BUY_SIGNAL"].sum()))
    print("Sell signals:", int(df["SELL_SIGNAL"].sum()))

    print("\nResearch only. No orders are placed.")


if __name__ == "__main__":
    main()