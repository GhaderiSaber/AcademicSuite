# Behavior Analysis Report: BAN-20260930-VAL-FAIL-CH4-ALIGNMENT-001

## 1. Meta-Information
- **Analysis ID:** BAN-20260930-VAL-FAIL-CH4-ALIGNMENT-001
- **Target Agent:** `statistics-agent`
- **Target Skill:** `chapter-4-writing`
- **Observable Failure Step:** Step 4: Execute Chapter 4 findings compilation (`compile_gold_standard_chapter4.py`)

## 2. Failure Signature
`VIOLATED_ASSUMPTION_IGNORED`

## 3. Root Cause Diagnosis
The validation failure is the result of five distinct causal mechanisms within `compile_gold_standard_chapter4.py` and the validation pipeline:

1. **BiDi Alignment Inversion (Contradictory Instructions)**
   - **Mechanism:** The script explicitly injected `<w:jc w:val="right"/>` into headings and titles within `add_h1`, `add_h2`, `add_table_title`, and `post_process_openxml`.
   - **Causality:** It followed an erroneous active lesson (`LSN-2026-EXPLICIT-RIGHT-ALIGNMENT`) which directly violated the OpenXML BiDi Golden Rule. Under Word's BiDi engine, adding `<w:bidi w:val="1"/>` sets the leading edge to Right. Adding `<w:jc w:val="right"/>` forces a trailing-edge flip, causing left-alignment.
   
2. **Narrative Justification Omissions**
   - **Mechanism:** Paragraphs copied verbatim from `Chapter_4_Preamble_Source.docx` were not justified in their source state.
   - **Causality:** The `post_process_openxml` function traversed the document to enforce headings and font bindings but lacked any logic to enforce `<w:jc w:val="both"/>` on substantive Persian narrative paragraphs.

3. **Untranslated English Acronyms in Table 1**
   - **Mechanism:** Table 1 originated from the imported preamble document which contained English acronyms (`IUS`, `SCI`, `Ref`).
   - **Causality:** The `post_process_openxml` DOM traversal inspected runs for raw markdown and font binding but entirely lacked a translation/sanitization pass to detect and replace English leakage in table cells.

4. **Table `bidiVisual` Schema Sequence Error**
   - **Mechanism:** The script used `tblPr[0].append(bidi)` in both `apply_table_apa7_and_bidi` and `post_process_openxml`.
   - **Causality:** `append()` places the element at the end of the `<w:tblPr>` node, whereas the strict ECMA-376 schema requires `<w:bidiVisual/>` to precede `<w:tblW>` and `<w:tblBorders>`.

5. **Chapter 5 Validator Misclassification**
   - **Mechanism:** The `CHK-CHAPTER5-PROSE-ONLY` check failed, indicating the validator thought the Chapter 4 document was Chapter 5.
   - **Causality:** The `academic_chapter_auditor` uses heuristic text matching. It likely misclassified the document by matching the section number "۵-۴" (5-4) or the filename `10_hypothesis_5.md` ("Hypothesis 5"), triggering the Chapter 5 checks erroneously.

## 4. Prescribed Counterfactual Behavior
To resolve these defects, the following counterfactual behaviors must be mechanically enforced:

- **Resolve BiDi Alignment:** Modify `compile_gold_standard_chapter4.py` to completely strip all `<w:jc>` tags from RTL headings, table titles, and inside `post_process_openxml`. Enforce `<w:bidi w:val="1"/>` exclusively to achieve natural right alignment.
- **Enforce Narrative Justification:** Update `post_process_openxml` to identify regular Persian text paragraphs (non-headings, non-tables) and explicitly inject `<w:jc w:val="both"/>` if it is missing.
- **Sanitize Preamble Acronyms:** Introduce a dictionary-based translation substitution array in `post_process_openxml` (e.g., replacing 'IUS' with its formal Persian construct) when processing runs within table cells.
- **Correct Element Sequence:** Replace `tblPr[0].append(bidi)` with `tblPr[0].insert(0, bidi)` to ensure `<w:bidiVisual w:val="1"/>` is placed as the first child element of `<w:tblPr>`.
- **Patch Validator Heuristics:** The `academic_chapter_auditor` script must be updated. The stage detection heuristic should rely on explicit metadata or strict title matching (e.g., matching exactly "فصل پنجم" rather than solitary instances of the number 5).
