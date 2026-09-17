# Lifecycle Hooks & Machine Enforcement Architecture

This document specifies the **machine-enforced lifecycle hooks** that protect system integrity, prevent instruction drift, enforce data immutability, and gate turn completion in the Academic Suite.

---

## 1. Overview & Architectural Rationale

While system prompts and agent contracts define expectations, LLMs are subject to **instruction drift** over long conversational trajectories. To guarantee absolute compliance with core research standards, critical invariants must be enforced outside the prompt context at the machine runtime layer.

Antigravity provides 5 lifecycle hooks (`PreInvocation`, `PostInvocation`, `PreToolUse`, `PostToolUse`, `Stop`). Academic Suite configures 4 active hooks via `.agents/hooks.json`:

```
               ┌───────────────────────┐
               │    User Invocation    │
               └───────────┬───────────┘
                           │
                           ▼
                    [PreInvocation] ──► Injects Constitutional Reminder
                           │
                           ▼
                 ┌───────────────────┐
                 │  Agent Proposes   │
                 │     Tool Call     │
                 └─────────┬─────────┘
                           │
                           ▼
                    [PreToolUse] ─────► Raw-Data Protection Guard
                           │            (Blocks modifications to raw datasets)
                           ▼
                 ┌───────────────────┐
                 │  Tool Executes    │
                 └─────────┬─────────┘
                           │
                           ▼
                    [PostToolUse] ────► Append Audit Event to audit_log.jsonl
                           │
                           ▼
                 ┌───────────────────┐
                 │   Agent Halts /   │
                 │   Attempts Stop   │
                 └─────────┬─────────┘
                           │
                           ▼
                        [Stop] ───────► Required Validation & Triad Gate
                                        (Blocks stop if validation fails or triad missing)
```

---

## 2. Hook 1 — Raw-Data Protection (`PreToolUse`)

### Mission
Guarantee the **absolute immutability of raw datasets**. Once raw data enters the research project directory, no agent or script may modify, overwrite, truncate, or delete it.

### Target Matcher
`run_command|write_to_file|replace_file_content`

### Enforcement Logic (`transcript_and_rule_guard.py:handle_pre_tool_use`)
1. **File Modification Interception (`write_to_file`, `replace_file_content`)**:
   - Inspects `args.TargetFile`.
   - Blocks if path contains `raw`, `raw_data`, `raw_inputs`, `01_raw_inputs`, `01_raw`.
   - Blocks if filename starts with `raw_`, ends with `_raw.*`, or matches `raw.(xlsx|csv|sav)`.
   - Returns:
     ```json
     {
       "decision": "deny",
       "reason": "HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Modification of raw dataset file '...' is strictly prohibited."
     }
     ```
2. **Shell Command Interception (`run_command`)**:
   - Inspects `args.CommandLine`.
   - Blocks destructive shell operations targeting raw paths (`rm`, `mv`, `>`, `>>`, `truncate`, `sed -i`, `cp ... raw`).
   - Returns:
     ```json
     {
       "decision": "deny",
       "reason": "HARD HOOK ENFORCEMENT (Raw-Data Immutability Guard): Command attempts to modify, overwrite, or delete raw data files."
     }
     ```

### Prescribed Workflow
Data Agent reads raw inputs from `01_raw_inputs/data_raw.xlsx`, cleans, scores, and transforms variables, and writes strictly to separate analytical paths (e.g. `01_raw_inputs/data_scored.xlsx` or `01_data/data_cleaned.xlsx`).

---

## 3. Hook 2 — Required Validation Gate (`Stop`)

### Mission
Prevent premature turn completion or unverified stage release. An agent cannot declare a stage finished or conclude an analytical turn if stage artifacts fail deterministic validation or violate the Triad Artifact Invariant.

### Target Matcher
Execution loop termination (`Stop` event).

### Enforcement Logic (`transcript_and_rule_guard.py:handle_stop`)
1. **Triad Artifact Invariant (Directive 3)**:
   - Scans active project and stage directories for micro-stage artifacts (`01_demographics`, `06_hypothesis_1`, etc.).
   - Verifies that every micro-stage produces the complete synchronized triad on disk:
     - `.docx` (Institutional Word Document)
     - `.md` (Scholarly Narrative & Tables)
     - `.json` (Structured Test Statistics & Parameters)
   - If any member of the triad is missing, the hook intercepts and returns:
     ```json
     {
       "decision": "continue",
       "reason": "HARD HOOK ENFORCEMENT (Directive 3 - Triad Artifact Invariant): Stage '...' has incomplete physical artifacts. Missing: [...]"
     }
     ```
