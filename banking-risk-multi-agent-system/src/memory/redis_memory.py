"""Short-term memory backed by Redis (with in-memory fallback for testing)."""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class RedisMemory:
    """Short-term session memory using Redis."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        self._ttl = ttl
        self._fallback: dict[str, str] = {}
        self._client: Any = None
        try:
            import redis  # type: ignore
            self._client = redis.from_url(redis_url, decode_responses=True)
            self._client.ping()
            logger.info("Redis connection established")
        except Exception as exc:
            logger.warning("Redis unavailable, using in-memory fallback: %s", exc)
            self._client = None

    def set(self, key: str, value: Any) -> None:
        serialized = json.dumps(value)
        if self._client:
            try:
                self._client.setex(key, self._ttl, serialized)
                return
            except Exception as exc:
                logger.warning("Redis set failed, using fallback: %s", exc)
        self._fallback[key] = serialized

    def get(self, key: str) -> Optional[Any]:
        if self._client:
            try:
                raw = self._client.get(key)
                if raw:
                    return json.loads(raw)
                return None
            except Exception as exc:
                logger.warning("Redis get failed, using fallback: %s", exc)
        raw = self._fallback.get(key)
        return json.loads(raw) if raw else None

    def delete(self, key: str) -> None:
        if self._client:
            try:
                self._client.delete(key)
                return
            except Exception as exc:
                logger.warning("Redis delete failed: %s", exc)
        self._fallback.pop(key, None)

    def exists(self, key: str) -> bool:
        if self._client:
            try:
                return bool(self._client.exists(key))
            except Exception as exc:
                logger.warning("Redis exists check failed: %s", exc)
        return key in self._fallback
