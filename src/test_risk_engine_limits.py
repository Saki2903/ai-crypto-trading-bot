from types import SimpleNamespace

from src.risk_engine import RiskEngine


def proposal():
    return SimpleNamespace(
        symbol="BTC/USDT",
        action="BUY",
        confidence=0.80,
        requires_review=True,
    )


def main():
    engine = RiskEngine()

    result = engine.validate(
        proposal(),
        order_value_usdt=10.0,
        current_exposure_usdt=0.0,
    )
    assert result.status == "APPROVE", result.reasons
    print("PASS: order at 10 USDT limit is accepted for review.")

    result = engine.validate(
        proposal(),
        order_value_usdt=10.01,
        current_exposure_usdt=0.0,
    )
    assert result.status == "REJECT", result.reasons
    assert "Order exceeds the maximum order value." in result.reasons
    print("PASS: order above 10 USDT is rejected.")

    result = engine.validate(
        proposal(),
        order_value_usdt=10.0,
        current_exposure_usdt=15.0,
    )
    assert result.status == "REJECT", result.reasons
    assert "Order would exceed maximum total exposure." in result.reasons
    print("PASS: exposure above 20 USDT is rejected.")

    result = engine.validate(
        proposal(),
        order_value_usdt=5.0,
        current_exposure_usdt=15.0,
    )
    assert result.status == "APPROVE", result.reasons
    print("PASS: order that stays within exposure limit is accepted for review.")
        # Edge cases: invalid order values
    for invalid_order in (
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
        0.0,
        "5.0",
        True,
    ):
        result = engine.validate(
            proposal(),
            order_value_usdt=invalid_order,
            current_exposure_usdt=0.0,
        )
        assert result.status == "REJECT", (
            f"Expected rejection for order_value_usdt={invalid_order!r}"
        )
        print(f"PASS: invalid order value {invalid_order!r} is rejected.") 
            # Edge cases: invalid current exposure values
    for invalid_exposure in (
        float("nan"),
        float("inf"),
        float("-inf"),
        -1.0,
        "5.0",
        True,
    ):
        result = engine.validate(
            proposal(),
            order_value_usdt=5.0,
            current_exposure_usdt=invalid_exposure,
        )
        assert result.status == "REJECT", (
            f"Expected rejection for current_exposure_usdt={invalid_exposure!r}"
        )
        print(f"PASS: invalid exposure {invalid_exposure!r} is rejected.")
    print("\nAll Risk Engine limit tests passed.")
    print("No API request was made; no trade was executed.")


if __name__ == "__main__":
    main()
