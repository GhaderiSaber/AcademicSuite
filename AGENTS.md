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
| **`persian-academic-translation`** | [.agents/skills/persian-academic-translation/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-academic-translation) | User requests translating English papers, book chapters, or theoretical frameworks into academic Persian. | English PDF / DOCX / TXT papers | `*_fa.docx` formatted with academic terminology and preserved citations. |
| **`academic-reference-extractor`** | [.agents/skills/academic-reference-extractor/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/academic-reference-extractor) | User needs EndNote/Zotero citations for a translated paper or specific thesis chapter. | Translated text with citations + Master paper bibliography | `.enw` (EndNote), `.ris` (Zotero/Mendeley), and `.txt` (APA list). |
| **`statistical-data-analyst`** | [.agents/skills/statistical-data-analyst/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/statistical-data-analyst) | User provides data (`.sav`, `.xlsx`, `.csv`) and requests analysis, hypothesis testing, or Chapter 4 writing. | Raw dataset + Hypotheses / Research Questions | `فصل چهارم: یافته‌های پژوهش.docx` + `stats_results.json` + APA 7 tables. |
| **`persian-discussion-builder`** | [.agents/skills/persian-discussion-builder/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-discussion-builder) | User requests writing Chapter 5 (بحث و نتیجه‌گیری) interpreting statistical findings against literature. | Chapter 4 results (`stats_results.json`) + Chapter 2 literature | `فصل پنجم: بحث و نتیجه‌گیری.docx` with clinical implications and limitations. |
| **`persian-thesis-builder`** | [.agents/skills/persian-thesis-builder/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-thesis-builder) | User wants to compile, merge, format, or assemble all thesis parts into a unified university document. | Master `.docx` template + Proposal + Translated Chapters 2, 4, 5 + Questionnaires | `Thesis_Compiled.docx` (Complete dissertation meeting university formatting rules). |

---

## 3. Data & Artifact Workflow Architecture

The skills are modular and designed to pass standard artifacts between each other across the entire thesis lifecycle:

```
[Research Idea / Variables] ──► (persian-proposal-builder)    ──► Proposal / Ch 1 & 3 (.docx)
                                                                           │
                                                                           ▼
[Raw English Literature]    ──► (persian-academic-translation) ──► Chapter 2 Lit (.docx)
                                                                           │
                                                                           ▼
[In-Text Citations]         ──► (academic-reference-extractor)   ──► .enw / .ris / .txt
                                                                           │
                                                                           ▼
[SPSS / Excel Dataset]      ──► (statistical-data-analyst)       ──► Chapter 4 (.docx)
                                                                           │
                                                                           ▼
[Hypotheses + Stats JSON]   ──► (persian-discussion-builder)     ──► Chapter 5 (.docx)
                                                                           │
                                                                           ▼
[All Chapters + Template]   ──► (persian-thesis-builder)         ──► Master Thesis (.docx)
```

---

## 4. Python Environment & CLI Command Reference

All calculation scripts are located in `.agents/skills/statistical-data-analyst/scripts/`.

### Run Automated Statistical Suite:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/data.xlsx" \
  --task auto \
  --config "path/to/config.json" \
  --out "stats_results.json"
```

### Run Specific Statistical Tasks:
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
