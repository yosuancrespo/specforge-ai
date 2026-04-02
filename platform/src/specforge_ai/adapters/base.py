from __future__ import annotations

from typing import Protocol

from ..models import AdapterRun, TestCase


class TestAdapter(Protocol):
    name: str

    def execute(self, cases: list[TestCase]) -> AdapterRun:
        ...

