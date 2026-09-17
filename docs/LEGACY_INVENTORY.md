# Legacy Inventory & Technical Debt Audit

**Document Version:** 1.0.0 (Phase 1 Audit)  
**Audit Scope:** Legacy workflows, deprecated skill shells, stale agent frontmatter bindings, and legacy Python dispatcher code.  

---

## 1. Executive Summary

During the development and migration of the **Academic Suite**, the repository transitioned from an early file-based workflow model (`.agents/workflows/`) and standalone Python execution loop into native **Google Antigravity Customizations** (Skills, Subagents, Rules, Plugins, and Lifecycle Hooks).

This transition left behind four categories of legacy components:
1. **Legacy Workflow Backups** (`.agents/workflows/`): 10 backup files (`.md.bak`) and 1 empty directory.
2. **Legacy Migrated Skill Shells** (`.agents/skills/`): 10 empty skill wrappers with 0 scripts and 0 references.
3. **Stale Agent Skill Bindings**: 11 agent definitions referencing the legacy skill names.
4. **Standalone Python Agent Emulators**: Legacy CLI dispatcher logic in `digital_saber.py` and `digital_saber_shell.py` violating the Sole Orchestrator Mandate (**Directive 12.1**).

*Note: Per Phase 1 instructions, no files are modified or deleted in this audit phase.*

---

## 2. Inventory of Legacy Workflows (`.agents/workflows/`)

The directory `.agents/workflows/` contains legacy workflow definitions that were migrated to the modern skills format:

| Legacy Workflow File | Size (Bytes) | Status | Modern Replacement Skill |
|---|---|---|---|
| `chapter2_literature.md.bak` | 14,361 | Deprecated Backup | `persian-literature-review-builder` + `literature-harvester` |
| `chapter4.md.bak` | 15,721 | Deprecated Backup | `statistical-data-analyst` + `academic-suite-orchestrator` |
| `chapter5.md.bak` | 13,341 | Deprecated Backup | `persian-discussion-builder` |
| `defense_presentation.md.bak` | 12,541 | Deprecated Backup | `persian-defense-presentation-builder` |
| `intervention_protocol.md.bak` | 11,567 | Deprecated Backup | `psychological-intervention-protocol-builder` |
| `journal_submission.md.bak` | 13,769 | Deprecated Backup | `journal-submission-assistant` + `academic-article-writer` |
| `proposal.md.bak` | 11,219 | Deprecated Backup | `persian-proposal-builder` + `gpower-sample-size-calculator` |
| `scale_validation.md.bak` | 13,698 | Deprecated Backup | `psychometric-scale-validator` + `psychometric-scale-resolver` |
| `thesis_assembly.md.bak` | 10,885 | Deprecated Backup | `persian-thesis-builder` |
| `thesis_revision.md.bak` | 12,459 | Deprecated Backup | `persian-thesis-revision-assistant` |
| `chapter4/` (directory) | 0 (empty) | Deprecated Residual Directory | N/A |

---

## 3. Inventory of Legacy Skill Shells (`.agents/skills/`)

When workflow migration was executed, 10 legacy workflows were converted into skill directories inside `.agents/skills/`. These are "empty shells" containing only a `SKILL.md` file without any bundled scripts or references:

| Legacy Skill Name | Path | Scripts | Refs | Reason for Legacy Classification | Modern Replacement |
|---|---|---|---|---|---|
| `chapter2_literature` | `.agents/skills/chapter2_literature/` | 0 | 0 | Migrated workflow shell; contains no execution tools. | `persian-literature-review-builder` |
| `chapter4` | `.agents/skills/chapter4/` | 0 | 0 | Workflow narrative; actual statistical scripts live in `statistical-data-analyst`. | `statistical-data-analyst` |
| `chapter5` | `.agents/skills/chapter5/` | 0 | 0 | Workflow narrative; actual docx compiler lives in `persian-discussion-builder`. | `persian-discussion-builder` |
| `defense_presentation` | `.agents/skills/defense_presentation/` | 0 | 0 | Shell skill; 48 production scripts live in `persian-defense-presentation-builder`. | `persian-defense-presentation-builder` |
| `intervention_protocol` | `.agents/skills/intervention_protocol/` | 0 | 0 | Shell skill; scripts live in `psychological-intervention-protocol-builder`. | `psychological-intervention-protocol-builder` |
| `journal_submission` | `.agents/skills/journal_submission/` | 0 | 0 | Shell skill; tools live in `journal-submission-assistant` & `academic-article-writer`. | `journal-submission-assistant` |
| `proposal` | `.agents/skills/proposal/` | 0 | 0 | Shell skill; tools live in `persian-proposal-builder` & `gpower-sample-size-calculator`. | `persian-proposal-builder` |
| `scale_validation` | `.agents/skills/scale_validation/` | 0 | 0 | Shell skill; tools live in `psychometric-scale-validator` & `psychometric-scale-resolver`. | `psychometric-scale-validator` |
| `thesis_assembly` | `.agents/skills/thesis_assembly/` | 0 | 0 | Shell skill; compilation scripts live in `persian-thesis-builder`. | `persian-thesis-builder` |
| `thesis_revision` | `.agents/skills/thesis_revision/` | 0 | 0 | Shell skill; triage engines live in `persian-thesis-revision-assistant`. | `persian-thesis-revision-assistant` |

