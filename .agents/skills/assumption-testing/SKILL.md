---
name: assumption-testing
description: Verify parametric assumptions: Shapiro-Wilk normality, Levene's test for equality of variance, regression slope homogeneity, Mauchly's sphericity, and collinearity VIF/Tolerance.
---

# Assumption Testing Skill (آزمون مفروضه‌های پارامتریک)

Executes the formal 10-step parametric assumption sequence:
- Univariate normality (Shapiro-Wilk + Skewness/Kurtosis)
- Homogeneity of variance (Levene's test)
- Homogeneity of regression slopes ($Group \times Covariate$)
- Multicollinearity (VIF and Tolerance)

## CLI Execution
```bash
python3 .agents/skills/assumption-testing/scripts/verify_assumptions.py --data data_cleaned.xlsx --dv post_score --group treatment_group --covariate pre_score --output 03_parametric_assumptions.json
```

