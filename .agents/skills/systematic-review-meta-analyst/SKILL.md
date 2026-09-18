---
name: systematic-review-meta-analyst
description: PRISMA 2020 systematic reviews and meta-analysis including PICO search, Cochrane RoB 2, Hedges' g pooling, heterogeneity, publication bias, and Forest/Funnel plot generation.
---

# Systematic Review & Meta-Analyst Skill

This skill empowers Antigravity to act as an evidence synthesis specialist and quantitative meta-analyst. It navigates the complete lifecycle of Systematic Reviews and Meta-Analyses according to PRISMA 2020 and the Cochrane Handbook for Systematic Reviews of Interventions.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Conducting or reporting a Systematic Review or Meta-Analysis in behavioral, psychological, or medical sciences.
- Documenting study selection attrition via a PRISMA 2020 4-phase flow diagram (Identification, Screening, Eligibility, Inclusion).
- Appraising study risk of bias using Cochrane RoB 2 (RCTs) or ROBINS-I (Non-randomized studies).
- Pooling study-level effect sizes into Hedges' $g$ (or Cohen's $d$, Odds Ratios) with small-sample bias correction.
- Evaluating statistical heterogeneity ($Q, I^2, \tau^2$) and testing publication bias via Egger's linear regression and Begg's rank test.
- Generating publication-grade 300-DPI Forest plots and Funnel plots.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- The task is a traditional narrative literature review for Chapter 2 $\to$ use `persian-literature-review-builder`.
- The task is primary empirical data collection or hypothesis testing on a single participant dataset $\to$ use `statistical-data-analyst`.
- The task is searching scientific databases for initial bibliographic citation mapping $\to$ use `literature-harvester` or `bibliometric-network-analyst`.

## 3. REQUIRED DATA
- **Study Extraction Data**: Extracted parameters per study:
  - Study identification: Author, year, sample sizes ($n_1, n_2$).
  - Quantitative outcomes: Means and standard deviations ($M_1, SD_1, M_2, SD_2$) or binary event rates ($e_1, n_1, e_2, n_2$).
- **PRISMA Tracking Counts**: Record counts across Identification, Screening, Eligibility, and Inclusion.
- **Risk of Bias Assessments**: Judgments across the 5 Cochrane RoB 2 domains.

## 4. ASSUMPTIONS
1. **Conceptual Homogeneity**: Included studies share sufficient methodological similarity to justify a pooled summary estimate.
2. **Small-Sample Adjustment**: Cohen's $d$ is positively biased in small samples; Hedges' $g$ correction ($J = 1 - \frac{3}{4df - 1}$) is mandatory.
3. **Model Selection**:
   - Fixed-Effect Model: Assumes a single true effect size; appropriate only when studies are functionally identical and $I^2 < 25\%$.
   - Random-Effects Model (DerSimonian-Laird): Assumes a distribution of true effects; mandatory when clinical or methodological heterogeneity exists ($I^2 \ge 25\%$).
4. **Publication Bias**: Funnel plot symmetry implies absence of small-study reporting bias; tested via Egger's regression ($p < .05$ indicates asymmetry).

## 5. DECISION TREE

```
Systematic Review & Meta-Analytic Workflow
  │
  ├─► Study Selection & Screening:
  │     └─► [PRISMA 2020 Protocol]
  │           - Track Identification -> Screening -> Eligibility -> Inclusion
  │           - Generate 4-phase PRISMA flow diagram
  │
  ├─► Methodological Quality Appraisal:
  │     ├─► Randomized Controlled Trials (RCTs):
  │     │     └─► [Cochrane RoB 2 (5 Domains)]
  │     │           - D1: Randomization, D2: Deviations, D3: Missing data,
  │     │             D4: Measurement, D5: Selection of reported result
  │     └─► Non-Randomized Studies:
  │           └─► [ROBINS-I Tool]
  │
  └─► Quantitative Synthesis (Meta-Analysis):
        ├─► Effect Size Metric:
        │     ├─► Continuous: Convert to Hedges' g (small-sample J correction)
        │     └─► Binary: Odds Ratio (OR) / Risk Ratio (RR)
        │
        ├─► Heterogeneity Evaluation:
        │     ├─► Cochran's Q (p < .10 indicates significant heterogeneity)
        │     ├─► Higgins' I²:
        │     │     ├─► I² < 25% (Low): Fixed-Effect Model (Inverse-Variance)
        │     │     └─► I² >= 25% (Moderate to High): Random-Effects Model (DerSimonian-Laird)
        │     └─► Between-study variance tau²
        │
        └─► Publication Bias & Small-Study Effects:
              ├─► Egger's Linear Regression (Significant intercept p < .05 = Bias)
              ├─► Begg & Mazumdar Rank Correlation
              └─► Funnel Plot Visual Inspection with Pseudo 95% Confidence Bounds
```

## 6. EXECUTION SCRIPT
Deterministic execution scripts:
```bash
# 1. Run quantitative meta-analysis pipeline:
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "study_data.json" \
  --out-dir "meta_analysis_results" \
  --lang fa

# 2. Render 300-DPI PRISMA 2020 Flowchart:
python3 .agents/skills/systematic-review-meta-analyst/scripts/generate_prisma_flowchart.py \
  --json "study_data.json" \
  --out "meta_analysis_results/prisma_2020_flowchart.png" \
  --dpi 300 \
  --lang fa
```

## 7. OUTPUT CONTRACT
The skill produces:
- `meta_analysis_results.json`:
  ```json
  {
    "model_type": "Random-Effects (DerSimonian-Laird)",
    "k_studies": 14,
    "total_n": 1240,
    "pooled_hedges_g": 0.54,
    "ci_95": [0.38, 0.70],
    "z_statistic": 6.62,
    "p_value": 0.0001,
    "heterogeneity": {
      "cochran_q": 28.45,
      "df": 13,
      "p_value": 0.008,
      "i_squared": 54.3,
      "tau_squared": 0.062
    },
    "publication_bias": {
      "eggers_intercept": 1.24,
      "eggers_p": 0.185,
      "interpretation": "No significant small-study publication bias"
    }
  }
  ```
- Physical institutional OpenXML Word report: `Meta_Analysis_Report.docx`.
- 300-DPI publication figures: `forest_plot.png`, `funnel_plot.png`, `prisma_2020_flowchart.png`.

## 8. VALIDATION
- Filenames must be strictly English ASCII characters (Directive 6).
- Every continuous effect size must use Hedges' $g$ rather than uncorrected Cohen's $d$.
- When $I^2 \ge 25\%$, the random-effects pooled estimate must be reported as the primary finding.
- Publication bias claims must cite both visual funnel inspection and Egger's regression test statistic.
- All numbers in narrative tables must strictly match `meta_analysis_results.json`.
