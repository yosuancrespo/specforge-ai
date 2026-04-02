from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import DocumentChunk, SourceDocument

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


SUPPORTED_SUFFIXES = {".md", ".feature", ".yaml", ".yml", ".json", ".sol"}


def discover_documents(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )


def parse_document(path: Path) -> SourceDocument:
    content = path.read_text(encoding="utf-8")
    doc_type = detect_doc_type(path)
    metadata: dict[str, Any] = {"suffix": path.suffix.lower()}

    if doc_type == "markdown":
        metadata["headings"] = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
    elif doc_type == "gherkin":
        metadata["scenarios"] = re.findall(r"^\s*Scenario:\s+(.+)$", content, re.MULTILINE)
    elif doc_type == "openapi":
        metadata.update(_openapi_metadata(content))
    elif doc_type == "solidity":
        metadata["contracts"] = re.findall(r"contract\s+([A-Za-z0-9_]+)", content)
    elif doc_type == "json":
        metadata["keys"] = list(_safe_json(content).keys())

    return SourceDocument(
        id=_doc_id(path),
        title=path.stem.replace("-", " ").replace("_", " ").title(),
        path=str(path),
        doc_type=doc_type,
        content=content,
        metadata=metadata,
    )


def chunk_document(document: SourceDocument, max_chars: int = 450) -> list[DocumentChunk]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", document.content) if part.strip()]
    chunks: list[DocumentChunk] = []
    buffer = ""
    index = 0

    for paragraph in paragraphs:
        candidate = f"{buffer}\n\n{paragraph}".strip() if buffer else paragraph
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            chunks.append(
                DocumentChunk(
                    id=f"{document.id}-chunk-{index}",
                    document_id=document.id,
                    content=buffer,
                    metadata={"doc_type": document.doc_type, "chunk_index": index},
                )
            )
            index += 1
        buffer = paragraph

    if buffer:
        chunks.append(
            DocumentChunk(
                id=f"{document.id}-chunk-{index}",
                document_id=document.id,
                content=buffer,
                metadata={"doc_type": document.doc_type, "chunk_index": index},
            )
        )

    return chunks


def detect_doc_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".feature":
        return "gherkin"
    if suffix == ".sol":
        return "solidity"
    if suffix in {".yaml", ".yml"} and "openapi" in path.stem.lower():
        return "openapi"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    return "markdown"


def _doc_id(path: Path) -> str:
    normalized = str(path).replace("\\", "/")
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


def _openapi_metadata(content: str) -> dict[str, Any]:
    if yaml is None:
        return {"operations": [], "servers": []}
    parsed = yaml.safe_load(content) or {}
    operations: list[str] = []
    for route, methods in (parsed.get("paths") or {}).items():
        for method in methods or {}:
            operations.append(f"{method.upper()} {route}")
    return {
        "operations": operations,
        "servers": [server.get("url") for server in parsed.get("servers", [])],
        "schema_version": parsed.get("openapi", "unknown"),
    }


def _safe_json(content: str) -> dict[str, Any]:
    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}

