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



