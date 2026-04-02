from __future__ import annotations

from pathlib import Path

import typer

from .config import settings
from .orchestrator import SpecForgeOrchestrator


app = typer.Typer(help="SpecForge AI CLI")
orchestrator = SpecForgeOrchestrator(settings)


@app.command()
def ingest(path: Path | None = typer.Argument(None, help="Path to specs, contracts, or fixtures")) -> None:
    result = orchestrator.ingest(path)
    source_label = ", ".join(result.get("source_roots", []))
    typer.echo(
        f"Ingested {result['document_count']} documents and {result['chunk_count']} chunks from {source_label}"
    )


@app.command()
def plan() -> None:
    result = orchestrator.plan()
    typer.echo(
        f"Created quality plan with {len(result['requirements'])} requirements and {len(result['risks'])} risks"
    )


@app.command()
def generate() -> None:
    result = orchestrator.generate()
    typer.echo(f"Generated {len(result['test_cases'])} test cases")


@app.command()
def run() -> None:
    result = orchestrator.run()
    failed = sum(1 for item in result["adapter_runs"] if item["status"] != "passed")
    typer.echo(
        f"Completed run {result['run_id']} with {len(result['adapter_runs'])} adapters and {failed} failures"
    )


@app.command()
def evaluate() -> None:
    result = orchestrator.evaluate()
    typer.echo(f"Evaluation score: {result['score']} ({result['recommendation']})")


@app.command()
def report() -> None:
    result = orchestrator.report()
    typer.echo(f"Release recommendation: {result['recommendation']}")


if __name__ == "__main__":  # pragma: no cover
    app()