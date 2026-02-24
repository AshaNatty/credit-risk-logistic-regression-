"""Tests for A2A protocol dispatch and error handling."""
from __future__ import annotations

import pytest

from src.agents.registry import AgentRegistry
from src.agents.task_agent import TaskAgent
from src.protocol.a2a_protocol import A2AProtocol
from src.protocol.message_schema import A2AMessage, MessageType


@pytest.fixture
async def protocol_setup():
    registry = AgentRegistry()
    task = TaskAgent()
    await registry.register(task)
    protocol = A2AProtocol(registry)
    yield protocol, registry, task
    await registry.shutdown_all()


@pytest.mark.asyncio
async def test_dispatch_success(protocol_setup):
    protocol, _, task = protocol_setup
    msg = A2AMessage(
        sender_id="test",
        recipient_id=task.agent_id,
        message_type=MessageType.TASK_REQUEST,
        payload={"task_type": "ping", "data": {}},
    )
    response = await protocol.dispatch(msg)
    assert response.success is True


@pytest.mark.asyncio
async def test_dispatch_unknown_agent(protocol_setup):
    protocol, _, _ = protocol_setup
    msg = A2AMessage(
        sender_id="test",
        recipient_id="nonexistent-id",
        message_type=MessageType.TASK_REQUEST,
        payload={},
    )
    response = await protocol.dispatch(msg)
    assert response.success is False
    assert "No agent found" in response.error


@pytest.mark.asyncio
async def test_dispatch_timeout(protocol_setup, monkeypatch):
    import asyncio
    protocol, _, task = protocol_setup

    async def slow_handle(message):
        await asyncio.sleep(10)

    monkeypatch.setattr(task, "handle", slow_handle)

    msg = A2AMessage(
        sender_id="test",
        recipient_id=task.agent_id,
        message_type=MessageType.TASK_REQUEST,
        payload={},
    )
    response = await protocol.dispatch(msg, timeout=0.01)
    assert response.success is False
    assert "timed out" in response.error.lower()
