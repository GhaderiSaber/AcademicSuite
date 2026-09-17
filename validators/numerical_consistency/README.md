# Numerical Consistency Validator

Validates numerical accuracy and psychometric mathematical bounds:
- Degrees of freedom concordance: $df_{\text{error}} == N - k - 1$.
- Variance deflation check: $SD \ge 0.10 \times \text{Range}$ (detects synthetic variance compression).
- Correlation bounds check ($-1.0 \le r \le +1.0$).
- Multi-Signal Anomaly Index (MSAI) computation.

## Verdicts
- `PASS`: All degrees of freedom match sample dimensions; effect sizes plausible; variance natural.
- `NEEDS_REVIEW`: Implausibly massive effect size ($d > 1.80, \eta_p^2 > .45$) or border variance deflation.
- `FAIL`: Degrees of freedom mismatch, correlation out of bounds, or synthetic zero variance.
