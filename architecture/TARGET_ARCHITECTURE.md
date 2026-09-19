# AcademicSuite — Target Architecture & Antigravity Compatibility Specification

**Document Version:** 1.0.0 (Target Architecture)  
**Operative Date:** September 2026 (1405 SH)  
**System Status:** Authoritative Target Architecture  

---

## 🏛️ Foundational Architectural Rule
> **From this point forward: No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**  
> **This prevents AcademicSuite from continuing to grow horizontally.**

---

## 1. Architectural Philosophy: Native Antigravity Alignment

The primary technical objective of the **Target Architecture** is to establish a seamless, thin compatibility boundary with Google Antigravity. Rather than attempting to wrap, emulate, or replace Antigravity's agent runtime, AcademicSuite functions as a collection of:
1. **Declarative Antigravity-Native Agents & Subagents** (`.agents/agents/`)
2. **On-Demand Progressive Disclosure Skills** (`.agents/skills/`)
3. **Deterministic Mathematical & Document Engines** (`scripts/` and skill `scripts/`)
4. **Lifecycle Hooks & OS Security Gates** (`.agents/hooks.json` and POSIX permissions)
5. **Fail-Closed Artifact Verification Contracts** (`contracts/` and `validators/`)

```text
+-----------------------------------------------------------------------------------+
|                        GOOGLE ANTIGRAVITY AGENT RUNTIME                           |
|                                                                                   |
|  [ Antigravity Session ] <---> [ Native invoke_subagent ] <---> [ Subagents ]     |
|          |                                                             |          |
|          | Context / Memory                                            | Tools    |
|          v                                                             v          |
|  [ Progressive Skills ]                                        [ Built-in Tools ] |
|   .agents/skills/<name>/SKILL.md                               - run_command      |
|                                                                - view_file        |
|                                                                - write_to_file    |
+----------------------------------------+------------------------------------------+
                                         |
                                         | Execution Boundary (run_command / CLI)
                                         v
+-----------------------------------------------------------------------------------+
|                         ACADEMICSUITE DETERMINISTIC "HANDS"                       |
|                                                                                   |
|   +--------------------------+  +-------------------------+  +-----------------+  |
|   | Statistical Engines      |  | Psychometrics & Sizing  |  | OpenXML Word    |  |
|   | - run_regression.py      |  | - gpower_engine.py      |  | - build_triad   |  |
|   | - run_sem.py             |  | - psychometrics.py      |  | - assemble_docx |  |
|   +--------------------------+  +-------------------------+  +-----------------+  |
+----------------------------------------+------------------------------------------+
                                         |
                                         | Output Verification Boundary
                                         v
+-----------------------------------------------------------------------------------+
|                         INDEPENDENT FAIL-CLOSED VALIDATION                        |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   | validators/run_all_validators.py                                          |   |
|   | - data_integrity          - statistical_assumptions                       |   |
|   | - numerical_consistency   - result_consistency                            |   |
|   | - reporting_consistency   - longitudinal_modmed                           |   |
|   +---------------------------------------------------------------------------+   |
|                                                                                   |
|          Generates: Synchronized Triad Artifacts (.docx + .md + .json)            |
+-----------------------------------------------------------------------------------+
```

---

## 2. The Six-Part Functional Separation Invariant

To guarantee architectural stability, eliminate hallucinations, and prevent horizontal sprawl, AcademicSuite strictly enforces the six-part separation of concerns across every research engagement:

```text
+──────────────────────+─────────────────────────────────────────────────────────────+
| Layer                | Operational Scope & Invariant Ownership                     |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 1. Agent             | DECIDES: Reasoning role, delegation, context,               |
|                      | decision-making, responsibility, communication              |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 2. Skill             | INSTRUCTS: Domain knowledge, decision trees,                |
|                      | execution instructions, reusable procedures, APA formats    |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 3. Script            | COMPUTES: Deterministic calculation, data transformation,   |
|                      | file generation, OpenXML compilation, hashing               |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 4. Hook              | ENFORCES: Synchronous interception, safety gates,           |
|                      | tamper prevention, honesty audits, tool execution control   |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 5. State Machine     | AUTHORIZES TRANSITION: Milestone progression gating,        |
|                      | immutable event timeline logging, state persistence         |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 6. Artifact Manifest | DEFINES COMPLETION: Schema contract validation,             |
|                      | required triad files (.docx+.md+.json), affirmative evidence |
+──────────────────────+─────────────────────────────────────────────────────────────+
```

