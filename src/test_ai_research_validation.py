
import json
import math

import pandas as pd

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse


class FakeLLM(LLMClient):
    def __init__(self):
        self.called = False

    def generate(self, prompt: str) -> LLMResponse:
        self.called = True
        return LLMResponse(
            content=json.dumps({
                "action": "BUY",
                "confidence": 0.8,
                "reasoning": "Test response",
                "risks": ["Test risk"],
            }),
            provider="fake",
            model="test-model",
            finish_reason="stop",
        )


def make_research():
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

    return AgentCoordinator().research(
        market_data=market_data,
        headlines=["Bitcoin adoption growth", "Crypto market risk"],
        symbol="BTC/USDT",
    )

def main():
    # Test invalid latest price.
    invalid_values = [
        math.nan,
        math.inf,
        -math.inf,
        0.0,
        -1.0,
        "100",
        True,
    ]

    for value in invalid_values:
        research = make_research()
        research.market_report.latest_price = value
        fake_llm = FakeLLM()

        try:
            AIDecisionAgent(llm=fake_llm).create_decision(research)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"Invalid latest_price was not rejected: {value!r}"
            )

        assert not fake_llm.called
        print(f"PASS: invalid latest_price {value!r} rejected.")

    # Test invalid hourly return.
    for value in [math.nan, math.inf, -math.inf, "1.5", True]:
        research = make_research()
        research.market_report.hourly_return_pct = value
        fake_llm = FakeLLM()

        try:
            AIDecisionAgent(llm=fake_llm).create_decision(research)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"Invalid hourly return was accepted: {value!r}"
            )

        assert not fake_llm.called
        print(f"PASS: invalid hourly return {value!r} rejected.")

    # Test invalid volatility.
    for value in [math.nan, math.inf, -math.inf, -1.0, "1.5", True]:
        research = make_research()
        research.market_report.volatility_pct = value
        fake_llm = FakeLLM()

        try:
            AIDecisionAgent(llm=fake_llm).create_decision(research)
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"Invalid volatility was accepted: {value!r}"
            )

        assert not fake_llm.called
        print(f"PASS: invalid volatility {value!r} rejected.")

    print("\nAll research validation tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
