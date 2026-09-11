# SABER_DECISION_RULES.md — Explicit Heuristics & Methodological Trade-Offs

> **Decision Axiom**: *Expert research consultancy is characterized by principled decisions at methodological crossroads. When assumptions fail or trade-offs emerge, Digital Saber adheres to deterministic, mathematically sound decision paths.*

---

## 1. Univariate & Multivariate Normality Crossroads

```text
Check: Shapiro-Wilk / Kolmogorov-Smirnov & Skewness/Kurtosis
│
├── |Skewness| ≤ 1.0 AND |Kurtosis| ≤ 1.5 AND N ≥ 30 per group:
│   └── VERDICT: Parametric tests (ANOVA, Regression, ANCOVA) are robust under Central Limit Theorem.
│
├── |Skewness| > 1.5 OR |Kurtosis| > 2.0 OR N < 20 per group:
│   ├── Is it an independent group comparison (2 groups)?
│   │   └── VERDICT: Mann-Whitney U test.
│   ├── Is it paired/repeated data (2 conditions)?
│   │   └── VERDICT: Wilcoxon signed-rank test.
│   ├── Is it a k ≥ 3 group comparison?
│   │   └── VERDICT: Kruskal-Wallis H test (with Dunn-Bonferroni post-hoc).
│   └── Is it a regression or mediation model?
│       └── VERDICT: 5,000-sample BCa (Bias-Corrected and Accelerated) Bootstrap Resampling.
```

---

## 2. Homoscedasticity & Covariance Equality Crossroads

```text
Check: Levene's Test (F, p) for Homogeneity of Variances
│
├── p > .05:
│   └── VERDICT: Standard ANOVA / Student's independent t-test.
│
└── p ≤ .05 (Variances Unequal):
    ├── Two groups (k = 2):
    │   └── VERDICT: Welch's t-test (adjusts degrees of freedom).
    └── Three or more groups (k ≥ 3):
        ├── Balanced sample sizes (n1 ≈ n2 ≈ n3):
        │   └── VERDICT: Welch's F or Brown-Forsythe ANOVA (Games-Howell post-hoc).
        └── Unbalanced sample sizes (n1 ≠ n2):
            └── VERDICT: MANDATORY Welch's F + Games-Howell post-hoc.
```

```text
Check: Box's M Test for Equality of Covariance Matrices (MANOVA / RM-ANOVA)
│
├── p > .001 (Box's M is evaluated conservatively at α = .001):
│   └── VERDICT: Wilks' Lambda is robust.
│
└── p ≤ .001 (Covariance matrices differ significantly):
    └── VERDICT: Use Pillai's Trace (more robust to covariance heterogeneity) instead of Wilks' Lambda.
```

---

## 3. Repeated Measures Sphericity Crossroads

```text
Check: Mauchly's Test of Sphericity (W, p)
│
├── p > .05:
│   └── VERDICT: Sphericity assumed; report standard F and df.
│
└── p ≤ .05 (Sphericity Violated):
    ├── Greenhouse-Geisser ε < 0.75:
    │   └── VERDICT: Report Greenhouse-Geisser corrected F and fractional df.
    └── Greenhouse-Geisser ε ≥ 0.75:
        └── VERDICT: Report Huynh-Feldt corrected F and fractional df.
```

---

## 4. ANCOVA Regression Slope Parallelism Crossroads

```text
Check: Group × Covariate Interaction Effect (F, p)
│
├── p > .05:
│   └── VERDICT: Slopes are parallel. Proceed with standard ANCOVA.
│
└── p ≤ .05 (Slopes are Non-Parallel / Heterogeneous):
    ├── Option A (Defensible Modern):
    │   └── VERDICT: Johnson-Neyman technique to identify floodlight regions where intervention is effective.
    └── Option B (Standard Dissertation Fallback):
        └── VERDICT: Switch design to Repeated Measures Split-Plot ANOVA (2 Groups × 2 Times).
```

---

## 5. Latent Variable Modeling: Regression vs. Path Analysis vs. SEM

```text
Check: Number of Constructs, Observed Items vs. Latent Composites
│
├── Single manifest DV, multiple manifest IVs:
│   └── VERDICT: Multiple Linear Regression (Hierarchical if testing incremental validity).
│
├── Multiple DVs, mediating mechanisms, but all measured as observed composite scores:
│   └── VERDICT: Path Analysis (via lavaan in R or AMOS).
│
├── Complex multi-item constructs with measurement error modeled simultaneously:
│   ├── Sample size N ≥ 200 (or ≥ 10 participants per free parameter):
│   │   └── VERDICT: Full Structural Equation Modeling (SEM) (CFA measurement model + structural paths).
│   └── Sample size N < 150:
│       └── VERDICT: Path Analysis on composite scale scores (Full SEM will suffer convergence and power issues).
```

---

## 6. Outlier Diagnostics & Treatment

1. **Univariate Outliers**:
   - Standardized $z$-score $|z| > 3.29$ ($p < .001$).
   - Rule: Check for data entry errors. If genuine participant response, report results with and without outlier (sensitivity analysis).
2. **Multivariate Outliers**:
   - Mahalanobis Distance ($D^2$) evaluated against $\chi^2$ distribution ($df = k$ predictors, $\alpha = .001$).
   - Cook's Distance ($D_i > 1.0$) or Leverage points ($h_{ii} > \frac{2(k+1)}{N}$).
   - Rule: Exclude cases exceeding critical Mahalanobis threshold only with explicit documentation in Chapter 4 methodology.

---

## 7. Supervisor Discrepancy & Academic Diplomacy Protocol

When a supervisor insists on an outdated or flawed procedure:
1. **Never confrontational**: Never advise the student to argue with the supervisor.
2. **The Dual Delivery**:
   - Primary Chapter Section: Formatted with the supervisor's preferred method (e.g. Pearson or Sobel).
   - Methodological Footnote & Appendix: Robust modern alternative (e.g. Bootstrap CI or Spearman) accompanied by authoritative APA 7 / psychometric literature citations (e.g., Hayes, 2018; Kline, 2023; Tabachnick & Fidell, 2019).
