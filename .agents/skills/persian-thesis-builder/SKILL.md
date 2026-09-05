---
name: persian-thesis-builder
description: >-
  Use this skill to assemble, synthesize, format, and compile full academic theses (رساله / پایان‌نامه)
  in Persian from modular research documents: institutional Word template (.docx), research proposal
  (for chapter 1, chapter 2 empirical background, and chapter 3), translated literature reviews (for
  chapter 2 theoretical foundations), statistical analysis document (chapter 4), discussion document
  (chapter 5), psychometric scales (appendices), and unified bilingual bibliographies (Persian & English APA references).
---

# Persian Academic Thesis Builder & Compiler Skill

This skill provides an automated, rigorous end-to-end framework for assembling, synthesizing, formatting, and compiling complete Iranian university master's theses and doctoral dissertations (رساله دکتری / پایان‌نامه کارشناسی ارشد) in standard academic Persian. It seamlessly fuses an institutional **Master Word Template (`.docx`)** with **modular research components** (research proposal, translated literature reviews, statistical output, psychological discussion, questionnaires, and APA bibliographies).

---

## 1. Assembly Pipeline & Data Flow Architecture

The compiler integrates heterogeneous research artifacts into a unified, publication-grade academic document:

```
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │ Institutional Master Template │     │    Research Proposal (.pdf/.doc)   │
  │    (e.g., Example Thesis.docx)│     │    - Problem statement, objectives │
  │    - Cover page & preliminary │     │    - Empirical background (in/out) │
  │    - Styles, gutters, headers │     │    - Methodology & instruments     │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  ▼                                       ▼
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │   Translate/ Folder Content   │     │    Chapters 4 & 5 Documents        │
  │   - PIU, IU, Impulsivity, SE  │     │    - Chapter 4: SEM models, tables │
  │   - Translated Persian texts  │     │    - Chapter 5: Discussion & tests │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  ▼                                       ▼
  ┌───────────────────────────────┐     ┌────────────────────────────────────┐
  │     Questionnaire/ Folder     │     │     Reference Sources              │
  │     - Psychometric scales     │     │     - Translate/ (*.txt / *.enw)   │
  │     - Demographic form        │     │     - Proposal & Chapter 5 refs    │
  └───────────────┬───────────────┘     └─────────────────┬──────────────────┘
                  │                                       │
                  └───────────────────┬───────────────────┘
                                      ▼
             ╔═══════════════════════════════════════════════════╗
             ║     Core Assembly Engine (build_full_thesis.py)   ║
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
| **Preliminary Pages (صفحات مقدماتی)** | Master Template (`Example Thesis.docx`) | Persian Cover, Basmalah (بسم‌الله), Authenticity & Ethics Statement, Defense Jury Approval, Dedication, Acknowledgements, Persian Abstract (چکیده), Table of Contents (فهرست مطالب), List of Tables (فهرست جداول), List of Figures (فهرست نمودارها). |
| **Chapter 1: Generalities (کلیات پژوهش)** | Research Proposal (`Proposal-Mrs Talebian`) | 1-1 Introduction & Problem Statement (بیان مسئله), 1-2 Significance & Necessity (ضرورت و اهمیت), 1-3 Objectives (اهداف کلی و اختصاصی), 1-4 Hypotheses / Questions (فرضیه‌ها), 1-5 Conceptual & Operational Definitions (تعاریف متغیرها). |
| **Chapter 2: Theoretical Foundations (مبانی نظری)** | Translation Folder (`Translate/`) | In-depth theoretical frameworks for all constructs (definitions, dimensions, cognitive/behavioral models, etiology, interventions) synthesized from translated literature (`*_fa.docx` or `*_fa.md`). |
| **Chapter 2: Empirical Background (پیشینه تجربی)** | Research Proposal (`Proposal-Mrs Talebian`) | Empirical research conducted in Iran (مطالعات داخلی) + international research (مطالعات خارجی) + literature synthesis and conceptual framework (جمع‌بندی پیشینه و مدل مفهومی). |
| **Chapter 3: Methodology (روش‌شناسی پژوهش)** | Research Proposal (`Proposal-Mrs Talebian`) | 3-1 Research Design (طرح پژوهش), 3-2 Population, Sample & Sampling (جامعه و نمونه), 3-3 Measurement Instruments (ابزارها و پرسشنامه‌ها), 3-4 Procedure (روش اجرا), 3-5 Statistical Analysis Plan (روش‌های تحلیل داده‌ها), 3-6 Ethical Considerations (ملاحظات اخلاقی). |
| **Chapter 4: Statistical Findings (یافته‌های پژوهش)** | Statistical Report (`Chapter 4.docx`) | Descriptive statistics, normality & multicollinearity tests, factor loadings, measurement model fit, Structural Equation Modeling (SEM) path analysis, mediation bootstrapping, and APA tables/figures. |
| **Chapter 5: Discussion & Conclusion (بحث و نتیجه‌گیری)** | Discussion Document (`Chapter 5.docx`) | 5-1 Introduction, 5-2 Hypothesis-by-hypothesis psychological discussion and comparison with prior findings, 5-3 Practical & Clinical Implications, 5-4 Limitations, 5-5 Recommendations, 5-6 Conclusion. |
| **References & Bibliography (منابع و مآخذ)** | Unified Aggregator (`Translate/` + Proposal + Ch5) | Divided strictly into: **A) Persian References (الف) منابع فارسی)** sorted alphabetically by Persian collation, and **B) English References (ب) منابع انگلیسی)** formatted in APA 7th Edition, sorted A–Z. |
| **Appendices (پیوست‌ها)** | Scales Folder (`Questionnaire/`) | Demographic questionnaire followed by full standard psychometric testing scales with clear Likert response tables and scoring instructions. |
| **English Back Matter (صفحات پایانی لاتین)** | Auto-generated from Abstract & Title | English Abstract page (Background, Method, Results, Conclusion, Keywords) + English Back Cover page. |

---

## 3. Academic Typography, Layout & BiDi OpenXML Standards

All assembled chapters, tables, and front matter must strictly adhere to Iranian graduate university formatting guidelines:

### A. Font System & Hierarchy
- **Chapter Titles (`Heading 1`)**: Font `B Titr` 16 or 18 pt Bold, Centered or Right-aligned, Space Before: 20 pt, Space After: 14 pt.
- **Major Headings (`Heading 2`)**: Font `B Titr` or `B Nazanin Bold` 14 pt Bold, Right-aligned, Space Before: 12 pt, Space After: 6 pt.
- **Subheadings (`Heading 3`)**: Font `B Nazanin Bold` 13 pt Bold, Right-aligned, Space Before: 8 pt, Space After: 4 pt.
- **Body Paragraphs (`Normal`)**: Font `B Nazanin` or `B Lotus` 13–14 pt Regular, Line Spacing: 1.15–1.3, Justified (`WD_ALIGN_PARAGRAPH.JUSTIFY`).
- **Tables & Figures**: Table titles positioned **above** the table (11 pt Bold); figure captions positioned **below** the figure (11 pt Bold). Table cells 10–11 pt Centered.
- **Footnotes & Latin Terms**: Font `Times New Roman` 9–10 pt, Left-aligned (LTR).

### B. BiDi Directionality & Footnote Line-Break Prevention (Critical OpenXML Rules)
To eliminate premature line wrapping, word scrambling, and flipped punctuation marks around footnotes in Microsoft Word:
1. **Paragraph Direction & Justification**:
   - All Persian body paragraphs must contain `<w:bidi/>` in paragraph properties (`w:pPr`).
   - Paragraph alignment must be **Justified** (`<w:jc w:val="both"/>` or `paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY`).
2. **Mandatory `<w:rtl/>` on ALL Text Runs (Zero Tolerance for Mixed Run Direction)**:
   - **Root Cause**: If a Persian text run lacks `<w:rtl/>` while a footnote reference run contains `<w:rtl/>`, Word treats the paragraph as alternating LTR and RTL runs (`[LTR Text] [RTL Footnote] [LTR Text]`). Word's layout engine then wraps the line prematurely at the footnote marker and flips surrounding word order.
   - **Standard**: Every single Persian text run (`<w:r>`) must explicitly include `<w:rtl/>` in `<w:rPr>`, alongside `<w:rFonts w:ascii="B Nazanin" w:cs="B Nazanin"/>` and `<w:lang w:val="fa-IR" w:bidi="fa-IR"/>`.
3. **Mandatory Native Word Footnotes Integration**:
   - The compiled thesis must assemble full native Word footnotes into `word/footnotes.xml` from all modular sources (translated literature reviews in Chapter 2 and draft footnotes in Chapters 4/5).
   - Follow the translation skill footnote rules:
     - No Latin in parentheses in body text; specialized terminology moved to footnotes on first occurrence.
     - First-occurrence-only deduplication for terminology and author citations.
     - Footnotes wired in `word/_rels/document.xml.rels` and `[Content_Types].xml`.
     - Footnote reference runs must include `<w:rStyle w:val="FootnoteReference"/>`, `<w:rFonts w:ascii="B Nazanin" w:cs="B Nazanin"/>`, `<w:rtl/>`, and `<w:lang w:val="fa-IR" w:bidi="fa-IR"/>` to guarantee authentic Persian numerals (۱، ۲، ۳...).
4. **Quotation Guillemet & Punctuation Placement**:
   - Footnote markers must always be placed **outside and immediately after closing quotation marks or punctuation** (e.g., `«تفکر منفی تکرارشونده»[^15]`, never `«تفکر منفی تکرارشونده[^15]»`). Placing footnote runs inside quotation marks splits the quotation pair across runs, inverting punctuation and triggering wrap glitches.
5. **Modern Word Layout Engine (`compatibilityMode = 15`)**:
   - In `word/settings.xml`, ensure `<w:compatSetting w:name="compatibilityMode" ... w:val="15"/>` is present. This prevents Microsoft Word (2013+) from opening the document in legacy Compatibility Mode (Word 2007/2010), activating DirectWrite modern Bidi text shaping.
6. **Table BiDi Properties & Native Captions**:
   - Tables must have `<w:bidiVisual/>` in `w:tblPr` and `<w:tcBidi/>` in `w:tcPr` to guarantee RTL column order.
   - All tables, charts, graphs, and photos must have native Word captions created from `References > Insert Caption` (`SEQ جدول_... \* ARABIC` and `SEQ شکل_... \* ARABIC`). Never strip or flatten caption fields into plain text.
7. **RTL Text Direction and Justified Alignment for ALL Headings**:
   - All document headings (`Heading 1`, `Heading 2`, `Heading 3`, `Heading 4`, `تیتر ۱`, `تیتر ۲`, `تیتر ۳`, etc.) must have:
     - `<w:bidi/>` in `<w:pPr>`.
     - Alignment set to right-aligned with justify (`<w:jc w:val="both"/>` or `<w:jc w:val="right"/>`).
     - Every run inside headings must have `<w:rtl/>` in `<w:rPr>`, Persian language tags (`fa-IR`), and appropriate bold fonts (`B Titr` / `B Nazanin Bold`).
8. **Non-Destructive Element-Level Chapter Injection (Zero Destruction Rule)**:
   - When injecting complex chapters (such as Chapter 4 containing statistical tables, histograms, P-P plots, and SEM path models), NEVER use `child.itertext()` or string re-construction which destroys bookmarks, drawing shapes, and fields.
   - Copy OpenXML elements directly (`copy.deepcopy(child)`), synchronize image files in `word/media/`, and update relationship IDs in `word/_rels/document.xml.rels`.
9. **Automatic Multilevel Hierarchical Heading Numbering**:
   - Numbering must be 100% dynamic via Microsoft Word's native list engine (`abstractNumId=2`, `numId=3`).
   - **Level 1 (`Heading 1`)**: Single chapter number (`۱-`, `۲-`, `۳-`, `۴-`, `۵-`). Unnumbered for back matter (`فهرست منابع` and `پیوست‌ها`).
   - **Level 2 (`Heading 2`)**: Two numbers (`[Parent]-[Itself]`, e.g., `۱-۱-`, `۱-۲-`, `۲-۱-`).
   - **Level 3 (`Heading 3`)**: Three numbers (`[Parent]-[Subparent]-[Itself]`, e.g., `۲-۱-۱-`, `۴-۱-۱-`).
   - **Strict OpenXML Schema Order**: Inside `<w:pPr>`, elements MUST be in exact sequence:
     `<w:pStyle>` $\rightarrow$ `<w:keepNext>` $\rightarrow$ `<w:numPr>` (`w:ilvl`, `w:numId`) $\rightarrow$ `<w:bidi>` $\rightarrow$ `<w:spacing>` $\rightarrow$ `<w:jc>`.
   - **Relationship Preservation**: Always preserve `rId2` (the OpenXML link to `word/numbering.xml`) in `word/_rels/document.xml.rels`.
10. **Native Markdown Formatting & Table Parsing**:
    - Raw asterisks (`*text*` for italic, `**text**` for bold) must be parsed into native `<w:i>` and `<w:b>` runs; raw asterisks must never remain in body paragraphs, citations, or references.
    - Markdown raw tables (consecutive lines starting with `|`) must be detected and converted into native APA Word tables (`<w:tbl>`) with shaded headers, borders, and native `SEQ جدول_...` captions.
11. **Appendix Questionnaire Table Layout Standards**:
    - Tables in appendices must avoid vertical syllable wrapping by specifying explicit column widths:
      - Column 0 (Index): 720 dxa.
      - Column 1 (Item/Question): 3600 dxa.
      - Columns 2–N (Likert scale options): ~650 dxa each.
    - Header text should use explicit line breaks (`کاملاً\nمخالفم`) and cell padding (`top/bottom=60 dxa, left/right=100 dxa`).


### C. Margins & Page Geometry
- **Right Margin (Binding Gutter / عطف صحافی)**: 3.5 cm (1.38 in)
- **Left Margin**: 2.5 cm (0.98 in)
- **Top Margin**: 3.0 cm (1.18 in)
- **Bottom Margin**: 2.5 cm (0.98 in)

### D. Persian Orthography & Character Sanitization
- **Zero-Width Non-Joiner (نیم‌فاصله `\u200c`)**: Strictly enforced for verbal prefixes (`می‌شود`, `برمی‌آید`), plural markers (`پژوهش‌های`, `یافته‌ها`), and compound terms (`خودکارآمدی`, `روان‌شناختی`, `مشکل‌آفرین`).
- **100% Pure Persian Characters**: Automatically sanitize any legacy Arabic characters in text and XML runs:
  - Arabic Yeh (`ي` U+064A) and Alef Maksura (`ى` U+0649) $\rightarrow$ Persian Yeh (`ی` U+06CC).
  - Arabic Kaf (`ك` U+0643) $\rightarrow$ Persian Keheh (`ک` U+06A9).
  - Arabic Teh Marbuta (`ة` U+0629) $\rightarrow$ Persian Heh (`ه` U+0647).
  - Eastern Arabic Digits (`٠١٢٣٤٥٦٧٨٩`) $\rightarrow$ Persian Digits (`۰۱۲۳۴۵۶۷۸۹`).

---

## 4. Step-by-Step Execution Protocol

Execute the thesis compilation pipeline following these nine stages:

### Step 1: Source Document Audit
Verify the availability and integrity of all source artifacts in the workspace:
1. Master Template: `Example Thesis.docx`
2. Research Proposal: `Proposal-Mrs Talebian.pdf` or `.doc`
3. Translated Literature: `Translate/` containing `*_fa.docx` / `*_fa.md` and `*_References_APA.txt`
4. Statistical & Discussion Documents: `Chapter 4.docx` and `Chapter 5.docx`
5. Measurement Scales: `Questionnaire/` containing raw scale forms

### Step 2: Proposal Section Extraction
Run the automated proposal extractor to segment the approved proposal into standalone chapter drafts:
```bash
python "C:\Users\ghade\.gemini\config\skills\persian-thesis-builder\scripts\extract_proposal_data.py" \
    --proposal-pdf "g:\My Drive\My Work\Fada Talebi\Proposal-Mrs Talebian.pdf" \
    --output-dir "g:\My Drive\My Work\Fada Talebi\Proposal_Extracted"
