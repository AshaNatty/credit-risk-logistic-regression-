"""A2A protocol handler: validation, routing, and error wrapping."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from src.core.logging_config import get_logger
from src.protocol.message_schema import A2AMessage, AgentResponse, MessageType

if TYPE_CHECKING:
    from src.agents.registry import AgentRegistry

logger = get_logger(__name__)


class A2AProtocol:
    """
    Handles message routing between agents through the registry.
    Provides validation, timeout enforcement, and error normalisation.
    """

    DEFAULT_TIMEOUT_SECONDS = 30.0

    def __init__(self, registry: "AgentRegistry") -> None:
        self._registry = registry

    async def dispatch(
        self, message: A2AMessage, timeout: float = DEFAULT_TIMEOUT_SECONDS
    ) -> AgentResponse:
        """Dispatch a message to the target agent, enforcing a timeout."""
        try:
            target = self._resolve_target(message)
            if target is None:
                return self._error_response(
                    message, f"No agent found for recipient '{message.recipient_id}'"
                )

            logger.info(
                "a2a_dispatch",
                extra={
                    "message_id": message.message_id,
                    "sender_id": message.sender_id,
                    "recipient_id": message.recipient_id,
                    "message_type": message.message_type,
                },
            )

            response = await asyncio.wait_for(target.handle(message), timeout=timeout)
            return response

        except asyncio.TimeoutError:
            logger.error(
                "a2a_timeout",
                extra={"message_id": message.message_id, "timeout": timeout},
            )
            return self._error_response(message, f"Agent timed out after {timeout}s")
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "a2a_dispatch_error",
                extra={"message_id": message.message_id, "error": str(exc)},
            )
            return self._error_response(message, str(exc))

    def _resolve_target(self, message: A2AMessage):
        if message.recipient_id:
            return self._registry.get(message.recipient_id)
        # Broadcast to first coordinator
        coordinators = self._registry.get_by_type("coordinator")
        return coordinators[0] if coordinators else None

    @staticmethod
    def _error_response(message: A2AMessage, error: str) -> AgentResponse:
        return AgentResponse(
            agent_id="protocol",
            message_id=message.message_id,
            success=False,
            error=error,
        )
