# Causal Root-Cause Analysis: BAN-20261001-TABLE-VARIABLE-SUBSCALE-COLUMNS-001

## 1. Identification
- **Analysis ID:** BAN-20261001-TABLE-VARIABLE-SUBSCALE-COLUMNS-001
- **Target Agent:** academic-writer
- **Target Skill:** chapter-4-writing
- **Failure Signature:** MERGED_VARIABLE_SUBSCALE_COLUMN

## 2. Root Cause Diagnosis
The structural presentation defect across Chapter 4 tables (e.g., Table 4-13, Table 4-15) is caused by flattening hierarchical variable data into a single column. The generation script (`compile_gold_standard_chapter4.py`) and markdown outputs combine row numbers, parent variables, and subscales into one column, such as `["متغیرها"]` or `["متغیر/سازه"]`. This occurs because the initial data structures and formatting logic omitted separate semantic columns for hierarchy, violating presentation standards (e.g., AP-2026-FLAT-OR-UNGROUPED-VARIABLE-SUBSCALE-TABLES).

## 3. Prescribed Behavior
All agents generating or compiling academic tables MUST enforce a strict 3-column prefix structure for descriptive, correlational, and inferential tables:
1. **Column 1:** `ردیف` (Sequential row index)
2. **Column 2:** `متغیر` (Parent Construct / Variable)
3. **Column 3:** `مؤلفه` (Subscale name, or 'نمره کل' for total)

**Specific Corrections:**
- In `02_analysis_code/compile_gold_standard_chapter4.py`: Update Table 4-15 to use 13 columns with headers `['ردیف', 'متغیر', 'مؤلفه', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹', '۱۰']`.
- Apply equivalent column expansions and mapping to Tables 4-16, 4-19, and 4-13.
- In all Markdown deliverables (`Chapter_4_Results.md`, `02_descriptives_and_reliability.md`, `04_correlations.md`), mechanically separate flattened variable/subscale columns into distinct `متغیر` and `مؤلفه` columns.
