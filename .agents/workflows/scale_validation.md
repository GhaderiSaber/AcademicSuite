# Psychometric Scale Standardization & Validation Workflow (هنجاریابی، روان‌سنجی و اعتباریابی ابزارهای اندازه‌گیری)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for executing the complete psychometric standardization and validation lifecycle under both **Classical Test Theory (CTT)** and modern **Item Response Theory (IRT)**.

```text
                                     INPUT
               Scale Metadata / Items / Scored Dataset (.xlsx, .sav, .csv)
               (Instrument Query, Expert Panel Ratings, Validation Scope)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │ Questionnaire Registry Lookup│
                        │ & Reverse-Key Resolution     │
                        │ (psychometric-scale-resolver)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 2: STATISTICAL EXPERT │
                        │ Content Validity & CVR / CVI │
                        │ Lawshe (1975) & Lynn (1986)  │
                        │ (psychometric-scale-validator│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 3: STATISTICAL EXPERT │
                        │ Construct Validity: EFA & CFA│
                        │ KMO, Scree, Promax, lavaan R │
                        │(psychometric-scale-validator)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 4: STATISTICAL EXPERT │
                        │ Convergent & Discriminant    │
                        │ Fornell-Larcker, AVE, CR,    │
                        │ HTMT, Omega (ω), Alpha (α)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 5: STATISTICAL AUDITOR │
                        │ Item Response Theory (IRT) & │
                        │ Samejima GRM, Infit/Outfit,  │
                        │ TIF Curves & ROC Cut-offs    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 6: DATA SIMULATOR      │
                        │ Monte Carlo Empirical Noise  │
                        │ (Rule 9 Non-Integer Means)   │
                        │ (psychometric-data-simulator)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STEP 7: OPENXML COMPILATION  │
                        │ 8-Table APA 7 Report (.docx) │
                        │ 6-Sheet Matrix (.xlsx), Plots│
                        │ (openxml_artifact_engine)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 8: FINAL JUDGE      │
                        │ Committee Defense Simulation │
                        │ & Saber Human Gate (124911145│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • گزارش_اعتباریابی_روانسنجی.docx (Chapter 4 Psychometric Report)
               • psychometric_validation_matrix.xlsx (6-Sheet Master Matrix)
               • psychometric_scree_roc_plots.png & irt_plots.png (300-DPI Plots)
               • cfa_lavaan_model.R (Executable CFA Analysis Script)
               • psychometric_validation_report.json (Structured Metrics Ledger)
```

---

## Prerequisites & Required Inputs

- **Scale Specifications**:
  - Target scale name, original authors, target construct, subscale structure, Likert scoring range (e.g. 1–5, 1–7), and negative/reverse-keyed items.
- **Validation Dataset / Empirical Ratings**:
  - Item responses matrix from participants ($N \ge 200$ for EFA/CFA; $N \ge 300$ for IRT).
  - Expert panel ratings for Content Validity ($N = 8 \text{ to } 15$ subject matter experts).
  - Criterion / Gold standard scores for ROC clinical cut-off determination.

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Registry Lookup & Reverse Scoring)
- **Agent**: `digital-saber` (wielding `psychometric-scale-resolver`)
- **Action**:
  - Queries `Questionnaires.xlsx` (4,880 instruments) to resolve factor structures, theoretical means, and reverse scoring keys.
  - Automatically identifies negatively phrased items and executes item inversion:
    $$X_{\text{reversed}} = (\text{Max} + \text{Min}) - X$$
  - Generates verified item profiles and subscale composite indicators.
- **Output**: Verified item scoring key and inverted dataset matrix.

### Step 2: Statistical Expert Subagent (Content Validity Ratio & Index)
- **Agent**: `statistical-expert` (wielding `psychometric-scale-validator`)
- **Action**:
  - Computes **Lawshe (1975) Content Validity Ratio ($CVR$)**:
    $$CVR = \frac{n_e - \frac{N}{2}}{\frac{N}{2}}$$
    Evaluates each item against critical thresholds for expert panel size (e.g. $CVR_{\text{crit}} = 0.59$ for $N=11$ at $p < .05$).
  - Computes **Waltz & Bausell / Lynn (1986) Content Validity Index ($CVI$)**:
    - Item-level $I\text{-}CVI \ge 0.78$.
    - Scale-level $S\text{-}CVI/\text{Ave} \ge 0.80$.
  - Computes Item Impact Score ($\text{Frequency} \times \text{Importance} \ge 1.5$).
- **Output**: Content validity audit table with Lawshe significance flags.

### Step 3: Statistical Expert Subagent (Construct Validity: EFA & CFA)
- **Agent**: `statistical-expert` (wielding `psychometric-scale-validator`)
- **Action**:
  - **Exploratory Factor Analysis (EFA)**:
    - Kaiser-Meyer-Olkin (KMO) sampling adequacy ($> 0.80$).
    - Bartlett's Test of Sphericity ($p < .001$).
    - Scree plot extraction and Promax oblique rotation (factor loadings $\lambda \ge 0.40$).
  - **Confirmatory Factor Analysis (CFA)**:
    - Fit indices: $\chi^2/df < 3.0$, $CFI \ge .90$, $TLI \ge .90$, $RMSEA \le .08$, $SRMR \le .08$.
    - Generates executable R `lavaan` model script (`cfa_lavaan_model.R`).
