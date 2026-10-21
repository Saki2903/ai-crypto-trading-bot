import json

import pandas as pd

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse
from src.risk_engine import RiskEngine


class MockLLM(LLMClient):
    """Offline mock; never contacts an external AI service."""

    def generate(self, prompt: str) -> LLMResponse:
        response = {
            "action": "HOLD",
            "confidence": 0.0,
            "reasoning": (
                "Offline demonstration only; no live market analysis "
                "or AI service was used."
            ),
            "risks": [
                "Synthetic demonstration data.",
                "No transaction has been executed.",
            ],
        }
        return LLMResponse(
            content=json.dumps(response),
            provider="mock",
            model="offline-demo",
            finish_reason="stop",
        )


def main():
    print("AI Crypto Trading Bot")
    print("Mode: Offline simulation only.")
    print("No external API calls or orders will be made.")

    market_data = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-10-01",
                periods=5,
                freq="h",
                tz="UTC",
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
    research = coordinator.research(
        market_data=market_data,
        headlines=headlines,
        symbol="BTC/USDT",
    )

    decision_agent = AIDecisionAgent(llm=MockLLM())
    decision = decision_agent.create_decision(research)

    risk_engine = RiskEngine()
    risk_result = risk_engine.validate(
        decision,
        order_value_usdt=5.0,
        current_exposure_usdt=0.0,
    )

    print("\n--- Market Research ---")
    print(f"Symbol: {research.market_report.symbol}")
    print(f"Market view: {research.market_report.market_view}")
    print(f"Latest sample price: {research.market_report.latest_price}")

    print("\n--- News Sentiment ---")
    print(f"Sentiment: {research.news_report.sentiment}")
    print(f"News count: {research.news_report.news_count}")

    print("\n--- AI Proposal (Mock) ---")
    print(f"Action: {decision.action}")
    print(f"Confidence: {decision.confidence}")
    print(f"Reasoning: {decision.reasoning}")

    print("\n--- Risk Validation ---")
    print(f"Status: {risk_result.status}")
    for reason in risk_result.reasons:
        print(f"- {reason}")

    print("\nNo order was created or executed.")


if __name__ == "__main__":
    main()
