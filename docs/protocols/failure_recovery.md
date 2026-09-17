# Failure Taxonomy & Incident Recovery Protocol (Phase 15)

## Purpose
Standardizes error classification and diagnostic routing when an execution failure occurs during academic analysis or document generation.

## Failure Taxonomy
Every failure must be classified into one of the canonical types:
- `DATA`: Missing values, corrupted encoding, invalid schema, or extreme outliers.
- `TOOL`: Python/R script crash, missing dependency, or non-zero exit code.
- `STATISTICAL`: Non-convergence in SEM/CFA, severe multicollinearity ($VIF > 10$), or inadmissible parameters ($Heywood$ cases).
- `METHODOLOGICAL`: Underpowered sample ($1-\beta < .80$), design-hypothesis mismatch.
- `VALIDATION`: Gatekeeper rejection by `validators/` (reporting, numerical, or data integrity failure).
- `PERMISSION`: Read/write access denial or missing file path.
- `AGENT`: Subagent timeout, contract violation, or schema non-conformity.

## Recovery Routing
Do not restart the entire task from scratch. Route to the appropriate specialist:
- `DATA` -> Route to `data-agent`.
- `TOOL` -> Inspect stderr and run diagnostics via `recovery/cli.py`.
- `STATISTICAL` -> Route to `statistics-agent` for parameter re-specification.
- `VALIDATION` -> Route back to producing agent with validator violation report.
