# AcademicSuite Integration Points: Continuous Behavioral Self-Improvement

**Document Version:** 1.0.0  
**Audit Date:** September 2026 (1405 SH)  
**Status:** Approved Architectural Specification  
**Core Law:** Integrate with existing production machinery without altering runtime invariants, modifying permissions, or violating the Sole Orchestrator Mandate (Directive 12.1).

---

## 1. Physical & Architectural Integration Map

The self-improvement subsystem does not replace existing execution components; it establishes passive taps and active evaluation hooks into the 7 primary execution boundaries of AcademicSuite:

```text
                                USER / RESEARCHER
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. HOOK BOUNDARY (.agents/hooks.json & transcript_and_rule_guard.py)        │
│    - Intercepts PreToolUse, PostToolUse, and Stop events                     │
│    - Trajectory Capture: Extracts tool calls, script arguments, and exits   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. ORCHESTRATOR & CAPABILITY BOUNDARY (scripts/academic_task_router.py)     │
│    - Task Recognition & Ordering: RESEARCH -> DATA -> STATS -> WRITING      │
│    - Route Verification: Resolves capability to skill and subagent          │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. STATE MACHINE BOUNDARY (scripts/academic_state_manager.py)               │
│    - Milestone Transitions: CREATED -> RUNNING -> VALIDATING -> APPROVED    │
│    - State Taps: Captures transition rationales, retries, and failures      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. DETERMINISTIC EXECUTION BOUNDARY (scripts/statistical_pipeline_engine.py)│
│    - Execution Manifests: CLI commands, dataset hashes, exit codes          │
│    - Hands Execution: Captures exact numerical output & script crashes       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. ADVERSARIAL CHALLENGER BOUNDARY (scripts/candidate_falsifier_engine.py)  │
│    - Candidate Deliberation: Multi-path generation (Saber vs Orthodox)      │
│    - Invalidation Tap: Captures rejected approaches into state/pitfalls.jsonl│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. DETERMINISTIC VALIDATOR BOUNDARY (validators/run_all_validators.py)      │
│    - 5 Domain Validators: Data, Numbers, Assumptions, Results, Reporting    │
│    - Validation Report: Captures itemized failures and evidence objects     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. HUMAN APPROVAL DESK BOUNDARY (contracts/approval.schema.json)            │
│    - Admin Desk Gate: Saber Ghaderi (124911145) approval cards              │
│    - Human Feedback Tap: Captures overrides, comments, and stipulations     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Trajectory Data Capture Points

Trajectory data must capture the complete causal chain: What was requested $\rightarrow$ What was planned $\rightarrow$ What was executed $\rightarrow$ What failed/succeeded $\rightarrow$ How it was corrected.

### Point 1: Antigravity Lifecycle Hook Boundary (`.agents/hooks.json`)
- **Location:** `.agents/verification/transcript_and_rule_guard.py`
- **Tapped Events:** `PostToolUse` and `Stop`.
- **Payload Captured:** Tool name, exact arguments, tool exit/return payload, conversation step index, and raw user prompts.
- **Integration Mechanism:** `PostToolUse` can append structured interaction events to a local trajectory buffer without interrupting runtime execution.

### Point 2: Event Engine Tap (`scripts/academic_event_engine.py`)
- **Location:** `AcademicEventEngine.emit()` in `scripts/academic_event_engine.py:165`.
- **Tapped Events:** All 14 canonical event types (`EXECUTION_STARTED`, `EXECUTION_COMPLETED`, `VALIDATION_FAILED`, `CRITIQUE_CREATED`, `REVISION_REQUESTED`, `MILESTONE_FAILED`, etc.).
- **Payload Captured:** Monotonic timestamp, project ID, milestone ID, stage ID, emitter agent, summary, artifact IDs, metrics, and execution details.
- **Integration Mechanism:** `AcademicEventEngine` already validates against `contracts/event.schema.json` and writes to `academic-state/events.jsonl`. This stream provides the primary chronological backbone for trajectory reconstruction.

### Point 3: State Machine Lifecycle Tap (`scripts/academic_state_manager.py`)
- **Location:** `StrictStateMachine.transition_milestone()` in `scripts/academic_state_manager.py:448`.
- **Tapped Transitions:** `RUNNING -> FAILED`, `VALIDATING -> FAILED`, `AWAITING_APPROVAL -> REJECTED`, and `VALIDATING -> AWAITING_APPROVAL`.
- **Payload Captured:** `from_state`, `to_state`, `actor`, `rationale`, `execution_info`, and the full transition `history` array.
- **Integration Mechanism:** Whenever a failure or rejection transition occurs, the state manager already logs the event and updates `current_state.json`.

### Point 4: Execution Manifest Collector (`scripts/statistical_pipeline_engine.py`)
- **Location:** `contracts/execution_manifest.schema.json` and CLI runner output.
- **Payload Captured:** `manifest_id`, `analysis_plan_hash`, `input_dataset_hash`, `dataset_provenance` (SHA-256, schema fingerprint), `code_identity`, `command`, `exit_code`, `produced_artifacts` with hashes, and exact execution duration.
- **Integration Mechanism:** Serialized alongside outputs in `academic-state/outputs/execution_manifest.json`.

### Point 5: Deterministic Validator Suite Tap (`validators/run_all_validators.py`)
- **Location:** `run_suite()` in `validators/run_all_validators.py:54`.
- **Payload Captured:** Complete `validation_report.json` conforming to `contracts/validation_report.schema.json`:
  - `overall_verdict` (`PASS`, `FAIL`, `BLOCKED`, `INCOMPLETE`).
  - `evidence_summary` (total items evaluated, checks run, checks failed, checks blocked).
  - Itemized `results[]` array with `check_id`, `rule`, `verdict`, `errors`, `warnings`, and concrete `evidence` dictionaries.

### Point 6: Challenger Falsifier Tap (`scripts/candidate_falsifier_engine.py`)
- **Location:** `AcademicChallenger.falsify_candidate()` and `CandidateDeliberationEngine.deliberate()`.
- **Payload Captured:** Proposed candidate analysis plans, challenger categorical verdicts (`SUPPORTED`, `WEAK`, `CONDITIONAL`, `REJECTED`), detailed counter-evidence, and corrective actions persisted via `AcademicPitfallRegistry`.

### Point 7: Human Approval Desk Tap (`contracts/approval.schema.json`)
- **Location:** `scripts/academic_state_manager.py:apply_approval()` and `scripts/admin_desk.py`.
- **Payload Captured:** Approval category (`project_pricing`, `methodology_specification`, `supervisor_comment_override`), status (`GRANTED`, `REJECTED`), `approver_identity`, `comments`, `conditions_or_stipulations`, and `target_artifacts`.

---

## 3. Learning Trigger Points

Learning must not occur randomly or continuously in an uncontrolled background loop. It must be triggered at deterministic lifecycle moments:

### Trigger A: Immediate Failure-Driven Learning (On Verification Failure)
- **Condition:** `validators/run_all_validators.py` returns `FAIL` or `BLOCKED`, or `transcript_and_rule_guard.py` intercepts a rule violation.
- **Trigger Event:** `VALIDATION_FAILED` or `MILESTONE_FAILED`.
- **Action:** Captures the failing artifact, extracts the violated rule and error evidence, creates a diagnostic record, and checks whether this error pattern matches an existing pitfall in `state/pitfalls.jsonl`.

### Trigger B: Adversarial Challenger Trigger (On Hypothesis/Model Rejection)
- **Condition:** `academic-challenger` falsifies a candidate statistical plan during `M6_MODEL_DELIBERATION`.
- **Trigger Event:** `CRITIQUE_CREATED` with status `REJECTED`.
- **Action:** Triggers `AcademicPitfallRegistry.create()` with `reusable: true`, recording why the candidate approach was invalid and what adapted approach was selected.

### Trigger C: Human Supervisor Feedback Trigger (On Human Rejection or Override)
- **Condition:** Saber Admin Desk (`124911145`) or the researcher rejects a milestone (`approval.status == "REJECTED"`), requests revisions (`REVISION_REQUESTED`), or provides diverging methodological decisions via `continuous_learning_engine.py`.
- **Trigger Event:** `MILESTONE_REJECTED` or human outcome recorded with `congruence_score < 1.0`.
- **Action:** Ingests human rationale and lessons learned, extracts divergence heuristics, and logs a candidate behavioral adjustment.

### Trigger D: Milestone Acceptance Trigger (On Clean Passing Success)
- **Condition:** Milestone successfully transitions to `APPROVED` with 100% passing deterministic validation.
- **Trigger Event:** `MILESTONE_APPROVED`.
- **Action:** Reinforces successful precedent cases in `CaseMemoryEngine` (increments confidence weights) and logs the successful execution manifest as a positive gold-standard exemplar.

### Trigger E: Post-Engagement Reflection (Batch / Periodic)
- **Condition:** Full dissertation or milestone pipeline concludes, or the user triggers the `/learn` slash command.
- **Trigger Action:** Sweeps accumulated episodic trajectory logs, clusters repeated validation warnings or retries, identifies candidate prompt/skill refinements, and schedules them for offline evaluation.

---

## 4. Participating Cognitive Roles & Agent Responsibilities

Self-improvement requires strict separation between **Diagnosticians**, **Synthesizers**, **Evaluators**, and **Target Workers**:

| Cognitive Role | Agent Package | Self-Improvement Responsibility | Permitted Actions |
| :--- | :--- | :--- | :--- |
| **Meta-Cognitive Conductor** | `academic-orchestrator` / `digital-saber` | Coordinates the self-improvement workflow, triggers candidate evaluation suites, and stages approved updates. | Invoke evaluators, read trajectories, write candidate specifications. |
| **Adversarial Falsifier** | `academic-challenger` | Diagnoses root causes of methodological and design failures; red-teams candidate improvements for unintended regression or vulnerability. | Inspect failure records, formulate counter-cases, score candidate robustness. |
| **Statistical Diagnostician** | `statistical-auditor` | Diagnoses statistical assumption breaches, degrees of freedom math errors, variance deflation, and MSAI anomalies. | Inspect statistical outputs, audit mathematical parameters, verify formulas. |
| **Rhetorical Diagnostician** | `results-auditor` | Diagnoses APA 7 table formatting failures, Persian leading zero breaches, and BiDi typography defects. | Inspect OpenXML Word and Markdown artifacts, audit formatting compliance. |
| **Epistemic Diagnostician** | `evidence-auditor` | Diagnoses citation discordance, ghost references, selective literature omissions, and Irandoc similarity failures. | Cross-check bibliographies against databases, audit similarity metrics. |
| **Institutional Gatekeeper** | `final-judge` | Conducts independent evaluation of candidate behavioral improvements against the permanent benchmark suite (`evals/run_eval_suite.py`) and Iranian defense criteria. | Run evaluation suites, verify scorecards, block non-conforming promotions. |
| **Target Worker Agents** | `statistics-agent`, `data-agent`, `academic-writer`, `research-agent` | Subjects of improvement. Their prompt guidelines, skill scripts, or heuristics are refined based on validated improvements. | Execute updated behavior once promoted; NEVER self-modify or self-promote. |

---

## 5. Skills to be Extended vs. New Specialized Skills

### 5.1 Existing Skills to be Extended
- **`thesis-integrity-auditor` (`.agents/skills/thesis-integrity-auditor/`)**:
  - *Extension:* Add diagnostic classification procedures mapping raw validator error strings to canonical pitfall categories.
  - *Constraint:* Must remain under 500 lines / 40 KB per Directive 18. Extended rubrics modularized into `references/`.
- **`digital-twin-academic-consultant` (`.agents/skills/digital-twin-academic-consultant/`)**:
  - *Extension:* Integrate continuous learning queries into proposal evaluation and price estimation.
- **`academic-suite-orchestrator` (`.agents/skills/academic-suite-orchestrator/`)**:
  - *Extension:* Add CLI commands to trigger offline evaluation regression sweeps (`python3 evals/run_eval_suite.py`).

### 5.2 New Specialized Evolution Skills (Future Implementation)
To avoid polluting existing domain skills with self-improvement meta-logic, dedicated modular skills should be introduced when implementation begins:
- `behavioral-diagnostician`: Extracts structured failure diagnostics from execution trajectories and validation reports.
- `candidate-evaluator`: Runs regression benchmarks comparing baseline behavior vs candidate improvements.
- `knowledge-curator`: Calibrates decision rules and manages the promotion of candidate heuristics into persistent memory.

---

## 6. Architectural Compatibility & Conflict Analysis

### 6.1 Compatibility with Existing Architecture
- **Reuse of Existing Contracts:** The 10 existing schemas in `contracts/` already define `event`, `pitfall`, `validation_report`, `execution_manifest`, and `approval`. Self-improvement builds directly on these schemas without schema duplication.
- **Reuse of Deterministic Validators:** The 5 validator suites in `validators/` serve as the deterministic ground-truth judges for behavioral improvements.
- **Reuse of Permanent Evals:** `evals/run_eval_suite.py` provides an existing 9-domain benchmark suite.

### 6.2 Strict Invariants & Anti-Conflict Rules

| Invariant | Potential Conflict | Architecture Rule to Prevent Violation |
| :--- | :--- | :--- |
| **Directive 12.1 (Sole Orchestrator Mandate)** | Building an external Python daemon or background agent dispatcher loop to manage self-improvement. | **STRICTLY PROHIBITED.** Antigravity is the sole agent runtime. All agent invocations must occur via native `invoke_subagent`. Self-improvement analysis runs as explicit, user-visible stages or slash commands (`/learn`). |
| **Directive 0 (Binary Honesty Protocol)** | AI fabricating improvement benchmarks or claiming a candidate passed evaluation when tests were skipped. | **STRICTLY PROHIBITED.** Candidate improvements cannot be promoted without physical, verified `evaluation_report.json` artifacts generated on disk by deterministic test scripts. |
| **Directive 6 (English-Only Filenames)** | Storing learned cases, candidate files, or evaluation logs with Persian names. | **STRICTLY PROHIBITED.** All trajectory logs, candidate files, and evaluation outputs must strictly use ASCII English characters (`[a-zA-Z0-9_.-]`). |
| **Directive 18 (Skill Modularity Standard)** | Expanding existing `SKILL.md` files with verbose self-improvement guidelines, exceeding 500 lines or 40 KB. | **STRICTLY PROHIBITED.** Core skill files must remain lean. Diagnostic rubrics must reside in modular `references/` subdirectories. |
| **Raw Data Immutability** | Writing self-improvement scratchpads or temporary evaluation runs into `01_raw_inputs/`. | **STRICTLY PROHIBITED.** `01_raw_inputs/` remains read-only (`0444`). Self-improvement artifacts must reside in dedicated evolution directories. |
| **Fail-Closed Promotion** | Allowing candidate improvements to take effect automatically without explicit human signoff. | **STRICTLY PROHIBITED.** Promotion to production active behavior requires Human Gate sign-off from Saber Admin Desk (`124911145`). |