2. **Deterministic Validator Gate**:
   - Dynamically invokes `validators/run_all_validators.py --stage-dir <path>` across all active stage directories containing `.json` and `.md` artifacts.
   - If any validator reports `FAIL` (e.g., reporting errors, unverified statistical assumptions, or numerical mismatches), the hook blocks turn completion:
     ```json
     {
       "decision": "continue",
       "reason": "HARD HOOK ENFORCEMENT (Required Validation Gate): Automated deterministic validation failed for stage directory '...'. Failures: [...]. Resolve errors before finishing."
     }
     ```
3. **Existing Validation Report Inspection**:
   - Checks `validation_report.json` on disk. If an existing report recorded `overall_verdict: FAIL`, completion is mechanically prohibited.

---

## 4. Hook 3 — Audit Logging (`PostToolUse`)

### Mission
Maintain an append-only, forensic log of all tool executions for compliance audits, error analysis, and post-session review.

### Target Matcher
`run_command|write_to_file|replace_file_content`

### Storage Destination
`.agents/memory/audit_log.jsonl` (gitignored to keep repository diffs clean).

### Record Schema
Each line in `audit_log.jsonl` contains a single JSON object:
```json
{
  "timestamp": "2026-09-17T05:12:05.290956+00:00",
  "conversation_id": "0763b519-2f67-40f0-b034-5a17140fc9fc",
  "step_index": 589,
  "tool_name": "run_command",
  "tool_args": {
    "CommandLine": "python3 tests/test_lifecycle_hooks.py",
    "Cwd": "/home/ghaderi-saber/Desktop/AcademicSuite"
  },
  "error": null,
  "status": "SUCCESS"
}
```

Large payload bodies (such as `CodeContent` in `write_to_file` or `ReplacementContent` in `replace_file_content`) are sanitized out to maintain a lightweight, highly responsive log.

---

## 5. Hook Configuration (`.agents/hooks.json`)

The hook configuration binds Antigravity events to the guard script:

```json
{
  "constitutional-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import os, sys; s = 'verification/transcript_and_rule_guard.py' if os.path.exists('verification/transcript_and_rule_guard.py') else '.agents/verification/transcript_and_rule_guard.py'; os.execv(sys.executable, [sys.executable, s] + sys.argv[1:])\" --event PreToolUse",
            "timeout": 15
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"import os, sys; s = 'verification/transcript_and_rule_guard.py' if os.path.exists('verification/transcript_and_rule_guard.py') else '.agents/verification/transcript_and_rule_guard.py'; os.execv(sys.executable, [sys.executable, s] + sys.argv[1:])\" --event PostToolUse",
            "timeout": 15
          }
        ]
      }
    ],
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 -c \"import os, sys; s = 'verification/transcript_and_rule_guard.py' if os.path.exists('verification/transcript_and_rule_guard.py') else '.agents/verification/transcript_and_rule_guard.py'; os.execv(sys.executable, [sys.executable, s] + sys.argv[1:])\" --event PreInvocation",
        "timeout": 15
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 -c \"import os, sys; s = 'verification/transcript_and_rule_guard.py' if os.path.exists('verification/transcript_and_rule_guard.py') else '.agents/verification/transcript_and_rule_guard.py'; os.execv(sys.executable, [sys.executable, s] + sys.argv[1:])\" --event Stop",
        "timeout": 15
      }
    ]
  }
}
```

---

## 6. Automated Test Verification

All three hooks are verified by the unit test suite in `tests/test_lifecycle_hooks.py`:
- `test_01_raw_data_protection_write`: Verifies `PreToolUse` blocks direct writes to raw data paths.
- `test_02_clean_data_write_allowed`: Verifies `PreToolUse` allows writes to code and analytical deliverables.
- `test_03_raw_data_protection_command`: Verifies `PreToolUse` blocks destructive shell commands targeting raw data.
- `test_04_audit_logging`: Verifies `PostToolUse` appends events to `.agents/memory/audit_log.jsonl`.
- `test_05_triad_artifact_stop_gate`: Verifies `Stop` hook blocks termination when a stage lacks the full triad (`.docx`, `.md`, `.json`).

Run the suite at any time:
```bash
python3 tests/test_lifecycle_hooks.py
```