```
Generated artifacts:
- `Chapter1_from_Proposal.md`: Problem statement, significance, objectives, hypotheses, definitions.
- `Chapter2_Empirical_from_Proposal.md`: Domestic and international empirical research findings.
- `Chapter3_from_Proposal.md`: Research design, sample, instrumentation, analysis plan, ethics.
- `Proposal_References.txt`: Proposal reference list.

### Step 3: Theoretical Foundations Synthesis (Chapter 2)
Synthesize the translated theoretical literature from `Translate/` into structured discourses for Chapter 2:
- Construct 1: Generalized Problematic Internet Use (`PIU_Pages_13-44_fa`)
- Construct 2: Intolerance of Uncertainty (`Intolerance_of_Uncertainty_Pages_1-26_fa`)
- Construct 3: Impulsivity (`Impulsivity_Pages_1-10_fa`)
- Construct 4: General Self-Efficacy (`Self_Efficacy_Pages_24-42_fa`)
- Organize into Sections 2-1, 2-2, 2-3, and 2-4.
- Append Empirical Background from proposal as Section 2-5 (Domestic & Foreign Studies).
- Conclude with Conceptual Model & Hypotheses as Section 2-6.

### Step 4: Empirical Findings Integration (Chapter 4)
Deep-copy all statistical output from `Chapter 4.docx` into the Chapter 4 body:
- Preserve all 22 APA tables (descriptive stats, correlation matrices, factor loadings, SEM fit indices).
- Preserve path diagrams and measurement model figures with standardized path coefficients ($\beta$).

### Step 5: Psychological Discussion Integration (Chapter 5)
Integrate `Chapter 5.docx` into the Chapter 5 body:
- Contextualize each empirical hypothesis against prior domestic and international literature.
- Formulate practical/educational applications, methodological limitations, future research suggestions, and concluding remarks.

### Step 6: Questionnaire Appendix Compilation
Run the questionnaire formatting utility:
```bash
python "C:\Users\ghade\.gemini\config\skills\persian-thesis-builder\scripts\format_questionnaires.py"
```
Produces `Questionnaires_Appendix.docx` featuring demographic survey forms and formatted Likert-scale test batteries.

### Step 7: Bilingual Reference Aggregation & Collation
Run the reference compilation engine:
```bash
python "C:\Users\ghade\.gemini\config\skills\persian-thesis-builder\scripts\compile_references.py" \
    --translate-dir "g:\My Drive\My Work\Fada Talebi\Translate" \
    --proposal-refs "g:\My Drive\My Work\Fada Talebi\Proposal_Extracted\Proposal_References.txt" \
    --output-txt "g:\My Drive\My Work\Fada Talebi\References_Compiled_APA.txt" \
    --output-docx "g:\My Drive\My Work\Fada Talebi\References_Compiled.docx"
