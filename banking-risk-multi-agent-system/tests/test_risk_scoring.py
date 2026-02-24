"""Tests for RiskScoringAgent."""
from __future__ import annotations

import asyncio
import pytest
from src.agents.risk.risk_scoring import RiskScoringAgent
from src.api.schemas import LoanPurpose, LoanRequest, RiskLevel


def _make_request(**kwargs) -> LoanRequest:
    defaults = dict(
        customer_id="CUST-001",
        annual_income=80000,
        monthly_debt=800,
        loan_amount=200000,
        loan_term_months=360,
        interest_rate=5.5,
        credit_score=720,
        employment_years=5.0,
        loan_purpose=LoanPurpose.HOME,
    )
    defaults.update(kwargs)
    return LoanRequest(**defaults)


@pytest.mark.asyncio
async def test_risk_scoring_returns_result():
    agent = RiskScoringAgent()
    result = await agent.run(_make_request())
    assert result.risk_score >= 0
    assert result.risk_score <= 1
    assert result.debt_to_income_ratio > 0
    assert result.monthly_payment > 0
    assert result.total_interest > 0
    assert len(result.amortization_schedule) == 360


@pytest.mark.asyncio
async def test_risk_scoring_low_risk():
    agent = RiskScoringAgent()
    result = await agent.run(
        _make_request(
            annual_income=200000,
            monthly_debt=500,
            loan_amount=100000,
            credit_score=800,
            employment_years=15,
        )
    )
    assert result.risk_level == RiskLevel.LOW


@pytest.mark.asyncio
async def test_risk_scoring_high_risk():
    agent = RiskScoringAgent()
    result = await agent.run(
        _make_request(
            annual_income=30000,
            monthly_debt=2000,
            loan_amount=150000,
            credit_score=580,
            employment_years=0.5,
        )
    )
    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)


def test_dti_computation():
    score = RiskScoringAgent._compute_dti(1000, 5000)
    assert score == pytest.approx(0.2)


def test_monthly_payment():
    pmt = RiskScoringAgent._compute_monthly_payment(100000, 6.0, 360)
    assert pmt == pytest.approx(599.55, rel=0.01)


def test_amortization_schedule_length():
    schedule = RiskScoringAgent._simulate_amortization(100000, 5.0, 12)
    assert len(schedule) == 12
    # Final balance should be near zero
    assert schedule[-1].balance == pytest.approx(0.0, abs=1.0)
