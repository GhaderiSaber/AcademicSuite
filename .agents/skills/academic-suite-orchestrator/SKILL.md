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

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-MANDATORY-SEM-FIGURE-GENERATION-001)**: When delegating SEM or relevant simulation tasks, explicitly require the generation of high-resolution path diagrams (semPlot / matplotlib) in the delegation scope. Correspondingly, require the validation-agent to actively assert the existence of these figure artifacts in the deliverables directory before passing the audit. [Enforcement: dynamic_invariant_guard.py (LSN-2026-MANDATORY-SEM-FIGURE-GENERATION-001)]
- **Lesson (LSN-2026-ANTIGRAVITY-217-SCOPED-AGENT-HOOK-ARCHITECTURE-001)**: Package each agent and subagent as an autonomous unit containing its definition (agent.md), contracts (contract.md), and dedicated lifecycle guard (guard.py / hooks.json) within its own dedicated folder. [Enforcement: dynamic_invariant_guard.py (LSN-2026-ANTIGRAVITY-217-SCOPED-AGENT-HOOK-ARCHITECTURE-001)]
- **Lesson (LSN-20260924-STRICT-ENGLISH-CONVERSATION-001)**: English-only for all meta-conversational and status reports regardless of artifact language. [Enforcement: dynamic_invariant_guard.py (LSN-20260924-STRICT-ENGLISH-CONVERSATION-001)]
- **Lesson (LSN-2026-LEARN-SUBAGENTS-001)**: Invoke exclusively native learning subagents (knowledge-curator, trajectory-analyzer, behavior-analyst, skill-evolver, evaluation-agent, curriculum-builder) whenever /learn or continuous self-improvement is triggered. [Enforcement: dynamic_invariant_guard.py (LSN-2026-LEARN-SUBAGENTS-001)]
- **Lesson (LSN-20260925-572A86)**: Standard compliance: Problem: 
There is a text in the references section that unrelated to references. 


The current local time is: 2026-09-25T18:58:52+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-572A86)]
You have this text in the references. This is unacceptable.
جامعیت: این فهرست شامل تمامی ارجاعات موجود در متن فصول ۲.۱ تا ۲.۷ (نظریات بنیادین، مدلهای شناختی، پرسشنامهها و پیشینههای تجربی متأخر تا سال ۲۰۲۵) میباشد.



The current local time is: 2026-09-25T19:42:53+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-1944FB)]
You have this text in the references. This is unacceptable.
جامعیت: این فهرست شامل تمامی ارجاعات موجود در متن فصول ۲.۱ تا ۲.۷ (نظریات بنیادین، مدلهای شناختی، پرسشنامهها و پیشینههای تجربی متأخر تا سال ۲۰۲۵) میباشد.



The current local time is: 2026-09-25T19:42:53+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-1944FB)]
There is a text in the references section that unrelated to references. 


The current local time is: 2026-09-25T18:58:52+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-572A86)]
There is a text in the references section that unrelated to references. 


The current local time is: 2026-09-25T18:58:52+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-572A86)]
There is a text in the references section that unrelated to references. 


The current local time is: 2026-09-25T18:58:52+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-572A86)]
There is a text in the references section that unrelated to references. 


The current local time is: 2026-09-25T18:58:52+03:30. [Enforcement: dynamic_invariant_guard.py (LSN-20260925-572A86)]
- **Lesson (LSN-2026-EXHAUSTIVE-TABLE-BY-TABLE-AUDIT-001)**: Every validation gatekeeper must inspect 100% of tables individually, asserting that every column header conforms to standard APA symbols, every table has a Persian definition note, and zero English words exist in narrative text or table cells. [Enforcement: dynamic_invariant_guard.py (LSN-2026-EXHAUSTIVE-TABLE-BY-TABLE-AUDIT-001)]