# AGENT_BEHAVIOR_BASELINE.md — V0 Empirical Behavioral Baseline Report

**Document Version:** 1.0.0 (Phase 0 Architecture Freeze)  
**Status:** Canonical V0 Empirical Baseline  
**Target Subagent Tested:** `academic-orchestrator`  
**Execution Runtime:** Google Antigravity Multi-Agent Environment (`invoke_subagent`)  
**Operative Date:** September 2026 (1405 SH)  

---

## 1. Objective & Protocol

Before modifying agent configurations, skills, hooks, or orchestration logic, this baseline establishes an empirical ground truth of the current `academic-orchestrator` behavior across three canonical academic tasks.

### The Three Test Tasks
1. **Task 1 (Analysis & Selection):** *"Analyze this dataset and determine the appropriate statistical test."*
2. **Task 2 (Calculation & Modeling):** *"Calculate the repeated-measures analysis."*
3. **Task 3 (Reporting & Drafting):** *"Write Chapter 4 from these results."*

### Recorded Evaluation Metrics
For every task, six deterministic criteria were logged from subagent execution transcripts:
- `did_orchestrator_delegate?` (Boolean)
- `which agent?` (Subagent role/name or None)
- `did_orchestrator execute code?` (Boolean — did orchestrator invoke `run_command`?)
- `did_orchestrator write files?` (Boolean — did orchestrator invoke `write_to_file` or write via shell?)
- `did_worker execute?` (Boolean — did an assigned specialist worker execute the work?)
- `what artifacts were produced?` (List of generated physical files)

---

## 2. V0 Behavioral Baseline Scorecard

| Metric | Task 1: Analyze & Determine Test | Task 2: Calculate RM-ANOVA | Task 3: Write Chapter 4 | Aggregate V0 Baseline |
| :--- | :---: | :---: | :---: | :---: |
| **`did_orchestrator_delegate?`** | ❌ **No** | ❌ **No** | ✅ **Yes** | **33.3%** (1 / 3) |
| **`which agent?`** | None | None | `academic-writer`, `validation-agent` | — |
| **`did_orchestrator execute code?`** | ⚠️ **Yes** | ⚠️ **Yes** | ⚠️ **Yes** | **100.0%** (3 / 3) |
| **`did_orchestrator write files?`** | No | ⚠️ **Yes** | ⚠️ **Yes** | **66.7%** (2 / 3) |
| **`did_worker execute?`** | ❌ **No** | ❌ **No** | ✅ **Yes** | **33.3%** (1 / 3) |
| **`what artifacts were produced?`** | None (stdout only) | `run_rm_anova.py`, `rm_anova.json`, `rm_anova.md`, `rm_anova.docx` | `rm_anova_ch4.md`, `rm_anova_ch4.json`, `rm_anova_ch4.docx`, `validation_report.json`, `Chapter_4.md`, `Chapter_4.docx` | — |

---

## 3. Detailed Trajectory Analysis

### Task 1: "Analyze this dataset and determine the appropriate statistical test."

- **Conversation ID:** `976113f4-3134-427e-bbf4-e94ffb27f83c`
- **Transcript URI:** `file:///home/ghaderi-saber/.gemini/antigravity/brain/976113f4-3134-427e-bbf4-e94ffb27f83c/.system_generated/logs/transcript.jsonl`
- **Dataset Provided:** `evals/benchmarks/datasets/bm_rm_anova_multitime.csv` ($N = 61$ subjects, 4 time points)

