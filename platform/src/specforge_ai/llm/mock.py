from __future__ import annotations

from .base import PromptRequest, PromptResponse


class MockLLMProvider:
    def generate(self, request: PromptRequest) -> PromptResponse:
        context_preview = " | ".join(item.strip().replace("\n", " ")[:120] for item in request.context[:3])
        if request.name == "quality-plan":
            text = (
                "SpecForge AI mock planner summary:\n"
                "- Focus validation on order amount, item cardinality, discount handling, and lifecycle transitions.\n"
                "- Prioritize contract drift between Markdown requirements and OpenAPI behavior.\n"
                f"- Grounding preview: {context_preview}"
            )
        elif request.name == "test-generation":
            text = (
                "Generated tests should cover positive amount validation, summary correctness, "
                "discount boundaries, and state transition controls."
            )
        elif request.name == "release-report":
            text = (
                "Release status is constrained by seeded defects and evaluation thresholds. "
                "The platform recommends a guarded release until core validation mismatches are fixed."
            )
        else:
            text = f"Mock response for {request.name}: {context_preview}"
        return PromptResponse(text=text, metadata={"provider": "mock"})

