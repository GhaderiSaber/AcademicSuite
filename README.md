# Antigravity Academic Skills Suite

An autonomous, modular AI skill suite designed for **Google Antigravity** and agentic pair-programmers. Specialized for **academic consulting, psychometric analysis, and university thesis preparation** (specifically for Master's and Doctoral students in Psychology, Counseling, and Behavioral Sciences).

---

## 🌟 Overview & Key Capabilities

This repository equips Antigravity with dedicated, professional-grade capabilities to deliver high-stakes academic projects:

1. **Academic Translation ([persian-academic-translation](.agents/skills/persian-academic-translation/))**:
   Translates English journal papers into formal academic Persian with specialized psychological terminology and proper half-space typography (نیم‌فاصله).
2. **Reference Extraction ([academic-reference-extractor](.agents/skills/academic-reference-extractor/))**:
   Extracts in-text citations from translated sections and generates clean EndNote (`.enw`), RIS (`.ris`), and APA 7 (`.txt`) citation libraries.
3. **Statistical Analysis & Chapter 4 ([statistical-data-analyst](.agents/skills/statistical-data-analyst/))**:
   Deterministic calculation engine (`pandas`, `scipy`, `statsmodels`) that ingests SPSS (`.sav`), Excel (`.xlsx`), and CSV data, verifies assumptions, tests hypotheses (ANCOVA, Hierarchical Regression, Mediation with 5,000 bootstrap resamples), and outputs publication-ready APA 7 Persian Word (`.docx`) tables and Chapter 4 reports.
4. **Master Thesis Assembly ([persian-thesis-builder](.agents/skills/persian-thesis-builder/))**:
   Fuses an institutional Master Word Template (`.docx`) with modular research components into a single, flawlessly formatted thesis meeting Iranian graduate university OpenXML formatting rules.

---

## 📁 Repository Structure

```text
AntigravitySkills/
├── .agents/
│   └── skills/
│       ├── academic-reference-extractor/   # EndNote, RIS, APA citation extractor
│       ├── persian-academic-translation/   # Psychology translation & terminology engine
│       ├── persian-thesis-builder/         # Master Word template thesis compiler
│       └── statistical-data-analyst/       # Statistical testing & Chapter 4 builder
│           ├── references/                 # Statistical decision trees & APA 7 guide
│           └── scripts/                    # psychology_stats.py & generate_apa_docx.py
├── AGENTS.md                               # Canonical agent behavioral rules & directives
├── SETUP_GUIDE.md                          # Migration guide for setting up on a new device
├── requirements.txt                        # Python dependencies
└── README.md                               # Project documentation
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

### In-Agent Prompt Examples
Simply instruct your Antigravity agent:
- *"Analyze this SPSS dataset and write Chapter 4 in Persian Word format."*
- *"Translate this psychological paper for Chapter 2 and preserve in-text citations."*
- *"Extract EndNote citations for all references in Chapter 2."*
- *"Compile the whole thesis into the university master template."*

---

## 📜 License & Maintenance
Maintained by Saber Ghaderi. Tailored for graduate academic consulting and university research workflows.
