# Behavior Analysis Report: BAN-20261001-TABLE-LTR-ONLYOFFICE-001

## 1. Identification
- **Analysis ID**: `BAN-20261001-TABLE-LTR-ONLYOFFICE-001`
- **Target Agent**: `academic-writer` & `validation-agent`
- **Target Skill**: `academic-suite-orchestrator` & `thesis-integrity-auditor`
- **Observable Failure Step**: Steps 8 and 12

## 2. Failure Signatures
- `XML_OBJECT_REUSE_ATTRIBUTE_LEAKAGE`
- `VALIDATOR_BLINDSPOT_ATTR_LEN`
- `ACTIVE_DOCUMENT_LOCK_DESYNC`

## 3. Root Cause Diagnosis
In `02_analysis_code/compile_gold_standard_chapter4.py` (Step 8), the `post_process_docx_zip` function evaluated preamble tables that already contained `<w:bidiVisual w:val='1'/>`. The code removed this element from the DOM (`tblPr.remove(bidi)`) but then directly re-inserted the exact same `xml.etree.ElementTree.Element` object (`tblPr.insert(tblW_idx, bidi)`) without clearing its `.attrib` dictionary. This resulted in the leakage of `w:val='1'` into the compiled DOCX. Consequently, ONLYOFFICE rejected the attribute as invalid for an `OnOffOnlyType` element, causing the table to fallback to Left-to-Right orientation.

Simultaneously, the script ignored the presence of an active lock file (`.~lock.Chapter_4_Results.docx#`) indicating that ONLYOFFICE held the document open, preventing the GUI from hot-reloading the updated disk state.

In Step 12, `validation-agent` using `academic_chapter_auditor.py` passed the defective table because the `CHK-TABLE-BIDI-DIRECTION` check merely verified the presence and relative ordering of `<w:bidiVisual>`, but failed to assert that its attribute length must be exactly zero (`len(bidi.attrib) == 0`).

## 4. Prescribed Counterfactual Behavior
1. **XML Attribute Sanitization**: In `compile_gold_standard_chapter4.py`, the code must explicitly call `bidi.attrib.clear()` before re-inserting the reused `bidiVisual` object, or alternatively, construct a completely fresh `ET.Element(f"{{{NS['w']}}}bidiVisual")` for every table, abandoning the old object entirely.
2. **Validator Strictness**: In `academic_chapter_auditor.py`, the `CHK-TABLE-BIDI-DIRECTION` check must be upgraded to enforce `assert len(bidi.attrib) == 0` (or logically fail if any attributes are present on `<w:bidiVisual>`), thereby eliminating the auditing blindspot.
3. **Concurrency Safety**: The compilation script should preemptively check for the existence of `.~lock` files for the target deliverable, aborting or warning if the file is actively locked by a desktop GUI editor to prevent silently working against an out-of-sync cache.
