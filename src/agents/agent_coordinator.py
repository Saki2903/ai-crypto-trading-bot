
from dataclasses import dataclass

import pandas as pd

from agents.market_research_agent import (
    MarketResearchAgent,
    MarketResearchReport,
)
from agents.news_sentiment_agent import (
    NewsSentimentAgent,
    NewsSentimentReport,
)


@dataclass
class CombinedResearchReport:
    market_report: MarketResearchReport
    news_report: NewsSentimentReport


class AgentCoordinator:
    """Runs research agents and combines their reports."""

    def __init__(self):
        self.market_agent = MarketResearchAgent()
        self.news_agent = NewsSentimentAgent()

    def research(
        self,
        market_data: pd.DataFrame,
        headlines: list[str],
        symbol: str = "BTC/USDT",
    ) -> CombinedResearchReport:
        market_report = self.market_agent.analyze(
            market_data,
            symbol=symbol,
        )

        news_report = self.news_agent.analyze(
            headlines,
            symbol=symbol,
        )

        return CombinedResearchReport(
            market_report=market_report,
            news_report=news_report,
        )
