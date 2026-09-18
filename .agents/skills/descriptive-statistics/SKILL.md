---
name: descriptive-statistics
description: Calculate univariate sample descriptive parameters (N, Mean, SD, Min, Max, Skewness, Kurtosis, SE) and demographic frequency distributions.
---

# Descriptive Statistics Skill (آمار توصیفی و ویژگی‌های جمعیت‌شناختی)

Computes univariate descriptive statistics, central tendency, dispersion metrics, distributional shape indices (skewness & kurtosis), and categorical demographic frequency tables in strict conformance with APA 7th Edition standards.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Stage 4.1 Demographic Profiling**: Calculating absolute frequencies ($n$) and percentages ($\%$) for categorical sample attributes (gender, education, age brackets, clinical subtype).
2. **Stage 4.2 Study Variables Descriptives**: Calculating sample size ($N$), Mean ($M$), Standard Deviation ($SD$), Standard Error ($SE$), Minimum ($\text{Min}$), Maximum ($\text{Max}$), Skewness, and Kurtosis for all primary study scales and subscales.
3. **Pre-Flight Distributional Screening**: Evaluating preliminary univariate normality via Kline (2023) skewness/kurtosis bounds before parametric modeling.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Testing Hypotheses**: Descriptive statistics summarize observed sample attributes; they do not test population inferences or experimental hypotheses.
2. **Reporting Mean/SD for Extreme Skewness**: If a variable exhibits extreme skewness ($|\text{Skew}| > 2.0$), reporting only Mean and $SD$ is misleading; Median and Interquartile Range ($\text{IQR}$) must be reported alongside or instead.
3. **Whole-Integer Artificial Means**: Empirical psychometric survey means almost never result in whole round integers (e.g. $M = 24.00$); watch for synthetic data fabrication.

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Continuous composite scores for study variables; categorical factors for demographics.
- **CLI Parameters**:
  - `--data`: Path to cleaned data file.
  - `--vars`: Comma-separated list of continuous study variables.
  - `--demographics`: Comma-separated list of categorical demographic variables.
  - `--output`: Destination path for `02_descriptives.json`.

---

## 4. Methodological & Statistical Assumptions
1. **Measurement Scales**: Interval or ratio scale for means, standard deviations, and skewness; nominal or ordinal for frequencies.
2. **Precision Standards (Directive 4)**:
   - Means, SDs, Min, Max: Exactly **2 decimal places** ($M = 24.35, SD = 4.12$).
   - Percentages: Exactly **1 decimal place** ($45.2\%$).
   - Standard dot decimal in Persian (`۰.۰۵`, `۲۴.۳۵`), never slashes (`۲۴/۳۵`).

---

## 5. Method-Selection Decision Tree
```text
Variable Type & Distributional Shape:
├── Categorical Demographic Variable (e.g. Gender, Marital Status):
│   └── USE: Frequency Distribution Table (Frequency n, Valid Percent %, Cumulative %)
└── Continuous Metric / Psychological Scale Score:
    ├── Skewness & Kurtosis Evaluation:
    │   ├── |Skewness| < 2.0 and |Kurtosis| < 7.0 (Kline, 2023):
    │   │   └── USE: Parametric Descriptives (N, M, SD, Min, Max, SE)
    │   └── Severe Skewness (|Skew| >= 2.0 or |Kurt| >= 7.0):
    │       └── USE: Robust Descriptives (Report Median & IQR alongside M & SD)
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/descriptive-statistics/scripts/compute_descriptives.py \
  --data path/to/cleaned_data.xlsx \
  --vars "mindfulness,psych_flexibility,burnout" \
  --demographics "gender,education,age_group" \
  --output path/to/02_descriptives.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`02_descriptives.json`**:
   - `study_variables`: List of objects containing `{"variable": ..., "n": ..., "mean": ..., "sd": ..., "se": ..., "min": ..., "max": ..., "skewness": ..., "kurtosis": ...}`.
   - `demographics`: Dictionary of categorical factors with levels, frequencies, and percentages.
2. **APA 7 OpenXML Word Tables**:
   - Table 1: Demographic Characteristics of Participants (جدول ۱: ویژگی‌های جمعیت‌شناختی آزمودنی‌ها).
   - Table 2: Descriptive Statistics of Study Variables (جدول ۲: شاخص‌های توصیفی متغیرهای پژوهش).

---

## 8. Validation & Forensic Sanity Checks
- **Sample Consistency Check**: Verify that $\sum n_i = N_{\text{total}}$ for all mutually exclusive demographic categories.
- **Range Sanity Check**: Ensure observed $\text{Min}$ and $\text{Max}$ values do not exceed the instrument's theoretical score bounds.
- **Standard Deviation Non-Zero Check**: $SD > 0.0$. Zero variance indicates a constant or straight-lined variable.

