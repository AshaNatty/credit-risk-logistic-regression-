"""Long-term memory stub — can be backed by any persistent store."""
from __future__ import annotations

import json
import asyncio
from pathlib import Path
from typing import Any, Optional

from src.memory.base_memory import BaseMemory


class LongTermMemory(BaseMemory):
    """
    File-backed long-term memory (JSON).  Replace with a database adapter
    (e.g., Redis, Postgres, DynamoDB) in production.
    """

    def __init__(self, storage_path: str = "./data/agent_long_term_memory.json") -> None:
        self._path = Path(storage_path)
        self._lock = asyncio.Lock()
        if not self._path.exists():
            self._path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self._path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    async def store(self, key: str, value: Any) -> None:
        async with self._lock:
            data = self._load()
            data[key] = value
            self._save(data)

    async def retrieve(self, key: str) -> Optional[Any]:
        async with self._lock:
            return self._load().get(key)

    async def delete(self, key: str) -> None:
        async with self._lock:
            data = self._load()
            data.pop(key, None)
            self._save(data)

    async def clear(self) -> None:
        async with self._lock:
            self._save({})

    async def exists(self, key: str) -> bool:
        async with self._lock:
            return key in self._load()
