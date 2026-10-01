# Causal Root-Cause Analysis: BAN-20261001-TABLE-VARIABLE-SUBSCALE-COLUMNS-001

## 1. Meta-Information
- **Task ID**: TSK-2026-LEARN-BAN-007
- **Trajectory ID**: TRJ-20261001-TABLE-VARIABLE-SUBSCALE-COLUMNS-001
- **Target Agent**: `academic-writer`
- **Target Skill**: `chapter-4-writing`
- **Capability**: `CHAPTER4`
- **Trigger**: USER_FEEDBACK (FDB-20261001-TABLE-001)

## 2. Diagnosis Details
**What behavior was wrong?**
The agents responsible for generating markdown tables and compiling the final `docx` using `compile_gold_standard_chapter4.py` concatenated distinct hierarchical metadata into single table columns. They embedded sequential row numbers directly into strings (e.g. `۱. اضطراب آینده‌نگر`) and merged parent construct names with child subscales into catch-all columns (e.g., `متغیر/سازه` or `متغیرها`), destroying visual taxonomic separation.

**Failure Signatures Analyzed:**
- `AP-2026-CORRELATION-TABLE-SINGLE-LABEL-COLUMN`
- `AP-2026-FLAT-OR-UNGROUPED-VARIABLE-SUBSCALE-TABLES`

**Root Cause:**
The architectural schema defined for Tables 4-13, 4-15, 4-16, and 4-19 neglected the explicit requirement for a decoupled 3-column prefix. The agent lacked an invariant explicitly forbidding string concatenation of row indexes and subscales. 

## 3. Prescribed Counterfactual Behavior
To resolve this defect canonically across all Chapter 4 deliverables and Python generation code:
1. **Mandatory 3-Column Prefix**: Every table displaying hierarchical psychological constructs must begin with 3 explicit, independent columns:
   - **Column 1 (`ردیف`)**: Sequential Persian row index (e.g. `۱`).
   - **Column 2 (`متغیر`)**: Parent variable/construct name (e.g. `تحمل‌ناپذیری عدم‌قطعیت`).
   - **Column 3 (`مؤلفه`)**: Subscale/dimension name (e.g. `اضطراب آینده‌نگر`). Use `نمره کل` for composite totals.
2. **Zero In-String Concatenation**: Row numbers must never be embedded into variable text strings.
3. **Script Modification**: Expand table array dimensions in `02_analysis_code/compile_gold_standard_chapter4.py` (e.g. Table 4-15 columns must be increased from 11 to 13, and Table 4-16 from 4 to 6 columns).
