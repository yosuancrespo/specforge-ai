from __future__ import annotations

import os

from .base import PromptRequest, PromptResponse

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None


class AnthropicLLMProvider:
    def __init__(self, api_key: str | None = None, model: str = "claude-3-7-sonnet-latest") -> None:
        self.api_key = api_key or os.getenv("SPECFORGE_ANTHROPIC_API_KEY", "")
        self.model = model

    def generate(self, request: PromptRequest) -> PromptResponse:
        if httpx is None:
            raise RuntimeError("httpx is required for AnthropicLLMProvider")
        if not self.api_key:
            raise RuntimeError("SPECFORGE_ANTHROPIC_API_KEY is not configured")

        payload = {
            "model": self.model,
            "max_tokens": 900,
            "system": "You are a grounded quality engineering assistant. Do not reveal hidden chain-of-thought.",
            "messages": [
                {
                    "role": "user",
                    "content": f"{request.instruction}\n\nGrounding:\n" + "\n\n".join(request.context),
                }
            ],
        }
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        text = ""
        for item in data.get("content", []):
            if item.get("type") == "text":
                text += item.get("text", "")
        return PromptResponse(text=text.strip(), metadata={"provider": "anthropic", "model": self.model})

