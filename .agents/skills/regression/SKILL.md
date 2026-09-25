---
name: regression
description: Execute standard, hierarchical, and stepwise multiple regression modeling, evaluating R2, delta R2, F-change, standardized beta, and collinearity diagnostics.
---

# Multiple & Hierarchical Regression Skill (تحلیل رگرسیون چندگانه و سلسله‌مراتبی)

Executes ordinary least squares (OLS) multiple and hierarchical linear regression, evaluating the 4-Tier Saber Regression Sequence, variance explained ($R^2$), incremental contribution ($\Delta R^2, F_{\text{change}}$), standardized parameters ($\beta$), and collinearity diagnostics (VIF & Tolerance).

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Predicting Continuous Dependent Variable**: Modeling the linear relationship between two or more independent predictors ($X_1, X_2, \dots, X_k$) and a continuous criterion variable ($Y$).
2. **Evaluating Incremental Variance Explained (Hierarchical Blockwise Entry)**: Determining whether a theoretical set of psychological predictors explains significant incremental variance above and beyond demographic baseline covariates (Block 1: Demographics $\to$ Block 2: Psychological constructs, testing $\Delta R^2$ and $F_{\text{change}}$).
3. **Comparing Relative Predictive Power**: Evaluating standardized regression coefficients ($\beta$) to determine which independent variables are the strongest unique contributors.
4. **Stepwise Exploratory Selection**: Identifying the most parsimonious subset of empirical predictors in exploratory research.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Categorical / Binary Outcome Variable**: If $Y$ is binary (0/1), OLS violates homoscedasticity and bounds $[0, 1]$; use Binary Logistic Regression.
2. **Severe Multicollinearity ($\text{VIF} > 5.0$ or $\text{Tolerance} < 0.20$)**: High collinearity inflates standard errors and causes coefficient sign inversions. Prune redundant predictors or combine into composite index.
3. **Repeated Longitudinal Measures from Same Subjects**: OLS assumes independent observations. If observations are clustered or repeated over time, use Linear Mixed Models (`statistical-data-analyst` or `longitudinal-moderated-mediation`).
4. **Severe Heteroscedasticity or Non-Normality of Residuals**: If Breusch-Pagan test indicates severe heteroscedasticity, use Robust Standard Errors (HC3) or Weighted Least Squares (WLS).

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Continuous or dummy-coded (0/1) independent variables ($X_1 \dots X_k$) and continuous dependent outcome ($Y$).
- **Minimum Sample Size**: Green's rule: $N \ge 50 + 8k$ for testing $R^2$, and $N \ge 104 + k$ for testing individual predictors $\beta$ (e.g. For $k = 4$, minimum $N = 108$).
- **Input CLI Parameters**:
  - `--dv`: Dependent variable column name.
  - `--ivs`: Comma-separated list of predictors (e.g. `"coping,resilience,social_support"`).
  - `--blocks`: (Optional) Blockwise hierarchical entry specification (e.g. `"age,gender|coping,resilience"`).

---

## 4. Methodological & Statistical Assumptions
1. **Linearity**: Evaluated via bivariate scatterplots and residual plots.
2. **Independence of Residuals**: Durbin-Watson statistic must fall between $1.50$ and $2.50$ (indicating zero first-order autocorrelation).
3. **Homoscedasticity**: Equal variance of residuals across levels of predicted values (Breusch-Pagan $p > .05$).
4. **Normality of Residuals**: Visual inspection of standardized residual histogram (normal bell curve overlay) and Normal P-P plot.
5. **Absence of Multicollinearity**: Tolerance $> 0.20$ and $\text{VIF} < 5.0$ for every predictor.

---

## 5. Method-Selection Decision Tree
```text
Regression Method Selection:
├── Purpose of Analysis:
│   ├── Controlling for Demographics / Testing Incremental Variance:
│   │   └── USE: Hierarchical Blockwise Regression (رگرسیون سلسله‌مراتبی)
│   │       ├── Block 1: Control Covariates (Age, Gender, Education) -> R1^2
│   │       └── Block 2: Focal Psychological Predictors -> R2^2, Delta R^2, F_change
│   ├── Testing Simultaneous Contribution of all Hypothesized Predictors:
│   │   └── USE: Simultaneous / Standard Multiple Regression (Enter Method)
│   └── Exploratory Reduction of Large Candidate Predictor Pool:
│       └── USE: Stepwise Regression (گام‌به‌گام) with probability-of-F-to-enter <= .05
└── Assumption Diagnostics Checklist:
    ├── Durbin-Watson: 1.50 <= DW <= 2.50
    ├── Collinearity: Tolerance >= .20, VIF <= 5.00
    └── Residuals: Normal P-P plot points hug 45-degree diagonal line
```

