from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class LoanPurpose(str, Enum):
    HOME = "home"
    AUTO = "auto"
    BUSINESS = "business"
    PERSONAL = "personal"
    EDUCATION = "education"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LoanRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = Field(..., description="Unique customer identifier")
    annual_income: float = Field(..., gt=0, description="Annual income in USD")
    monthly_debt: float = Field(..., ge=0, description="Total monthly debt obligations")
    loan_amount: float = Field(..., gt=0, description="Requested loan amount")
    loan_term_months: int = Field(..., ge=6, le=360, description="Loan term in months")
    interest_rate: float = Field(..., gt=0, le=100, description="Annual interest rate (%)")
    credit_score: int = Field(..., ge=300, le=850, description="FICO credit score")
    employment_years: float = Field(..., ge=0, description="Years of employment")
    loan_purpose: LoanPurpose = Field(..., description="Purpose of the loan")


class AmortizationEntry(BaseModel):
    month: int
    payment: float
    principal: float
    interest: float
    balance: float


class RiskScoringResult(BaseModel):
    debt_to_income_ratio: float
    monthly_payment: float
    total_interest: float
    total_cost: float
    risk_score: float
    risk_level: RiskLevel
    amortization_schedule: List[AmortizationEntry] = Field(default_factory=list)
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)


class PolicyClause(BaseModel):
    clause_id: str
    title: str
    content: str
    relevance_score: float


class PolicyValidationResult(BaseModel):
    is_compliant: bool
    policy_clauses: List[PolicyClause]
    validation_notes: str
    grounded_assessment: str


class AuditEntry(BaseModel):
    timestamp: str
    agent: str
    action: str
    input_summary: str
    output_summary: str
    reasoning: str


class ComplianceAuditResult(BaseModel):
    audit_id: str
    is_approved: bool
    reasoning_trace: List[AuditEntry]
    audit_report: str
    recommendations: List[str]


class CustomerIntentResult(BaseModel):
    intent_summary: str
    risk_indicators: List[str]
    confidence_score: float


class LoanDecision(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING_REVIEW = "pending_review"


class LoanAssessmentResponse(BaseModel):
    request_id: str
    customer_id: str
    decision: LoanDecision
    customer_intent: CustomerIntentResult
    risk_scoring: RiskScoringResult
    policy_validation: PolicyValidationResult
    compliance_audit: ComplianceAuditResult
    processing_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
