from types import SimpleNamespace

from src.risk_engine import RiskEngine


def main():
    engine = RiskEngine(minimum_confidence=0.60)

    valid_buy = SimpleNamespace(
        symbol="BTC/USDT",
        action="BUY",
        confidence=0.80,
        requires_review=True,
    )
    result = engine.validate(valid_buy, order_value_usdt=5.0, current_exposure_usdt=0.0)
    assert result.status == "APPROVE", result.reasons
    print("PASS: valid BUY proposal passes initial checks.")

    hold_proposal = SimpleNamespace(
        symbol="BTC/USDT",
        action="HOLD",
        confidence=0.80,
        requires_review=True,
    )
    result = engine.validate(hold_proposal, order_value_usdt=5.0, current_exposure_usdt=0.0)
    assert result.status == "REJECT", result.reasons
    print("PASS: HOLD proposal cannot authorize an order.")

    unknown_symbol = SimpleNamespace(
        symbol="ETH/USDT",
        action="BUY",
        confidence=0.90,
        requires_review=True,
    )
    result = engine.validate(unknown_symbol, order_value_usdt=5.0, current_exposure_usdt=0.0)
    assert result.status == "REJECT", result.reasons
    assert "Symbol is not allowed." in result.reasons
    print("PASS: unapproved symbol is rejected.")

    print("\nAll initial Risk Engine tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
