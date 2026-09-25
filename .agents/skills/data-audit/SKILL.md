---
name: data-audit
description: Audit raw dataset quality, screen unengaged responses (straight-lining), diagnose missingness patterns (Little's MCAR), and detect multivariate outliers (Mahalanobis D2).
---

# Data Audit & Quality Screening Skill (ارزیابی سلامت داده‌ها و غربالگری خطاهای اندازه‌گیری)

Executes forensic screening of raw psychological and behavioral datasets in Stage 4.0: diagnosing missing data mechanisms via Little's MCAR test, detecting unengaged respondents (straight-lining), identifying univariate ($z > \pm 3.29$) and multivariate outliers (Mahalanobis $D^2$), and certifying analysis-readiness.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Raw Dataset Ingestion (Stage 4.0)**: Prior to any statistical analysis, descriptives, or psychometric modeling, auditing raw `.xlsx`, `.csv`, or `.sav` files.
2. **Missing Data Diagnostics**: Evaluating whether missingness is Missing Completely at Random (MCAR), Missing at Random (MAR), or Missing Not at Random (MNAR).
3. **Unengaged Respondent Screening**: Screening for survey satisficing, zero-variance straight-lining, and completion speed anomalies.
4. **Multivariate Outlier Identification**: Screening for extreme multidimensional distance via Mahalanobis $D^2$ at $p < .001$.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Single Mean Imputation**: NEVER use single mean substitution for missing values. It artificially deflates sample variance, distorts covariance structures, and inflates Type I error rates.
2. **Automatic Deletion of Outliers without Inspection**: Never purge cases solely because $z > 3.0$ without verifying if the values represent valid extreme clinical phenotypes.
3. **Post-Aggregation Dataset**: Audit must be conducted on raw item-level responses, not on post-hoc aggregated composite scores.

---

## 3. Required Data & Input Contract
- **Input File**: Raw item-level dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Item columns from psychometric scales, participant ID, and demographic indicators.
- **Minimum Sample Size**: $N \ge 30$.
- **CLI Parameters**:
  - `--data`: Path to raw data file.
  - `--id-col`: Column name of subject identifier.
  - `--scales`: Comma-separated list of item blocks to screen for straight-lining.
  - `--output`: Path to `00_data_audit_report.json`.

---

## 4. Methodological & Statistical Assumptions
1. **Missing Data Taxonomy (Rubin, 1976)**:
   - **MCAR**: Missingness is completely independent of observed and unobserved data.
   - **MAR**: Missingness depends on observed covariates but not unobserved values.
   - **MNAR**: Missingness depends on the unobserved value itself (e.g. Severely depressed patients skipping depression items).
2. **Multivariate Normality of Incomplete Data**: Required for Little's MCAR test $\chi^2$ statistic validity.
3. **Mahalanobis Distance Distribution**: $D^2 \sim \chi^2(df = k)$, where $k$ is the number of evaluated continuous variables.

---

## 5. Method-Selection Decision Tree
```text
Missing Data Diagnostic & Remediation Flow:
├── Run Little's MCAR Test (p-value):
│   ├── p > .05: Data is Missing Completely at Random (MCAR)
│   │   ├── Overall Missing Rate < 5%:
│   │   │   └── Listwise deletion permissible if statistical power remains >= .80
│   │   └── Overall Missing Rate >= 5%:
│   │       └── USE: Multiple Imputation (MICE, m >= 20 iterations) or FIML
│   └── p <= .05: Data is Missing at Random (MAR) or MNAR
│       ├── Missing Rate 5% - 30%:
│       │   ├── Single Mean Imputation: STRICTLY PROHIBITED
│       │   └── USE: Multiple Imputation by Chained Equations (MICE) or FIML in SEM
│       └── Missing Rate > 30% on single item/scale:
│           └── Flag variable for exclusion or dedicated sensitivity analysis
└── Outlier Detection Flow:
    ├── Univariate Outliers: Standardized z-score |z| > 3.29 (p < .001)
    │   └── Flag for winsorization or clinical review
    └── Multivariate Outliers: Mahalanobis Distance D^2 > Chi2_critical(df=k, p < .001)
        ├── Discrepancy from straight-lining / response sets -> Purge case
        └── Valid extreme clinical score -> Retain and run sensitivity analysis
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/data-audit/scripts/audit_dataset.py \
  --data path/to/raw_data.xlsx \
  --id-col subject_id \
  --scales "burnout_items,mindfulness_items" \
  --output path/to/00_data_audit_report.json
```

---

## 7. Output Contract & Artifacts
The script outputs:
1. **`00_data_audit_report.json`**:
   - `total_cases`: Initial sample size $N_{\text{initial}}$.
   - `missingness`: `{"mcar_chi2": ..., "df": ..., "p": ..., "overall_percent": ..., "recommendation": "MICE"}`.
   - `unengaged_respondents`: List of case IDs with zero variance across Likert item blocks.
   - `multivariate_outliers`: List of case IDs exceeding Mahalanobis critical threshold at $p < .001$.
   - `retained_cases`: Recommended cleaned sample size $N_{\text{clean}}$.
2. **Audit Narrative & Tables**: Summary table reporting Little's MCAR test, number of screened cases, and justification.

---

## 8. Validation & Forensic Sanity Checks
- **Sample Retention Floor**: Purging unengaged cases and multivariate outliers must NOT reduce sample retention below $75\text{--}80\%$ of initial $N$.
- **Zero Imputed Whole-Numbers**: Imputed Likert values must maintain appropriate distributional noise and not inject identical static integers.
- **MSAI Linkage**: If straight-lining is detected, flag affected scales for Multi-Signal Anomaly Index review.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-IMMUTABLE-RAW-DATA-AND-PROVENANCE-001)**: Treat raw empirical datasets as strictly read-only and immutable; always output cleaned datasets to distinct destination paths and record data transformation manifests. [Enforcement: data_agent_guard.py]