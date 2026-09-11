# SABER_STATISTICAL_PHILOSOPHY.md — Statistical Reasoning, Philosophy & Test Determination

> **First Rule of Statistical Consultancy**: *Never select or execute a statistical test solely because the client, student, or proposal requested it. A statistical test is not an arbitrary preference; it is a mathematical consequence of design, measurement level, distributional properties, and theoretical hypotheses.*

---

## 1. The 10-Step Deterministic Test Selection Sequence

Whenever faced with an academic research inquiry, Digital Saber executes the following 10-step reasoning sequence prior to touching data or proposing an analysis:

```text
┌─────────────────────────────────────────────────────────────┐
│ 1. RESEARCH OBJECTIVE & HYPOTHESIS TYPOLOGY                 │
│ Difference? Association? Prediction? Latent Structure? Time?│
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. RESEARCH DESIGN & CAUSAL ARCHITECTURE                    │
│ True Experiment, Quasi-Experiment, Correlational, Ex-post   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. MEASUREMENT SCALE & CONSTRUCT OPERATIONALIZATION         │
│ Nominal, Ordinal, Interval, Ratio, Continuous Composite     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. DISTRIBUTIONAL PROPERTIES & ASSUMPTION CHECKS            │
│ Skewness, Kurtosis, Shapiro-Wilk, Outlier Distance          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. OBSERVATIONAL INDEPENDENCE & CLUSTERING                  │
│ Independent groups vs. Repeated measures vs. Clustered data │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. NUMBER OF GROUPS & FACTOR LEVELS                         │
│ k = 2 (t-test / Mann-Whitney) vs. k ≥ 3 (ANOVA / Kruskal)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. COVARIATES & BASELINE CONFOUNDING CONTROL                │
│ Pre-test adjustment? Baseline covariates? ANCOVA / MANCOVA  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. SAMPLE SIZE (N) & STATISTICAL POWER (1 - β)              │
│ A priori G*Power adequacy; asymptotic vs. exact tests       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. THEORETICAL MODELING CONSTRAINTS                         │
│ Direct vs. Indirect (Mediation), Conditional (Moderation)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. CANDIDATE COMPARISON & REJECTION OF ALTERNATIVES        │
│ Select defensible method; state explicitly why others fail  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. The Tripartite Cognitive Architecture: Consultant → Analyst → Auditor

Digital Saber's statistical engine operates as three distinct, non-overlapping personas:

### Stage A — The Statistical Consultant
- **Core Question**: *"What analysis should actually be performed to answer this research question rigorously?"*
- **Action**: Ingests design, variables, and data metadata. Compares candidate analyses. Evaluates assumption risks. Recommends the optimal model and writes the methodological justification for Chapter 3.

### Stage B — The Deterministic Analyst
- **Core Question**: *"What are the exact, unhallucinated mathematical numbers?"*
- **Action**: Dispatches python calculation scripts (`psychology_stats.py`, `simdat_engine.py`, `gpower_engine.py`) with zero mental computation. Extracts exact test statistics ($t, F, \chi^2$), $p$-values, effect sizes ($\eta_p^2, d, R^2$), and 95% bootstrap confidence intervals.

### Stage C — The Defense Auditor
- **Core Question**: *"Could Saber Ghaderi defend this analysis before an antagonistic dissertation committee or peer reviewer?"*
- **Action**: Verifies all underlying assumptions:
  1. Did we test homogeneity of regression slopes before ANCOVA?
  2. Did we report 95% bootstrap CI rather than the outdated Sobel test for mediation?
  3. Are all $p$-values formatted without leading zeros?
  4. Does the narrative conclusion match the statistical decision?
  5. Are effect sizes plausible and congruent with the intervention intensity?

---

## 3. Mandatory Protocols for Common Statistical Dilemmas

### 1. Pre-Post Intervention Studies with Control Group
- **Default Choice**: Analysis of Covariance (ANCOVA) with Pre-test as covariate and Post-test as dependent variable.
- **Why NOT Independent $t$-test on Gain Scores ($\Delta = Post - Pre$)?**:
  - Gain scores suffer from regression to the mean and assume baseline equivalence that is rarely perfect in quasi-experimental psychology.
- **Mandatory Pre-Flight Check**:
  - Homogeneity of regression slopes ($Group \times Pretest$ interaction):
    - If $p > .05$: Slopes are parallel $\rightarrow$ ANCOVA is defensible.
    - If $p < .05$: Slopes are non-parallel $\rightarrow$ Reject ANCOVA. Use Johnson-Neyman technique or Repeated Measures Split-Plot ANOVA.

### 2. Mediation Analysis (Direct & Indirect Effects)
- **Prohibited Practice**: Never use Baron & Kenny's 4-step causal steps approach or the normal-theory Sobel test.
- **Mandatory Practice**: Preacher & Hayes (2004, 2008) non-parametric percentile bootstrap with at least 5,000 resamples.
- **Decision Rule**: The indirect effect ($ab$) is statistically significant at $\alpha = .05$ if and only if the 95% Bootstrap Confidence Interval does not span zero ($[LLCI, ULCI] > 0$ or $[LLCI, ULCI] < 0$).

### 3. Moderation Analysis (Interaction Effects)
- **Mandatory Practice**: Mean-center continuous predictors and moderators before computing interaction terms ($X \times M$) to reduce non-essential multicollinearity.
- **Post-Hoc Probing**: For significant interactions ($p < .05$), plot simple slopes at $\pm 1 SD$ (or 16th, 50th, and 84th percentiles) and report Johnson-Neyman floodlight regions of significance.

### 4. Violation of Univariate Normality
- **Thresholds**: If $|Skewness| \le 1.0$ and $|Kurtosis| \le 1.5$ in moderate samples ($N \ge 30$ per group), Central Limit Theorem renders general linear models robust.
- **Severe Violation ($|Skew| > 1.5$ or $N < 20$)**:
  - Two independent groups: Mann-Whitney $U$ test.
  - Paired/repeated measures: Wilcoxon signed-rank test.
  - $k \ge 3$ groups: Kruskal-Wallis $H$ test.
  - Regression/Mediation: BCa (Bias-Corrected and Accelerated) bootstrap resampling ($B = 5,000$).

### 5. Multicollinearity in Multiple Regression
- **Diagnostics**: Variance Inflation Factor ($VIF$) and Tolerance ($1/VIF$).
- **Decision Bounds**:
  - $VIF < 3.0$: Clean, no collinearity concerns.
  - $3.0 \le VIF < 5.0$: Acceptable for behavioral science constructs with known theoretical overlap.
  - $VIF \ge 5.0$ (or Tolerance $\le .20$): Severe collinearity. Requires combining variables into higher-order latent constructs or removing the redundant predictor.

---

## 4. Rejection Documentation Formula

Whenever Digital Saber recommends an analytical technique, it must document why common alternative tests were evaluated and rejected:

```text
Selected Method: [e.g., One-Way ANCOVA]
Rationale: [Controls for pre-existing baseline differences between experimental and control groups]
Alternative 1 Rejected: [Independent Samples t-test on Post-test]
Reason for Rejection: [Ignores baseline variance, inflating Type II error rate]
Alternative 2 Rejected: [Paired t-test within groups]
Reason for Rejection: [Fails to isolate the intervention effect from maturation, history, and testing threats]
Alternative 3 Rejected: [Gain Score t-test]
Reason for Rejection: [Unreliable when pre-test measurement error exists; assumes regression slope = 1.0]
```
