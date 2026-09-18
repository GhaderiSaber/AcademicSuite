# Methodological Deliberation & Academic Challenger Report

## Executive Summary
- **Project ID**: `study_act_burnout`
- **Design Type**: `quasi_experimental`
- **Time Structure**: `pre_post_repeated_measures`
- **Selected Candidate**: `CAND-ANCOVA-BURNOUT-01` (`ancova_analysis_of_covariance`)
- **Selection Verdict**: **CONDITIONAL**
- **Synthesis Rationale**: Deliberation evaluated 3 competing candidate analysis plans. Candidate 'CAND-ANCOVA-BURNOUT-01' (One-Way ANCOVA) was selected under CONDITIONAL status. Methodological justification: Controls for non-equivalent baseline differences in quasi-experimental designs, Reduces unexplained error variance, increasing statistical precision and power, Complies with Lords paradox recommendations for non-randomized pre-post groups. Disqualified candidates: CAND-POST-TTEST-02 (Raw Posttest Independent Samples t-test), CAND-REP-ANOVA-03 (Two-Way Mixed Repeated Measures ANOVA) due to fatal design/assumption vulnerabilities persisted into canonical pitfall registry. Synthesized conditions addressed: Verify homogeneity of regression slopes (Group × Pretest interaction p > .05)..

---

## 1. Candidate Evaluation & Challenger Invalidation Matrix

| Candidate ID | Challenger Verdict | Methodological Vulnerabilities / Conditions | Avoided Pitfalls |
| :--- | :---: | :--- | :--- |
| `CAND-ANCOVA-BURNOUT-01` | **CONDITIONAL** | **CONDITION**: Verify homogeneity of regression slopes (Group × Pretest interaction p > .05). | None |
| `CAND-POST-TTEST-02` | **REJECTED** | **FATAL**: Recurring Pitfall [PIT-1789707831-CAND-POST-ANOVA-02]: Unjustified omission of available baseline covariate.<br>**FATAL**: Unjustified omission of available baseline covariate. | `PIT-1789707831-CAND-POST-ANOVA-02` |
| `CAND-REP-ANOVA-03` | **REJECTED** | **FATAL**: Recurring Pitfall [PIT-1789707831-CAND-REP-ANOVA-03]: Unjustified omission of available baseline covariate.<br>**FATAL**: Unjustified omission of available baseline covariate. | `PIT-1789707831-CAND-REP-ANOVA-03` |

---

## 2. Canonical Pitfalls Registry Action

The Academic Challenger invalidated 2 candidate approach(es) and permanently recorded them to `state/pitfalls.jsonl`:
- **`CAND-POST-TTEST-02`** (Raw Posttest Independent Samples t-test): *Recurring Pitfall [PIT-1789707831-CAND-POST-ANOVA-02]: Unjustified omission of available baseline covariate.; Unjustified omission of available baseline covariate.*
- **`CAND-REP-ANOVA-03`** (Two-Way Mixed Repeated Measures ANOVA): *Recurring Pitfall [PIT-1789707831-CAND-REP-ANOVA-03]: Unjustified omission of available baseline covariate.; Unjustified omission of available baseline covariate.*

---

## 3. Synthesized Analysis Plan Summary
- **Primary Hypothesis**: Significant main effect indicates ACT intervention reduces nurse burnout beyond pretest differences.
- **Estimand**: Average treatment contrast on posttest burnout adjusted for baseline burnout score
- **Model Family**: `ancova_analysis_of_covariance`
- **Software Engine**: `python`
- **Assigned Subagent**: `statistics-agent`
- **Artifact Triad Path**: `06_hypothesis_1.json`

> [!NOTE]
> Complete formal specification written to `analysis_plan.json` conforming to `contracts/analysis_plan.schema.json`.