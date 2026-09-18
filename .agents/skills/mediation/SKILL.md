---
name: mediation
description: Execute Preacher & Hayes bootstrap mediation (PROCESS Model 4) with 5,000 resamples, generating 95% BCa confidence intervals for indirect effects.
---

# Mediation Analysis Skill (تحلیل میانجی‌گری با روش بوت‌استرپ)

Executes modern Preacher & Hayes bootstrap mediation modeling (PROCESS Model 4 and Model 6), decomposing total effects into direct and indirect pathways with 5,000 Bias-Corrected and Accelerated (BCa) bootstrap confidence intervals.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Testing Indirect Explanatory Mechanisms**: Evaluating whether a third variable ($M$) transmits or mediates the effect of an independent predictor ($X$) onto a dependent outcome ($Y$).
2. **Hypothesis Testing for Intermediary Processes**: Testing hypotheses such as: "Mindfulness indirectly reduces burnout through the mediation of psychological flexibility."
3. **Evaluating Serial Mediation Chains**: Testing sequential explanatory cascades ($X \to M_1 \to M_2 \to Y$) under PROCESS Model 6.
4. **Decomposing Causal Paths**: Calculating unstandardized and standardized path coefficients: path $a$ ($X \to M$), path $b$ ($M \to Y$), path $c'$ (direct effect $X \to Y$), path $c$ (total effect), and indirect effect ($a \times b$).

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Sobel Test Alone (Baron & Kenny 1986)**: NEVER rely on the traditional Sobel $z$-test or Baron & Kenny 4-step criteria. The product distribution of $a \times b$ is positively skewed and non-normal, making Sobel severely underpowered and prone to Type II errors.
2. **Multi-Item Latent Constructs with Measurement Error**: If constructs have multiple Likert items and measurement error must be accounted for, use Latent Structural Equation Modeling (`sem`).
3. **Severe Multicollinearity**: If $r(X, M) > .80$, severe collinearity inflates standard errors of direct effect path $c'$.
4. **Cross-Sectional Data Over-Interpreted as Causality**: Causality cannot be claimed from cross-sectional designs; interpretation must use probabilistic language ("supports an indirect association").

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Continuous or composite scale scores ($X$: Independent, $M$: Mediator, $Y$: Dependent, plus optional covariates $C_1, C_2$).
- **Minimum Sample Size**: $N \ge 120$ for bootstrap stability (ideally $N \ge 200$).
- **Model Arguments**:
  - `--iv`: Predictor variable column name.
  - `--mediator`: Mediator variable column name(s).
  - `--dv`: Outcome variable column name.
  - `--bootstrap`: Number of resamples (mandatory: **5000**).
  - `--ci`: Confidence interval width (**95**).

---

## 4. Methodological & Statistical Assumptions
1. **Linearity**: Linear relationships for $X \to M$, $M \to Y$, and $X \to Y$.
2. **Homoscedasticity & Normality of OLS Residuals**: Evaluated via Breusch-Pagan test and Q-Q plots.
3. **No Unmeasured Confounding**: Assumes no unmeasured confounders for $X \to Y$, $X \to M$, and $M \to Y$ relationships.
4. **Temporal Ordering**: Ideally $X$ precedes $M$, and $M$ precedes $Y$ in time.

---

## 5. Method-Selection Decision Tree
```text
Mediation Methodology Selection:
├── Latent Constructs with Multiple Items?
│   └── USE: Latent SEM (sem skill with lavaan bootstrap mediation)
└── Observed Composite Scale Scores:
    ├── Number and Structure of Mediators:
    │   ├── Single Mediator (X -> M -> Y):
    │   │   └── USE: PROCESS Model 4 (Simple Bootstrap Mediation)
    │   ├── Multiple Parallel Mediators (X -> M1, M2 -> Y):
    │   │   └── USE: PROCESS Model 4 Parallel (compares specific indirect effects)
    │   └── Sequential / Serial Cascade (X -> M1 -> M2 -> Y):
    │       └── USE: PROCESS Model 6 (Serial Mediation)
    └── Evaluation & Decision Rules:
        ├── 5,000 BCa Bootstrap 95% Confidence Interval for indirect effect (a * b):
        │   ├── 95% CI excludes 0 (e.g. [.082, .341]): Indirect effect SIGNIFICANT
        │   └── 95% CI includes 0 (e.g. [-.041, .215]): Indirect effect NOT SIGNIFICANT
        └── Direct Effect (c') Status:
            ├── Indirect Sig & c' Not Sig (p >= .05): Full Mediation (میانجی‌گری کامل)
            ├── Indirect Sig & c' Sig (p < .05): Partial Mediation (میانجی‌گری جزئی)
            └── Indirect Not Sig: No Mediation
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/mediation/scripts/run_mediation.py \
  --data path/to/cleaned_data.xlsx \
  --iv mindfulness \
  --mediator psych_flexibility \
  --dv burnout \
  --bootstrap 5000 \
  --ci 95 \
  --output path/to/07_mediation_hypothesis.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`XX_mediation.json`**:
   - `path_a`: `{"coeff": ..., "se": ..., "t": ..., "p": ..., "r2": ...}`
   - `path_b`: `{"coeff": ..., "se": ..., "t": ..., "p": ...}`
   - `path_c_prime`: `{"coeff": ..., "se": ..., "t": ..., "p": ...}` (Direct effect)
   - `path_c`: `{"coeff": ..., "se": ..., "t": ..., "p": ...}` (Total effect)
   - `indirect_effect`: `{"point_estimate": ..., "boot_se": ..., "boot_ci_lower": ..., "boot_ci_upper": ..., "significant": true}`
   - `effect_size`: Ratio of indirect-to-total effect ($P_M = (a \times b) / c$) and completely standardized indirect effect ($\beta_{\text{ind}}$).
2. **APA 7 OpenXML Word Table**: 3-line regression decomposition table formatted with *B Nazanin* / *B Titr*, reporting paths $a, b, c, c'$, and bootstrap intervals.

---

## 8. Validation & Forensic Sanity Checks
- **Bootstrap Non-Zero Invariant**: $95\%$ CI must be derived from 5,000 resamples; verifying that `boot_ci_lower` and `boot_ci_upper` do not span zero.
- **Arithmetic Identity Check**: Total effect must equal direct plus indirect: $c = c' + (a \times b)$ (in linear OLS).
- **Prohibition of $p = .000$**: Report strictly as $p < .001$ in English or $p < ۰.۰۰۱$ in Persian.

