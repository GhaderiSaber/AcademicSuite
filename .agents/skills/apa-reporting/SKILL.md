---
name: apa-reporting
description: Generate strictly formatted APA 7th Edition 3-line tables, enforce statistical symbol italicization, Persian leading zero standard (۰.۰۰۱), and OpenXML LTR numeric decoupling.
---

# APA Reporting Skill

This skill formats statistical results, tables, and in-text metrics into institutional APA 7th Edition standards with authentic Persian academic typography and OpenXML BiDi compliance.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Converting raw statistical results (`.json`) into APA 7th Edition Markdown or Word tables.
- Enforcing the 3-line horizontal border standard (zero vertical borders).
- Formatting statistical metrics in narrative text (*M, SD, t, F, p, r, β, η², z*).
- Applying the Persian leading zero standard (`۰.۰۰۱`, `۰.۰۵`) and dot decimal delimiter (`.`).
- Decoupling numbers to LTR (`rtl="0"`) with `Times New Roman` in OpenXML tables so negative signs precede numbers ($-0.32$).

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- The task is calculating statistical tests, models, or effect sizes $\to$ use `statistical-data-analyst`, `regression`, `mediation`, or `sem`.
- The task is auditing thesis consistency across chapters $\to$ use `thesis-integrity-auditor`.
- The task is compiling a complete 5-chapter thesis document $\to$ use `persian-thesis-builder`.

## 3. REQUIRED DATA
- **Input Data**: Structured statistical JSON containing parameter estimates, degrees of freedom, $p$-values, effect sizes, and descriptive statistics.
- **Target Language**: Persian (`fa`) or English (`en`).
- **Target Format**: Markdown table (`.md`) or Word OpenXML (`.docx`).

## 4. ASSUMPTIONS
1. **Zero Vertical Borders**: Tables must have exactly three horizontal borders (top, header bottom, table bottom); vertical borders are prohibited.
2. **Symbol Italicization**: Latin statistical letters (*M, SD, t, F, p, r, R², β, B, z, SE, df, n, N*) must be italicized. Greek letters (*α, β, η², χ²*) remain regular.
3. **Decimal Precision**: Test statistics, means, SDs to 2 decimals ($M = 24.35, t = 3.88$); $p$-values to exactly 3 decimals ($p = .014$).
4. **Leading Zero Rule**:
   - English APA: Omit leading zero for numbers bounded by 0 and 1 ($p = .023, r = .48$).
   - Persian Academic Standard: NEVER omit leading zero in Persian (`۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`). Writing `.۰۰۱` or `.۰۵` is prohibited.
5. **No p = .000**: Output of $.000$ must be reported strictly as $p < .001$ (`p < ۰.۰۰۱` یا `۰.۰۰۱ > p`).

## 5. TABLE OPENXML SPECIFICATIONS
- **Table Captions**: Right-aligned (`<w:jc w:val="right"/>`) with `<w:bidi w:val="1"/>`.
- **Column 1 (labels)**: Right-aligned (`<w:jc w:val="right"/>`) with `<w:bidi w:val="1"/>`.
- **Columns 2+ (numeric statistics)**: Centered (`<w:jc w:val="center"/>`).
- **Table container**: Centered on page.
- **Notes**: Justified (`<w:jc w:val="both"/>`).

## 6. DECISION TREE

```
APA 7 Reporting & Table Formatting
  │
  ├─► Target Language:
  │     ├─► Persian (Farsi):
  │     │     ├─► Decimal Delimiter: Standard dot (۰.۰۵, never ۰/۰۵)
  │     │     ├─► Leading Zero: MANDATORY (۰.۰۰۱, ۰.۰۵, never .۰۰۱ or .۰۵)
  │     │     ├─► Directionality: RTL table (<w:bidiVisual/>)
  │     │     └─► Numeric Decoupling: LTR (rtl="0") + Times New Roman for negative values (-0.32)
  │     │
  │     └─► English:
  │           ├─► Numbers bounded by 0 and 1: Omit leading zero (p = .023, r = .48, R² = .34)
  │           └─► Unbounded numbers: Retain leading zero (t = 2.45, F = 12.30, M = 0.85)
  │
  ├─► Table Structure:
  │     ├─► Zero vertical gridlines
  │     ├─► Top border: 0.75 pt solid
  │     ├─► Header bottom border: 0.50 pt solid
  │     └─► Table bottom border: 0.75 pt solid
  │
  └─► Statistical Symbols:
        ├─► Latin Letters: Italic (*M, SD, t, F, p, r, β, z, SE, df, n, N*)
        └─► Greek Letters: Regular (α, β, η², χ²)
```

