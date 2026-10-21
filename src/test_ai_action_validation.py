
import json

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse

import pandas as pd


class FakeLLM(LLMClient):
    def __init__(self, action):
        self.action = action

    def generate(self, prompt: str) -> LLMResponse:
        content = json.dumps({
            "action": self.action,
            "confidence": 0.8,
            "reasoning": "Test response",
            "risks": ["Test risk"],
        })

        return LLMResponse(
            content=content,
            provider="fake",
            model="test-model",
            finish_reason="stop",
        )


def main():
    market_data = pd.DataFrame({
        "timestamp": pd.date_range(
            "2026-10-01", periods=5, freq="h", tz="UTC"
        ),
        "open": [100, 101, 102, 101, 103],
        "high": [102, 103, 103, 104, 105],
        "low": [99, 100, 101, 100, 102],
        "close": [101, 102, 101, 103, 104],
        "volume": [10, 12, 11, 15, 14],
    })

    research = AgentCoordinator().research(
        market_data=market_data,
        headlines=["Bitcoin adoption growth", "Crypto market risk"],
        symbol="BTC/USDT",
    )

    invalid_actions = ["BUY_NOW", "", None, 123, True, ["BUY"]]

    for action in invalid_actions:
        agent = AIDecisionAgent(llm=FakeLLM(action))
        decision = agent.create_decision(research)

        assert decision.action == "HOLD", (
            f"Unsafe action accepted: {action!r}"
        )
        assert decision.confidence == 0.0
        assert decision.requires_review is True

        print(f"PASS: invalid action {action!r} safely falls back to HOLD.")

    print("\nAll invalid action tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
