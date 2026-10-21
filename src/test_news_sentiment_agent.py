
from src.agents.news_sentiment_agent import NewsSentimentAgent


def main():
    agent = NewsSentimentAgent()

    headlines = [
        "Bitcoin adoption growth and positive rally",
        "Crypto market crash after major hack",
        "Bitcoin partnership announced",
    ]

    report = agent.analyze(headlines, symbol="BTC/USDT")

    print("=== NEWS & SENTIMENT REPORT ===")
    print("Symbol:", report.symbol)
    print("News analysed:", report.news_count)
    print("Positive score:", report.positive_score)
    print("Negative score:", report.negative_score)
    print("Overall sentiment:", report.sentiment)

    print("\nEvidence:")
    for item in report.evidence:
        print("-", item)
    
    print("\n=== INPUT VALIDATION TESTS ===")

    try:
        agent.analyze("This is not a list")
    except TypeError as error:
        print("PASS: Invalid input type rejected:", error)
    else:
        raise AssertionError("Invalid input type was not rejected")

    try:
        agent.analyze([""])
    except ValueError as error:
        print("PASS: Empty headline rejected:", error)
    else:
        raise AssertionError("Empty headline was not rejected")


if __name__ == "__main__":
    main()
