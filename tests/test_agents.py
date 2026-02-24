"""Tests for BaseAgent, AgentRegistry, CoordinatorAgent, and TaskAgent."""
from __future__ import annotations

import pytest

from src.agents.registry import AgentRegistry
from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.task_agent import TaskAgent
from src.protocol.message_schema import A2AMessage, MessageType


@pytest.fixture
async def registry():
    r = AgentRegistry()
    yield r
    await r.shutdown_all()


@pytest.fixture
async def populated_registry():
    r = AgentRegistry()
    coordinator = CoordinatorAgent(registry=r)
    task = TaskAgent()
    await r.register(coordinator)
    await r.register(task)
    yield r, coordinator, task
    await r.shutdown_all()


@pytest.mark.asyncio
async def test_register_agent(registry):
    task = TaskAgent()
    await registry.register(task)
    assert registry.get(task.agent_id) is task


@pytest.mark.asyncio
async def test_deregister_agent(registry):
    task = TaskAgent()
    await registry.register(task)
    await registry.deregister(task.agent_id)
    assert registry.get(task.agent_id) is None


@pytest.mark.asyncio
async def test_duplicate_registration_raises(registry):
    task = TaskAgent()
    await registry.register(task)
    with pytest.raises(ValueError):
        await registry.register(task)


@pytest.mark.asyncio
async def test_task_agent_handles_task(populated_registry):
    _, _, task = populated_registry
    msg = A2AMessage(
        sender_id="test",
        recipient_id=task.agent_id,
        message_type=MessageType.TASK_REQUEST,
        payload={"task_type": "echo", "data": {"value": 42}},
    )
    response = await task.handle(msg)
    assert response.success is True
    assert response.payload["processed"] is True


@pytest.mark.asyncio
async def test_coordinator_delegates_to_task(populated_registry):
    _, coordinator, _ = populated_registry
    msg = A2AMessage(
        sender_id="test",
        recipient_id=coordinator.agent_id,
        message_type=MessageType.TASK_REQUEST,
        payload={"task_type": "echo", "data": {}},
    )
    response = await coordinator.handle(msg)
    assert response.success is True


@pytest.mark.asyncio
async def test_health_check(populated_registry):
    _, _, task = populated_registry
    health = await task.health_check()
    assert health["status"] == "healthy"
    assert health["agent_type"] == "task"