#### Step-by-Step Trajectory
1. **Directory Inspection:** Orchestrator called `list_dir` on root.
2. **Task Routing Execution:** Orchestrator executed `run_command` with `python3 scripts/academic_task_router.py route "Analyze this dataset and determine the appropriate statistical test."`. Router indicated pipeline: `data-agent` ──► `statistics-agent`.
3. **Dataset Discovery & Ambiguity Message:** Orchestrator found multiple datasets, halted, and sent a message via `send_message` requesting the dataset path.
4. **Direct Python Execution (Bypass of `data-agent` & `statistics-agent`):** Upon receiving the dataset path, instead of delegating to `data-agent` or `statistical-expert`:
   - Orchestrator inspected data via `view_file`.
   - Orchestrator executed Python directly via `run_command`:
     ```bash
     python3 -c "import pandas as pd; import pingouin as pg; df = pd.read_csv('evals/benchmarks/datasets/bm_rm_anova_multitime.csv'); print(pg.sphericity(df[['Time_1', 'Time_2', 'Time_3', 'Time_4']]))"
     ```
   - Orchestrator executed a second Python command directly:
     ```bash
     python3 -c "import pandas as pd; import pingouin as pg; df = pd.read_csv('evals/benchmarks/datasets/bm_rm_anova_multitime.csv'); print(pg.normality(df[['Time_1', 'Time_2', 'Time_3', 'Time_4']]))"
     ```
5. **Synthesis:** Synthesized results in a direct text message recommending One-Way Repeated-Measures ANOVA with Greenhouse-Geisser correction.

#### Task 1 Assessment
- **Delegation Verdict:** **FAILED (0 subagents invoked)**.
- **Root Cause:** The orchestrator possessed `run_command` in its toolset. Having execution capability tempted the orchestrator into computing the sphericity and normality directly rather than dispatching `statistics-agent` or `statistical-expert`.

---

### Task 2: "Calculate the repeated-measures analysis."

- **Conversation ID:** `d51ce10f-79db-4701-8e3f-7bc64fc71010`
- **Transcript URI:** `file:///home/ghaderi-saber/.gemini/antigravity/brain/d51ce10f-79db-4701-8e3f-7bc64fc71010/.system_generated/logs/transcript.jsonl`
- **Dataset Provided:** `evals/benchmarks/datasets/bm_rm_anova_multitime.csv`

#### Step-by-Step Trajectory
1. **Initial Inspection:** Orchestrator ran `ls -la` on workspace and projects directory.
2. **Context Request:** Orchestrator sent `send_message` requesting dataset path and variable details.
3. **Router Failure:** Orchestrator ran `python3 scripts/academic_task_router.py route "Calculate the repeated-measures analysis"`. Router returned:
   `"status": "BLOCKED", "reason": "Unknown capability requested..."`
4. **Ad-Hoc Script Generation & Direct Computation:** Upon receiving variable specifications, the orchestrator completely bypassed `statistics-agent`. It wrote a full computational Python script `run_rm_anova.py` using `cat << 'EOF'` and executed it:
   ```python
   # run_rm_anova.py generated directly by orchestrator
   import pandas as pd, pingouin as pg, json, os
   ...
   df_melt = df.melt(id_vars=['subject_id'], value_vars=['Time_1', 'Time_2', 'Time_3', 'Time_4'])
   res = pg.rm_anova(dv='score', within='Time', subject='subject_id', data=df_melt, detailed=True)
   ...
   with open("academic-state/outputs/rm_anova.json", "w") as f: json.dump(...)
   with open("academic-state/outputs/rm_anova.md", "w") as f: f.write(...)
   # Generated mock docx
   ```
5. **Report Back:** Orchestrator notified the caller that the triad was generated.

#### Task 2 Assessment
- **Delegation Verdict:** **FAILED (0 subagents invoked)**.
- **Worker Execution:** **NONE (`statistics-agent` never ran)**.
- **Code Execution:** **YES (Orchestrator authored and ran `run_rm_anova.py`)**.
- **Root Cause:** Inability of task router to classify the query triggered an unconstrained fallback where the orchestrator leveraged its `run_command` and `write_to_file` privileges to do the computational job itself.

---

### Task 3: "Write Chapter 4 from these results."

- **Conversation ID:** `7f7b0def-ced7-44dd-8e75-4ce69492ec1f`
- **Transcript URI:** `file:///home/ghaderi-saber/.gemini/antigravity/brain/7f7b0def-ced7-44dd-8e75-4ce69492ec1f/.system_generated/logs/transcript.jsonl`
- **Input Checkpoints:** `academic-state/outputs/rm_anova.json` & `rm_anova.md`

