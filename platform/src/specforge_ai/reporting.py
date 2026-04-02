from __future__ import annotations

from .models import ReleaseReport


def build_release_report(
    run_id: str,
    quality_plan: dict,
    generated_tests: dict,
    run_result: dict,
    evaluation: dict,
    summary_text: str,
) -> ReleaseReport:
    findings = []
    for adapter_run in run_result.get("adapter_runs", []):
        findings.extend(adapter_run.get("findings", []))

    highlights = [
        f"Requirements extracted: {len(quality_plan.get('requirements', []))}",
        f"Test cases generated: {len(generated_tests.get('test_cases', []))}",
        f"Adapter runs executed: {len(run_result.get('adapter_runs', []))}",
        f"Evaluation score: {evaluation.get('score', 0.0)}",
    ]

    return ReleaseReport(
        run_id=run_id,
        recommendation=evaluation.get("recommendation", "needs-attention"),
        summary=summary_text,
        highlights=highlights,
        findings=findings,
        metrics=evaluation.get("metrics", []),
    )


def render_markdown(report: ReleaseReport) -> str:
    findings_markdown = "\n".join(
        f"- **{item['severity'].upper()}** {item['title']}: {item['summary']}"
        if isinstance(item, dict)
        else f"- **{item.severity.upper()}** {item.title}: {item.summary}"
        for item in report.findings
    )
    metrics_markdown = "\n".join(
        f"- {metric['name'] if isinstance(metric, dict) else metric.name}: "
        f"{metric['score'] if isinstance(metric, dict) else metric.score} "
        f"(threshold {metric['threshold'] if isinstance(metric, dict) else metric.threshold})"
        for metric in report.metrics
    )
    highlights_markdown = "\n".join(f"- {line}" for line in report.highlights)
    return f"""# Release Readiness Report

## Summary

- Run ID: `{report.run_id}`
- Recommendation: `{report.recommendation}`
- Generated at: `{report.generated_at}`

{report.summary}

## Highlights

{highlights_markdown}

## Findings

{findings_markdown or "- No findings"}

## Metrics

{metrics_markdown}
"""

