# Antigravity Academic Skills Suite

An autonomous, modular AI skill suite designed for **Google Antigravity** and agentic pair-programmers. Specialized for **academic consulting, psychometric analysis, and university thesis preparation** (specifically for Master's and Doctoral students in Psychology, Counseling, and Behavioral Sciences).

---

## 🌟 Overview & Key Capabilities

This repository equips Antigravity with dedicated, professional-grade capabilities to deliver high-stakes academic projects across the entire research lifecycle:

1. **Research Proposal ([persian-proposal-builder](.agents/skills/persian-proposal-builder/))**:
   Formulates graduate research proposals, problem statements (بیان مسئله) via the inverted-triangle model, directional hypotheses, definitions, G*Power sample sizes, and Chapters 1 & 3.
2. **Intervention Protocol & Manual Builder ([psychological-intervention-protocol-builder](.agents/skills/psychological-intervention-protocol-builder/))**:
   Designs and compiles standardized clinical and educational intervention protocols (ACT, CBT, Schema Therapy, CFT, MBSR, Positive Psychotherapy), generating Chapter 3 APA 7 session summary tables and comprehensive Appendix session-by-session clinical manuals in Word (`.docx`) and structured JSON.
3. **Academic Translation ([persian-academic-translation](.agents/skills/persian-academic-translation/))**:
   Translates English journal papers into formal academic Persian with specialized psychological terminology and proper half-space typography (نیم‌فاصله) for Chapter 2.
4. **Reference Extraction ([academic-reference-extractor](.agents/skills/academic-reference-extractor/))**:
   Extracts in-text citations from translated sections and generates clean EndNote (`.enw`), RIS (`.ris`), and APA 7 (`.txt`) citation libraries.
5. **Psychometric Scale Resolution ([psychometric-scale-resolver](.agents/skills/psychometric-scale-resolver/))**:
   Specialized psychometric instrument engine executing 3-tier search (`Questionnaires.xlsx`, local project docs, cloud drive archive), item-to-factor mapping, reverse-scoring algebra, subscale aggregation, and Cronbach's alpha verification.
6. **Statistical Analysis & Chapter 4 ([statistical-data-analyst](.agents/skills/statistical-data-analyst/))**:
   Deterministic calculation engine (`pandas`, `scipy`, `statsmodels`) that ingests SPSS (`.sav`), Excel (`.xlsx`), and CSV data, verifies assumptions, tests hypotheses (ANCOVA, Hierarchical Regression, Mediation with 5,000 bootstrap resamples), and outputs publication-ready APA 7 Persian Word (`.docx`) tables and Chapter 4 reports.
7. **Discussion & Synthesis ([persian-discussion-builder](.agents/skills/persian-discussion-builder/))**:
   Synthesizes Chapter 4 statistical findings with Chapter 2 literature to draft Chapter 5 (بحث و نتیجه‌گیری) using theoretical mechanisms, clinical implications, limitations, and recommendations.
8. **Master Thesis Assembly ([persian-thesis-builder](.agents/skills/persian-thesis-builder/))**:
   Cross-platform OpenXML compilation engine (`compile_full_thesis.py`) that fuses institutional Master Word templates (`.docx`) with modular chapter drafts, unified references, dynamic questionnaire appendices, and Persian typography (*B Titr*, *B Nazanin*, *B Lotus*).
9. **Irandoc Plagiarism Reducer ([irandoc-plagiarism-reducer](.agents/skills/irandoc-plagiarism-reducer/))**:
   Executes deep syntactic clause inversion, thematic literature synthesis, and scientific synonym substitution to lower Irandoc (همانندجو / سمیم‌نور) similarity percentages below university defense thresholds (typically < 20% or < 30%) while preserving APA 7 citations and نیم‌فاصله.
10. **Supervisor Revision Assistant ([persian-thesis-revision-assistant](.agents/skills/persian-thesis-revision-assistant/))**:
   Extracts Word comments and margin annotations from reviewed drafts, triages requested edits, applies targeted revisions, and generates the official Point-by-Point Response Table (`جدول_پاسخ_به_نظرات_اساتید.docx`).
11. **Master Thesis Defense Presentation ([persian-defense-presentation-builder](.agents/skills/persian-defense-presentation-builder/))**:
   Synthesizes thesis chapters, statistical findings, and discussion models into a defense-ready 16:9 widescreen PowerPoint presentation (`.pptx`) with native RTL OpenXML formatting, authentic Iranian academic typography (*B Titr*, *B Nazanin*), visual card containers, and comprehensive oral candidate Speaker Notes (متن گفتار دانشجو).
12. **Academic Article Writer ([academic-article-writer](.agents/skills/academic-article-writer/))**:
   Synthesizes all heterogeneous project artifacts (theses, Chapter 4 statistical data, translated literature, and psychometric scales) into high-impact, publication-grade academic journal articles adhering to international peer-review standards (IMRaD, APA 7th Edition, JARS) for both International English journals (ISI / Scopus Q1/Q2) and Iranian Scientific-Research journals (علمی-پژوهشی / ISC).
13. **Journal Submission Assistant ([journal-submission-assistant](.agents/skills/journal-submission-assistant/))**:
   Packages research papers into publisher-compliant submission bundles for international (Elsevier, Springer, Wiley, MDPI) and Iranian ISC journals: formal Cover Letters to the Editor-in-Chief, Title Pages with standard 14 CRediT authorship taxonomy roles and ethical declarations, Highlights strictly validated to $\le 85$ characters, and APA 7 Point-by-Point Response to Reviewers rebuttal tables for Revise & Resubmit (R&R) decisions.
14. **Systematic Review & Meta-Analyst ([systematic-review-meta-analyst](.agents/skills/systematic-review-meta-analyst/))**:
   Conducts and synthesizes gold-standard systematic reviews and quantitative meta-analyses adhering to PRISMA 2020 and Cochrane Risk of Bias (RoB 2) standards: multi-database Boolean search strategies, PRISMA study flow tracking, deterministic Hedges' $g$ effect sizes, Fixed-Effect & DerSimonian-Laird Random-Effects pooling, heterogeneity quantification ($Q$, $I^2$, $\tau^2$), Egger's publication bias test, and high-resolution Forest and Funnel plots.
15. **Psychometric Data Simulator ([psychometric-data-simulator](.agents/skills/psychometric-data-simulator/))**:
   Generates realistic synthetic datasets using Monte Carlo simulation algorithms for Structural Equation Modeling (SEM), Confirmatory Factor Analysis (CFA), multi-item discrete Likert response scales (1–5, 1–7, 1–10) with indicator factor loadings ($\lambda$), measurement noise ($\theta$), and reverse items, and Randomized Clinical Trials (RCT) with repeated-measures pretest-posttest-followup designs. Exports multi-sheet Excel workbooks (`.xlsx`), CSV datasets, executable R `lavaan` scripts, and fit summaries.
16. **Qualitative Data Analysis & Chapter 4 ([qualitative-data-analyst](.agents/skills/qualitative-data-analyst/))**:
   End-to-end qualitative analysis and reporting engine supporting **Braun & Clarke (2006, 2019, 2021) Reflexive Thematic Analysis** (6-phase pipeline, 3-tier theme hierarchy: Basic, Organizing, Global) and **Strauss & Corbin (1990, 1998) Systematic Grounded Theory** (open, axial, selective coding, and 6-dimension Paradigmatic Model). Computes inter-coder reliability (Holsti's PAO, Cohen's Kappa), conducts Lincoln & Guba (1985) trustworthiness audits, renders 300-DPI thematic network diagrams (`thematic_network.png`), exports 5-sheet coding matrices (`thematic_matrix.xlsx`), and compiles defense-ready Persian/English Chapter 4 Word reports (`.docx`).
17. **Literature Review & Chapter 2 Synthesis ([persian-literature-review-builder](.agents/skills/persian-literature-review-builder/))**:
   Translates and integrates English theoretical foundations from foreign dissertations and literature (strictly avoiding copying from Persian theses to prevent cliches and high Irandoc similarity), organizes recent Iranian (Magiran, SID, ISC) and international (Scopus, PubMed, WoS) empirical literature using a 5-part reporting formula, embeds APA 7 borderless empirical summary tables, articulates research gaps and conceptual frameworks, and compiles defense-ready Word (`.docx`) and multi-sheet Excel workbooks.
18. **Psychometric Scale Validator ([psychometric-scale-validator](.agents/skills/psychometric-scale-validator/))**:
   End-to-end scale standardization, Classical Test Theory (CTT), and modern Item Response Theory (IRT) engine: verification of WHO/ITC translation protocols, quantitative Lawshe (1975) CVR against critical panel thresholds, Waltz & Bausell / Lynn (1986) CVI ($I\text{-}CVI$, $S\text{-}CVI/\text{Ave}$), Item Impact Scores, Exploratory Factor Analysis (EFA: KMO, Bartlett, Scree plot, Promax/Varimax), Confirmatory Factor Analysis (CFA: $\chi^2/df$, CFI, TLI, RMSEA, SRMR), Fornell & Larcker Convergent (AVE $\ge 0.50$, CR $\ge 0.70$) and Discriminant Validity, APA 7th Edition McDonald's Omega ($\omega$) and Cronbach's Alpha ($\alpha$), Test-Retest ICC, Item Response Theory (IRT) Graded Response Model (GRM: discrimination $a$, category thresholds $b_1-b_4$, Infit/Outfit MNSQ, Test Information Function TIF, and Differential Item Functioning DIF), Norm score conversions (Z, T, Percentiles), and ROC Curve clinical cut-off determination. Compiles defense-ready Chapter 4 Word reports (`.docx` with 8 APA 7 tables), 6-sheet Excel validation matrices, and dual 300-DPI visual plots.
19. **Master Research Pipeline Orchestrator ([academic-suite-orchestrator](.agents/skills/academic-suite-orchestrator/))**:
   Unified research orchestration engine that executes multi-stage, inter-skill pipelines across all 18 skills with 5 turnkey presets (`thesis_empirical`, `scale_validation`, `qualitative_study`, `meta_analysis`, `thesis_to_publication`), automatic artifact handoffs, dependency DAG validation (`--dry-run`), step-level resumption (`--resume-from`), execution manifest generation (`orchestrator_manifest.json`), and comprehensive Markdown project dashboards (`PROJECT_DASHBOARD.md`).
20. **Thesis Integrity & Cross-Chapter Forensic Auditor ([thesis-integrity-auditor](.agents/skills/thesis-integrity-auditor/))**:
   Automated academic jury, forensic proofreader, and cross-chapter consistency verification engine: audits hypothesis-result-discussion alignment (Ch 1 $\leftrightarrow$ Ch 4 $\leftrightarrow$ Ch 5), validates methodology sample sizes and degrees of freedom ($t$-test, ANOVA, ANCOVA, regression $df$), executes bidirectional citation reconciliation (orphaned in-text citations vs ghost bibliography entries, year mismatches), and enforces APA 7th Edition statistical formatting rules (leading zeroes, $p = .000$, effect sizes). Generates publication-grade audit Word reports (`.docx`), 5-sheet citation reconciliation workbooks (`.xlsx`), and machine-readable JSON summaries.

---

## 📁 Repository Structure

```text
AcademicSuite/
├── .agents/
│   └── skills/
│       ├── academic-article-writer/            # ISI/Scopus & ISC journal article compiler
│       ├── academic-reference-extractor/       # EndNote, RIS, APA citation extractor
│       ├── academic-suite-orchestrator/        # Master multi-stage pipeline & DAG workflow orchestrator
│       ├── irandoc-plagiarism-reducer/         # Irandoc similarity reduction & academic paraphraser
│       ├── journal-submission-assistant/       # Submission collateral, CRediT taxonomy & rebuttal tables
│       ├── persian-academic-translation/       # Psychology translation & terminology engine
│       ├── persian-defense-presentation-builder/ # Defense slide deck (.pptx) & speaker notes compiler
│       ├── persian-discussion-builder/         # Chapter 5 discussion & theoretical explanation
│       ├── persian-literature-review-builder/  # Chapter 2 theoretical & empirical literature synthesizer
│       ├── persian-proposal-builder/           # Research proposal & methodology builder
│       ├── persian-thesis-builder/             # Generic cross-platform thesis compiler
│       ├── persian-thesis-revision-assistant/  # Word comment extractor & response table builder
│       ├── psychological-intervention-protocol-builder/ # Evidence-based treatment manual & Ch 3 table builder
│       ├── psychometric-data-simulator/        # Monte Carlo SEM, Likert scale & RCT data simulator
│       ├── psychometric-scale-resolver/        # Questionnaire resolution, scoring & psychometrics
│       ├── psychometric-scale-validator/       # Scale standardization, EFA/CFA, IRT (GRM, TIF, DIF) & ROC
│       ├── qualitative-data-analyst/           # Thematic analysis, grounded theory & Ch 4 qualitative reporter
│       ├── statistical-data-analyst/           # Statistical testing & Chapter 4 builder
│       ├── systematic-review-meta-analyst/     # PRISMA 2020 & Cochrane meta-analysis engine
│       └── thesis-integrity-auditor/           # Cross-chapter integrity audit, hypothesis & citation reconciler
├── AGENTS.md                                   # Canonical agent behavioral rules & directives
├── SETUP_GUIDE.md                              # Migration guide for setting up on a new device
├── Questionnaires.xlsx                         # Master index of 4,800+ psychological instruments
├── requirements.txt                            # Python dependencies
└── README.md                                   # Project documentation
```

---

## 🚀 Quick Setup on a New Device

### 1. Prerequisites
- **Python 3.10+**
- **Git**
- **Google Antigravity IDE** or an agentic coding assistant
- Standard Iranian academic Persian fonts installed on the OS:
  - *B Nazanin*
  - *B Titr*
  - *B Lotus*

### 2. Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📖 Usage Quick-Start

### Questionnaire Factor Scoring & Psychometric Resolution
Query `Questionnaires.xlsx` and the Google Drive library or score raw item datasets:
```bash
# 1. Search questionnaire registry and Google Drive library
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"

# 2. Inspect scoring keys, subscales, and reverse items
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# 3. Score raw survey responses (applies reverse scoring, subscale sums/means, and alpha)
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### Statistical Analysis & Chapter 4 Generation
Given a student's dataset (`data.xlsx` or `data.sav`):
```bash
# 1. Run statistical suite (Normality, ANCOVA, Regression, Mediation)
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "data.xlsx" \
  --task auto \
  --config "study_config.json" \
  --out "stats_results.json"

# 2. Generate APA 7th Edition Word Document (Chapter 4)
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

### Master Thesis Compilation
Compile modular chapters, dynamic questionnaire appendices, and references into an institutional Word template:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "university_template.docx" \
  --output "رساله_کامل.docx" \
  --title "اثربخشی درمان مبتنی بر پذیرش و تعهد بر انعطاف‌پذیری روان‌شناختی" \
  --author "دانشجو: نام و نام خانوادگی" \
  --supervisor "استاد راهنما: دکتر ..." \
  --ch1 "فصل_اول.docx" \
  --ch2 "فصل_دوم.docx" \
  --ch3 "فصل_سوم.docx" \
  --ch4 "فصل_چهارم.docx" \
  --ch5 "فصل_پنجم.docx" \
  --refs "منابع_یکپارچه.txt" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire"
```

### Master Thesis Defense Presentation (PowerPoint .pptx)
Generate a defense slide deck (16:9 widescreen, RTL OpenXML, B Titr/Nazanin) with candidate oral speaker notes:
```bash
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy
```

### Academic Article Compilation (ISI/Scopus or ISC)
Given structured article data synthesized from project files:
```bash
# English Article (ISI / Scopus)
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload.json" \
  --out "Academic_Article_Manuscript.docx" \
  --lang en

# Persian Article (علمی-پژوهشی / ISC)
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload.json" \
  --out "مقاله_علمی_پژوهشی.docx" \
  --lang fa
```

### Intervention Protocol Compilation (Chapter 3 Table & Appendix Manual)
Generate standardized session summary tables for Chapter 3 and comprehensive Appendix clinical manuals:
```bash
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به دردهای مزمن عضلانی-اسکلتی" \
  --output-docx "پروتکل_مداخله_اکت.docx" \
  --output-json "protocol_act.json"
```

### Irandoc Paraphrasing & Similarity Reduction
Rewrite high-similarity literature and discussion chapters to reduce Irandoc scores (< 20%) while preserving citations:
```bash
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_کاهش_همانندجویی.docx"
```

### Journal Submission Collateral & Rebuttal Compilation
Generate formal Cover Letters, Title Pages with standard 14 CRediT authorship taxonomy roles, verified Highlights ($\le 85$ chars), and Point-by-Point Response to Reviewers rebuttal tables:
```bash
# Compile English Submission Bundle (Cover Letter, Title Page, Highlights, Rebuttal)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload.json" \
  --out-dir "./submission_package_en" \
  --lang en

# Compile Persian Submission Bundle (علمی-پژوهشی / ISC)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload_fa.json" \
  --out-dir "./submission_package_fa" \
  --lang fa
```

### Systematic Review & Quantitative Meta-Analysis (PRISMA 2020)
Pool clinical trial effect sizes, assess Cochrane RoB 2, test publication bias, and render high-res Forest and Funnel plots:
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

### Monte Carlo Psychometric & Statistical Data Simulation
Generate realistic synthetic datasets across any quantitative research design with one command or custom JSON:
```bash
# Instant Run via Research Presets (No JSON file required):
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset hierarchical_regression --out-dir "./sim_reg"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset moderation_model1 --out-dir "./sim_mod"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset factorial_anova --out-dir "./sim_anova"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset mixed_split_plot --out-dir "./sim_rm"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset ancova_trial --out-dir "./sim_rct"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset logistic_diagnosis --out-dir "./sim_logistic"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset efa_battery --out-dir "./sim_efa"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset non_parametric_skewed --out-dir "./sim_np"

# Custom Structural Equation Modeling (SEM) / CFA Simulation:
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_payload.json" \
  --out-dir "./sim_sem_output" \
  --seed 42
```

### Qualitative Data Analysis & Chapter 4 Compilation
Analyze qualitative interview transcripts or coding matrices and compile defense-ready Chapter 4 reports:
```bash
# 1. Reflexive Thematic Analysis (Braun & Clarke 3-tier hierarchy & network diagram)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "thematic_payload.json" \
  --out-dir "./qualitative_output_thematic" \
  --lang fa

# 2. Grounded Theory (Strauss & Corbin 6-dimension paradigmatic model)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "grounded_theory_payload.json" \
  --out-dir "./qualitative_output_gt" \
  --lang fa
```

### Chapter 2 Literature Review & Empirical Matrix Compilation
Synthesize foreign thesis theoretical chapters, organize Iranian/international empirical studies, and compile defense-ready Chapter 2 Word documents:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json "ch2_payload.json" \
  --out-dir "./chapter2_output" \
  --lang fa
```

### Psychometric Scale Standardization & Validation
Conduct scale cultural adaptation, Lawshe CVR, Waltz-Bausell CVI, EFA/CFA, McDonald's $\omega$, and ROC clinical cut-off determination:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "./validation_output" \
  --lang fa
```

### End-to-End Academic Pipeline Orchestration
Coordinate and execute multi-stage research pipelines with turnkey presets, artifact handoffs, and executive project dashboards:
```bash
# 1. Run complete empirical thesis pipeline (Proposal -> Simulation -> Stats -> Ch 5 -> Full Thesis -> Defense Slides)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset thesis_empirical \
  --out-dir "./my_thesis_study"

# 2. Dry-run pipeline DAG validation
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset scale_validation \
  --dry-run

# 3. Resume from a specific pipeline checkpoint
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --preset thesis_empirical \
  --out-dir "./my_thesis_study" \
  --resume-from statistics
```

### Thesis Integrity & Cross-Chapter Forensic Audit
Execute an automated mock jury check on full theses to verify hypothesis-result alignment, degrees of freedom, and citation reconciliation:
```bash
# 1. Standard Persian Dissertation Audit Report (.docx, .xlsx, .json)
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --lang fa

# 2. English / International Journal Thesis Mode
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results_en" \
  --lang en
```

### In-Agent Prompt Examples
Simply instruct your Antigravity agent:
- *"Audit my completed thesis: verify whether all Chapter 1 hypotheses are tested in Chapter 4 and discussed in Chapter 5."*
- *"Check whether my degrees of freedom in ANCOVA and regression tables match the total sample size reported in Chapter 3."*
- *"Reconcile all in-text citations against the reference list and flag any orphaned citations or ghost bibliography entries."*
- *"Verify APA 7 statistical formatting compliance across my dissertation chapters (leading zeros, p-values, effect sizes)."*
- *"Run the full empirical thesis pipeline from proposal to defense presentation slides for a study on ACT therapy and chronic pain."*
- *"Execute the scale validation pipeline to standardize the Cognitive Flexibility Inventory (CFI) and generate the journal submission package."*
- *"Run the qualitative study pipeline to analyze 15 interview transcripts on marital resilience and build Chapter 4, Chapter 5, and the master thesis."*
- *"Execute the PRISMA meta-analysis pipeline on mindfulness trials and package the manuscript for Elsevier submission."*
- *"Rewrite Chapter 2 to reduce Irandoc similarity below 15% while keeping all citations intact."*
- *"Generate an 8-session ACT intervention protocol and Chapter 3 table for chronic pain patients."*
- *"Find the subscales, scoring method, and questions for Connor-Davidson Resilience Scale."*
- *"Score this raw survey file using the Penn State Worry Questionnaire keys and reverse items."*
- *"Analyze this SPSS dataset and write Chapter 4 in Persian Word format."*
- *"Translate this psychological paper for Chapter 2 and preserve in-text citations."*
- *"Extract EndNote citations for all references in Chapter 2."*
- *"Compile the whole thesis into the university master template with questionnaire appendices."*
- *"Review supervisor margin comments on my thesis and generate the response table."*
- *"Generate defense presentation slides (.pptx) with candidate speaker notes from my completed thesis."*
- *"Synthesize my thesis and Chapter 4 dataset into an ISI journal article in English."*
- *"Draft an ISC scientific-research article in Persian from this completed thesis."*
- *"Prepare the journal submission collateral package (Cover Letter, Title Page with CRediT roles, and Highlights) for Elsevier."*
- *"Draft a point-by-point response to reviewers rebuttal table for my revised manuscript."*
- *"Conduct a quantitative meta-analysis on these 10 RCTs and generate the PRISMA 2020 flowchart, Forest plot, and Funnel plot."*
- *"Evaluate the risk of bias using Cochrane RoB 2 and run Egger's regression test for publication bias."*
- *"Simulate a 300-subject SEM dataset testing mediation between Psychological Flexibility, Pain Acceptance, and Quality of Life with 5-point Likert items."*
- *"Generate an RCT dataset for 60 subjects comparing ACT vs Control across Pre, Post, and 3-month Follow-up with target Cohen's d = 0.8."*
- *"Analyze these 15 interview transcripts using Braun & Clarke Reflexive Thematic Analysis and generate the thematic network diagram and Chapter 4 report in Persian."*
- *"Build a Strauss & Corbin Grounded Theory paradigmatic model for marital forgiveness and output the 5-sheet Excel matrix and Word dissertation chapter."*
- *"Calculate Holsti's inter-coder reliability index and Cohen's Kappa between two independent raters for my qualitative coding."*
- *"Compile Chapter 2 from these translated foreign dissertation sections, summarize 6 Iranian and 6 foreign empirical studies, and generate the APA 7 summary table in Word."*
- *"Extract the research gap and conceptual model for my thesis on Internet Gaming Disorder and Ego Strength in Chapter 2."*
- *"Standardize this 20-item scale: calculate Lawshe CVR, Waltz-Bausell CVI, run EFA/CFA, compute McDonald's omega and test-retest ICC, and determine clinical cut-off using ROC curve analysis."*
- *"Write Chapter 4 for my questionnaire standardization thesis in Persian Word format with all 7 APA 7 tables and dual Scree/ROC plots."*

---

## 📜 License & Maintenance
Maintained by Saber Ghaderi. Tailored for graduate academic consulting and university research workflows.
