"""CoordinatorAgent: routes incoming tasks to appropriate TaskAgents."""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.agents.base_agent import BaseAgent
from src.core.logging_config import get_logger
from src.protocol.message_schema import A2AMessage, AgentResponse, MessageType

if TYPE_CHECKING:
    from src.agents.registry import AgentRegistry

logger = get_logger(__name__)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator that receives orchestration messages and delegates
    subtasks to registered TaskAgents.
    """

    AGENT_TYPE = "coordinator"

    def __init__(self, registry: "AgentRegistry") -> None:
        super().__init__(
            agent_type=self.AGENT_TYPE,
            capabilities=["route", "delegate", "aggregate"],
        )
        self._registry = registry

    async def startup(self) -> None:
        logger.info("coordinator_startup", extra={"agent_id": self.agent_id})

    async def shutdown(self) -> None:
        logger.info("coordinator_shutdown", extra={"agent_id": self.agent_id})

    async def handle(self, message: A2AMessage) -> AgentResponse:
        logger.info(
            "coordinator_received",
            extra={"message_id": message.message_id, "msg_type": message.message_type},
        )

        if message.message_type == MessageType.TASK_REQUEST:
            return await self._delegate_task(message)
        elif message.message_type == MessageType.HEALTH_CHECK:
            return AgentResponse(
                agent_id=self.agent_id,
                message_id=message.message_id,
                success=True,
                payload={"status": "ok", "registered_agents": self._registry.count()},
            )
        else:
            return AgentResponse(
                agent_id=self.agent_id,
                message_id=message.message_id,
                success=False,
                error=f"Unsupported message type: {message.message_type}",
            )

    async def _delegate_task(self, message: A2AMessage) -> AgentResponse:
        task_type = (message.payload or {}).get("task_type", "")
        candidates = self._registry.get_by_type("task")

        if not candidates:
            return AgentResponse(
                agent_id=self.agent_id,
                message_id=message.message_id,
                success=False,
                error="No TaskAgents available.",
            )

        target = candidates[0]
        logger.info(
            "coordinator_delegating",
            extra={"target_agent_id": target.agent_id, "task_type": task_type},
        )
        return await target.handle(message)
