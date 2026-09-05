---
name: persian-academic-translation
description: >-
  Use this skill whenever translating academic papers, research articles, thesis chapters,
  proposals, or technical documents into Persian (فارسی). Guides extracting document content,
  applying domain-specific academic terminology (psychology, behavioral science, methodology,
  statistics), maintaining Persian typography rules (نیم‌فاصله), and formatting translations.
---

# Academic Persian Translation Skill

This skill guides the agent in translating academic and scholarly literature (articles, thesis chapters, proposals, psychometric questionnaires, and reports) from English into fluent, standard academic Persian (فارسی روان و دانشگاهی).

---

## 1. Preparation & Document Reading

1. **Locate and Inspect Source File**:
   - For PDF documents: Use `view_file` to read the PDF and its OCR/text stream.
   - For Word (`.docx`) files: Read or extract paragraphs and headings.
   - For plain text / Markdown: Read directly with `view_file`.
2. **Determine Translation Scope**:
   - Confirm whether the user wants:
     - Full paper translation.
     - Section-by-section translation (e.g., Abstract, Introduction, Method, Results, Discussion).
     - Executive summary / key takeaways in Persian.
3. **Reference Subject Glossaries**:
   - For psychology, psychiatry, and behavioral science: Consult [Psychology & Behavioral Science Glossary](./references/psychology_glossary.md).
   - For research design, psychometrics, and data analysis: Consult [Methodology & Statistics Glossary](./references/methodology_statistics.md).

---

## 2. Core Translation Principles

### A. Academic Tone & Fluency (لحن علمی و آکادمیک)
- **Natural Persian Syntax**: Avoid robotic word-by-word translation. Rephrase sentences so they flow naturally in formal Persian scholarly literature.
- **Active vs. Passive Voice**: In English academic writing, passive voice is ubiquitous ("It was observed that..."). In Persian, rephrase smoothly into natural formal prose (e.g., به جای ترجمه تحت‌اللفظی «مشاهده شد که»، بنویسید: «نتایج پژوهش نشان داد که...»).
- **Precision**: Do not summarize or omit nuances unless explicitly requested. Maintain the rigor of the author's arguments.

### B. Handling Technical Terms & Abbreviations (قاعده پانویس برای اصطلاحات تخصصی)
- **Footnote English Equivalents Instead of In-Text Parentheses (پانویس اصطلاحات به جای پرانتز در متن)**:
  - Do NOT clutter Persian body text with Latin phrases in parentheses (e.g., avoid writing «عدم تحمل بلاتکلیفی (Intolerance of Uncertainty - IU)» inside the paragraph).
  - Instead, write the fluent Persian equivalent in the text and place the authentic English term and any abbreviation in a **footnote (پانویس)** on its **first occurrence**:
    - *In Text*: «...نقش کلیدی عدم تحمل بلاتکلیفی[^1] در شکل‌گیری نگرانی...»
    - *Footnote*: `[^1]: Intolerance of Uncertainty (IU)`
    - *In Text*: «...اختلال اضطراب فراگیر[^2] یکی از...»
    - *Footnote*: `[^2]: Generalized Anxiety Disorder (GAD)`
- **First Occurrence Only Rule for Terminology (عدم تکرار پانویس برای اصطلاحات)**:
  - Each specialized term or abbreviation is footnoted **only once** at its first appearance in the document.
  - On all subsequent occurrences, use solely the established Persian term without attaching another footnote.
- **Questionnaires & Psychometric Scales**:
  - The scale name in Persian is footnoted with its official English title and acronym on first mention:
    - *In Text*: «سیاهه نشانه‌های بیماری ویرایش نهم[^3]» $\rightarrow$ *Footnote*: `[^3]: Symptom Checklist-90-Revised (SCL-90-R)`
    - *In Text*: «مقیاس تکانشگری بارات[^4]» $\rightarrow$ *Footnote*: `[^4]: Barratt Impulsiveness Scale (BIS-11)`

### C. Persian Typographic Standards (اصول نگارش و ویرایش فارسی)
- **Zero-Width Non-Joiner (نیم‌فاصله)**:
  - Consistently use zero-width non-joiner (`\u200c`) for prefixes, suffixes, and compound words:
    - پیشوندها: «می‌شود»، «می‌توان» (نه «می شود»).
    - پسوندها: «پژوهش‌های»، «یافته‌ها»، «پیامدهای» (نه «پژوهش های»).
    - واژگان مرکب: «خطرپذیری»، «تصمیم‌گیری»، «خودکارآمدی»، «روان‌شناختی»، «مشکل‌آفرین» (نه «خطر پذیری» یا «خطرپذیری»).
