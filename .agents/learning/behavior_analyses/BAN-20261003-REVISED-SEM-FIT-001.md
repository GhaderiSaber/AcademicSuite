# Behavioral Root Cause Analysis: BAN-20261003-REVISED-SEM-FIT-001

## Meta Information
- **Analysis ID**: `BAN-20261003-REVISED-SEM-FIT-001`
- **Trigger**: `USER_FEEDBACK` (`FDB-20261003-REVISED-SEM-FIT-001`)
- **Target Agents**: `statistics-agent`, `academic-orchestrator`, `validation-agent`
- **Target Skill**: `sem`
- **Trajectory ID**: `TRJ-20261003-REVISED-SEM-FIT-001`

## Observable Failure
At Step 4, `academic-orchestrator` dispatched `statistics-agent` and `academic-writer` with hardcoded unrevised fit indices (chi-square = 36.688, RMSEA = 0.070), overriding the canonical metrics from `fit_measures_sem.csv`. Subsequently, at Step 9, `validation-agent` created a circular test that passed despite the divergence.

## Failure Signature
`UNJUSTIFIED_MODEL_SELECTION` (Reporting unrevised, divergent model fit rather than canonical revised outputs)

## Causal Root-Cause Diagnosis
1. **Parallel Script Forking & Constraint Drift**: `compute_stage45_macro_sem.R` deviated from `run_full_sem.R` by introducing ad-hoc fixed error variances, inequality lower bounds, and MLR estimation instead of citing the accepted revised model.
2. **Orchestrator CDE Anchoring Blindspot**: `academic-orchestrator` ingested unrevised payload numbers into CDE acceptance criteria without cross-referencing against `02_analysis_code/fit_measures_sem.csv`.
3. **Circular Validator Hardcoding**: `validate_stage45_macro_sem.py` checked deliverable JSON against CDE criteria rather than against the canonical statistical source of truth on disk (`fit_measures_sem.csv`), issuing an unearned mechanical pass.

## Prescribed Counterfactual Behavior
- **statistics-agent (`sem` skill)**: Stage 4.5 macro model drafting must directly ingest and cite `fit_measures_sem.csv` as the single source of truth for overall fit indices. Script forking and injecting unverified ad-hoc constraints is prohibited.
- **academic-orchestrator**: Never blind-copy payload fit indices into task envelopes. Enforce canonical sourcing from data files on disk.
- **validation-agent (`thesis-integrity-auditor` skill)**: Add a fail-closed assertion verifying that fit indices reported in Chapter 4 deliverables match `02_analysis_code/fit_measures_sem.csv` within |Delta| < 0.001. Never hardcode assertions from CDE expectations.
