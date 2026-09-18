---
name: academic-suite-orchestrator
description: Deterministic batch pipeline CLI runner executing multi-stage script sequences and artifact handoffs on disk ("The Hands").
---

# AcademicSuite Batch Pipeline CLI Runner (موتور اجرای متوالی اسکریپت‌ها بر روی دیسک)

> **Architectural Boundary (Directive 12.1 — Sole Orchestrator Mandate)**:  
> **Google Antigravity and the `academic-orchestrator` agent are the sole multi-agent orchestrators**. This skill does **NOT** select agents, control high-level project lifecycles, or coordinate milestone state machines.  
> This skill is strictly **"The Hands"**: a deterministic CLI runner (`orchestrator_cli.py`) that executes ordered batches of Python/R scripts on disk and generates execution manifests.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. An agent needs to **execute an explicit sequence of deterministic CLI scripts on disk** (e.g. running data cleaning followed by statistical calculation and OpenXML assembly).
2. The agent needs **dry-run validation** of file dependencies before launching long computations (`--dry-run`).
3. The agent needs **step-level checkpointing and resumption** for interrupted script runs (`--resume-from <step>` or `--step <step>`).
4. Compiling the final disk execution audit trail (`orchestrator_manifest.json`) and summary status table (`PROJECT_DASHBOARD.md`).

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Making High-Level Research or Deliberation Decisions**: Selecting research questions, choosing statistical methods, or evaluating competing models must be performed by specialist agents (`methodology-expert`, `statistical-expert`, `academic-challenger`).
2. **Multi-Agent Coordination & Delegation**: Delegating tasks to subagents must occur natively via Antigravity's `invoke_subagent` tool, never through a Python script.
3. **Project State & Milestone Management**: Setting milestone states, verifying approvals, and checking gatekeeper requirements belongs to `StrictStateMachine` (`scripts/academic_state_manager.py`).
4. **Single-Stage Isolated Execution**: When only one specific analysis is needed (e.g., only CFA or only Mediation), invoke that specific skill (`cfa`, `mediation`) directly rather than chaining through the batch runner.

---

## 3. Required Inputs & Execution Contract
The runner accepts an explicit configuration payload or command-line flags:
- `--steps`: Comma-separated list of execution steps (e.g., `simulation,statistics,discussion`).
- `--config`: Path to validated project JSON configuration.
- `--out-dir`: Absolute output directory path for generated deliverables.
- `--mode`: Execution mode (`production` [default] vs `demo`). In `production` mode, missing payloads immediately raise `StageDependencyError` with zero silent fallback to sample data.

---

## 4. Execution Syntax ("The Hands")

### Standard Explicit Step Execution:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --steps proposal,simulation,statistics,discussion,thesis,defense \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --mode production
```

### Dry-Run DAG Dependency Validation:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --steps statistics,audit \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --dry-run
```

---

## 5. Output Contract & Artifacts
Every execution run generates two verified tracking artifacts in `--out-dir`:
1. **`orchestrator_manifest.json`**: Machine-readable JSON recording step timestamps, exit codes, script identities, and output artifact paths.
2. **`PROJECT_DASHBOARD.md`**: Executive markdown table summarizing executed steps, exit codes, duration benchmarks, and clickable artifact links.

---

## 6. Validation & Forensic Sanity Checks
- **Zero Silent Fallback (Directive 0 & 2)**: In `production` mode, missing payloads cause immediate script termination with exit code 1.
- **Exit Code Verification**: Each child process must return exit code 0. Any non-zero exit code halts the sequence.
- **Physical Disk Confirmation**: Upstream files must physically exist on disk before downstream steps begin.
