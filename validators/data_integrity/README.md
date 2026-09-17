# Data Integrity Validator

Evaluates dataset quality and curation integrity:
- Missingness rate threshold checks (< 5% for imputation; > 15% requires exclusion).
- Zero-variance unengaged response detection (straight-lining).
- Multivariate outlier verification (Mahalanobis $D^2, p < .001$).
- Little's MCAR test interpretation check.

## Verdicts
- `PASS`: Dataset is clean, zero unengaged responses, missingness < 5% or MCAR confirmed.
- `NEEDS_REVIEW`: High missingness (> 10%) or undocumented potential outliers.
- `FAIL`: Zero-variance straight-lining detected, or unaddressed MNAR missingness.
