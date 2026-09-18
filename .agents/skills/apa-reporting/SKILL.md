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

## 5. DECISION TREE

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

## 6. EXECUTION SCRIPT
Deterministic table scaffolding script:
```bash
python3 .agents/skills/apa-reporting/scripts/scaffold_apa_tables.py \
  --input "stats_results.json" \
  --output "apa7_table.md"
```

## 7. OUTPUT CONTRACT
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

## 8. VALIDATION
- Verify presence of exactly 3 horizontal borders and zero vertical borders.
- Check that all Latin statistical abbreviations are italicized.
- In Persian deliverables, verify zero missing leading zeros (`.۰۵` or `.۰۰۱` are violations).
- Ensure no instance of $p = .000$ exists in the report.
- Verify that negative statistics have the minus sign preceding the number ($-0.32$, not $0.32-$).
