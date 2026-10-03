# Root-Cause Causal Diagnosis: BAN-20261003-TABLE-NOTE-ENGLISH-LEAKAGE-001

## 1. Meta-Information
- **Analysis ID:** BAN-20261003-TABLE-NOTE-ENGLISH-LEAKAGE-001
- **Trajectory ID:** TRJ-20261003-TABLE-NOTE-ENGLISH-LEAKAGE-001
- **Target Agent:** `academic-writer`
- **Target Skill:** `apa-reporting`
- **Failure Signature:** `OMITTED_PERSIAN_TRANSLATION_AND_PREFIX`

## 2. Observable Failure Step
- **Step Number:** 135
- **Action Type:** Document Compilation
- **Description:** Table element 135 note and Table 22 header were generated without checking for the mandatory 'یادداشت:' prefix and leaving untranslated English text 'Bentler'.

## 3. Root Cause Diagnosis
The defect occurred because the deserialized table note from `05_macro_model.json` ('N = ۴۸۳. برآورد با روش حداکثر...') was passed directly to `add_table_note` without defensive prefix enforcement. Furthermore, the raw header containing the English word 'Bentler' was injected directly into OpenXML and Markdown without transliterating it to formal academic Persian ('هو و بنتلر، ۱۹۹۹'). This violates Directive 5 regarding Zero inline Latin script in Persian narrative.

## 4. Prescribed Counterfactual Behavior
Enforce defensive validation prior to document compilation:
1. Automatically prepend the 'یادداشت: ' prefix to table notes if missing.
2. Perform strict transliteration of English author names (e.g., 'Bentler' to 'هو و بنتلر، ۱۹۹۹') before injecting text strings into Markdown or OpenXML deliverables, enforcing zero inline Latin script within Persian tables/narratives.
