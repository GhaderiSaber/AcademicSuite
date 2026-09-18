---
name: assumption-testing
description: "Verify parametric assumptions: Shapiro-Wilk normality, Levene's test for equality of variance, regression slope homogeneity, Mauchly's sphericity, and collinearity VIF/Tolerance."
---

# Assumption Testing Skill (آزمون مفروضه‌های آماری و اعتبارسنجی مدل)

Executes rigorous verification of mathematical and parametric assumptions prior to hypothesis testing, ensuring that statistical inferences satisfy foundational model requirements and preventing methodological invalidation.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Pre-Flight Hypothesis Testing (Stage 03)**: Before running $t$-tests, ANOVA, ANCOVA, regression, mediation, or SEM, verifying that the empirical distribution satisfies parametric criteria.
2. **One-Way ANCOVA Verification**: Testing the critical non-negotiable assumption of **Homogeneity of Regression Slopes** ($Group \times Pretest$ interaction, $p > .05$).
3. **Repeated-Measures ANOVA**: Evaluating Mauchly's test of sphericity and estimating Greenhouse-Geisser ($\epsilon$) corrections.
4. **Multiple Regression Collinearity Diagnostics**: Calculating Variance Inflation Factor ($\text{VIF} < 5.0$) and Tolerance ($> 0.20$).

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Over-Relying on Formal Normality Tests with Large Samples ($N > 300$)**: Kolmogorov-Smirnov and Shapiro-Wilk tests become hyper-sensitive to trivial deviations at large $N$ ($p < .05$ even when skewness is near zero). In large samples ($N \ge 200$), rely on **Kline (2023) empirical distribution thresholds** ($|\text{Skewness}| < 2.0$ and $|\text{Kurtosis}| < 7.0$) and visual Q-Q plots.
2. **Ignoring Homogeneity of Slopes in ANCOVA**: Never proceed with standard ANCOVA if slope homogeneity is violated ($p \le .05$); this invalidates the baseline adjustment.
3. **Automated Replacement of Parametric Tests without Residual Inspection**: Mild violations of normality do not mandate switching to non-parametric tests when Central Limit Theorem applies ($N \ge 30$ per group) and F-tests are robust.

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Dependent continuous outcome (`--dv`), grouping factor (`--group`), and optional covariate (`--covariate`) or predictor list (`--ivs`).
- **CLI Parameters**:
  - `--dv`: Outcome variable.
  - `--group`: Categorical grouping variable.
  - `--covariate`: Continuous baseline covariate (for ANCOVA).
  - `--ivs`: Comma-separated list of predictors (for collinearity).

---

## 4. Methodological & Statistical Assumptions
1. **Univariate Normality**: Residuals or distributions within each group follow Gaussian distribution.
2. **Homogeneity of Variances**: Error variance of dependent outcome is equal across groups (Levene's test $p > .05$).
3. **Homogeneity of Regression Slopes**: The slope of the relationship between covariate and DV is equivalent across experimental conditions ($F_{\text{interaction}}, p > .05$).
4. **Sphericity (Repeated Measures)**: Variances of the differences between all possible pairs of within-subject conditions are equal (Mauchly's $W, p > .05$).
5. **Absence of Multicollinearity**: Predictors must not correlate too highly ($r < .85, \text{VIF} < 5.0$).

---

## 5. Method-Selection Decision Tree
```text
Target Parametric Test:
├── Group Comparisons (t-test / One-Way ANOVA):
│   ├── Normality: Shapiro-Wilk (N < 200) or Kline Skew < 2, Kurt < 7 (N >= 200)
│   │   ├── Satisfied: Parametric test (Student t / ANOVA)
│   │   └── Violated & Small N: Non-parametric (Mann-Whitney U / Kruskal-Wallis)
│   └── Homogeneity of Variance (Levene test):
│       ├── p > .05: Standard equal-variances pooled t-test / ANOVA
│       └── p <= .05: Welch's t-test / Welch's ANOVA (Games-Howell post-hoc)
├── One-Way ANCOVA (Intervention Trial with Pre-test):
│   ├── Step 1: Pre-test/Post-test Correlation: r >= .30 (justifies covariate)
│   ├── Step 2: Levene's Test: p > .05
│   └── Step 3: Homogeneity of Slopes (Group * Pretest Interaction):
│       ├── p > .05: Proceed with One-Way ANCOVA
│       └── p <= .05: VIOLATION. Use Johnson-Neyman technique or moderation
├── Repeated-Measures ANOVA:
│   └── Mauchly's Sphericity Test:
│       ├── p > .05: Sphericity assumed
│       └── p <= .05: Violated. Apply epsilon correction:
│           ├── Greenhouse-Geisser if epsilon < .75
│           └── Huynh-Feldt if epsilon >= .75
└── Multiple Regression:
    ├── Independence: Durbin-Watson between 1.50 and 2.50
    ├── Collinearity: Tolerance >= .20, VIF <= 5.00
    └── Homoscedasticity: Breusch-Pagan p > .05
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/assumption-testing/scripts/verify_assumptions.py \
  --data path/to/cleaned_data.xlsx \
  --dv post_score \
  --group treatment_group \
  --covariate pre_score \
  --output path/to/03_parametric_assumptions.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`03_parametric_assumptions.json`**:
   - `normality`: `{"statistic": ..., "p": ..., "skewness": ..., "kurtosis": ..., "status": "PASS"}`
   - `homogeneity_of_variance`: `{"levene_f": ..., "p": ..., "status": "PASS"}`
   - `homogeneity_of_slopes`: `{"f_interaction": ..., "df1": ..., "df2": ..., "p": ..., "status": "PASS"}`
   - `multicollinearity`: List of `{"variable": ..., "tolerance": ..., "vif": ...}`
2. **APA 7 OpenXML Word Table**: 3-line institutional summary table reporting test statistics, degrees of freedom, $p$-values, and explicit compliance status.

---

## 8. Validation & Forensic Sanity Checks
- **Binary Decision Gate**: If any non-negotiable assumption fails (e.g. slope homogeneity $p \le .05$ in ANCOVA), the pipeline halts and surfaces the failure to the Academic Challenger and Pitfall Registry.
- **Reporting Invariant**: Never state an assumption was checked unless the mathematical command and test statistic physically exist in workspace logs.

