"""CustomerIntentAgent – interpret customer intent from loan request."""
from __future__ import annotations

import logging
from typing import List

from src.api.schemas import CustomerIntentResult, LoanRequest, LoanPurpose

logger = logging.getLogger(__name__)

_PURPOSE_RISK_MAP = {
    LoanPurpose.HOME: 0.3,
    LoanPurpose.AUTO: 0.4,
    LoanPurpose.EDUCATION: 0.35,
    LoanPurpose.BUSINESS: 0.55,
    LoanPurpose.PERSONAL: 0.6,
}


class CustomerIntentAgent:
    """Analyses customer intent and surfaces risk indicators."""

    async def run(self, request: LoanRequest) -> CustomerIntentResult:
        logger.info("CustomerIntentAgent processing request_id=%s", request.request_id)

        risk_indicators = self._detect_risk_indicators(request)
        confidence = self._compute_confidence(request, risk_indicators)
        summary = self._summarise_intent(request, risk_indicators)

        return CustomerIntentResult(
            intent_summary=summary,
            risk_indicators=risk_indicators,
            confidence_score=round(confidence, 4),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_risk_indicators(request: LoanRequest) -> List[str]:
        indicators = []
        monthly_income = request.annual_income / 12
        dti = request.monthly_debt / monthly_income if monthly_income > 0 else 1.0

        if dti > 0.43:
            indicators.append(f"High DTI ratio: {dti:.1%}")
        if request.credit_score < 650:
            indicators.append(f"Below-average credit score: {request.credit_score}")
        if request.employment_years < 1:
            indicators.append("Less than 1 year of employment history")
        if request.loan_amount > request.annual_income * 3:
            indicators.append("Loan amount exceeds 3x annual income")
        if request.loan_term_months > 120:
            indicators.append(f"Extended loan term: {request.loan_term_months} months")
        return indicators

    @staticmethod
    def _compute_confidence(request: LoanRequest, risk_indicators: List[str]) -> float:
        base = _PURPOSE_RISK_MAP.get(request.loan_purpose, 0.5)
        penalty = len(risk_indicators) * 0.05
        return max(0.1, min(1.0, 1.0 - base - penalty))

    @staticmethod
    def _summarise_intent(request: LoanRequest, risk_indicators: List[str]) -> str:
        purpose_label = request.loan_purpose.value.capitalize()
        indicator_text = (
            f" Risk indicators detected: {len(risk_indicators)}."
            if risk_indicators
            else " No significant risk indicators detected."
        )
        return (
            f"Customer {request.customer_id} is requesting a ${request.loan_amount:,.0f} "
            f"{purpose_label} loan over {request.loan_term_months} months at {request.interest_rate}% APR."
            + indicator_text
        )
