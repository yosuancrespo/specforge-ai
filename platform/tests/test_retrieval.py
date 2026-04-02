from specforge_ai.models import DocumentChunk
from specforge_ai.retrieval import InMemoryVectorStore, Retriever


def test_retriever_prioritizes_relevant_chunks() -> None:
    retriever = Retriever(InMemoryVectorStore())
    retriever.index(
        [
            DocumentChunk(id="1", document_id="doc-1", content="amount must be positive"),
            DocumentChunk(id="2", document_id="doc-2", content="escrow contract emits release event"),
        ]
    )

    results = retriever.query("positive amount validation", top_k=1)

    assert results
    assert results[0].chunk.id == "1"