## 7. EXECUTION SCRIPT
Determinism table scaffolding script:
```bash
python3 .agents/skills/apa-reporting/scripts/scaffold_apa_tables.py \
  --input "stats_results.json" \
  --output "apa7_table.md"
```

## 8. OUTPUT CONTRACT
The skill produces:
- Physical APA 7 markdown table (`apa7_table.md`) or Word table with 3 horizontal borders:
  ```markdown
  ### جدول ۱. شاخص‌های توصیفی و استنباطی متغیرهای پژوهش (APA 7th Edition)

  | متغیر | میانگین (*M*) | انحراف استاندارد (*SD*) | آماره آزمون (*t*) | درجات آزادی (*df*) | سطح معناداری (*p*) |
  |:---|:---:|:---:|:---:|:---:|:---:|
  | تاب‌آوری | ۲۴.۳۵ | ۴.۱۸ | ۳.۸۸ | ۵۸ | ۰.۰۰۱ > |
  | اضطراب فراگیر | ۱۸.۱۲ | ۳.۷۲ | — | — | — |

  *یادداشت.* سطح معناداری در سطح ۰.۰۵ ارزیابی شده است. اعداد آماری با فونت Times New Roman و متن فارسی با B Nazanin تنظیم شده‌اند.
  ```

## 9. VALIDATION
- Verify presence of exactly 3 horizontal borders and zero vertical borders.
- Check that all Latin statistical abbreviations are italicized.
- In Persian deliverables, verify zero missing leading zeros (`.۰۵` or `.۰۰۱` are violations).
- Ensure no instance of $p = .000$ exists in the report.
- Verify that negative statistics have the minus sign preceding the number ($-0.32$, not $0.32-$).

---

## 10. INSTITUTIONAL INVARIANTS & PREVIOUS LESSONS GRADUATED

### 10.1 Correlation Matrix 3-Column Header Standard
All bivariate correlation matrices must begin with three fixed label columns before matrix values:
- **Column 1**: `ردیف` (1, 2, 3...)
- **Column 2**: `متغیر` (Parent construct name)
- **Column 3**: `مؤلفه` / `خرده‌مقیاس` (Subscale name, or empty for unidimensional constructs)
Followed by numbered matrix columns (`۱`, `۲`, `۳`, ...) containing correlation coefficients.

### 10.2 Significance Asterisk Strict Boundary
- Significance asterisks (`* p < ۰.۰۵`, `** p < ۰.۰۱`, `*** p < ۰.۰۰۱`) are **strictly and exclusively restricted to correlation matrices**.
- **Zero Asterisks Rule**: Descriptives, ANOVA, regression coefficients, collinearity, assumption tests, and demographic tables must report exact $p$-values with **zero asterisks** on cells, labels, or variable names.

### 10.3 Pure Numeric $p$-Values in Table Cells
- Never repeat the symbol `p` inside table cells (e.g. `p = ۰.۰۱` or `p < ۰.۰۰۱`).
- Since the table header already defines the column as $p$ or `سطح معناداری (p)`, cell content must be strictly numeric (`۰.۰۰۱`, `۰.۰۴۵`, or `> ۰.۰۰۱`).

