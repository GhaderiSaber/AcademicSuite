# Deterministic Execution Layer Specification

**Document Version:** 1.0.0 (Phase 6 Implementation)  
**Core Invariant:** Moving Deterministic Calculation Out of LLM Memory  
**Operative Date:** September 2026 (1405 SH)  

---

## 1. Architectural Mandate: The Model Orchestrates, Code Calculates

A primary failure mode of LLM-based research assistants is attempting to perform arithmetic, sample statistics, correlation matrices, degrees of freedom, and $p$-value calculations in generative memory. This inevitably produces mathematical hallucinations, inconsistent degrees of freedom, and unpublishable findings.

The Academic Suite strictly decouples cognition from computation:

$$\text{Cognitive Agent (LLM)} \overset{\text{specifies}}{\longrightarrow} \text{Skill Procedure} \overset{\text{executes}}{\longrightarrow} \text{R / Python CLI} \overset{\text{outputs}}{\longrightarrow} \text{Structured JSON Artifact}$$

```text
+-----------------------------------------------------------------------------+
|                             COGNITIVE LAYER (LLM)                           |
|  - Understands research question & theoretical framework                   |
|  - Selects appropriate statistical test from 10-step parametric tree        |
|  - Compiles execution specification (spec.json)                             |
|  - Never performs mental math, rounding, or p-value estimation              |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                             SKILL PROCEDURE LAYER                           |
|  - Exposes standardized input/output JSON schemas                           |
|  - Documents parameter cutoffs (Hu & Bentler, Cohen, Shadish)               |
|  - Provides verified CLI recipes and benchmark examples                     |
+-------------------------------------+---------------------------------------+
                                      | run_command
                                      v
+-----------------------------------------------------------------------------+
|                     DETERMINISTIC EXECUTION LAYER ("The Hands")             |
|                                                                             |
|   +--------------------------+       +----------------------------------+   |
|   |    R / lavaan Scripts    |       |      Python / semopy / pingouin  |   |
|   | - run_sem.R              |       | - run_sem.py                     |   |
|   | - run_cfa.R              |  OR   | - run_cfa.py                     |   |
|   | - run_mediation.R        |       | - run_mediation.py               |   |
|   +--------------------------+       +----------------------------------+   |
|                                                                             |
|  - Reads physical empirical dataset (.xlsx, .csv, .sav)                     |
|  - Injects local virtualenv packages dynamically (.venv site-packages)       |
|  - Performs exact linear algebra, matrix inversion & bootstrapping          |
|  - Exits with return code 0 or explicit error trace                         |
+-------------------------------------+---------------------------------------+
                                      | writes to disk
                                      v
+-----------------------------------------------------------------------------+
|                        STRUCTURED CHECKPOINT ARTIFACTS                      |
|  - sem_results.json / mediation_results.json / data_cleaned.xlsx            |
|  - Synchronized Triad: <stage>.docx + <stage>.md + <stage>.json             |
|  - Ingested by Validation Layer for Multi-Signal Anomaly Index (MSAI)       |
+-----------------------------------------------------------------------------+
```

---

## 2. Exemplar Execution Pipelines

### Pipeline A: Structural Equation Modeling (SEM)
```text
statistics-agent
       │
       ▼
   SEM Skill (.agents/skills/sem/)
       │
       ▼
run_sem.py / run_sem.R
       │
       ▼
sem_results.json
```

1. **Cognitive Step (`statistics-agent`):** Identifies latent constructs, measurement items, and directional structural paths from the theoretical model. Formulates `sem_spec.json`.
2. **Procedure Step (`sem/SKILL.md`):** Specifies 11 Goodness-of-Fit indices to extract against Hu & Bentler (1999) cutoffs ($\chi^2/df \le 3.0, CFI \ge .95, TLI \ge .95, RMSEA \le .06, SRMR \le .08$).
3. **Execution Step (`run_sem.py` / `run_sem.R`):**
   ```bash
   python3 .agents/skills/sem/scripts/run_sem.py \
     --data data_cleaned.xlsx \
     --spec sem_spec.json \
     --output 05_macro_model.json
   ```
4. **Structured Result (`05_macro_model.json`):** Contains exact $\chi^2, df, p$, standardized path coefficients ($\beta$), standard errors ($SE$), and $z$-values. The LLM extracts these exact values into the manuscript without alteration.

---

### Pipeline B: Bootstrap Mediation (PROCESS Model 4)
```text
statistics-agent
       │
       ▼
Mediation Skill (.agents/skills/mediation/)
       │
       ▼
run_mediation.py / run_mediation.R
       │
       ▼
mediation_results.json
```