---

## 3. The Native-Agent Contract

AcademicSuite defines agents purely as Antigravity-compatible Markdown files. There is **zero proprietary Python agent runtime** or wrapper class.

### 3.1 The Minimal Agent Contract
An agent is valid in Antigravity when it contains only:
```markdown
---
name: sample-agent
description: Clear, actionable description of role and delegation triggers.
---

# Agent Instructions

Detailed behavioral instructions, domain principles, and workflows.
```

### 3.2 The Progressive Capability Contract
As needs expand, the following official Antigravity fields may be added:
```markdown
---
name: statistical-expert
description: Advanced quantitative modeling authority for SEM, CFA, mediation, moderation.
role: Statistical Modeling & Latent Structural Analysis Authority
model: pro
mainAgent: true
subagent: true
tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - list_dir
  - grep_search
  - find_by_name
skills:
  - sem
  - cfa
  - mediation
  - moderation
  - regression
  - statistical-data-analyst
agents:
  - statistics-agent
  - psychometric-expert
inheritCustomizations: true
---
```

### 3.3 Strict Frontmatter Policy Elimination
- **`commandExecutionPolicy` is strictly forbidden in frontmatter**.
- Antigravity's agent loader rejects frontmatter with unknown fields, hiding the agent from the IDE dropdown and subagent registry.
- Security is instead enforced through the multi-layered security architecture described in Section 5.

---

## 4. Subagent & MainAgent Semantics

In Antigravity:
- **`mainAgent: true`**: Agent appears in the primary workspace agent selector / chat interface.
- **`subagent: true`**: Agent appears in the available subagents registry for the `invoke_subagent` tool.
- **`mainAgent: true, subagent: true`** (Dual-Role Authority): Specialist authorities (such as `methodology-expert`, `statistical-expert`, `academic-writer`) can be selected by the user for direct interactive chat OR spawned dynamically by `academic-orchestrator` as subagents.
- **`mainAgent: false, subagent: true`** (Pure Specialist Subagent): Pure workers and critics (such as `statistics-agent`, `data-curator`, `results-auditor`) are invoked solely by orchestrators and authorities.

---

## 5. Multi-Layered Defense-in-Depth Security

In place of unsupported frontmatter policy flags, execution restrictions are enforced mechanically across four independent layers:

```text
Layer 1: Antigravity Platform & IDE Permissions
   │     Workspace settings, user confirmation prompts on untrusted commands.
   ▼
Layer 2: POSIX / OS Least-Privilege File Permissions
   │     scripts/permission_manager.py marks raw datasets as 0444 (Read-Only).
   ▼
Layer 3: Constitutional Lifecycle Hooks (.agents/hooks.json)
   │     PreToolUse blocks destructive shell commands, non-ASCII filenames, and dataset mutation.
   │     Stop hook inspects transcript.jsonl to enforce Binary Honesty and invoke_subagent truth.
   ▼
Layer 4: Deterministic Scripts & Agent Instructions
         Domain scripts fail-closed on unauthorized inputs; agent contracts forbid out-of-scope actions.
```

---

## 6. The Triad Artifact Invariant & Stage-Gate Granularity

Under Constitutional Directive 3:
1. **Zero Monolithic Generations**: Generating an entire chapter or dissertation in a single un-audited prompt is strictly forbidden.
2. **Synchronized Triad Artifacts**: Every micro-stage and individual hypothesis must produce three synchronized physical files on disk:
   - **`.json`**: Exact numerical parameters, test statistics, and audit flags.
   - **`.md`**: Human-readable narrative, APA 7 tables, and statistical interpretations for immediate diffing.
   - **`.docx`**: Institutional OpenXML document with RTL typography, Persian font bindings (`B Nazanin` / `B Titr`), decoupled LTR numbers, and native Word OMML math equations.
