---
name: scale_validation
description: >-
  Psychometric scale standardization, Classical Test Theory (CTT), Item Response Theory (IRT), CVR/CVI, and construct validation.
---

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
                        │ STAGE V.1: CONTENT VALIDITY  │
                        │ Lawshe CVR & Lynn CVI Panel  │
                        │ (01_content_validity.docx)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE V.2: ITEM ANALYSIS   │
                        │ Loop Discrimination & Loop   │
                        │ (02_item_analysis.docx)      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE V.3: EFA FACTORING   │
                        │ KMO, Bartlett, Scree Plot    │
                        │ (03_efa_results.docx)        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE V.4: CFA MODELING    │
                        │ lavaan Fit Indices & Loadings│
                        │ (04_cfa_results.docx)        │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE V.5: CONSTRUCT VALIDITY│
                        │ AVE, CR, HTMT, Fornell-Larck │
                        │ (05_construct_validity.docx) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE V.6: RELIABILITY & INV │
                        │ Alpha, Omega, Multigroup Inv │
                        │ (06_reliability_inv.docx)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE V.7: IRT & ROC CURVES  │
                        │ Samejima GRM, TIF & Cut-offs │
                        │ (07_irt_roc.docx)            │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE V.8: REPORT ASSEMBLY   │
                        │ OpenXML Section Assembly     │
                        │(Scale_Validation_Report.docx)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE V.9: FINAL JUDGE     │
                        │ Psychometric Defense Sim     │
                        │(XX_val_defense_brief.docx)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                               FINAL DELIVERABLES
                • Scale_Validation_Report.docx (Chapter 4 Psychometric Report)
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

### Micro-Stage Execution Sequence & Anti-Shortcut Protocol (Directive 3 & 11)

To prevent shortcutting, scale validation reporting is strictly partitioned into independent micro-stages:

#### Stage V.1: Content Validity Ratio (CVR) & Index (CVI)
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `01_content_validity.docx` (Lawshe CVR and Lynn CVI expert panel ratings).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.2: Item Analysis & Classical Descriptives
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `02_item_analysis.docx` (Corrected item-total correlations, alpha-if-item-deleted, loop discrimination).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.3: Exploratory Factor Analysis (EFA)
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `03_efa_results.docx` (KMO, Bartlett test of sphericity, scree plot, Promax/Varimax rotation).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.4: Confirmatory Factor Analysis (CFA)
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `04_cfa_results.docx` (Standardized factor loadings, modification indices, 11 fit indices).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.5: Convergent & Discriminant Validity
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `05_construct_validity.docx` (AVE, CR, HTMT matrix, Fornell-Larcker criterion).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.6: Scale Reliability & Measurement Invariance
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `06_reliability_inv.docx` (Cronbach's $\alpha$, McDonald's $\omega$, multigroup configural/metric/scalar invariance).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.7: Modern Psychometrics (IRT & ROC Diagnostics)
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `07_irt_roc.docx` (Samejima GRM parameters, Test Information Functions, ROC optimal cut-offs).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.8: Scale Validation Report Assembly
- **Agent**: Execution Layer via `orchestrator_cli.py --assemble-chapter Scale_Validation_Report.docx`
- **Output**: `Scale_Validation_Report.docx` (Concatenated from verified section documents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage V.9: Final Psychometric Defense Simulator
- **Agent**: `final-judge`
- **Output**: `XX_val_defense_brief.docx` (Cross-examination on invariance, DIF, and diagnostic cut-offs).
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

## Deliverables Checklist
- [ ] `Psychometric_Validation_Report.docx` — Complete Chapter 4 psychometric validation report with 8 APA 7 tables.
- [ ] `psychometric_validation_matrix.xlsx` — 6-sheet master psychometric Excel matrix.
- [ ] `psychometric_scree_roc_plots.png` — 300-DPI Scree & ROC curve plots.
- [ ] `psychometric_irt_plots.png` — 300-DPI IRT TIF & Item Characteristic Curves.
- [ ] `cfa_lavaan_model.R` — Executable CFA lavaan model script.
- [ ] `psychometric_validation_report.json` — Machine-readable psychometric metrics ledger.

---

## Antigravity Multi-Agent Execution Architecture (Directive 12, 12.1 & PURE_ANTIGRAVITY_DELIBERATION_PROTOCOL)

1. **The Hands**: Deterministic tools (`psychometric_validator_engine.py`, `generate_validation_docx.py`, `simdat_engine.py`) run via CLI to compute CVR/CVI, EFA/CFA, IRT parameters, ROC curves, and OpenXML tables on disk.
2. **The Brains & Critics**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `psychometric-expert`: Formulates scale adaptation protocol, item discrimination, and IRT/CFA model specifications.
   - `statistical-auditor`: Audits factor loadings, AVE/CR convergent-discriminant validity, and Multi-Signal Anomaly Index.
   - `results-auditor`: Verifies strict APA 7 table formatting and psychometric symbol notation ($\omega, \alpha, \lambda, \theta$).
   - `academic-writer`: Compiles the 8-table psychometric validation report in academic Persian.
   - `final-judge`: Cross-examines measurement invariance, differential item functioning (DIF), and clinical cut-off determination.
3. **Sole Orchestrator**: Subagents and execution instruments are orchestrated directly and exclusively by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and the Critic-Generator Barrier.

