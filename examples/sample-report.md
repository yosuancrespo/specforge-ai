# Sample Release Readiness Report

## Executive summary

- Run identifier: `specforge-local-run`
- Requirements extracted: 5
- Generated test cases: 5
- Adapter runs executed: 2
- Live findings surfaced: 2
- Eval score: 0.94
- Release recommendation: `needs-attention`

## Key findings

1. The order creation endpoint accepted a payload with zero amount and no items even though the product specification requires both validations.
2. The summary endpoint returned a final total that did not subtract the discount from the order amount.

## Evidence

- Grounding source: `demo/specs/product-spec.md`
- Contract source: `demo/specs/openapi.yaml`
- Acceptance source: `demo/specs/checkout.feature`
- Execution adapter: `go-api`
- Mutation engine contribution: boundary payloads around `amount`, `items`, and `discount`

## Recommended next actions

1. Tighten validation in the Go API request handler.
2. Correct the summary calculation so discounts are subtracted rather than added.
3. Extend live probes to cover lifecycle transition drift if you want the demo to surface an additional seeded defect.