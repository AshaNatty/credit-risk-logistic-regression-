"""TaskAgent: executes concrete tasks delegated by the CoordinatorAgent."""
from __future__ import annotations

from src.agents.base_agent import BaseAgent
from src.core.logging_config import get_logger
from src.memory.short_term import ShortTermMemory
from src.protocol.message_schema import A2AMessage, AgentResponse, MessageType

logger = get_logger(__name__)


class TaskAgent(BaseAgent):
    """
    General-purpose task executor.  Stores results in short-term memory
    and returns structured responses.
    """

    AGENT_TYPE = "task"

    def __init__(self) -> None:
        super().__init__(
            agent_type=self.AGENT_TYPE,
            capabilities=["execute", "store", "retrieve"],
        )
        self._memory = ShortTermMemory()

    async def startup(self) -> None:
        logger.info("task_agent_startup", extra={"agent_id": self.agent_id})

    async def shutdown(self) -> None:
        await self._memory.clear()
        logger.info("task_agent_shutdown", extra={"agent_id": self.agent_id})

    async def handle(self, message: A2AMessage) -> AgentResponse:
        logger.info(
            "task_agent_received",
            extra={"message_id": message.message_id, "msg_type": message.message_type},
        )

        if message.message_type == MessageType.TASK_REQUEST:
            result = await self._execute_task(message)
            return result
        elif message.message_type == MessageType.MEMORY_QUERY:
            key = (message.payload or {}).get("key")
            value = await self._memory.retrieve(key) if key else None
            return AgentResponse(
                agent_id=self.agent_id,
                message_id=message.message_id,
                success=True,
                payload={"key": key, "value": value},
            )
        else:
            return AgentResponse(
                agent_id=self.agent_id,
                message_id=message.message_id,
                success=False,
                error=f"Unsupported message type: {message.message_type}",
            )

    async def _execute_task(self, message: A2AMessage) -> AgentResponse:
        payload = message.payload or {}
        task_type = payload.get("task_type", "generic")
        task_data = payload.get("data", {})

        # Simulate task execution (replace with real logic)
        result = {"task_type": task_type, "processed": True, "input": task_data}

        await self._memory.store(f"task:{message.message_id}", result)

        return AgentResponse(
            agent_id=self.agent_id,
            message_id=message.message_id,
            success=True,
            payload=result,
        )