- **Punctuation**:
  - Use Persian comma (`،`) instead of English comma (`,`).
  - Use Persian semicolon (`؛`) instead of English semicolon (`;`).
  - Use quotation guillemets (« ») instead of straight double quotes (" ").
  - Use Persian question mark (`؟`).
- **Numbers and Statistics**:
  - In flowing Persian text, write Persian numerals where appropriate.
  - In statistical notation (such as $p < 0.05$, $F(1, 654) = 4.32$, $\alpha = 0.88$, $M = 16.32$, $SD = 1.54$), keep the international mathematical notation intact.

### D. Handling In-Text References & Citations (مدیریت ارجاعات درون‌متنی)

In academic literature and theses, references usually follow either the **Numbered system** (e.g., `[1]`, `[5, 6]`) or the **Author-Date system (APA)** (e.g., `(Smith et al., 2020)`). Handle them according to the following conventions:

1. **Numbered Citations (شیوه عددی / ونکوور)**:
   - Preserve citation brackets and numbers exactly where they belong in the sentence: `[1]`, `[2, 3]`, `[15–17]`.
   - Place them immediately adjacent to the relevant term or before the period/comma:
     - *English*: `...could lead to mental disorders [1].`
     - *Persian*: «...می‌تواند به اختلالات روانی منجر شود [1].»
   - Ensure RTL text flow does not invert bracket order.

2. **Author-Date Citations (شیوه نویسنده-سال / APA) — قاعده پانویس انگلیسی**:
   - **Main Rule (نام فارسی با پانویس لاتین)**:
     - All author names must be rendered in Persian in the body text (both narrative and parenthetical).
     - On the **first mention** of each author/study in the text, insert a **footnote (پانویس)** containing the original English name.
     - Translate "and colleagues" / "et al." to «و همکاران» and "&" to «و».
   - **Narrative Citations (در جریان متن)**:
     - *English*: *"Chen and colleagues (2020) have shown..."*
     - *Persian*: «چن و همکاران[^1] (2020) نشان دادند...»
     - *Footnote*: `[^1]: Chen et al.`
     - *English*: *"According to Griffiths' (2005) model..."*
     - *Persian*: «بر اساس مدل گریفیث[^2] (2005)...»
     - *Footnote*: `[^2]: Griffiths`
   - **Parenthetical Citations (در انتهای جمله داخل پرانتز)**:
     - *English*: `...associated with internet addiction (Cerniglia et al., 2019).`
     - *Persian*: «...با اعتیاد به اینترنت مرتبط است (سرنیگلیا و همکاران[^3]، 2019).»
     - *Footnote*: `[^3]: Cerniglia et al.`
     - *English*: `(Bekhbat & Neigh, 2018)` $\rightarrow$ `(بخباط و نی[^4]، 2018)`
     - *Footnote*: `[^4]: Bekhbat & Neigh`
   - **Page Numbers and Locators**:
     - *English*: `(Fossati et al., 2001, p. 632)`
     - *Persian*: `(فوساتی و همکاران، 2001، ص. ۶۳۲)`
    - **Subsequent Mentions & Strict Deduplication Rule (قاعده اکید عدم تکرار پانویس برای منابع)**:
      - **Once footnoted, NEVER footnote that reference again**: When an author/study has been footnoted at its first occurrence, all subsequent mentions anywhere in the document must simply use the Persian transliteration without an in-text footnote marker (e.g., «چن و همکاران (2020)» or «کانمن و تورسکی (1979)»).
      - This applies to both narrative and parenthetical citations, keeping the footnotes clean, uncluttered, and strictly non-redundant.
    - **Unified Footnote Stream (جریان یکپارچه پانویس‌ها)**:
      - Both **in-text references** (Latin author names) and **technical terminology** (English equivalent terms) share the document's continuous footnote numbering stream (۱، ۲، ۳...).
      - Every unique reference and every unique specialized term is footnoted **exactly once** at its first appearance.
    - **Important Formatting Rule for .docx**:
      - In companion Markdown files, footnotes use standard markdown syntax `[^1]`.
      - In **Word documents (`.docx`)**, footnotes must **never** appear as literal bracket characters (`[^1]`). Instead, they must be compiled as native Word footnote objects (`<w:footnoteReference>`) with Persian numerals (see Section 4).

