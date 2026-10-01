# Behavior Analysis Report: BAN-20261001-WORD-TABLE-RTL-DIRECTION-001

## Metadata
- **Analysis ID:** BAN-20261001-WORD-TABLE-RTL-DIRECTION-001
- **Trajectory ID:** TRJ-20261001-WORD-TABLE-RTL-DIRECTION-001
- **Trigger:** USER_FEEDBACK (FDB-20261001-WORD-TABLE-RTL-DIRECTION-001)
- **Target Agent:** academic-writer
- **Target Skill:** chapter-4-writing
- **Capability:** CHAPTER4

## 1. What behavior was wrong? (Causal Root-Cause Diagnosis)
The compilation script `02_analysis_code/compile_gold_standard_chapter4.py` and its subsequent patches failed to correctly construct the OpenXML DOM for Right-to-Left (RTL) tables across four architectural layers. This quad-defect resulted in Microsoft Word desktop GUI displaying "Left-to-right" instead of "Right-to-left" for all tables.
The exact failures were:
1. **OPENXML_ONOFFONLY_ATTRIBUTE_ERROR**: The script injected `<w:bidiVisual w:val='1'/>` instead of the empty element `<w:bidiVisual/>`. The Word GUI deserializer rejects the unexpected `w:val` attribute on this OnOffOnlyType element.
2. **SECTPR_OUT_OF_ORDER_BIDI**: In `<w:sectPr>`, the compiler appended `<w:bidi/>` after `<w:docGrid/>` or omitted it entirely. OpenXML schema strictly dictates that `<w:bidi/>` must precede `<w:docGrid/>`. This sequencing violation caused section-level LTR fallback.
3. **SETTINGS_MISSING_BIDI_LOCALE**: The script only modified `word/document.xml` and ignored `word/settings.xml`, thereby omitting the required `<w:themeFontLang w:bidi='fa-IR'/>` and modern compatibilityMode, failing to configure document-wide Persian RTL context.
4. **CELL_PARAGRAPH_BIDI_OMISSION**: The script only applied `<w:bidi w:val='1'/>` to paragraphs longer than 80 characters or headings. Table cell paragraphs were bypassed, depriving them of mandatory RTL text flow context.

Furthermore, the validator `academic_chapter_auditor.py` possessed a blindspot, explicitly permitting `w:val="1"` on `<w:bidiVisual>`, falsely passing the document.

## 2. Prescribed Counterfactual Behavior
To ensure correct RTL table direction in Microsoft Word, compilers and validators must enforce the following exact behaviors:
1. **Table Property Layer**: Compilers must inject the empty `<w:bidiVisual/>` element (without the `w:val` attribute) into `<w:tblPr>`. Validators must explicitly reject `<w:bidiVisual>` elements that contain a `w:val` attribute.
2. **Section Property Layer**: Compilers must guarantee that `<w:bidi/>` is inserted in correct schema sequence inside `<w:sectPr>`, specifically prior to `<w:docGrid/>`.
3. **Document Settings Layer**: Compilers must unpack and update `word/settings.xml` to include `<w:themeFontLang w:bidi='fa-IR'/>` and `<w:compatSetting w:name='compatibilityMode' w:val='15'/>`.
4. **Cell Paragraph Layer**: Compilers must inject `<w:bidi w:val='1'/>` into the `<w:pPr>` of every single paragraph within a table cell, regardless of character length or heading status.
