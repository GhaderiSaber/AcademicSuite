# AcademicSuite Learning Gaps Audit: Missing Telemetry, Silos, and Attribution Deficits

**Document Version:** 1.0.0  
**Audit Date:** September 2026 (1405 SH)  
**Status:** Comprehensive Gap Analysis  
**Methodology:** Direct inspection of `.agents/`, `contracts/`, `validators/`, `scripts/`, `evals/`, and project directories.

---

## 1. Executive Summary of Learning Gaps

While AcademicSuite possesses sophisticated execution, validation, and gating controls, it currently lacks an **autonomous behavioral feedback loop**. The existing system exhibits five structural gaps:

1. **Storage Silo Fragmentation:** Rich trajectory data (tool calls, thinking traces, raw inputs/outputs) is trapped in Antigravity's session-specific `transcript.jsonl` and is not mirrored into durable project state.
2. **Unstructured Human Feedback:** Conversational user corrections, supervisor critiques, and defense committee feedback remain as unstructured natural language text in chat, unparsed into persistent learning signals.
3. **Absence of Root-Cause Attribution:** Validation failures and Challenger critiques document *symptoms* (e.g. `CHK-APA-LEADING-ZERO: FAIL`), but do not diagnose *causes* (e.g. "Is the prompt flawed?", "Did the agent forget to call the script?", or "Is the script regex defective?").
4. **Static Behavior vs. Dynamic Memory:** While case precedents can be appended to `.agents/memory/cases/`, the active behavioral instructions (`agent.md`, `contract.md`, `SKILL.md`) remain static.
5. **No Evaluation & Promotion Harness:** There is no infrastructure to stage a candidate prompt or heuristic improvement, run regression benchmarks against it, and safely promote or roll it back.

---

## 2. Granular Inspection of the 14 Information Capture Dimensions

### 2.1 User Corrections
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - `continuous_learning_engine.py:record_human_outcome()` accepts structured dictionaries with `action: AGREE | ADJUST | OVERRIDE`, `divergence_rationale`, and `lessons_learned`.
  - `contracts/approval.schema.json` captures human approver `comments` and `conditions_or_stipulations`.
  - `skills/persian-thesis-revision-assistant/` formats formal Point-by-Point Response Tables.
- **The Gap:**
  - During live pair-programming sessions in Antigravity, user corrections often take the form of conversational chat messages (e.g. *"No, my advisor said we must use split-plot ANOVA instead of ANCOVA because of non-parallel slopes"*, or *"Fix the table, the numbers are missing leading zeros"*).
  - These conversational corrections exist **only** as `USER_INPUT` steps in `transcript.jsonl`. They are not automatically parsed, categorized, or fed into the decision journal or pitfall registry.
  - **Unknown Information:** User satisfaction after final release outside the conversation is **UNKNOWN**.

### 2.2 Agent Actions
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Macro lifecycle events are recorded in `academic-state/events.jsonl` (`MILESTONE_STARTED`, `PLAN_CREATED`, `EXECUTION_STARTED`, `EXECUTION_COMPLETED`, `VALIDATION_STARTED`).
  - `contracts/execution_manifest.schema.json` records high-level pipeline steps, assigned subagents, and skill names.
- **The Gap:**
  - Micro-actions—exact tool call sequences, internal chain-of-thought (`thinking`), intermediate file views, and grep searches—exist exclusively in Antigravity's internal transcript log (`~/.gemini/antigravity/brain/<cid>/.system_generated/logs/transcript.jsonl`).
  - When an Antigravity conversation ends or context is compacted, this fine-grained action history is disconnected from the project repository.

### 2.3 Agent Decisions
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - High-stakes research decisions (statistical test selection, sample size compromises, price quotations) are logged in `.agents/memory/decisions/*.json` via `decision_journal_engine.py` and in `academic-state/decisions.json`.
  - Statistical analysis strategy is formalized in `analysis_plan.json`.
  - Rejected candidate approaches are recorded in `state/pitfalls.jsonl`.
- **The Gap:**
  - Tactical operational decisions (e.g. deciding which literature database to search first, deciding to re-run a script with altered flags, adjusting paragraph cadence) are not journaled.
  - The link between an agent's internal rationale and the eventual validation outcome is not systematically correlated.

