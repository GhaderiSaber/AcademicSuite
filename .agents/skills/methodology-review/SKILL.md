---
name: methodology-review
description: Audit research design validity, internal/external validity safeguards, statistical power (G*Power), and Chapter 3 methodology scaffolding.
---

# Methodology Review Skill (ارزیابی روش‌شناسی پژوهش)

Evaluates methodological rigor for Chapter 3 & proposals:
- G*Power statistical power verification ($1-\beta \ge .80$)
- Experimental and quasi-experimental validity safeguards
- Operational variable definitions

## CLI Execution
```bash
python3 .agents/skills/methodology-review/scripts/audit_methodology.py --spec methodology_spec.json --output 01_methodology_audit.json
```

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-20260925-159234)**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~524/600 tokens (87.3%)]
- **Target Capability**: `CHAPTER4` | **Task**: `chapter_4_drafting` | **Agent**: `academic-writer` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- [AP-2026-MISSING-BLANK-LINE-BEFORE-HEADINGS] Avoid: Placing headings directly underneath body text without an explicit preceding blank line or skipping blank lines in DOCX generators.
  Approved Remedy: Insert exactly one blank newline before each heading in Markdown and enforce an explicit blank line separation in OpenXML DOCX.

💡 Relevant Active Lessons:
- [LSN-2026-FORMATTING-AND-FILTERING-FAILURE-001] Mandate: Enforce explicit blank line logic for headings. Implement a strict filter for Appendices to strip narrative/scoring text, retaining only the table and its title.
  Generalization: Formatting boundaries must be explicitly enforced in generators, and section-specific content filters must be applied to exclude non-compliant text.
- [LSN-2026-PERSIAN-SCRIPT-ONLY-WITH-ENGLISH-FOOTNOTES-001] Mandate: Enforce zero Latin script in Persian body text. Transliterate all author names to Persian, use Persian equivalents for technical terms, and provide original English text strictly via footnotes.
  Generalization: Running Persian academic text must strictly contain zero Latin script words.
- [LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001] Mandate: Strictly ban regex string substitutions on minified XML. Mandate structured XML DOM parsing via lxml or ElementTree for all OpenXML modifications. Mandate mechanical body paragraph count verification (> 0) before release.
  Generalization: Never use regex for structural modification of minified XML files like OpenXML.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
### Contractual Delegation Envelope (CDE)
```json
{
  "task_id": "TSK-2026-REMEDIATE-HEADING-SPACING-AND-APPENDICES",
  "stage": "Remediation of Heading Spacing & Clean Appendices Tables-Only Assembly",
  "worker_agent": "academic-writer",
  "objective": "Enforce explicit 1 blank line before each header and 0 blank lines after headers, and format the Appendices ('پیوست') section to contain strictly only the Questions tables with their designated question headers",
  "target_script": "python3 02_analysis_code/remediate_heading_spacing_and_appendices.py",
  "inputs": [
    "03_deliverables/Thesis_Final_Master.docx",
    "03_deliverables/All_Appendices.docx",
    "01_raw_inputs/Questionnaires/-کنترل-شغلی.docx",
    "01_raw_inputs/Questionnaires/Oldham_and_Hackman_Job_Characteristics.docx",
    "01_raw_inputs/Questionnaires/Organizational Innovation.docx"
  ],
  "required_artifacts": [
    "03_deliverables/All_Appendices.docx",
    "03_deliverables/Thesis_Final_Master.docx",
    "03_deliverables/thesis_assembly_manifest.json"
  ],
  "acceptance_criteria": [
    "1. Heading Spacing Invariant: Traverse all headings across Thesis_Final_Master.docx and ensure each heading has exactly ONE blank line before it and ZERO blank lines after it (no empty paragraph nodes following headings, body text follows immediately).",
    "2. Appendices Strict Filtering Invariant: Rebuild All_Appendices.docx so that it contains ONLY the three question tables, each preceded solely by its designated questionnaire header (e.g. 'پیوست ۱: پرسشنامه ویژگیهای شغلی هکمن و اولدهام', 'پیوست ۲: پرسشنامه کنترل شغلی کاراسک', 'پیوست ۳: پرسشنامه نوآوری سازمانی'). Completely purge all scoring instructions, reverse-item keys, reliability/validity descriptions, and introductory greetings.",
    "3. Recompile Thesis_Final_Master.docx with the cleaned All_Appendices.docx and verified heading spacing.",
    "4. Verify with python-docx that headings have the required blank line before and 0 blank lines after, and that Appendices contain only tables and headers.",
    "5. Update 03_deliverables/thesis_assembly_manifest.json with verification booleans."
  ],
  "constraints": [
    "Directive 4 (APA 7th Edition typography)",
    "Directive 5 (Persian Academic OpenXML Typography Standards, RTL, DOM XML processing)",
    "Directive 6 (English ASCII filenames)",
    "Directive 23 (Clean Workspace Root Standard: place script in 02_analysis_code/)"
  ]
}
```

Please author and execute `02_analysis_code/remediate_heading_spacing_and_appendices.py` to enforce both constraints, and return structured completion metrics.


The current local time is: 2026-09-25T21:43:48+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-159234)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `trajectory-analyzer` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Reconstruct observable actions, tool calls, and error trajectory for user critique: Problem: 
1. You should have a one blank line before each header. But there isn't any blank line after the headers. 
2. In the 'پیوست' section you should have only the Questions table with header of that question. 

The current local time is: 2026-09-25T21:26:53+03:30.