```
The script automatically:
1. Harvests all Persian and English citations across `Translate/`, the proposal, and Chapter 5.
2. Deduplicates records based on author names, year, and titles.
3. Collates Persian references strictly according to Persian alphabetical order.
4. Formats English references according to APA 7th Edition, sorted A–Z with hanging indents.

### Step 8: Master Thesis Assembly
Execute the core compiler engine:
```bash
python "C:\Users\ghade\.gemini\config\skills\persian-thesis-builder\scripts\build_full_thesis.py"
```
This engine:
1. Loads the institutional template (`Example Thesis.docx`).
2. Updates cover page, student name, thesis title, supervisor, and Persian abstract.
3. Prunes old thesis body content while preserving front matter and section properties.
4. Injects Chapters 1 through 5 with 100% Persian typography, proper headings, and justified paragraph flow.
5. Injects compiled bilingual references and questionnaire appendices.
6. Appends English back matter (English abstract and back cover page).
7. Injects `compatibilityMode = 15` in `word/settings.xml` and saves `Thesis_Compiled.docx`.

### Step 9: Quality Assurance & Field Updates
1. **Field Code Update in Microsoft Word**:
   - Open `Thesis_Compiled.docx` in Word, right-click on the Table of Contents, List of Tables, and List of Figures, and select **Update Field (Update entire table)**, or press `F9` to synchronize page numbers.
2. **Footnote Verification**:
   - Verify that Latin footnotes appear neatly at the bottom of their respective pages with Persian numerals in text and zero premature line wraps.
3. **Heading Hierarchy Check**:
   - Confirm that `Heading 1`, `Heading 2`, and `Heading 3` styles are cleanly recognized in Word's Navigation Pane.

---

## 5. Supporting Resources & Scripts

- [Thesis Structure Guide](./references/thesis_structure_guide.md): Comprehensive chapter breakdown and university specifications.
- [Bilingual APA 7th Reference Guidelines](./references/apa_bilingual_reference_rules.md): Detailed rules for Persian and English references.
- [Sample Assembly Workflow](./examples/thesis_assembly_sample.md): Step-by-step example execution walkthrough.
- [build_full_thesis.py](./scripts/build_full_thesis.py): Master thesis compiler script.
- [compile_references.py](./scripts/compile_references.py): Bilingual reference aggregator and deduplicator.
- [extract_proposal_data.py](./scripts/extract_proposal_data.py): Automated proposal section extractor.
- [format_questionnaires.py](./scripts/format_questionnaires.py): Questionnaire appendix formatter.