3. **One-Hypothesis-One-Stage**: Every hypothesis in Chapter 4 and Chapter 5 has an independent micro-stage directory (`06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json`).

---

## 7. Continuous Learning & Self-Improvement Boundaries

The self-improvement subsystem (`learning/` and `contracts/evolution/`) operates under strict containment:
1. **Zero Runtime Self-Modification**: Learning subagents cannot directly mutate active skill files (`SKILL.md`) or agent specifications (`agent.md`).
2. **Candidate Mutation Protocol**: Improvements are drafted as structured candidates (`improvement_candidate.schema.json`) and benchmarked against frozen evaluation suites (`evaluation_case.schema.json`).
3. **Human-in-the-Loop Promotion**: Promotion requires explicit verification by `evaluation-agent` and final human approval. 

---

## 8. Capability-Driven Orchestration Architecture (Phase 3)

### 8.1 Resolution Architecture
AcademicSuite replaces static linear progression chains (`stage 1 → stage 2 → ... → statistics-agent`) with dynamic, capability-based resolution:

```text
Task Prompt
     │
     ▼
Research Objective & Empirical Design Derivation
     │  - study_type: RCT, correlational_structural, scale_validation, qualitative, meta_analysis
     │  - group_structure: multi-group, single-group, factorial
     │  - temporal_dynamics: repeated measures, cross-sectional, single-point
     │  - waves: follow-up, pre-post, cross-sectional
     │  - factors: ["RCT", "multi-group", "repeated measures", "follow-up"]
     ▼
Required Capabilities Matrix
     │  - design-methodology
     │  - longitudinal-analysis
     │  - assumption-checking
     │  - effect-size
     │  - post-hoc/comparison
     │  - statistical-execution
     │  - results-writing
     │  - audit
     ▼
Dynamic Antigravity Subagent Team Assembly
     │  - Lead Orchestrator: academic-orchestrator
     │  - Minimal Assembled Subagents: [methodology-expert, data-curator, statistical-expert,
     │                                  statistics-agent, academic-writer, statistical-auditor,
     │                                  academic-challenger, validation-agent]
     │  - Pruned Agents: Explicitly accounts for and excludes unneeded workspace agents
     │                   with documented scientific rationale
     ▼
Native Antigravity Execution via `invoke_subagent`
```

### 8.2 Architectural Invariants
1. **Deterministic Resolver as "The Hands"**: `scripts/academic_task_router.py` and `scripts/capability_resolver.py` compute design parameters, capability requirements, and team compositions deterministically. They never execute agents or simulate orchestration.
2. **Antigravity as Sole Conductor**: `academic-orchestrator` is the sole orchestrator, dynamically invoking only the resolved subagent roles via native `invoke_subagent`.
3. **Fail-Closed Safety**: Out-of-domain, non-academic, or unsupported requests are blocked with `status: BLOCKED` and `escalation_required: true`. Ambiguous requests return candidate capabilities and clarification prompts rather than guessing.

---

## 9. The Methodology Decision Layer & The 8-Step Decision Ladder (Phase 4)

### 9.1 The 8-Step Ladder
AcademicSuite elevates methodology into an autonomous decision layer that precedes and constrains all inferential computation:

```text
1. Research Question
       ↓
2. Empirical Design
       ↓
3. Estimand Definition
       ↓
4. Candidate Methods Evaluation
       ↓
5. Assumption Diagnostics Checklist
       ↓
6. Method Selection & Refutation Matrix
       ↓
7. Execution Specification (Execution Contract)
       ↓
8. Statistical Executor ("The Hands")
```

### 9.2 The Methodology Decision Record (MDR) Contract
All methodological reasoning is codified into a binding contract:
`contracts/methodology_decision_record.schema.json`.

