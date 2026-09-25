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
- **Lesson (LSN-20260925-A833B2)**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~164/600 tokens (27.3%)]
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