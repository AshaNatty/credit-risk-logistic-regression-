"""In-process short-term memory backed by a bounded dictionary."""
from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Any, Optional

from src.memory.base_memory import BaseMemory


class ShortTermMemory(BaseMemory):
    """
    Fast, in-process memory with an optional max-size eviction policy (LRU).
    Suitable for within-session context.
    """

    def __init__(self, max_size: int = 1000) -> None:
        self._store: OrderedDict[str, Any] = OrderedDict()
        self._max_size = max_size
        self._lock = asyncio.Lock()

    async def store(self, key: str, value: Any) -> None:
        async with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = value
            if len(self._store) > self._max_size:
                self._store.popitem(last=False)

    async def retrieve(self, key: str) -> Optional[Any]:
        async with self._lock:
            value = self._store.get(key)
            if value is not None:
                self._store.move_to_end(key)
            return value

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)

    async def clear(self) -> None:
        async with self._lock:
            self._store.clear()

    async def exists(self, key: str) -> bool:
        async with self._lock:
            return key in self._store
