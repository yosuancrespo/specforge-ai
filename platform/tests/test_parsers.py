from pathlib import Path

from specforge_ai.parsers import chunk_document, parse_document


def test_parse_markdown_document(tmp_path: Path) -> None:
    path = tmp_path / "product-spec.md"
    path.write_text("# Title\n\nThe amount must be positive.\n", encoding="utf-8")

    document = parse_document(path)

    assert document.doc_type == "markdown"
    assert document.metadata["headings"] == ["Title"]


def test_chunk_document_returns_stable_chunks(tmp_path: Path) -> None:
    path = tmp_path / "notes.md"
    path.write_text("Paragraph one.\n\nParagraph two.\n\nParagraph three.", encoding="utf-8")

    document = parse_document(path)
    chunks = chunk_document(document, max_chars=25)

    assert len(chunks) == 3
    assert chunks[0].metadata["chunk_index"] == 0

