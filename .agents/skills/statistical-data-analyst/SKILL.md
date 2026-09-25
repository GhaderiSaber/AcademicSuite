---
name: statistical-data-analyst
description: Execute hypothesis tests (ANCOVA, Repeated Measures, regression, bootstrap mediation), verify parametric assumptions, and generate APA 7 Chapter 4 reports in DOCX.
---

# Psychology Statistical Data Analyst & Chapter 4 Builder Skill

This skill turns Antigravity into an expert psychometrician and statistical data analyst specialized in graduate-level research in psychology, counseling, educational sciences, and behavioral sciences. It executes deterministic statistical computations (`scipy`, `statsmodels`, `pandas`, `pingouin`) and generates APA 7th Edition Word (`.docx`) and structured data (`.json`) artifacts without arithmetic hallucinations.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Testing group differences across experimental or quasi-experimental interventions (Pre-test vs. Post-test with Control Group).
- Running One-Way ANCOVA with baseline covariates, Independent Samples $t$-tests, Paired $t$-tests, or One-Way ANOVA.
- Running Repeated-Measures ANOVA or evaluating when to transition to Linear Mixed Models (LMM).
- Evaluating multiple regression models (standard, hierarchical) following the 4-Tier Saber sequence.
- Producing defense-ready Chapter 4 thesis results packages, statistical tables, and publication-grade visualizations.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- The task requires complex latent structural equation modeling with $> 2$ latent constructs and measurement error modeling $\to$ use `sem`.
- The task requires measurement model validation, CFA factor structure, AVE, or CR $\to$ use `cfa`.
- The task requires dedicated moderation with Johnson-Neyman floodlight analysis $\to$ use `moderation`.
- The task is 3-wave longitudinal moderated mediation with autoregressive baselines $\to$ use `longitudinal-moderated-mediation`.
- The task is solely dataset hygiene, missing value imputation, or reverse scoring $\to$ use `data-cleaning` or `psychometric-scale-resolver`.

## 3. REQUIRED DATA
- **Input Formats**: Analysis-ready dataset (`.xlsx`, `.csv`, `.sav`) with scored composite variables or subscales.
- **Study Configuration**: `study_config.json` defining independent variables (IV), dependent variables (DV), covariates (CV), demographic columns, and hypothesis specifications.
- **Minimum Sample Requirements**:
  - ANCOVA: $n \ge 15\text{--}20$ per cell, total $N \ge 30$.
  - Independent $t$-test: $n \ge 15$ per group.
  - Repeated-Measures ANOVA: $N \ge 25\text{--}30$ with balanced timepoints.
  - Linear Mixed Models (LMM): $N \ge 30$ subjects with repeated observations.

## 4. ASSUMPTIONS
1. **Normality**: Univariate normality of residuals or DV per group (Shapiro-Wilk $p > .05$ for $n < 50$; Skewness $\in [-1.5, +1.5]$, Kurtosis $\in [-2.0, +2.0]$ for large samples).
2. **Homogeneity of Variances**: Levene's test of equality of error variances ($p > .05$). If violated in ANOVA, apply Welch's $F$ or Brown-Forsythe.
3. **Homogeneity of Regression Slopes (ANCOVA Mandate)**: The interaction between covariate and group ($Group \times Covariate$) must be non-significant ($p > .05$).
4. **Sphericity (Repeated Measures)**: Mauchly's test of sphericity ($p > .05$). If violated ($p \le .05$), apply Greenhouse-Geisser ($\epsilon < .75$) or Huynh-Feldt ($\epsilon \ge .75$).
5. **Linearity**: Linear relationship between covariate and DV at each level of the IV.
6. **Independence of Covariate and Treatment**: Covariate must be measured prior to treatment or baseline without treatment effect.

## 5. DECISION TREE

