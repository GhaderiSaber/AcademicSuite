---
name: gpower-sample-size-calculator
description: A priori, post hoc, and sensitivity statistical power analysis (G*Power 3.1 & Cohen 1988) for t-tests, ANOVA, ANCOVA, regression, mediation, and SEM.
---

# G*Power Sample Size Calculator & Power Analysis Skill

This skill provides deterministic statistical power calculations, sample size justifications, and power curve visualizations following Cohen's (1988) power framework and Faul et al.'s (2007, 2009) G*Power 3.1 algorithms.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Conducting *A Priori* power analysis to determine required minimum sample size $N$ for a research proposal, grant, or Chapter 3 methodology.
- Conducting *Post Hoc* power analysis to determine achieved power ($1-\beta$) given sample size, observed effect size, and $\alpha$.
- Conducting *Sensitivity* power analysis to determine minimum detectable effect size for a fixed available sample.
- Calculating required sample sizes for ANCOVA, ANOVA, Repeated Measures, Multiple Regression, $t$-tests, or SEM/CFA.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- The task requires running inferential hypothesis tests on an empirical dataset $\to$ use `statistical-data-analyst`.
- The task requires sampling design strategy, cluster sampling weights, or sampling frame selection $\to$ use `methodology-review`.
- The task requires psychometric item parameter recovery in IRT $\to$ use `psychometric-scale-validator`.

## 3. REQUIRED DATA
- **Analysis Type**: `a_priori`, `post_hoc`, or `sensitivity`.
- **Target Test**: `ancova`, `anova`, `regression`, `t_test_ind`, `t_test_paired`, `correlation`, or `sem`.
- **Design Parameters**:
  - $\alpha$ level (standard $.05$).
  - Desired power $1-\beta$ (standard $.80$ to $.95$).
  - Anticipated effect size ($d = 0.50$ medium, $f = 0.25$ medium, $f^2 = 0.15$ medium, $r = 0.30$ medium).
  - Number of groups, covariates, or predictors.

## 4. ASSUMPTIONS
1. **Accurate Effect Size Estimation**: Effect sizes should derive from published meta-analyses or Cohen's empirical benchmarks, never arbitrarily inflated.
2. **Type I Error Rate ($\alpha$)**: Standard two-tailed $\alpha = .05$ unless directional hypothesis justification is established.
3. **Non-Central Distributions**: Power calculations rely on non-central $t$, $F$, or $\chi^2$ distributions with non-centrality parameter $\lambda$.
4. **Sample Homogeneity and Equal Allocation**: Default assumes equal group sizes unless allocation ratio $\kappa$ is explicitly declared.

## 5. DECISION TREE

```
Power Analysis & Sample Size Determination
  │
  ├─► Analysis Goal:
  │     ├─► Planning Stage (Sample size unknown):
  │     │     └─► [A Priori Analysis] -> Input: alpha, power (0.80/0.85), effect size -> Output: Required N
  │     ├─► Post-Data Collection (Sample size fixed):
  │     │     └─► [Post Hoc Analysis] -> Input: alpha, N, observed effect size -> Output: Achieved Power (1 - beta)
  │     └─► Resource-Constrained (Fixed N available):
  │           └─► [Sensitivity Analysis] -> Input: alpha, power (0.80), N -> Output: Minimum Detectable Effect
  │
  └─► Statistical Test Family:
        ├─► Group Comparisons with Covariates:
        │     └─► [ANCOVA]: df1 = groups - 1, df2 = N - groups - covariates, lambda = f^2 × N
        ├─► Multi-Group Mean Comparisons:
        │     └─► [ANOVA]: One-Way (f), Factorial (f), Repeated-Measures (epsilon, correlation)
        ├─► 2-Group Comparison:
        │     ├─► Independent: [t-test Independent] (Cohen's d, allocation ratio)
        │     └─► Within-Subjects: [t-test Paired] (Cohen's dz)
        ├─► Regression & Prediction:
        │     └─► [Multiple Linear Regression]: f^2 = R^2 / (1 - R^2), number of predictors
        └─► Latent Variable SEM / CFA:
              ├─► Westland (2010) lower-bound sample algorithm
              └─► Rule-of-thumb: Bentler-Chou 10:1 ratio; Kline (2016) N >= 200 threshold
```

## 6. EXECUTION SCRIPT
Deterministic calculation and deliverable compilation:
```bash
# ANCOVA Power Analysis (Persian Chapter 3 output):
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test ancova \
  --groups 2 \
  --covariates 1 \
  --power 0.85 \
  --effect-size 0.25 \
  --out-dir "gpower_results_ancova" \
  --lang fa

# Multiple Regression Power Analysis:
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test regression \
  --predictors 4 \
  --power 0.80 \
  --effect-size 0.15 \
  --out-dir "gpower_results_regression" \
  --lang en
```

## 7. OUTPUT CONTRACT
The engine generates:
- `gpower_results.json`:
  ```json
  {
    "test": "ANCOVA",
    "analysis_type": "a_priori",
    "alpha": 0.05,
    "power": 0.85,
    "effect_size_f": 0.25,
    "num_groups": 2,
    "num_covariates": 1,
    "critical_f": 4.07,
    "required_n": 58,
    "actual_power": 0.854,
    "citations": ["Faul et al. (2007)", "Cohen (1988)"]
  }
  ```
- Physical institutional OpenXML Word deliverable: `GPower_Sample_Size_Report.docx`.
- 300-DPI publication power curve: `power_curve_plot.png`.
- 4-sheet calculation workbook: `sample_size_calculator_matrix.xlsx`.

## 8. VALIDATION
- Total required $N$ must round UP to the nearest integer.
- Actual achieved power must equal or exceed target power ($1-\beta \ge \text{target}$).
- Group allocation ratios must yield integer sample allocations per cell.
- Persian Word deliverable must strictly enforce OpenXML BiDi RTL (`<w:bidi w:val="1"/>`) and `B Nazanin` / `B Titr` typography.