- **Output**: EFA rotated factor matrix, Scree plot, and CFA goodness-of-fit table.

### Step 4: Statistical Expert Subagent (Convergent, Discriminant & Reliability Metrics)
- **Agent**: `statistical-expert` and `statistical-auditor`
- **Action**:
  - **Fornell & Larcker (1981) Construct Validity**:
    - Average Variance Extracted ($AVE \ge 0.50$).
    - Composite Reliability ($CR \ge 0.70$).
    - Discriminant Validity: $\sqrt{AVE_j} > r_{jk} \quad (\forall k \neq j)$.
    - Heterotrait-Monotrait Ratio of Correlations ($HTMT < .85$).
  - **APA 7th Edition Modern Reliability**:
    - McDonald's Omega ($\omega_t \ge .70$, $\omega_h \ge .60$).
    - Cronbach's Alpha ($\alpha \ge .70$) with item-deleted diagnostics.
    - Test-Retest Intraclass Correlation Coefficient ($ICC \ge .75$).
- **Output**: Convergent, discriminant, and reliability evaluation matrices.

### Step 5: Statistical Auditor Subagent (Item Response Theory & Clinical Cut-offs)
- **Agent**: `statistical-auditor` (wielding `psychometric-scale-validator`)
- **Action**:
  - **Samejima's Graded Response Model (GRM)**:
    - Item discrimination ($a_i$ categorized via Baker 2001 criteria).
    - Category threshold difficulty parameters ($b_{ik}$).
    - Infit & Outfit Mean Square ($MNSQ \in [0.60, 1.40]$).
  - **Information & Errors**:
    - Item Information Functions (IIF) and Test Information Function (TIF).
    - Conditional Standard Error of Measurement: $SE(\theta) = 1/\sqrt{I(\theta)}$.
  - **Norm Transformations & ROC Analysis**:
    - Norm tables: Raw Score $\to$ Z-Score $\to$ T-Score $\to$ Percentile Rank ($PR$).
    - ROC Curve: Sensitivity, Specificity, AUC ($> 0.80$), and optimal cut-off via Youden's $J = \text{Sens} + \text{Spec} - 1$.
- **Output**: IRT parameters, TIF/CCC plots, norm conversions, and ROC cut-off table.

### Step 6: Data Simulator Subagent (Organic Empirical Noise - Rule 9 & Rule 10)
- **Agent**: `statistical-expert` (wielding `psychometric-data-simulator`)
- **Action**:
  - When simulating psychometric datasets, strictly enforces **Rule 9**:
    - Group means must have bounded decimal noise ($\delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$).
    - Whole-integer artificial means ($M = 5.000$) are strictly prohibited.
    - Discrete participant Likert responses ($1 \le X_{ij} \le 5$).
    - Non-identical standard deviations ($SD \neq 1.000$).
  - Preserves univariate normality (Skewness & Kurtosis within $[-0.85, +0.85]$).
- **Output**: Clean, organic psychometric simulation datasets.

### Step 7: OpenXML Physical Document Compilation
- **Agent**: `academic-writer` (wielding `openxml_artifact_engine`)
- **Action**:
  - Compiles `گزارش_اعتباریابی_روانسنجی.docx`:
    - 8 APA 7th Edition borderless tables (Demographics, CVR/CVI, EFA, CFA, Fornell-Larcker, Reliability, IRT, Norms).
    - BiDi directionality (`<w:bidi w:val="1"/>` and `<w:bidiVisual/>`).
    - Embedded 300-DPI visual plots.
  - Compiles `psychometric_validation_matrix.xlsx`:
    - 6 formatted Excel sheets (Item Analysis, EFA Loadings, CFA Fit, IRT GRM Parameters, Norm Conversions, ROC Diagnostics).
  - Compiles `cfa_lavaan_model.R` and `psychometric_validation_report.json`.
- **Output**: Complete validation document package.

### Step 8: Final Judge Subagent & Human Gate
- **Agent**: `final-judge` and `digital-saber`
- **Action**:
  - Evaluates Psychometric Rigor & Defense Readiness Index (Target: $\ge 95\%$).
  - Submits review card to Saber Admin Desk (`124911145`) under **Rule 11**.
  - Logs entry in `DecisionJournalEngine`.
- **Output**: Final approved psychometric validation package.

---

## Deliverables Checklist
- [ ] `گزارش_اعتباریابی_روانسنجی.docx` — Complete Chapter 4 psychometric validation report with 8 APA 7 tables.
- [ ] `psychometric_validation_matrix.xlsx` — 6-sheet master psychometric Excel matrix.
- [ ] `psychometric_scree_roc_plots.png` — 300-DPI Scree & ROC curve plots.
- [ ] `psychometric_irt_plots.png` — 300-DPI IRT TIF & Item Characteristic Curves.
- [ ] `cfa_lavaan_model.R` — Executable CFA lavaan model script.
- [ ] `psychometric_validation_report.json` — Machine-readable psychometric metrics ledger.
