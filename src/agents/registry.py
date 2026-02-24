"""Thread-safe agent registry for discovery and lifecycle management."""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from src.agents.base_agent import BaseAgent
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    """Singleton-style registry that maps agent IDs to live agent instances."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._lock = asyncio.Lock()

    async def register(self, agent: BaseAgent) -> None:
        async with self._lock:
            if agent.agent_id in self._agents:
                raise ValueError(f"Agent {agent.agent_id} is already registered.")
            self._agents[agent.agent_id] = agent
            await agent.startup()
            agent._is_running = True
            logger.info(
                "agent_registered",
                extra={"agent_id": agent.agent_id, "agent_type": agent.agent_type},
            )

    async def deregister(self, agent_id: str) -> None:
        async with self._lock:
            agent = self._agents.pop(agent_id, None)
            if agent:
                await agent.shutdown()
                agent._is_running = False
                logger.info("agent_deregistered", extra={"agent_id": agent_id})

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def get_by_type(self, agent_type: str) -> list[BaseAgent]:
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def count(self) -> int:
        """Return the number of currently registered agents."""
        return len(self._agents)

    def list_agents(self) -> list[dict]:
        return [
            {
                "agent_id": a.agent_id,
                "agent_type": a.agent_type,
                "capabilities": a.metadata.capabilities,
            }
            for a in self._agents.values()
        ]

    async def shutdown_all(self) -> None:
        async with self._lock:
            for agent in list(self._agents.values()):
                await agent.shutdown()
                agent._is_running = False
            self._agents.clear()
            logger.info("all_agents_shutdown")
