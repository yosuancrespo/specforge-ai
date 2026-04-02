# ADR-0001: Monorepo shape

## Status

Accepted

## Context

The project needs to showcase AI engineering, QA strategy, API testing, mutation testing, and smart-contract validation in a single GitHub repository without becoming a random collection of unrelated experiments.

## Decision

Use a monorepo with:

- `platform/` for the orchestration core
- `dashboard/` for the evidence UI
- `demo/` for the sample system and contract assets
- `evals/` for prompt regression assets
- `n8n/` for automation workflows

## Consequences

- The repository tells one coherent story
- Toolchain setup is heavier than a single-language project
- CI must coordinate multiple runtimes

