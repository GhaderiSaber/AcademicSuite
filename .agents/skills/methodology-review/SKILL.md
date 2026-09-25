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
- **Lesson (LSN-20260925-0BEFCA)**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~163/600 tokens (27.2%)]
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
