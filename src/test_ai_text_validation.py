
import json

import pandas as pd

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse


class FakeLLM(LLMClient):
    def __init__(self, reasoning, risks):
        self.reasoning = reasoning
        self.risks = risks

    def generate(self, prompt: str) -> LLMResponse:
        content = json.dumps({
            "action": "BUY",
            "confidence": 0.8,
            "reasoning": self.reasoning,
            "risks": self.risks,
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

    invalid_cases = [
        ("", ["Test risk"]),
        ("   ", ["Test risk"]),
        (None, ["Test risk"]),
        (123, ["Test risk"]),
        ("Test reasoning", "risk as string"),
        ("Test reasoning", [123]),
        ("Test reasoning", [""]),
        ("Test reasoning", ["   "]),
    ]

    for reasoning, risks in invalid_cases:
        agent = AIDecisionAgent(
            llm=FakeLLM(reasoning, risks)
        )
        decision = agent.create_decision(research)

        assert decision.action == "HOLD", (
            f"Invalid response accepted: reasoning={reasoning!r}, "
            f"risks={risks!r}"
        )
        assert decision.confidence == 0.0
        assert decision.requires_review is True

        print(
            f"PASS: invalid reasoning/risks rejected: "
            f"{reasoning!r}, {risks!r}"
        )

    print("\nAll text validation tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
