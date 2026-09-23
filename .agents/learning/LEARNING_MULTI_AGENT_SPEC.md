# LEARNING_MULTI_AGENT_SPEC.md — Native Multi-Agent Self-Improvement Architecture

## 1. Architectural Philosophy: Real Behavior & Role Separation

AcademicSuite's continuous self-improvement framework is grounded in **real observable agent behavior** rather than synthetic or hallucinated trajectories. The self-improvement architecture enforces a strict division of cognitive labor across six specialized learning subagents, each answering a single, unambiguous core question.

```mermaid
flowchart TD
    subgraph Trigger ["1. Trigger Source"]
        UF["USER_FEEDBACK_DETECTED (FeedbackRecord)"]
        VF["VALIDATION_FAILED (QC Anomaly)"]
    end

    subgraph NativeSubagents ["2. Antigravity Native Learning Subagents"]
        TA["trajectory-analyzer\n'What actually happened?'"]
        BA["behavior-analyst\n'What behavior was wrong?'"]
        KC["knowledge-curator\n'What generalizable lesson does this imply?'"]
        SE["skill-evolver (Branch Workspace)\n'What candidate modification would change the behavior?'"]
        EA["evaluation-agent (Branch Workspace)\n'Did the modification actually improve behavior?'"]
        CB["curriculum-builder\n'What future task would test whether the lesson generalizes?'"]
    end

    subgraph HumanGate ["3. Release Gate"]
        HG["Human Gate (Saber Admin Desk: 124911145)\nPromotion Decision & Canonical Merge"]
    end

    UF -->|Transcript & Context| TA
    VF -->|Logs & Context| TA
    TA -->|TrajectoryRecord| BA
    BA -->|BehaviorAnalysisReport| KC
    KC -->|Staged Lesson / Anti-Pattern| SE
    SE -->|ImprovementCandidate (Diff)| EA
    EA -->|EvaluationResult (3-Arm Verdict)| HG
    KC -.->|Failure Modes| CB
    CB -->|CurriculumTask (L1-L4)| EA
```

---

## 2. The Six Core Questions & Operational Roster

| Subagent Identifier | The Core Question Answered | Cognitive Responsibility | Allowed Tools | Workspace Mode |
| :--- | :--- | :--- | :--- | :--- |
| **`trajectory-analyzer`** | *"What actually happened?"* | Reconstructs observable tool calls, script exits, parameter values, and artifact generation from transcript logs. Zero private chain-of-thought access. | `view_file`, `list_dir`, `grep_search`, `find_by_name` | `inherit` (Read-only) |
| **`behavior-analyst`** | *"What behavior was wrong?"* | Causal root-cause analysis. Pinpoints exact failure mechanisms, assumption violations, degree-of-freedom mismatches, and defect signatures. | `view_file`, `list_dir`, `grep_search`, `find_by_name` | `inherit` (Read-only) |
| **`knowledge-curator`** | *"What generalizable lesson does this imply?"* | Synthesizes persistent, versioned lessons, anti-patterns, principles, and exemplars. Enforces strict scope containment (`project` vs `cross-project`). | `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file` | `inherit` (Staging write-only) |
| **`skill-evolver`** | *"What candidate modification would change the behavior?"* | Synthesizes targeted candidate mutations (`improvement_candidate`) to Skills and deterministic scripts with unified diffs. | `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file` | `branch` (Isolated workspace) |
| **`evaluation-agent`** | *"Did the modification actually improve behavior?"* | Independently benchmarks candidates across 3-way evaluation arms (original, unadapted, adapted) and 8 dimensions. Forbids unverified declarations of success. | `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command` | `branch` (Execution-enabled) |
| **`curriculum-builder`** | *"What future task would test whether the lesson generalizes?"* | Architect graduated complexity challenge tasks (L1 to L4) and synthetic benchmark datasets targeting diagnosed agent weaknesses. | `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file` | `inherit` (Staging write-only) |

---

## 3. Deliberation Pipeline & Sequential Handoff Protocol

### Step 1: Trigger Ingestion & Event Deduplication
1. Triggers arrive via `USER_FEEDBACK_DETECTED` (from user corrections) or `VALIDATION_FAILED` (from MSAI / QC integrity hooks).
2. The orchestrator checks `processed_event_ids` in `learning/experience/processed_events.jsonl` to ensure zero duplicate processing (Phase 17).
3. Payload includes target metadata: `target_agent`, `target_skill`, `capability`, `task`, `stage`.

### Step 2: Observable Trajectory Reconstruction (`trajectory-analyzer`)
- **Invocation**: `invoke_subagent(TypeName="trajectory-analyzer", Prompt="Reconstruct observable trajectory for event EVT-...")`
- **Behavior**: Reads `transcript.jsonl` and disk artifacts. Extracts exact tool calls, CLI commands, exit codes, and output files.
- **Invariant**: Strict Zero CoT policy. Reconstructs observable actions only.
- **Output**: `learning/experience/trajectories/<session_id>/trajectory.json` compliant with `contracts/evolution/trajectory.schema.json`.

