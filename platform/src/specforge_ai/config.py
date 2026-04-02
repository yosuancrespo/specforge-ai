from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _resolve_path(value: str | None, base: Path) -> Path:
    if not value:
        return base
    path = Path(value)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _discover_repo_root() -> Path:
    override = os.getenv("SPECFORGE_REPO_ROOT")
    if override:
        return Path(override).resolve()

    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / "platform").exists() and (candidate / "demo").exists():
            return candidate
    return current.parents[3]


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    artifacts_dir: Path
    dataset_dir: Path
    prompts_dir: Path
    reports_dir: Path
    database_url: str
    vector_store: str
    embedding_provider: str
    llm_provider: str
    demo_api_base_url: str
    openapi_contract_path: Path
    solidity_artifact_dir: Path
    n8n_webhook_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        repo_root = _discover_repo_root()
        return cls(
            repo_root=repo_root,
            artifacts_dir=_resolve_path(
                os.getenv("SPECFORGE_ARTIFACTS_DIR", "artifacts/runs"),
                repo_root,
            ),
            dataset_dir=_resolve_path(
                os.getenv("SPECFORGE_DATASET_DIR", "evals/datasets"),
                repo_root,
            ),
            prompts_dir=_resolve_path(
                os.getenv("SPECFORGE_PROMPTS_DIR", "evals/prompts"),
                repo_root,
            ),
            reports_dir=_resolve_path(
                os.getenv("SPECFORGE_REPORTS_DIR", "artifacts/runs/reports"),
                repo_root,
            ),
            database_url=os.getenv(
                "SPECFORGE_DATABASE_URL",
                "postgresql+psycopg://specforge:specforge@postgres:5432/specforge",
            ),
            vector_store=os.getenv("SPECFORGE_VECTOR_STORE", "pgvector"),
            embedding_provider=os.getenv("SPECFORGE_EMBEDDING_PROVIDER", "mock"),
            llm_provider=os.getenv("SPECFORGE_LLM_PROVIDER", "mock"),
            demo_api_base_url=os.getenv("SPECFORGE_DEMO_API_BASE_URL", "http://localhost:8080"),
            openapi_contract_path=_resolve_path(
                os.getenv("SPECFORGE_GO_CONTRACT_PATH", "demo/specs/openapi.yaml"),
                repo_root,
            ),
            solidity_artifact_dir=_resolve_path(
                os.getenv("SPECFORGE_SOLIDITY_ARTIFACT_DIR", "demo/contracts/out"),
                repo_root,
            ),
            n8n_webhook_url=os.getenv(
                "SPECFORGE_N8N_WEBHOOK_URL",
                "http://localhost:5678/webhook/specforge-alert",
            ),
        )


settings = Settings.from_env()