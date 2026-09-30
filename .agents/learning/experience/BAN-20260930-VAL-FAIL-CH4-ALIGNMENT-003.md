# Behavior Analysis Report: BAN-20260930-VAL-FAIL-CH4-ALIGNMENT-003

## Overview
**Target Agent**: `academic-writer`
**Target Skill**: `chapter-4-writing`
**Observable Failure Step**: Global Validation Audit
**Failure Signature**: `VIOLATED_ASSUMPTION_IGNORED`

## Root Cause Diagnosis
1. **CHK-BIDI-ALIGNMENT-INVERSION**: The compilation script (`compile_gold_standard_chapter4.py`) explicitly injects `<w:jc w:val="right"/>` for Persian headings (e.g., in `post_process_openxml` and `add_h*` functions). This violates the OpenXML BiDi Golden Rule outlined in the standards manual, which strictly requires omitting `w:jc` for right alignment under RTL to prevent the trailing-edge flip bug in Word rendering.
2. **CHK-NARRATIVE-JUSTIFICATION**: Paragraphs copied from the `Chapter_4_Preamble_Source.docx` retained their original flawed left/right alignment. The `post_process_openxml` function failed to enforce `<w:jc w:val="both"/>` (justification) on these narrative paragraphs, leaving 35 paragraphs ragged.
3. **CHK-TABLE-BIDI-DIRECTION**: In `post_process_openxml`, the script used `tblPr[0].append(...)` to add `<w:bidiVisual/>`. `append` places the element at the very end of the children list (after `<w:tblW>`), which violates the strict `CT_TblPr` child sequencing rules in OpenXML.
4. **CHK-ENGLISH-WORD-LEAKAGE**: English acronyms (e.g., IUS, SCI, Ref) residing in Table 1 of the preamble source were not translated or sanitized to formal Persian when the elements were copied into the final deliverable.
5. **CHK-CHAPTER5-PROSE-ONLY**: A false positive was triggered in `academic_chapter_auditor.py` because the string "فصل پنجم" appeared in the Section 8-4 heading (bridge to Chapter 5). The auditor brittlely inferred that the document was Chapter 5 and inappropriately applied the Prose-Only (zero tables) rule to Chapter 4.

## Prescribed Counterfactual Behavior
1. **Fix BiDi Alignment**: Modify `compile_gold_standard_chapter4.py` to completely omit `<w:jc w:val="right"/>` for headings. Ensure it only injects `<w:bidi w:val="1"/>`. In `post_process_openxml`, if a `<w:jc>` node is present in an RTL right-aligned paragraph, it must be removed.
2. **Enforce Narrative Justification**: Update `post_process_openxml` to detect substantive narrative paragraphs (excluding headings/table captions) and strictly enforce `<w:jc w:val="both"/>`.
3. **Correct Table BiDi Sequencing**: Modify the table processing in `post_process_openxml` to use `tblPr[0].insert(0, ...)` instead of `append` so that `<w:bidiVisual/>` correctly precedes `<w:tblW>` and adheres to ECMA-376 sequencing.
4. **Sanitize English Acronyms**: Implement a translation map / regex substitution during the copy phase to convert English acronyms to their Persian equivalents (e.g., "IUS" -> "عدم‌قطعیت").
5. **Refine Auditor Regex**: Update `academic_chapter_auditor.py` to distinguish between a genuine Chapter 5 title and a transitional heading within Chapter 4, preventing false triggering of Chapter 5 invariants.
