# Parametric Assumption Verification Sequence

## 1. Normality (Shapiro-Wilk)
- $p > .05$: Distribution does not significantly depart from normality.
- In sample sizes $N > 100$, rely on Skewness/Kurtosis $[-0.85, +0.85]$.

## 2. Homogeneity of Variance (Levene)
- $p > .05$: Equal variances assumed across groups.
- If $p \le .05$: Apply Welch's ANOVA or robust standard errors.

## 3. Homogeneity of Regression Slopes (ANCOVA)
- Model: $DV = Group + Covariate + (Group \times Covariate)$.
- Interaction term must be non-significant ($p > .05$).
- If $p \le .05$: ANCOVA is invalid. Apply Johnson-Neyman moderation analysis.
