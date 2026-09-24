---
name: academic-suite-orchestrator
description: Deterministic batch pipeline CLI runner executing multi-stage script sequences and artifact handoffs on disk ("The Hands").
---

# AcademicSuite Batch Pipeline CLI Runner (موتور اجرای متوالی اسکریپت‌ها بر روی دیسک)

> **Decoupling Note (Directive 12.1 — Sole Orchestrator Mandate)**:  
> High-level multi-agent orchestration belongs exclusively to `academic-orchestrator`. This skill is strictly **"The Hands"**: a deterministic CLI runner (`orchestrator_cli.py`) executing ordered batches of Python/R scripts on disk and compiling execution manifests.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
1. **Executing an Explicit Sequence of Deterministic Scripts**: A multi-step workflow on disk needs sequential batch execution (e.g., data cleaning followed by statistical calculation and OpenXML assembly).
2. **Dependency Validation**: Dry-run verification of file dependencies is required before launching computations (`--dry-run`).
3. **Resumption & Checkpointing**: Resuming or rerunning specific interrupted pipeline steps (`--resume-from <step>` or `--step <step>`).
4. **Execution Audit Compilation**: Generating the physical execution manifest (`orchestrator_manifest.json`) and status table (`PROJECT_DASHBOARD.md`).

---

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
1. **Single-Stage Isolated Execution**: When only one specific analysis is needed (e.g., only CFA or only Mediation), invoke that domain skill (`cfa`, `mediation`) directly.
2. **Interactive Stage-Gates**: When intermediate qualitative review, supervisor feedback, or interactive confirmation is needed between steps.

---

## 3. REQUIRED INPUTS & CONTRACT
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
