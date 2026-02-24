"""CoordinatorAgent – orchestrates all agents in the pipeline."""
from __future__ import annotations

import logging
import time

from src.agents.compliance.compliance_audit import ComplianceAuditAgent
from src.agents.customer_intent import CustomerIntentAgent
from src.agents.retrieval.policy_validation import PolicyValidationAgent
from src.agents.risk.risk_scoring import RiskScoringAgent
from src.api.schemas import LoanAssessmentResponse, LoanDecision, LoanRequest
from src.memory.redis_memory import RedisMemory
from src.memory.sqlite_memory import SQLiteMemory

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """Orchestrates the multi-agent loan assessment pipeline."""

    def __init__(
        self,
        risk_agent: RiskScoringAgent | None = None,
        intent_agent: CustomerIntentAgent | None = None,
        policy_agent: PolicyValidationAgent | None = None,
        audit_agent: ComplianceAuditAgent | None = None,
        redis_memory: RedisMemory | None = None,
        sqlite_memory: SQLiteMemory | None = None,
    ):
        self._risk_agent = risk_agent or RiskScoringAgent()
        self._intent_agent = intent_agent or CustomerIntentAgent()
        self._policy_agent = policy_agent or PolicyValidationAgent()
        self._audit_agent = audit_agent or ComplianceAuditAgent()
        self._redis = redis_memory or RedisMemory()
        self._db = sqlite_memory or SQLiteMemory()

    async def process(self, request: LoanRequest) -> LoanAssessmentResponse:
        start = time.monotonic()
        logger.info("CoordinatorAgent starting pipeline for request_id=%s", request.request_id)

        # Check short-term cache
        cached = self._redis.get(f"assessment:{request.request_id}")
        if cached:
            logger.info("Cache hit for request_id=%s", request.request_id)
            return LoanAssessmentResponse(**cached)

        # Agent-to-Agent pipeline
        intent_result = await self._intent_agent.run(request)
        risk_result = await self._risk_agent.run(request)
        policy_result = await self._policy_agent.run(request, risk_result.risk_score)
        audit_result = await self._audit_agent.run(request, risk_result, policy_result)

        # Determine final decision
        decision = self._determine_decision(audit_result.is_approved, risk_result.risk_level.value)

        elapsed_ms = (time.monotonic() - start) * 1000

        response = LoanAssessmentResponse(
            request_id=request.request_id,
            customer_id=request.customer_id,
            decision=decision,
            customer_intent=intent_result,
            risk_scoring=risk_result,
            policy_validation=policy_result,
            compliance_audit=audit_result,
            processing_time_ms=round(elapsed_ms, 2),
            metadata={
                "pipeline_version": "1.0.0",
                "agents_invoked": ["CustomerIntentAgent", "RiskScoringAgent", "PolicyValidationAgent", "ComplianceAuditAgent"],
            },
        )

        # Cache result and persist
        self._redis.set(f"assessment:{request.request_id}", response.model_dump())
        self._db.save_assessment(
            request.request_id,
            request.customer_id,
            decision.value,
            response.model_dump(),
        )

        logger.info(
            "CoordinatorAgent completed request_id=%s decision=%s elapsed_ms=%.2f",
            request.request_id,
            decision,
            elapsed_ms,
        )
        return response

    @staticmethod
    def _determine_decision(is_approved: bool, risk_level: str) -> LoanDecision:
        if is_approved:
            return LoanDecision.APPROVED
        if risk_level == "critical":
            return LoanDecision.DENIED
        return LoanDecision.PENDING_REVIEW
