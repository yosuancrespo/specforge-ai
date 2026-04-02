from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import EvalMetric


@dataclass
class EvaluationSummary:
    score: float
    metrics: list[EvalMetric]
    recommendation: str


class LocalEvalRunner:
    def evaluate(
        self,
        quality_plan: dict[str, Any],
        generated_tests: dict[str, Any],
        run_result: dict[str, Any],
    ) -> EvaluationSummary:
        metrics: list[EvalMetric] = []

        requirement_count = len(quality_plan.get("requirements", []))
        generated_count = len(generated_tests.get("test_cases", []))
        finding_count = sum(len(run.get("findings", [])) for run in run_result.get("adapter_runs", []))

        metrics.append(
            EvalMetric(
                name="requirements_coverage",
                score=round(min(generated_count / max(requirement_count, 1), 1.0), 2),
                threshold=0.8,
                passed=generated_count >= requirement_count,
                notes="Generated cases should cover the majority of extracted requirements.",
            )
        )
        metrics.append(
            EvalMetric(
                name="grounded_risk_detection",
                score=1.0 if finding_count >= 2 else 0.5,
                threshold=0.7,
                passed=finding_count >= 2,
                notes="The seeded demo should surface at least two meaningful findings.",
            )
        )
        metrics.append(
            EvalMetric(
                name="prompt_regression_readiness",
                score=0.83,
                threshold=0.75,
                passed=True,
                notes="Mock local eval mirrors the promptfoo regression suite threshold.",
            )
        )

        aggregate = round(sum(metric.score for metric in metrics) / len(metrics), 2)
        recommendation = "needs-attention" if aggregate < 0.9 or finding_count else "ready"
        return EvaluationSummary(score=aggregate, metrics=metrics, recommendation=recommendation)

