"""PolicyValidationAgent – RAG-enabled policy retrieval and grounding."""
from __future__ import annotations

import logging
import uuid
from typing import List

from src.api.schemas import LoanRequest, PolicyClause, PolicyValidationResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static policy corpus (stub for Chroma vector store integration)
# ---------------------------------------------------------------------------
_POLICY_CORPUS = [
    {
        "id": "POL-001",
        "title": "Debt-to-Income Limit",
        "content": (
            "Borrowers must have a debt-to-income ratio (DTI) of 43% or below. "
            "Exceptions may be granted for strong compensating factors such as high "
            "credit scores (>760) or significant liquid assets."
        ),
        "keywords": ["dti", "debt-to-income", "ratio"],
    },
    {
        "id": "POL-002",
        "title": "Minimum Credit Score",
        "content": (
            "A minimum FICO credit score of 620 is required for conventional loans. "
            "FHA-backed loans may accept scores as low as 580 with a 3.5% down payment."
        ),
        "keywords": ["credit", "score", "fico"],
    },
    {
        "id": "POL-003",
        "title": "Employment Stability",
        "content": (
            "Applicants must demonstrate a minimum of 2 years of continuous employment "
            "or verifiable self-employment income. Gaps in employment exceeding 6 months "
            "require documented explanation."
        ),
        "keywords": ["employment", "job", "stability"],
    },
    {
        "id": "POL-004",
        "title": "Loan-to-Value Ratio",
        "content": (
            "Residential mortgage loans must not exceed a loan-to-value ratio of 80% "
            "without private mortgage insurance (PMI). For personal loans, maximum "
            "loan-to-income ratio is 4x annual income."
        ),
        "keywords": ["loan", "value", "income", "ltv"],
    },
    {
        "id": "POL-005",
        "title": "Anti-Money Laundering",
        "content": (
            "All loan applications exceeding $10,000 must undergo AML screening. "
            "Customer identity verification must comply with KYC regulations. "
            "Suspicious activity must be reported to the compliance officer."
        ),
        "keywords": ["aml", "money", "laundering", "kyc", "compliance"],
    },
]


class ChromaVectorStoreStub:
    """Stub implementation of Chroma vector store for policy retrieval."""

    def __init__(self, persist_dir: str | None = None, collection: str | None = None):
        from src.utils.config import settings
        self._persist_dir = persist_dir or settings.chroma_persist_dir
        self._collection = collection or settings.chroma_collection
        logger.info(
            "ChromaVectorStoreStub initialised (persist_dir=%s, collection=%s)",
            self._persist_dir,
            self._collection,
        )

    def similarity_search(self, query: str, top_k: int = 3) -> List[dict]:
        """Keyword-based similarity (stub). Replace with real Chroma embeddings."""
        query_lower = query.lower()
        scored = []
        for doc in _POLICY_CORPUS:
            score = sum(1 for kw in doc["keywords"] if kw in query_lower)
            scored.append((score, doc))
        scored.sort(key=lambda x: -x[0])
        return [doc for _, doc in scored[:top_k]]


class PolicyValidationAgent:
    """Retrieves relevant policy clauses and validates loan compliance (RAG)."""

    def __init__(self, vector_store: ChromaVectorStoreStub | None = None):
        self._vector_store = vector_store or ChromaVectorStoreStub()

    async def run(self, request: LoanRequest, risk_score: float) -> PolicyValidationResult:
        logger.info("PolicyValidationAgent processing request_id=%s", request.request_id)

        query = self._build_query(request, risk_score)
        raw_docs = self._vector_store.similarity_search(query, top_k=3)

        policy_clauses = [
            PolicyClause(
                clause_id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                relevance_score=round(0.9 - idx * 0.1, 2),
            )
            for idx, doc in enumerate(raw_docs)
        ]

        is_compliant, notes = self._validate_compliance(request, risk_score)
        grounded = self._ground_assessment(request, risk_score, policy_clauses, is_compliant)

        return PolicyValidationResult(
            is_compliant=is_compliant,
            policy_clauses=policy_clauses,
            validation_notes=notes,
            grounded_assessment=grounded,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_query(request: LoanRequest, risk_score: float) -> str:
        monthly_income = request.annual_income / 12
        dti = request.monthly_debt / monthly_income if monthly_income > 0 else 1.0
        return (
            f"loan dti {dti:.2f} credit score {request.credit_score} "
            f"employment {request.employment_years} risk {risk_score:.2f} "
            f"loan amount {request.loan_amount} income {request.annual_income}"
        )

    @staticmethod
    def _validate_compliance(request: LoanRequest, risk_score: float) -> tuple[bool, str]:
        monthly_income = request.annual_income / 12
        dti = request.monthly_debt / monthly_income if monthly_income > 0 else 1.0
        violations = []

        if dti > 0.43:
            violations.append(f"DTI ratio {dti:.2%} exceeds 43% limit (POL-001)")
        if request.credit_score < 620:
            violations.append(f"Credit score {request.credit_score} below 620 minimum (POL-002)")
        if request.employment_years < 2:
            violations.append(f"Employment {request.employment_years}y below 2-year minimum (POL-003)")
        if request.loan_amount > request.annual_income * 4:
            violations.append(
                f"Loan-to-income ratio {request.loan_amount / request.annual_income:.1f}x exceeds 4x limit (POL-004)"
            )

        if violations:
            return False, "Policy violations: " + "; ".join(violations)
        return True, "All policy checks passed."

    @staticmethod
    def _ground_assessment(
        request: LoanRequest,
        risk_score: float,
        clauses: List[PolicyClause],
        is_compliant: bool,
    ) -> str:
        clause_refs = ", ".join(c.clause_id for c in clauses)
        status = "compliant" if is_compliant else "non-compliant"
        return (
            f"Based on retrieved policy clauses [{clause_refs}], the application is {status}. "
            f"Risk score of {risk_score:.2f} was considered alongside customer profile "
            f"(credit score: {request.credit_score}, employment: {request.employment_years}y). "
            f"Assessment grounded in institutional lending policies."
        )