### Step 3: Causal Root-Cause Diagnosis (`behavior-analyst`)
- **Invocation**: `invoke_subagent(TypeName="behavior-analyst", Prompt="Diagnose root cause of failure in trajectory ...")`
- **Behavior**: Compares observed trajectory against expected skill contracts and statistical standards. Classifies failure mode signature (e.g. `MISSING_PERSIAN_LEADING_ZERO`, `VIOLATED_ASSUMPTION_IGNORED`). Formulates counterfactual.
- **Output**: `BehaviorAnalysisReport` compliant with `contracts/evolution/behavior_analysis.schema.json`.

### Step 4: Knowledge Distillation & Anti-Pattern Cataloging (`knowledge-curator`)
- **Invocation**: `invoke_subagent(TypeName="knowledge-curator", Prompt="Distill generalizable lesson and catalog anti-patterns from report ...")`
- **Behavior**: Formulates structured lesson candidate, updates anti-pattern catalog, defines boundary conditions.
- **Invariant**: Validated staging (`status: "VALIDATED"`, `is_active_behavior: true`). Active lessons are immediately consumed by agents and subagents in pre-flight briefings.
- **Output**: JSON files in `learning/knowledge/lessons/`, `anti-patterns/`, `exemplars/`.

### Step 5: Candidate Patch Synthesis (`skill-evolver`)
- **Invocation**: `invoke_subagent(TypeName="skill-evolver", Workspace="branch", Prompt="Synthesize candidate modification to address lesson ...")`
- **Behavior**: Operates in an isolated branched workspace. Formulates unified diff for target script or `SKILL.md`. Computes SHA-256 target checksum and projected metric improvements.
- **Invariant**: Zero direct mutation of canonical `.agents/skills/`. Must satisfy Directive 18 single-view ceilings (<= 500 lines, <= 40,000 bytes).
- **Output**: `learning/candidates/<candidate_id>/candidate.json` compliant with `contracts/evolution/improvement_candidate.schema.json`.

### Step 6: Independent Candidate Evaluation (`evaluation-agent`)
- **Invocation**: `invoke_subagent(TypeName="evaluation-agent", Workspace="branch", Prompt="Execute 3-way evaluation arm on candidate ...")`
- **Behavior**: Applies candidate diff in isolated branch workspace. Executes deterministic test harnesses (`run_command`) on baseline, unadapted candidate, and adapted candidate. Measures 8 multidimensional metrics:
  1. Success rate on triggering task
  2. Success rate on held-out tasks
  3. Regression rate on unrelated tasks
  4. Tool efficiency
  5. Context efficiency
  6. Human intervention rate
  7. Verification pass rate
  8. Anomaly score (MSAI)
- **Invariant**: Physical execution evidence required (exit code 0, test logs). Zero scalar intelligence scores.
- **Output**: `learning/evaluations/<eval_id>/evaluation_result.json` compliant with `contracts/evolution/evaluation_result.schema.json`.

### Step 7: Graduated Curriculum Expansion (`curriculum-builder`)
- **Invocation**: `invoke_subagent(TypeName="curriculum-builder", Prompt="Synthesize graduated curriculum task targeting weakness ...")`
- **Behavior**: Generates L1–L4 benchmark tasks and synthetic datasets with bounded empirical decimal noise ($\delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$) per Directive 9.
- **Output**: `evals/curriculum/<task_id>/curriculum_task.json` compliant with `contracts/evolution/curriculum_task.schema.json`.

### Step 8: Human-in-the-Loop Release Gate
- When `evaluation_result.overall_verdict == "PASS"`, the lead orchestrator notifies Saber's Admin Desk (`124911145`).
- Formal human approval records a `promotion_decision` in `learning/promotions/`. Only then is the candidate diff merged to canonical assets via conventional git commit.

---

## 4. Architectural Invariants (Zero Tolerance)

1. **Sole Orchestrator Mandate (Directive 12.1)**:
   - Antigravity is the sole agent runtime and orchestrator.
   - Python classes or scripts MUST NEVER emulate, manage, or dispatch subagents.
   - All subagents must be physically invoked via Antigravity's native `invoke_subagent` tool.
2. **Least-Privilege Enforcement**:
   - `trajectory-analyzer` and `behavior-analyst` are strictly read-only.
   - `knowledge-curator`, `skill-evolver`, and `curriculum-builder` have staging write tools but zero command execution.
   - `evaluation-agent` is the sole learning role equipped with `run_command` to execute deterministic test harnesses.
3. **Six-Part Functional Separation (Directive 19)**:
   - *Agent decides*: The 6 learning roles reason, diagnose, synthesize, and evaluate.
   - *Skill instructs*: Domain instructions guide specific analysis and reporting formats.
   - *Script computes*: Deterministic evaluation scripts and data simulators compute numbers and hashes.
   - *Hook enforces*: Lifecycle hooks intercept events and prevent unauthorized mutations.
   - *State machine authorizes*: Gated milestones control progression.
   - *Artifact manifest defines completion*: JSON schemas validate every stage output.
