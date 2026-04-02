# End-to-End Walkthrough

## Scenario

The bundled demo product is a lightweight order orchestration service for digital purchases. Product requirements are captured in Markdown, acceptance criteria in Gherkin, and the external API in OpenAPI. The implementation intentionally drifts from the documented contract.

## Happy path

1. Ingest the demo specs and contracts.
2. Build a retrieval index from chunks and metadata.
3. Ask the planning workflow to extract requirements, risks, and likely defect hotspots.
4. Generate API and contract test cases.
5. Execute the generated checks and collect evidence.
6. Evaluate the quality of the generated artifacts.
7. Compile a release-readiness report and visualize it in the dashboard.
8. Trigger an n8n alert flow when eval or contract thresholds fail.

## Expected outcome

The happy path should not end with a clean release recommendation. In the current validated demo snapshot, the system intentionally reports a guarded outcome because the Go API contains seeded validation drift and discount-calculation drift.

A representative run shows:

- 5 extracted requirements
- 5 generated tests
- 2 live findings in the Go API
- An evaluation score around `0.94`
- A final recommendation of `needs-attention`

That result is the evidence. It demonstrates that the platform is grounded in the specs and can surface meaningful defects instead of producing an uninformative all-green report.

## Portfolio talking points

- The repository shows how modern QA can move from static test cases to grounded, agent-assisted workflows.
- The architecture keeps LLM providers abstract while still enabling real integrations like Claude.
- Evals are first-class artifacts, not a side note.
- Polyglot modules are present because they reinforce the story, not because they inflate the tech list.

## Suggested demo flow for GitHub

1. Start with the product spec and seeded defects.
2. Show the CLI commands and the generated quality plan.
3. Open the sample report and highlight grounded evidence.
4. Show the dashboard screenshots or live run.
5. Finish with the n8n workflow and CI gates.