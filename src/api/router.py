"""FastAPI route definitions for the agent orchestration API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Optional

from src.core.metrics import REQUEST_COUNT, REQUEST_LATENCY
from src.core.orchestrator import Orchestrator
from src.protocol.message_schema import A2AMessage, AgentResponse, MessageType

router = APIRouter(prefix="/api/v1", tags=["agents"])


def get_orchestrator() -> Orchestrator:
    from src.api.main import app
    return app.state.orchestrator


class TaskRequest(BaseModel):
    sender_id: str = "api_client"
    task_type: str
    data: Optional[dict[str, Any]] = None
    recipient_id: Optional[str] = None


@router.post("/tasks", response_model=AgentResponse, status_code=status.HTTP_200_OK)
async def submit_task(
    request: TaskRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> AgentResponse:
    """Submit a task to the orchestrator for routing."""
    REQUEST_COUNT.labels(endpoint="/tasks", method="POST").inc()
    with REQUEST_LATENCY.labels(endpoint="/tasks").time():
        message = A2AMessage(
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            message_type=MessageType.TASK_REQUEST,
            payload={"task_type": request.task_type, "data": request.data or {}},
        )
        return await orchestrator.dispatch(message)


@router.get("/agents", status_code=status.HTTP_200_OK)
async def list_agents(
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> dict:
    """List all registered agents."""
    REQUEST_COUNT.labels(endpoint="/agents", method="GET").inc()
    return {"agents": orchestrator.registry.list_agents()}


@router.get("/agents/{agent_id}/health", status_code=status.HTTP_200_OK)
async def agent_health(
    agent_id: str,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> dict:
    """Health check for a specific agent."""
    agent = orchestrator.registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found.")
    return await agent.health_check()


@router.get("/health", status_code=status.HTTP_200_OK)
async def system_health() -> dict:
    """Overall system health."""
    return {"status": "healthy"}
