import pandas as pd

from src.agents.agent_coordinator import AgentCoordinator


def main():
    market_data = pd.read_csv("data/raw/btc_usdt_1h.csv")

    sample_headlines = [
        "Bitcoin adoption growth and positive rally",
        "Crypto market crash after major hack",
        "Bitcoin partnership announced",
    ]

    report = AgentCoordinator().research(
        market_data=market_data,
        headlines=sample_headlines,
        symbol="BTC/USDT",
    )

    print("=== LOCAL RESEARCH PIPELINE ===")
    print("Symbol:", report.market_report.symbol)
    print("Latest historical close:", report.market_report.latest_price)
    print("Market view:", report.market_report.market_view)
    print("News sentiment:", report.news_report.sentiment)
    print("Headlines analysed:", report.news_report.news_count)

    assert report.market_report.symbol == "BTC/USDT"
    assert report.news_report.symbol == "BTC/USDT"
    assert report.news_report.news_count == len(sample_headlines)

    print("\nPASS: local market and news research pipeline works.")
    print("Historical data and sample headlines only; no API request or trade.")


if __name__ == "__main__":
    main()
