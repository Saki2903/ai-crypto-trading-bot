from types import SimpleNamespace

from src.risk_engine import RiskEngine


def make_proposal(
    symbol="BTC/USDT",
    action="BUY",
    confidence=0.80,
    requires_review=True,
):
    return SimpleNamespace(
        symbol=symbol,
        action=action,
        confidence=confidence,
        requires_review=requires_review,
    )


def main():
    engine = RiskEngine(minimum_confidence=0.60)

    result = engine.validate(make_proposal(confidence=0.40))
    assert result.status == "REJECT", result.reasons
    assert "Confidence is below the minimum threshold." in result.reasons
    print("PASS: low-confidence proposal is rejected.")

    result = engine.validate(make_proposal(confidence=1.50))
    assert result.status == "REJECT", result.reasons
    assert "Confidence must be between 0 and 1." in result.reasons
    print("PASS: out-of-range confidence is rejected.")

    result = engine.validate(make_proposal(requires_review=False))
    assert result.status == "REJECT", result.reasons
    assert "Human review requirement is missing." in result.reasons
    print("PASS: proposal without human review is rejected.")
    # Edge cases: non-finite and invalid confidence values
    for invalid_confidence in (float("nan"), float("inf"), float("-inf"), "0.8"):
        result = engine.validate(make_proposal(confidence=invalid_confidence))
        assert result.status == "REJECT", (
            f"Expected rejection for confidence={invalid_confidence!r}"
        )
        print(f"PASS: invalid confidence {invalid_confidence!r} is rejected.")
    print("\nAll additional Risk Engine tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
