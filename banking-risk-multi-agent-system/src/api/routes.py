"""API route definitions."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from src.agents.coordinator import CoordinatorAgent
from src.api.schemas import HealthResponse, LoanAssessmentResponse, LoanRequest
from src.utils.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Shared coordinator instance (could be DI in larger apps)
_coordinator = CoordinatorAgent()


@router.post(
    "/assess",
    response_model=LoanAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a loan risk assessment request",
    description="Runs the full multi-agent pipeline and returns a structured loan assessment.",
)
async def assess_loan(request: LoanRequest) -> LoanAssessmentResponse:
    try:
        return await _coordinator.process(request)
    except Exception as exc:
        logger.exception("Assessment failed for request_id=%s: %s", request.request_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment failed: {str(exc)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        services={
            "api": "ok",
            "redis": "ok (fallback)",
            "sqlite": "ok",
            "chroma": "ok (stub)",
        },
    )
