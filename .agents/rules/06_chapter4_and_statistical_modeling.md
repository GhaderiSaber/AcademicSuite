---
trigger: model_decision
description: "Chapter 4 research findings reporting: 3-table APA 7 regression suite, SEM structural equation modeling, CFA measurement models, assumption verification, effect sizes."
---

# Chapter 4 & Statistical Modeling Specification (Directives 2, 4, 10)

Structural and reporting requirements for Chapter 4 research findings (یافته‌های پژوهش).

## 1. Canonical Chapter 4 Structure
1. **Preliminary Data Screening**:
   - Sample demographics ($n$, percentages).
   - Descriptive statistics ($M, SD$, Skewness, Kurtosis).
   - Normality verification (univariate via Shapiro-Wilk/z-scores, multivariate via Mardia's coefficient).
   - Missing data patterns and outlier diagnostics (Mahalanobis distance $D^2$).
2. **Measurement Model (CFA / Scale Validation)**:
   - Factor loadings ($\lambda \ge 0.40$ or $0.50$).
   - Construct reliability ($CR \ge 0.70$) and Cronbach's alpha ($\alpha \ge 0.70$).
   - Convergent validity ($AVE \ge 0.50$).
   - Discriminant validity (Fornell-Larcker criterion and HTMT $< 0.85$ or $0.90$).
3. **Hypothesis Testing & Structural Model (SEM / Regression)**:
   - Model fit indices ($\chi^2/df < 3$, $CFI \ge 0.90$, $TLI \ge 0.90$, $RMSEA \le 0.08$, $SRMR \le 0.08$).
   - Path coefficients ($\beta$), standard errors ($SE$), $t$-values, and $p$-values.
   - Indirect/mediation effects evaluated via bootstrap confidence intervals (e.g. 5,000 resamples).

## 2. Regression Reporting Suite (Mandatory 3 Tables)
When reporting multivariate regression hypotheses, provide the complete 3-table sequence:
1. **Table 1: Correlation Matrix**: Bivariate Pearson correlations ($r$), $p$-values, $M$, and $SD$ across all predictors and criterion variables.
2. **Table 2: Model Summary & Combined ANOVA (11 columns)**: Model, $R$, $R^2$, $\Delta R^2$, Adjusted $R^2$, $SE$, Regression/Residual/Total Sum of Squares ($SS$), degrees of freedom ($df$), Mean Square ($MS$), $F$-statistic, $p$-value.
3. **Table 3: Coefficients & Collinearity Diagnostics (8 columns)**: Variable, Unstandardized coefficients ($B, SE$), Standardized coefficient ($\beta$), $t$-statistic, $p$-value, Collinearity diagnostics (Tolerance, $VIF < 5$).

## 3. Epistemic Transparency
- Report assumption violations and non-significant results ($p > .05$) honestly and transparently. Never alter data or drop cases arbitrarily to force statistical significance.
