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

### Step 7: Academic Writer Subagent (Persian Chapter 4 Drafting - 7-Part Deep Architecture)
- **Agent**: `academic-writer`
- **Action**:
  - Ingests verified tables, statistical results (`stats_results.json`), and generated 300-DPI plots.
  - Drafts Chapter 4 in authentic academic Persian structured strictly into Saber Ghaderi's **7-Part Architecture**:
    1. **مقدمه فصل چهارم** (Chapter Overview, analytical scope, and roadmap)
    2. **ویژگی‌های جمعیت‌شناختی نمونه** (Categorical frequency tables for gender, education, marital status, and age binning with dominant profile narratives)
    3. **یافته‌های توصیفی متغیرها** (The 9-column master table [متغیر, مؤلفه, N, M, SD, KU, SK, Min, Max] with Kline/strict normality interpretations)
    4. **بررسی مفروضه‌های ۶ گانه آزمون‌های پارامتریک** (Normality, Multicollinearity with Tolerance/VIF, Durbin-Watson independence, Breusch-Pagan homoscedasticity, Mahalanobis $D^2$ outlier screening, and G*Power/sample size justification)
    5. **یافته‌های استنباطی و آزمون فرضیه‌ها** (Each hypothesis formulated with Saber's **4-Tier Sequence**: Tier 1 Bivariate Correlation $\to$ Tier 2 Combined ANOVA & Model Summary $\to$ Tier 3 Regression Coefficients $\to$ Tier 4 Diagnostic Residual Plots)
    6. **تحلیل مدل‌های ساختاری / میانجی‌گری** (Hayes PROCESS Model 6 serial mediation with 5,000 bootstrap iterations or R lavaan SEM with 11 fit indices and path diagram)
    7. **سنتز و جدول ماتریس خلاصه آزمون فرضیه‌ها** (Executive summary table of all hypotheses and final empirical verdicts)
  - Enforces Persian half-spaces (`\u200c`), standard dot notation for decimals, preserving leading zero (`۰.۰۰۱`, `۰.۰۵`), and eliminating all AI clichés.
  - Compiles publication-ready Word document with OpenXML directionality `<w:bidi w:val="1"/>`, borderless APA 7 tables, and physically embedded 300-DPI figures via `generate_apa_docx.py`.
- **Output**: `Chapter_4_Results.docx` (yielding authentic 2,500 to 10,000+ words).

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

## Dual Execution Modes (Directive 12 & HYBRID_MULTI_AGENT_SPEC)

### Mode 1: Monolithic Offline Batch Execution
For automated batch compilation, background pipelines, and CI/CD tests without interactive deliberation:
```bash
python3 -c "from digital_saber import DigitalSaber; DigitalSaber().run_workflow('chapter4', output_dir='output')"
```
*Executes all 10 stages in a single Python process, deterministically generating all Directive 3 artifacts on disk.*

### Mode 2: Antigravity Native Multi-Agent Deliberation
For interactive high-stakes dissertation review, viva voce cross-examination, and adversarial auditing:
1. Deterministic calculation runs via Python CLI to generate physical `stats_results.json`.
2. The coordinator agent calls `invoke_subagent` to spawn independent reviewer subagents:
   - `methodology-expert`: Audits design, power, and validity.
   - `statistical-auditor`: Runs adversarial MSAI anomaly checks on `stats_results.json`.
   - `results-auditor`: Verifies APA 7 rules, leading zero compliance, and OpenXML layout.
   - `final-judge`: Simulates viva voce oral defense cross-examination.
3. Subagents run concurrently in separate contexts and report findings back to the coordinator.
4. Coordinator reconciles critiques and commits approved deliverables.
