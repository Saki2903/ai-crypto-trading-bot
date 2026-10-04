
from dataclasses import dataclass
from typing import Literal


Sentiment = Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]


@dataclass
class NewsSentimentReport:
    symbol: str
    sentiment: Sentiment
    positive_score: int
    negative_score: int
    evidence: list[str]
    news_count: int


class NewsSentimentAgent:
    """Analyses supplied news headlines without placing trades."""

    POSITIVE_KEYWORDS = {
        "surge",
        "rally",
        "growth",
        "adoption",
        "approval",
        "bullish",
        "partnership",
        "record",
        "gain",
        "positive",
    }

    NEGATIVE_KEYWORDS = {
        "crash",
        "drop",
        "hack",
        "fraud",
        "ban",
        "bearish",
        "lawsuit",
        "loss",
        "negative",
        "risk",
    }

    def analyze(
        self,
        headlines: list[str],
        symbol: str = "BTC/USDT",
    ) -> NewsSentimentReport:
        if not isinstance(headlines, list):
            raise TypeError("headlines must be a list of strings.")

        if not all(
            isinstance(headline, str) and headline.strip()
            for headline in headlines
        ):
            raise ValueError("Every headline must be a non-empty string.")

        positive_score = 0
        negative_score = 0
        evidence = []

        for headline in headlines:
            words = set(
                headline.lower()
                .replace("-", " ")
                .replace(",", " ")
                .replace(".", " ")
                .split()
            )

            positive_matches = words & self.POSITIVE_KEYWORDS
            negative_matches = words & self.NEGATIVE_KEYWORDS

            positive_score += len(positive_matches)
            negative_score += len(negative_matches)

            if positive_matches or negative_matches:
                evidence.append(
                    f"{headline} | "
                    f"Positive: {sorted(positive_matches)} | "
                    f"Negative: {sorted(negative_matches)}"
                )

        if positive_score > negative_score:
            sentiment = "POSITIVE"
        elif negative_score > positive_score:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"

        if not evidence:
            evidence.append(
                "No configured sentiment keywords were found."
            )

        return NewsSentimentReport(
            symbol=symbol,
            sentiment=sentiment,
            positive_score=positive_score,
            negative_score=negative_score,
            evidence=evidence,
            news_count=len(headlines),
        )
