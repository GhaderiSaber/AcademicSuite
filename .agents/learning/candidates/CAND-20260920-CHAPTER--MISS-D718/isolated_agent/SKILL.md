---
name: chapter-4-writing
description: End-to-end orchestration for Chapter 4 findings, enforcing One-Hypothesis-One-Stage micro-stages, Triad Artifact Invariant (.docx, .md, .json), and Master Decision Matrix.
---

# Chapter 4 Writing Skill (تدوین فصل چهارم یافته‌های پژوهش)

Orchestrates the Chapter 4 micro-stage findings pipeline:
- Generates the synchronized Triad Artifact Invariant (`.docx` + `.md` + `.json`)
- Enforces One-Hypothesis-One-Stage isolation
- Produces the Master Hypotheses Decision Matrix

## CLI Execution
```bash
python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py --stage "آزمون فرضیه اول" --base "06_hypothesis_1" --outdir 03_deliverables/stage_06_hypothesis_1
```



# --- Candidate Refinement ---
--- a/.agents/skills/chapter-4-writing/SKILL.md
+++ b/.agents/skills/chapter-4-writing/SKILL.md
@@ -15,3 +15,16 @@
 python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py --stage "آزمون فرضیه اول" --base "06_hypothesis_1" --outdir 03_deliverables/stage_06_hypothesis_1
 ```
 
+
+
+## 📋 Mandatory Operational Step: chapter-4-writing Execution
+Prior to concluding this stage:
+1. **Conditional Execution Rules**:
+   - **WHEN condition X (Standard prerequisites satisfied)**:
+     → use approach A (Execute standard analysis).
+   - **WHEN condition Y (Alternative design characteristics present)**:
+     → use approach B (Adjust model parameters accordingly).
+   - **EXCEPT condition Z (Risk of 'GENERAL_METHODOLOGICAL_DEFECT' detected)**:
+     → use approach C (Adhere strictly to domain guidelines and verify task requirements against evaluation checklist.).
+2. **Audit Requirement**: Verify that all parameters meet academic and institutional standards.
+3. **Artifact Traceability**: Emit structured checkpoint artifact documenting execution parameters and verifying zero 'GENERAL_METHODOLOGICAL_DEFECT'.
