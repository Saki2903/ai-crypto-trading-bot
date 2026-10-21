from src.test_ai_safety_fallback import AgentCoordinator, AIDecisionAgent
from src.test_ai_safety_fallback import LLMClient, LLMResponse
from src.test_ai_safety_fallback import pd


class InvalidJsonFakeLLM(LLMClient):
    """Return invalid JSON without making an API request."""

    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(
            content='This is not valid JSON',
            provider="fake",
            model="test-model",
            finish_reason="stop",
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

    decision = AIDecisionAgent(
        llm=InvalidJsonFakeLLM()
    ).create_decision(research)

    print("Action:", decision.action)
    print("Confidence:", decision.confidence)
    print("Requires review:", decision.requires_review)

    assert decision.action == "HOLD"
    assert decision.confidence == 0.0
    assert decision.requires_review is True

    print("\nPASS: invalid JSON safely falls back to HOLD.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
