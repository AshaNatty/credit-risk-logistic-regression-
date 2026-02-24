"""Tests for CoordinatorAgent."""
from __future__ import annotations

import pytest
from src.agents.coordinator import CoordinatorAgent
from src.api.schemas import LoanDecision, LoanPurpose, LoanRequest


def _make_request(**kwargs) -> LoanRequest:
    defaults = dict(
        customer_id="CUST-004",
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
async def test_coordinator_full_pipeline():
    coordinator = CoordinatorAgent()
    request = _make_request()
    response = await coordinator.process(request)

    assert response.request_id == request.request_id
    assert response.customer_id == "CUST-004"
    assert response.decision in (LoanDecision.APPROVED, LoanDecision.DENIED, LoanDecision.PENDING_REVIEW)
    assert response.risk_scoring.risk_score >= 0
    assert response.compliance_audit.audit_id
    assert response.processing_time_ms > 0


@pytest.mark.asyncio
async def test_coordinator_caches_result():
    coordinator = CoordinatorAgent()
    request = _make_request()
    response1 = await coordinator.process(request)
    response2 = await coordinator.process(request)
    assert response1.request_id == response2.request_id
    assert response1.decision == response2.decision
