---
name: chapter4
description: >-
  End-to-end orchestration for statistical findings, parametric assumption verification, MSAI auditing, APA 7 formatting, and Chapter 4 dissertation drafting.
---

# Chapter 4 End-to-End Orchestration Workflow (فصل چهارم: یافته‌های پژوهش)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for executing, auditing, drafting, and verifying **Chapter 4: Statistical Findings** for graduate dissertations and master's theses in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                     Raw Dataset (.xlsx / .sav / .csv)
                     Research Hypotheses & Variables
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE 4.0: CURATION     │
                         │ Data Curator (MCAR / Out) │
                         │(00_data_curation_report)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.1: DEMOGRAPHICS  │
                         │ Frequency & Profile Table │
                         │   (01_demographics.docx)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.2: DESCRIPTIVES  │
                         │ Psychometrics, Alpha/Omega│
                         │(02_descriptives_reliab)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE 4.3: ASSUMPTIONS  │
                         │ Normality, Levene, VIF    │
                         │ (03_assumptions.docx)     │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.4: CORRELATIONS  │
                         │ Bivariate Matrix & Discrim│
                         │ (04_correlations.docx)    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.5: MACRO MODEL   │
                         │ SEM 11 Fit Indices/Primary│
                         │   (05_macro_model.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 4.6.1: HYPOTHESIS 1 │
                         │ Dedicated 3-Table Testing │
                         │  (06_hypothesis_1.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 4.6.k: HYPOTHESIS k │
                         │ Dedicated Testing (k = 2+)│
                         │  (XX_hypothesis_k.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 4.7: MEDIATION PATHS│
                         │ Bootstrap 5,000 / 95% BCa │
                         │   (XX_mediation_1.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.8: CH 4 SUMMARY  │
                         │ Master Decision Matrix    │
                         │  (XX_chapter_summary.docx)│
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │  STAGE 4.9: STATISTICAL QC│                 │   STAGE 4.10: RESULTS QC  │
  │     Statistical Auditor   │                 │       Results Auditor     │
  │ (MSAI Multi-Signal Audit) │                 │  (APA 7 & Leading Zero)   │
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.11: CH ASSEMBLY  │
                         │ OpenXML Section Assembly  │
                         │  (Chapter_4_Results.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 4.12: FINAL JUDGE  │
                         │ Viva Voce Defense Sim     │
                         │(XX_defense_brief.docx)    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                               FINAL DELIVERABLE
```

---

## Prerequisites & Required Inputs

- **Dataset**: Physical dataset file (`.sav`, `.xlsx`, `.csv`).
- **Research Specification**:
  - Research Topic & Title.
  - Formal Hypotheses or Research Questions.
  - Identified Variables (Independent, Dependent, Covariates, Mediators/Moderators).
  - Measurement Instruments (Questionnaire names, item counts, subscales).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests dataset path and research specification.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve the top 3 historical precedents sharing similar research designs and variables.
  - Initializes the project record in `.agents/memory/decision_journal_engine.py` with status `PENDING_EXECUTION`.
- **Output**: Project brief containing precedent adaptation notes.

### Step 2: Methodology Expert Subagent (Design & Validity Controls)
- **Agent**: `methodology-expert`
- **Action**:
  - Formulates the exact design classification (e.g., Quasi-Experimental Pre-Post with Control, Mixed Split-Plot, or Structural Equation Model).
  - Formulates statistical power verification via G*Power formula ($1-\beta \ge .80$).
  - Specifies baseline covariate justification to guard against regression to the mean.
- **Output**: `methodology_spec.json`.

### Step 3: Statistical Expert Subagent (Inferential Analysis Plan)
- **Agent**: `statistical-expert`
- **Action**:
  - Establishes the 10-step parametric decision sequence:
    1. Univariate normality protocol (Shapiro-Wilk + Skewness/Kurtosis $[-0.85, +0.85]$).
    2. Homogeneity of variance (Levene's test $p > .05$).
    3. Regression slope homogeneity ($Group \times Covariate$ $p > .05$).
    4. Sphericity in Repeated Measures (Mauchly's $W$, Greenhouse-Geisser adjustment).
    5. Multicollinearity (VIF $< 5.0$, Tolerance $> .20$).
  - Prepares the hypothesis test mapping:
    - Primary hypothesis $\rightarrow$ One-Way ANCOVA (or PROCESS / Split-Plot).
    - Explicitly rejects deprecated methods (Gain-Score t-test, Baron & Kenny, Median Splits).
- **Output**: `statistical_plan.json`.

### Step 4: Deterministic Code Execution (Python Terminal Runner)
- **Agent**: Execution Layer (`run_command` in terminal)
- **Action**:
  - **Zero LLM calculation**: Runs the bundled scripts in `.agents/skills/statistical-data-analyst/scripts/` on the physical dataset.
  - Ingests dataset, calculates descriptive indices (*M, SD, Min, Max*), checks all assumptions, executes inferential hypothesis tests, and outputs exact values.
- **Output**: `stats_results.json` and raw SPSS/Excel summary tables.

### Step 5: Statistical QC Subagent (Adversarial Quality Audit)
- **Agent**: `statistical-auditor`
- **Action**:
  - Ingests `stats_results.json`.
  - Runs Multi-Signal Anomaly Index (MSAI) evaluating:
    - Effect size plausibility ($\eta_p^2, d$).
    - Variance deflation check ($SD < 0.10 \times Range$).
    - Degrees of freedom concordance ($df_{error} = N - k - 1$).
    - Slope interaction significance.
  - Emits an anomaly verdict: `AUDIT_PASSED` or `FLAG_FOR_REVIEW` with viva voce defense guidance.
- **Output**: `statistical_audit_report.json`.

### Step 6: Results QC Subagent (APA 7 Typography & OMML Audit)
- **Agent**: `results-auditor`
- **Action**:
  - Ingests raw data tables and test statistics.
  - Enforces APA 7th Edition rules:
    - Zero leading zeros on bounded values in English ($p = .023$, $\eta_p^2 = .18$); in Persian reports, strictly preserve leading zero (`۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`) with standard dot ('.') format and zero slashes.
    - Never reporting $p = .000$ (replaces with $p < .001$ in English, or $p < ۰.۰۰۱$ / $۰.۰۰۱ > p$ in Persian).
    - Exactly 3 horizontal borders with zero vertical borders.
    - Verification of native Word OMML math equations (`<m:oMath>`) preservation.
- **Output**: `results_qc_checklist.json`.

### Micro-Stage Execution Sequence & Triad Artifact Invariant (Directive 3 & 11)

To prevent shortcutting, Chapter 4 drafting is strictly partitioned into independent micro-stages. Monolithic execution is prohibited. **Triad Artifact Invariant**: Every stage generates `.docx` (APA 7 OpenXML), `.md` (Markdown narrative & tables), and `.json` (structured data/audit).

#### Stage 4.0: Data Curation & Preprocessing
- **Agent**: `data-curator`
- **Output**: `00_data_curation_report.json`, `00_data_curation_report.md` + `data_cleaned.xlsx` (Little's MCAR test, unengaged response filtering, Mahalanobis $D^2$).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.1: Demographic Profiling & Participant Attributes
- **Agent**: `academic-writer`
- **Output**: `01_demographics.docx`, `01_demographics.md`, `01_demographics.json` (Frequency tables, percentages, APA 7 demographic narrative).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.2: Psychometrics & Scale Reliability
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `02_descriptives_and_reliability.docx`, `02_descriptives_and_reliability.md`, `02_descriptives_and_reliability.json` (Construct, subscale, $N, M, SD$, Skewness, Kurtosis, Cronbach's $\alpha$, McDonald's $\omega$).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.3: Parametric Assumptions Suite
- **Agent**: `statistical-expert`
- **Output**: `03_parametric_assumptions.docx`, `03_parametric_assumptions.md`, `03_parametric_assumptions.json` (Shapiro-Wilk, Levene's test, regression slope homogeneity, collinearity VIF/Tolerance, linearity).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.4: Bivariate Correlation Matrix Analysis
- **Agent**: `academic-writer`
- **Output**: `04_bivariate_correlations.docx`, `04_bivariate_correlations.md`, `04_bivariate_correlations.json` (Subscale correlation matrix, discriminant validity evaluation, multi-paragraph scholarly narrative directly above the table).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.5: Macro SEM Model Fit / Primary Omnibus Model
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `05_macro_model.docx`, `05_macro_model.md`, `05_macro_model.json` (11 Goodness-of-Fit indices table vs Hu/Bentler criteria + 300-DPI Structural Path Diagram).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.6.1: Hypothesis 1 Testing & Dissection (One-Hypothesis-One-Stage Invariant)
- **Agent**: `academic-writer`
- **Output**: `06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json` (3-table standard: correlation, ANOVA summary, regression coefficients + deep narrative dissection).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.6.k: Hypothesis k Testing & Dissection (Dedicated Independent Stages)
- **Agent**: `academic-writer`
- **Output**: `XX_hypothesis_k.docx`, `XX_hypothesis_k.md`, `XX_hypothesis_k.json` (Each subsequent hypothesis is analyzed and drafted in its own dedicated stage).
- **Stage-Gate**: Emit Completion Report and await user confirmation after each hypothesis.

#### Stage 4.7.1 to 4.7.k: Indirect Mediation Paths (Bootstrap 5,000)
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `XX_mediation_k.docx`, `XX_mediation_k.md`, `XX_mediation_k.json` (Indirect effects, 5,000 resamples, 95% BCa CI).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.8: Master Decision Matrix & Chapter 4 Summary
- **Agent**: `academic-writer`
- **Output**: `XX_chapter_summary.docx`, `XX_chapter_summary.md`, `XX_chapter_summary.json` (Comprehensive 1-2 page synthesis, Master Hypotheses Decision Table, transition bridge to Chapter 5).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.9: Statistical QC (MSAI Anomaly Audit)
- **Agent**: `statistical-auditor`
- **Output**: `XX_statistical_audit_report.json`, `XX_statistical_audit_report.md` (Multi-Signal Anomaly Index audit on all numbers across sections).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.10: Results QC (APA 7 & OpenXML Typography)
- **Agent**: `results-auditor`
- **Output**: `XX_results_qc_checklist.json`, `XX_results_qc_checklist.md` (Leading zero check `۰.۰۰۱`, 3-line borders, OMML equation preservation).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.11: Chapter Assembly & Merging
- **Agent**: Execution Layer via `orchestrator_cli.py --assemble-chapter Chapter_4_Results.docx`
- **Output**: `Chapter_4_Results.docx` + `Chapter_4_Results.md` (Concatenated from verified section documents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 4.12: Final Committee Defense Simulator
- **Agent**: `final-judge`
- **Output**: `XX_defense_cross_examination_brief.docx`, `XX_defense_cross_examination_brief.md`, `defense_readiness.json` (5 examiner cross-examination questions & defense model answers).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

---

### Interactive Stage-Gate Communication Format (Directive 11)
At the completion of each micro-stage above, the agent MUST output:
```markdown
### 🏁 Stage X Completion Report: <Stage Name>
- **What Was Done**: Subagent used, deterministic scripts executed, exact numbers verified, and physical disk artifacts generated.
- **What Will Be Done Next**: Target next stage name, assigned subagent, input prerequisites, and expected deliverables.

> **Awaiting Confirmation**: Please review the above stage results. Reply to confirm or adjust, and I will proceed to **Stage X+1: `<Next Stage Name>`**.
```
The agent **MUST STOP and wait for user confirmation** before advancing. Monolithic multi-stage execution in a single turn is prohibited.

---

## Antigravity Multi-Agent Execution Architecture (Directive 12 & HYBRID_MULTI_AGENT_SPEC)

1. **Hands**: Deterministic statistical calculations run via Python CLI (`psychology_stats.py`, `generate_apa_docx.py`, `simdat_engine.py`) generating physical `stats_results.json` and APA 7 tables.
2. **Brains**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `methodology-expert`: Audits design, power, and validity.
   - `statistical-auditor`: Runs adversarial MSAI anomaly checks on `stats_results.json`.
   - `results-auditor`: Verifies APA 7 rules, leading zero compliance, and OpenXML layout.
   - `final-judge`: Simulates viva voce oral defense cross-examination.
3. **Orchestrator**: Cognitive roles and deterministic hands are orchestrated directly by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and decision journaling.
