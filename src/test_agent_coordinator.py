
import pandas as pd

from agents.agent_coordinator import AgentCoordinator


def main():
    market_data = pd.DataFrame(
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

    headlines = [
        "Bitcoin adoption growth and positive rally",
        "Crypto market crash after major hack",
        "Bitcoin partnership announced",
    ]

    coordinator = AgentCoordinator()
    report = coordinator.research(
        market_data=market_data,
        headlines=headlines,
        symbol="BTC/USDT",
    )

    print("=== COMBINED RESEARCH REPORT ===")

    print("\n--- MARKET RESEARCH ---")
    print("Latest price:", report.market_report.latest_price)
    print("Market view:", report.market_report.market_view)
    print("Hourly return:", f"{report.market_report.hourly_return_pct:.3f}%")

    print("\n--- NEWS SENTIMENT ---")
    print("News analysed:", report.news_report.news_count)
    print("Positive score:", report.news_report.positive_score)
    print("Negative score:", report.news_report.negative_score)
    print("Sentiment:", report.news_report.sentiment)

    print("\nCoordinator test completed successfully.")


if __name__ == "__main__":
    main()