Please examine:
1. How headers and paragraph spacing were rendered across docx generation scripts, checking the presence of blank lines before/after headers.
2. How the 'پیوست' (Appendices) section was constructed from raw questionnaire files (All_Appendices.docx) and what extra explanatory text or scoring guidelines were retained instead of only having the questions table with its header.


The current local time is: 2026-09-25T21:27:06+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-A833B2)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `trajectory-analyzer` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Reconstruct observable actions, tool calls, and error trajectory for user critique: Problem: 
1. You should have a one blank line before each header. But there isn't any blank line after the headers. 
2. In the 'پیوست' section you should have only the Questions table with header of that question. 

The current local time is: 2026-09-25T21:26:53+03:30.

Please examine:
1. How headers and paragraph spacing were rendered across docx generation scripts, checking the presence of blank lines before/after headers.
2. How the 'پیوست' (Appendices) section was constructed from raw questionnaire files (All_Appendices.docx) and what extra explanatory text or scoring guidelines were retained instead of only having the questions table with its header.


The current local time is: 2026-09-25T21:27:06+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-A833B2)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `knowledge-curator` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Catalog the diagnosed anti-pattern into state/pitfalls.jsonl based on behavior analysis BAN-20260925-001 (FORMATTING_AND_FILTERING_FAILURE):
1. Missing explicit blank line before headings and/or presence of trailing blank lines after headings in DOCX generation.
2. Failure to filter out non-table narrative/scoring text in the 'پیوست' (Appendices) section, requiring strictly only the questionnaire table with its title.

Please catalog structured anti-patterns and actionable lessons in .agents/learning/knowledge/.


The current local time is: 2026-09-25T21:35:29+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-826A8D)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `knowledge-curator` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Catalog the diagnosed anti-pattern into state/pitfalls.jsonl based on behavior analysis BAN-20260925-001 (FORMATTING_AND_FILTERING_FAILURE):
1. Missing explicit blank line before headings and/or presence of trailing blank lines after headings in DOCX generation.
2. Failure to filter out non-table narrative/scoring text in the 'پیوست' (Appendices) section, requiring strictly only the questionnaire table with its title.

Please catalog structured anti-patterns and actionable lessons in .agents/learning/knowledge/.


The current local time is: 2026-09-25T21:35:29+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-826A8D)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `skill-evolver` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Synthesize candidate mutation based on LSN-2026-FORMATTING-AND-FILTERING-FAILURE-001 and AP-2026-FORMATTING-AND-FILTERING-FAILURE to update apa-reporting and persian-thesis-builder skills:
1. Enforce explicit 1 blank line before each header and 0 blank lines after headers in OpenXML paragraphs and templates.
2. In the 'پیوست' (Appendices) section, filter out all non-table narrative, scoring instructions, and author/psychometric introductions, retaining strictly only the question tables and their designated question headers.

Stage candidate into .agents/learning/candidates/improvement_candidate.json without directly mutating canonical skills.


The current local time is: 2026-09-25T21:36:17+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-48AA4C)]
- **Target Capability**: `GENERAL_ACADEMIC` | **Task**: `general_task` | **Agent**: `skill-evolver` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- None cataloged. Enforce standard APA 7 & OpenXML rigor.

💡 Relevant Active Lessons:
- No specialized lessons flagged. Standard pipeline rules apply.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
Synthesize candidate mutation based on LSN-2026-FORMATTING-AND-FILTERING-FAILURE-001 and AP-2026-FORMATTING-AND-FILTERING-FAILURE to update apa-reporting and persian-thesis-builder skills:
1. Enforce explicit 1 blank line before each header and 0 blank lines after headers in OpenXML paragraphs and templates.
2. In the 'پیوست' (Appendices) section, filter out all non-table narrative, scoring instructions, and author/psychometric introductions, retaining strictly only the question tables and their designated question headers.

Stage candidate into .agents/learning/candidates/improvement_candidate.json without directly mutating canonical skills.


The current local time is: 2026-09-25T21:36:17+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-48AA4C)]
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
1. You should have a one blank line before each header. But there isn't any blank line after the headers. 
2. In the 'پیوست' section you should have only the Questions table with header of that question. 

Trajectory details:
- Trajectory artifact: EVT-20260925-HEADING-APPENDIX-FEEDBACK/trajectory.json
- Spacing failure: Heading insertion lacked blank line before heading and/or introduced extra spacing after headings.
- Appendix failure: Wholesale ingestion of raw questionnaire documents (introductory notes, psychometric justifications, scoring instructions) instead of strictly filtering for question tables and their designated question headers.

Please formulate causal diagnosis, failure mode signature, and behavioral remedies.


The current local time is: 2026-09-25T21:34:57+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-0BEFCA)]
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
1. You should have a one blank line before each header. But there isn't any blank line after the headers. 
2. In the 'پیوست' section you should have only the Questions table with header of that question. 

Trajectory details:
- Trajectory artifact: EVT-20260925-HEADING-APPENDIX-FEEDBACK/trajectory.json
- Spacing failure: Heading insertion lacked blank line before heading and/or introduced extra spacing after headings.
- Appendix failure: Wholesale ingestion of raw questionnaire documents (introductory notes, psychometric justifications, scoring instructions) instead of strictly filtering for question tables and their designated question headers.

Please formulate causal diagnosis, failure mode signature, and behavioral remedies.


The current local time is: 2026-09-25T21:34:57+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-0BEFCA)]