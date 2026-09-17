# Chapter 4 End-to-End Orchestration Workflow (فصل چهارم: یافته‌های پژوهش)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for executing, auditing, drafting, and verifying **Chapter 4: Statistical Findings** for graduate dissertations and master's theses in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                     Raw Dataset (.xlsx / .sav / .csv)
                     Research Hypotheses & Variables
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STEP 1: DIGITAL SABER   │
                         │   Master Lead Assessment  │
                         │  (Precedent CBR Retrieval)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 2: METHODOLOGY EXPERT│
                         │ Design & Validity Threats │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 3: STATISTICAL EXPERT│
                         │ Inferential Analysis Plan │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 4: EXECUTION LAYER   │
                         │ Deterministic Python / CLI│
                         │   (stats_results.json)    │
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │ STEP 5: STATISTICAL QC    │                 │   STEP 6: RESULTS QC      │
  │   Statistical Auditor     │                 │     Results Auditor       │
  │ (MSAI & Assumption Check) │                 │(APA 7 & OMML Typography)  │
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 7: ACADEMIC WRITER   │
                         │5-Part Epistemic Paragraphs│
                         │  (Chapter_4_Results.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    STEP 8: FINAL JUDGE    │
                         │ Viva Voce Defense Sim     │
                         │ Approval Readiness (0-100)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 9: SABER HUMAN GATE  │
                         │ Admin Desk Sign-Off       │
                         │     (ID: 124911145)       │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                               FINAL DELIVERABLE
```

---

## Prerequisites & Required Inputs

- **Project Brief (SSOT)**: Verified `PROJECT_BRIEF.md` (Client scope, target deliverables, deadlines, and physical asset inventory).
- **Dataset**: Physical dataset file (`.sav`, `.xlsx`, `.csv`) in `01_raw_inputs/`.
- **Research Specification**:
  - Research Topic & Title.
  - Formal Hypotheses or Research Questions.
  - Identified Variables (Independent, Dependent, Covariates, Mediators/Moderators).
  - Measurement Instruments (Questionnaire names, item counts, subscales).

---

## Step-by-Step Subagent Execution Protocol

### Step 0: Project Discovery & Baseline Verification (Project Passport)
- **Agent**: `digital-saber` / `data-curator`
- **Action**:
  - Inspects `PROJECT_BRIEF.md` in the project root to anchor client requirements, target deliverables, and deadlines.
  - If missing, executes:
    `python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py --init-brief --dir "/path/to/project"`
  - Verifies that raw datasets and approved proposals are present on disk before triggering analytical pipelines.
- **Output**: Verified `PROJECT_BRIEF.md` with active gap checklist.

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

### Step 7: Academic Writer Subagent (Persian Chapter 4 Drafting — Section & Table Grounded Architecture)
- **Agent**: `academic-writer`
- **Reference**: Emulates [.agents/references/saber_chapter4_exemplars.md](file:///.agents/references/saber_chapter4_exemplars.md)
- **Action**:
  - Ingests verified Word tables, statistical results (`stats_results.json`), and generated 300-DPI plots.
  - Executes Saber's **Section-by-Section & Step-by-Step AI Drafting Protocol**:
    1. **Section Introductions (مقدمه بخش‌ها)**: Drafts contextual roadmaps for the Chapter, Demographics, Descriptives, Assumptions, and Inferential sections.
    2. **Gold Standard for Academic Table Explanations (تحلیل استاندارد عمیق و آکادمیک جداول)**: Every substantive table (descriptives, assumptions, correlation matrix, regressions, SEM fit indices, direct paths, indirect bootstrap paths, and summary matrix) MUST have an extensive, multi-paragraph scholarly narrative placed **DIRECTLY ABOVE** the table caption. Superficial, 1-2 sentence, tiny, or juvenile explanations are strictly forbidden:
       - *Bivariate Correlation Matrix*: Mandatory in-depth scholarly analysis evaluating sign, magnitude, significance, discriminant validity, and multicollinearity safeguards ($r < .85$).
       - *Context & Objective (تحلیل زمینه و متغیر)*: Grounding the statistical purpose.
       - *Key Numerical Highlights (واکاوی داده‌ها و مقادیر کلیدی)*: Dissecting exact numbers, variances, effect sizes, and bootstrap confidence intervals.
       - *Formal In-Text Reference (ارجاع رسمی به جدول)*: e.g. `(جدول ۴- X)`.
       - *Empirical Verdict (استنتاج آماری اولیه)*: Definitive empirical conclusion.
    3. **3-Table Standard for Relationship Hypotheses**: For every relationship hypothesis, presents exactly 3 distinct tables: Table 1 (Bivariate Correlation Matrix), Table 2 (Model Summary & ANOVA), and Table 3 (Regression Coefficients & Collinearity Diagnostics).
    4. **SEM Macro-to-Micro Reporting Architecture**: When testing mediation/structural paths from an overarching model:
       - *Macro-Level Section First*: Reports overall SEM results comprehensively BEFORE individual hypotheses: Table A (11 Goodness-of-Fit indices comparing baseline vs. harnessed model against Kline & Hu/Bentler criteria), Figure B (300-DPI Structural Path Diagram), Table C (Direct Structural Paths Table with $B, SE, \beta, t/z, p$), Table D (Indirect & Serial Bootstrap 5,000 Table with 95% BCa CIs).
       - *Dedicated Individual Hypothesis Subsections*: Followed by an independent subsection for each SEM-related hypothesis (e.g. Hypotheses 3 to 8) with deep empirical dissection.
    5. **Diagnostic Figures Explanations (تحلیل نمودارها)**: Interprets residual histograms, normal P-P plots, or SEM diagrams directly adjacent to each figure.
    6. **Comprehensive Whole Chapter Summary (خلاصه و جمع‌بندی جامع فصل چهارم)**: Concludes Chapter 4 with an extensive synthesis spanning **1 to 2 full pages** (strictly prohibiting short single-paragraph summaries), featuring the Master Hypotheses Decision Matrix Table (`جدول ماتریس جمع‌بندی نهایی فرضیات`) and the Conceptual Transition Bridge to Chapter 5.
  - **Strict Empirical Guardrail**: **ZERO literature comparisons (e.g. Beck, Bandura, Hayes) and ZERO psychological theoretical mechanisms in Chapter 4**. All literature discussions and theoretical interpretations are strictly deferred to **Chapter 5**.
  - Enforces Persian half-spaces (`\u200c`), standard dot notation for decimals, preserving leading zero (`۰.۰۰۱`, `۰.۰۵`), and eliminating all AI clichés.
  - Compiles publication-ready Word document with OpenXML directionality `<w:bidi w:val="1"/>`, borderless APA 7 tables, and physically embedded 300-DPI figures via `generate_apa_docx.py`.
- **Output**: `Chapter_4_Results.docx` (yielding authentic 3,500 to 12,000+ words).

### Step 8: Final Judge Subagent (Defense Viva Voce Simulator)
- **Agent**: `final-judge`
- **Action**:
  - Reviews `Chapter_4_Results.docx`.
  - Simulates external examiner cross-examination with 5 critical questions.
  - Formulates defense model answers with APA 7 literature citations.
  - Calculates Committee Defense Readiness Score ($0\text{--}100\%$).
- **Output**: `defense_cross_examination_report.docx` and JSON summary.

### Step 9: Saber Human Gate Sign-off (Rule 11)
- **Agent**: `digital-saber`
- **Action**:
  - Posts the complete project summary card to Saber's Admin Desk (`124911145`):
    - Title, Design, $N$, Hypotheses, Key Statistics.
    - Audit results and Defense Readiness score.
    - Interactive commands: `/approve_chapter4` or `/adjust_chapter4`.
  - Upon approval, deliverable is marked `RELEASED` and logged in `.agents/memory/decision_journal_engine.py`.

---

## Antigravity Multi-Agent Execution Architecture (Directive 12 & HYBRID_MULTI_AGENT_SPEC)

1. **Hands**: Deterministic statistical calculations run via Python CLI (`psychology_stats.py`, `generate_apa_docx.py`, `simdat_engine.py`) generating physical `stats_results.json` and APA 7 tables.
2. **Brains**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `methodology-expert`: Audits design, power, and validity.
   - `statistical-auditor`: Runs adversarial MSAI anomaly checks on `stats_results.json`.
   - `results-auditor`: Verifies APA 7 rules, leading zero compliance, and OpenXML layout.
   - `final-judge`: Simulates viva voce oral defense cross-examination.
3. **Orchestrator**: Cognitive roles and deterministic hands are orchestrated directly by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and decision journaling.
