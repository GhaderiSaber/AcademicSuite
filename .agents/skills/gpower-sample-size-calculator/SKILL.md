---
name: gpower-sample-size-calculator
description: Automated sample size determination and statistical power analysis engine based on Faul et al.'s (2007, 2009) G*Power 3.1 methodology and Cohen's (1988) statistical power framework. Computes a priori, post hoc, and sensitivity power for t-tests, ANOVA, ANCOVA, Repeated Measures, Multiple Linear Regression, Pearson r correlation, and SEM/CFA. Exports publication-grade Chapter 3 methodology defense justifications (.docx), 300-DPI dual-panel power curve plots (.png), multi-sheet Excel matrices (.xlsx), and machine-readable JSON summaries.
---

# `gpower-sample-size-calculator` — Academic Sample Size & Power Determination Engine (Skill #21)

`gpower-sample-size-calculator` is the official academic sample size justification and statistical power analysis engine of the **AcademicSuite**. It provides exact, defense-ready sample size calculations and power curve visualizations adhering strictly to Cohen's (1988) power framework and Faul et al.'s (2007, 2009) G*Power 3.1.9.7 algorithms.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user requests **calculating sample size** or **statistical power** for a research proposal, dissertation Chapter 3, or journal article.
- The user asks: *"How many subjects do I need for an ANCOVA with 2 groups and 1 pre-test covariate?"*
- The user asks for a **G*Power calculation** or **power curve figure** for their defense presentation.
- The user needs an **official Chapter 3 methodology writeup** citing Faul et al. (2007, 2009) and Cohen (1988).
- The user wants to conduct a **sensitivity analysis** (what is the minimum detectable effect size for my sample of $N = 60$?).
- The user needs to verify sample size adequacy for **Structural Equation Modeling (SEM)** or **Confirmatory Factor Analysis (CFA)** using Westland (2010) or Bentler & Chou (1987) rules.

---

## 2. Statistical Test Families Supported

1. **Analysis of Covariance (ANCOVA)**:
   - Evaluates required $N$ controlling for $c$ baseline covariates across $k$ experimental groups.
   - Non-centrality $\lambda = f^2 \times N$, $df_1 = k - 1, df_2 = N - k - c$.
2. **Analysis of Variance (ANOVA)**:
   - One-Way ANOVA, Factorial ANOVA ($2 \times 2, 2 \times 3, 3 \times 3$).
3. **Repeated Measures ANOVA**:
   - Within factors, Between-Within interaction across $m$ measurements with correlation $r$ and sphericity correction $\epsilon$.
4. **Multiple Linear Regression**:
   - Fixed model ($R^2$ deviation from zero), hierarchical step 2 $R^2$ increase ($f^2 = \frac{R^2}{1-R^2}$).
5. **$t$-Tests**:
   - Independent samples $t$-test (with group allocation ratio $\kappa = n_2/n_1$), Paired samples $t$-test ($d_z$).
6. **Bivariate Correlation**:
   - Pearson $r$ (two-tailed / one-tailed).
7. **Structural Equation Modeling (SEM / CFA)**:
   - Westland (2010) lower-bound sample sizes, Bentler-Chou $10:1$ parameter ratio, and Kline (2015) graduate consensus thresholds ($N \ge 200$).

---

## 3. Cohen's Effect Size Benchmarks

| Metric | Small | Medium (Standard) | Large |
| :---: | :---: | :---: | :---: |
| **Cohen's $d$** ($t$-tests) | $0.20$ | **$0.50$** | $0.80$ |
| **Cohen's $f$** (ANOVA/ANCOVA) | $0.10$ | **$0.25$** | $0.40$ |
| **Cohen's $f^2$** (Regression) | $0.02$ | **$0.15$** | $0.35$ |
| **Pearson $r$** (Correlation) | $0.10$ | **$0.30$** | $0.50$ |

---

## 4. CLI Command Reference

### Standard ANCOVA Calculation (Persian Chapter 3 Report):
```bash
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test ancova \
  --groups 2 \
  --covariates 1 \
  --power 0.85 \
  --effect-size 0.25 \
  --out-dir "./sample_size_ancova" \
  --lang fa
```

### Multiple Regression Calculation (English Mode):
```bash
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test regression \
  --predictors 4 \
  --power 0.80 \
  --effect-size 0.15 \
  --out-dir "./sample_size_regression" \
  --lang en
```

### Full Multi-Test JSON Payload:
```bash
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --json "sample_gpower_payload.json" \
  --out-dir "./gpower_results" \
  --lang fa
```

---

## 5. Generated Deliverables

1. **`گزارش_محاسبه_حجم_نمونه_جی‌پاور.docx`** (or `GPower_Sample_Size_Report.docx`):
   - Professional Word document formatted with native RTL OpenXML BiDi and authentic Iranian typography (*B Titr*, *B Nazanin*, *Times New Roman*).
   - Chapter 3 ready-to-paste narrative paragraph, APA 7 parameter input-output table, and embedded 300-DPI power curve figure.
2. **`power_curve_plot.png` (300 DPI)**:
   - High-resolution dual-panel figure: Left panel displays Power ($1-\beta$) vs Sample Size ($N$) across Small, Medium, Large effect sizes; Right panel displays the central vs non-central critical distribution.
3. **`sample_size_calculator_matrix.xlsx`**:
   - 4-sheet Excel workbook: `Executive Summary`, `Power Curve Data`, `Sensitivity Analysis`, `SEM & CFA Rules`.
4. **`gpower_results.json`**:
   - Machine-readable results schema for seamless integration into research proposals and dissertation pipelines.
