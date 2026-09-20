# Independent Validation System Specification

**Document Version:** 1.0.0 (Phase 8 Implementation)  
**Core Architectural Law:** The producer must never be the sole judge of its own output.  
**Operative Date:** September 2026 (1405 SH)  

---

## 1. Executive Summary & Validation Mandate

In autonomous agent pipelines, allowing generator agents (`academic-writer`, `statistics-agent`) to evaluate their own work creates circular confirmation bias, unchecked hallucinations, and corrupted deliverables.

Under **Phase 8**, the Academic Suite establishes an independent, adversarial validation layer consisting of:
1. **`validation-agent`:** The cognitive evaluator and Viva Voce defense committee simulator.
2. **Deterministic Validators (`validators/`):** 5 programmatic inspection engines executing mathematical, statistical, and typographical verification on physical disk artifacts.

```text
+-----------------------------------------------------------------------------+
|                            PRODUCER AGENT                                   |
|   (e.g. statistics-agent, academic-writer, data-agent)                      |
|                                                                             |
|                     Generates physical candidate artifacts:                 |
|                     - sem_results.json / data_cleaned.xlsx                  |
|                     - 06_hypothesis_1.docx / 06_hypothesis_1.md             |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                            VALIDATION AGENT                                 |
|   (Independent Adversarial Auditor & Defense Committee Gatekeeper)          |
|                                                                             |
|                 Invokes Deterministic Validator Suite CLI:                  |
|          python3 validators/run_all_validators.py --stage-dir <path>        |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                       DETERMINISTIC VALIDATOR ENGINES                       |
|                                                                             |
|  1. data_integrity/          <- Little's MCAR, straight-lining, D2 outliers |
|  2. numerical_consistency/   <- df math (N-k-1), variance deflation, MSAI   |
|  3. statistical_assumptions/ <- Shapiro-Wilk, Levene, slope homogeneity     |
|  4. result_consistency/      <- Exact decimal match between JSON, MD, DOCX   |
|  5. reporting_consistency/   <- APA 7 borders, Persian leading zero, cliches|
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                       STANDARDIZED THREE-STATE VERDICT                      |
|                                                                             |
|               [ PASS ]   /   [ NEEDS_REVIEW ]   /   [ FAIL ]                |
|                                                                             |
|  - PASS: Clearance granted; Orchestrator advances to Stage X+1              |
|  - NEEDS_REVIEW: Flagged for researcher diagnostic inspection               |
|  - FAIL: Stage halted; Orchestrator re-delegates targeted fix               |
+-----------------------------------------------------------------------------+
```

---

## 2. Directory of Deterministic Validators (`validators/`)

### 1. `validators/data_integrity/`
- **Script:** [`validators/data_integrity/validator.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/data_integrity/validator.py)
- **Target Deliverables:** `data_cleaned.xlsx`, `00_data_curation_report.json`
- **Evaluated Signals:**
  - Missingness threshold check ($< 5\%$ allowed for EM imputation; $> 15\%$ requires case exclusion).
  - Unengaged respondent detection (zero-variance straight-lining flags `FAIL`).
  - Multivariate outliers: Confirms Mahalanobis $D^2$ ($p < .001$) outliers are documented in the curation log.
  - Little's MCAR test: Flags `FAIL` if missingness is MAR/MNAR ($p \le .05$) without appropriate handling.

### 2. `validators/numerical_consistency/`
- **Script:** [`validators/numerical_consistency/validator.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/numerical_consistency/validator.py)
- **Target Deliverables:** `stats_results.json`, `<stage>.json`
- **Evaluated Signals:**
  - Degrees of freedom concordance:
    $$df_{\text{error}} == N - k - 1$$
    Flags `FAIL` if reported $df$ does not match data dimensions.
  - Variance deflation screening: Flags `NEEDS_REVIEW` if $SD < 0.10 \times \text{Scale Range}$ (detects synthetic variance compression).
  - Parameter bounds: Verifies correlations remain in $[-1.0, +1.0]$ and $R^2$ in $[0.0, 1.0]$.
  - Multi-Signal Anomaly Index (MSAI) computation ($0-100$).

