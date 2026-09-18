---
name: cfa
description: Execute Confirmatory Factor Analysis (CFA), factor loadings (lambda), construct reliability (CR/omega), convergent validity (AVE), and model fit.
---

# Confirmatory Factor Analysis (CFA) Skill (تحلیل عاملی تأییدی)

Evaluates measurement models, construct validity, convergent/discriminant validity, and factorial invariance for established psychometric instruments and theoretical dimensions.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Testing Established Theoretical Factor Structures**: The researcher has an a priori theoretical scale structure (e.g. 3-factor burnout, 5-factor personality) and needs to verify if empirical covariance data reproduces the hypothesized structure.
2. **Construct Validity Assessment**: Evaluating standardized factor loadings ($\lambda$), Construct Reliability ($\text{CR} \ge .70$), and Average Variance Extracted ($\text{AVE} \ge .50$).
3. **Measurement Invariance Testing**: Testing configural, metric, scalar, and strict invariance across demographic groups (e.g. male vs female, clinical vs non-clinical).
4. **Prerequisite Measurement Model for SEM**: Validating measurement models prior to estimating structural paths in Chapter 4 / Stage 05.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Unknown or Exploratory Factor Structure**: If the dimensionality is unestablished, novel, or exploratory, use **Exploratory Factor Analysis (EFA)** within `psychometric-scale-validator` first (Horn's Parallel Analysis).
2. **Small Sample Size ($N < 150$)**: CFA requires minimum $N \ge 200$ or a participant-to-parameter ratio $N:q \ge 10:1$. For tiny clinical samples, use CTT item analysis.
3. **Pure Single-Item Indicators**: Cannot run CFA on single-item global questions.
4. **Formative Constructs**: If indicators cause the construct rather than reflect it, use PLS-SEM rather than Covariance-Based CFA.

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned item-level dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Continuous or 5- to 7-point Likert items grouped by theoretical factor.
- **Minimum Sample Size**: $N \ge 200$ (ideally $N \ge 10 \times \text{number of items}$).
- **Model Specification (`cfa_spec.json`)**:
  ```json
  {
    "factors": {
      "emotional_exhaustion": ["item_1", "item_2", "item_3", "item_4"],
      "depersonalization": ["item_5", "item_6", "item_7"],
      "personal_accomplishment": ["item_8", "item_9", "item_10"]
    },
    "estimator": "MLR"
  }
  ```

---

## 4. Methodological & Statistical Assumptions
1. **Multivariate Normality**: Mardia's multivariate skewness and kurtosis. If violated, use Robust Maximum Likelihood (`MLR` / `MLM` with Satorra-Bentler correction).
2. **Independence of Observations**: No unmodeled clustering or nesting.
3. **Linearity**: Linear relationships between latent factors and observed indicators.
4. **Absence of Multicollinearity**: Inter-factor correlations $r < .85$.
5. **Identification**: Minimum 3 indicators per latent factor (or 2 if factors are correlated).

---

## 5. Method-Selection Decision Tree
```text
Factor Structure Known A Priori?
├── NO:
│   └── USE: EFA (Horn's Parallel Analysis & Promax rotation in psychometric-scale-validator)
└── YES:
    ├── Measurement Level & Distribution:
    │   ├── Multivariate Normal Likert (>= 5 categories): Maximum Likelihood (ML)
    │   ├── Non-Normal Continuous/Likert: Robust Maximum Likelihood (MLM / MLR)
    │   └── Binary / Ordinal (<= 4 categories): Diagonally Weighted Least Squares (WLSMV)
    └── Quality Evaluation Thresholds:
        ├── Factor Loadings: lambda >= .50 (ideally >= .70), p < .001
        ├── Convergent Validity: AVE >= .50 and CR >= .70
        ├── Discriminant Validity:
        │   ├── Fornell-Larcker: sqrt(AVE_i) > r_ij for all j != i
        │   └── HTMT (Heterotrait-Monotrait Ratio): HTMT < .85 (strict) or < .90
        └── Fit Indices: chi2/df < 3.0, CFI >= .95, TLI >= .95, RMSEA <= .06, SRMR <= .08
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/cfa/scripts/run_cfa.py \
  --data path/to/cleaned_data.xlsx \
  --spec path/to/cfa_spec.json \
  --estimator MLR \
  --output path/to/05_cfa_results.json
```

---

## 7. Output Contract & Artifacts
The script outputs:
1. **`cfa_results.json`**:
   - `fit_indices`: `{"chi2": ..., "df": ..., "chi2_df": ..., "cfi": ..., "tli": ..., "rmsea": ..., "rmsea_ci": [...], "srmr": ...}`
   - `factor_loadings`: List of `{"factor": ..., "item": ..., "unstd_b": ..., "std_loading": ..., "se": ..., "z": ..., "p": ...}`
   - `construct_validity`: `{"factor": ..., "ave": ..., "cr": ..., "omega": ...}`
   - `htmt_matrix`: Heterotrait-Monotrait correlation matrix.
2. **APA 7 OpenXML Word Table**: 3-line border table formatted in *B Nazanin* / *B Titr* with decoupled LTR numbers.

---

## 8. Validation & Forensic Sanity Checks
- **Degrees of Freedom Formula**: $df = \frac{p(p + 1)}{2} - q$, where $p$ is observed variables and $q$ is free parameters. Must be positive ($df > 0$).
- **Heywood Cases**: Check for negative error variances ($\theta < 0$) or standardized loadings $> 1.0$. If present, flag for model respecification.
- **Cross-Loading Hygiene**: Modification indices (MI) for error covariances permitted ONLY between items of the same latent factor with clear theoretical justification.