3. **End-of-Document Reference List (فهرست منابع پایانی)**:
    - Keep the original Latin reference entries untouched under the section heading **«منابع / References»**, as academic indexing (DOIs, journal names, authors) requires the authentic Latin citation.

---

## 3. Section-by-Section Translation Guide

Follow the standard structure of scientific papers:

1. **Title (عنوان)**: Concise, capturing all independent and dependent variables.
2. **Abstract (چکیده)**:
   - **Background & Aims (مقدمه و اهداف)**
   - **Methods (روش پژوهش)**: Sample size, design, instruments.
   - **Results (یافته‌ها)**: Core empirical findings and statistics.
   - **Conclusions (نتیجه‌گیری)**: Implications.
   - **Keywords (کلیدواژه‌ها)**.
3. **Introduction & Literature Review (مقدمه و پیشینه نظری)**:
   - Frame the problem, theoretical foundations, and gaps in research.
4. **Methodology (روش‌شناسی پژوهش)**:
   - Participants & Procedure (جامعه، نمونه و روش اجرا).
   - Measures / Instruments (ابزارهای سنجش و پرسشنامه‌ها).
   - Statistical Analysis (روش تحلیل داده‌ها).
5. **Results (یافته‌ها و تحلیل آماری)**:
   - Descriptive statistics (آمار توصیفی).
   - Inferential statistics (آمار استنباطی: آزمون فرضیه‌ها، تحلیل واریانس، همبستگی، رگرسیون).
   - Tables translated with proper RTL alignment.
6. **Discussion & Limitations (بحث، نتیجه‌گیری و محدودیت‌ها)**:
   - Contextualize findings with prior literature, explain discrepancies, and state clinical/practical implications.

---

## 4. Deliverable Format

