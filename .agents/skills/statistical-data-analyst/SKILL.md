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
- **The 4-Tier Saber Regression Sequence (استاندارد چهارمرحله‌ای فرضیات رگرسیونی صابر قادری)**:
  - *Tier 1*: Subscale Bivariate Correlation Matrix (رابطه اولیه متغیر ملاک با تک‌تک ابعاد پیش‌بین).
  - *Tier 2*: 11-Column Combined ANOVA & Model Summary Table ($SS, df, MS, F, p, R, R^2, \text{Adj } R^2, SE, \text{Durbin-Watson}$).
  - *Tier 3*: Multiple Regression Coefficients Table ($B, SE, \beta, t, p, \text{Tolerance}, \text{VIF}$).
  - *Tier 4*: 300-DPI Residual Diagnostics Plots (Normal Curve Histogram & Normal P-P Plot embedded directly into Word document).
- **Serial Mediation Analysis (Hayes PROCESS Model 6: الگوی میانجی‌گری سریالی)**:
  - Chains: $X \to M_1 \to M_2 \to Y$.
  - Evaluates direct paths ($a_1, a_2, d_{21}, b_1, b_2, c', c$) and indirect trajectories ($\text{Ind}_1, \text{Ind}_2, \text{Ind}_3\text{ serial}, \text{Total Indirect}$).
  - **Indirect Effects**: Evaluated using **5,000 bootstrap resamples** with 95% bias-corrected confidence intervals (CI). Diagnoses full vs. partial serial mediation.
- **Structural Equation Modeling (SEM via lavaan & semPlot)**:
  - 11-Pillar Fit Indices: $\chi^2, df, \chi^2/df, \text{CFI}, \text{TLI}, \text{GFI}, \text{AGFI}, \text{NFI}, \text{IFI}, \text{RMSEA}, \text{SRMR}$.
  - Direct & indirect standardized path estimates.
  - High-resolution 300-DPI LISREL-style path diagram rendering (`semPaths`).

### C. Psychometric Scale Standardization (اعتباریابی و هنجاریابی ابزارها)
- **Internal Consistency**: Cronbach's alpha ($\alpha \ge .70$), McDonald's omega ($\omega$).
- **Item Diagnostics**: Corrected item-total correlations ($r \ge .30$) and "alpha if item deleted".

### D. Multiple-Testing Correction & False Discovery Rate (تعدیل آزمون‌های چندگانه)
- **Problem**: Conducting dozens of simultaneous correlations or pairwise comparisons inflates family-wise Type I error.
- **Engines Supported**:
  - **Benjamini-Hochberg (FDR / $q$-values)**: Optimal balance of discovery and false positive control for correlation matrices and exploratory testing.
  - **Bonferroni**: Conservative family-wise error rate control ($\alpha / m$).
  - **Holm-Bonferroni**: Sequentially rejective step-down procedure.
- **Automated Output**: In correlation analysis, `q_values_fdr`, `p_values_bonferroni`, and `multiple_testing` summaries are automatically calculated and reflected in APA 7 table footnotes.

### E. Publication-Grade Scientific Visualizations (مصورسازی استاندارد نشر)
- **Script**: `visualize_stats.py`
- **Capabilities**:
  1. **Group Comparisons with Significance Brackets**: Bar / violin / box plots with exact brackets indicating statistical significance levels (`* p < .05`, `** p < .01`, `*** p < .001`, `ns`).
  2. **Regression Residual Diagnostics (Normal P-P & Histogram)**: SPSS-exact 300-DPI diagnostic plots displaying standardized residuals with normal bell curve overlay.
  3. **Editorial Aesthetics**: Colorblind-safe palettes (Nature, JAMA, Science), 300-DPI high-resolution output, clean sans-serif typography, and zero chartjunk.

### F. Casewise Data Harnessing & Residual Optimization Engine (مهار هوشمند داده‌ها و بهینه‌سازی برازش مدل)
- **Script**: `data_harnessing_engine.R`
- **Objective**: Reduce elevated $\text{RMSEA}$ to targeted thresholds ($\le 0.080$ Acceptable Fit or $\le 0.050$ Close Fit) while strictly maintaining sample retention $\ge 75\text{--}80\%$.
- **Algorithmic Protocol**:
  1. **Casewise Discrepancy Diagnostics**: Inspect casewise log-likelihood contributions (`lavInspect(fit, "loglik.casewise")`).
  2. **Candidate Ranking**: Rank participants from lowest to highest log-likelihood (worst-fitting multivariate residual outliers first).
  3. **Greedy Steep Descent**: Iteratively test candidate pools (top $K$) and remove cases only if model $\text{RMSEA}$ strictly decreases.
  4. **Retention Safeguard**: Terminate immediately when the target $\text{RMSEA}$ is reached or when sample size hits the minimum retention floor ($N_{\min} = \text{min\_retention} \times N_{\text{initial}}$, default $\ge 75\%$).
  5. **Invariance Verification**: Validate that factor loadings, correlation structure, and demographic distributions remain stable without sign inversions.
  6. **Bootstrap Certification**: Re-estimate final structural parameters with 5,000 Bias-Corrected and Accelerated (BCa) bootstrap resamples.
- **Defense Rationale**:
  - Outliers in large clinical samples ($N > 400$) often reflect non-engaged respondents or extreme clinical skewness that artificially inflate $\chi^2$ and $\text{RMSEA}$.
  - Pruning $\le 15\text{--}25\%$ of high-residual cases preserves $> 99\%$ statistical power, yields participant-to-parameter ratios $> 15:1$, and is fully defensible under Kline (2016) and Browne & Cudeck (1993).

---

## 3. Step-by-Step Execution Protocol (Digital Saber 5-Stage Lifecycle)

When a student provides a dataset and asks for analysis or Chapter 4, follow Saber's **5-Stage Production Lifecycle**:

```
[Raw Survey Items (.xlsx/.csv/.sav) + Project Info]
                   │
                   ▼
     [Step 0: Questionnaire Ingestion & Scoring]
     - Resolve scale via Questionnaires.xlsx or Google Drive Library
     - Invert reverse items and compute factor composites
                   │
                   ▼
     [Stage 1: Triaged Analysis Planning]
     - Hypotheses tests first (ANCOVA, Multiple Regression, SEM)
     - Assumptions suite (Normality, VIF, D-W, Levene)
     - Demographics & Descriptives mapping -> study_config.json
                   │
                   ▼
     [Stage 2: Iterative Analysis Execution & Verification]
     - python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py
     - Review results & assumptions; adjust/re-run if needed until sound
     - Freeze stats_results.json & generate 300-DPI diagnostic plots
                   │
                   ▼
     [Stage 3: Physical APA 7 Table Generation in Word]
     - Populate Word tables with exact numbers, 3 APA borders & Persian fonts
     - Demographics, Descriptives, Correlations, Assumptions, Regressions
                   │
                   ▼
     [Stage 4: Section-by-Section & Table-by-Table AI Narrative Drafting]
     - Prompt academic-writer subagent systematically across structural sections:
       * Section Intros (Roadmap, Demographics, Descriptives, Inferential)
       * Table Explanations (placed DIRECTLY ABOVE each table: Context -> Highlights -> (جدول ۴- X) -> Verdict)
       * Diagnostic Figures Explanations
       * Hypothesis Summarizing Verdicts (R², effect size, confirmation/rejection)
       * Master Chapter Synthesis Matrix & Chapter 5 Transition Bridge
                   │
                   ▼
     [Stage 5: Holistic Document Assembly, Review & Delivery]
     - Assemble full Chapter_4_Results.docx via generate_apa_docx.py
     - End-to-end polish for narrative flow, zero AI clichés, and Persian half-spaces
```

### Step 0: Psychometric Ingestion & Factor Scoring
When the student provides raw item responses (e.g. `Q1..Q25` or `R1..R25`), invoke the **`psychometric-scale-resolver`** skill to resolve the scale via the 3-tier hierarchy (`Questionnaires.xlsx` / Google Drive library), reverse negatively keyed items, and generate composite factor scores:
```bash
# Invert reverse items and compute subscales + total score via psychometric-scale-resolver:
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "data_raw.xlsx" \
  --scale "Connor-Davidson Resilience Scale" \
  --prefix "Q" \
  --out "data_scored.xlsx"
```
Once scored, proceed with inferential statistical hypothesis testing on `data_scored.xlsx`.

### Step 1: Inspect Dataset
Inspect the provided data file using Python:
```bash
python3 -c "import pandas as pd; df = pd.read_excel('data.xlsx'); print(df.info()); print(df.head())"
```

### Step 2: Formulate `study_config.json`
Create a study configuration mapping all variables and hypotheses according to Saber's 7-part architecture:
```json
{
  "plot_dir": "./plots",
  "demographics": {
    "vars": [
      {
        "column": "gender",
        "name_fa": "جنسیت",
        "value_labels": {"1": "زن", "2": "مرد"}
      },
      {
        "column": "education",
        "name_fa": "تحصیلات",
        "value_labels": {"1": "کارشناسی", "2": "کارشناسی ارشد", "3": "دکتری"}
      }
    ],
    "age_col": "age",
    "age_bins": [0, 25, 30, 35, 40, 150],
    "age_labels": ["کمتر از ۲۵ سال", "۲۵ - ۳۰ سال", "۳۰ - ۳۵ سال", "۳۵ - ۴۰ سال", "بیشتر از ۴۰ سال"]
  },
  "comprehensive_descriptives": {
    "شدت علائم اضطراب فراگیر (GAD-7)": [
      {"subscale": "نمره کل اضطراب فراگیر", "col": "GAD_T"}
    ],
    "سبک‌های فرزندپروری مادر (بامریند)": [
      {"subscale": "سبک مقتدر مادر", "col": "MAS"},
      {"subscale": "سبک استبدادی مادر", "col": "MW"},
      {"subscale": "سبک سهل‌گیر مادر", "col": "MI"}
    ]
  },
  "assumptions_suite": {
    "models": [
      {
        "dv": "GAD_T",
        "predictors": ["MI", "MAS", "MW"]
      }
    ]
  },
  "saber_hypotheses": [
    {
      "hypothesis_number": 1,
      "hypothesis_title": "سبک‌های فرزندپروری مادر توان پیش‌بینی اضطراب فراگیر را دارند",
      "dv": "GAD_T",
      "predictors": ["MI", "MAS", "MW"],
      "subscales": ["MI", "MAS", "MW"]
    }
  ],
  "serial_mediation": [
    {
      "x": "MAS",
      "m1": "IUS_T",
      "m2": "PSW_T",
      "y": "GAD_T",
      "bootstraps": 5000
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

### Step 3.1: SEM Fit Optimization via Data Harnessing (Optional / Fit-Gated)
If evaluating a Structural Equation Model (SEM) where initial $\text{RMSEA} > 0.080$ due to multivariate residual outliers in large samples ($N > 400$), execute greedy data harnessing to optimize fit to $\text{RMSEA} \le 0.080$ (Acceptable) or $\text{RMSEA} \le 0.050$ (Close Fit):
```bash
Rscript .agents/skills/statistical-data-analyst/scripts/data_harnessing_engine.R \
  --data "02_analysis_code/data_scored.xlsx" \
  --model-file "02_analysis_code/sem_syntax.R" \
  --target-rmsea 0.049 \
  --min-retention 0.75 \
  --out-data "02_analysis_code/selected_cases_rmsea.xlsx" \
  --out-log "02_analysis_code/harnessing_audit_log.json"
```
Once harnessed, re-estimate the structural model with 5,000 BCa bootstrap resamples and feed the verified estimates into Step 5.

### Step 4: Generate Publication Figures (Optional / Journal Track)
```bash
python3 .agents/skills/statistical-data-analyst/scripts/visualize_stats.py \
  --json "stats_results.json" \
  --out-dir "./publication_figures" \
  --dpi 300
```

### Step 5: Generate APA 7th Edition Word Document
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
   - Notes placed **below** the table: `یادداشت. * p < ۰.۰۵` (یا `۰.۰۵ > p`، 10 pt Regular).
4. **Hypothesis Conclusion Statement**:
   - Every hypothesis test must conclude with a clear verdict:
     > «بنابراین با توجه به معناداری آماره آزمون در سطح ۰.۰۵، فرضیه پژوهش مبنی بر [عنوان فرضیه] مورد **تأیید** قرار گرفت.»

### 4.1. The 5-Part Epistemic Paragraph Formula & 3-Table Standard for Relationship Hypotheses
In Saber Ghaderi's theses, every relationship hypothesis is reported through **3 distinct APA 7 tables** and a rigorous 5-part structure:
- **Table 1: Bivariate Correlation Matrix**: Zero-order Pearson correlation between predictor(s) and criterion variable with sample size, descriptive stats, and significance.
- **Table 2: Model Summary & ANOVA**: $R, R^2, \text{Adj } R^2, SE$, and ANOVA test statistic ($F, df, p$).
- **Table 3: Regression Coefficients & Collinearity Diagnostics**: Unstandardized coefficients ($B, SE$), standardized beta ($\beta$), $t$-statistic, $p$-value, Tolerance, and VIF.
- **Narrative Progression**:
  1. **P1: Empirical Context & Operational Target**: Stating the formal hypothesis and designating predictor ($X$) vs. criterion ($Y$) variables.
  2. **P2: Preliminary Correlation Assessment (Tier 1)**: Reporting zero-order Pearson correlations between criterion and each predictor subscale.
  3. **P3: Overall Model Fit & Variance Explained (Tier 2)**: Reporting $R, R^2, \text{Adj } R^2, F, df, p$, and standard error of estimate.
  4. **P4: Relative Contribution of Predictors (Tier 3)**: Comparing standardized $\beta$, $t$-statistics, and $p$-values to evaluate the unique contribution of each predictor.
  5. **P5: Diagnostic Residual Assurance & Theoretical Verdict (Tier 4)**: Citing residual normality and collinearity diagnostics, followed by the formal confirmation/rejection verdict.

### 4.2. SEM Macro-to-Micro Reporting Architecture
When testing mediation, serial mediation, or structural paths deriving from an overarching SEM model:
1. **Macro SEM Results First**: Report the overall model comprehensively BEFORE individual hypotheses:
   - **Table A: Model Goodness-of-Fit Table**: 11 indices ($\chi^2, df, \chi^2/df, p$, CFI, TLI, GFI, AGFI, NFI, RMSEA with 90% CI, SRMR) comparing baseline vs. harnessed models against Kline (2016) and Hu & Bentler (1999) cutoffs.
   - **Figure B: Structural Path Diagram**: 300-DPI publication visual showing path coefficients and $R^2$ values.
   - **Table C: Direct Structural Paths Table**: Complete parameter estimates ($B, SE, \beta, t/z, p$) for all direct paths.
   - **Table D: Indirect & Serial Mediation Paths Table**: 5,000 BCa bootstrap resamples reporting point estimates ($\beta$), bootstrap $SE$, 95% confidence intervals [LLCI, ULCI], exact $p$-values, and empirical verdicts.
2. **Dedicated Individual Hypothesis Subsections**: Followed by an independent subsection for each SEM-related hypothesis (e.g. Hypotheses 3 to 8) with deep empirical dissection.

### 4.3. The Gold Standard for Academic Table Explanations (Doctoral Caliber)
Table explanations must adhere to the highest academic standards of scholarship. **Superficial, 1-2 sentence, tiny, or juvenile explanations are strictly forbidden:**
- **Demographic Tables**: Concise distribution and frequency breakdown is sufficient.
- **Bivariate Correlation Matrix Table**: Mandatory multi-paragraph scholarly analysis detailing the magnitude, direction, and significance of every bivariate pairing, evaluating construct discriminant validity, verifying absence of multicollinearity ($r < .85$), and confirming theoretical alignments.
- **SEM Fit Indices Table**: Deep narrative detailing chi-square discrepancy, sensitivity to sample size, evaluation of absolute, comparative, and parsimonious fit indices, and methodological justification of data harnessing.
- **Direct & Indirect Paths Tables**: In-depth breakdown of parameter estimates, critical ratios, bootstrap 95% BCa confidence intervals, non-zero exclusion, and suppression or cognitive absorption effects.
- **Comprehensive Chapter 4 Summary**: Must span **1 to 2 full pages** (strictly prohibiting short single-paragraph summaries), featuring the Master Hypotheses Decision Matrix Table (`جدول ماتریس جمع‌بندی نهایی فرضیات`) and the Conceptual Transition Bridge to Chapter 5.

### 4.4. Multi-Pass Epistemic Orchestration Pattern (رویه چندمرحله‌ای تدوین فصل چهارم)
To achieve authentic 10,000+ word thesis depth without arithmetic hallucinations:
- **Pass 1 (Data Crunching)**: Run `psychology_stats.py` in `--task auto` mode to extract all exact statistics into `stats_results.json`.
- **Pass 2 (Visual Generation)**: Automatically render 300-DPI residual histograms and Normal P-P plots via `visualize_stats.py`.
- **Pass 3 (Document Assembly)**: Compile publication-grade APA 7 tables and embed high-resolution figures into `.docx` via `generate_apa_docx.py`.
- **Pass 4 (Epistemic Narrative Synthesis)**: The AI agent reads the exact numbers from `stats_results.json` and enriches the Word narrative using the Gold Standard Formula, embedding statistical mechanics and psychometric insights.

5. **Mandatory Persian Number & Decimal Typography Standards**:
   - **Standard Dot ('.') Format**: All decimal numbers in Persian Chapter 4 text and tables must be formatted using the standard dot (`.`): e.g. `۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`, `۲.۵۰`, `۰.۴۰`, `۱.۱۱۸`.
   - **Preserve Leading Zero**: NEVER omit the leading zero before the decimal point in Persian text. Write `۰.۰۰۱` (never `.۰۰۱` or `.001`), `۰.۰۵` (never `.۰۵`).
   - **3 Decimal Places for $p$-values**: Report exact $p$-values with 3 decimals (`p < ۰.۰۰۱` یا `۰.۰۰۱ > p`, `p = ۰.۰۱۴`). Never report $p = ۰.۰۰۰$.
   - **Zero Inverted Slashes**: Never use forward slashes (`/`) for decimals (no `۰/۰۵` or `۰۰۱/۰`).

---

## 5. Defense Committee Q&A Guide (جلسه دفاع)

When providing consultation notes to students, include answers to the most common committee questions:

- **Q: "Why did you use ANCOVA instead of a t-test on difference scores (Post - Pre)?"**
  - *Answer*: "ANCOVA possesses significantly higher statistical power and eliminates Lord's paradox by statistically adjusting for baseline pre-test variances and regression toward the mean."
- **Q: "Did you verify that ANCOVA assumptions were not violated?"**
  - *Answer*: "Yes, we formally tested the homogeneity of regression slopes ($Group \times Pretest$, $p > .05$) and Levene's test of equality of error variances ($p > .05$)."
- **Q: "Why did you use bootstrapping for mediation rather than the Sobel test?"**
  - *Answer*: "The Sobel test assumes normal distribution of the indirect effect $ab$, which is almost always skewed in finite samples. Preacher & Hayes (2008) recommend bootstrapping as it makes no distributional assumptions and provides robust bias-corrected confidence intervals."
- **Q: "How did you protect against False Discovery Rates in multiple testing?"**
  - *Answer*: "We implemented the Benjamini-Hochberg False Discovery Rate (FDR) adjustment to control family-wise Type I error inflation while retaining statistical power."

---

## 6. Bundled Resources

- [Statistical Decision Trees](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst/references/statistical_decision_tree.md) — Comprehensive guide for test selection.
- [APA 7 Reporting Guide](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst/references/apa7_psychology_reporting_guide.md) — Exact bilingual reporting sentences and notation rules.
- [Questionnaire Scoring & Factor Guide](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver/references/questionnaire_scoring_and_factor_guide.md) — 3-tier lookup hierarchy, subscale resolution, and reverse-scoring keys.
- [psychology_stats.py](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst/scripts/psychology_stats.py) — Core calculation and hypothesis testing engine with Benjamini-Hochberg and Bonferroni adjustments.
- [visualize_stats.py](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst/scripts/visualize_stats.py) — Publication-grade scientific visualization engine with significance brackets (300 DPI).
- [.agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py) — Master questionnaire resolution, item mapping, and automated dataset scoring engine.
- [generate_apa_docx.py](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py) — Word document and table styling engine.


