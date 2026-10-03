# Behavior Analysis Report: BAN-20261003-CH1-DOM-CORRUPTION-001

## 1. Meta-Information
- **Analysis ID**: BAN-20261003-CH1-DOM-CORRUPTION-001
- **Target Agent**: `academic-writer`, `validation-agent`
- **Failure Signature**: `UNSCOPED_SECTION_INJECTION_AND_COLLATERAL_DELETION`

## 2. Root Cause Diagnosis
The trajectory analysis reveals three primary causal mechanisms for the Chapter 1 structural corruption:

1. **Unscoped Multi-Section Markdown Injection**: The `academic-writer` injected the entirety of `revision_ch1_intro.md` as a single, monolithic block directly into the "Problem Statement" section. Because this markdown file contained multiple sub-sections (Chapter Heading, Problem Statement, Conceptual Definitions), they were structurally misaligned and forced into the wrong document hierarchy.
2. **Collateral Section Destruction**: To resolve duplicate "Conceptual Definitions," the `academic-writer` executed a blanket wipe of the Key Terms section (`clear_section` targeting everything between "تعاریف واژه ها و اصطلاحات کلیدی" and "فصل دوم"). This indiscriminately obliterated the "Operational Definitions" (`تعاریف عملیاتی`), which were strictly required but not present in the revision text.
3. **Structural Order Blindspot in Validator**: The `validation-agent` constructed a flawed validation test (`validate_thesis_revision.py`) that performed unordered bag-of-words checks (substring presence) on flattened XML strings. It entirely neglected the canonical document structure, heading sequences, and the existence of the operational definitions, leading to a false positive `PASS`.

## 3. Prescribed Behavior
To ensure correct behavior and prevent recurrence of this failure mode, the agents must adopt the following invariants:

1. **Surgical DOM Section-by-Section Replacement**: Agents must parse multi-section markdown documents and map them discretely to their exact OpenXML heading counterparts. Monolithic text dumps are prohibited.
2. **Strictly Bounded Deletions**: Deletion operations within the DOM must specifically target the intended node (e.g., only erasing "Conceptual Definitions") and structurally preserve all adjacent, collateral sub-sections (e.g., "Operational Definitions") unless explicit replacement content is provided.
3. **Rigorous Structural Validation**: Validation protocols must perform DOM-aware parsing to enforce the correct sequence of headings, verify paragraph styles, and explicitly assert the presence of critical document sections (such as Operational Definitions) instead of relying on rudimentary unstructured string searches.