1. **Cognitive Step (`statistics-agent`):** Maps independent variable ($X$), mediator ($M$), and dependent variable ($Y$), rejecting Baron & Kenny in favor of Preacher & Hayes bootstrapping.
2. **Procedure Step (`mediation/SKILL.md`):** Configures 5,000 bootstrap resamples and Bias-Corrected and Accelerated (BCa) 95% confidence intervals.
3. **Execution Step (`run_mediation.py` / `run_mediation.R`):**
   ```bash
   python3 .agents/skills/mediation/scripts/run_mediation.py \
     --data data_cleaned.xlsx \
     --iv mindfulness \
     --mediator psychological_flexibility \
     --dv wellbeing \
     --bootstrap 5000 \
     --output XX_mediation_1.json
   ```
4. **Structured Result (`XX_mediation_1.json`):** Contains path $a$, path $b$, direct effect $c'$, total effect $c$, indirect effect $a \times b$, and exact $[CI_{\text{lower}}, CI_{\text{upper}}]$.

---

### Pipeline C: Data Audit & Outlier Screening
```text
data-agent
    │
    ▼
Data Audit Skill (.agents/skills/data-audit/)
    │
    ▼
audit_dataset.py
    │
    ▼
00_data_audit_report.json
```

1. **Cognitive Step (`data-agent`):** Ingests raw data file and inspects variable columns.
2. **Procedure Step (`data-audit/SKILL.md`):** Defines parameters for Little's MCAR test, zero-variance straight-lining, and Mahalanobis $D^2$ ($\alpha = .001$).
3. **Execution Step (`audit_dataset.py`):**
   ```bash
   python3 .agents/skills/data-audit/scripts/audit_dataset.py \
     --data data/raw_data.xlsx \
     --output 00_data_audit_report.json
   ```
4. **Structured Result (`00_data_audit_report.json`):** Outputs exact missingness rate, Little's MCAR $p$-value, and list of flagged outlier IDs.

---

### Pipeline D: Micro-Stage Triad Scaffolding
```text
writing-agent
      │
      ▼
Chapter 4 Writing Skill (.agents/skills/chapter-4-writing/)
      │
      ▼
scaffold_chapter4_triad.py
      │
      ▼
06_hypothesis_1.docx + .md + .json
```

1. **Cognitive Step (`writing-agent`):** Formulates narrative dissection and interpretations for Hypothesis 1.
2. **Procedure Step (`chapter-4-writing/SKILL.md`):** Mandates synchronized triad generation under Directive 3.
3. **Execution Step (`scaffold_chapter4_triad.py`):**
   ```bash
   python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py \
     --stage "Hypothesis 1 Testing" \
     --base "06_hypothesis_1" \
     --outdir projects/active/ch4
   ```
4. **Structured Result:** Physically generates `06_hypothesis_1.docx`, `06_hypothesis_1.md`, and `06_hypothesis_1.json` on disk before any assembly or advancement.

---

## 3. Dynamic Environment Discovery Architecture

To prevent execution failures caused by Python environment mismatches (e.g. running system `python3` instead of `.venv/bin/python3`), every statistical script in `.agents/skills/*/scripts/` incorporates automated local virtualenv discovery:

```python
# Dynamic discovery of local virtualenv site-packages (.venv / venv)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)
```

This guarantees seamless runtime access to:
- `semopy` (Structural Equation Modeling)
- `pingouin` (Parametric tests, mediation, ANCOVA, reliability)
- `statsmodels` (Multiple linear regression, GLM, ANOVA)
- `scipy` & `numpy` (Probability distributions, matrix inversion)
- `pandas` & `openpyxl` (SPSS, Excel, CSV dataset manipulation)
- `python-docx` (OpenXML Word document compilation)

---

## 4. Governing Invariants of Deterministic Execution

1. **Directive 2 (Zero Mental Calculation):** Test statistics ($t, F, \chi^2, z$), degrees of freedom ($df$), $p$-values, effect sizes ($\eta_p^2, d, R^2$), and confidence intervals must never be calculated or estimated mentally in LLM memory.
2. **Directive 4 (Prohibition of $p = .000$):** Scripts and reporting templates format $p$-values $< .001$ strictly as $p < .001$ (or $p < ۰.۰۰۱$ / $۰.۰۰۱ > p$ in Persian).
3. **Directive 9 (Realistic Decimal Noise):** Synthetic and simulated datasets must inject bounded empirical decimal noise ($\delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$) rather than whole-integer group means.
4. **Directive 3 (Artifact Triad Completeness):** Every inferential stage must emit physical on-disk checkpoint artifacts before validation clearance is requested.
