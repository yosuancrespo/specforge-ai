from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..models import AdapterRun, Finding, TestCase


@dataclass
class SolidityTestAdapter:
    contract_root: Path
    name: str = "solidity"

    def execute(self, cases: list[TestCase]) -> AdapterRun:
        source = self.contract_root / "src" / "OrderEscrow.sol"
        findings: list[Finding] = []

        if not source.exists():
            findings.append(
                Finding(
                    id="solidity-missing-source",
                    title="Solidity source was not found",
                    severity="medium",
                    summary="The adapter could not inspect the bounded Web3 module source tree.",
                    evidence=[str(source)],
                )
            )
        else:
            content = source.read_text(encoding="utf-8")
            if "markDelivered" in content and "onlyBuyer" not in content:
                findings.append(
                    Finding(
                        id="solidity-role-guard",
                        title="Delivery transition is not explicitly role-guarded",
                        severity="medium",
                        summary=(
                            "The showcase contract exposes a transition that should be covered by Foundry tests "
                            "and explicit role assertions."
                        ),
                        evidence=[str(source)],
                    )
                )

        return AdapterRun(
            adapter=self.name,
            status="failed" if findings else "passed",
            findings=findings,
            metrics={"cases_considered": len(cases)},
        )

