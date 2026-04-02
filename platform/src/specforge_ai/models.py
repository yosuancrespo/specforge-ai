from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ArtifactKind(str, Enum):
    SOURCE_BUNDLE = "source-bundle"
    QUALITY_PLAN = "quality-plan"
    GENERATED_TESTS = "generated-tests"
    RUN_RESULT = "run-result"
    EVAL_RESULT = "eval-result"
    RELEASE_REPORT = "release-report"


@dataclass
class SourceDocument:
    id: str
    title: str
    path: str
    doc_type: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentChunk:
    id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Requirement:
    id: str
    statement: str
    source_ids: list[str]
    priority: str = "high"


@dataclass
class RiskItem:
    id: str
    title: str
    rationale: str
    related_requirements: list[str]
    severity: str = "medium"


@dataclass
class TestCase:
    id: str
    title: str
    adapter: str
    objective: str
    steps: list[str]
    assertions: list[str]
    source_ids: list[str]
    tags: list[str] = field(default_factory=list)


@dataclass
class Finding:
    id: str
    title: str
    severity: str
    summary: str
    evidence: list[str]


@dataclass
class AdapterRun:
    adapter: str
    status: str
    findings: list[Finding] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalMetric:
    name: str
    score: float
    threshold: float
    passed: bool
    notes: str


@dataclass
class ReleaseReport:
    run_id: str
    recommendation: str
    summary: str
    highlights: list[str]
    findings: list[Finding]
    metrics: list[EvalMetric]
    generated_at: str = field(default_factory=utc_now)


@dataclass
class ArtifactEnvelope:
    kind: ArtifactKind
    created_at: str
    payload: dict[str, Any]


def jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if is_dataclass(value):
        return jsonable(asdict(value))
    return value