An MDR contains:
- **`research_question`**: The exact empirical inquiry.
- **`design`**: Formal empirical architecture (`study_type`, `group_structure`, `temporal_dynamics`, `waves`, `factors`).
- **`estimand`**: The target causal/statistical parameter (ATE, CATE, indirect effect, factor loading).
- **`candidate_methods`**: Comparative assessment of candidate analytical strategies with pros, cons, and suitability.
- **`assumptions`**: Diagnostic checklist with test methods, thresholds, and pre-specified violation remediation fallbacks.
- **`selected_method`**: Formally chosen model family and execution script.
- **`rejected_methods`**: Literature-grounded refutation matrix citing peer-reviewed methodological precedents:
  - Rejecting gain-score t-tests due to Lord's paradox (Lord, 1967; Vickers & Altman, 2001).
  - Rejecting post-test only ANOVA due to baseline variance neglect and power loss (Cohen, 1988).
  - Rejecting Baron & Kenny regression due to deflated statistical power (Hayes, 2018).
  - Rejecting Sobel tests due to skewed product distributions (Preacher & Hayes, 2004).
  - Rejecting median splits due to 35-50% power loss (MacCallum et al., 2002).
- **`execution_contract`**: The binding execution contract passed downstream to `statistics-agent` and `StatisticalPipelineEngine`.

### 9.3 Inviolable Execution Decoupling
1. **The Executor Never Invents Methodology**: `statistics-agent` receives the `execution_contract` and executes deterministically. It has zero authority to select, alter, or invent statistical models.
2. **Method Lock Enforcement**: `StatisticalPipelineEngine` validates the plan against `methodology_decision_record.schema.json` and raises `MethodMismatchError` or `MethodologyViolationError` if any deviation from the contract is attempted.

---

## 10. The Deterministic Statistical Execution Subsystem (Phase 5)

### 10.1 The 4-Tier Cognitive & Computational Boundary
AcademicSuite enforces an unbending separation between cognitive reasoning, deterministic computation, academic rhetoric, and adversarial validation:

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│ Tier 1: LLM Reasoning ("What should be done?")                                 │
│ - Agents: statistical-expert, methodology-expert                              │
│ - Generates: Methodology Decision Record (MDR) & StatisticalExecutorContract  │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Binding 7-Part Input Contract
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ Tier 2: Deterministic Computation ("What are the actual numbers?")            │
│ - Agents / Engines: statistics-agent, StatisticalPipelineEngine, Python/R     │
│ - Computes: Exact test statistics, df, p-values, effect sizes, CIs, diagnostics│
│ - Invariant: Zero LLM mental arithmetic; zero synthetic statistics in prod     │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Verified 7-Part Output Package
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ Tier 3: Scholarly Drafting ("What do verified numbers mean?")                 │
│ - Agents: academic-writer                                                     │
│ - Generates: APA 7 narrative, table interpretations, Chapter 4/5 drafts       │
│ - Invariant: Numbers strictly extracted from Tier 2 JSON; zero hallucinations │
└──────────────────────────────────────┬────────────────────────────────────────┘
                                       │ Draft Artifacts (.docx, .md, .json)
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│ Tier 4: Adversarial Audit ("Are those claims actually supported?")            │
│ - Agents: statistical-auditor, validation-agent                               │
│ - Audits: Reported claims vs. JSON, df vs. N, assumption compliance, MSAI     │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 The 7-Part Input & Output Contract Architecture
Every statistical execution is governed by two formal JSON schemas:
1. **Input Contract (`contracts/statistical_executor_contract.schema.json`)**:
   - `DATA`: File path, format, SHA-256 data hash, data mode (`production`, `demo`, `test`, `simulation`), and `is_synthetic` flag.
   - `VARIABLE MAP`: Explicit assignment of dependent, independent, covariates, moderators, mediators, cluster, and ID variables.
   - `DESIGN`: Study typology, between/within factors, and measurement timepoints.
   - `METHOD SPECIFICATION`: Model family, exact method name, computational engine, and model formula.
   - `ASSUMPTIONS`: Formal list of parametric assumptions to verify before inferential testing.
   - `PARAMETERS`: Confidence level (0.95), alpha (0.05), bootstrap resamples (5,000), random seed, and missing data strategy.
   - `OUTPUT CONTRACT`: Target deliverables, table formats, effect size metrics, CI types, and decimal precision rules.
