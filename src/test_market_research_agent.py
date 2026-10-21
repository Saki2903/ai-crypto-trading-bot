
import pandas as pd

from src.agents.market_research_agent import MarketResearchAgent


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

    # Test 3: Missing close value should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01", periods=2, freq="h", tz="UTC"
            ),
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [100, float("nan")],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Missing close value rejected:", error)
    else:
        raise AssertionError("Missing close value was not rejected")
        

    # Test 4: Infinite close price should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01", periods=2, freq="h", tz="UTC"
            ),
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [100, float("inf")],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Infinite close price rejected:", error)
    else:
        raise AssertionError("Infinite close price was not rejected")
     
    # Test 5: Invalid OHLC relationship should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01", periods=2, freq="h", tz="UTC"
            ),
            "open": [100, 101],
            "high": [102, 102],
            "low": [99, 100],
            "close": [101, 103],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Invalid OHLC relationship rejected:", error)
    else:
        raise AssertionError("Invalid OHLC relationship was not rejected") 
    # Test 6: Infinite high price should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01", periods=2, freq="h", tz="UTC"
            ),
            "open": [100, 101],
            "high": [102, float("inf")],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Infinite high price rejected:", error)
    else:
        raise AssertionError("Infinite high price was not rejected")
    # Test 7: Invalid timestamp should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": ["not-a-date", "also-not-a-date"],
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except (ValueError, TypeError) as error:
        print("PASS: Invalid timestamps rejected:", error)
    else:
        raise AssertionError("Invalid timestamps were not rejected")  
    # Test 8: Missing timestamp should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": [
                pd.Timestamp("2026-10-01", tz="UTC"),
                pd.NaT,
            ],
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except (ValueError, TypeError) as error:
        print("PASS: Missing timestamp rejected:", error)
    else:
        raise AssertionError("Missing timestamp was not rejected")
    # Test 9: Duplicate timestamps should be rejected
    duplicate_time = pd.Timestamp("2026-10-01", tz="UTC")
    invalid_data = pd.DataFrame(
        {
            "timestamp": [duplicate_time, duplicate_time],
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Duplicate timestamps rejected:", error)
    else:
        raise AssertionError("Duplicate timestamps were not rejected")
    # Test 10: Unexpected candle interval should be rejected
    invalid_data = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2026-10-01 00:00:00+00:00",
                 "2026-10-01 02:00:00+00:00"],
                utc=True,
            ),
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 12],
        }
    )

    try:
        agent.analyze(invalid_data)
    except ValueError as error:
        print("PASS: Unexpected candle interval rejected:", error)
    else:
        raise AssertionError("Unexpected candle interval was not rejected")
test_invalid_data()    