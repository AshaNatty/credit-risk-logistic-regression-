"""Pluggable vector store interface."""
from __future__ import annotations

import abc
from typing import Any, Optional


class BaseVectorStore(abc.ABC):
    """
    Abstract interface for a vector / semantic search store.
    Implement this to plug in ChromaDB, Pinecone, Weaviate, etc.
    """

    @abc.abstractmethod
    async def add(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> None:
        """Add or update a document embedding."""

    @abc.abstractmethod
    async def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Return the top-k most similar documents."""

    @abc.abstractmethod
    async def delete(self, doc_id: str) -> None:
        """Remove a document from the store."""

    @abc.abstractmethod
    async def clear(self) -> None:
        """Drop all documents from the store."""
