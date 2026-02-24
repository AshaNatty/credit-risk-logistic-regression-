"""Tests for PolicyValidationAgent."""
from __future__ import annotations

import pytest
from src.agents.retrieval.policy_validation import PolicyValidationAgent
from src.api.schemas import LoanPurpose, LoanRequest


def _make_request(**kwargs) -> LoanRequest:
    defaults = dict(
        customer_id="CUST-002",
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
async def test_policy_validation_compliant():
    agent = PolicyValidationAgent()
    result = await agent.run(_make_request(), risk_score=0.3)
    assert result.is_compliant is True
    assert result.policy_clauses
    assert "passed" in result.validation_notes


@pytest.mark.asyncio
async def test_policy_validation_non_compliant_low_credit():
    agent = PolicyValidationAgent()
    result = await agent.run(_make_request(credit_score=550), risk_score=0.7)
    assert result.is_compliant is False
    assert "620" in result.validation_notes


@pytest.mark.asyncio
async def test_policy_validation_non_compliant_high_dti():
    agent = PolicyValidationAgent()
    result = await agent.run(
        _make_request(monthly_debt=5000, annual_income=80000), risk_score=0.5
    )
    assert result.is_compliant is False


@pytest.mark.asyncio
async def test_grounded_assessment_present():
    agent = PolicyValidationAgent()
    result = await agent.run(_make_request(), risk_score=0.3)
    assert len(result.grounded_assessment) > 10
