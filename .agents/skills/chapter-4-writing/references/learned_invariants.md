
### Invariant LSN-20260925-A4DD06 (20260925_180802)
- **Category**: Lesson
- **Rule**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~583/600 tokens (97.2%)]
- **Target Capability**: `CHAPTER4` | **Task**: `chapter_4_drafting` | **Agent**: `academic-writer` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- [AP-2026-RAW-MARKDOWN-LEAKAGE-AND-REDUNDANT-HEADERS] Avoid: Allowing raw markdown syntax (>, ---, markdown links, unmatched asterisks) to leak into Word DOCX deliverables, using ambiguous question/hypothesis titles, or repeating headers like 'پایه تحصیلی (*پایه تحصیلی*)'.
  Approved Remedy: Enforce strict heading naming standard ('سوال اول: ...', 'فرضیه اول: ...'), strip parenthetical duplicates, remove raw markdown tokens from markdown source, and equip the OpenXML renderer with robust parsing.
- [AP-2026-ISOLATED-PROSE-POLISHING] Avoid: Fixing prose style only in isolated paragraphs flagged by the user while leaving the remaining sections in an unrefined, mechanical state.
  Approved Remedy: When an academic tone issue is flagged, conduct a global chapter-wide sweep to apply the validated scholarly standard across all sections uniformly.
- [AP-2026-VERBOSE-PERSIAN-TABLE-HEADERS] Avoid: Writing clumsy verbose Persian terms in table metric headers (e.g. مجموع مجذورات (SS)) instead of standard APA Latin symbols, or leaving raw English words scattered in Persian narrative.
  Approved Remedy: Use concise APA Latin symbols in table headers, define them in Persian in the note, and ensure pure Persian prose without raw English words.

💡 Relevant Active Lessons:
- [LSN-2026-PERSIAN-SCRIPT-ONLY-WITH-ENGLISH-FOOTNOTES-001] Mandate: Enforce zero Latin script in Persian body text. Transliterate all author names to Persian, use Persian equivalents for technical terms, and provide original English text strictly via footnotes.
  Generalization: Running Persian academic text must strictly contain zero Latin script words.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
### Contractual Delegation Envelope (CDE)
```json
{
  "task_id": "TSK-2026-REMEDIATE-REFS-LEAK-POST-GRADUATION",
  "stage": "Remediation of Bibliographic Leakage & Master Monograph Update",
  "worker_agent": "academic-writer",
  "objective": "Execute the clean remediation of references in Comprehensive_References.docx and Thesis_Final_Master.docx using evolved structural validation, purging all leaked subheadings and non-reference text",
  "target_script": "python3 02_analysis_code/restore_comprehensive_references_v2.py",
  "inputs": [
    "03_deliverables/Thesis.docx",
    "04_references_and_lit/Reference.docx",
    "03_deliverables/Thesis_Chapters1to3.docx",
    "01_raw_inputs/فصل 4 خانم مرضیه ابراهیمی (1).docx",
    "03_deliverables/Chapter_5_Discussion.docx",
    "03_deliverables/All_Appendices.docx"
  ],
  "required_artifacts": [
    "03_deliverables/Comprehensive_References.docx",
    "03_deliverables/Thesis_Final_Master.docx",
    "03_deliverables/thesis_assembly_manifest.json"
  ],
  "acceptance_criteria": [
    "Apply the graduated structural citation parsing invariants (LSN-2026-STRUCTURAL-REFERENCE-PARSING-001): every reference entry MUST have author-year markers (e.g. 4-digit solar/Gregorian year)",
    "Strictly exclude subheadings such as 'الف) منابع و مآخذ فارسی (کتب و مقالات)', 'ب) منابع و مآخذ انگلیسی (لاتین)', and any section labels or note lines",
    "Regenerate 03_deliverables/Comprehensive_References.docx containing ONLY genuine references, categorized into 'الف) منابع فارسی' and 'ب) منابع انگلیسی'",
    "Recompile 03_deliverables/Thesis_Final_Master.docx incorporating the purified bibliography, maintaining Chapters 1-5, all 222 OpenXML footnotes, and appendices intact",
    "Verify that the references section contains zero non-reference text",
    "Update 03_deliverables/thesis_assembly_manifest.json with verified pure reference counts"
  ],
  "constraints": [
    "Directive 4 (APA 7th Edition typography)",
    "Directive 5 (Persian Academic OpenXML Typography Standards, RTL, hanging indents)",
    "Directive 6 (English ASCII filenames)",
    "Directive 23 (Clean Workspace Root Standard: place script in 02_analysis_code/)"
  ]
}
```

Please execute `02_analysis_code/restore_comprehensive_references_v2.py` and return structured completion metrics.


The current local time is: 2026-09-25T19:13:18+03:30.
- **Enforcement**: results_auditor_guard.py

### Invariant LSN-20260925-C57A9F (20260925_180806)
- **Category**: Lesson
- **Rule**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~163/600 tokens (27.2%)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `behavior-analyst` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Perform causal root-cause analysis on the reconstructed trajectory to determine failure mechanism for user critique: Problem: 
You have this text in the references. This is unacceptable.
جامعیت: این فهرست شامل تمامی ارجاعات موجود در متن فصول ۲.۱ تا ۲.۷ (نظریات بنیادین، مدلهای شناختی، پرسشنامهها و پیشینههای تجربی متأخر تا سال ۲۰۲۵) میباشد.

Trajectory details:
- Unanchored 4-digit regex matched '۲۰۲۵' inside descriptive prose.
- Structural filter failed to identify prefix 'جامعیت:' as non-reference meta-annotation.
- Missing bibliographic syntax validator (e.g. requiring author surname, initials/title, publication type).

Please formulate causal diagnosis, failure mode signature, and behavioral remedy.


The current local time is: 2026-09-25T19:49:25+03:30.
- **Enforcement**: results_auditor_guard.py
