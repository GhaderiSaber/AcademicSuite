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



