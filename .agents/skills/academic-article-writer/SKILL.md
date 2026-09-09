---
name: academic-article-writer
description: >-
  Expert academic journal article drafting and compilation skill for psychology, behavioral sciences, and social sciences.
  Harvests heterogeneous research artifacts from the project folder (full thesis, proposal, translated literature,
  SPSS/Excel statistical results, psychometric scales, and Questionnaires.xlsx) to compose publication-ready,
  high-impact peer-reviewed journal manuscripts adhering to international IMRaD and APA 7th Edition standards
  for both International English journals (ISI, Scopus Q1/Q2, Web of Science) and Iranian Scientific-Research
  journals (علمی-پژوهشی / ISC).
---

# Academic Journal Article Writer Skill (نگارش و تدوین مقالات علمی-پژوهشی و ISI)

This skill empowers Antigravity to act as an elite academic author and peer-reviewed journal strategist. It synthesizes modular thesis chapters, translated theoretical literature, and statistical findings into **high-impact, publication-grade academic journal articles (15–25 pages, 4,500–6,500 words)**.

It adheres strictly to **IMRaD architecture (Introduction, Method, Results, and Discussion)**, **APA 7th Edition**, and **JARS (Journal Article Reporting Standards)**, supporting both **International English journals (ISI / Scopus)** and **Iranian Scientific-Research journals (علمی-پژوهشی / ISC)**.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user asks to **write a journal article (مقاله پژوهشی / مقاله ISI / ISC)** based on a completed thesis, dissertation, or raw project data.
2. The user has **Chapter 4 statistical data (`stats_results.json`)** and source literature and wants to compose an empirical research paper.
3. The user needs to condense an exhaustive 150-page thesis into a high-density, peer-review-ready manuscript.
4. The user needs a structured abstract (Background, Objective, Method, Results, Conclusion), MeSH keywords, or APA 7 borderless tables for a journal submission.

---

## 2. Multi-Source Project Ingestion Architecture

The agent systematically scans the active project folder to harvest and condense inputs into the IMRaD framework:

```
┌──────────────────────────────────────┐     ┌────────────────────────────────────┐
│      Proposal / Chapters 1 & 3       │     │     Translated Literature (Ch 2)   │
│ - Societal & clinical problem burden │     │ - Conceptual & theoretical models  │
│ - Specific objectives & hypotheses   │     │ - Recent (2020-2025) empirical lit │
│ - Population, G*Power, instruments   │     │ - International & Iranian studies  │
└──────────────────┬───────────────────┘     └─────────────────┬──────────────────┘
                   │                                           │
                   ▼                                           ▼
          [1. INTRODUCTION]                           [4. DISCUSSION]
          - 4-Paragraph Funnel                        - Theoretical mechanisms
          - Critical research gap                     - Global lit comparison
          - Explicit hypotheses                       - Practical implications
                   │                                           ▲
                   ▼                                           │
             [2. METHOD]                                       │
          - G*Power sample size                                │
          - Psychometric properties                            │
          - Statistical analysis plan                          │
                   │                                           │
                   ▼                                           │
            [3. RESULTS] ──────────────────────────────────────┘
          - Descriptives & Normality
          - 3-4 High-Information APA Tables (ANCOVA / Regression / SEM)
          - Bootstrap 95% Confidence Intervals
```

---

## 3. Dual Publication Tracks

| Feature | **Track A: International English (ISI / Scopus)** | **Track B: Iranian ISC (علمی-پژوهشی)** |
| :--- | :--- | :--- |
| **Language & Tone** | Formal Academic English (C1/C2 vocabulary). | Polished Academic Persian (ادبیات فاخر علمی). |
| **Typography** | `Times New Roman` 12 pt, 1.5/Double-spaced, 1-inch margins. | `B Titr` 14 pt Bold (Headings), `B Nazanin` 12 pt Regular. |
| **Abstract** | English Structured Abstract (200–250 words) + Keywords. | Bilingual: Persian چکیده + Latin Abstract page. |
| **Target Journals** | Elsevier, Springer, Frontiers, Wiley, Taylor & Francis. | مجلات علمی-پژوهشی دانشگاه تهران، شهید بهشتی، خوارزمی و... |

---

## 4. Execution Workflow

### Step 1: Ingest Project Data & Select Track
Inspect the project directory to locate:
- Statistical output: `stats_results.json` or `فصل چهارم: یافته‌های پژوهش.docx`.
- Methodological details: `پروپوزال_طرح_پژوهش.docx` or Chapter 3.
- Theoretical literature: `Translate/` folder or Chapter 2.
- Psychometric instruments: Ingest from project files or query `Questionnaires.xlsx` and the Google Drive master library via `questionnaire_resolver.py search "<scale_name>"` for verified item counts, subscale factors, and Likert anchors.
- Discussion points: Chapter 5.

Confirm the target language track (`--lang en` for International ISI/Scopus, or `--lang fa` for Iranian ISC).

### Step 2: Consult Quality Benchmarks
- Read [imrad_quality_benchmarks.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer/references/imrad_quality_benchmarks.md) for international peer-review standards.
- Read [article_abstract_and_title_guide.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer/references/article_abstract_and_title_guide.md) for title formulas and structured abstract formatting.

### Step 3: Formulate Article Content JSON
Prepare a structured JSON file containing the condensed, high-density scientific prose for each section:
- `title`: High-impact title without filler words.
- `authors` & `affiliation`: Author names and institutional department.
- `abstract`: Structured dictionary (`background`, `objective`, `methods`, `results`, `conclusion`).
- `keywords`: 4–6 controlled terms (MeSH / APA Thesaurus).
- `introduction`: 4-paragraph funnel.
- `method`: Design, G*Power sample size, measures with sample items and $\alpha$, procedure, analysis plan.
- `results`: Narrative + 3–4 APA 7 tables.
- `discussion`: Theoretical mechanisms, empirical comparisons, implications, limitations, conclusion.
- `references`: APA 7th edition bibliography.

### Step 4: Compile Journal-Ready Word Document
Execute the compiler script:
```bash
# For International English Manuscript (ISI / Scopus):
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload.json" \
  --out "Academic_Article_Manuscript.docx" \
  --lang en

# For Iranian Scientific-Research Manuscript (ISC / علمی-پژوهشی):
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload_fa.json" \
  --out "مقاله_علمی_پژوهشی_نهایی.docx" \
  --lang fa
```

---

## 5. Peer-Review Submission Quality Checklist

Before submitting the manuscript to an academic journal, verify:
- [ ] Title contains independent, mediator, and dependent variables without fluff.
- [ ] Abstract word count is strictly between 200 and 250 words.
- [ ] Method section includes a formal G*Power 3.1 sample size justification.
- [ ] For every psychometric instrument, Cronbach's $\alpha$ from the current study and sample items are reported.
- [ ] All tables strictly adhere to APA 7: zero vertical borders, 3 horizontal borders, table captions above, notes below.
- [ ] Discussion explicitly explains the *psychological and theoretical mechanisms* (e.g., Beck, Bandura, Gross) rather than simply repeating statistical figures.
- [ ] Every in-text citation matches an entry in the References list (and vice versa).
- [ ] **Word OMML Math Preservation**: If editing an existing manuscript, never use naive `p.text = "..."` replacement. Verify native Word math formulas (`<m:oMath>`) are preserved intact and extract visible text using `"".join([e.text or "" for e in p._p.iter() if e.tag.endswith("}t")])`.

