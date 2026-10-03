# Causal Behavior Analysis: BAN-20261003-CORRELATION-ORDER-001

## 1. Defect Identification
- **Analysis ID**: BAN-20261003-CORRELATION-ORDER-001
- **Target Agent**: `statistics-agent`, `academic-writer`, `validation-agent`
- **Target Skill**: `chapter-4-writing`
- **Observable Failure Step**: Step 4 (`compute_stage4b4_correlations.py` hardcoding) and Step 16 (Validator blindspot).
- **Failure Signature**: `VIOLATED_ASSUMPTION_IGNORED`

## 2. Root Cause Diagnosis
The structural defect originated computationally. The `statistics-agent` hardcoded the `study_vars_meta` list in `compute_stage4b4_correlations.py` such that subscales (e.g., `IUS_FA`, `IUS_RA`, `Ru_Ref`, `Ru_Bro`, `Ru_Dep`) preceded their respective composite total scores (`IUS_T`, `RRS_T`). This bottom-up sequence was uncritically propagated by `academic-writer` into the final Markdown and DOCX Table 4-14 outputs. The defect successfully bypassed `validation-agent` because `validate_stage43_correlations.py` verified binary size, caption, column counts, and sample size, but completely lacked a cross-table row sequence parity assertion against Table 4-13.

## 3. Prescribed Counterfactual Behavior
1. **Computational Ordering**: When defining variable metadata for correlation matrices, `statistics-agent` MUST structurally order multidimensional constructs such that the Total Composite Score (`کل`) strictly precedes its constituent subscales.
2. **Drafting Propagation**: `academic-writer` must maintain consistent hierarchical construct ordering across all Chapter 4 tables.
3. **Validator Hardening**: `validation-agent` MUST assert strict cross-table structural parity. The row sequence of constructs and subscales in the correlation matrix (Table 4-14) must be programmatically verified against the descriptive statistics table (Table 4-13). Fail closed if any construct places subscales before total composite scores.
