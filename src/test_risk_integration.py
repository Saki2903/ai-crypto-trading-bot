from src.agents.ai_decision_agent import DecisionReport
from src.risk_engine import RiskEngine


def main():
    engine = RiskEngine()

    sample_decision = DecisionReport(
        symbol="BTC/USDT",
        action="BUY",
        confidence=0.80,
        reasoning="Sample proposal for local integration testing.",
        supporting_evidence=["Synthetic test evidence only."],
        risks=["This is not a live market recommendation."],
        requires_review=True,
    )

    result = engine.validate(
        sample_decision,
        order_value_usdt=5.0,
        current_exposure_usdt=0.0,
    )
    assert result.status == "APPROVE", result.reasons
    print("PASS: decision report passes Risk Engine validation.")

    result = engine.validate(
        sample_decision,
        order_value_usdt=10.0,
        current_exposure_usdt=15.0,
    )
    assert result.status == "REJECT", result.reasons
    assert "Order would exceed maximum total exposure." in result.reasons
    print("PASS: decision report is rejected when exposure limit is exceeded.")

    print("\nRisk Engine integration test passed.")
    print("Synthetic decision only; no API request or trade occurred.")


if __name__ == "__main__":
    main()
