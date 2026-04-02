from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters.go_api import GoAPITestAdapter
from .adapters.solidity import SolidityTestAdapter
from .config import Settings
from .evaluation import LocalEvalRunner
from .llm.anthropic import AnthropicLLMProvider
from .llm.base import PromptRequest
from .llm.mock import MockLLMProvider
from .models import ArtifactKind, DocumentChunk, Requirement, RiskItem, TestCase, jsonable
from .parsers import chunk_document, discover_documents, parse_document
from .reporting import build_release_report, render_markdown
from .retrieval import InMemoryVectorStore, PgVectorStore, Retriever
from .store import ArtifactStore


class SpecForgeOrchestrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.retriever = Retriever(self._make_vector_store())
        self.store = ArtifactStore(settings.artifacts_dir)
        self.provider = (
            AnthropicLLMProvider()
            if settings.llm_provider == "anthropic"
            else MockLLMProvider()
        )
        self.eval_runner = LocalEvalRunner()
        self.go_adapter = GoAPITestAdapter(settings.demo_api_base_url)
        self.solidity_adapter = SolidityTestAdapter(settings.repo_root / "demo" / "contracts")

    def ingest(self, root: Path | None = None) -> dict[str, Any]:
        if root is None:
            roots = [
                self.settings.repo_root / "demo" / "specs",
                self.settings.repo_root / "demo" / "contracts" / "src",
            ]
            paths = [path for base in roots for path in discover_documents(base)]
        else:
            roots = [root]
            paths = discover_documents(root)

        docs = [parse_document(path) for path in paths]
        chunks = [chunk for doc in docs for chunk in chunk_document(doc)]
        self.retriever = Retriever(self._make_vector_store())
        self.retriever.index(chunks)
        payload = {
            "source_roots": [str(item) for item in roots],
            "documents": jsonable(docs),
            "chunks": jsonable(chunks),
            "document_count": len(docs),
            "chunk_count": len(chunks),
        }
        self.store.write_json(ArtifactKind.SOURCE_BUNDLE, "ingest", payload)
        return payload

    def plan(self) -> dict[str, Any]:
        sources = self.store.latest_payload(ArtifactKind.SOURCE_BUNDLE) or self.ingest()
        self._reindex_sources(sources)
        documents = sources["documents"]
        requirements = self._extract_requirements(documents)
        risks = self._extract_risks(requirements)
        retrieved = [
            {"content": item.chunk.content, "score": item.score}
            for item in self.retriever.query("order validation discount lifecycle summary event release", top_k=7)
        ]
        provider_summary = self.provider.generate(
            PromptRequest(
                name="quality-plan",
                instruction=(
                    "Produce a concise quality strategy summary grounded in the provided specifications."
                ),
                context=[item["content"] for item in retrieved],
            )
        )
        payload = {
            "requirements": jsonable(requirements),
            "risks": jsonable(risks),
            "retrieved_context": retrieved,
            "provider_summary": provider_summary.text,
        }
        self.store.write_json(ArtifactKind.QUALITY_PLAN, "quality-plan", payload)
        return payload

    def generate(self) -> dict[str, Any]:
        quality_plan = self.store.latest_payload(ArtifactKind.QUALITY_PLAN) or self.plan()
        test_cases = self._build_test_cases(quality_plan["requirements"])
        provider_summary = self.provider.generate(
            PromptRequest(
                name="test-generation",
                instruction="Summarize the intent of the generated tests.",
                context=[case["objective"] for case in test_cases],
            )
        )
        payload = {
            "test_cases": test_cases,
            "provider_summary": provider_summary.text,
        }
        self.store.write_json(ArtifactKind.GENERATED_TESTS, "generated-tests", payload)
        return payload

    def run(self) -> dict[str, Any]:
        generated_tests = self.store.latest_payload(ArtifactKind.GENERATED_TESTS) or self.generate()
        grouped = self._group_by_adapter(generated_tests["test_cases"])
        go_run = self.go_adapter.execute(grouped.get("go-api", []))
        solidity_run = self.solidity_adapter.execute(grouped.get("solidity", []))

        payload = {
            "run_id": "specforge-local-run",
            "adapter_runs": jsonable([go_run, solidity_run]),
            "generated_case_count": len(generated_tests["test_cases"]),
        }
        self.store.write_json(ArtifactKind.RUN_RESULT, "run-result", payload)
        self.store.write_text(ArtifactKind.RUN_RESULT, "run-result", _junit_xml(payload), suffix=".xml")
        return payload

    def evaluate(self) -> dict[str, Any]:
        quality_plan = self.store.latest_payload(ArtifactKind.QUALITY_PLAN) or self.plan()
        generated_tests = self.store.latest_payload(ArtifactKind.GENERATED_TESTS) or self.generate()
        run_result = self.store.latest_payload(ArtifactKind.RUN_RESULT) or self.run()

        summary = self.eval_runner.evaluate(quality_plan, generated_tests, run_result)
        payload = jsonable(summary)
        self.store.write_json(ArtifactKind.EVAL_RESULT, "eval-result", payload)
        return payload

    def report(self) -> dict[str, Any]:
        quality_plan = self.store.latest_payload(ArtifactKind.QUALITY_PLAN) or self.plan()
        generated_tests = self.store.latest_payload(ArtifactKind.GENERATED_TESTS) or self.generate()
        run_result = self.store.latest_payload(ArtifactKind.RUN_RESULT) or self.run()
        evaluation = self.store.latest_payload(ArtifactKind.EVAL_RESULT) or self.evaluate()
        provider_summary = self.provider.generate(
            PromptRequest(
                name="release-report",
                instruction="Summarize release readiness without revealing hidden chain-of-thought.",
                context=[
                    quality_plan.get("provider_summary", ""),
                    generated_tests.get("provider_summary", ""),
                    f"Findings: {sum(len(run['findings']) for run in run_result['adapter_runs'])}",
                    f"Eval score: {evaluation.get('score', 0.0)}",
                ],
            )
        )
        report = build_release_report(
            run_id=run_result["run_id"],
            quality_plan=quality_plan,
            generated_tests=generated_tests,
            run_result=run_result,
            evaluation=evaluation,
            summary_text=provider_summary.text,
        )
        markdown = render_markdown(report)
        payload = jsonable(report)
        self.store.write_json(ArtifactKind.RELEASE_REPORT, "release-report", payload)
        self.store.write_text(ArtifactKind.RELEASE_REPORT, "release-report", markdown)
        return payload

    def _make_vector_store(self):
        if self.settings.vector_store == "pgvector":
            return PgVectorStore(self.settings.database_url)
        return InMemoryVectorStore()

    def _reindex_sources(self, sources: dict[str, Any]) -> None:
        self.retriever = Retriever(self._make_vector_store())
        chunks = [DocumentChunk(**item) for item in sources.get("chunks", [])]
        self.retriever.index(chunks)

    @staticmethod
    def _extract_requirements(documents: list[dict[str, Any]]) -> list[Requirement]:
        product_source = _find_source(documents, "product-spec.md")
        feature_source = _find_source(documents, "checkout.feature")
        contract_source = _find_source(documents, "openapi.yaml")
        solidity_source = _find_source(documents, "OrderEscrow.sol")

        requirements = [
            Requirement(
                id="REQ-001",
                statement="The platform must reject order creation requests with a non-positive amount.",
                source_ids=[product_source],
            ),
            Requirement(
                id="REQ-002",
                statement="The platform must require at least one order item before an order can be created.",
                source_ids=[feature_source],
            ),
            Requirement(
                id="REQ-003",
                statement="The order summary must accurately reflect discounts and the final payable amount.",
                source_ids=[contract_source],
            ),
            Requirement(
                id="REQ-004",
                statement="Lifecycle transitions must remain aligned with documented status rules.",
                source_ids=[product_source, contract_source],
            ),
        ]
        if solidity_source:
            requirements.append(
                Requirement(
                    id="REQ-005",
                    statement="Contract release and delivery transitions must emit auditable events.",
                    source_ids=[solidity_source],
                    priority="medium",
                )
            )
        return requirements

    @staticmethod
    def _extract_risks(requirements: list[Requirement]) -> list[RiskItem]:
        requirement_ids = {item.id for item in requirements}
        risks = [
            RiskItem(
                id="RISK-001",
                title="Validation drift",
                rationale="Weak request validation can bypass business rules.",
                related_requirements=["REQ-001", "REQ-002"],
                severity="high",
            ),
            RiskItem(
                id="RISK-002",
                title="Summary correctness",
                rationale="Incorrect totals can erode trust and create billing issues.",
                related_requirements=["REQ-003"],
                severity="high",
            ),
            RiskItem(
                id="RISK-003",
                title="State transition drift",
                rationale="Workflow states can become more permissive than intended.",
                related_requirements=["REQ-004"],
                severity="medium",
            ),
        ]
        if "REQ-005" in requirement_ids:
            risks.append(
                RiskItem(
                    id="RISK-004",
                    title="Contract event coverage",
                    rationale="Escrow actions should remain auditable through event assertions.",
                    related_requirements=["REQ-005"],
                    severity="medium",
                )
            )
        return risks

    @staticmethod
    def _build_test_cases(requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        catalog = [
            TestCase(
                id="TC-API-001",
                title="Reject zero-value order",
                adapter="go-api",
                objective="Validate that the API rejects a non-positive amount.",
                steps=[
                    "Create an order payload with amount set to 0.",
                    "Submit the payload to POST /orders.",
                ],
                assertions=[
                    "The API should return a 400-class validation error.",
                    "The response should explain that amount must be positive.",
                ],
                source_ids=["REQ-001"],
                tags=["contract", "negative", "seeded-defect"],
            ),
            TestCase(
                id="TC-API-002",
                title="Reject empty item collection",
                adapter="go-api",
                objective="Validate that an order requires at least one item.",
                steps=[
                    "Create an order payload with an empty items list.",
                    "Submit the payload to POST /orders.",
                ],
                assertions=["The API should reject the request with a validation error."],
                source_ids=["REQ-002"],
                tags=["contract", "negative"],
            ),
            TestCase(
                id="TC-API-003",
                title="Verify summary total accuracy",
                adapter="go-api",
                objective="Ensure discounted totals match the documented contract.",
                steps=[
                    "Create a discounted order fixture.",
                    "Request the summary projection for the order.",
                ],
                assertions=["The final total should equal amount minus discount."],
                source_ids=["REQ-003"],
                tags=["calculation", "summary"],
            ),
        ]

        requirement_ids = {item["id"] for item in requirements}
        if "REQ-005" in requirement_ids:
            catalog.extend(
                [
                    TestCase(
                        id="TC-SOL-001",
                        title="Verify delivery transition guardrails",
                        adapter="solidity",
                        objective="Ensure delivery state transitions remain consistent with the bounded contract flow.",
                        steps=[
                            "Deploy the escrow contract.",
                            "Attempt a delivery transition from an unauthorized role.",
                        ],
                        assertions=["The transition should revert or fail the role check."],
                        source_ids=["REQ-004", "REQ-005"],
                        tags=["solidity", "state-machine"],
                    ),
                    TestCase(
                        id="TC-SOL-002",
                        title="Emit event on funds release",
                        adapter="solidity",
                        objective="Verify that the contract emits an auditable event when funds are released.",
                        steps=["Call the release pathway with the happy-path preconditions satisfied."],
                        assertions=["The ReleaseApproved event should be emitted exactly once."],
                        source_ids=["REQ-005"],
                        tags=["solidity", "events"],
                    ),
                ]
            )
        return jsonable(catalog)

    @staticmethod
    def _group_by_adapter(test_cases: list[dict[str, Any]]) -> dict[str, list[TestCase]]:
        grouped: dict[str, list[TestCase]] = {}
        for item in test_cases:
            grouped.setdefault(item["adapter"], []).append(TestCase(**item))
        return grouped


def _find_source(documents: list[dict[str, Any]], filename: str) -> str:
    for document in documents:
        if Path(document["path"]).name == filename:
            return document["path"]
    return filename


def _junit_xml(run_result: dict[str, Any]) -> str:
    total = len(run_result.get("adapter_runs", []))
    failures = sum(1 for run in run_result.get("adapter_runs", []) if run.get("status") != "passed")
    testcase_entries = []
    for run in run_result.get("adapter_runs", []):
        finding_text = " | ".join(finding["title"] for finding in run.get("findings", []))
        if run.get("status") == "passed":
            testcase_entries.append(
                f'<testcase classname="specforge.{run["adapter"]}" name="{run["adapter"]}" />'
            )
        else:
            testcase_entries.append(
                (
                    f'<testcase classname="specforge.{run["adapter"]}" name="{run["adapter"]}">'
                    f'<failure message="{finding_text or "adapter failed"}" />'
                    f"</testcase>"
                )
            )
    return (
        f'<testsuite name="specforge" tests="{total}" failures="{failures}">'
        + "".join(testcase_entries)
        + "</testsuite>"
    )

