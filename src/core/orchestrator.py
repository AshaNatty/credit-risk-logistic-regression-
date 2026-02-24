"""Central orchestrator: wires registry, protocol, and agents together."""
from __future__ import annotations

from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.registry import AgentRegistry
from src.agents.task_agent import TaskAgent
from src.core.config import Settings
from src.core.logging_config import get_logger
from src.protocol.a2a_protocol import A2AProtocol
from src.protocol.message_schema import A2AMessage, AgentResponse

logger = get_logger(__name__)


class Orchestrator:
    """
    Top-level component that owns the registry and protocol handler.
    Bootstraps default agents on startup.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self.registry = AgentRegistry()
        self._protocol = A2AProtocol(self.registry)

    async def setup(self) -> None:
        """Initialise and register default agents."""
        coordinator = CoordinatorAgent(registry=self.registry)
        task_agent = TaskAgent()

        await self.registry.register(coordinator)
        await self.registry.register(task_agent)

        logger.info(
            "orchestrator_setup_complete",
            extra={"registered_count": len(self.registry._agents)},
        )

    async def teardown(self) -> None:
        await self.registry.shutdown_all()
        logger.info("orchestrator_teardown_complete")

    async def dispatch(self, message: A2AMessage) -> AgentResponse:
        return await self._protocol.dispatch(
            message, timeout=self._settings.task_timeout_seconds
        )
