# G*Power Mathematical Power Standards & Sample Size Guidelines

This document serves as the theoretical and mathematical foundation for **`gpower-sample-size-calculator`** (Skill #21) in the AcademicSuite, adhering strictly to Cohen's (1988) statistical power framework and Faul, Erdfelder, Lang, & Buchner's (2007, 2009) G*Power algorithms.

---

## 1. Fundamentals of Statistical Power Analysis

In statistical hypothesis testing, four interrelated parameters form a closed mathematical system:

$$\text{Significance Criterion } (\alpha) \quad \longleftrightarrow \quad \text{Statistical Power } (1 - \beta) \quad \longleftrightarrow \quad \text{Sample Size } (N) \quad \longleftrightarrow \quad \text{Effect Size } (ES)$$

Given any three parameters, the fourth is deterministically computed.

### Definitions
1. **Type I Error ($\alpha$)**: Probability of falsely rejecting a true null hypothesis (False Positive). Standard academic threshold: $\alpha = .05$.
2. **Type II Error ($\beta$)**: Probability of failing to reject a false null hypothesis (False Negative).
3. **Statistical Power ($1 - \beta$)**: Probability of correctly rejecting a false null hypothesis. Standard thresholds: $.80$ (Cohen's convention), $.90$, or $.95$ for high-stakes clinical interventions.
4. **Effect Size (ES)**: Quantitative measure of the magnitude of an experimental intervention or the strength of an association in the population.

---

## 2. Cohen's Effect Size Benchmarks for Psychological Research

| Test Family | Statistical Test | Effect Size Metric | Small | Medium | Large | Formula / Definition |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **$t$-Tests** | Independent Samples | $d$ | $0.20$ | $0.50$ | $0.80$ | $d = \frac{\mu_1 - \mu_2}{\sigma_{\text{pooled}}}$ |
| **$t$-Tests** | Paired Samples | $d_z$ | $0.20$ | $0.50$ | $0.80$ | $d_z = \frac{\mu_D}{\sigma_D} = \frac{d}{\sqrt{2(1-r)}}$ |
| **$F$-Tests** | One-Way ANOVA | $f$ | $0.10$ | $0.25$ | $0.40$ | $f = \frac{\sigma_m}{\sigma} = \sqrt{\frac{\eta^2}{1 - \eta^2}}$ |
| **$F$-Tests** | ANCOVA | $f$ | $0.10$ | $0.25$ | $0.40$ | Adjusted variance ratio controlling for $c$ covariates |
| **$F$-Tests** | Repeated Measures | $f$ | $0.10$ | $0.25$ | $0.40$ | Adjusted by correlation $r$ among repeated measures |
| **$F$-Tests** | Multiple Regression | $f^2$ | $0.02$ | $0.15$ | $0.35$ | $f^2 = \frac{R^2}{1 - R^2}$ |
| **$t$-Tests** | Correlation | $r$ | $0.10$ | $0.30$ | $0.50$ | Pearson product-moment correlation |

---

## 3. Mathematical Formulations by Test Family

### 3.1 Independent Samples $t$-Test
- **Allocation Ratio**: $\kappa = \frac{n_2}{n_1}$ (typically $\kappa = 1.0$ for equal groups).
- **Non-Centrality Parameter ($\delta$)**:
  $$\delta = d \sqrt{\frac{n_1 n_2}{n_1 + n_2}} = d \sqrt{\frac{N \kappa}{(1 + \kappa)^2}}$$
- **Degrees of Freedom**: $df = n_1 + n_2 - 2 = N - 2$.
- **Critical Value**: $t_{\text{crit}} = t_{1 - \alpha/2, df}$ (for two-tailed).
- **Statistical Power**:
  $$1 - \beta = 1 - F_{t(\delta, df)}(t_{\text{crit}}) + F_{t(\delta, df)}(-t_{\text{crit}})$$
  where $F_{t(\delta, df)}$ is the cumulative distribution function of the non-central $t$-distribution.

### 3.2 One-Way Analysis of Variance (ANOVA) & ANCOVA
- **Non-Centrality Parameter ($\lambda$)**:
  $$\lambda = f^2 \times N$$
- **Degrees of Freedom**:
  - ANOVA: $df_1 = k - 1$ (between), $df_2 = N - k$ (within/error).
  - ANCOVA: $df_1 = k - 1$ (between), $df_2 = N - k - c$ (error, where $c$ is the number of covariates).
- **Critical Value**: $F_{\text{crit}} = F_{1 - \alpha, df_1, df_2}$.
- **Statistical Power**:
  $$1 - \beta = 1 - F_{F(\lambda, df_1, df_2)}(F_{\text{crit}})$$
  where $F_{F(\lambda, df_1, df_2)}$ is the cumulative distribution function of the non-central $F$-distribution.

### 3.3 Multiple Linear Regression (Fixed Model, $R^2$ from Zero)
- For $k$ predictor variables and total sample size $N$:
- **Effect Size Metric**: $f^2 = \frac{R^2}{1 - R^2}$.
- **Non-Centrality Parameter ($\lambda$)**:
  $$\lambda = f^2 \times N$$
- **Degrees of Freedom**: $df_1 = k$, $df_2 = N - k - 1$.
- **Critical Value**: $F_{\text{crit}} = F_{1 - \alpha, df_1, df_2}$.
- **Power**: Evaluated via non-central $F$-distribution: $1 - F_{F(\lambda, k, N-k-1)}(F_{\text{crit}})$.

### 3.4 Repeated Measures ANOVA (Between-Within Interaction)
- For $k$ groups, $m$ repeated measurements, and average inter-correlation $r$:
- **Adjusted Effect Size**:
  $$f_{\text{adj}} = \frac{f}{\sqrt{1 - r}}$$
- **Degrees of Freedom**:
  $$df_1 = (k - 1)(m - 1)$$
  $$df_2 = (N - k)(m - 1)$$
- Sphericity correction ($\epsilon$): Greenhouse-Geisser adjustment applied if $\epsilon < 0.75$.

---

## 4. Structural Equation Modeling (SEM) Sample Size Rules

For Master's and Doctoral dissertations utilizing SEM or Confirmatory Factor Analysis (CFA):

1. **Westland's (2010) Minimum Sample Size Formula**:
   $$N \ge 50 \times \left( \frac{j}{k} \right)^2 - 450 \times \left( \frac{j}{k} \right) + 1100$$
   where $j$ is the number of observed indicator variables, and $k$ is the number of unobserved latent variables.
2. **Bentler & Chou (1987) Ratio Rule**:
   - Minimum: **5 cases per estimated parameter** ($5:1$).
   - Recommended: **10 cases per estimated parameter** ($10:1$).
3. **Kline (2015) Absolute Lower Bound Rule**:
   - $N < 100$: Unacceptable for SEM estimation.
   - $N = 100 - 200$: Acceptable for small models with high factor loadings ($\lambda > 0.70$).
   - $N > 200$: Standard academic consensus threshold for SEM defense.

---

## 5. Three Analysis Modalities

1. **A Priori Power Analysis (تحلیل توان پیشینی)**:
   - *Timing*: Conducted before data collection (during Proposal / Chapter 3 drafting).
   - *Inputs*: Target $\alpha$, target power $1 - \beta$, expected effect size.
   - *Output*: Minimum required sample size $N$.
2. **Post Hoc Power Analysis (تحلیل توان پسینی)**:
   - *Timing*: Conducted after data collection (during Chapter 4 data analysis).
   - *Inputs*: Actual sample size $N$, $\alpha$, observed effect size.
   - *Output*: Achieved statistical power ($1 - \beta$).
3. **Sensitivity Analysis (تحلیل حساسیت)**:
   - *Timing*: Pre-defense or during defense preparation.
   - *Inputs*: Fixed available sample size $N$, $\alpha$, desired power ($0.80$).
   - *Output*: Minimum detectable population effect size ($ES_{\text{min}}$).
