# Data Audit Guidelines & Thresholds

## 1. Missingness Diagnostics
- **Little's MCAR Test**:
  - $p > .05$: Missing Completely at Random. Expectation-Maximization (EM) or Multiple Imputation (MI) is permissible.
  - $p \le .05$: Missing at Random (MAR) or MNAR. Listwise deletion or Full Information Maximum Likelihood (FIML) required.
- **Threshold**: Item missingness $> 15\%$ on core outcome variables warrants participant exclusion.

## 2. Unengaged Responses (Straight-Lining)
- Standard deviation across psychometric battery $SD \le 0.15$ indicates unengaged responding.
- Flag participant IDs with zero response variance.

## 3. Multivariate Outlier Detection
- Compute Mahalanobis Distance ($D^2$) across continuous psychological variables.
- Evaluate against $\chi^2(df)$ at $lpha = .001$.
- Exclude confirmed outliers and record participant IDs in the curation audit log.
