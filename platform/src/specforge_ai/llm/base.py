from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class PromptRequest:
    name: str
    instruction: str
    context: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptResponse:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class LLMProvider(Protocol):
    def generate(self, request: PromptRequest) -> PromptResponse:
        ...