### 2.4 Tool Usage
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Tool invocations are captured in Antigravity's `transcript.jsonl` and intercepted in real-time by `.agents/verification/transcript_and_rule_guard.py` (`PreToolUse`, `PostToolUse`).
  - Terminal CLI script execution is recorded in `contracts/execution_manifest.schema.json`.
- **The Gap:**
  - No aggregated telemetry exists across sessions. There is no repository-level record of tool error rates, tool timeouts, or tool misuse patterns (e.g. attempting to use `replace_file_content` on read-only raw data).

### 2.5 Skill Usage
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Skills are declared in agent frontmatter (`skills:` list), emitted in Pre-Flight Declarations (Directive 1), and logged in `execution_manifest.schema.json` (`steps[].skill_name`).
- **The Gap:**
  - No performance metrics are captured per skill. The system cannot answer: *"Which skill fails validation most frequently?"*, *"Which skill produces the most typography warnings?"*, or *"Which skill exceeds token budget limits?"*.

### 2.6 Subagent Delegation
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - Subagent invocations are recorded in `transcript.jsonl` (`invoke_subagent`), verified by the Antigravity `Stop` hook (Directive 0 & 12 honesty gate), and structured via `contracts/handoff.schema.json` envelopes.
- **The Gap:**
  - While delegation calls are fully captured, the *quality* and *efficiency* of subagent delegation (e.g. whether a subagent was provided insufficient context requiring unnecessary tool lookups) is not evaluated.

### 2.7 Artifacts
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - Synchronized Triad Invariant (`.docx`, `.md`, `.json`) is mechanically enforced on disk by `transcript_and_rule_guard.py:handle_stop()`.
  - Tracked with cryptographic SHA-256 hashes, timestamps, and producer IDs in `contracts/artifact_manifest.schema.json` and `academic-state/artifacts.json`.
- **The Gap:**
  - Artifact tracking is mature; the only gap is historical diffing across revision cycles (e.g. tracking how `06_hypothesis_1.docx` changed between attempt 1 and attempt 2).

### 2.8 Validation Failures
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - `contracts/validation_report.schema.json` enforces a strict 5-tier status taxonomy (`PASS`, `FAIL`, `BLOCKED`, `INCOMPLETE`, `UNKNOWN`).
  - `validators/run_all_validators.py` aggregates itemized check failures across 5 validator engines.
  - Failures trigger `VALIDATION_FAILED` events and are logged to `state/pitfalls.jsonl` under category `validation`.
- **The Gap:**
  - Failures are captured, but **diagnosis of cause** is manual. The system does not automatically classify whether a failure was caused by prompt ambiguity, a missing skill instruction, or a code bug.

### 2.9 Challenger Findings
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - `scripts/candidate_falsifier_engine.py` invokes `AcademicChallenger` to falsify candidate analysis plans.
  - Returns non-numeric categorical verdicts (`SUPPORTED`, `WEAK`, `CONDITIONAL`, `REJECTED`).
  - Automatically records rejected approaches into `state/pitfalls.jsonl` via `AcademicPitfallRegistry` with `reusable: true`.
- **The Gap:**
  - Challenger findings are indexed to prevent *repeating* the same flawed candidate approach, but they do not automatically update the candidate generator's heuristics to prevent *generating* flawed candidates in the first place.

### 2.10 Successful Outcomes
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Validated artifacts receive `overall_verdict: "PASS"`.
  - Milestones transition to `MilestoneState.APPROVED`.
  - Human sign-off is recorded with `status: "GRANTED"` in `contracts/approval.schema.json`.
  - `continuous_learning_engine.py` reinforces precedent case confidence weights on agreement.
- **The Gap:**
  - Success is captured at the internal machine gate level.
  - Real-world external outcomes (e.g. thesis grade awarded by external university examiner, journal peer-review acceptance) are **UNKNOWN** unless manually input.

### 2.11 Failed Outcomes
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - Machine crashes, timeout exceptions, schema validation errors, and validator rejections strictly transition milestones to `FAILED` or `REJECTED`.
  - Enforced by fail-closed exception hierarchies in `academic_state_manager.py` and `academic_event_engine.py`.
