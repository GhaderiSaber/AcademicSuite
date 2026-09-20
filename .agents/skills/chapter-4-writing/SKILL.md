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

