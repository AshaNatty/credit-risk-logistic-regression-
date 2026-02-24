"""Application settings loaded from environment variables."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "agentic-ai-core-framework"
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]
    max_agents: int = 50
    task_timeout_seconds: float = 30.0
    short_term_memory_max_size: int = 1000
    long_term_memory_path: str = "/tmp/agent_long_term_memory.json"
    chroma_collection_name: str = "agent_knowledge"
    prometheus_port: int = 9090
