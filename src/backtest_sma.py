
import pandas as pd
from pathlib import Path

FEE_RATE = 0.001  # Illustrative 0.1% fee per side


def main():
    project_dir = Path(__file__).resolve().parent.parent
    csv_path = project_dir / "data" / "raw" / "btc_usdt_1h.csv"

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    # Calculate moving averages
    df["SMA_10"] = df["close"].rolling(window=10).mean()
    df["SMA_20"] = df["close"].rolling(window=20).mean()

    previous_sma_10 = df["SMA_10"].shift(1)
    previous_sma_20 = df["SMA_20"].shift(1)

    # Signals are known at candle close
    df["BUY_SIGNAL"] = (
        (previous_sma_10 <= previous_sma_20)
        & (df["SMA_10"] > df["SMA_20"])
    )

    df["SELL_SIGNAL"] = (
        (previous_sma_10 >= previous_sma_20)
        & (df["SMA_10"] < df["SMA_20"])
    )

    # Execute the signal at the next candle's open
    df["BUY_EXECUTION"] = (
        df["BUY_SIGNAL"].shift(1).fillna(False).astype(bool)
    )
    df["SELL_EXECUTION"] = (
        df["SELL_SIGNAL"].shift(1).fillna(False).astype(bool)
    )

    cash = 1.0
    btc = 0.0
    in_position = False
    entries = 0
    equity_values = []

    for row in df.itertuples(index=False):
        if not in_position and row.BUY_EXECUTION:
            btc = cash * (1 - FEE_RATE) / row.open
            cash = 0.0
            in_position = True
            entries += 1

        elif in_position and row.SELL_EXECUTION:
            cash = btc * row.open * (1 - FEE_RATE)
            btc = 0.0
            in_position = False

        equity_values.append(cash + btc * row.close)

    df["STRATEGY_EQUITY"] = equity_values

    # Close any remaining position at the final close
    # and include the exit fee in final equity.
    if in_position:
        final_equity = btc * df["close"].iloc[-1] * (1 - FEE_RATE)
        df.loc[df.index[-1], "STRATEGY_EQUITY"] = final_equity
    else:
        final_equity = df["STRATEGY_EQUITY"].iloc[-1]

    strategy_return = (final_equity - 1.0) * 100

    # Buy-and-hold baseline, including entry and exit fees
    first_open = df["open"].iloc[0]
    last_close = df["close"].iloc[-1]
    buy_hold_equity = (
        (last_close / first_open) * (1 - FEE_RATE) ** 2
    )
    buy_hold_return = (buy_hold_equity - 1.0) * 100

    # Strategy drawdown, including final exit fee if applicable
    running_peak = df["STRATEGY_EQUITY"].cummax()
    drawdown = df["STRATEGY_EQUITY"] / running_peak - 1
    max_drawdown = drawdown.min() * 100

    # Create buy-and-hold equity curve
    df["BUY_HOLD_EQUITY"] = (
        df["close"] / first_open
    ) * (1 - FEE_RATE)

    # Include the final exit fee
    df.loc[df.index[-1], "BUY_HOLD_EQUITY"] *= (1 - FEE_RATE)

    # Save equity data for charting
    equity_path = (
        project_dir / "data" / "processed" / "sma_backtest_equity.csv"
    )

    df[
        ["timestamp", "STRATEGY_EQUITY", "BUY_HOLD_EQUITY"]
    ].to_csv(equity_path, index=False)

    print("Equity data saved to:", equity_path)

    print("SMA Crossover Backtest")
    print("-" * 40)
    print("Candles:", len(df))
    print("Entries executed:", entries)
    print(f"Assumed fee per side: {FEE_RATE * 100:.2f}%")
    print(f"Strategy net return: {strategy_return:.3f}%")
    print(f"Buy-and-hold net return: {buy_hold_return:.3f}%")
    print(f"Strategy max drawdown: {max_drawdown:.3f}%")
    print("Final position:", "LONG" if in_position else "FLAT")
    print("\nEducational backtest only; not a profit forecast.")


if __name__ == "__main__":
    main()
