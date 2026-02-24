"""Pydantic schemas that define the Agent-to-Agent (A2A) wire protocol."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HEALTH_CHECK = "health_check"
    MEMORY_QUERY = "memory_query"
    BROADCAST = "broadcast"
    ERROR = "error"


class A2AMessage(BaseModel):
    """Envelope for all inter-agent communication."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: Optional[str] = None
    message_type: MessageType
    payload: Optional[dict[str, Any]] = None
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ttl_seconds: int = Field(default=60, ge=1)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class AgentResponse(BaseModel):
    """Standardised response envelope returned by every agent handler."""

    agent_id: str
    message_id: str
    success: bool
    payload: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}
