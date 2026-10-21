import json
import math
from dataclasses import dataclass
from typing import Literal


from src.agents.agent_coordinator import CombinedResearchReport
from src.llm.base import LLMClient
from src.llm.client_factory import create_llm_client


TradeAction = Literal["BUY", "SELL", "HOLD"]


@dataclass
class DecisionReport:
    symbol: str
    action: TradeAction
    confidence: float
    reasoning: str
    supporting_evidence: list[str]
    risks: list[str]
    requires_review: bool = True


class AIDecisionAgent:
    """
    Creates an AI-assisted decision proposal from market and news evidence.
    Does not execute trades.
    """

    def __init__(self, llm: LLMClient | None = None):
     self.llm = llm if llm is not None else create_llm_client()

    def _safe_hold(
        self,
        symbol: str,
        evidence: list[str],
        reason: str,
    ) -> DecisionReport:
        return DecisionReport(
            symbol=symbol,
            action="HOLD",
            confidence=0.0,
            reasoning=reason,
            supporting_evidence=evidence,
            risks=[
                "AI output is not independently verified.",
                "News sentiment uses keyword matching and may miss context.",
                "Historical market data cannot guarantee future performance.",
                "Transaction costs, liquidity and slippage are not fully modelled.",
            ],
            requires_review=True,
        )

    def create_decision(
        self,
        research: CombinedResearchReport,
    ) -> DecisionReport:
        if research is None:
            raise ValueError("Research report is required.")

        market = research.market_report
        news = research.news_report
        
        # Validate market report fields before building the AI prompt.
        if not isinstance(market.symbol, str) or not market.symbol.strip():
            raise ValueError("Market symbol must be a non-empty string.")

        if (
            isinstance(market.latest_price, bool)
            or not isinstance(market.latest_price, (int, float))
            or not math.isfinite(market.latest_price)
            or market.latest_price <= 0
        ):
            raise ValueError("Latest price must be a finite positive number.")

        if (
            isinstance(market.hourly_return_pct, bool)
            or not isinstance(market.hourly_return_pct, (int, float))
            or not math.isfinite(market.hourly_return_pct)
        ):
            raise ValueError("Hourly return must be a finite number.")

        if (
            isinstance(market.volatility_pct, bool)
            or not isinstance(market.volatility_pct, (int, float))
            or not math.isfinite(market.volatility_pct)
            or market.volatility_pct < 0
        ):
            raise ValueError("Volatility must be a finite non-negative number.")

        if market.market_view not in ("BULLISH", "BEARISH", "NEUTRAL"):
            raise ValueError("Invalid market view.")

        if not isinstance(market.evidence, list) or not all(
            isinstance(item, str) and item.strip()
            for item in market.evidence
        ):
            raise ValueError("Market evidence must contain non-empty strings.")

        # Validate news report fields.
        if not isinstance(news.symbol, str) or not news.symbol.strip():
            raise ValueError("News symbol must be a non-empty string.")

        if news.sentiment not in ("POSITIVE", "NEGATIVE", "NEUTRAL"):
            raise ValueError("Invalid news sentiment.")

        for field_name, value in (
            ("positive_score", news.positive_score),
            ("negative_score", news.negative_score),
            ("news_count", news.news_count),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or value < 0
            ):
                raise ValueError(
                    f"{field_name} must be a non-negative integer."
                )

        if not isinstance(news.evidence, list) or not all(
            isinstance(item, str) and item.strip()
            for item in news.evidence
        ):
            raise ValueError("News evidence must contain non-empty strings.")
 
        if market.symbol != news.symbol:
            raise ValueError(
                "Market and news reports must refer to the same symbol."
            )

        if not market.evidence:
            raise ValueError("Market evidence is required.")

        if not news.evidence:
            raise ValueError("News evidence is required.")

        evidence = [
            f"Market view: {market.market_view}",
            f"Latest price: {market.latest_price:.2f}",
            f"Latest hourly return: {market.hourly_return_pct:.3f}%",
            f"Historical volatility: {market.volatility_pct:.3f}%",
            f"News sentiment: {news.sentiment}",
            f"Positive keyword score: {news.positive_score}",
            f"Negative keyword score: {news.negative_score}",
            *market.evidence,
            *news.evidence,
        ]

        prompt_data = {
            "symbol": market.symbol,
            "market": {
                "latest_price": market.latest_price,
                "hourly_return_pct": market.hourly_return_pct,
                "volatility_pct": market.volatility_pct,
                "market_view": market.market_view,
                "evidence": market.evidence,
            },
            "news": {
                "sentiment": news.sentiment,
                "positive_score": news.positive_score,
                "negative_score": news.negative_score,
                "news_count": news.news_count,
                "evidence": news.evidence,
            },
        }

        prompt = f"""
You are a cautious crypto research assistant.
Analyse the supplied evidence. Do not execute trades.
Evidence may be incomplete or misleading. Do not invent facts.
Do not treat keyword sentiment as proof of market direction.

Return only one valid JSON object with exactly these fields:
{{
  "action": "BUY" or "SELL" or "HOLD",
  "confidence": a number from 0.0 to 1.0,
  "reasoning": "brief evidence-based explanation",
  "risks": ["risk 1", "risk 2"]
}}

Use HOLD when evidence is mixed, insufficient, or uncertain.
Confidence is your assessment of this proposal, not a probability of profit.
Do not include Markdown fences or any text outside the JSON.

Research evidence:
{json.dumps(prompt_data, ensure_ascii=False)}
"""

        try:
            response = self.llm.generate(prompt)

            if response.finish_reason == "length":
              raise ValueError("AI response was truncated due to output token limit.")

            if not response.content or not response.content.strip():
              raise ValueError("AI returned empty content.")

            result = json.loads(response.content)

            if not isinstance(result, dict):
                raise ValueError("AI response must be a JSON object.")

            action = result.get("action")
            confidence = result.get("confidence")
            reasoning = result.get("reasoning")
            risks = result.get("risks")

            if action not in ("BUY", "SELL", "HOLD"):
                raise ValueError("Invalid action.")

            if (
               isinstance(confidence, bool)
               or not isinstance(confidence, (int, float))
               or not math.isfinite(confidence)
               or not 0.0 <= confidence <= 1.0
               ):
               raise ValueError(
              "Confidence must be a finite number between 0 and 1."
               )

            if not isinstance(reasoning, str) or not reasoning.strip():
                raise ValueError("Reasoning must be a non-empty string.")

            
            if (
                not isinstance(risks, list)
                or not all(
                    isinstance(risk, str) and risk.strip()
                    for risk in risks
                 )
            ):
                raise ValueError(
                     "Risks must be a list of non-empty strings."
                )

            return DecisionReport(
                symbol=market.symbol,
                action=action,
                confidence=float(confidence),
                reasoning=reasoning.strip(),
                supporting_evidence=evidence,
                risks=risks + [
                    "AI proposals require independent validation.",
                    "No transaction has been executed.",
                ],
                requires_review=True,
            )

        except Exception as exc:
            import traceback
            traceback.print_exc()

            return self._safe_hold(
                symbol=market.symbol,
                evidence=evidence,
                reason=(
                    "AI proposal could not be safely validated. "
                    f"Using HOLD fallback. Details: {type(exc).__name__}"
                ),
            )
