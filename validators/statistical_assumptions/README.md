# Statistical Assumptions Validator

Verifies compliance with the 10-step parametric assumption sequence:
- Univariate normality: Shapiro-Wilk $p > .05$ or Skewness $[-0.85, +0.85]$.
- Homogeneity of variance: Levene's test $p > .05$.
- Regression slope homogeneity: $Group \times Covariate$ interaction $p > .05$.
- Multicollinearity: VIF $< 5.0$, Tolerance $> .20$.

## Verdicts
- `PASS`: All parametric assumptions verified and met.
- `NEEDS_REVIEW`: Moderate skewness requiring non-parametric confirmation.
- `FAIL`: Violated Levene's test or slope interaction without documented statistical correction.
