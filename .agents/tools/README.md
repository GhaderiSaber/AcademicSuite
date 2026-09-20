# Tools Layer — Deterministic Computational Engines ("The Hands")

In accordance with **Phase 6** of the Academic Suite Architecture and **Directive 12.1 (Sole Orchestrator Mandate)**:
- Antigravity and its specialized subagents are the **Cognitive Brains** (planning, interpreting, orchestrating).
- The tools in this directory and within `.agents/skills/*/scripts/` are the **Deterministic Hands** (calculating, auditing, compiling).

## Structure
- `python/`: Deterministic Python execution scripts:
  - `statistical_runner.py`: General Python runner for parametric assumptions and models.
  *(Note: Unreferenced helpers like openxml_helpers.py were pruned in Phase 35; canonical OpenXML generation is owned by scripts/structured_docx_generator.py).*
- `r/`: Deterministic R scripts:
  - `sem_lavaan_runner.R`: Lavaan runner for SEM micro-stages.