2. **Output Result Package (`contracts/statistical_execution_result.schema.json`)**:
   - `RESULT JSON`: Model name, sample size $N$, primary test statistic ($F, t, \chi^2$), degrees of freedom ($df_1, df_2$), exact $p$-value, and execution status.
   - `TABLES`: APA 7th Edition formatted markdown tables.
   - `DIAGNOSTICS`: Parametric assumption test statistics, $p$-values, and pass/fail indicators.
   - `EFFECT SIZES`: Standardized effect sizes ($\eta_p^2, d, R^2, \beta$).
   - `CONFIDENCE INTERVALS`: Parameter bounds and bootstrap BCa intervals.
   - `MODEL INFORMATION`: Convergence status, iteration count, and log-likelihood/AIC/BIC.
   - `PROVENANCE`: Input contract hash, data file hash, script path, execution timestamp, and runtime environment details.

### 10.3 Anti-Synthetic & Zero-Default-Sample Invariants
1. **Production Fail-Closed Guard**: In `production` mode, `StatisticalPipelineEngine` mechanically blocks missing datasets (`MissingProductionDataError`) and any attempt to substitute demo/sample fixtures (`ProductionSampleFallbackBlockedError`).
2. **Zero Synthetic Statistics**: Under no circumstance may arbitrary or hardcoded values (`effect_size = 0.25`, `CI = [0.10, 0.40]`) be emitted in production mode.
3. **Explicit Simulation Flags**: Datasets or models intended for psychometric simulation or benchmark testing must explicitly declare `is_synthetic: true` and `data_mode: "simulation"` or `"test"`.

### 10.4 Cryptographic Provenance & Computational Reproducibility
Every statistical result is cryptographically linked to the exact input data, execution contract, script identity, and python runtime environment via SHA-256 hashes, ensuring 100% auditable academic provenance.

---

## 11. Elimination of Synthetic Data Escape Routes & Universal Fail-Closed Policy (Phase 6)

### 11.1 The Four-Tier Architectural Classification
To ensure complete transparency and prevent latent data contamination, all data artifacts and execution pathways across AcademicSuite belong strictly to one of four tiers:
1. **`TEST FIXTURE`**: Deterministic synthetic inputs used exclusively inside `tests/` suites and test harnesses.
2. **`DEMO`**: Educational demonstrations permitting bundled example payloads ONLY when `--mode demo` is explicitly provided.
3. **`SIMULATION`**: Monte Carlo psychometric simulation workflows requiring explicit `--mode simulation` and tagged with `"is_synthetic": True` and `"data_mode": "simulation"`.
4. **`PRODUCTION`**: Live thesis and dissertation consulting workflows strictly requiring real, physically verified empirical data on disk.

### 11.2 Universal Fail-Closed Policy (`missing empirical input → BLOCKED`)
In production mode, any attempt to run without empirical data or fall back to bundled sample fixtures is mechanically blocked:
- **Presentation Builder (`persian-defense-presentation-builder/main.py`)**: Added `--mode {production, demo, test, simulation}`. In production mode, missing inputs or pointers to sample fixtures (`sample_*.json`, `/examples/`) trigger `CRITICAL SAFETY VIOLATION` and exit code 1 (`BLOCKED`).
- **Intervention Compiler (`compile_intervention_protocol.py`)**: Added `--mode` parameter. In production mode, unprovided payloads or pointers to sample fixtures raise `MissingProductionDataError` or `ProductionSampleFallbackBlockedError`.
- **Dual Loop Self-Improvement Engine (`academic_dual_loop_engine.py`)**: Fast loop and slow loop require real physical experiences and artifact outputs in production mode. Synthesis of mock experiences (`fast_loop_project`, `duration_seconds: 1.0`, `effect_size: 0.25`) is strictly BLOCKED.
- **Script Execution Guard (`script_execution_guard.py`)**: Added `is_synthetic: bool = False` check and internal JSON inspection. Production mode blocks any payload containing sample markers or `"is_synthetic": True`.
- **Batch Orchestrator (`orchestrator_cli.py`)**: Purges `default_sample` fallbacks and inspects incoming payloads for internal synthetic flags in production mode.




