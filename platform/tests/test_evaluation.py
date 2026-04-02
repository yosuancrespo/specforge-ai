from specforge_ai.evaluation import LocalEvalRunner


def test_eval_runner_marks_seeded_findings_as_useful() -> None:
    runner = LocalEvalRunner()
    summary = runner.evaluate(
        quality_plan={"requirements": [{"id": "REQ-1"}, {"id": "REQ-2"}]},
        generated_tests={"test_cases": [{"id": "TC-1"}, {"id": "TC-2"}]},
        run_result={
            "adapter_runs": [
                {"findings": [{"id": "F-1"}]},
                {"findings": [{"id": "F-2"}]},
            ]
        },
    )

    assert summary.score >= 0.75
    assert summary.metrics[1].passed is True

