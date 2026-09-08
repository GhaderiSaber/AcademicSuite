---
name: statistical-data-analyst
description: >-
  Expert statistical data analysis and Chapter 4 reporting skill tailored for psychological, educational,
  and behavioral research. Ingests SPSS (.sav), Excel (.xlsx), and CSV datasets, verifies statistical
  assumptions (normality, homoscedasticity, multicollinearity), executes hypothesis tests (ANCOVA, Repeated Measures,
  t-tests, hierarchical regression, bootstrap mediation, Cronbach's alpha), and generates publication-grade
  APA 7th Edition Word (.docx) tables and defense-ready Chapter 4 reports in academic Persian and English.
---

# Psychology Statistical Data Analyst & Chapter 4 Builder Skill

This skill turns Antigravity into an **expert psychometrician and statistical data analyst** specialized in graduate-level research in psychology, counseling, educational sciences, and organizational behavior.

It bridges the gap between raw data files (`.sav`, `.xlsx`, `.csv`) and **defense-ready Chapter 4 thesis documents (`یافته‌های پژوهش.docx`)** or **journal article results sections**. All statistical calculations are executed deterministically through Python (`scipy`, `statsmodels`, `pandas`), strictly eliminating arithmetic hallucinations.

---

## 1. Service Delivery Modes

This skill accommodates the distinct consulting packages you provide to university students:

| Mode | Deliverable | Format | Purpose |
| :--- | :--- | :--- | :--- |
| **`chapter4`** *(Default)* | Full Chapter 4 (`فصل چهارم: یافته‌های پژوهش.docx`) | Word `.docx` + Persian Typography | Formatted with *B Titr*, *B Nazanin*, APA 7 borderless tables, and complete academic narrative. Plugs directly into `persian-thesis-builder`. |
| **`article`** | Journal Results Section | Word `.docx` or Markdown | Condensed APA 7 tables, high-DPI figures, and compact reporting for ISI, Scopus, or ISC submissions. |
| **`defense_consult`** | Viva / Defense Preparation Cheat-Sheet | Markdown / Summary | Clear, plain-language explanations of *why* tests were selected, what $p$-values and effect sizes mean, and scripted answers for thesis committee questions. |
| **`stats_only`** | Structured Statistical Archive | JSON + Clean Excel tables | Exact statistical values, correlation matrices, and test summaries for clients who only need the numbers. |

---

## 2. Core Methodological Domains in Psychology

The skill provides specialized workflows for the three standard psychology research designs:

### A. Experimental & Intervention Studies (طرح‌های آزمایشی و نیمه‌آزمایشی)
- **Designs**: Pre-test vs. Post-test with Control Group (e.g., Mindfulness, CBT, Neurofeedback).
- **Primary Tool**: **One-Way ANCOVA (تحلیل کوواریانس تک‌متغیری)**:
  - Covariate: Pre-test baseline scores.
  - Independent Variable: Group (Experimental vs. Control).
  - Dependent Variable: Post-test scores.
- **Critical Assumption Guardrails**:
  1. *Homogeneity of regression slopes*: The interaction ($Group \times Pretest$) must be non-significant ($p > .05$).
  2. *Homogeneity of variances*: Levene's test ($p > .05$).
  3. *Reporting*: $F$, $df$, $p$, adjusted means, and partial eta-squared ($\eta_p^2$).

### B. Correlational, Predictive & Mediation Studies (طرح‌های همبستگی و مدل‌های ساختاری)
- **Correlation Matrix**: Pearson $r$ (parametric) or Spearman $\rho$ (non-parametric) with significance stars (*, **).
- **Hierarchical Multiple Regression**:
  - Step 1: Control/demographic variables (Age, Gender, Education).
  - Step 2: Primary psychological predictors.
  - Reporting: $R^2$, $\Delta R^2$, $F$, $\Delta F$, standardized $\beta$, $t$, and Collinearity VIF ($< 5.0$).
- **Mediation Analysis (Hayes PROCESS Model 4)**:
  - Path $a$ ($X \to M$), Path $b$ ($M \to Y$), Path $c$ (Total), Path $c'$ (Direct).
  - **Indirect Effect**: Evaluated using **5,000 bootstrap resamples** with 95% bias-corrected confidence intervals (CI). Confirmed if 95% CI does not span zero.

### C. Psychometric Scale Standardization (اعتباریابی و هنجاریابی ابزارها)
- **Internal Consistency**: Cronbach's alpha ($\alpha \ge .70$), McDonald's omega ($\omega$).
- **Item Diagnostics**: Corrected item-total correlations ($r \ge .30$) and "alpha if item deleted".

---

## 3. Step-by-Step Execution Protocol

When a student provides a dataset and asks for analysis or Chapter 4, follow this 5-step protocol:

```
[Student Data (.sav/.xlsx) + Hypotheses]
                   │
                   ▼
       [Step 1: Data Triage]
       - Inspect columns, sample size, missing values
                   │
                   ▼
    [Step 2: Formulate Config JSON]
    - Map hypotheses to tests (ANCOVA, Regression, Mediation)
                   │
                   ▼
  [Step 3: Run Deterministic Engine]
  - python3 psychology_stats.py --auto --config study_config.json
                   │
                   ▼
  [Step 4: Generate Word Document]
  - python3 generate_apa_docx.py --json stats_results.json --mode chapter4
                   │
                   ▼
  [Step 5: Defense Review & Delivery]
  - Verify tables, APA notation, and hypothesis conclusions
```

### Step 1: Inspect Dataset
Inspect the provided data file using Python:
```bash
python3 -c "import pandas as pd; df = pd.read_excel('data.xlsx'); print(df.info()); print(df.head())"
```

### Step 2: Formulate `study_config.json`
Create a study configuration mapping all variables and hypotheses:
```json
{
  "descriptives": {
    "vars": ["Pre_Anxiety", "Post_Anxiety", "Resilience", "Self_Efficacy"]
  },
  "reliability": {
    "Resilience_Scale": ["R1", "R2", "R3", "R4", "R5"],
    "Self_Efficacy_Scale": ["SE1", "SE2", "SE3", "SE4"]
  },
  "correlation": {
    "vars": ["Resilience", "Self_Efficacy", "Post_Anxiety"],
    "method": "pearson"
  },
  "ancova": [
    {
      "dv": "Post_Anxiety",
      "group": "Group",
      "covar": "Pre_Anxiety"
    }
  ],
  "mediation": [
    {
      "x": "Pre_Anxiety",
      "m": "Resilience",
      "y": "Post_Anxiety",
      "bootstraps": 2000
    }
  ]
}
```

### Step 3: Run the Calculation Engine
Execute the bundled script in `.agents/skills/statistical-data-analyst/scripts/`:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/dataset.xlsx" \
  --task auto \
  --config "study_config.json" \
  --out "stats_results.json"
```

### Step 4: Generate APA 7th Edition Word Document
Run the Word generator script:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

---

## 4. Academic Writing Standards for Chapter 4 (Persian)

Ensure all generated chapter text strictly follows standard Iranian university conventions:
1. **Never guess or estimate numbers**: All figures in the text must match `stats_results.json` to the exact decimal point.
2. **Font Styling**:
   - Chapter Titles: `B Titr 16 pt Bold`
   - Subheadings: `B Nazanin 14 pt Bold`
   - Body Paragraphs: `B Nazanin 13 pt Regular`, Line spacing 1.25, Justified.
   - Statistics: `Times New Roman 11 pt Italic` (*M, SD, t, F, p, r, β, η²*).
3. **APA 7 Table Rules**:
   - Tables must have **no vertical borders**.
   - Exactly 3 horizontal borders: Top line, Header line, Bottom line.
   - Captions placed **above** the table: `جدول ۱-۴. شاخص‌های توصیفی...` (11 pt Bold).
   - Notes placed **below** the table: `یادداشت. * p < .۰۵` (10 pt Regular).
4. **Hypothesis Conclusion Statement**:
   - Every hypothesis test must conclude with a clear verdict:
     > «بنابراین با توجه به معناداری آماره آزمون در سطح ۰/۰۵، فرضیه پژوهش مبنی بر [عنوان فرضیه] مورد **تأیید** قرار گرفت.»

---

## 5. Defense Committee Q&A Guide (جلسه دفاع)

When providing consultation notes to students, include answers to the most common committee questions:

- **Q: "Why did you use ANCOVA instead of a t-test on difference scores (Post - Pre)?"**
  - *Answer*: "ANCOVA possesses significantly higher statistical power and eliminates Lord's paradox by statistically adjusting for baseline pre-test variances and regression toward the mean."
- **Q: "Did you verify that ANCOVA assumptions were not violated?"**
  - *Answer*: "Yes, we formally tested the homogeneity of regression slopes ($Group \times Pretest$, $p > .05$) and Levene's test of equality of error variances ($p > .05$)."
- **Q: "Why did you use bootstrapping for mediation rather than the Sobel test?"**
  - *Answer*: "The Sobel test assumes normal distribution of the indirect effect $ab$, which is almost always skewed in finite samples. Preacher & Hayes (2008) recommend bootstrapping as it makes no distributional assumptions and provides robust bias-corrected confidence intervals."

---

## 6. Bundled Resources

- [Statistical Decision Trees](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/statistical-data-analyst/references/statistical_decision_tree.md) — Comprehensive guide for test selection.
- [APA 7 Reporting Guide](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/statistical-data-analyst/references/apa7_psychology_reporting_guide.md) — Exact bilingual reporting sentences and notation rules.
- [psychology_stats.py](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/statistical-data-analyst/scripts/psychology_stats.py) — Core calculation engine.
- [generate_apa_docx.py](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py) — Word document and table styling engine.