- **The Gap:**
  - The state machine halts and logs failure; however, there is no automated post-mortem synthesis analyzing systemic failure clusters across multiple projects.

### 2.12 Revision Cycles
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Milestone transitions `FAILED -> READY/PLANNED` and `REJECTED -> PLANNED/SCOPED` are logged in the milestone `history` array.
  - `events.jsonl` logs `REVISION_REQUESTED`.
  - `skills/persian-thesis-revision-assistant/` tracks point-by-point reviewer feedback.
- **The Gap:**
  - The number of revision cycles is not aggregated as a quality metric.
  - There is no automated analysis of *why* revisions occur or whether certain supervisor profiles consistently require specific structural adjustments.

### 2.13 Final User Acceptance
- **Current Capture Status:** **PARTIALLY CAPTURED**
- **Existing Mechanism:**
  - Category `final_dissertation_release` and `defense_readiness_clearance` in `contracts/approval.schema.json`.
  - Requires explicit digital signature or acknowledgment from Saber Admin Desk (`124911145`).
  - `final-judge` emits the Iranian defense scorecard (0–20 scale).
- **The Gap:**
  - Post-defense institutional outcomes (actual university defense grade, external examiner comments, committee revisions) are **UNKNOWN** to the local repository.

### 2.14 Statistical Execution Metadata
- **Current Capture Status:** **CAPTURED**
- **Existing Mechanism:**
  - `contracts/execution_manifest.schema.json` captures command line, Python/R interpreter, dataset SHA-256 fingerprint, script identity hash, and output artifact paths.
  - `stats_results.json` captures exact degrees of freedom, effect sizes, test statistics, and fit indices.
- **The Gap:**
  - Fully captured and reproducible; no significant gaps in execution metadata.

---

## 3. The Attribution Deficit: Why Captured Failures Do Not Produce Learning

The central diagnostic insight of this audit is that **AcademicSuite has abundant telemetry but zero automated attribution**:

```text
CURRENT STATE:
Validation Failure Detected (e.g. "Missing leading zero in 06_hypothesis_1.md: .041")
       │
       ▼
Logged in validation_report.json & events.jsonl
       │
       ▼
Stage Halted / Retry Triggered (Human or Agent manually edits text)
       │
       ▼
STOPS HERE: System never asks WHY the agent produced .041 instead of ۰.۰۴۱.
            No prompt is updated. No skill is refined. No heuristic is saved.
            Next week, the same agent will make the exact same error again.
```

### The Three Missing Diagnostic Capabilities:
1. **Source Attribution:** Distinguishing between:
   - *Prompt Deficit:* The agent prompt did not emphasize the rule strongly enough.
   - *Skill Script Deficit:* The underlying Python generation script omitted a formatting step.
   - *Data Anomaly:* The input data contained an extreme distribution requiring special handling.
   - *Model Capability Deficit:* The LLM degraded due to context saturation.
2. **Hypothesis Formulation:** Translating a diagnosed root cause into a falsifiable candidate improvement (e.g. *"Adding an explicit regex formatting filter in `generate_hypothesis_triad_docx.py` will eliminate 100% of missing leading zeros in Persian output"*).
3. **Regression Auditing:** Proving that the candidate improvement fixes the defect without breaking any other constitutional invariant.

---

## 4. Unknown Information Registry

To strictly adhere to acceptance criteria, the following information is documented as **UNKNOWN**:

1. **Post-Submission Institutional Outcomes:** Real-world university defense grades, committee deliberation transcripts, and final Irandoc registration confirmations are not captured by local telemetry.
2. **Journal Peer-Review Cycles:** External journal reviewer reports, revision letters, and editorial decisions are not systematically tracked unless manually placed in project folders.
3. **Cross-Project Subagent Performance Trends:** Because each project maintains its own isolated `academic-state/` directory, global historical performance metrics across different project workspaces are currently unindexed.
4. **Non-Recorded Conversational Corrections:** User corrections made in previous Antigravity chat sessions whose transcripts were purged or stored in other user profiles are permanent unknowns.
