# AGENTS.md — Global Agent Instructions & Operational Guidelines

This repository contains the **Academic Thesis & Statistical Consultancy Skill Suite** for Google Antigravity and autonomous coding agents. It is designed to assist academic researchers and graduate students (specifically in Psychology, Counseling, and Behavioral Sciences) with translating literature, extracting citations, conducting rigorous statistical analysis, writing defense-ready Chapter 4 reports, and compiling full graduate theses.

---

## 1. Golden Rules for Any AI Agent Working in This Workspace

Every AI agent operating in this repository **MUST** strictly adhere to the following directives:

### Rule 1: Progressive Disclosure (Always Consult SKILL.md First)
- Do **not** guess workflows or procedures.
- When tasked with a job (e.g., translation, data analysis, reference extraction, or thesis assembly), your **first action** must be to read the corresponding skill's `SKILL.md` using `view_file`.
- All domain rules, scripts, and edge-case handling are encapsulated inside `.agents/skills/<skill-name>/`.

### Rule 2: Deterministic Calculation (Zero Hallucinations)
- **NEVER calculate, estimate, or hallucinate statistical numbers, $p$-values, effect sizes, or test statistics in your head.**
- Always execute the bundled Python scripts in `.agents/skills/statistical-data-analyst/scripts/` via the terminal (`run_command`) on the real dataset (`.xlsx`, `.csv`, `.sav`).
- Extract exact values from the script's output JSON/table and paste them directly into reports.

### Rule 3: Strict APA 7th Edition Typography & Formatting
All statistical results (whether in Persian or English) must comply with APA 7th Edition standards:
1. **Italicization**: Latin statistical symbols (*M, SD, t, F, p, r, R², β, B, z, SE*) **must be italicized**. Greek letters (*α, ω, η², χ²*) remain regular unless university guidelines state otherwise.
2. **Decimal Places**:
   - Means, SDs, test statistics ($t, F$), effect sizes: **2 decimal places** (e.g., $M = 24.35$, $t = 3.88$, $d = 0.78$).
   - $p$-values: **Exactly 3 decimal places** (e.g., $p = .014$).
3. **The Leading Zero Rule**:
   - Numbers bounded between 0 and 1 ($p$, $r$, $R^2$, $\eta_p^2$, $\alpha$, $\beta$) **must omit the leading zero**:
     - Correct: $p = .023$, $r = .48$, $\eta_p^2 = .19$
     - Incorrect: $p = 0.023$, $r = 0.48$, $\eta_p^2 = 0.19$
4. **Never Report $p = .000$**:
   - If a software outputs $.000$, report it strictly as **$p < .001$** (یا در فارسی: **۰/۰۰۱ > p**).
5. **APA 7 Table Rules**:
   - Tables must have **zero vertical borders**.
   - Exactly 3 horizontal borders: Top line (solid 0.75 pt), Header bottom underline (solid 0.5 pt), and Table bottom line (solid 0.75 pt).
   - Table titles/captions **above** the table; table notes/asterisks **below** the table.

### Rule 4: Persian Academic Typography & OpenXML Standards
When assembling or editing Persian Word documents (`.docx`):
- **Fonts**:
  - Chapter Titles: `B Titr` 16–18 pt Bold, Centered.
  - Headings 2 & 3: `B Titr` or `B Nazanin Bold` 13–14 pt Bold, Right-aligned.
  - Body Paragraphs: `B Nazanin` or `B Lotus` 13–14 pt Regular, Line Spacing 1.15–1.3, Justified (`WD_ALIGN_PARAGRAPH.JUSTIFY`).
  - Numbers and Statistics: `Times New Roman` 10–11 pt.
- **BiDi & OpenXML Directionality**:
  - Always enforce `<w:bidi w:val="1"/>` on Persian paragraphs and `<w:bidiVisual/>` on tables.
  - Enforce explicit font binding with `<w:rFonts w:ascii="Times New Roman" w:cs="B Nazanin"/>` to prevent font fallback corruption.
  - Maintain Persian half-spaces (نیم‌فاصله: `\u200c`) in compound words (e.g., `می‌شود`, `پیش‌آزمون`, `یافته‌ها`).

---

## 2. Skill Inventory & Activation Matrix

