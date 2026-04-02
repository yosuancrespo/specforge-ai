from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import ArtifactEnvelope, ArtifactKind, jsonable, utc_now


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _kind_dir(self, kind: ArtifactKind) -> Path:
        target = self.root / kind.value
        target.mkdir(parents=True, exist_ok=True)
        return target

    def write_json(self, kind: ArtifactKind, stem: str, payload: dict[str, Any]) -> Path:
        target = self._kind_dir(kind) / f"{self._timestamp()}-{stem}.json"
        envelope = ArtifactEnvelope(kind=kind, created_at=utc_now(), payload=payload)
        target.write_text(json.dumps(jsonable(envelope), indent=2), encoding="utf-8")
        return target

    def write_text(self, kind: ArtifactKind, stem: str, content: str, suffix: str = ".md") -> Path:
        target = self._kind_dir(kind) / f"{self._timestamp()}-{stem}{suffix}"
        target.write_text(content, encoding="utf-8")
        return target

    def latest_payload(self, kind: ArtifactKind) -> dict[str, Any] | None:
        files = sorted(self._kind_dir(kind).glob("*.json"))
        if not files:
            return None
        payload = json.loads(files[-1].read_text(encoding="utf-8"))
        return payload["payload"]

    def latest_path(self, kind: ArtifactKind, suffix: str = ".json") -> Path | None:
        files = sorted(self._kind_dir(kind).glob(f"*{suffix}"))
        if not files:
            return None
        return files[-1]

    @staticmethod
    def _timestamp() -> str:
        return datetime.utcnow().strftime("%Y%m%d%H%M%S")

