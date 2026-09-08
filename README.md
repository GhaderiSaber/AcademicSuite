# Antigravity Academic Skills Suite

An autonomous, modular AI skill suite designed for **Google Antigravity** and agentic pair-programmers. Specialized for **academic consulting, psychometric analysis, and university thesis preparation** (specifically for Master's and Doctoral students in Psychology, Counseling, and Behavioral Sciences).

---

## 🌟 Overview & Key Capabilities

This repository equips Antigravity with dedicated, professional-grade capabilities to deliver high-stakes academic projects across the entire research lifecycle:

1. **Research Proposal ([persian-proposal-builder](.agents/skills/persian-proposal-builder/))**:
   Formulates graduate research proposals, problem statements (بیان مسئله) via the inverted-triangle model, directional hypotheses, definitions, G*Power sample sizes, and Chapters 1 & 3.
2. **Academic Translation ([persian-academic-translation](.agents/skills/persian-academic-translation/))**:
   Translates English journal papers into formal academic Persian with specialized psychological terminology and proper half-space typography (نیم‌فاصله) for Chapter 2.
3. **Reference Extraction ([academic-reference-extractor](.agents/skills/academic-reference-extractor/))**:
   Extracts in-text citations from translated sections and generates clean EndNote (`.enw`), RIS (`.ris`), and APA 7 (`.txt`) citation libraries.
4. **Statistical Analysis & Chapter 4 ([statistical-data-analyst](.agents/skills/statistical-data-analyst/))**:
   Deterministic calculation engine (`pandas`, `scipy`, `statsmodels`) that ingests SPSS (`.sav`), Excel (`.xlsx`), and CSV data, verifies assumptions, tests hypotheses (ANCOVA, Hierarchical Regression, Mediation with 5,000 bootstrap resamples), and outputs publication-ready APA 7 Persian Word (`.docx`) tables and Chapter 4 reports.
5. **Discussion & Synthesis ([persian-discussion-builder](.agents/skills/persian-discussion-builder/))**:
   Synthesizes Chapter 4 statistical findings with Chapter 2 literature to draft Chapter 5 (بحث و نتیجه‌گیری) using theoretical mechanisms, clinical implications, limitations, and recommendations.
6. **Master Thesis Assembly ([persian-thesis-builder](.agents/skills/persian-thesis-builder/))**:
   Fuses an institutional Master Word Template (`.docx`) with modular research components into a single, flawlessly formatted thesis meeting Iranian graduate university OpenXML formatting rules.
7. **Supervisor Revision Assistant ([persian-thesis-revision-assistant](.agents/skills/persian-thesis-revision-assistant/))**:
   Extracts Word comments and margin annotations from reviewed drafts, triages requested edits, applies targeted revisions, and generates the official Point-by-Point Response Table (`جدول_پاسخ_به_نظرات_اساتید.docx`).
8. **Academic Article Writer ([academic-article-writer](.agents/skills/academic-article-writer/))**:
   Synthesizes all heterogeneous project artifacts (theses, Chapter 4 statistical data, translated literature, and psychometric scales) into high-impact, publication-grade academic journal articles adhering to international peer-review standards (IMRaD, APA 7th Edition, JARS) for both International English journals (ISI / Scopus Q1/Q2) and Iranian Scientific-Research journals (علمی-پژوهشی / ISC).

---

## 📁 Repository Structure

```text
AcademicSuite/
├── .agents/
│   └── skills/
│       ├── academic-article-writer/            # ISI/Scopus & ISC journal article compiler
│       ├── academic-reference-extractor/       # EndNote, RIS, APA citation extractor
│       ├── persian-academic-translation/       # Psychology translation & terminology engine
│       ├── persian-discussion-builder/         # Chapter 5 discussion & theoretical explanation
│       ├── persian-proposal-builder/           # Research proposal & methodology builder
│       ├── persian-thesis-builder/             # Master Word template thesis compiler
│       ├── persian-thesis-revision-assistant/  # Word comment extractor & response table builder
│       └── statistical-data-analyst/           # Statistical testing & Chapter 4 builder
├── AGENTS.md                                   # Canonical agent behavioral rules & directives
├── SETUP_GUIDE.md                              # Migration guide for setting up on a new device
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

### Questionnaire Factor Scoring & Psychometric Resolution
Query `Questionnaires.xlsx` and the Google Drive library or score raw item datasets:
```bash
# 1. Search questionnaire registry and Google Drive library
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py search "Connor-Davidson"

# 2. Inspect scoring keys, subscales, and reverse items
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# 3. Score raw survey responses (applies reverse scoring, subscale sums/means, and alpha)
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### In-Agent Prompt Examples
Simply instruct your Antigravity agent:
- *"Score this raw survey file using the Penn State Worry Questionnaire keys and reverse items."*
- *"Find the subscales, scoring method, and questions for Connor-Davidson Resilience Scale."*
- *"Analyze this SPSS dataset and write Chapter 4 in Persian Word format."*
- *"Translate this psychological paper for Chapter 2 and preserve in-text citations."*
- *"Extract EndNote citations for all references in Chapter 2."*
- *"Compile the whole thesis into the university master template."*
- *"Review supervisor margin comments on my thesis and generate the response table."*
- *"Synthesize my thesis and Chapter 4 dataset into an ISI journal article in English."*
- *"Draft an ISC scientific-research article in Persian from this completed thesis."*

---

## 📜 License & Maintenance
Maintained by Saber Ghaderi. Tailored for graduate academic consulting and university research workflows.
