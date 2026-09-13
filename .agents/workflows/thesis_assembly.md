# Master Dissertation Compilation & Formatting Workflow (تدوین و یکپارچه‌سازی جامع رساله و پایان‌نامه)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for consolidating modular research documents (Chapters 1 through 5, psychometric scales, bilingual references, and institutional front matter) into a unified, publication-ready Persian master's thesis or doctoral dissertation (`.docx`) compliant with Iranian Graduate Council formatting regulations.

```text
                                     INPUT
               Modular Chapter Documents (Ch 1–5 .docx) + Template + Scales
               (Title, Candidate, Supervisors, University Guidelines)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │ Master Institutional Scoping │
                        │ (University Council Formats) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 2: RESULTS AUDITOR    │
                        │ Cross-Chapter Audit & Check  │
                        │ (Chapters Completeness & QC) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 3: ACADEMIC WRITER    │
                        │ Full Thesis Consolidation    │
                        │ (Front Matter, Ch 1-5, App.) │
                        │    (persian-thesis-builder)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 4: EVIDENCE AUDITOR   │
                        │ Unified Bibliography Engine  │
                        │ (Bilingual Persian & English)│
                        │ (academic-reference-extractor)
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 5: FINAL JUDGE      │
                        │ Graduate Council Compliance  │
                        │ Simulation (Approval 0-100)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 6: SABER HUMAN GATE    │
                        │ Admin Desk Approval Card     │
                        │     (ID: 124911145)          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • Complete_Graduate_Thesis.docx / Thesis_Compiled.docx
               • thesis_manifest.json (Compilation Ledger & Structural Specs)
```

---

## Prerequisites & Required Inputs

- **Modular Chapter Files**:
  - Chapter 1: Introduction & Problem Statement (`.docx`)
  - Chapter 2: Theoretical Foundations & Literature Review (`.docx`)
  - Chapter 3: Methodology & Instruments (`.docx`)
  - Chapter 4: Findings & APA 7 Tables (`.docx` from `statistical-data-analyst`)
  - Chapter 5: Discussion & Implications (`.docx` from `persian-discussion-builder`)
- **Institutional Metadata**:
  - University Name, Faculty, Department, Degree Level.
  - Candidate Name, Supervisors (*استاد راهنما*), Advisors (*استاد مشاور*).
  - Persian & English Thesis Titles.
  - Persian & English Abstracts.
- **Appendices & Instruments**:
  - Psychometric Scale Names (resolved against `Questionnaires.xlsx`).
  - Intervention Manuals / Protocols (if experimental).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Institutional Scoping)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests university formatting handbook specifications:
    - Fonts: `B Titr` for chapter headings (16–18 pt Bold), `B Nazanin` or `B Lotus` for body (13–14 pt), `Times New Roman` for Latin terms and numbers (10–11 pt).
    - Margins: Standard 3 cm inside (binding gutter), 2.5 cm outside, 3 cm top, 2.5 cm bottom.
    - Line Spacing: 1.15 to 1.3, Justified paragraphs.
- **Output**: Compilation structural plan and pagination roadmap.

### Step 2: Results Auditor Subagent (Cross-Chapter Integrity & Completeness)
- **Agent**: `results-auditor`
- **Action**:
  - Verifies presence and completeness of all 5 required chapters.
  - Ensures sequential numbering of tables (e.g. Table 4-1, Table 4-2) and figures (Figure 4-1).
  - Confirms native Word Math `<m:oMath>` formulas are intact and not stripped.
- **Output**: Chapter verification ledger and integrity approval.

### Step 3: Academic Writer Subagent (Master Document Synthesis)
- **Agent**: `academic-writer` (wielding `persian-thesis-builder`)
- **Action**:
  - Executes `compile_full_thesis.py` to construct the unified dissertation:
    1. **Front Matter**: Cover page (Persian), Bismillah page, Committee approval signature sheet, Dedication (*تقدیم*), Acknowledgements (*سپاسگزاری*), Persian Abstract with keywords.
    2. **Preliminary Lists**: Table of Contents, List of Tables, List of Figures, List of Abbreviations.
    3. **Chapter 1**: کلیات پژوهش (بیان مسئله، اهداف، فرضیه‌ها، تعاریف نظری و عملیاتی).
    4. **Chapter 2**: مبانی نظری و پیشینه پژوهش.
    5. **Chapter 3**: روش‌شناسی پژوهش (طرح، جامعه و نمونه، ابزارها، روش اجرا و تحلیل).
    6. **Chapter 4**: یافته‌های پژوهش (آمار توصیفی، بررسی مفروضه‌ها، آزمون فرضیه‌ها با جداول سه‌خطی APA 7).
    7. **Chapter 5**: بحث و نتیجه‌گیری (تبیین روان‌شناختی، پیشینه، کاربردها، محدودیت‌ها، پیشنهادها).
    8. **Appendices**: Standardized Likert questionnaire forms with scoring guidelines generated dynamically via `questionnaire_resolver`.
    9. **Back Matter**: English Abstract, English Title Page, and Back Cover.
- **Output**: Unified compiled dissertation document.

### Step 4: Evidence Auditor Subagent (Unified Bibliography Compilation)
- **Agent**: `evidence-auditor` (wielding `academic-reference-extractor`)
- **Action**:
  - Compiles unified bilingual reference lists:
    - Persian References: Alphabetical by Persian author surname, `B Nazanin` 11 pt, 0.5-inch hanging indent.
    - English References: Alphabetical by Latin author surname, `Times New Roman` 10 pt, 0.5-inch hanging indent.
  - Guarantees 100% bidirectional citation concordance across all 5 chapters.
- **Output**: Clean, unified references section inserted into master thesis.

### Step 5: Final Judge Subagent (University Council Compliance Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Simulates the University Graduate Council formatting audit:
    - Checks margin gutters, page numbering continuity (Abjad for preliminaries, Arabic numerals for body).
    - Checks table borders (zero vertical lines) and header formatting.
    - Evaluates Graduate Council Approval Probability Index (0–100%).
- **Output**: Compliance audit verdict (e.g. 98.5% Ready for Binding).

### Step 6: Digital Saber Human Gate Sign-Off (Admin Desk ID: 124911145)
- **Agent**: `digital-saber`
- **Action**:
  - Generates Admin Desk card for Saber Ghaderi (`124911145`).
  - Logs execution in `.agents/memory/decisions/dec_*.json` via `decision_journal_engine.py`.
  - Holds final client delivery pending one-click approval (`/approve_A401`).
- **Output**: Final approved dissertation ready for printing and viva voce defense.

---

## Deliverables Checklist

| # | Artifact | Description | Target Path |
|---|---|---|---|
| 1 | **`Complete_Graduate_Thesis.docx` / `Thesis_Compiled.docx`** | Complete 150-page master thesis / doctoral dissertation containing all front matter, Chapters 1–5, APA 7 tables, appendices, and bilingual back matter. | `output/` |
| 2 | **`thesis_manifest.json`** | Machine-readable compilation ledger (chapter word counts, table counts, figure counts, scales included, and council approval score). | `output/` |
