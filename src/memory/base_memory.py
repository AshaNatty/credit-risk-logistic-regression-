"""Abstract interface for all memory backends."""
from __future__ import annotations

import abc
from typing import Any, Optional


class BaseMemory(abc.ABC):
    """Base class defining the memory contract for all agents."""

    @abc.abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Persist a key-value pair."""

    @abc.abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key, returning None if not found."""

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key from the store."""

    @abc.abstractmethod
    async def clear(self) -> None:
        """Wipe all stored entries."""

    @abc.abstractmethod
    async def exists(self, key: str) -> bool:
        """Return True if the key exists."""
