# Order Orchestration Product Specification

## Overview

The demo product is a lightweight order orchestration service for digital purchases. It exists to demonstrate AI-augmented quality workflows against a small but realistic system with contract drift and validation defects.

## Business rules

1. An order must contain at least one line item.
2. `amount` must be strictly greater than zero.
3. `discount` cannot exceed `amount`.
4. The order summary must compute `final_total = amount - discount`.
5. Orders start in `draft`, may move to `confirmed`, and can then move to `fulfilled` or `cancelled`.
6. Status transitions must be validated server-side.
7. API responses must return deterministic JSON payloads for reporting workflows.

## Quality risks

- Validation drift between spec and implementation
- Summary calculation regressions after discount changes
- Missing status transition guardrails
- Weak contract enforcement in downstream consumers

## AI-assisted QA goals

- Extract requirements from this document and cross-check them against the OpenAPI contract
- Generate contract and negative tests from the business rules
- Detect seeded mismatches through grounded evidence
- Produce a release-readiness report with actionable findings

