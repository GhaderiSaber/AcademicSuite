---
name: persian-thesis-builder
description: >-
  Use this skill to assemble, synthesize, format, and compile full academic theses (رساله / پایان‌نامه)
  in Persian from modular research documents: institutional Word template (.docx), research proposal
  (for chapter 1, chapter 2 empirical background, and chapter 3), translated literature reviews (for
  chapter 2 theoretical foundations), statistical analysis document (chapter 4), discussion document
  (chapter 5), psychometric scales (appendices), and unified bilingual bibliographies (Persian & English APA references).
---

# Persian Academic Thesis Builder & Compiler Skill (تدوین و یکپارچه‌سازی پایان‌نامه و رساله دانشگاهی)

This skill provides an automated, rigorous framework for assembling, synthesizing, formatting, and compiling complete Iranian university master's theses and doctoral dissertations (رساله دکتری / پایان‌نامه کارشناسی ارشد) in standard academic Persian. It seamlessly fuses an institutional **Master Word Template (`.docx`)** with **modular research components** (research proposal, translated literature reviews, statistical output, psychological discussion, questionnaires, and APA bibliographies).

---

## 1. Assembly Pipeline & Data Flow Architecture

The compiler integrates heterogeneous research artifacts into a unified, defense-ready academic document:

```
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │ Institutional Master Template │     │    Research Proposal (.docx/.pdf)  │
  │    - Cover page & preliminary │     │    - Problem statement, objectives │
  │    - Styles, gutters, headers │     │    - Empirical background (in/out) │
  │    - TOC & List of Tables     │     │    - Methodology & instruments     │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  ▼                                       ▼
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │   Translate/ Folder Content   │     │    Chapters 4 & 5 Documents        │
  │   - Translated literature     │     │    - Chapter 4: Stats tables, SEM  │
  │   - Theoretical foundations   │     │    - Chapter 5: Discussion & tests │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  ▼                                       ▼
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │   Psychometric Scales & Data  │     │     Bilingual Reference Sources    │
  │   - Questionnaires.xlsx       │     │     - Persian & English APA lists  │
  │   - psychometric-scale-resolver│    │     - academic-reference-extractor │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  └───────────────────┬───────────────────┘
                                      ▼
             ╔═══════════════════════════════════════════════════╗
             ║     Core Assembly Engine (compile_full_thesis.py) ║
             ╠═══════════════════════════════════════════════════╣
             ║ 1. Preliminary Matter (Cover, Approval, Abstract) ║
             ║ 2. Chapter 1: Generalities of Research (Proposal) ║
             ║ 3. Chapter 2: Foundations (Translate) + Empirical ║
             ║ 4. Chapter 3: Research Methodology (Proposal)     ║
             ║ 5. Chapter 4: Statistical Results (Chapter 4.docx)║
             ║ 6. Chapter 5: Discussion & Synthesis (Ch 5.docx)  ║
             ║ 7. Bilingual References (A: Persian | B: English) ║
             ║ 8. Appendices (Standard Psychometric Questionnaires║
             ║ 9. English Back Matter (Abstract & Back Cover)    ║
             ╚═══════════════════════════════════════════════════╝
                                      │
                                      ▼
                  ┌───────────────────────────────────────┐
                  │      Thesis_Compiled.docx (Final)     │
                  └───────────────────────────────────────┘
```

---

## 2. Modular Source-to-Target Thesis Mapping

The thesis compiler maps modular inputs directly into standard Iranian graduate school chapters:

| Final Thesis Component | Primary Source Document | Content Scope & Structural Rules |
| :--- | :--- | :--- |
| **Preliminary Pages (صفحات مقدماتی)** | Master Template (`template.docx`) | Persian Cover, Basmalah (بسم‌الله), Authenticity & Ethics Statement, Defense Jury Approval, Dedication, Acknowledgements, Persian Abstract (چکیده), Table of Contents (فهرست مطالب), List of Tables (فهرست جداول), List of Figures (فهرست نمودارها). |
| **Chapter 1: Generalities (کلیات پژوهش)** | Research Proposal or Ch 1 Draft | 1-1 Introduction & Problem Statement (بیان مسئله), 1-2 Significance & Necessity (ضرورت و اهمیت), 1-3 Objectives (اهداف کلی و اختصاصی), 1-4 Hypotheses / Questions (فرضیه‌ها), 1-5 Conceptual & Operational Definitions (تعاریف متغیرها). |
| **Chapter 2: Theoretical Foundations (مبانی نظری)** | Translation Folder (`Translate/`) | In-depth theoretical frameworks for all constructs synthesized from translated literature (`*_fa.docx`). |
| **Chapter 2: Empirical Background (پیشینه تجربی)** | Research Proposal or Literature Review | Empirical research conducted in Iran (مطالعات داخلی) + international research (مطالعات خارجی) + literature synthesis and conceptual framework (جمع‌بندی پیشینه و مدل مفهومی). |
| **Chapter 3: Methodology (روش‌شناسی پژوهش)** | Research Proposal or Ch 3 Draft | 3-1 Research Design (طرح پژوهش), 3-2 Population, Sample & Sampling (جامعه و نمونه), 3-3 Measurement Instruments (ابزارها و پرسشنامه‌ها), 3-4 Procedure (روش اجرا), 3-5 Statistical Analysis Plan (روش‌های تحلیل داده‌ها), 3-6 Ethical Considerations (ملاحظات اخلاقی). |
| **Chapter 4: Statistical Findings (یافته‌های پژوهش)** | Statistical Report (`Chapter 4.docx`) | Descriptive statistics, normality tests, factor loadings, ANCOVA, regression, SEM path analysis, mediation bootstrapping, and APA borderless tables. |
| **Chapter 5: Discussion & Conclusion (بحث و نتیجه‌گیری)** | Discussion Document (`Chapter 5.docx`) | 5-1 Introduction, 5-2 Hypothesis-by-hypothesis psychological discussion and comparison with prior findings, 5-3 Practical & Clinical Implications, 5-4 Limitations, 5-5 Recommendations, 5-6 Conclusion. |
| **References & Bibliography (منابع و مآخذ)** | Unified Aggregator (`references.docx`/`.txt`) | Divided strictly into: **A) Persian References (الف) منابع فارسی)** sorted alphabetically by Persian collation, and **B) English References (ب) منابع انگلیسی)** formatted in APA 7th Edition, sorted A–Z. |
| **Appendices (پیوست‌ها)** | `psychometric-scale-resolver` | Demographic questionnaire followed by full standard psychometric testing scales with clear Likert response tables and scoring instructions. |
| **English Back Matter (صفحات پایانی لاتین)** | Auto-generated from Abstract & Title | English Abstract page (Background, Method, Results, Conclusion, Keywords) + English Back Cover page. |

---

## 3. Academic Typography, Layout & BiDi OpenXML Standards

All assembled chapters, tables, and front matter must strictly adhere to Iranian graduate university formatting guidelines:

### A. Font System & Hierarchy
- **Chapter Titles (`Heading 1`)**: Font `B Titr` 16 or 18 pt Bold, Centered, Space Before: 24 pt, Space After: 14 pt.
- **Major Headings (`Heading 2`)**: Font `B Titr` 14 pt Bold, Right-aligned, Space Before: 14 pt, Space After: 6 pt.
- **Subheadings (`Heading 3`)**: Font `B Nazanin Bold` 13 pt Bold, Right-aligned, Space Before: 8 pt, Space After: 4 pt.
- **Body Paragraphs (`Normal`)**: Font `B Nazanin` or `B Lotus` 13–14 pt Regular, Line Spacing: 1.25, Justified (`WD_ALIGN_PARAGRAPH.JUSTIFY`).
- **Tables & Figures**: Table titles positioned **above** the table (11 pt Bold); figure captions positioned **below** the figure (11 pt Bold). Table cells 10–11 pt Centered.
- **Footnotes & Latin Terms**: Font `Times New Roman` 9–10 pt, Left-aligned (LTR).

### B. BiDi Directionality & OpenXML Rules
1. **Paragraph Direction**: Enforce `<w:bidi w:val="1"/>` on all Persian paragraphs.
2. **Font Fallback Protection**: Enforce explicit font binding with `<w:rFonts w:ascii="Times New Roman" w:cs="B Nazanin"/>`.
3. **Table BiDi**: Enforce `<w:bidiVisual/>` on table properties to guarantee Right-to-Left column ordering.

---

## 4. Execution Workflow with `compile_full_thesis.py`

### CLI Command Reference:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "path/to/University_Template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "path/to/Chapter1.docx" \
  --ch2 "path/to/Chapter2_Translate" \
  --ch3 "path/to/Chapter3.docx" \
  --ch4 "path/to/Chapter4.docx" \
  --ch5 "path/to/Chapter5.docx" \
  --refs "path/to/References_APA.txt" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire" \
  --title-en "The Effectiveness of Mindfulness on Academic Anxiety and Resilience" \
  --author-en "Student Name" \
  --supervisor-en "Supervisor Name, Ph.D."
```

### Post-Assembly Quality Assurance:
1. **Field Code Update in Microsoft Word**:
   - Open `Thesis_Compiled.docx` in Word, right-click on the Table of Contents, List of Tables, and List of Figures, and select **Update Field (Update entire table)**, or press `F9` to synchronize page numbers.
2. **Footnote Verification**:
   - Verify that Latin footnotes appear neatly at the bottom of their respective pages with Persian numerals in text and zero premature line wraps.
3. **Heading Hierarchy Check**:
   - Confirm that `Heading 1`, `Heading 2`, and `Heading 3` styles are cleanly recognized in Word's Navigation Pane.

---

## 5. Supporting Resources & Scripts

- [Thesis Structure Guide](./references/thesis_structure_guide.md) — Comprehensive chapter breakdown and university specifications.
- [Bilingual APA 7th Reference Guidelines](./references/apa_bilingual_reference_rules.md) — Detailed rules for Persian and English references.
- [compile_full_thesis.py](./scripts/compile_full_thesis.py) — Unified master thesis compiler engine.
