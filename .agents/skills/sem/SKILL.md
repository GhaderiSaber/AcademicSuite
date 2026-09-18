---
name: sem
description: Execute Structural Equation Modeling (SEM), evaluating latent structural paths and 11 Goodness-of-Fit indices against Hu & Bentler (1999) cutoffs.
---

# Structural Equation Modeling (SEM) Skill (مدل‌یابی معادلات ساختاری)

Evaluates complex latent structural relationships, simultaneous direct/indirect paths, and macro-model goodness-of-fit against the institutional 11-Pillar Hu & Bentler (1999) benchmarks.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Testing Complex Theoretical Network Models**: Simultaneously evaluating multiple independent variables, multiple mediators, and multiple dependent constructs.
2. **Latent Variable Modeling**: Accounting for measurement error by modeling latent constructs derived from multiple observed indicators (unlike standard regression which assumes zero measurement error).
3. **Macro Model Fit Assessment**: Stage 05 macro-model evaluation calculating all 11 fit indices ($\chi^2, \chi^2/df, \text{CFI}, \text{TLI}, \text{IFI}, \text{NFI}, \text{GFI}, \text{AGFI}, \text{RMSEA}, \text{SRMR}$).
4. **Structural Path Significance**: Estimating standardized path coefficients ($\beta$), standard errors, critical ratios ($z$), and $p$-values.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Small Sample Size ($N < 200$)**: Covariance-based SEM is unreliable on small samples. If $N < 150$, use Partial Least Squares (PLS-SEM) or path analysis with observed composite scores.
2. **Pure Observed Variable Regression**: If all variables are single observed indicators without latent constructs, use Multiple Regression (`regression`) or PROCESS Path Analysis (`mediation`).
3. **Exploratory Factor Mining**: Never use SEM to discover factor structures; conduct CFA (`cfa`) first to establish measurement model adequacy before fitting structural paths.

---

## 3. Required Data & Input Contract
- **Input File**: Analysis-ready dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Continuous or composite scale scores / multi-item Likert indicators.
- **Minimum Sample Size**: $N \ge 200$ (Kline 2023 guideline: $N:q \ge 10:1$ to $20:1$).
- **Model Specification (`sem_model.json`)**:
  ```json
  {
    "measurement_model": {
      "mindfulness": ["item_1", "item_2", "item_3"],
      "psych_flexibility": ["item_4", "item_5", "item_6"],
      "burnout": ["item_7", "item_8", "item_9"]
    },
    "structural_paths": [
      {"from": "mindfulness", "to": "psych_flexibility"},
      {"from": "psych_flexibility", "to": "burnout"},
      {"from": "mindfulness", "to": "burnout"}
    ],
    "estimator": "MLR"
  }
  ```

---

## 4. Methodological & Statistical Assumptions
1. **Multivariate Normality**: Assessed via Mardia's coefficient (kurtosis $< 5.0$). If violated, use Robust Satorra-Bentler corrections (`estimator: "MLM"` or `"MLR"`).
2. **Linearity**: Presumes linear structural relations among latent variables.
3. **Proper Model Identification**: The number of unique data moments $p(p + 1)/2$ must exceed the number of free parameters $q$ ($df > 0$).
4. **Absence of Multicollinearity**: Extreme collinearity between exogenous latents ($\phi > .85$) destabilizes matrix inversion.

---

## 5. Method-Selection Decision Tree
```text
Latent Constructs or Observed Composites?
├── Observed Composite Variables Only:
│   └── USE: Path Analysis via OLS Regression or PROCESS (mediation / moderation)
└── Latent Constructs with Observed Indicators:
    ├── Sample Size & Distribution:
    │   ├── N >= 200 & Normal / Moderately Non-Normal:
    │   │   └── USE: Covariance-Based SEM (lavaan / run_sem.py)
    │   │       ├── Mardia Kurtosis < 5.0: Standard Maximum Likelihood (ML)
    │   │       └── Mardia Kurtosis >= 5.0: Robust Maximum Likelihood (MLM / MLR)
    │   └── N < 150 or Formative Constructs:
    │       └── USE: Partial Least Squares SEM (PLS-SEM)
    └── Fit Indices Benchmarks (Hu & Bentler, 1999):
        ├── Absolute Fit: chi2/df < 3.0, RMSEA <= .06 (90% CI upper <= .08), SRMR <= .08
        ├── Incremental Fit: CFI >= .95, TLI >= .95, IFI >= .95
        └── Parsimony Fit: PNFI >= .50, PCFI >= .50
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/sem/scripts/run_sem.py \
  --data path/to/cleaned_data.xlsx \
  --spec path/to/sem_model.json \
  --estimator MLR \
  --output path/to/05_macro_model.json
```

---

## 7. Output Contract & Artifacts
The script outputs:
1. **`05_macro_model.json`**:
   - `fit_indices`: Evaluated against Hu & Bentler benchmarks (`PASS` / `MARGINAL` / `FAIL`).
   - `structural_paths`: Standardized coefficients ($\beta$), unstandardized ($B, SE$), critical ratios ($z$), and $p$-values.
   - `indirect_effects`: 5,000 bootstrap CI for mediated paths.
   - `r_squared`: Explained variance for each endogenous latent construct ($R^2$).
2. **APA 7 OpenXML Word Deliverable (`05_macro_model.docx`)**:
   - 3-Line Macro Model Fit Table (Persian titles, *Times New Roman* decoupled stats).
   - Structural Path Coefficients Table with asterisks (`*** p < .001`).
3. **Markdown Inspection Artifact (`05_macro_model.md`)**: Full human-readable results narrative.

---

## 8. Validation & Forensic Sanity Checks
- **Degrees of Freedom**: Ensure positive $df$. Zero $df$ indicates just-identified (saturated) model with untestable fit.
- **Out-of-Bounds Standardized Estimates**: Check that no $|\beta| > 1.0$ (indicative of multicollinearity or specification error).
- **Residual Covariances**: Standardized residual covariance matrix values must lie between $-2.58$ and $+2.58$.

