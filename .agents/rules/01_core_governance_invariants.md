---
trigger: always_on
description: "Core constitutional governance: Directive 0 Binary Honesty Protocol, Directive 2 Deterministic Calculations on Real Data, Directive 6 English ASCII Filenames, Directive 23 Clean Workspace Root, Directive 25 Universal Anti-Shortcut & No-Rush Mandate."
---

# Core Governance Invariants (Directives 0, 2, 6, 23, 25)

These foundational constitutional directives govern all operations across the AcademicSuite workspace.

## 1. Directive 0: Binary Honesty Protocol & Anti-Deception
- When asked a compliance query ("Did you check X?", "Did you follow the rules?"), your response MUST begin with an unambiguous **"Yes"** or **"No"** as the very first word.
- Disclose omissions, failures, or edge cases factually without defensive excuses, sycophancy, or rationalization.
- Multi-agent execution claims strictly require physical `invoke_subagent` calls. Never state that a specialist subagent executed an analysis unless it was physically invoked.

## 2. Directive 2: Deterministic Calculation Invariant
- **Zero mental math or hallucinated statistics in memory.** All numbers, means, standard deviations, $p$-values, effect sizes, and model parameters must be computed via bundled deterministic Python/R CLI scripts on real datasets.
- Calculations must execute through canonical scripts in `.agents/skills/*/scripts/` or `scripts/`.
- Intermediate numerical outputs must be preserved in structured JSON analytical anchors.

## 3. Directive 6: English Primary Interaction & ASCII English Filenames
- Agents communicate, reason, plan, and report strictly in English (Persian is reserved exclusively for academic deliverable content).
- Every file, script, dataset, or directory created on disk MUST strictly use ASCII English characters (`^[a-zA-Z0-9_.-]+$`). Non-ASCII filenames on disk are strictly prohibited.

## 4. Directive 23: Clean Workspace Root Standard
- Zero executable scripts or loose deliverable files in repository root.
- All code and artifacts must route strictly to:
  1. Scratch directory (`<appDataDir>/brain/<id>/scratch/` or `scratch/`)
  2. Analysis code (`02_analysis_code/`)
  3. Reusable scripts (`scripts/` or `.agents/scripts/`)
  4. Test suite (`tests/`)
  5. Deliverables (`03_deliverables/` or stage folders)

## 5. Directive 25: Universal Anti-Shortcut, Zero-Fastpath & No-Rush Mandate
- Zero permission to take fastpaths, shortpaths, ad-hoc bypasses, temporary workarounds, placeholder stubs, or mock implementations.
- Strictly zero rush or haste in getting the job done. Never prioritize speed, turn economy, or conversational expediency over thoroughness, correctness, and completeness.
- Every task must be carried out fully, properly, and meticulously according to canonical standards, specifications, test suites, and validation gates before completion.
