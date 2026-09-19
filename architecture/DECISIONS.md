# AcademicSuite — Architectural Decision Records (ADRs)

**Document Version:** 1.0.0  
**Operative Date:** September 2026 (1405 SH)  
**Status:** Approved & Binding  

---

## Index of Architectural Decision Records

| ADR ID | Title | Status | Date |
|---|---|---|---|
| [ADR-001](#adr-001-antigravity-native-runtime-as-sole-multi-agent-orchestrator) | Antigravity Native Runtime as Sole Multi-Agent Orchestrator | Accepted | 2026-09-16 |
| [ADR-002](#adr-002-elimination-of-commandexecutionpolicy-from-agent-frontmatter) | Elimination of `commandExecutionPolicy` from Agent Frontmatter | Accepted | 2026-09-17 |
| [ADR-003](#adr-003-subagent-and-mainagent-discovery-semantics) | Subagent and MainAgent Discovery Semantics | Accepted | 2026-09-19 |
| [ADR-004](#adr-004-the-triad-artifact-invariant-and-one-hypothesis-one-stage) | The Triad Artifact Invariant and One-Hypothesis-One-Stage Granularity | Accepted | 2026-09-15 |
| [ADR-005](#adr-005-multi-layered-defense-in-depth-security-architecture) | Multi-Layered Defense-in-Depth Security Architecture | Accepted | 2026-09-18 |
| [ADR-006](#adr-006-hard-boundary-against-horizontal-growth-and-sprawl) | Hard Boundary Against Horizontal Growth & Architectural Sprawl | Accepted | 2026-09-19 |
| [ADR-007](#adr-007-the-six-part-functional-separation-invariant) | The Six-Part Functional Separation Invariant | Accepted | 2026-09-19 |
| [ADR-008](#adr-008-dynamic-orchestration-via-native-antigravity-subagent-capability-resolution) | Dynamic Orchestration via Native Subagent Capability Resolution | Accepted | 2026-09-19 |
| [ADR-009](#adr-009-methodology-decision-layer-and-formal-execution-contracts) | Methodology Decision Layer and Formal Execution Contracts (MDR) | Accepted | 2026-09-19 |
| [ADR-010](#adr-010-deterministic-statistical-execution-layer-and-elimination-of-mental-arithmetic) | Deterministic Statistical Execution Layer & Elimination of Mental Math | Accepted | 2026-09-19 |
| [ADR-011](#adr-011-complete-elimination-of-synthetic-data-escape-routes-and-universal-fail-closed-policy) | Complete Elimination of Synthetic Data Escape Routes | Accepted | 2026-09-19 |
| [ADR-012](#adr-012-formal-state-machine-engine-and-elimination-of-direct-stage-mutations) | Formal State Machine Engine & Elimination of Direct Stage Mutations | Accepted | 2026-09-19 |
| [ADR-013](#adr-013-authoritative-stage-manifests-and-cross-artifact-agreement-gating) | Authoritative Stage Manifests & Cross-Artifact Agreement Gating | Accepted | 2026-09-19 |
| [ADR-014](#adr-014-fail-closed-validation-architecture-and-sequential-gate-cascade) | Fail-Closed Validation Architecture and Sequential Gate Cascade | Accepted | 2026-09-19 |
| [ADR-015](#adr-015-cross-artifact-triad-consistency-validation-and-structured-docx-compilation) | Cross-Artifact Triad Consistency Validation & Structured DOCX Compilation | Accepted | 2026-09-19 |
| [ADR-016](#adr-016-separation-of-interpretation-from-evidence-and-5-link-claim-provenance) | Separation of Interpretation from Evidence & 5-Link Claim Provenance | Accepted | 2026-09-19 |
| [ADR-017](#adr-017-separated-writing-architecture-and-interpretation-contracts) | Separated Writing Architecture & Interpretation Contracts | Accepted | 2026-09-19 |
| [ADR-018](#adr-018-state-authorized-human-approval-engine-and-prohibition-of-prompt-based-halting) | State-Authorized Human Approval Engine & Elimination of Prompt Halting | Accepted | 2026-09-19 |
| [ADR-019](#adr-019-tripartite-lifecycle-hook-architecture-safety-integrity-learning-and-non-orchestrator-invariant) | Tripartite Lifecycle Hook Architecture & Non-Orchestrator Invariant | Accepted | 2026-09-19 |
| [ADR-020](#adr-020-factual-event-driven-trajectory-recording-and-prohibition-of-speculative-inference) | Factual Event-Driven Trajectory Recording & Prohibition of Speculation | Accepted | 2026-09-19 |
| [ADR-021](#adr-021-deterministic-feedback-routing-and-prohibition-of-generic-target-defaults) | Deterministic Feedback Routing & Prohibition of Generic Target Defaults | Accepted | 2026-09-19 |
| [ADR-022](#adr-022-idempotent-feedback-processing-and-event-deduplication-hygiene) | Idempotent Feedback Processing & Event Deduplication Hygiene | Accepted | 2026-09-19 |

---

## ADR-001: Antigravity Native Runtime as Sole Multi-Agent Orchestrator

### Context
Previous iterations explored custom Python wrappers and dispatcher scripts to emulate multi-agent communication loops, subagent queues, and turn coordination. This created a dual-runtime conflict with Google Antigravity's built-in execution engine, leading to tool desynchronization, unmonitored subagents, and violation of the native Antigravity lifecycle.

### Decision
Antigravity is declared the **sole agent runtime and multi-agent orchestrator** (Directive 12.1).
- All subagents must be invoked natively via Antigravity's `invoke_subagent` tool.
- Python scripts are classified strictly as "The Hands" (deterministic CLI tools executed via `run_command`).
- Developing or executing standalone Python agent emulators is strictly prohibited.

### Consequences
- **Positive**: Native UI visibility in Antigravity IDE, correct transcript logging, full lifecycle hook enforcement, zero duplicate event loops.
- **Negative**: Coordination logic cannot use bespoke Python multithreading; must rely on Antigravity subagent mechanisms.

---

## ADR-002: Elimination of `commandExecutionPolicy` from Agent Frontmatter

### Context
Historical templates included `commandExecutionPolicy: request-review` (or snake_case `command_execution_policy`) inside agent YAML frontmatter. Antigravity's agent loader uses a strict parser schema for Markdown agents. Unknown frontmatter fields cause the parser to drop the agent silently, hiding it from the IDE `/agents` dropdown and subagent registry.

### Decision
`commandExecutionPolicy` and all variant spellings are completely removed and barred from agent YAML frontmatter.
- Agent specifications contain only valid Antigravity frontmatter properties.
- Execution restrictions and shell safety are enforced via workspace permissions, native OS permissions, and `.agents/hooks.json`.

### Consequences
- **Positive**: 100% agent discoverability across all Antigravity surfaces.
- **Negative**: Frontmatter cannot declare per-agent execution policies; must rely on tool lists and lifecycle hooks.

---

## ADR-003: Subagent and MainAgent Discovery Semantics

### Context
In Antigravity, the agent loader uses two boolean flags in frontmatter:
- `mainAgent`: Controls whether the agent appears in the top-level chat / user persona picker.
- `subagent`: Controls whether the agent is mounted in the `invoke_subagent` tool registry.
Previously, Tier 1 and Tier 2 domain authorities (`methodology-expert`, `statistical-expert`, `academic-writer`, `evidence-auditor`, `final-judge`) were marked `mainAgent: true, subagent: false`. Consequently, when `academic-orchestrator` attempted to delegate tasks to these domain authorities, Antigravity blocked the call because they were excluded from the subagent registry.

### Decision
All specialist domain authorities that can be delegated to by the lead orchestrator must have `subagent: true`.
- Orchestrators and domain authorities can have `mainAgent: true, subagent: true` (dual-role: interactive chat or callable worker).
- Pure execution workers and critics have `mainAgent: false, subagent: true`.
- The `agent_integrity` validator strictly checks that any agent listed in another agent's `agents:` array has `subagent: true`.

### Consequences
- **Positive**: `academic-orchestrator` can seamlessly invoke all 22 domain agents and 6 learning subagents natively.
- **Negative**: Specialist authorities will appear in both the main agent picker and the subagents list.

---

## ADR-004: The Triad Artifact Invariant and One-Hypothesis-One-Stage

### Context
Monolithic LLM generation of academic chapters leads to severe hallucinations, loss of statistical precision, omission of negative results, and typography errors in complex Persian BiDi layouts.

### Decision
Under Directive 3, every micro-stage and individual hypothesis must produce a **synchronized physical triad of artifacts on disk**:
1. **`.json`**: Machine-readable statistics, parameters, and audit checklists.
2. **`.md`**: Scholarly narrative, APA 7 tables, and interpretations for instant inspection and diffing.
3. **`.docx`**: Institutional OpenXML document with strict typography (`B Nazanin` / `B Titr`), decoupled LTR numbers, and native Word OMML math.
Furthermore, under the One-Hypothesis-One-Stage invariant, each hypothesis has its own isolated micro-stage directory.

### Consequences
- **Positive**: Complete auditability, diffable outputs, zero mental statistical calculation, fail-closed validation.
- **Negative**: Higher disk space and multi-stage orchestration overhead.

---

## ADR-005: Multi-Layered Defense-in-Depth Security Architecture

### Context
Protecting raw empirical datasets from accidental mutation or tampering is an existential requirement in academic consulting. Frontmatter declarations alone cannot prevent tool misuse or malicious scripts.

### Decision
Security is implemented across four independent layers:
1. **Platform Layer**: Antigravity tool permissions and interactive confirmation gates.
2. **OS Layer**: `scripts/permission_manager.py` enforces POSIX `0444` (read-only) modes on raw input datasets.
3. **Hook Layer**: `.agents/hooks.json` intercepts `PreToolUse` to block destructive commands (`rm -rf`, `chmod`) and raw data writes, and `Stop` to enforce the Binary Honesty Protocol.
4. **Execution Layer**: Deterministic scripts check file existence and fail closed on unauthorized paths.

### Consequences
- **Positive**: Full tamper resistance, zero risk of raw data loss, cross-platform POSIX/Windows support.
- **Negative**: Development scripts must explicitly stage derived files in `02_clean_and_scored/` rather than modifying raw inputs.

---

## ADR-006: Hard Boundary Against Horizontal Growth & Architectural Sprawl

### Context
AcademicSuite has expanded to 28 agents, 44 skills, and 29 contracts. Unchecked proliferation of specialized agents and wrapper abstractions increases cognitive overhead, maintenance burden, and context fragmentation.

### Decision
A permanent freeze on horizontal growth is instituted:
> **No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**
- Any new component requires an Architectural Gap Justification filed in `architecture/CURRENT_ARCHITECTURE.md`.
- Default preference must be to refine existing deterministic scripts ("The Hands") or update existing skills rather than creating new agents or skills.

### Consequences
- **Positive**: Focused refinement, deep stability, predictable behavior, zero feature bloat.
- **Negative**: Developers cannot create ad-hoc experimental agents without formal justification.

---

## ADR-007: The Six-Part Functional Separation Invariant

### Context
Without strict structural boundaries, capabilities tend to leak across layers: agents attempt to calculate numbers or format XML tables in their heads, skills attempt to manage subagent orchestration or execute background processes, and scripts attempt to make autonomous research decisions. This causes hallucinations, non-deterministic bugs, and untraceable failures.

### Decision
A mandatory, constitutional Six-Part Functional Separation Invariant is enacted:
```text
Agent          ───> DECIDES: Reasoning role, delegation, context, decision-making, responsibility, communication
Skill          ───> INSTRUCTS: Domain knowledge, decision trees, execution instructions, reusable procedures
Script         ───> COMPUTES: Deterministic calculation, validation, transformation, file generation, hashing
Hook           ───> ENFORCES: Interception, safety, tamper-prevention, mechanical validation, honesty checks
State machine  ───> AUTHORIZES TRANSITION: Milestone progression, event timeline recording, state gating
Artifact manifest ─> DEFINES COMPLETION: Schema contracts, required deliverables, fail-closed affirmative evidence
```

### Consequences
- **Positive**: Clean context boundaries, complete auditability, fail-closed mechanical enforcement, zero mental arithmetic by LLMs.
- **Negative**: New workflows must explicitly map their operations across all six layers rather than embedding logic in a monolithic prompt.

---

## ADR-008: Dynamic Capability-Driven Orchestration vs. Static Linear Staging

### Context
Legacy orchestration in AcademicSuite relied on hardcoded sequential stage progression (`stage 1 → stage 2 → ... → statistics-agent`) and bloated static teams (often invoking or assuming all 22+ agents). Furthermore, Python script abstractions had occasionally attempted to manage agent lifecycles, violating the Sole Orchestrator Mandate (Directive 12.1).

### Decision
Rebuild orchestration strictly around deterministic **Capability Resolution** ("The Hands"):
```text
Task
 │
 ▼
Research Objective
 │
 ▼
Empirical Research Design (study_type, group_structure, temporal_dynamics, waves, factors)
 │
 ▼
Required Capabilities Matrix (design-methodology, longitudinal-analysis, assumption-checking, effect-size, post-hoc/comparison, statistical-execution, results-writing, audit)
 │
 ▼
Minimal Dynamically Assembled Native Antigravity Subagents (strictly pruning unneeded agents with documented rationale)
```

1. **Python Role**: Python routing (`academic_task_router.py`, `capability_resolver.py`) is strictly a deterministic capability resolver that identifies empirical design parameters, capability matrices, and required subagents. It never executes or emulates subagents.
2. **Antigravity Role**: The Antigravity Lead Agent (`academic-orchestrator`) is the sole conductor, natively invoking only the dynamically resolved subagents via `invoke_subagent`.
3. **Deterministic Pruning**: All 28 workspace agents are accounted for. Any unneeded agent is explicitly pruned with a documented rationale (e.g., pruning `psychometric-expert` for RCTs using validated scales; pruning `qualitative-analyst` for quantitative trials).

### Consequences
- **Positive**: Minimal agent context overhead, zero superfluous subagent invocations, clear scientific design derivation, 100% adherence to Directive 12.1 and Directive 19.
- **Negative**: Dynamic team resolution must be computed per task prompt prior to subagent invocation.

---

## ADR-009: Methodology as an Autonomous Decision Layer (MDR Contract)

### Context
In naive AI statistical workflows, agents often jump directly from user prompts to arbitrary statistical calculations, omitting critical design choices, estimand definitions, and assumption evaluations. When statistical executors select or alter models on the fly, analysis becomes non-defensible, prone to p-hacking, and vulnerable to classical statistical traps (such as gain-score t-tests falling into Lord's paradox, or median-split ANOVAs discarding 35-50% power).

### Decision
Establish an explicit, binding **Methodology Decision Layer** governed by an authoritative 8-step decision ladder:
```text
Research Question
       ↓
Design
       ↓
Estimand
       ↓
Candidate Methods
       ↓
Assumptions
       ↓
Method Selection & Refutation Matrix
       ↓
Execution Specification (Execution Contract)
       ↓
Statistical Executor ("The Hands")
```

1. **Autonomous Methodology Layer**: `methodology-expert` formulates and signs a binding **Methodology Decision Record (MDR)** conforming to `contracts/methodology_decision_record.schema.json`.
2. **Defensible Refutation Matrix**: Every MDR must evaluate candidate methods and provide formal, literature-grounded refutations for all non-selected methods (e.g., refuting gain-score t-tests via Lord's paradox; refuting Baron & Kenny and Sobel tests in favor of Hayes bootstrap 5,000).
3. **Execution Contract Decoupling**: The statistical executor (`statistics-agent` and `StatisticalPipelineEngine`) receives the `execution_contract` as a strictly downstream consumer. The executor is mechanically forbidden from inventing, selecting, or altering methodology (`MethodMismatchError` / `MethodologyViolationError`).

### Consequences
- **Positive**: Complete academic defensibility, zero arbitrary or unapproved model selection by executors, transparent refutation matrices, full compliance with Directive 12.1 and Directive 19.
- **Negative**: Adds an upfront requirement to formulate and validate the MDR before numerical execution proceeds.

---

## ADR-010: Hardened Deterministic Statistical Execution Layer & Contract

### Context
In academic consulting and statistical analysis, LLM cognitive systems are susceptible to arithmetic hallucinations, mental calculations of $t, F, p$, and effect sizes, and silent fallback to synthetic or mock datasets (`effect_size = 0.25`, `CI = [0.10, 0.40]`) when real empirical data is missing or difficult to parse. To maintain uncompromising scientific integrity, the statistical execution layer must become a strictly deterministic computational subsystem where LLMs are never permitted to compute or hallucinate numbers.

### Decision
Implement a hardened, deterministic statistical execution subsystem governed by:
1. **The 4-Tier Cognitive & Computational Boundary**:
   - **LLM (`statistical-expert` / `methodology-expert`)**: *What should be done?* (Methodological reasoning, estimand mapping, assumption planning, and authoring the binding Statistical Executor Contract).
   - **Python/R (`statistics-agent` / `StatisticalPipelineEngine`)**: *What are the actual numbers?* (Deterministic calculation on real curated data without LLM mental arithmetic).
   - **LLM (`academic-writer`)**: *What do verified numbers mean?* (Translating verified numerical results into substantive academic narrative and APA tables without modifying numbers).
   - **Validator (`statistical-auditor` / `validation-agent`)**: *Are those claims actually supported?* (Adversarially auditing narrative claims against output JSON, verifying degrees of freedom against sample size $N$, and calculating MSAI scores).
2. **The 7-Part Input Contract (`contracts/statistical_executor_contract.schema.json`)**:
   - `DATA`: File path, format, SHA-256 hash, data mode (`production`, `demo`, `test`, `simulation`), and `is_synthetic` boolean.
   - `VARIABLE MAP`: Explicit mappings for dependent, independent, covariates, moderators, mediators, cluster, and ID variables.
   - `DESIGN`: Design typology, between/within factors, and measurement timepoints.
   - `METHOD SPECIFICATION`: Statistical family, method name, computational engine, and model formula.
   - `ASSUMPTIONS`: Formal list of parametric assumptions to verify.
   - `PARAMETERS`: Confidence level (0.95), alpha (0.05), bootstrap resamples (5,000), random seed, and missing data strategy.
   - `OUTPUT CONTRACT`: Required output formats, table format, effect sizes, confidence intervals, and decimal precision.
3. **The 7-Part Output Contract (`contracts/statistical_execution_result.schema.json`)**:
   - `RESULT JSON`: Model name, sample size, primary test statistic, degrees of freedom, exact p-value, and execution status.
   - `TABLES`: Formatted APA 7th Edition markdown tables.
   - `DIAGNOSTICS`: Parametric assumption test statistics, p-values, and pass/fail indicators.
   - `EFFECT SIZES`: Standardized effect sizes ($\eta_p^2, d, R^2, \beta$).
   - `CONFIDENCE INTERVALS`: Parameter bounds and bootstrap BCa intervals.
   - `MODEL INFORMATION`: Convergence status, iteration count, and log-likelihood/AIC/BIC.
   - `PROVENANCE`: Input contract hash, data file hash, script path, execution timestamp, and environment details.
4. **Anti-Synthetic & Zero Default Sample Invariants**:
   - Zero synthetic statistics in production mode.
   - Zero default samples or mock fixtures in production mode.
   - Missing data or sample data in production immediately triggers fatal fail-closed errors (`MissingProductionDataError`, `ProductionSampleFallbackBlockedError`).
   - Synthetic benchmarks and simulations must explicitly declare `is_synthetic: true` and `data_mode: "simulation"` or `"test"`.

### Consequences
- **Positive**: 100% arithmetic reproducibility, zero hallucinated statistical numbers, complete cryptographic audit trails, fail-closed enforcement preventing uncurated or mock data from leaking into production deliverables.
- **Negative**: Requires strict data curation and schema validation before any statistical computation can be executed.

---

## ADR-011: Complete Elimination of Synthetic Data Escape Routes and Universal Fail-Closed Policy

### Context
In prior implementations of AcademicSuite, certain pipeline tools, presentation generators, intervention compilers, and dual-loop self-improvement engines retained legacy fallback paths. When empirical payloads or physical artifacts on disk were omitted, these tools silently fell back to bundled sample fixtures (e.g. `examples/sample_defense_payload.json`, built-in ACT intervention presets, or synthetic experiences with `duration_seconds: 1.0` and fallback stats `effect_size: 0.25`). This created severe latent risks of synthetic data or unverified figures leaking into production academic chapters, slides, or intervention manuals.

### Decision
Enact a complete, repository-wide elimination of all silent synthetic data escape routes and enforce an uncompromising universal fail-closed policy:
1. **Four-Tier Architectural Classification**:
   - `TEST FIXTURE`: Unit/integration test data isolated exclusively within `tests/` and test runners.
   - `DEMO`: Educational demonstrations requiring explicit `--mode demo` flag.
   - `SIMULATION`: Explicit Monte Carlo psychometric simulations requiring explicit `--mode simulation` or `is_synthetic = True`.
   - `PRODUCTION`: Live academic consulting requiring real, physically verified empirical data on disk.
2. **Universal Fail-Closed Invariant in Production Mode (`missing empirical input → BLOCKED`)**:
   - **Persian Defense Presentation Builder (`main.py`)**: Added `--mode {production, demo, test, simulation}`. In production mode, missing input JSON or any pointer to sample fixtures (`sample_*.json`, `/examples/`) immediately prints `CRITICAL SAFETY VIOLATION` and exits with code 1 (`BLOCKED`).
   - **Intervention Protocol Compiler (`compile_intervention_protocol.py`)**: Added `--mode` parameter. In production mode, omitting `--json` or pointing to sample/preset files strictly raises `MissingProductionDataError` or `ProductionSampleFallbackBlockedError`.
   - **Academic Dual Loop Engine (`academic_dual_loop_engine.py`)**: In production mode (`mode="production"`), fast loop requires an existing empirical `existing_experience_id` and verified physical `artifacts`; slow loop requires an empirical `candidate_payload`. Synthetic mock experience synthesis (`fast_loop_project`, `duration_seconds: 1.0`, `effect_size: 0.25`) is strictly BLOCKED.
   - **Universal Script Execution Guard (`script_execution_guard.py`)**: Added `"simulation"` mode. Added `is_synthetic: bool = False`. Production mode strictly blocks any explicit `is_synthetic=True`, sample/demo paths, or JSON payloads internally tagged with `"is_synthetic": True`.
   - **Master Academic Orchestrator (`orchestrator_cli.py`)**: Added `"simulation"` mode. In production mode, purges all `default_sample` pointers and inspects input payloads for internal synthetic flags, raising `ProductionSampleFallbackBlockedError`.
3. **Explicit Simulation Invariant**:
   - If simulation or demo data is desired, `mode = "simulation"` or `mode = "demo"` must be explicit in CLI arguments or method parameters, and generated payloads must be tagged with `"is_synthetic": True` and `"data_mode": "simulation"`.

### Consequences
- **Positive**: 100% elimination of silent fallbacks, zero accidental leakage of synthetic data into academic deliverables, complete enforcement of Directive 0, Directive 2, and Directive 13.
- **Negative**: CLI commands and orchestrator scripts require explicit input payloads or explicit `--mode demo` / `--mode simulation` flags.

---

## ADR-012: Formal State Machine Engine and Elimination of Direct Stage Mutations

### Context
In earlier iterations of AcademicSuite, stage advancement was primarily tracked via ad-hoc functions like `set_stage(project_path, stage)` that directly mutated the `current_stage` string in `project.json`. This allowed callers to bypass prerequisite checks, skip intermediate stages, advance without physical artifacts on disk, and omit human approval gates. To guarantee research integrity, state progression must be governed by a mathematically rigorous state machine with legal states, legal directed transitions, and mandatory prerequisite, artifact, and authorization validation gates.

### Decision
Replace ad-hoc stage mutation with a formal, deterministic state machine implemented in `scripts/academic_state_manager.py` (`StrictStateMachine` and `request_transition()`):

1. **Legal States Codification**:
   - **Project States**:
     - `PROJECT_CREATED`: Project initialized with study parameters and research questions.
     - `PROJECT_APPROVED`: All mandatory stages approved with granted release approval.
     - `PROJECT_REJECTED`: Project formally terminated or rejected by defense committee.
   - **Stage States**:
     - `STAGE_LOCKED`: Stage is locked awaiting completion of upstream prerequisite stages.
     - `STAGE_READY`: All prerequisites approved and required input artifacts exist on disk.
     - `STAGE_RUNNING`: Stage execution actively underway by designated subagent/script.
     - `STAGE_VALIDATING`: Deterministic computation finished; adversarial quality checks running.
     - `STAGE_AWAITING_APPROVAL`: Passing validation report on disk; awaiting human/gate approval.
     - `STAGE_APPROVED`: Formal human approval granted and passing validation report verified.
     - `STAGE_REJECTED`: Reviewer rejected stage output; requires revision and retry.
     - `STAGE_FAILED`: Execution crashed, exception encountered, or validation failed.
     - `STAGE_BLOCKED`: Fatal external dependency or prerequisite defect blocking execution.

2. **Legal Directed Transitions (Fail-Closed Graph)**:
   - `STAGE_LOCKED` $\rightarrow$ `{STAGE_READY, STAGE_BLOCKED}`
   - `STAGE_READY` $\rightarrow$ `{STAGE_RUNNING, STAGE_BLOCKED}`
   - `STAGE_RUNNING` $\rightarrow$ `{STAGE_VALIDATING, STAGE_FAILED, STAGE_BLOCKED}`
   - `STAGE_VALIDATING` $\rightarrow$ `{STAGE_AWAITING_APPROVAL, STAGE_FAILED, STAGE_BLOCKED}`
   - `STAGE_AWAITING_APPROVAL` $\rightarrow$ `{STAGE_APPROVED, STAGE_REJECTED}`
   - `STAGE_APPROVED` $\rightarrow$ `{STAGE_RUNNING}` (explicit re-execution / iteration)
   - `STAGE_REJECTED` $\rightarrow$ `{STAGE_READY, STAGE_LOCKED}`
   - `STAGE_FAILED` $\rightarrow$ `{STAGE_READY, STAGE_BLOCKED}`
   - `STAGE_BLOCKED` $\rightarrow$ `{STAGE_READY, STAGE_LOCKED}`
   - `PROJECT_CREATED` $\rightarrow$ `{PROJECT_APPROVED, PROJECT_REJECTED}`
   - *Everything else*: strictly raises `InvalidStateTransitionError`.

3. **The 6-Step `request_transition()` Pipeline**:
   - Step 1: **Validate Transition**: Check source $\rightarrow$ target against legal directed graph.
   - Step 2: **Validate Prerequisites**: Check that all upstream stages are `STAGE_APPROVED`.
   - Step 3: **Validate Artifacts**: Check that required input artifacts (for `READY`/`RUNNING`) and required output artifacts (for `VALIDATING`/`AWAITING_APPROVAL`/`APPROVED`) physically exist on disk with positive byte size.
   - Step 4: **Validate Authorization**: For `STAGE_APPROVED` or `PROJECT_APPROVED`, verify an explicit granted approval record exists with `is_approved == True` and verify a passing validation report (`overall_verdict: PASS`).
   - Step 5: **Commit Transition**: Atomically persist stage status and history in `current_state.json` and sync `project.json`. If a stage becomes `STAGE_APPROVED`, automatically unlock downstream stages whose prerequisites are fully satisfied (`STAGE_LOCKED` $\rightarrow$ `STAGE_READY`).
   - Step 6: **Emit Event**: Emit durable, schema-validated event to `events.jsonl` via `AcademicEventEngine`.

4. **Complete Elimination of Direct `set_stage` Mutations in Production**:
   - Direct calling of `set_stage()` in `production` mode strictly raises `DirectStageMutationBlockedError`.
   - All state progression must occur through `request_transition()` or the CLI subcommand `request-transition`.

### Consequences
- **Positive**: Complete elimination of skipped stages, zero unverified state mutations, rigorous artifact and prerequisite gating, full compliance with Directive 3, Directive 11, and Directive 19.
- **Negative**: Requires formal transition requests and prerequisite satisfaction before advancing between stages.

---

## ADR-013: Authoritative Stage Manifests and Cross-Artifact Agreement Gating

### Context
In earlier iterations of AcademicSuite, pipeline stages often decided completion simply because a single expected output file was detected on disk (e.g. "found a JSON file"). This loose heuristic failed to verify:
1. Whether all declared deliverables—specifically the Triad Invariant (`.docx`, `.md`, `.json`)—were completely generated and non-empty.
2. Whether deliverables had been tampered with or modified after generation.
3. Whether numbers reported in human-readable Markdown or institutional Word documents contradicted the underlying statistical JSON data.
4. Whether the outputs were genuinely produced from the declared empirical dataset rather than cached or mock inputs.
5. Whether upstream dependency milestones had been cryptographically validated before downstream execution commenced.

### Decision
Implement the **Authoritative Stage Manifest Subsystem** governed by `contracts/stage_manifest.schema.json` and executed by `scripts/stage_manifest_engine.py`:
1. **Authoritative Manifest Requirement (`manifest.json`)**:
   Every meaningful academic stage must produce and maintain a schema-validated `manifest.json` on disk. The system strictly forbids deciding that a stage is complete merely because an individual output file was located.
2. **Mandatory Manifest Contract Contents**:
   - `stage_id` & `project_id`: Unique micro-stage and study identifiers.
   - `producer`: Designated cognitive agent, computational script, and exact command invoked.
   - `inputs`: Declared input files with SHA-256 cryptographic hashes at consumption time.
   - `required_artifacts`: Declared deliverables, strictly enforcing the Triad Invariant (`stats_json`, `narrative_markdown`, `openxml_word`) for findings and hypothesis stages.
   - `dependencies`: Upstream prerequisite stages with manifest paths and SHA-256 hashes.
   - `hashes`: Table of SHA-256 cryptographic hashes for every produced artifact on disk.
   - `validation_requirements`: Required validator script, expected verdict (`PASS`), and cross-agreement flag.
   - `status`: Lifecycle status (`IN_PROGRESS`, `GENERATED`, `VALIDATED`, `APPROVED`, `REJECTED`, `FAILED`).
   - `timestamps`: `created_at`, `completed_at`, `validated_at`, `approved_at`.
   - `cross_agreement`: Embedded audit verification proving concordance across formats.
3. **Fail-Closed Cross-Artifact Agreement Invariant**:
   For any stage producing statistical findings, `scripts/stage_manifest_engine.py` calls `validators/result_consistency/validator.py` to audit numerical parameters ($N, F, t, p, \beta, B, z, R^2, \eta_p^2$, fit indices) across `.json`, `.md`, and `.docx`. Any contradiction immediately fails closed with `ManifestCrossAgreementError`.
4. **State Machine Transition Gating**:
   In `StrictStateMachine.request_transition()`, transitioning a stage to `STAGE_VALIDATING`, `STAGE_AWAITING_APPROVAL`, or `STAGE_APPROVED` strictly discovers and validates `manifest.json`. Any missing manifest, missing file, hash mismatch, or numerical discrepancy raises a fail-closed exception (`MissingStageManifestError`, `ManifestArtifactMissingError`, `ManifestHashMismatchError`, `ManifestInputMismatchError`, `ManifestTriadMissingError`, `ManifestDependencyMismatchError`, `ManifestCrossAgreementError`).
5. **Atomic Lifecycle Update**:
   Upon transition to `STAGE_APPROVED`, `StrictStateMachine` updates `manifest.json` status to `APPROVED` and records `timestamps.approved_at`.

### Consequences
---

## ADR-014: Fail-Closed Validation Architecture and Sequential Gate Cascade

### Context
In earlier iterations of validation systems, sub-validators and test suites operated under a permissive "PASS unless something fails" default philosophy. Under that paradigm:
1. Passing an empty dictionary (`{}`) or a file with zero statistical parameters resulted in a silent `PASS`.
2. A missing stage manifest was treated as a benign omission or skipped entirely.
3. Verdicts were binary (`PASS` or `FAIL`), obscuring whether a check was unverified, blocked by missing prerequisites, or explicitly failed.
4. Upstream dependency manifests were not sequentially chained into the validation gate.

For high-stakes graduate thesis defense deliverables (Chapters 4 and 5), unverified or empty artifacts must never silently pass.

### Decision
Rebuild the AcademicSuite validation engine (`validators/run_all_validators.py`, `validators/numerical_consistency/`, `validators/reporting_consistency/`, `validators/result_consistency/`, and `contracts/validation_report.schema.json`) around a strict fail-closed architecture:

1. **Constitutional Validator Philosophy**:
   Shift from *"PASS unless something fails"* to **"UNVERIFIED unless every required condition passes"**.
2. **4-Tier Verdict Taxonomy**:
   - `UNKNOWN` / `UNVERIFIED`: Initial state or check that was skipped, incomplete, or lacks affirmative empirical evidence ($\text{evidence} = 0$).
   - `BLOCKED`: Missing prerequisite, missing input dataset, missing manifest, or missing required physical deliverable on disk.
   - `FAIL`: Explicit schema violation, cryptographic hash mismatch, corrupted payload, out-of-bound statistic, cliché detection, prohibited $p = .000$, Persian leading zero omission, or numerical contradiction across formats.
   - `PASS`: Affirmative success awarded **only** when every sequential gate has executed and verified with concrete empirical evidence ($\text{total\_evidence} \ge 1$ and $\text{checks\_failed} = 0, \text{checks\_blocked} = 0$).
3. **The 6-Gate Sequential Cascade**:
   - **Gate 0: Manifest Existence Check**: Check `manifest.json` on disk. If missing under `--require-manifest`: immediately return `UNVERIFIED`.
   - **Gate 1: Manifest Schema Validation**: Validate `manifest.json` against `contracts/stage_manifest.schema.json`. Schema error returns `FAIL`.
   - **Gate 2: Artifact Existence, Non-Empty, Hashes & Triad Invariant**:
     - Verify declared required deliverables exist on disk (missing $\rightarrow$ `BLOCKED`).
     - Verify files are non-empty ($0\text{ bytes} \rightarrow \text{FAIL}$).
     - Verify SHA-256 cryptographic hashes against manifest (mismatch $\rightarrow$ `FAIL`).
     - Verify Triad Invariant for findings/hypothesis stages (`.docx`, `.md`, `.json` present).
   - **Gate 3: Numerical Consistency Execution**:
     - Audit statistical parameters ($N, \text{df}, F, t, p, \beta, R^2, \text{fit indices}$).
     - Zero numbers audited $\rightarrow$ `UNKNOWN` (never silent PASS).
     - Out-of-bounds or prohibited values $\rightarrow$ `FAIL`.
   - **Gate 4: Narrative & Cross-Artifact Concordance Execution**:
     - Audit Markdown reporting consistency (no clichés, no $p=.000$, Persian leading zero preserved).
     - Audit numerical agreement across `.json`, `.md`, and `.docx` (discrepancy $\rightarrow$ `FAIL`).
   - **Gate 5: Upstream Dependency Verification**:
     - Verify upstream dependency manifests exist on disk (missing $\rightarrow$ `BLOCKED`).
     - Verify upstream manifest SHA-256 hashes match declared hash (tampering $\rightarrow$ `FAIL`).
   - **Gate 6: Composite Fail-Closed Verdict Resolution**:
     - If $\text{blocked} > 0 \rightarrow \text{BLOCKED}$.
     - Else if $\text{failed} > 0 \rightarrow \text{FAIL}$.
     - Else if $\text{unverified} > 0 \text{ or } \text{unknown} > 0 \text{ or } \text{evidence} = 0 \text{ or } \text{passed} = 0 \rightarrow \text{UNVERIFIED}$.
     - Else if $\text{passed} = \text{total} \text{ and } \text{evidence} \ge 1 \rightarrow \text{PASS}$.

### Consequences
- **Positive**: Complete structural impossibility of empty or unverified payloads achieving `PASS`, 100% fail-closed gate sequence, strict compliance with Directive 0, Directive 3, and Directive 19.
- **Negative**: All pipeline deliverables must carry affirmative empirical evidence and satisfy all 6 sequential gates.

---

## ADR-015: Cross-Artifact Triad Consistency Validation & Structured DOCX Compilation

### Context
In academic deliverables (Chapters 4 and 5), the system produces a synchronized Triad of artifacts: machine-readable JSON (`result.json`), Markdown narrative (`result.md`), and Word document (`result.docx`).
In previous systems:
1. Numerical tolerances were excessively loose ($\Delta \le 0.05$), allowing contradictory parameters (such as $\beta = .39$ vs $\beta = .42$) to pass unnoticed.
2. Tables were checked only superficially without verifying cell-by-cell concordance against machine-readable sources ($n$, $\text{mean}$, $SD$, $p$, effect size, confidence interval $[LL, UL]$).
3. The Word `.docx` file was vulnerable to independent manual drafting drift, where numbers in Word diverged from the JSON computational ground truth.

### Decision
Implement strict 3-way cross-artifact consistency validation and deterministic structured DOCX compilation:

1. **Strict 3-Way Parameter Concordance**:
   - Every statistical parameter ($\beta, t, F, z, N, R^2, \text{effect\_size}, CI$) extracted from `result.json` is reconciled across `result.md` and `result.docx`.
   - Tolerance tightened to strict numerical identity ($|\Delta| \le 0.01$, with $|\Delta| \le 0.015$ ceiling for decimal rounding).
   - If `result.json` specifies $\beta = .42$, but `result.md` reports $\beta = .37$ and `result.docx` reports $\beta = .39$, the system automatically fails closed and rejects the stage (`FAIL`).
2. **Deep Table-Level Concordance (`audit_table_concordance`)**:
   - Table cells in Markdown and DOCX tables (e.g. Table 4.3) are parsed and cross-checked against JSON `table_data` and parameters:
     - Sample size ($n$ or $N$)
     - Mean ($M$)
     - Standard deviation ($SD$)
     - Significance level ($p$)
     - Effect size ($d, \eta_p^2, \text{partial } \eta^2$)
     - Confidence interval ($[LL, UL]$)
   - Contradictions in any cell trigger an explicit `FAIL` verdict.
3. **Deterministic DOCX Compilation (`scripts/structured_docx_generator.py`)**:
   - DOCX files must never be independently authored with manually typed numbers.
   - `structured_docx_generator.py` compiles Word documents directly from verified structured JSON data and narrative Markdown.
   - Embeds native APA 7 3-line tables (`<w:bidiVisual/>`), Persian typography (`B Titr` 14pt, `B Nazanin` 13pt), and decoupled LTR numbers (`Times New Roman`).
4. **Authoritative Manifest Chaining**:
   - `scripts/stage_manifest_engine.py` calls `validate_cross_artifacts()` during manifest generation and raises `ManifestCrossAgreementError` on any cross-artifact discrepancy.

### Consequences
- **Positive**: Complete elimination of cross-format numerical drift, 100% table-level mathematical accuracy, deterministic and reproducible DOCX generation.
- **Negative**: Markdown and DOCX text cannot use approximate numbers differing from the exact JSON calculations.

---

## ADR-016: Separation of Interpretation from Evidence and 5-Link Claim Provenance

### Context
In empirical research (graduate theses, journal manuscripts, discussion chapters, abstracts, conclusions), authors make substantive scientific claims:
- *"Acceptance and Commitment Therapy produces a clinically meaningful reduction in occupational burnout among ICU nurses."*
- *"Psychological flexibility fully mediates the relationship between perfectionism and test anxiety."*

Historically:
1. No formal boundary existed between raw statistical execution outputs, verified results, scholarly interpretations, and substantive scientific claims.
2. Scientific assertions could quietly drift into broader generalizations than the empirical data supported.
3. Claims could cite phantom or modified statistics without detection if no explicit provenance chain tied the claim back to the raw dataset and analysis script.

### Decision
Implement an explicit 4-tier evidence layer and enforce an unbroken 5-link provenance relationship for every substantive claim:

1. **The 4-Tier Evidence Hierarchy**:
   $$\text{Tier 1: Raw Statistical Output} \longrightarrow \text{Tier 2: Verified Result} \longrightarrow \text{Tier 3: Interpretation} \longrightarrow \text{Tier 4: Claim}$$
   - **Tier 1 (Raw Statistical Output)**: Unfiltered computational matrices, ANOVA tables, bootstrap distributions, log files (`raw_output.json`).
   - **Tier 2 (Verified Result)**: Audited parameters in `result.json` with verified degrees of freedom, admissible bounds, and APA 7 precision.
   - **Tier 3 (Interpretation)**: Contextualized scholarly statements linking verified numbers to directional hypotheses (`result.md`).
   - **Tier 4 (Claim)**: Substantive scientific assertions situated in thesis results, discussion, abstracts, conclusions, or journal manuscripts.

2. **The 5-Link Provenance Relationship**:
   $$\text{claim} \longrightarrow \text{artifact} \longrightarrow \text{statistic} \longrightarrow \text{analysis} \longrightarrow \text{data}$$
   Every substantive claim must declare:
   - **Link 1 (Claim)**: `claim_id`, `statement`, `claim_type`, `target_scope`, `interpretation`.
   - **Link 2 (Artifact)**: Deliverable path, cryptographic SHA-256 hash, format, and section location.
   - **Link 3 (Statistic)**: Parameter key, metric values ($F, t, \beta, p, \eta_p^2, CI$), and `result.json` hash.
   - **Link 4 (Analysis)**: Analysis ID, method name, model formula, script path, script hash, execution timestamp, and raw output hash.
   - **Link 5 (Data)**: Dataset path, dataset SHA-256 hash, sample size ($N$), and filtering query.

3. **Fail-Closed Provenance Enforcement**:
   - `scripts/evidence_provenance_engine.py` provides deterministic `build`, `verify`, and `trace` operations.
   - `validators/provenance_validator.py` enforces fail-closed validation on all 5 links.
   - **Orphan Claim Detection**: Any substantive scientific claim appearing in narrative deliverables (`.md`, `.docx`) that lacks registered provenance in `claim_provenance.json` immediately triggers `FAIL` and rejects the stage.

### Consequences
- **Positive**: 100% auditable provenance trace from high-level scientific claims down to raw empirical data bytes; complete elimination of phantom claims and ungrounded generalizations; seamless Viva Voce cross-examination defence.
- **Negative**: Substantive claims in thesis chapters and papers must be formally declared and linked in `claim_provenance.json`.

---

## ADR-017: Separated Writing Architecture and Interpretation Contracts

### Context
In academic theses and empirical journal writing, LLMs acting as writers often attempt to re-compute, round, or alter statistical parameters in their heads—effectively acting as an ad-hoc "second statistician." This behavior causes numerical drift ($\beta = .42$ becoming $.37$ or $.39$), over-generalization, and unauthorized modification of statistical truth.

### Decision
Rework the writing architecture around strict separation of statistical truth and academic rhetoric:
$$\text{Verified Result Artifacts} \longrightarrow \text{Interpretation Contract} \longrightarrow \text{Writing Agent} \longrightarrow \text{Draft} \longrightarrow \text{Writing QC} \longrightarrow \text{Statistical Claim QC} \longrightarrow \text{Final Document}$$

1. **The Invariant: The Writer Never Becomes a Second Statistician**:
   - The writing agent (`academic-writer`) is strictly prohibited from calculating, approximating, or altering numbers.
   - The writer must ingest `interpretation_contract.json` prior to drafting and embed contracted statistical parameters verbatim.
2. **Authoritative Interpretation Contract (`contracts/interpretation_contract.schema.json`)**:
   - Defines exact statistical facts, APA 7 table structures, hypothesis verdicts (`SUPPORTED` / `REJECTED`), mandated phrases, and forbidden claims.
   - For Chapter 4: $\text{statistical result} \to \text{table} \to \text{interpretation} \to \text{paragraph}$ (with strict prohibition against external literature or theory deep-dives).
   - For Chapter 5: $\text{verified finding} \to \text{theoretical interpretation} \to \text{literature comparison} \to \text{limitations} \to \text{implications}$.
3. **Two-Stage QC Pipeline**:
   - **Stage 1 (Writing QC)**: Audits academic tone, eliminates AI clichés («شایان ذکر است که»), enforces the Persian leading zero standard (`۰.۰۵`), and checks cadence variability ($CV \ge 0.40$).
   - **Stage 2 (Statistical Claim QC)**: Audits exact numerical identity ($|\Delta| \le 0.01$), table concordance, and 5-link claim provenance.
4. **Deterministic Document Assembly**:
   - Generates the immutable Triad deliverable: `.docx` (via `structured_docx_generator.py`), `.md`, and `.json`.

### Consequences
- **Positive**: Complete prevention of numerical drift in narrative text; strict compliance with Directive 0, Directive 2, and Directive 4; reproducible, defense-ready chapter drafts.
- **Negative**: Narrative drafting requires prior generation of `interpretation_contract.json`.

---

## ADR-018: Formal Human Approval State and Cryptographic Approval Contracts

### Context
In prior systems, human-in-the-loop verification relied primarily on conversational prompt instructions (e.g., *"HALT and wait for user"*). This approach suffered from several fundamental defects:
1. **Fragile Prompt Dependency**: Autonomous agents or batch execution loops could easily overlook or rationalise past prompt instructions, leading to unapproved multi-stage runaways.
2. **Lack of Cryptographic Accountability**: An agent claiming "user approved" possessed no tamper-evident proof that the user actually inspected and authorized the exact files on disk.
3. **Absence of Reified State**: Approval existed only as conversational memory rather than an immutable, auditable state machine phase. Downstream stages could not deterministically query whether upstream stages had received formal sign-off.

### Decision
Rebuild human approval as an authoritative physical state backed by cryptographic contracts and deterministic state machine transitions:

$$\text{STAGE\_VALIDATING} \longrightarrow \text{STAGE\_AWAITING\_APPROVAL} \xrightarrow[\text{Explicit Human Approval}]{\text{approval event}} \text{STAGE\_APPROVED} \longrightarrow \text{Next Stage Unlocked (STAGE\_READY)}$$

1. **Approval as an Authoritative Physical State (`STAGE_AWAITING_APPROVAL`)**:
   - Approval is no longer a prompt suggestion; it is a first-class state in `StrictStateMachine` / `AcademicStateManager`.
   - Transition to `STAGE_AWAITING_APPROVAL` requires a verified passing validation report (`validation_report.json` with `overall_verdict: "PASS"`).
2. **Authoritative Approval Record Contract (`contracts/approval_record.schema.json`)**:
   - Every approval request instantiates an immutable record:
     - `approval_id`: Unique identifier (e.g., `APP-06_hypothesis_1-20260919120000`).
     - `stage_id`: Unique identifier of the stage awaiting approval.
     - `artifact_hash`: Cryptographic SHA-256 hash of the stage manifest or primary deliverable on disk.
     - `validation_hash`: Cryptographic SHA-256 hash of the passing validation report (`validation_report.json`).
     - `requested_at`: ISO 8601 UTC timestamp.
     - `approved_by`: Identity of the approving authority (e.g., `saber_admin`, `124911145`).
     - `approved_at`: ISO 8601 UTC timestamp of the decision.
     - `decision`: Authoritative enum (`PENDING` | `APPROVED` | `REJECTED`).
     - `status`: Lifecycle status (`PENDING` | `GRANTED` | `REJECTED`).
     - `is_approved`: Boolean flag, strictly `false` by default, set to `true` only upon explicit grant.
3. **Cryptographic Tamper Protection (`ApprovalTamperError`)**:
   - At approval execution, `scripts/academic_approval_engine.py` re-computes SHA-256 hashes of the deliverable and validation report on disk.
   - If either file has mutated since the approval was requested, approval is rejected with `ApprovalTamperError`.
4. **Mechanical Downstream Gating & Auto-Unlocking**:
   - Dependent downstream stages remain in `STAGE_LOCKED` while the prerequisite is in `STAGE_AWAITING_APPROVAL`.
   - Upon successful execution of `approve_stage`, the state machine transitions the stage to `STAGE_APPROVED`, emits `MILESTONE_APPROVED`, and automatically unlocks downstream dependent stages (`STAGE_LOCKED -> STAGE_READY`).
5. **Deterministic Approval Engine (`scripts/academic_approval_engine.py`)**:
   - CLI commands: `request`, `approve`, `reject`, and `status`.

### Consequences
- **Positive**: 100% elimination of prompt-based halting vulnerabilities; cryptographic proof of human authorization; mechanical prevention of unapproved stage advancement; tamper-evident audit trail conforming to Directive 11 and Directive 19.
- **Negative**: Stages requiring human gates must explicitly transition through `STAGE_AWAITING_APPROVAL` and receive an approval command before downstream stages unlock.

---

## ADR-019: Tripartite Lifecycle Hook Architecture (Safety, Integrity, Learning) and Non-Orchestrator Invariant

### Context
In earlier iterations, lifecycle governance was implemented via a monolithic guard script (`transcript_and_rule_guard.py`) that intermingled distinct concerns: file mutation safety, system security, artifact checking, validation execution, continuous learning, and multi-agent truthfulness auditing. Over time, hooks began encroaching on workflow coordination (e.g., inspecting stage dependencies and checking for multi-step chapter assembly in PreToolUse), risking architectural drift where hooks acted as a de facto orchestrator.

### Decision
Divide all Antigravity lifecycle hooks into three distinct, specialized classes and strictly enforce the **Hook Non-Orchestrator Invariant**:

1. **The Three Hook Classes**:
   - **Class A: Safety Hooks (`.agents/hooks/safety_hooks.py`)**:
     - *Raw-Data Protection*: Blocks file mutation tools (`write_to_file`, `replace_file_content`, etc.) and destructive shell commands (`rm`, `mv`, `>`, `sed -i`) targeting raw datasets (`/raw/`, `01_raw_inputs/`, `data_raw.*`).
     - *Dangerous Command Protection*: Intercepts and denies destructive bash operations (`rm -rf .agents`, `rm -rf .git`, `rm -rf /`, fork bombs).
     - *Outside-Workspace Protection*: Enforces confinement within declared workspace roots, mandates English-only ASCII filenames (Directive 6), and blocks unauthorized worker delegation and excessive subagent nesting depth ($\ge 3$).
   - **Class B: Integrity Hooks (`.agents/hooks/integrity_hooks.py`)**:
     - *Artifact Verification*: Enforces the Triad Artifact Invariant (.docx + .md + .json) across stage deliverables and audits skill modularity ceilings (Directive 18: max 500 lines, 40,000 bytes).
     - *State Consistency*: Guarantees that stage deliverables possess valid state records and authoritative manifests without unapproved mutations.
     - *Manifest Verification*: Confirms that completed stages possess an authoritative `manifest.json` on disk matching declared physical files.
     - *Post-Analysis Validation & Honesty Gate*: Verifies that completed stages evaluate to `PASS` in validation reports, and enforces Directive 0 (Binary Honesty Protocol & Multi-Agent Truthfulness) on conversation transcripts.
   - **Class C: Learning Hooks (`.agents/hooks/learning_hooks.py`)**:
     - *Capture User Correction*: Automatically scans user prompts in `PreInvocation` and `Stop` for critique and guidance, recording feedback via `AcademicCorrectionDetector` and `AcademicIntegratedLearningHub`.
     - *Capture Validation Failure*: Intercepts validation failures and records causal incidents in `state/pitfalls.jsonl` and experience logs.
     - *Capture Agent Trajectory*: Logs tool execution events and sanitized parameters in `state/audit_log.jsonl` during `PostToolUse`.

2. **The Hook Non-Orchestrator Invariant**:
   - Hooks strictly execute synchronous interception, constraint enforcement, diagnostic logging, and post-turn integrity audits.
   - Hooks are **strictly prohibited from acting as an academic orchestrator**:
     - Hooks must **never** mutate state machine milestone progression.
     - Hooks must **never** select, dispatch, or sequence subagents.
     - Hooks must **never** draft, synthesize, or re-write academic narrative deliverables.
   - Orchestration is the sole responsibility of the Antigravity Lead Agent (`academic-orchestrator`), supported by deterministic skill engines ("The Hands").

3. **Unified Dispatcher & Backward-Compatible Facade**:
   - `.agents/hooks/hook_dispatcher.py` routes incoming Antigravity events (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`) strictly to Class A, B, and C modules.
   - `.agents/verification/transcript_and_rule_guard.py` is maintained as a thin facade delegating to the tripartite classes, preserving 100% backward compatibility with existing tests.

### Consequences
- **Positive**: Clean separation of concerns conforming to Directive 19; eliminate monolithic sprawl; prevent hook overreach into workflow orchestration; maintain robust safety, cryptographic integrity, and automated learning capture.
- **Negative**: Hook modifications require editing class-specific modules (`safety_hooks.py`, `integrity_hooks.py`, `learning_hooks.py`) rather than a single script.

---

## ADR-020: Factual Event-Driven Trajectory Recording and Prohibition of Speculative Inference

### Status
Accepted

### Context
In earlier iterations of `AcademicExperienceRecorder`, trajectory records were partially synthesized through speculative inference:
- If a milestone transitioned or existed in state `RUNNING` or `APPROVED`, the engine inferred that a CLI tool `run_command` was called and invented a mock execution with dummy parameters (`duration_ms = 1000`, mock script paths).
- If a stage directory contained artifacts, `ordered_actions` was populated with hypothetical `SKILL_INVOCATION` and `ARTIFACT_GENERATION` steps even if no tool call was physically observed.

This speculative inference violated Directive 0 (Radical Honesty & Anti-Deception) and degraded the epistemic value of trajectory data for continuous learning. Furthermore, Antigravity lifecycle hook payloads already provide rich, observable execution metadata (`conversationId`, `workspacePaths`, `transcriptPath`, `toolCall`, `stepIdx`, `artifactDirectoryPath`, `modelName`), which serves as an authoritative source of truth.

### Decision
1. **Canonical 11 Observable Events**:
   Trajectory capture is strictly governed by 11 discrete, observable physical events:
   - `TOOL_CALLED`: Tool invocation proposed or intercepted (`PreToolUse`).
   - `TOOL_RETURNED`: Tool execution completed (`PostToolUse`).
   - `FILE_READ`: File inspection tool executed (`view_file`, `read_resource`, `read_url_content`).
   - `FILE_WRITTEN`: File creation or modification tool executed (`write_to_file`, `replace_file_content`, `apply_diff`).
   - `COMMAND_STARTED`: CLI process initiated (`run_command`).
   - `COMMAND_FINISHED`: CLI process terminated with exit code (`run_command`).
   - `AGENT_INVOKED`: Subagent delegation initiated (`invoke_subagent`).
   - `AGENT_RETURNED`: Subagent completed turn.
   - `VALIDATION_STARTED`: Validator or check suite initiated.
   - `VALIDATION_FAILED`: Validator check failed with explicit error or non-zero exit code.
   - `USER_CORRECTION`: Human critique, correction, or revision directive detected.

2. **Antigravity Hook Metadata as Source of Truth**:
   Every event record must extract and preserve the factual execution metadata from Antigravity hooks:
   - `conversationId`
   - `workspacePaths`
   - `transcriptPath`
   - `toolCall` (name and sanitized arguments)
   - `stepIdx`
   - `artifactDirectoryPath`
   - `modelName`

3. **Strict Prohibition of Speculative Fabrication**:
   - `AcademicExperienceRecorder` and `TrajectoryEngine` must **never fabricate** tool usages, skill activations, or subagent delegations based on milestone state.
   - If no physical tools were executed in a stage or milestone, `tool_usages`, `skill_activations`, and `subagent_delegations` remain strictly empty (`[]`).
   - If `state/trajectory_events.jsonl` or `transcript.jsonl` exists, the trajectory must be assembled directly from observable event streams.

4. **Dedicated Trajectory Engine (`scripts/trajectory_engine.py`)**:
   - Manages real-time atomic appending to `state/trajectory_events.jsonl` and `state/audit_log.jsonl`.
   - Provides deterministic parsing of `transcript.jsonl` into the 11 canonical events.
   - Compiles compliant `trajectory.json` artifacts conforming to `contracts/evolution/trajectory.schema.json`.
   - Strictly enforces zero private chain-of-thought (`chain_of_thought`, `thinking`, `internal_monologue`).

### Consequences
- **Positive**: Trajectories reflect 100% ground-truth observable reality; eliminates hallucinated tool calls; provides verifiable provenance for every action; enriches learning and continuous improvement engines with real telemetry.
- **Negative**: Stages recorded without active hook execution or transcript logs will possess empty tool lists rather than mock tool summaries.

---

## ADR-021: Deterministic Feedback Routing and Prohibition of Generic Target Defaults

### Status
Accepted

### Context
In earlier iterations of the continuous learning pipeline, when user critique was captured via `AcademicIntegratedLearningHub.process_user_turn()`, missing caller metadata triggered hardcoded fallback defaults:
```python
meta.get("target_skill", "statistical-data-analyst")
meta.get("target_agent", "statistics-agent")
```
Consequently, feedback regarding theoretical literature citations, research methodology, qualitative themes, academic prose tone, or OpenXML typography was mistakenly attributed to `statistics-agent` and `statistical-data-analyst`. This created catastrophic feedback pollution:
- `statistics-agent` received anti-patterns and improvement candidates for problems in literature synthesis or APA formatting.
- Genuine methodology or writing skills received zero feedback for diagnosed issues.
- The continuous improvement loop (`run_fast_loop()`) attempted to optimize the wrong skills with irrelevant lessons.

### Decision
1. **Mandatory 5-Field Target Structure**:
   Every `FeedbackRecord` generated across the system must strictly contain:
   - `target_agent`: Assigned subagent role (e.g., `literature-expert`, `methodology-expert`, `academic-writer`, `results-auditor`).
   - `target_skill`: Specific production skill folder (e.g., `persian-literature-review-builder`, `methodology-review`, `chapter-4-writing`, `apa-reporting`).
   - `capability`: Canonical capability identifier (e.g., `literature_synthesis`, `research_methodology`, `academic_writing`, `apa_formatting`).
   - `task`: Associated milestone or task identifier (e.g., `M2_LITERATURE`, `M3_METHODOLOGY`).
   - `stage`: Associated micro-stage identifier (e.g., `02_literature_review`, `06_hypothesis_1`).

2. **Authoritative 4-Tier Resolution Hierarchy (`scripts/academic_feedback_router.py`)**:
   Target capability resolution is executed deterministically without generic guessing:
   - **Tier 1: Explicit Metadata**: Provided directly in caller metadata (`target_agent`, `target_skill`, `capability`, `task`, `stage`).
   - **Tier 2: Active State Machine**: Inspects `state/current_state.json` for active milestones in status `RUNNING`, `VALIDATING`, `AWAITING_APPROVAL`, or `READY`.
   - **Tier 3: Transcript Forensics**: Inspects the most recent tool calls in `transcript.jsonl` (extracting skill from `run_command` paths or target file patterns in file tools).
   - **Tier 4: Semantic Domain Mapping**: Classifies critique patterns against domain dictionaries (`WRITING_CORRECTION`, `EVIDENCE_CORRECTION`, `METHODOLOGY_CORRECTION`, `DATA_ANALYSIS_CORRECTION`, `QUALITY_STYLE_CORRECTION`, `RESEARCH_INTEGRITY_CORRECTION`, `PROCESS_CORRECTION`, `STATISTICAL_CORRECTION`).

3. **Absolute Prohibition of Generic Defaults (Fail-Closed)**:
   - If feedback cannot be resolved to a verified capability across all 4 tiers, the router must raise `UnresolvableFeedbackTargetError`.
   - Falling back to `statistics-agent` or any other generic default is **strictly prohibited**.

4. **Explicit Feedback Lifecycle Event**:
   - The router emits `USER_FEEDBACK_DETECTED` to `TrajectoryEngine` (`state/trajectory_events.jsonl`), `state/audit_log.jsonl`, and `learning/telemetry/activity.jsonl` immediately upon detection.
   - The feedback record is passed with its resolved target capability directly into `AcademicIntegratedLearningHub.run_fast_loop(target_agent, target_skill, capability)`.

### Consequences
- **Positive**: Guarantees 100% targeting accuracy in continuous learning; eliminates cross-capability feedback pollution; ensures that improvement candidates and lessons are applied strictly to the responsible agent and skill; full adherence to Directives 0, 12.1, and 19.
- **Negative**: Ambiguous feedback lacking both active state machine context and transcript logs will fail-closed rather than silently logging under a fallback agent.

---

## ADR-022: Idempotent Feedback Processing & Event Deduplication Hygiene

### Status
Accepted

### Context
In earlier iterations of the feedback and learning pipeline, user corrections were processed via an ad-hoc, multi-path flow:
`scan_transcript()` followed by `process_user_turn()`.
Both methods attempted to detect and process corrections without unified event tracking or deduplication:
- `scan_transcript()` parsed the entire `transcript.jsonl` from line 0 on every invocation, detecting corrections and writing feedback artifacts to disk.
- Immediately afterward, `process_user_turn()` was invoked on the exact same user turn, detecting the correction again and triggering redundant fast evolution loops.
- Subsequent lifecycle hook executions (e.g. `Stop` or `PreInvocation`) re-scanned past turns, reprocessing historical corrections repeatedly.

This duplicate processing polluted the learning store, created redundant feedback artifacts, and wasted computational resources.

### Decision
1. **The `USER_FEEDBACK_DETECTED` Event & Deterministic `event_id`**:
   Every detected feedback instance is modeled as a canonical `USER_FEEDBACK_DETECTED` event with a unique, deterministic `event_id`:
   ```python
   seed = f"{conversation_id}:{turn_index}:{clean_user_text}"
   event_id = f"EVT-FDB-{sha256(seed)[:16].upper()}"
   ```
   - Same turn + same critique text $\to$ identical `event_id`.
   - Distinct turn ($turn\_index_2 \ne turn\_index_1$) $\to$ distinct `event_id` (enabling legitimate repetition counting).
   - Explicit caller-provided `event_id` is honored directly.

2. **Persistent Event Store (`FeedbackEventTracker`)**:
   - Maintains an in-memory set and atomically persists to `learning/experience/feedback/processed_event_ids.json`.
   - Thread-safe and process-safe via atomic temporary file replacement (`os.replace`).
   - Automatically refreshes from disk on lookup if an event is not yet cached in memory.

3. **Strict Deduplication Rule (Idempotency Invariant)**:
   - When an event arrives at `AcademicIntegratedLearningHub.process_user_turn()`, `AcademicCorrectionDetector.scan_transcript()`, or `FeedbackRouter.emit_feedback_detected()`:
     ```python
     if tracker.is_event_processed(event_id):
         return {
             "action": "IGNORED_DUPLICATE",
             "event": "USER_FEEDBACK_DETECTED",
             "event_id": event_id,
             "status": "ALREADY_PROCESSED",
             "is_correction": False
         }
     ```
   - If `scan_transcript()` processes a turn first, subsequent `process_user_turn()` on that turn is ignored.
   - If `process_user_turn()` processes a turn first, subsequent `scan_transcript()` on that turn is ignored.
   - Repeated scans of the same transcript produce exactly zero duplicate feedback records.

### Consequences
- **Positive**: 100% elimination of duplicate feedback processing; zero redundant fast evolution loops; clean, idempotent event-processing hygiene conforming to Directives 0 and 19.
- **Negative**: Critique text without turn metadata within the same session will be deduplicated on subsequent identical submissions unless an explicit distinct `event_id` or `turn_index` is provided.

---

## ADR-023: Closed Behavioral Evolution Engine with 3-Way Arms and Isolated Sandboxes

### Status
Accepted

### Context
While previous evolution phases implemented components for experience recording, feedback detection, candidate generation, and promotion gating, they did not form a fully closed behavioral evolution loop. Crucial architectural gaps remained:
1. Candidate patches lacked an isolated instantiation sandbox, creating risk of premature modification to production skills or agents.
2. Candidate testing relied on monolithic or scalar benchmarks rather than explicit counterfactual multi-arm comparisons.
3. Behavior analysis lacked a dedicated observable-only root cause engine grounded strictly in trajectory events without chain-of-thought hallucination.
4. QC failures (e.g. stage validator gate rejections) were not treated as first-class triggers symmetric with user feedback.

### Decision
1. **The 13-Stage Closed Behavioral Evolution Sequence**:
   The self-improvement architecture strictly follows the closed-loop pipeline:
   ```text
                PRODUCTION AGENT
                       │
                       ▼
                  REAL TASK
                       │
                       ▼
                REAL TRAJECTORY
                       │
             ┌─────────┴──────────┐
             ▼                    ▼
        USER FEEDBACK        QC FAILURE
             │                    │
             └─────────┬──────────┘
                       ▼
               BEHAVIOR ANALYSIS
                       │
                       ▼
                 LESSON HYPOTHESIS
                       │
                       ▼
                CANDIDATE PATCH
                       │
                       ▼
             ISOLATED AGENT VERSION
                       │
                       ▼
                  REAL TEST
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          baseline  candidate  adversarial
             │         │         │
             └─────────┼─────────┘
                       ▼
                INDEPENDENT QC
                       │
                       ▼
                HELD-OUT TESTS
                       │
                       ▼
                   PROMOTE
   ```

2. **Dual First-Class Triggers**:
   - `USER_FEEDBACK`: Originates from `USER_FEEDBACK_DETECTED` with deduplication hygiene.
   - `QC_FAILURE`: Originates from `VALIDATION_FAILED` (stage validator gates, challenger red-team critiques, integrity violations).

3. **Observable-Only Behavior Analysis (`AcademicBehaviorAnalyzer`)**:
   - Ingests trajectory events (`ordered_actions`) and trigger details.
   - Pinpoints observable step where defect manifested without inspecting or hallucinating private chain-of-thought tokens (`sanitize_observable_only`).
   - Categorizes failure signature against domain taxonomy (`REPORTING_P_ZERO`, `MISSING_PERSIAN_LEADING_ZERO`, `DICHOTOMIZING_CONTINUOUS_VARIABLE`, `VIOLATED_ASSUMPTION_IGNORED`, etc.).
   - Emits schema-validated `BehaviorAnalysisReport` conforming to `contracts/evolution/behavior_analysis.schema.json`.

4. **Isolated Agent Sandbox (`AcademicIsolatedAgentSandbox`)**:
   - Materializes candidate mutation in `learning/candidates/<cid>/isolated_agent/`.
   - Clones target components and applies patch cleanly.
   - Emits `isolated_manifest.json` tracking original and patched file hashes.
   - Canonical production files in `.agents/agents/` and `.agents/skills/` remain 100% untouched.

5. **Three-Way Test Arms (`baseline`, `candidate`, `adversarial`)**:
   - Compares 3 explicit arms:
     - `baseline`: Unmodified production agent/skill on the test case.
     - `candidate`: Isolated candidate agent version on the test case.
     - `adversarial`: Isolated candidate on an adversarial challenge case.
   - Verifies: `defect_resolved`, `candidate_outperformed_baseline`, `adversarial_resilience_verified`, and `zero_regressions_verified`.
   - Emits `ThreeWayEvaluationReport` conforming to `contracts/evolution/three_way_evaluation.schema.json`.

6. **Independent QC & Held-Out Generalization**:
   - Evaluates candidate across 8 independent quality dimensions (`AcademicEvaluationLab`).
   - Verifies cryptographic integrity of held-out cases (`verify_heldout_integrity`).
   - Enforces overfitting guard (`check_overfitting`).

7. **Pareto-Governed Promotion (`AcademicPromotionEngine`)**:
   - LOW-RISK auto-promotes; MEDIUM-RISK stages with human approval; HIGH-RISK blocks.
   - Creates pre-promotion snapshot, updates canonical files, emits `PRM-*.json`, logs telemetry in `improvement_history.jsonl`, and audits post-promotion drift (`AcademicBehaviorDriftMonitor`).

### Consequences
- **Positive**: Fully closes the evolutionary loop around real observable behavior; prevents premature canonical file mutations via sandboxes; provides rigorous 3-way counterfactual evidence before promotion; eliminates overfitting via cryptographically sealed held-out suites; adheres strictly to Directives 0, 6, 12.1, and 19.
- **Negative**: Requires additional disk storage for candidate sandboxes and 3-way evaluation reports in `learning/candidates/` and `learning/evaluations/three_way/`.

---

## ADR-024: Separation of Learning Roles Across Six Native Antigravity Subagents

### Status
Accepted

### Context
In prior designs, the self-improvement architecture relied partly on monolithic Python classes or blurred boundaries between diagnosing defects, distilling lessons, formulating patches, and evaluating candidates. This risked violating:
1. **Directive 12.1 (Sole Orchestrator Mandate & Prohibition of Python Agent Emulation)**: Python scripts must never impersonate cognitive agents or manage subagent dispatch.
2. **Directive 19 (Six-Part Functional Separation Invariant)**: Agents reason and decide; Skills instruct; Scripts compute; Hooks enforce; State machines authorize; Manifests define completion.

Furthermore, an agent or script formulating a code modification must never evaluate or grade its own output, and observable trajectory reconstruction must never inspect private chain-of-thought tokens.

### Decision
1. **The Six Core Questions Mapping**:
   The continuous self-improvement framework is strictly partitioned across six specialized cognitive roles in `.agents/agents/`, each answering a single, unambiguous core question:
   - **`trajectory-analyzer`**: *"What actually happened?"*
     Reconstructs observable tool calls, CLI commands, exit codes, and output artifacts from `transcript.jsonl` and hook telemetry. Strictly zero private chain-of-thought access.
   - **`behavior-analyst`**: *"What behavior was wrong?"*
     Conducts causal root-cause analysis on observable trajectories and triggers (`USER_FEEDBACK_DETECTED` / `VALIDATION_FAILED`), classifying failure signatures without modifying files or executing commands.
   - **`knowledge-curator`**: *"What generalizable lesson does this imply?"*
     Distills persistent, versioned lessons (`learning/knowledge/lessons/`), anti-patterns, and exemplars, enforcing strict scope containment (`project` vs `cross-project`) without directly promoting candidates.
   - **`skill-evolver`**: *"What candidate modification would change the behavior?"*
     Synthesizes targeted candidate modifications (`improvement_candidate`) with unified diffs in an isolated branch workspace, adhering to Directive 18 single-view ceilings (<= 500 lines, <= 40,000 bytes).
   - **`evaluation-agent`**: *"Did the modification actually improve behavior?"*
     Independently tests candidate modifications in an isolated branch workspace against deterministic test harnesses and 3-way evaluation arms across 8 dimensions. Forbids unverified declarations of success and scalar intelligence scores.
   - **`curriculum-builder`**: *"What future task would test whether the lesson generalizes?"*
     Architects graduated complexity challenge tasks (L1 to L4) and benchmark datasets with bounded empirical decimal noise ($\delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$) per Directive 9.

2. **Least-Privilege Tool Boundaries**:
   - `trajectory-analyzer` & `behavior-analyst`: Strictly read-only (`view_file`, `list_dir`, `grep_search`, `find_by_name`). Zero write, zero run tools.
   - `knowledge-curator`, `skill-evolver`, `curriculum-builder`: Staging write-only (`view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`). Zero `run_command`.
   - `evaluation-agent`: Execution-enabled (`view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`).

3. **Native Antigravity Multi-Agent Orchestration**:
   - The Lead Orchestrator coordinates all learning roles via native `invoke_subagent`.
   - Python scripts in `.agents/skills/` and `scripts/` serve strictly as deterministic computational utilities ("The Hands").
   - Formal multi-agent protocol documented in `learning/LEARNING_MULTI_AGENT_SPEC.md`.

### Consequences
- **Positive**: Clean cognitive separation of concerns; zero Python agent emulation; independent, un-gameable evaluation; strict least-privilege tool security; 100% compliance with Directives 0, 9, 12.1, 18, and 19.
- **Negative**: Deliberation requires coordinated sequential invocations across native subagents.

---

## ADR-025: Real Candidate Generation Pipeline (5-Input, 2-Stage, 7-Category Architecture)

### Status
Accepted

### Context
In earlier iterations of the self-improvement system, candidate patch generation relied on a rigid heuristic shortcut:
$$\text{evidence} \longrightarrow \text{keyword match} \longrightarrow \text{hard-coded mutation}$$
This resulted in severe defects:
1. **Ungrounded Hallucinations**: Patches contained canned, repetitive text (e.g., repeating longitudinal mixed models advice even when testing `apa-reporting` or `data-cleaning`).
2. **Disconnected from Target Code**: Mutations were not synthesized against the actual text of the target `SKILL.md` or `agent.md`, risking unapplyable diffs.
3. **Narrow Modification Scope**: Candidates were limited to generic procedural text rather than targeting specific cognitive, procedural, and heuristic control surfaces.

### Decision
Rebuild candidate generation into an authentic, context-driven 5-input, 2-stage evolutionary pipeline:

$$\begin{aligned}
\text{trajectory} + \text{feedback} + \text{failure} &+ \text{existing Skill} + \text{relevant knowledge} \\
&\downarrow \\
\text{Behavior Analyst } &(\text{AcademicBehaviorAnalyzer}) \\
&\downarrow \\
\text{candidate diagnosis } &(\text{gap, category, section, resolution}) \\
&\downarrow \\
\text{Skill Evolver } &(\text{AcademicCandidateGenerator}) \\
&\downarrow \\
\text{candidate patch } &(\text{unified diff, testable hypothesis})
\end{aligned}$$

1. **The Five Inputs**:
   - `trajectory`: Observable ordered actions, tool usages, and outputs (zero private chain-of-thought).
   - `feedback`: Concrete user correction with target agent, target skill, and desired behavior.
   - `failure`: Automated validator or QC failure report.
   - `existing Skill`: Physical raw text of target `SKILL.md` or `agent.md` read directly from disk.
   - `relevant knowledge`: Curated lessons, anti-patterns, and exemplars from `learning/knowledge/`.

2. **Stage 1: Behavior Analyst Diagnosis**:
   - `AcademicBehaviorAnalyzer._diagnose_candidate_gap()` analyzes the failure against the existing skill text and relevant knowledge.
   - Categorizes the defect into one of the **Seven Target Modification Categories**:
     1. `agent instruction`: Modifying system prompts or agent cognitive directives.
     2. `Skill`: Adding or refining step-by-step operational workflows in `SKILL.md`.
     3. `decision tree`: Introducing explicit conditional branching and model comparison criteria.
     4. `verification rule`: Adding pre-flight gates or post-execution verification checks.
     5. `delegation rule`: Specifying subagent delegation triggers and role boundaries.
     6. `retrieval rule`: Improving contextual lookup, questionnaire keys, or exemplar retrieval.
     7. `exception rule`: Handling edge cases, assumption violations, missing data, and boundary conditions.
   - Pinpoints `affected_section` and formulates `diagnosed_gap` and `proposed_resolution`.

3. **Stage 2: Skill Evolver Candidate Patch**:
   - `AcademicCandidateGenerator.generate_candidate_from_real_behavior()` consumes the candidate diagnosis and existing skill content.
   - Dynamically constructs a targeted modification tailored to the diagnosed category and affected section.
   - Generates a valid unified diff (`--- a/... +++ b/...`) against the existing skill text.
   - Formulates an empirical `testable_hypothesis` ("If ... then ... will ...").
   - Enforces Directive 18 single-view ceilings ($\le 500$ lines, $\le 40,000$ bytes).
   - Validates the candidate against `contracts/evolution/improvement_candidate.schema.json`.

### Consequences
- **Positive**: Complete elimination of canned hardcoded mutations; authentic contextual patches across all 7 architectural surfaces; verifiable unified diffs; guaranteed compliance with Directive 18 ceilings and Directive 19 functional separation.
- **Negative**: Requires disk I/O to load existing skill/agent files and knowledge bases during candidate generation.

---

## ADR-026: Physical Activation and Hash-Change Verification Invariant in Behavioral Promotion

### Status
Accepted

### Context
In prior implementations, a behavioral improvement candidate could transition through the lifecycle stages up to `PROMOTED` and `ACTIVE` while the canonical `SKILL.md` or `agent.md` on disk remained completely unchanged. The promotion engine only recorded declarative knowledge or logged database entries, allowing phantom promotions where the system claimed continuous evolution without any physical change in production agent capabilities.

### Decision
Rebuild the promotion layer around physical file activation and the **Target Hash Verification Invariant**:

$$\begin{aligned}
\text{candidate generated} &\longrightarrow \text{candidate materialized} \longrightarrow \text{candidate executed} \\
&\longrightarrow \text{candidate evaluated} \longrightarrow \text{candidate passes gates} \\
&\longrightarrow \text{candidate version activated on disk}
\end{aligned}$$

1. **Physical File Activation (`_deploy_active_candidate`)**:
   - Every candidate targeting a `SKILL.md`, `agent.md`, or script file must physically apply its mutation to the canonical target component on disk.
   - Computes baseline content hash: $H_{\text{baseline}} = \text{sha256}(C_{\text{baseline}})$.
   - Creates an immutable rollback snapshot in `learning/promotions/snapshots/<snap_id>.json` storing the exact $C_{\text{baseline}}$ and $H_{\text{baseline}}$.
   - Applies the mutation (`UNIFIED_DIFF`, `FULL_CONTENT_REPLACEMENT`, or `PARAMETER_PATCH`).
   - Enforces Directive 18 single-view ceilings ($\le 500$ lines, $\le 40,000$ bytes) fail-closed.
   - Physically writes the mutated content to disk.
   - Reads back the file from disk and computes active content hash: $H_{\text{active}} = \text{sha256}(C_{\text{active}})$.

2. **The Target Hash Verification Invariant**:
   - If $H_{\text{active}} == H_{\text{baseline}}$ where a change was expected:
     $$\text{PROMOTION FAILURE}$$
   - The engine raises `PromotionHashMismatchError`, rolls back any partial disk changes, archives the candidate under `learning/archive/` with `failure_reason: "PROMOTION FAILURE: Target Skill hash did not change where a change was expected"`, and refuses to mark the candidate `ACTIVE`.

3. **Deterministic Rollback (`rollback_promotion`)**:
   - `AcademicPromotionEngine.rollback_promotion(promotion_id_or_snapshot_id)` reads the rollback snapshot, restores $C_{\text{baseline}}$ to the target file on disk, verifies that the restored hash matches $H_{\text{baseline}}$, and marks the candidate `ROLLED_BACK`.

4. **Closed-Loop Integration**:
   - `AcademicRealBehaviorEvolution` (Stage 13) verifies that `active_component_hash != baseline_component_hash` upon promotion before concluding the evolutionary loop.

### Consequences
- **Positive**: Complete elimination of phantom promotions; 100% guarantee that every `PROMOTED` candidate physically changes production behavior; tamper-evident rollback capability; strict adherence to Directives 0, 8, 12.1, 18, and 19.
- **Negative**: Requires disk write access to `.agents/skills/` or `.agents/agents/` during authorized promotion.

