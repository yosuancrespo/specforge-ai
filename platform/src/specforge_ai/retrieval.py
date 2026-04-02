from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Protocol

from .models import DocumentChunk


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


@dataclass
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


class VectorStore(Protocol):
    def add(self, chunks: list[DocumentChunk]) -> None:
        ...

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        ...


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []

    def add(self, chunks: list[DocumentChunk]) -> None:
        self._chunks.extend(chunks)

    def search(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        query_tokens = _tokenize(query)
        results: list[RetrievedChunk] = []
        for chunk in self._chunks:
            chunk_tokens = _tokenize(chunk.content)
            overlap = len(query_tokens & chunk_tokens)
            if overlap == 0:
                continue
            score = overlap / math.sqrt(max(len(query_tokens), 1) * max(len(chunk_tokens), 1))
            results.append(RetrievedChunk(chunk=chunk, score=round(score, 4)))
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]


class PgVectorStore(InMemoryVectorStore):
    """Pgvector-ready placeholder with deterministic lexical fallback."""

    def __init__(self, database_url: str) -> None:
        super().__init__()
        self.database_url = database_url


class Retriever:
    def __init__(self, store: VectorStore) -> None:
        self.store = store

    def index(self, chunks: list[DocumentChunk]) -> None:
        self.store.add(chunks)

    def query(self, question: str, top_k: int = 5) -> list[RetrievedChunk]:
        return self.store.search(question, top_k=top_k)