- **Primary Format (.docx Document)**:
  - All academic translations should be delivered as a Microsoft Word document (`.docx`), saved in the user's project folder (e.g., `[Original_Name]_fa.docx`).
  - **Document Styling Specifications**:
    - **Reading Order**: Right-to-Left (RTL / `w:bidi`) for all Persian paragraphs.
    - **Typography**: Persian standard fonts (B Nazanin, Vazirmatn, or Tahoma) at 13–14 pt with 1.15 line spacing.
    - **Headings**:
      - All document headings (`Heading 1`, `Heading 2`, `Heading 3`, `Heading 4`) must have **RTL text direction** (`<w:bidi/>`), **right-aligned with justify** (`<w:jc w:val="both"/>` or `<w:jc w:val="right"/>`), and `<w:rtl/>` on every run with Persian font (`B Titr` / `B Nazanin Bold`).
      - Title: 18 pt Bold, Center-aligned.
      - Heading 1 (فصل‌ها / بخش‌های اصلی): 16 pt Bold, Right-aligned with justify.
      - Heading 2 (زیربخش‌ها): 14 pt Bold, Right-aligned with justify.
      - Heading 3: 13 pt Bold, Right-aligned with justify.
    - **Tables, Charts & Figures**:
      - Must have `<w:bidiVisual/>` and `<w:tcBidi/>` in OpenXML.
      - All tables, charts, and figures must have native Microsoft Word captions created from `References > Insert Caption` (`SEQ جدول_... \* ARABIC` for tables and `SEQ شکل_... \* ARABIC` for figures/charts). Never strip or flatten caption fields into plain text.
    - **Footnotes & BiDi Line-Break Prevention (پانویس‌های استاندارد نیتیو و جلوگیری قطعی از شکستگی خطوط)**:
      - Footnotes must be generated as **true native OpenXML Word Footnotes** (`w:footnoteReference` in `word/document.xml` coupled with `word/footnotes.xml`), NOT raw bracket text (`[^...]`).
      - Word automatically places the footnote separator line and Latin citation text at the bottom of the exact page where the reference occurs.
      - **Critical Rule: Consistent `<w:rtl/>` on ALL Text Runs (جلوگیری از شکستن خط در محل پانویس)**:
        - **Problem**: If a Persian text run lacks `<w:rtl/>` while the footnote reference run contains `<w:rtl/>`, Word treats the paragraph as mixed LTR/RTL runs. In an RTL paragraph, this causes Word's layout engine to break the line prematurely at the footnote marker and scramble the visual order of surrounding phrases.
        - **Solution**: **Every single Persian text run** (`<w:r>`) must explicitly include `<w:rtl/>` in its `<w:rPr>`, alongside `<w:lang w:val="fa-IR" w:bidi="fa-IR"/>` and `<w:rFonts w:ascii="B Nazanin" w:cs="B Nazanin"/>`. This ensures 100% directional consistency and flawless inline flow across footnote markers.
      - **Paragraph Justification (`WD_ALIGN_PARAGRAPH.JUSTIFY`)**:
        - All body paragraphs containing Persian text and footnotes must have `<w:bidi/>` in `w:pPr` and be **Justified** (`<w:jc w:val="both"/>` or `paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY`). This prevents ragged margins and avoids premature line wrapping at punctuation/citation boundaries.
      - **Quote & Punctuation Placement with Footnotes**:
        - Footnote markers must always be positioned **immediately AFTER closing quotation marks or punctuation** (e.g. `«تفکر منفی تکرارشونده»[^15]`, never inside `«تفکر منفی تکرارشونده[^15]»`). Placing footnote runs inside quotation marks splits the quotation pair across runs, causing punctuation inversion and line-wrap glitches.
      - **Persian Numerals for Footnote Markers (اعداد فارسی در پانویس)**:
        - The footnote reference run (`<w:r>`) must include:
          - `<w:rStyle w:val="FootnoteReference"/>` (Footnote reference character style).
          - `<w:rFonts w:ascii="B Nazanin" w:hAnsi="B Nazanin" w:cs="B Nazanin"/>` (Complex script Persian font).
          - `<w:rtl/>` (Right-to-Left marker).
          - `<w:lang w:val="fa-IR" w:bidi="fa-IR"/>` (Persian locale 1065).
        - This guarantees that Word renders the in-text footnote number as an authentic **Persian numeral** (۱، ۲، ۳...) matching the Persian text flow.
      - **Modern Word Layout Engine (`compatibilityMode = 15`)**:
        - In `word/settings.xml`, ensure `<w:compatSetting w:name="compatibilityMode" ... w:val="15"/>` is set. This prevents modern versions of Microsoft Word (Word 2013, 2016, 2019, 2021, 365) from opening the document in legacy "Compatibility Mode", activating DirectWrite modern Bidi text shaping.
  - **Generation**: Use the bundled helper script [create_persian_docx.py](./scripts/create_persian_docx.py) which handles full native OpenXML footnote packing, consistent `w:rtl` run tagging, and Persian font injection.
- **Companion Markdown (.md)**:
  - An optional companion Markdown file (or chat preview) can be provided alongside the `.docx` for rapid review.
- **Bilingual Glossary Summary**:
  - Include a bilingual terminology table at the end of the document summarizing key psychological and statistical terms translated.
- See [Sample Translation Walkthrough](./examples/translation_sample.md) for benchmark quality standards.

---

## 5. Automatic Reference Extraction Alongside Translation (استخراج همگام منابع بخش‌های ترجمه‌شده)

When translating any academic paper, thesis chapter, or section, **always extract and save the section-specific bibliographic references concurrently or immediately following the translation**:

1. **Section Citation Harvesting**:
   - As the translation is composed, the footnoted citations provide a definitive catalog of works cited in that specific section.
2. **Filtering Against Master Bibliography**:
   - Using the companion skill [`academic-reference-extractor`](../academic-reference-extractor/SKILL.md), parse the source document's master bibliography and filter down **strictly to the works cited in the translated portion**.
   - Do NOT dump the entire 200–500 entry bibliography of the book/dissertation; export only the references for the translated section.
3. **Automatic Multi-Format Reference Generation**:
   - Concurrently generate and save three reference files in the user's translation directory:
     - **`.enw` (EndNote Import)**: `[Document_Name]_[Section]_References.enw`
     - **`.ris` (Universal RIS for Zotero / Mendeley / Citavi)**: `[Document_Name]_[Section]_References.ris`
     - **`.txt` (Formatted APA Reference List)**: `[Document_Name]_[Section]_References_APA.txt`
4. **Unified Delivery**:
   - In the final report, deliver direct clickable links to both:
     - The translation files (`.docx` with native Persian footnotes and companion `.md`).
     - The section reference files (`.enw`, `.ris`, and `.txt`).

