# ADR-0002: Provider abstraction

## Status

Accepted

## Context

The repository should support real LLM integrations, but it should not tie the architecture, tests, and documentation to a single provider or require live network access for every local demonstration.

## Decision

Define provider interfaces for LLMs, retrieval stores, test adapters, and eval runners. Ship a mock provider as the default local mode and expose Anthropic-style configuration for real Claude integration.

## Consequences

- Local demos stay reproducible
- Real providers can be added without rewriting workflows
- Prompt and agent regressions can be evaluated with deterministic fixtures

