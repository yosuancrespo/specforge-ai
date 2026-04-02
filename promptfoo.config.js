module.exports = {
  description: "SpecForge AI eval suite",
  prompts: [
    "file://evals/prompts/requirements-extraction.txt",
    "file://evals/prompts/test-generation.txt",
    "file://evals/prompts/defect-triage.txt"
  ],
  providers: [
    {
      id: "file://evals/providers/mock-provider.js",
      label: "specforge-mock"
    }
  ],
  tests: "file://evals/datasets/promptfoo-tests.yaml",
  defaultTest: {
    options: {
      rubricPrompt: "file://evals/rubrics/default-rubric.txt"
    }
  }
};

