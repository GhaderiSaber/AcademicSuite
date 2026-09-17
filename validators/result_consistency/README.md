# Result Consistency Validator

Verifies cross-artifact alignment across the Triad Artifact Invariant:
- Extracts exact test statistics (*t, F, p, \beta, d*) from `.json`.
- Confirms that every statistical number reported in `.md` and `.docx` matches `.json` to the exact decimal digit.
- Ensures sample size $N$ is identical across all representations.

## Verdicts
- `PASS`: 100% numerical match between JSON parameters, Markdown tables, and Word narrative.
- `FAIL`: Any discrepancy between JSON calculation and textual reporting.
