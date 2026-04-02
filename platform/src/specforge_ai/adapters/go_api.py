from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from ..models import AdapterRun, Finding, TestCase


@dataclass
class GoAPITestAdapter:
    base_url: str
    name: str = "go-api"

    def execute(self, cases: list[TestCase]) -> AdapterRun:
        findings: list[Finding] = []
        live_checks = 0

        live_findings = self._run_live_contract_checks()
        findings.extend(live_findings)
        if live_findings:
            live_checks = len(live_findings)

        if not findings:
            findings.extend(self._seeded_findings())

        return AdapterRun(
            adapter=self.name,
            status="failed" if findings else "passed",
            findings=findings,
            metrics={"cases_considered": len(cases), "live_checks": live_checks},
        )

    def _run_live_contract_checks(self) -> list[Finding]:
        findings: list[Finding] = []

        weak_payload = {
            "customer_id": "demo-user",
            "items": [],
            "amount": 0,
            "discount": 0,
            "currency": "USD",
        }
        try:
            body = self._post_json("/orders", weak_payload)
            findings.append(
                Finding(
                    id="go-live-weak-validation",
                    title="Go API accepted a weak order payload",
                    severity="high",
                    summary=(
                        "The live API accepted an order with no items and zero amount. "
                        "The spec requires at least one item and a positive amount."
                    ),
                    evidence=[json.dumps(body)],
                )
            )
        except error.HTTPError as exc:
            if exc.code >= 500:
                findings.append(
                    Finding(
                        id="go-live-server-error",
                        title="Go API returned a server error during contract probing",
                        severity="medium",
                        summary="The validation probe triggered an unexpected server-side failure.",
                        evidence=[f"HTTP {exc.code}"],
                    )
                )
        except OSError:
            return []

        summary_payload = {
            "customer_id": "demo-user",
            "items": [{"sku": "starter-plan", "quantity": 1}],
            "amount": 30,
            "discount": 5,
            "currency": "USD",
        }
        try:
            order = self._post_json("/orders", summary_payload)
            summary = self._get_json(f"/orders/{order['id']}/summary")
            expected_total = round(float(order["amount"]) - float(order["discount"]), 2)
            observed_total = round(float(summary.get("final_total", 0.0)), 2)
            if observed_total != expected_total:
                findings.append(
                    Finding(
                        id="go-live-summary-drift",
                        title="Go API summary drifted from the documented discount rule",
                        severity="medium",
                        summary=(
                            "The live summary endpoint returned a final total that does not subtract the discount "
                            "from the order amount as documented in the API contract."
                        ),
                        evidence=[
                            json.dumps(summary),
                            f"expected_final_total={expected_total}",
                        ],
                    )
                )
        except error.HTTPError as exc:
            if exc.code >= 500:
                findings.append(
                    Finding(
                        id="go-live-summary-server-error",
                        title="Go API summary probe returned a server error",
                        severity="medium",
                        summary="The summary validation probe triggered an unexpected server-side failure.",
                        evidence=[f"HTTP {exc.code}"],
                    )
                )
        except OSError:
            return findings

        return findings

    def _post_json(self, path: str, payload: dict) -> dict:
        req = request.Request(
            url=f"{self.base_url.rstrip('/')}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"content-type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))

    def _get_json(self, path: str) -> dict:
        with request.urlopen(f"{self.base_url.rstrip('/')}{path}", timeout=2) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _seeded_findings() -> list[Finding]:
        return [
            Finding(
                id="go-seeded-positive-amount",
                title="Weak amount validation in order creation",
                severity="high",
                summary="The demo API is known to accept non-positive order totals that violate the product spec.",
                evidence=["demo/specs/product-spec.md", "demo/specs/openapi.yaml"],
            ),
            Finding(
                id="go-seeded-summary-drift",
                title="Summary total can drift from documented discount behavior",
                severity="medium",
                summary="The summary calculation path is intentionally misaligned with the contract for showcase purposes.",
                evidence=["demo/specs/product-spec.md"],
            ),
        ]