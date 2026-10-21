
import json

from src.agents.ai_decision_agent import AIDecisionAgent
from src.llm.base import LLMClient
from src.llm.response import LLMResponse
from src.test_ai_research_validation import make_research


class FakeLLM(LLMClient):
    def __init__(self):
        self.called = False

    def generate(self, prompt: str) -> LLMResponse:
        self.called = True
        return LLMResponse(
            content=json.dumps({
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": "Test response",
                "risks": ["Test risk"],
            }),
            provider="fake",
            model="test-model",
            finish_reason="stop",
        )


def check_rejected(research, description):
    fake_llm = FakeLLM()

    try:
        AIDecisionAgent(llm=fake_llm).create_decision(research)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Invalid report was accepted: {description}")

    assert not fake_llm.called, (
        f"LLM was called with invalid report: {description}"
    )

    print(f"PASS: {description} rejected before LLM call.")


def main():
    # Test invalid market views.
    for value in ["UNKNOWN", "", None, 123]:
        research = make_research()
        research.market_report.market_view = value
        check_rejected(research, f"market_view={value!r}")

    # Test invalid news sentiment.
    for value in ["MIXED", "", None, 123]:
        research = make_research()
        research.news_report.sentiment = value
        check_rejected(research, f"sentiment={value!r}")

    print("\nAll report enum validation tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