---

## 6. Execution Script ("The Hands")
```bash
# Standard Simultaneous Multiple Regression
python3 .agents/skills/regression/scripts/run_regression.py \
  --data path/to/cleaned_data.xlsx \
  --dv burnout \
  --ivs "workload,emotional_labor,autonomy" \
  --output path/to/06_regression_results.json

# Hierarchical Regression with Covariate Blocks
python3 .agents/skills/regression/scripts/run_regression.py \
  --data path/to/cleaned_data.xlsx \
  --dv burnout \
  --blocks "age,experience|workload,autonomy" \
  --output path/to/06_hierarchical_results.json
```

---

## 7. Output Contract & Artifacts
The script produces the **4-Tier Saber Regression Sequence**:
1. **`06_regression_results.json`**:
   - `model_summary`: $R, R^2, \text{Adj } R^2, SE_{\text{est}}, F(df_1, df_2), p, \text{Durbin-Watson}$.
   - `hierarchical_summary`: $\Delta R^2, F_{\text{change}}, p_{\Delta F}$.
   - `coefficients`: List of predictors with $B, SE, \beta, t, p, \text{Tolerance}, \text{VIF}$.
2. **APA 7 OpenXML Word Table**:
   - Combined ANOVA & Model Summary 11-column table.
   - Multiple Regression Coefficients table with Persian labels and decoupled LTR statistics.
3. **Diagnostic Graphics**: 300-DPI Normal Residual Histogram and Normal P-P plot.

---

## 8. Validation & Forensic Sanity Checks
- **Degrees of Freedom Sanity Check**: Regression $df_{\text{reg}} = k$; Residual $df_{\text{res}} = N - k - 1$; Total $df_{\text{total}} = N - 1$.
- **$R^2$ Upper Bound**: $0.0 \le R^2 \le 1.0$. Adjusted $R^2 \le R^2$.
- **Collinearity Flag**: Any predictor with $\text{VIF} > 5.0$ must be flagged for multi-signal anomaly review.

---

## 9. INSTITUTIONAL INVARIANTS & PREVIOUS LESSONS GRADUATED

### 9.1 Canonical 3-Table Regression Standard
Every regression hypothesis must be reported via exactly three separate tables:
1. **Table 1: Bivariate Correlation Matrix**: Pearson correlations among predictors and criterion, with Col 1 (`ردیف`), Col 2 (`متغیر`), Col 3 (`مؤلفه`).
2. **Table 2: Model Summary & ANOVA Table (11 Columns)**: Combined model fit and variance analysis ($SS, df, MS, F, p, R, R^2, \text{Adj } R^2, SE_{\text{est}}, DW$).
3. **Table 3: Regression Coefficients & Collinearity (8 Columns)**: Parameter estimates and diagnostic indices (Predictor, $B, SE, \beta, t, p$, Tolerance, VIF).

### 9.2 Regression ANOVA Option A Standard
In regression ANOVA tables with multiple criterion variables:
- **Column 1**: `متغیر ملاک` (Criterion construct name).
- **Column 2**: `منبع تغییرات` (Strictly `رگرسیون`, `باقیمانده`, `کل`).
- **Row Labels**: Regression rows are labeled with the dependent variable name. Residual and total rows must be labeled simply as `باقیمانده` and `کل`. Never append parenthetical variable names to residual or total rows.
- **Multiple Criteria Coefficients**: When reporting multiple criteria in a single coefficients table, Column 1 must specify `متغیر ملاک`.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-THREE-TABLE-REGRESSION-STANDARD-001)**: Strictly enforce the 3-Table Standard for all regression model reporting across JSON schemas, markdown narratives, and DOCX tables. [Enforcement: statistics_agent_guard.py]