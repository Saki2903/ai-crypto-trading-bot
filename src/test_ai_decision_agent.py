
import pandas as pd

from src.agents.agent_coordinator import AgentCoordinator
from src.agents.ai_decision_agent import AIDecisionAgent


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

    decision_agent = AIDecisionAgent()
    decision = decision_agent.create_decision(research)

    print("=== DECISION AGENT REPORT ===")
    print("Symbol:", decision.symbol)
    print("Action:", decision.action)
    print("Confidence:", decision.confidence)
    print("Reasoning:", decision.reasoning)
    print("Requires review:", decision.requires_review)

    print("\nSupporting evidence:")
    for item in decision.supporting_evidence:
        print("-", item)

    print("\nRisks:")
    for risk in decision.risks:
        print("-", risk)


if __name__ == "__main__":
    main()