| Skill Name | Path | When to Activate | Core Inputs | Primary Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **`persian-proposal-builder`** | [.agents/skills/persian-proposal-builder/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-proposal-builder) | User requests writing or refining a graduate research proposal (پروپوزال), drafting Chapter 1 or Chapter 3, or calculating sample size. | Research topic, variables, population, instruments | `پروپوزال_طرح_پژوهش.docx` meeting university review council rules. |
| **`psychological-intervention-protocol-builder`** | [.agents/skills/psychological-intervention-protocol-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychological-intervention-protocol-builder) | User requests drafting or compiling an experimental intervention protocol (ACT, CBT, Schema, CFT, MBSR, Positive Psychotherapy) for Chapter 3 or thesis appendix. | Treatment approach, target population, session count | `پروتکل_مداخله.docx` (Ch 3 table + Appendix manual) + `protocol_summary.json`. |
| **`persian-academic-translation`** | [.agents/skills/persian-academic-translation/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-academic-translation) | User requests translating English papers, book chapters, or theoretical frameworks into academic Persian. | English PDF / DOCX / TXT papers | `*_fa.docx` formatted with academic terminology and preserved citations. |
| **`academic-reference-extractor`** | [.agents/skills/academic-reference-extractor/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-reference-extractor) | User needs EndNote/Zotero citations for a translated paper or specific thesis chapter. | Translated text with citations + Master paper bibliography | `.enw` (EndNote), `.ris` (Zotero/Mendeley), and `.txt` (APA list). |
| **`psychometric-scale-resolver`** | [.agents/skills/psychometric-scale-resolver/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver) | User needs to identify questionnaires, extract subscale factor structures, scoring methods, reverse-scoring keys, or score raw survey items. | Raw items (`Q1..Q40`) or Scale query + `Questionnaires.xlsx` | `data_scored.xlsx` + factor subscales + Cronbach's $\alpha$. |
| **`statistical-data-analyst`** | [.agents/skills/statistical-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst) | User provides data (`.sav`, `.xlsx`, `.csv`) and requests analysis, hypothesis testing, or Chapter 4 writing. | Scored dataset + Hypotheses / Research Questions | `فصل چهارم: یافته‌های پژوهش.docx` + `stats_results.json` + APA 7 tables. |
| **`persian-discussion-builder`** | [.agents/skills/persian-discussion-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-discussion-builder) | User requests writing Chapter 5 (بحث و نتیجه‌گیری) interpreting statistical findings against literature. | Chapter 4 results (`stats_results.json`) + Chapter 2 literature | `فصل پنجم: بحث و نتیجه‌گیری.docx` with clinical implications and limitations. |
| **`persian-thesis-builder`** | [.agents/skills/persian-thesis-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-builder) | User wants to compile, merge, format, or assemble all modular thesis parts into a unified university document. | Master `.docx` template + Chapters 1-5 + References + Scales | `Thesis_Compiled.docx` (Complete dissertation meeting university formatting rules). |
| **`irandoc-plagiarism-reducer`** | [.agents/skills/irandoc-plagiarism-reducer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/irandoc-plagiarism-reducer) | User needs to reduce Irandoc (همانندجو) similarity score below 20% or 30%, rewrite flagged literature/discussion text, or eliminate cliches. | Flagged `.docx` or text + Irandoc report | `*_paraphrased.docx` + side-by-side comparison report (`.docx`). |
| **`persian-thesis-revision-assistant`** | [.agents/skills/persian-thesis-revision-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-revision-assistant) | User needs to review, extract, and resolve supervisor/examiner comments and produce the formal response table. | Reviewed `.docx` with comments or feedback text | `جدول_پاسخ_به_نظرات_اساتید.docx` + revised chapters. |
| **`persian-defense-presentation-builder`** | [.agents/skills/persian-defense-presentation-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-defense-presentation-builder) | User requests creating defense slides (.pptx) or preparing for the viva voce oral defense before examiners. | Completed thesis / chapters / stats_results.json | `جلسه_دفاع.pptx` (16:9 widescreen, RTL OpenXML, Iranian typography, and candidate Speaker Notes). |
| **`academic-article-writer`** | [.agents/skills/academic-article-writer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer) | User requests drafting, structuring, or compiling an academic journal article from thesis chapters and project data for ISI/Scopus (English) or ISC (Persian). | Full project artifacts (Proposal, Lit Review, Stats JSON, Ch 5) | `Academic_Article_Manuscript.docx` (English) or `مقاله_علمی_پژوهشی.docx` (Persian) meeting IMRaD & APA 7 standards. |
| **`journal-submission-assistant`** | [.agents/skills/journal-submission-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/journal-submission-assistant) | User needs journal submission collateral (Cover Letter, Title Page with 14 CRediT roles, Highlights <= 85 chars, Declarations) or Point-by-Point Response to Reviewers for Revise & Resubmit. | Manuscript draft, metadata, or reviewer comments | `Cover_Letter.docx`, `Title_Page.docx`, `Highlights.docx`, `Response_to_Reviewers.docx`. |
| **`systematic-review-meta-analyst`** | [.agents/skills/systematic-review-meta-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/systematic-review-meta-analyst) | User conducts or reports systematic review or meta-analysis (PRISMA 2020 & Cochrane RoB 2), pooling Hedges' g, calculating heterogeneity (Q, I², τ²), testing publication bias (Egger), or generating Forest & Funnel plots. | Trial outcome datasets (means, SDs, Ns) or screening numbers | `Meta_Analysis_Report.docx` + `forest_plot.png` + `funnel_plot.png` + `meta_analysis_statistics.json`. |
| **`psychometric-data-simulator`** | [.agents/skills/psychometric-data-simulator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-data-simulator) | User requests synthetic psychometric datasets, Monte Carlo SEM/CFA data generation, multi-item discrete Likert scale responses with reverse items, or randomized clinical trial (RCT) repeated-measures pre/post data. | Structural model parameters ($\mathbf{B}, \mathbf{\Gamma}$), factor loadings ($\mathbf{\Lambda}$), or RCT trial specifications | Multi-sheet Excel workbook (`.xlsx`), CSV dataset, executable R `lavaan` script (`lavaan_syntax.R`), and simulation summary JSON. |
| **`qualitative-data-analyst`** | [.agents/skills/qualitative-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/qualitative-data-analyst) | User provides interview transcripts, focus groups, or qualitative data requiring Braun & Clarke Reflexive Thematic Analysis, Strauss & Corbin Grounded Theory, Paradigmatic Model (6 dimensions), or Chapter 4 qualitative reporting. | Interview transcripts / quotes / coding payload | `فصل_چهارم_یافته‌های_کیفی.docx` + `thematic_matrix.xlsx` + `thematic_network.png` (300 DPI) + `qualitative_summary.json`. |
| **`persian-literature-review-builder`** | [.agents/skills/persian-literature-review-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-literature-review-builder) | User requests drafting, synthesizing, or compiling Chapter 2 (فصل دوم: مبانی نظری و پیشینه پژوهش), translating English theoretical foundations, organizing Iranian/international empirical studies, or building APA 7 summary tables. | Foreign dissertations/theses, variables, empirical study records | `فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx` + `empirical_literature_matrix.xlsx` + `literature_summary.json`. |
| **`psychometric-scale-validator`** | [.agents/skills/psychometric-scale-validator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-validator) | User conducts scale adaptation, standardization, psychometric validation (Lawshe CVR, Waltz-Bausell CVI, EFA, CFA, McDonald's omega, Fornell-Larcker, Item Response Theory [IRT] Graded Response Model [GRM], Infit/Outfit MNSQ, Test Information Function [TIF], Differential Item Functioning [DIF], and ROC cut-offs) or writes psychometric Chapter 4 reports. | Raw survey items, expert panel ratings, scale structure | `فصل_چهارم_ویژگی‌های_روان‌سنجی_و_هنجاریابی.docx` (8 APA 7 tables) + `psychometric_validation_matrix.xlsx` (6 sheets) + dual 300-DPI plots (`scree_and_roc_plots.png`, `irt_tif_and_ccc_plots.png`) + `psychometric_summary.json`. |
| **`academic-suite-orchestrator`** | [.agents/skills/academic-suite-orchestrator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-suite-orchestrator) | User requests running end-to-end multi-stage research workflows, turnkey academic pipelines (empirical thesis, scale validation, qualitative study, meta-analysis, publication preparation), or managing research project dashboards. | Project config JSON or preset (`thesis_empirical`, `scale_validation`, `qualitative_study`, `meta_analysis`, `thesis_to_publication`) | Coordinated stage deliverables + `orchestrator_manifest.json` + `PROJECT_DASHBOARD.md`. |

---

## 3. Data & Artifact Workflow Architecture

The skills are modular and designed to pass standard artifacts between each other across the entire research, defense, and publication lifecycle:

```
[Research Idea / Variables] ──► (persian-proposal-builder)         ──► Proposal / Ch 1 & 3 (.docx)
            │                                                                   │
            ├─────────────────► (psychological-intervention-protocol-builder) ─┤ ──► Ch 3 Table & Protocol Manual
            │                                                                   ▼
[Foreign Theses / Studies]  ──► (persian-literature-review-builder)  ──► Chapter 2 Lit (.docx) + Matrix (.xlsx)
                                                                                │
                                                                                ▼
[In-Text Citations]         ──► (academic-reference-extractor)        ──► .enw / .ris / .txt
                                                                                │
                                                                                ▼
[SEM/CFA Model or RCT Design] ──► (psychometric-data-simulator)       ──► Simulated Data (.xlsx / .csv / lavaan.R)
                                                                                │
                                                                                ▼
[Raw Survey Responses]      ──► (psychometric-scale-resolver)         ──► data_scored.xlsx (Factors + Alphas)
                                                                                │
                                                                                ▼
[Scored Dataset + Hypo]     ──► (statistical-data-analyst)            ──► Chapter 4 Quant (.docx) + stats_results.json
                                                                                │
[Interviews / Focus Groups] ──► (qualitative-data-analyst)            ──► Chapter 4 Qual (.docx) + Matrix (.xlsx) + Diagram (.png)
                                                                                │
                                                                                ▼
[Findings + Lit Review]     ──► (persian-discussion-builder)          ──► Chapter 5 (.docx)
                                                                                │
                                                                                ▼
[All Chapters + Template]   ──► (persian-thesis-builder)              ──► Master Thesis (.docx)
                                                                                │
                                        ┌───────────────────────────────────────┴───────────────────────────────────────┐
                                        ▼                                                                               ▼
[Irandoc Flagged Thesis] ──► (irandoc-plagiarism-reducer)                                       [Completed Thesis & Data]
                                        │                                                                               │
                                        ▼                                                                               ▼
                            فصل_بازنویسی_ایرانداک.docx                                          (academic-article-writer)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Supervisor/Jury Review] ──► (persian-thesis-revision-assistant)                                Journal Manuscript (.docx)
                                        │                                                                               │
                                        ▼                                                                               ▼
                            Response Table (.docx)                                              (journal-submission-assistant)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Defense Session Prep]   ──► (persian-defense-presentation-builder)                             Submission Package (.docx)
                                        │                                                       ├── 1. Cover Letter
                                        ▼                                                       ├── 2. Title Page & CRediT
                            جلسه_دفاع.pptx (RTL OpenXML + Speaker Notes)                        ├── 3. Highlights (<= 85 chars)
                                                                                                └── 4. Response to Reviewers (R&R)
```

---

## 4. Python Environment & CLI Command Reference

### Irandoc Paraphrasing & Similarity Reduction:
```bash
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_کاهش_همانندجویی.docx"
```

### Intervention Protocol Compilation (Chapter 3 Table & Appendix Manual):
```bash
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به دردهای مزمن عضلانی-اسکلتی" \
  --output-docx "پروتکل_مداخله_اکت.docx" \
  --output-json "protocol_act.json"
```

### Defense Presentation Compilation (PowerPoint .pptx):
```bash
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy
```

### Journal Submission Collateral & Rebuttal Package Compilation:
```bash
# English Submission Package (ISI / Scopus Q1-Q4)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload.json" \
  --out-dir "./submission_package_en" \
  --lang en

# Persian Submission Package (علمی-پژوهشی / ISC)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload_fa.json" \
  --out-dir "./submission_package_fa" \
  --lang fa
```

### Systematic Review & Quantitative Meta-Analysis (PRISMA 2020 & Cochrane RoB 2):
```bash
# English Synthesis (Forest Plot, Funnel Plot, APA 7 Manuscript)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload.json" \
  --out-dir "./meta_analysis_output_en" \
  --lang en

# Persian Synthesis (علمی-پژوهشی / ISC)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload_fa.json" \
  --out-dir "./meta_analysis_output_fa" \
  --lang fa
```

### Monte Carlo Psychometric & Statistical Data Simulation (All Research Paradigms):
```bash
# 1. Instant Run via Research Presets (No JSON needed!)
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset hierarchical_regression --out-dir "./sim_reg"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset moderation_model1 --out-dir "./sim_mod"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset factorial_anova --out-dir "./sim_anova"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset mixed_split_plot --out-dir "./sim_rm"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset ancova_trial --out-dir "./sim_rct"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset logistic_diagnosis --out-dir "./sim_logistic"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset efa_battery --out-dir "./sim_efa"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset non_parametric_skewed --out-dir "./sim_np"

# 2. Custom Structural Equation Modeling (SEM) / CFA Mode
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_simulation_payload.json" \
  --out-dir "./simulated_sem_data" \
  --seed 42
```

### Qualitative Data Analysis & Chapter 4 Reporting (Thematic Analysis & Grounded Theory):
```bash
# Reflexive Thematic Analysis (Braun & Clarke 6-phase thematic network)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "thematic_payload.json" \
  --out-dir "./qualitative_output_thematic" \
  --lang fa

# Grounded Theory (Strauss & Corbin 6-dimension paradigmatic model)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "grounded_theory_payload.json" \
  --out-dir "./qualitative_output_gt" \
  --lang fa
```

### Chapter 2 Literature Review & Empirical Matrix Compilation:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json "ch2_payload.json" \
  --out-dir "./chapter2_output" \
  --lang fa
```

### Psychometric Scale Standardization & Validation:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "./psychometric_validation_output" \
  --lang fa
```

### Master Thesis Compilation:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "path/to/template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "Chapter1.docx" \
  --ch2 "Chapter2.docx" \
  --ch3 "Chapter3.docx" \
  --ch4 "Chapter4.docx" \
  --ch5 "Chapter5.docx" \
  --refs "References_Compiled.docx" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire"
```

### Questionnaire Lookup & Factor Scoring:
```bash
# Search Registry (Questionnaires.xlsx) & Google Drive Library
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"

# Inspect Scale Scoring Profile, Subscales, and Reverse Keys
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# Score Raw Survey Item Responses into Factors and Scale Composites
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### Run Automated Statistical Suite:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/data.xlsx" \
  --task auto \
  --config "path/to/config.json" \
  --out "stats_results.json"
```

### Run Specific Statistical Tasks:
- **Score Scale & Factors**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data_raw.xlsx --task score_scale --scale "Connor-Davidson Resilience Scale" --prefix "Q" --out-scored data_scored.xlsx`
- **Descriptives & Normality**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task descriptives --vars "Pre_Test,Post_Test,Resilience"`
- **Scale Reliability ($\alpha$)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task reliability --items "Q1,Q2,Q3,Q4,Q5"`
- **Intervention ANCOVA**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task ancova --dv Post_Test --group Group --covar Pre_Test`
- **Hierarchical Regression**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task regression --dv Outcome --step1 "Age,Gender" --step2 "Resilience,Self_Efficacy"`
- **Bootstrap Mediation (Model 4)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task mediation --x Stress --m Resilience --y Depression --bootstraps 2000`

### Generate APA 7 Persian Word Document:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

### End-to-End Academic Pipeline Orchestration:
```bash
# 1. Run turnkey pipeline preset (thesis_empirical, scale_validation, qualitative_study, meta_analysis, thesis_to_publication)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset thesis_empirical \
  --out-dir "./my_thesis_project"

# 2. Dry-run validation (inspect execution plan and dependency DAG without running)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset scale_validation \
  --dry-run

# 3. Custom project configuration with custom step payloads
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --config "project_config.json" \
  --out-dir "./custom_academic_study"

# 4. Granular checkpointing & step control
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset thesis_empirical \
  --out-dir "./my_thesis_project" \
  --resume-from statistics

python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset thesis_empirical \
  --out-dir "./my_thesis_project" \
  --step discussion
```

---

## 5. Defense Committee Quality Checklist

Before delivering any Chapter 4 or statistical output to a student, verify:
- [ ] Normality (Shapiro-Wilk) and Homogeneity of Variance (Levene) were formally checked and reported.
- [ ] For experimental studies, ANCOVA slope homogeneity ($Group \times Pretest$, $p > .05$) was tested.
- [ ] For mediation models, 95% bootstrap confidence intervals were reported (not Sobel test).
- [ ] All table numbers in the narrative match the table captions (`جدول ۱-۴`, `جدول ۲-۴`).
- [ ] All tables contain only 3 horizontal lines (no vertical lines).
- [ ] All $p$-values omit the leading zero ($p = .012$, not $p = 0.012$).
- [ ] Every hypothesis has an unambiguous concluding sentence affirming or rejecting it.

---

## 6. Questionnaire Registry & Psychometric Scale Directives

When preparing datasets, writing research proposals, or drafting methodology chapters:
1. **3-Tier Hierarchy**:
   - **Tier 1 (Project Folder)**: Prioritize client-provided questionnaires and project files.
   - **Tier 2 (Excel Registry - `Questionnaires.xlsx`)**: 4,880 rows mapping English/Persian names, subscales, items, Likert anchors, theoretical means, and reverse items.
   - **Tier 3 (Google Drive Library - `Pending Works/Questionnaire`)**: 2,206 original `.pdf`, `.docx`, and `.doc` instruments for item texts and scoring manuals.
2. **Reverse Scoring Formula**:
   - Always transform negatively keyed items using $Item_{\text{rev}} = (Min + Max) - Item$ before computing subscale sums, means, or Cronbach's alpha.
3. **Subscale & Total Composite Reporting**:
   - Report Cronbach's $\alpha$ for each subscale and total scale separately.
   - Confirm theoretical score ranges and midpoints ($Mean_{\text{theor}} = \frac{Min + Max}{2}$) in the narrative.