### 10.4 Hierarchical Variable Layout & Composite Row Invariant
- For instruments with parent variables and subscales, use a two-column structure: Column 1 = `متغیر`, Column 2 = `مؤلفه`.
- **Composite Row Invariant**: The overall/composite metric of the parent variable must be placed **directly on the parent variable row** (Col 1 = Variable name, Col 2 = blank, Cols 3+ = total score $M, SD$, etc.). Subscales are listed on subsequent rows in Col 2.
- Creating an empty parent row followed by a separate redundant "نمره کل" or "مجموع" row at the bottom is strictly prohibited.

### 10.5 Persian Thesis Table Numbering Standard
- Table numbers in Persian theses must place the chapter number first followed by hyphen and table number: `جدول [فصل]- [شماره]` (e.g. `جدول ۴- ۱`, `جدول ۴- ۳۱`). Inverted numbering (`جدول ۱- ۴`) is prohibited.

### 10.6 Table Caption Typography & Placement
- Table captions must be formatted in **12 pt B Nazanin Regular** (non-bold, never `B Titr`).
- Narrative text introducing the table must always precede the table caption; never place narrative findings explanations under the table where the note belongs.

### 10.7 Zero Blank Lines Between Table and Note
- The table note (`*یادداشت.* ...`) must immediately follow the bottom border of the table without an intervening empty line or blank paragraph mark.

### 10.8 Conceptual Construct Purity
- Variable names in tables must represent pure conceptual constructs (e.g. `خودآسیبی`, `افسردگی`), strictly stripped of operational instrument nouns (`پرسشنامه`, `مقیاس`, `سیاهه`) and author surnames.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-TABLE-APA-SYMBOLS-AND-PERSIAN-NOTES-001)**: Use standard APA statistical symbols (M, SD, SE, F, t, p, R, R², B, β, OR, χ², df, SS, MS, DW, VIF, Tol) in table header cells; provide Persian definitions in table notes; enforce zero raw English words in Persian body text; include comprehensive introduction at chapter start and comprehensive summary at chapter end. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-REGRESSION-ANOVA-ROW-LABELS-001)**: In all regression ANOVA tables (خلاصه مدل و تحلیل واریانس), format source of variance rows as: [Variable Name], 'باقیمانده', 'کل' for each criterion variable, strictly omitting parenthetical variable names on residual and total rows. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-COMPREHENSIVE-ACADEMIC-PROSE-STANDARD-001)**: Apply global academic prose refinement across all chapters, ensuring unified syntax, past-tense empirical consistency, and natural narrative transitions while preserving exact statistical ground truth. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-REGRESSION-ANOVA-OPTION-A-STANDARD-001)**: In all regression ANOVA tables with multiple criterion variables, use a two-column structure: Column 1 ('متغیر ملاک') and Column 2 ('منبع تغییرات' with 'رگرسیون', 'باقیمانده', 'کل'). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-QUESTION-HYPOTHESIS-HEADINGS-AND-CLEAN-DOCX-001)**: Enforce 'سوال اول: ...' and 'فرضیه اول: ...' section titles, clean non-redundant subheadings, and complete elimination of raw markdown artifacts in Word output. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-MANDATORY-BLANK-LINE-BEFORE-HEADINGS-001)**: Ensure an explicit blank line precedes every heading across Markdown source and Word DOCX deliverables. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-OPENXML-ALIGNMENT-SCHEMA-001)**: Use python-docx native enums (p.alignment = WD_ALIGN_PARAGRAPH.RIGHT/CENTER/JUSTIFY) and never append loose <w:jc> tags at the end of <w:pPr>. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-STARS-ONLY-IN-CORRELATION-TABLES-001)**: Restrict asterisk usage in tables exclusively to correlation matrices; purge all asterisks from non-correlation table cells, headers, and notes. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-TABLE-NUMBERING-CHAPTER-FIRST-001)**: Number all thesis tables with chapter first: 'جدول [فصل]- [شماره]' (e.g. 'جدول ۴- ۳۱'). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-VARIABLE-COMPOSITE-ROW-INVARIANT-001)**: Always populate parent variable rows with overall/composite metrics; never create an empty parent row followed by a separate 'total' row. [Enforcement: results_auditor_guard.py]