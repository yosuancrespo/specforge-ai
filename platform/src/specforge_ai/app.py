from __future__ import annotations

from pathlib import Path

from .config import settings
from .models import ArtifactKind
from .orchestrator import SpecForgeOrchestrator

try:
    from fastapi import FastAPI, HTTPException
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("FastAPI is required to run the SpecForge API") from exc


app = FastAPI(title="SpecForge AI", version="0.1.0")
orchestrator = SpecForgeOrchestrator(settings)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "specforge-ai"}


@app.post("/ingest")
def ingest(path: str | None = None) -> dict:
    return orchestrator.ingest(Path(path)) if path else orchestrator.ingest()


@app.post("/plan")
def plan() -> dict:
    return orchestrator.plan()


@app.post("/generate")
def generate() -> dict:
    return orchestrator.generate()


@app.post("/run")
def run() -> dict:
    return orchestrator.run()


@app.post("/evaluate")
def evaluate() -> dict:
    return orchestrator.evaluate()


@app.post("/report")
def report() -> dict:
    return orchestrator.report()


@app.get("/artifacts/{kind}")
def latest_artifact(kind: str) -> dict:
    try:
        artifact_kind = ArtifactKind(kind)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown artifact kind: {kind}") from exc

    payload = orchestrator.store.latest_payload(artifact_kind)
    if payload is None:
        raise HTTPException(status_code=404, detail=f"No artifact found for {kind}")
    return payload