### 3. `validators/statistical_assumptions/`
- **Script:** [`validators/statistical_assumptions/validator.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/statistical_assumptions/validator.py)
- **Target Deliverables:** `03_parametric_assumptions.json`, `assumptions.json`
- **Evaluated Signals:**
  - Univariate Normality: Shapiro-Wilk test ($p > .05$) and Skewness/Kurtosis within $[-0.85, +0.85]$.
  - Homogeneity of Variance: Levene's test ($p > .05$). Flags `FAIL` if $p \le .05$ without Welch/robust correction.
  - Homogeneity of Regression Slopes: $Group \times Covariate$ interaction ($p > .05$). Flags `FAIL` if $p \le .05$ because ANCOVA is fundamentally invalid.
  - Multicollinearity: Collinearity diagnostics (VIF $< 5.0$, Tolerance $> .20$).

### 4. `validators/result_consistency/`
- **Script:** [`validators/result_consistency/validator.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/result_consistency/validator.py)
- **Target Deliverables:** Synchronized Triad (`<stage>.json` vs. `<stage>.md` vs. `<stage>.docx`)
- **Evaluated Signals:**
  - Cross-artifact numerical fidelity: Extracts exact test statistics (*t, F, p, \beta, d*) from `.json` and scans `.md` and `.docx` text.
  - Flags `FAIL` if a number reported in narrative or tables differs from the deterministic calculation JSON.
  - Verifies sample size $N$ is invariant across all 3 files.

### 5. `validators/reporting_consistency/`
- **Script:** [`validators/reporting_consistency/validator.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/reporting_consistency/validator.py)
- **Target Deliverables:** `<stage>.md`, `<stage>.docx`
- **Evaluated Signals:**
  - Persian Leading Zero Standard: Scans text for `.۰۰۱` or `.۰۵` without leading zero. Flags `FAIL` under Directive 4.
  - Prohibition of $p = .000$: Flags `FAIL` if $p = .000$ or $.000$ is detected. Must be $p < .001$ or $p < ۰.۰۰۱$.
  - APA 7 Table Borders: Verifies presence of exactly 3 horizontal borders and zero vertical borders.
  - Decoupled LTR Numbers: Confirms negative signs precede numbers ($-0.32$).
  - Robotic AI Cliché Detection: Flags expressions like *«شایان ذکر است که»* or *«پرواضح است»*.

---

## 3. Master Unified Validator CLI Runner

The suite is orchestrated via [`validators/run_all_validators.py`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/validators/run_all_validators.py):

```bash
python3 validators/run_all_validators.py --stage-dir projects/active/ch4/stage_4_6_1
```

### JSON Output Structure:
```json
{
  "suite": "Academic Suite Deterministic Validation Suite",
  "stage_directory": "projects/active/ch4/stage_4_6_1",
  "overall_verdict": "PASS",
  "results": [
    {
      "validator": "numerical_consistency",
      "verdict": "PASS",
      "errors": [],
      "warnings": [],
      "sample_size_audited": 60
    },
    {
      "validator": "reporting_consistency",
      "verdict": "PASS",
      "errors": [],
      "warnings": [],
      "file_audited": "06_hypothesis_1.md"
    }
  ]
}
```

---

## 4. Concrete Workflow Example: Statistics Agent to Validator

```text
Statistics Agent
       ↓
sem_results.json
       ↓
Statistical Validator (validators/numerical_consistency/validator.py)
       ↓
PASS / FAIL / NEEDS_REVIEW
```

1. **Generation:** `statistics-agent` runs `run_sem.py` on `data_cleaned.xlsx` and outputs `sem_results.json`.
2. **Handoff:** `academic-orchestrator` invokes `validation-agent` with the path to `sem_results.json`.
3. **Execution:** `validation-agent` executes:
   ```bash
   python3 validators/numerical_consistency/validator.py --stats sem_results.json --n 116
   ```
4. **Verdict Evaluation:**
   - If degrees of freedom match model parameters and fit indices satisfy cutoffs $\rightarrow$ **`PASS`**.
   - If CFI is between $0.90$ and $0.94$ $\rightarrow$ **`NEEDS_REVIEW`** with diagnostic guidance for modification indices.
   - If degrees of freedom are negative or $p = .000$ was emitted $\rightarrow$ **`FAIL`**, blocking stage progression.
