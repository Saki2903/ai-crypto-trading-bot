from types import SimpleNamespace

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse

import pandas as pd


class TruncatedFakeLLM(LLMClient):
    """Simulate a truncated AI response without calling an API."""

    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            content='{"action": "BUY"',
            provider="fake",
            model="test-model",
            finish_reason="length",
        )


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

    research = AgentCoordinator().research(
        market_data=market_data,
        headlines=["Bitcoin adoption growth", "Crypto market risk"],
        symbol="BTC/USDT",
    )

    agent = AIDecisionAgent(llm=TruncatedFakeLLM())
    decision = agent.create_decision(research)

    print("Action:", decision.action)
    print("Confidence:", decision.confidence)
    print("Requires review:", decision.requires_review)
    print("Reason:", decision.reasoning)

    assert decision.action == "HOLD", "Unsafe: expected HOLD fallback"
    assert decision.confidence == 0.0, "Expected zero confidence"
    assert decision.requires_review is True, "Human review must be required"
    assert "safely validated" in decision.reasoning.lower(), "Expected truncation fallback"

    print("\nPASS: truncated response safely falls back to HOLD.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
