from dataclasses import dataclass
import math
from typing import Literal

RiskStatus = Literal["APPROVE", "REJECT"]


@dataclass
class RiskCheckResult:
    status: RiskStatus
    symbol: str
    action: str
    reasons: list[str]


class RiskEngine:
    """Validate proposals and simulation limits; never execute trades."""

    def __init__(
        self,
        allowed_symbols: set[str] | None = None,
        minimum_confidence: float = 0.60,
        max_order_usdt: float = 10.0,
        max_exposure_usdt: float = 20.0,
    ):
        if not math.isfinite(minimum_confidence) or not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1.")
        if not math.isfinite(max_order_usdt) or max_order_usdt <= 0:
            raise ValueError("max_order_usdt must be positive and finite.")
        if not math.isfinite(max_exposure_usdt) or max_exposure_usdt <= 0:
            raise ValueError("max_exposure_usdt must be positive and finite.")

        self.allowed_symbols = (
            set(allowed_symbols) if allowed_symbols is not None else {"BTC/USDT"}
        )
        self.minimum_confidence = minimum_confidence
        self.max_order_usdt = max_order_usdt
        self.max_exposure_usdt = max_exposure_usdt

    def validate(
        self,
        decision,
        order_value_usdt: float | None = None,
        current_exposure_usdt: float = 0.0,
    ) -> RiskCheckResult:
        reasons = []

        if decision.symbol not in self.allowed_symbols:
            reasons.append("Symbol is not allowed.")

        if decision.action not in {"BUY", "SELL", "HOLD"}:
            reasons.append("Invalid action.")

        confidence = decision.confidence
        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not math.isfinite(confidence)
            or not 0.0 <= confidence <= 1.0
        ):
            reasons.append("Confidence must be between 0 and 1.")
        elif confidence < self.minimum_confidence:
            reasons.append("Confidence is below the minimum threshold.")

        if decision.action == "HOLD":
            reasons.append("HOLD proposals do not authorize an order.")

        if decision.requires_review is not True:
            reasons.append("Human review requirement is missing.")

        if order_value_usdt is None:
            reasons.append("Order value in USDT is required.")
        elif (
            isinstance(order_value_usdt, bool)
            or not isinstance(order_value_usdt, (int, float))
            or not math.isfinite(order_value_usdt)
            or order_value_usdt <= 0
        ):
            reasons.append("Order value must be positive and finite.")
        elif order_value_usdt > self.max_order_usdt:
            reasons.append("Order exceeds the maximum order value.")

        if (
            isinstance(current_exposure_usdt, bool)
            or not isinstance(current_exposure_usdt, (int, float))
            or not math.isfinite(current_exposure_usdt)
            or current_exposure_usdt < 0
        ):
            reasons.append("Current exposure must be non-negative and finite.")
        elif (
            isinstance(order_value_usdt, (int, float))
            and not isinstance(order_value_usdt, bool)
            and math.isfinite(order_value_usdt)
            and order_value_usdt > 0
            and current_exposure_usdt + order_value_usdt > self.max_exposure_usdt
        ):
            reasons.append("Order would exceed maximum total exposure.")

        if reasons:
            return RiskCheckResult(
                status="REJECT",
                symbol=decision.symbol,
                action=decision.action,
                reasons=reasons,
            )

        return RiskCheckResult(
            status="APPROVE",
            symbol=decision.symbol,
            action=decision.action,
            reasons=[
                "Proposal passed initial risk checks.",
                "No order was executed.",
                "Human review is still required.",
            ],
        )