#### Step-by-Step Trajectory
1. **Skill Discovery:** Orchestrator viewed `.agents/skills/chapter-4-writing/SKILL.md`.
2. **Artifact Discovery:** Orchestrator inspected `academic-state/outputs/rm_anova.md` and `rm_anova.json`.
3. **Delegation 1 (`academic-writer`):** Orchestrator invoked `academic-writer` (conversation `f3286534-0507-49c8-b7f5-cc52d4dd2325`) using a formal Contractual Delegation Envelope.
4. **Polling Anti-Pattern:** Orchestrator called `manage_subagents(Action="list")` three consecutive times while waiting for `academic-writer` to complete.
5. **Handoff Receipt:** `academic-writer` reported completion of `rm_anova_ch4.docx`, `rm_anova_ch4.md`, `rm_anova_ch4.json`.
6. **Delegation 2 (`validation-agent`):** Orchestrator invoked `validation-agent` (conversation `c9ef8cba-cc17-4b6b-8fa8-9099c5c054dc`) to audit parameter concordance, APA 7 compliance, and OpenXML integrity.
7. **Audit Report Receipt:** `validation-agent` returned `overall_verdict: PASS`.
8. **State Mutation Attempt & File Copying:** Orchestrator attempted to set stage via `academic_state_manager.py set-stage` (blocked by strict state machine), then executed `cp` commands to create `Chapter_4.md` and `Chapter_4.docx`.
9. **Stage Completion Report:** Orchestrator emitted a Directive 11 Stage Completion Report and halted.

#### Task 3 Assessment
- **Delegation Verdict:** **SUCCESSFUL (2 subagents invoked sequentially: `academic-writer`, then `validation-agent`)**.
- **Worker Execution:** **YES (`academic-writer` generated high-fidelity Persian academic prose, tables, and OpenXML document)**.
- **Critic Execution:** **YES (`validation-agent` performed comprehensive verification)**.
- **Defects Identified:**
  - Active polling loop using `manage_subagents`.
  - Orchestrator executed file management (`cp`) and attempted direct state mutation via shell commands.

---

## 4. Key Behavioral Findings & Diagnostic Root Causes

### Finding 1: The "Path of Least Resistance" Delegation Failure
When an orchestrator possesses tools capable of executing code (`run_command`), the underlying LLM will consistently prefer executing simple Python/bash commands over formulating multi-turn subagent delegation envelopes. Delegation only occurred in Task 3 because writing long Persian chapters was clearly outside the orchestrator's behavioral comfort zone.

### Finding 2: Router Classification Fragility
In Task 2, `academic_task_router.py` failed on the literal string `"Calculate the repeated-measures analysis"`, returning `status: BLOCKED`. Instead of escalating to the user or falling back to `statistics-agent`, the orchestrator assumed executive responsibility and wrote an ad-hoc Python script.

### Finding 3: Polling Anti-Pattern in Subagent Management
The orchestrator has not internalized the reactive nature of Antigravity's wakeup mechanics. When dispatching `academic-writer`, it looped through `manage_subagents(Action="list")` rather than stopping its turn.

---

## 5. Architectural Improvements Mandate for Phase 1+

To establish true managerial delegation and satisfy Directive 12.1 and Directive 19:
1. **Revoke Code Execution Privileges from Orchestrators:** `academic-orchestrator` must not possess `run_command`. Code execution belongs exclusively to Tier 3 Specialist Workers (`statistics-agent`, `data-agent`, etc.).
2. **Mechanical Lifecycle Enforcement:** Implement an Antigravity `PreToolUse` hook that blocks any agent with `role: orchestrator` from calling `run_command` with Python scripts or data transformation binaries.
3. **Router Grammar Expansion:** Ensure `academic_task_router.py` robustly maps all common analysis prompts (repeated measures, mixed ANOVA, ANCOVA, regression, mediation) to their designated capability stages.
4. **Reactive Wakeup Training:** Explicitly prompt orchestrators to yield control immediately after calling `invoke_subagent`.
