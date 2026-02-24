"""ComplianceAuditAgent – reasoning trace and audit report."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import List

from src.api.schemas import (
    AuditEntry,
    ComplianceAuditResult,
    LoanRequest,
    PolicyValidationResult,
    RiskScoringResult,
)
from src.memory.sqlite_memory import SQLiteMemory

logger = logging.getLogger(__name__)


class ComplianceAuditAgent:
    """Produces a full reasoning trace and structured audit report."""

    def __init__(self, db: SQLiteMemory | None = None):
        self._db = db or SQLiteMemory()

    async def run(
        self,
        request: LoanRequest,
        risk_result: RiskScoringResult,
        policy_result: PolicyValidationResult,
    ) -> ComplianceAuditResult:
        audit_id = str(uuid.uuid4())
        logger.info(
            "ComplianceAuditAgent processing request_id=%s audit_id=%s",
            request.request_id,
            audit_id,
        )

        trace = self._build_trace(request, risk_result, policy_result)
        is_approved = policy_result.is_compliant and risk_result.risk_level.value in ("low", "medium")
        report = self._generate_report(audit_id, request, risk_result, policy_result, is_approved)
        recommendations = self._generate_recommendations(request, risk_result, policy_result)

        # Persist audit to long-term memory
        for entry in trace:
            self._db.log_audit(request.request_id, entry.agent, entry.action, entry.reasoning)

        return ComplianceAuditResult(
            audit_id=audit_id,
            is_approved=is_approved,
            reasoning_trace=trace,
            audit_report=report,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_trace(
        request: LoanRequest,
        risk_result: RiskScoringResult,
        policy_result: PolicyValidationResult,
    ) -> List[AuditEntry]:
        now = datetime.now(timezone.utc).isoformat()
        return [
            AuditEntry(
                timestamp=now,
                agent="RiskScoringAgent",
                action="risk_computation",
                input_summary=f"Loan ${request.loan_amount:,.0f} for {request.customer_id}",
                output_summary=f"Risk score={risk_result.risk_score:.4f} level={risk_result.risk_level}",
                reasoning=(
                    f"DTI={risk_result.debt_to_income_ratio:.2%}, "
                    f"monthly_payment=${risk_result.monthly_payment:,.2f}, "
                    f"factors={risk_result.scoring_factors}"
                ),
            ),
            AuditEntry(
                timestamp=now,
                agent="PolicyValidationAgent",
                action="policy_retrieval_and_validation",
                input_summary=f"Risk score={risk_result.risk_score:.4f}",
                output_summary=f"Compliant={policy_result.is_compliant}",
                reasoning=policy_result.grounded_assessment,
            ),
            AuditEntry(
                timestamp=now,
                agent="ComplianceAuditAgent",
                action="final_compliance_determination",
                input_summary=f"All agent outputs for request_id={request.request_id}",
                output_summary=f"is_approved={policy_result.is_compliant and risk_result.risk_level.value in ('low', 'medium')}",
                reasoning=(
                    f"Policy compliant: {policy_result.is_compliant}. "
                    f"Risk level: {risk_result.risk_level}. "
                    f"Final determination based on combined agent outputs."
                ),
            ),
        ]

    @staticmethod
    def _generate_report(
        audit_id: str,
        request: LoanRequest,
        risk_result: RiskScoringResult,
        policy_result: PolicyValidationResult,
        is_approved: bool,
    ) -> str:
        decision_text = "APPROVED" if is_approved else "DENIED"
        return (
            f"LOAN ASSESSMENT AUDIT REPORT\n"
            f"{'=' * 60}\n"
            f"Audit ID     : {audit_id}\n"
            f"Request ID   : {request.request_id}\n"
            f"Customer ID  : {request.customer_id}\n"
            f"Loan Amount  : ${request.loan_amount:,.2f}\n"
            f"Decision     : {decision_text}\n"
            f"\n"
            f"RISK SUMMARY\n"
            f"{'-' * 40}\n"
            f"Risk Score   : {risk_result.risk_score:.4f}\n"
            f"Risk Level   : {risk_result.risk_level}\n"
            f"DTI Ratio    : {risk_result.debt_to_income_ratio:.2%}\n"
            f"Monthly Pmt  : ${risk_result.monthly_payment:,.2f}\n"
            f"\n"
            f"POLICY VALIDATION\n"
            f"{'-' * 40}\n"
            f"Compliant    : {policy_result.is_compliant}\n"
            f"Notes        : {policy_result.validation_notes}\n"
            f"\n"
            f"GROUNDED ASSESSMENT\n"
            f"{'-' * 40}\n"
            f"{policy_result.grounded_assessment}\n"
        )

    @staticmethod
    def _generate_recommendations(
        request: LoanRequest,
        risk_result: RiskScoringResult,
        policy_result: PolicyValidationResult,
    ) -> List[str]:
        recs = []
        if risk_result.debt_to_income_ratio > 0.36:
            recs.append("Consider reducing monthly debt obligations before reapplying.")
        if request.credit_score < 700:
            recs.append("Improving credit score to 700+ would unlock better rates.")
        if risk_result.risk_level.value in ("high", "critical"):
            recs.append("A co-signer or additional collateral may improve approval chances.")
        if not policy_result.is_compliant:
            recs.append("Address policy violations noted in the validation report.")
        if not recs:
            recs.append("Application meets all standard criteria. Proceed with standard processing.")
        return recs
