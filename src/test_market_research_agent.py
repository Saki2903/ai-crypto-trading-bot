
import pandas as pd

from agents.market_research_agent import MarketResearchAgent


def main():
    sample_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01", periods=5, freq="h", tz="UTC"
            ),
            "open": [100, 101, 102, 101, 103],
            "high": [102, 103, 103, 104, 105],
            "low": [99, 100, 101, 100, 102],
            "close": [101, 102, 101, 103, 104],
            "volume": [10, 12, 11, 15, 14],
        }
    )

    agent = MarketResearchAgent()
    report = agent.analyze(sample_data, symbol="BTC/USDT")

    print("=== MARKET RESEARCH REPORT ===")
    print("Symbol:", report.symbol)
    print("Latest price:", report.latest_price)
    print(f"Latest candle return: {report.hourly_return_pct:.3f}%")
    print(f"Historical volatility: {report.volatility_pct:.3f}%")
    print("Market view:", report.market_view)

    print("\nEvidence:")
    for item in report.evidence:
        print("-", item)


if __name__ == "__main__":
    main()

def test_invalid_data():
    agent = MarketResearchAgent()

    # Test 1: Empty DataFrame should be rejected
    try:
        agent.analyze(pd.DataFrame())
    except ValueError as error:
        print("\nPASS: Empty data rejected:", error)
    else:
        raise AssertionError("Empty data was not rejected")

    # Test 2: Missing required columns should be rejected
    try:
        agent.analyze(pd.DataFrame({"close": [100, 101]}))
    except ValueError as error:
        print("PASS: Missing columns rejected:", error)
    else:
        raise AssertionError("Missing columns were not rejected")


test_invalid_data()
