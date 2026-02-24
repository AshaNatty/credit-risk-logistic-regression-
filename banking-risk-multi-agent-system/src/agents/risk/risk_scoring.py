"""RiskScoringAgent – numerical heavy computation."""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List

from src.api.schemas import (
    AmortizationEntry,
    LoanRequest,
    RiskLevel,
    RiskScoringResult,
)

logger = logging.getLogger(__name__)


class RiskScoringAgent:
    """Computes debt-to-income ratio, amortization schedule, and risk score."""

    # Weight map for risk scoring
    _WEIGHTS: Dict[str, float] = {
        "dti": 0.35,
        "credit_score": 0.30,
        "employment": 0.15,
        "loan_to_income": 0.20,
    }

    async def run(self, request: LoanRequest) -> RiskScoringResult:
        logger.info("RiskScoringAgent processing request_id=%s", request.request_id)

        monthly_income = request.annual_income / 12
        dti = self._compute_dti(request.monthly_debt, monthly_income)
        monthly_payment = self._compute_monthly_payment(
            request.loan_amount, request.interest_rate, request.loan_term_months
        )
        schedule = self._simulate_amortization(
            request.loan_amount, request.interest_rate, request.loan_term_months
        )
        total_interest = sum(e.interest for e in schedule)
        total_cost = request.loan_amount + total_interest

        risk_score, factors = self._compute_risk_score(request, dti, monthly_payment, monthly_income)
        risk_level = self._classify_risk(risk_score)

        return RiskScoringResult(
            debt_to_income_ratio=round(dti, 4),
            monthly_payment=round(monthly_payment, 2),
            total_interest=round(total_interest, 2),
            total_cost=round(total_cost, 2),
            risk_score=round(risk_score, 4),
            risk_level=risk_level,
            amortization_schedule=schedule,
            scoring_factors=factors,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_dti(monthly_debt: float, monthly_income: float) -> float:
        """Debt-to-income ratio (including new loan is handled by caller)."""
        if monthly_income == 0:
            return 1.0
        return monthly_debt / monthly_income

    @staticmethod
    def _compute_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
        """Standard fixed-rate mortgage payment formula."""
        r = annual_rate / 100 / 12
        if r == 0:
            return principal / term_months
        return principal * r * math.pow(1 + r, term_months) / (math.pow(1 + r, term_months) - 1)

    @staticmethod
    def _simulate_amortization(
        principal: float, annual_rate: float, term_months: int
    ) -> List[AmortizationEntry]:
        """Generate full amortization schedule."""
        r = annual_rate / 100 / 12
        if r == 0:
            monthly_payment = principal / term_months
        else:
            monthly_payment = principal * r * math.pow(1 + r, term_months) / (math.pow(1 + r, term_months) - 1)

        schedule: List[AmortizationEntry] = []
        balance = principal
        for month in range(1, term_months + 1):
            interest_payment = balance * r if r > 0 else 0.0
            principal_payment = monthly_payment - interest_payment
            balance = max(balance - principal_payment, 0.0)
            schedule.append(
                AmortizationEntry(
                    month=month,
                    payment=round(monthly_payment, 2),
                    principal=round(principal_payment, 2),
                    interest=round(interest_payment, 2),
                    balance=round(balance, 2),
                )
            )
        return schedule

    def _compute_risk_score(
        self,
        request: LoanRequest,
        dti: float,
        monthly_payment: float,
        monthly_income: float,
    ) -> tuple[float, Dict[str, Any]]:
        """Compute normalised risk score [0, 1] where higher = riskier."""

        # DTI component (>0.43 is traditional threshold)
        dti_score = min(dti / 0.65, 1.0)

        # Credit score component (inverse: lower score = higher risk)
        credit_score_normalised = (request.credit_score - 300) / (850 - 300)
        credit_risk = 1.0 - credit_score_normalised

        # Employment component (inverse: less employment = higher risk)
        employment_score = min(request.employment_years / 10, 1.0)
        employment_risk = 1.0 - employment_score

        # Loan-to-income ratio
        loan_to_income = request.loan_amount / request.annual_income
        lti_score = min(loan_to_income / 5.0, 1.0)

        composite = (
            self._WEIGHTS["dti"] * dti_score
            + self._WEIGHTS["credit_score"] * credit_risk
            + self._WEIGHTS["employment"] * employment_risk
            + self._WEIGHTS["loan_to_income"] * lti_score
        )

        factors = {
            "dti_score": round(dti_score, 4),
            "credit_risk_score": round(credit_risk, 4),
            "employment_risk_score": round(employment_risk, 4),
            "loan_to_income_score": round(lti_score, 4),
            "composite_risk_score": round(composite, 4),
        }
        return composite, factors

    @staticmethod
    def _classify_risk(score: float) -> RiskLevel:
        if score < 0.30:
            return RiskLevel.LOW
        if score < 0.55:
            return RiskLevel.MEDIUM
        if score < 0.75:
            return RiskLevel.HIGH
        return RiskLevel.CRITICAL