---

## 4. Stale Legacy References in Agent Frontmatters

11 out of 15 agent definition files in `.agents/agents/` still declare one or more of these 10 legacy skill shells in their `skills:` list:

| Agent File | Stale Legacy Skills Declared | Modern Replacement Skills Already Present |
|---|---|---|
| `academic-writer.md` | `chapter4`, `chapter5`, `thesis_assembly` | `persian-thesis-builder`, `persian-discussion-builder`, `academic-article-writer`, `ai-academic-tone-polisher` |
| `digital-saber.md` | `chapter4`, `thesis_revision` | `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor` |
| `final-judge.md` | `defense_presentation` | `thesis-integrity-auditor`, `persian-defense-presentation-builder` |
| `intervention-designer.md` | `intervention_protocol` | `psychological-intervention-protocol-builder` |
| `journal-strategist.md` | `journal_submission` | `academic-article-writer`, `journal-submission-assistant`, `ai-academic-tone-polisher` |
| `literature-expert.md` | `chapter2_literature` | `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer` |
| `methodology-expert.md` | `proposal` | `gpower-sample-size-calculator`, `persian-proposal-builder`, `psychological-intervention-protocol-builder` |
| `psychometric-expert.md` | `scale_validation` | `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator` |
| `results-auditor.md` | `chapter4` | `thesis-integrity-auditor`, `statistical-data-analyst` |
| `statistical-auditor.md` | `chapter4` | `thesis-integrity-auditor`, `statistical-data-analyst` |
| `statistical-expert.md` | `chapter4` | `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator` |

---

## 5. Legacy Python Agent Orchestrators vs. Sole Orchestrator Mandate

Under **Directive 12.1 (Sole Orchestrator Mandate & Prohibition of Python Agent Emulation)**:
> *"Antigravity is the sole agent runtime and multi-agent orchestrator. The Antigravity Lead Agent coordinates subagents natively via `invoke_subagent`. Under NO circumstance may an agent write, re-introduce, or execute Python classes or scripts that attempt to manage, dispatch, or simulate subagents, agent communication, or multi-agent workflows."*

Two legacy Python files contain deprecated dispatcher and orchestration logic created before Antigravity native subagent orchestration was standardized:

1. **`digital_saber.py` (Workspace Root, 568 lines):**
   - Contains a command-line interface attempting to invoke cognitive layers, run pseudo-agent loops, and dispatch tasks through Python rather than Antigravity tools.
   - Should be retained strictly as an administrative CLI tool or refactored into a thin deterministic helper for `academic-suite-orchestrator`.
2. **`.agents/shared/digital_saber_shell.py` (900 lines):**
   - Implements an interactive terminal shell (`DigitalSaberShell(cmd.Cmd)`) with prompt loops, command dispatch, and interactive sessions.
   - Superseded by the Antigravity IDE and chat interface.

---

## 6. Migration & Retirement Status (Phase 16 Complete)

All technical debt and legacy migration items have been formally resolved:
1. **Retired `.agents/workflows/`**: All 10 `.md.bak` files have been moved to `legacy/workflows/`, and `.agents/workflows/README.md` documents deprecation.
2. **Consolidated Skills to 43 Production Skills**: The 10 legacy workflow shells were safely retired to `legacy/skills/`, leaving exactly 43 active, tool-backed production packages in `.agents/skills/`.
3. **Cleaned Agent Definitions & Contracts**: All 22 agent definition files (`agent.md`) and behavioral contracts (`contract.md`) have been re-bound to canonical production skills with zero stale references remaining.
4. **Deterministic Python CLI Tools**: Clarified that Python scripts act strictly as deterministic computational tools ("The Hands") under Directive 12.1.
