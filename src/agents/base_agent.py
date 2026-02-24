"""Abstract base class for all agents in the framework."""
from __future__ import annotations

import abc
import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from src.protocol.message_schema import A2AMessage, AgentResponse


class AgentMetadata(BaseModel):
    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    capabilities: list[str] = Field(default_factory=list)


class BaseAgent(abc.ABC):
    """Abstract base class that every agent must extend."""

    def __init__(self, agent_type: str, capabilities: list[str] | None = None) -> None:
        self.metadata = AgentMetadata(
            agent_type=agent_type,
            capabilities=capabilities or [],
        )
        self._is_running = False

    @property
    def agent_id(self) -> str:
        return self.metadata.agent_id

    @property
    def agent_type(self) -> str:
        return self.metadata.agent_type

    @abc.abstractmethod
    async def handle(self, message: A2AMessage) -> AgentResponse:
        """Process an incoming A2A message and return a structured response."""

    @abc.abstractmethod
    async def startup(self) -> None:
        """Lifecycle hook called when the agent starts."""

    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Lifecycle hook called when the agent stops."""

    async def health_check(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": "healthy" if self._is_running else "stopped",
            "capabilities": self.metadata.capabilities,
        }
