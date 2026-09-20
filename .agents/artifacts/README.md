# Global Artifact Repository & Handoff Bus (Phase 7)

In accordance with **Phase 7 (Establish Artifact-Based Communication)** of the Academic Suite Architecture:
Agents communicate primarily through structured, machine-verifiable physical artifacts on disk rather than through large conversational dumps.

## Directory Layout
- `project/`: Master project specifications (`project.json`, `requirements.json`, `decisions.json`).
- `analysis/`: Analytical checkpoint artifacts (`data_quality.json`, `descriptive.json`, `reliability.json`, `regression.json`, `sem.json`).
- `validation/`: Independent gatekeeper scorecards (`data_validation.json`, `statistical_validation.json`, `writing_validation.json`).
- `reports/`: Assembled deliverables (`Chapter_4_Results.docx`, `Chapter_4_Results.md`, `Defense_Presentation.pptx`, `presentation.html`).

## Handoff Contract
1. Every stage produces a synchronized triad or structured JSON checkpoint.
2. Producer agents write to `artifacts/` or study-specific `academic-state/`.
3. Consumer and validator agents read physical files from disk and verify schema compliance.
