---
name: systematic-review-meta-analyst
description: >-
  Expert systematic review and quantitative meta-analysis skill adhering to PRISMA 2020 standards and Cochrane
  Risk of Bias (RoB 2). Formulates PICO search strings for international (PubMed, Scopus, Web of Science, PsycINFO)
  and Iranian (Magiran, SID, Irandoc) databases, generates PRISMA 4-phase study flow diagrams, executes RoB 2
  evaluations, deterministically computes Hedges' g effect sizes, pooled effects (Fixed-Effect and DerSimonian-Laird
  Random-Effects), heterogeneity (Q, I², τ²), and publication bias (Egger's regression), generating high-resolution
  Forest and Funnel plots alongside publication-ready APA 7 Word manuscripts (.docx) in English or Persian.
---

# Systematic Review & Meta-Analyst Skill (مرور سیستماتیک و فراتحلیل بر اساس PRISMA 2020)

This skill empowers Antigravity to act as an elite evidence synthesis specialist and quantitative meta-analyst. It navigates the complete lifecycle of **Systematic Reviews and Meta-Analyses** (Level 1 scientific evidence) according to **PRISMA 2020 (Preferred Reporting Items for Systematic Reviews and Meta-Analyses)** and the **Cochrane Handbook for Systematic Reviews of Interventions**.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user requests conducting or reporting a **Systematic Review (مرور سیستماتیک)** or **Meta-Analysis (فراتحلیل)** in psychology, psychiatry, counseling, or behavioral medicine.
2. The user needs to construct a **PRISMA 2020 Flow Diagram** documenting study identification, screening, eligibility, and inclusion numbers.
3. The user needs to evaluate the methodological quality or risk of bias of studies using **Cochrane RoB 2 (Randomized Controlled Trials)** or **ROBINS-I (Non-randomized studies)**.
4. The user has study-level quantitative data ($N$, Mean, SD, or events/totals) and needs to pool effect sizes (**Cohen's $d$, Hedges' $g$, Odds Ratio**), compute heterogeneity ($Q$, $I^2$, $\tau^2$), and test publication bias (**Egger's test**, Begg's test).
5. The user needs to generate publication-grade **Forest Plots** and **Funnel Plots** or compile an APA 7 synthesis Word document (`.docx`).

---

## 2. Evidence Synthesis Architecture & Lifecycle

```
[PICO Research Question & Scope]
               │
               ▼
[Phase 1: Identification]
├── Boolean search across PubMed, Scopus, WoS, PsycINFO, Magiran, SID
└── Automated deduplication tracking
               │
               ▼
[Phase 2: Screening]
├── Title and abstract screening based on inclusion/exclusion criteria
└── Document reasons for exclusion
               │
               ▼
[Phase 3: Eligibility & Appraisal]
├── Full-text retrieval and eligibility assessment
└── Cochrane RoB 2 appraisal across 5 domains
               │
               ▼
[Phase 4: Quantitative Synthesis & Meta-Analysis]
├── Effect size computation (Hedges' g with small-sample correction)
├── Model pooling: Fixed-Effect & Random-Effects (DerSimonian-Laird)
├── Heterogeneity triage (Cochran's Q, Higgins' I², Tau²)
├── Publication bias diagnostics (Egger's regression, Funnel plot)
└── Visual Forest Plot & APA 7 Systematic Review Manuscript (.docx)
```

---

## 3. Methodological Pillars & Standards

### Pillar A: PRISMA 2020 Compliance
- Strict tracking across the 4 stages of the PRISMA 2020 statement:
  1. *Identification*: Records identified from databases, registers, and other sources.
  2. *Screening*: Records screened by title and abstract, and duplicates removed.
  3. *Eligibility*: Full-text reports assessed against explicit inclusion and exclusion criteria.
  4. *Inclusion*: Studies included in qualitative systematic review and quantitative meta-analysis.
- Comprehensive 27-item checklist verification.

### Pillar B: Cochrane Risk of Bias 2 (RoB 2) Appraisal
Each randomized trial is evaluated across 5 mandatory bias domains:
- **Domain 1**: Bias arising from the randomization process (allocation sequence concealment, baseline balance).
- **Domain 2**: Bias due to deviations from intended interventions (blinding of participants and personnel).
- **Domain 3**: Bias due to missing outcome data (attrition rates, intention-to-treat analysis).
- **Domain 4**: Bias in measurement of the outcome (blinding of outcome assessors, standardized instruments).
- **Domain 5**: Bias in selection of the reported result (pre-registered protocol / trial registry alignment).
- **Overall Judgment**: Categorized as *Low risk of bias*, *Some concerns*, or *High risk of bias*.

### Pillar C: Deterministic Meta-Analytic Algebra
- **Small-Sample Bias Correction**: Always converts Cohen's $d$ into **Hedges' $g$** via the exact correction factor:
  $$J = 1 - \frac{3}{4(N_1 + N_2 - 2) - 1}$$
  $$g = d \times J$$
- **Dual Pooling Models**:
  - *Fixed-Effect Model*: Weighted by inverse variance ($w_i = 1 / v_i$).
  - *Random-Effects Model*: Incorporates between-study variance via the DerSimonian-Laird estimator:
    $$\tau^2 = \max\left(0, \frac{Q - (k - 1)}{\sum w_i - \frac{\sum w_i^2}{\sum w_i}}\right)$$
    $$w_i^* = \frac{1}{v_i + \tau^2}$$
- **Heterogeneity Reporting**:
  - Cochran's $Q$ test ($df = k - 1, p_Q$).
  - Higgins' $I^2 = \max\left(0, \frac{Q - df}{Q}\right) \times 100\%$ ($< 25\%$ Low, $25\% - 75\%$ Moderate, $> 75\%$ High).
  - Between-study variance $\tau^2$ and standard deviation $\tau$.
- **Publication Bias**:
  - **Egger's Linear Regression**: Regresses standardized effect size ($SND = g_i / SE_i$) on precision ($1 / SE_i$). Significant intercept ($p < .05$) indicates funnel plot asymmetry and publication bias.
  - Begg and Mazumdar's rank correlation test.

---

## 4. Execution Workflow

### Step 1: Prepare Study-Level Payload
Format extracted study parameters and screening counts into `meta_analysis_payload.json` following the schema in `examples/sample_meta_analysis_payload.json`.

### Step 2: Run Meta-Analysis Engine
Execute the Python computational pipeline:
```bash
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json study_data.json \
  --out-dir ./meta_analysis_results \
  --lang en
```
For Persian thesis or journal publication (ISC):
```bash
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json study_data.json \
  --out-dir ./meta_analysis_results_fa \
  --lang fa
```

### Step 3: Generate High-Resolution PRISMA 2020 Flowchart (Optional / Dedicated Figure)
To generate a standalone 300-DPI vector-quality PRISMA 2020 4-phase flow diagram:
```bash
python3 .agents/skills/systematic-review-meta-analyst/scripts/generate_prisma_flowchart.py \
  --json study_data.json \
  --out ./meta_analysis_results/prisma_2020_flowchart.png \
  --dpi 300 \
  --lang en
```
Or for Persian thesis/defense:
```bash
python3 .agents/skills/systematic-review-meta-analyst/scripts/generate_prisma_flowchart.py \
  --json study_data.json \
  --out ./meta_analysis_results/نمودار_جریان_پریسما_۲۰۲۰.png \
  --dpi 300 \
  --lang fa
```

### Step 4: Inspect Generated Deliverables
1. **`prisma_2020_flowchart.png`**: Publication-grade 4-phase PRISMA 2020 flow diagram documenting exact study attrition across Identification, Screening, Eligibility, and Inclusion.
2. **`forest_plot.png`**: High-resolution forest plot illustrating each study's effect size ($g$), 95% CI, relative weight (%), and the pooled summary diamond.
3. **`funnel_plot.png`**: Funnel plot of precision ($1 / SE$) or $SE$ vs. effect size with pseudo 95% confidence bounds.
4. **`Meta_Analysis_Report.docx`**: APA 7 formatted synthesis containing:
   - PRISMA 2020 Flow Numbers.
   - Characteristics of Included Studies Table.
   - Cochrane RoB 2 Quality Assessment Matrix.
   - Quantitative Meta-Analysis Results Table (Pooled $g$, 95% CI, $Z$, $p$, $Q$, $I^2$, $\tau^2$, Egger's $t$ & $p$).
   - Embedded Forest and Funnel plots.
   - Narrative synthesis and clinical interpretation.
