"""Tests for ComplianceAuditAgent."""
from __future__ import annotations

import pytest
from src.agents.compliance.compliance_audit import ComplianceAuditAgent
from src.agents.retrieval.policy_validation import PolicyValidationAgent
from src.agents.risk.risk_scoring import RiskScoringAgent
from src.api.schemas import LoanPurpose, LoanRequest


def _make_request(**kwargs) -> LoanRequest:
    defaults = dict(
        customer_id="CUST-003",
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
async def test_compliance_audit_approved():
    agent = ComplianceAuditAgent()
    risk_agent = RiskScoringAgent()
    policy_agent = PolicyValidationAgent()
    request = _make_request()
    risk_result = await risk_agent.run(request)
    policy_result = await policy_agent.run(request, risk_result.risk_score)
    audit_result = await agent.run(request, risk_result, policy_result)

    assert audit_result.audit_id
    assert isinstance(audit_result.is_approved, bool)
    assert len(audit_result.reasoning_trace) == 3
    assert audit_result.audit_report
    assert audit_result.recommendations


@pytest.mark.asyncio
async def test_compliance_audit_denied_on_violations():
    agent = ComplianceAuditAgent()
    risk_agent = RiskScoringAgent()
    policy_agent = PolicyValidationAgent()
    request = _make_request(
        credit_score=500,
        monthly_debt=5000,
        annual_income=40000,
        employment_years=0.5,
    )
    risk_result = await risk_agent.run(request)
    policy_result = await policy_agent.run(request, risk_result.risk_score)
    audit_result = await agent.run(request, risk_result, policy_result)

    assert audit_result.is_approved is False
    assert len(audit_result.recommendations) > 0
