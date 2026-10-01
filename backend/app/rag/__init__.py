"""RAG stubs — document indexing/retrieval reserved for later phases."""

from abc import ABC, abstractmethod
from typing import Any


class RAGStore(ABC):
    @abstractmethod
    async def upsert(self, documents: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def query(self, text: str, top_k: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError


class NoOpRAGStore(RAGStore):
    async def upsert(self, documents: list[dict[str, Any]]) -> None:
        raise NotImplementedError("RAG is not enabled in Phase 1 (Foundation).")

    async def query(self, text: str, top_k: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError("RAG is not enabled in Phase 1 (Foundation).")