```
Experimental / Group Comparison Design
  │
  ├─► Covariate / Baseline Score Collected?
  │     ├─► YES: Test Homogeneity of Regression Slopes (Group × Baseline)
  │     │     ├─► Non-significant (p > .05):
  │     │     │     └─► [One-Way ANCOVA (Covariate = Pretest, DV = Posttest)]
  │     │     │           - Eliminates Lord's paradox; increases statistical power
  │     │     │           - Report F, df, p, adjusted means, partial η²
  │     │     └─► Significant (p <= .05):
  │     │           └─► Violation! Do NOT run standard ANCOVA.
  │     │                 └─► [Moderation Model / Johnson-Neyman Technique]
  │     │                       - Treat Baseline as moderator of treatment effect
  │     │
  │     └─► NO Baseline Covariate:
  │           ├─► 2 Independent Groups:
  │           │     ├─► Normal: [Independent Samples t-test] (Report t, df, p, Cohen's d)
  │           │     └─► Non-normal: [Mann-Whitney U Test] (Report U, z, p, r)
  │           └─► 3+ Independent Groups:
  │                 ├─► Normal + Homogeneous: [One-Way ANOVA + Tukey HSD]
  │                 ├─► Normal + Heterogeneous Variances: [Welch's ANOVA + Games-Howell]
  │                 └─► Non-normal: [Kruskal-Wallis H Test + Dunn-Bonferroni]
  │
  └─► Repeated Observations Across Time (Within-Subjects):
        ├─► 2 Timepoints (Single Group Pre-Post):
        │     ├─► Normal: [Paired Samples t-test] (Report t, df, p, Cohen's dz)
        │     └─► Non-normal: [Wilcoxon Signed-Rank Test]
        │
        └─► 3+ Waves or Multi-Group Repeated Measures (Pre, Post, Follow-up):
              ├─► Complete data across all waves & spherical:
              │     └─► [Repeated-Measures ANOVA (Mixed RM-ANOVA)]
              │           - Check Mauchly sphericity -> Greenhouse-Geisser if p < .05
              └─► Missing waves (> 5% missingness) OR unbalanced intervals:
                    └─► [Linear Mixed Models (LMM / Multilevel Modeling)]
                          - Full Information Maximum Likelihood (FIML)
                          - Handles missing waves without listwise case deletion
```

## 6. EXECUTION SCRIPT
Deterministic calculation and document generation scripts:
```bash
# 1. Run core hypothesis testing engine (ANCOVA, ANOVA, t-tests, regression):
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "data_scored.xlsx" \
  --task auto \
  --config "study_config.json" \
  --out "stats_results.json"

# 2. Render 300-DPI publication figures (group comparisons, residual diagnostics):
python3 .agents/skills/statistical-data-analyst/scripts/visualize_stats.py \
  --json "stats_results.json" \
  --out-dir "./publication_figures" \
  --dpi 300

# 3. Compile institutional APA 7 OpenXML Word document:
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "Chapter_4_Results.docx" \
  --mode chapter4
```

## 7. OUTPUT CONTRACT
Each analysis run produces:
- `stats_results.json`:
  ```json
  {
    "test_type": "ANCOVA",
    "f_statistic": 14.82,
    "df_between": 1,
    "df_error": 57,
    "p_value": 0.0003,
    "partial_eta_squared": 0.206,
    "adjusted_means": {
      "experimental": 24.35,
      "control": 18.12
    },
    "assumptions": {
      "homogeneity_of_slopes_p": 0.412,
      "levene_p": 0.285,
      "shapiro_p": 0.198
    },
    "verdict": "CONFIRMED"
  }
  ```
- Physical APA 7 3-line table with decoupled LTR numbers and `Times New Roman` statistical symbols.
- Scholarly narrative adhering to Saber's 5-part epistemic paragraph structure.

## 8. VALIDATION
- All numerical values, degrees of freedom, and test statistics must be verified against `stats_results.json`.
- $p$-values reported with exactly 3 decimal places (`p = .014`), preserving leading zeros in Persian (`۰.۰۱۴`, never `.۰۱۴` or `۰/۰۱۴`).
- $p = .000$ strictly converted to $p < .001$ (`p < ۰.۰۰۱` یا `۰.۰۰۱ > p`).
- Direction of mean difference or adjusted mean difference must align with theoretical hypothesis.
- Residual normality and assumption checklists must be satisfied prior to confirming results.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-VALIDATOR-THREE-TABLE-FAIL-CLOSED-001)**: Enforce fail-closed structural validation for regression models: exactly 3 tables per model (Correlations, ANOVA 11-col, Coefficients 8-col), failing any deliverable that consolidates them. [Enforcement: data_agent_guard.py]
