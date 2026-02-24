"""Chroma vector store adapter stub.

Replace the stub methods with real ChromaDB client calls once
`chromadb` is added to requirements.txt and a Chroma server is available.
"""
from __future__ import annotations

from typing import Any, Optional

from src.core.logging_config import get_logger
from src.retrieval.base_vector_store import BaseVectorStore

logger = get_logger(__name__)


class ChromaAdapterStub(BaseVectorStore):
    """
    Stub adapter for ChromaDB.

    Usage (production):
        import chromadb
        self._client = chromadb.HttpClient(host=host, port=port)
        self._collection = self._client.get_or_create_collection(collection_name)
    """

    def __init__(self, collection_name: str = "default") -> None:
        self._collection_name = collection_name
        self._store: dict[str, dict] = {}
        logger.info(
            "chroma_adapter_init",
            extra={"collection": collection_name, "mode": "stub"},
        )

    async def add(self, doc_id: str, text: str, metadata: Optional[dict] = None) -> None:
        self._store[doc_id] = {"text": text, "metadata": metadata or {}}
        logger.debug("chroma_add", extra={"doc_id": doc_id})

    async def query(self, query_text: str, top_k: int = 5) -> list[dict[str, Any]]:
        # Stub: return all docs up to top_k (no real embedding)
        results = list(self._store.values())[:top_k]
        logger.debug(
            "chroma_query",
            extra={"query": query_text, "results_count": len(results)},
        )
        return results

    async def delete(self, doc_id: str) -> None:
        self._store.pop(doc_id, None)

    async def clear(self) -> None:
        self._store.clear()
