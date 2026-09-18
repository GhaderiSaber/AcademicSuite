# AcademicSuite Current State Audit: Architectural Foundation for Self-Improvement

**Document Version:** 1.0.0  
**Audit Date:** September 2026 (1405 SH)  
**System Status:** Production Operational — Antigravity Native Orchestration with Deterministic Hands  
**Scope:** Deep inspection of current agents, skills, state engines, events, validators, feedback channels, and memory systems to establish the baseline for behavioral self-improvement.

---

## 1. Executive Summary

AcademicSuite has successfully completed its architectural migration to a strictly decoupled, contract-governed cognitive architecture:
1. **Durable Main Agents & Bounded Specialist Subagents:** 22 persistent cognitive roles defined in `.agents/agents/`, governed by 12-section behavioral contracts (`contract.md`), least-privilege tool whitelists, and native Antigravity orchestration (`invoke_subagent`).
2. **Deterministic Execution Layer ("The Hands"):** 43 production skills in `.agents/skills/` executing verified Python and R scripts on real datasets. LLM mental calculations are strictly forbidden under Constitutional Directive 2.
3. **Artifact-First Communication & State Machine:** Discrete research micro-stages coordinated via strict JSON contract schemas (`contracts/*.schema.json`), producing synchronized on-disk triads (`.docx`, `.md`, `.json`) per Directive 3.
4. **Adversarial Validation & Auditing:** Independent validator engines (`validators/run_all_validators.py`), an active Academic Challenger (`academic-challenger`), an Evidence Auditor (`evidence-auditor`), and an institutional Final Judge (`final-judge`).

The system currently possesses substantial infrastructure for **recording episodic research events, validating outputs, logging pitfalls, and gating human decisions**. However, these systems operate as disjoint safeguards rather than a closed-loop self-improvement subsystem. This document details the precise current state of every component relevant to continuous behavioral evolution.

---

## 2. Agent Inventory & Frontmatter Audit

The repository defines exactly **22 agent packages** in `.agents/agents/`. Each package conforms to Option 1 directory structure (`agent.md` runtime prompt + frontmatter, `contract.md` behavioral contract, `<name>.md` discovery symlink).

### 2.1 Core Primary Roles (Main Agents)
- **`academic-orchestrator`** (`mainAgent: true`, `subagent: false`, `model: pro`):
  - *Tools:* `invoke_subagent`, `manage_subagents`, `send_message`, `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `ask_question`.
  - *Bound Skills:* `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`.
  - *Role:* Master research project conductor, capability resolver, dependency tracker, and stage-gate governor.
- **`academic-writer`** (`mainAgent: false`, `subagent: true`, `model: pro`):
  - *Tools:* `view_file`, `write_to_file`, `list_dir`, `grep_search`, `find_by_name`.
  - *Bound Skills:* `chapter-4-writing`, `persian-literature-review-builder`, `persian-discussion-builder`, `persian-thesis-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `apa-reporting`.
  - *Role:* Defense-ready prose and table generation adhering to Saber's 5-part epistemic paragraph structure.
- **`data-agent`** (`mainAgent: false`, `subagent: true`, `model: pro`):
  - *Tools:* `run_command`, `view_file`, `write_to_file`, `list_dir`, `grep_search`, `find_by_name`.
  - *Bound Skills:* `data-cleaning`, `data-audit`, `psychometric-scale-resolver`, `psychometric-scale-validator`.
  - *Role:* Dataset ingestion, reverse-scoring, missingness diagnosis, and psychometric curation.
- **`statistics-agent`** (`mainAgent: false`, `subagent: true`, `model: pro`):
  - *Tools:* `run_command`, `view_file`, `write_to_file`, `list_dir`, `grep_search`, `find_by_name`.
  - *Bound Skills:* `descriptive-statistics`, `reliability-analysis`, `assumption-testing`, `sem`, `cfa`, `mediation`, `moderation`, `regression`, `statistical-data-analyst`.
  - *Role:* Parametric assumption verification, statistical modeling, and triad data extraction.
- **`research-agent`** (`mainAgent: false`, `subagent: true`, `model: pro`):
  - *Tools:* `view_file`, `write_to_file`, `read_url_content`, `search_web`, `list_dir`, `grep_search`, `find_by_name`.
  - *Bound Skills:* `literature-review`, `methodology-review`, `literature-harvester`, `gpower-sample-size-calculator`.
  - *Role:* Scientific literature harvesting, inverted-triangle problem formulation, and research design.
- **`validation-agent`** (`mainAgent: false`, `subagent: true`, `model: pro`):
  - *Tools:* `run_command`, `view_file`, `write_to_file`, `list_dir`, `grep_search`, `find_by_name`.
  - *Bound Skills:* `thesis-integrity-auditor`, `apa-reporting`.
  - *Role:* Independent verification conductor, invoking deterministic validator suites and grading institutional readiness.

### 2.2 Specialist Domain Roles & Adversarial Critics
- **`academic-challenger`**: Red-teaming subagent. Evaluates candidate analysis plans, tests for p-hacking and specification searching, emits categorical verdicts (`SUPPORTED`, `WEAK`, `CONDITIONAL`, `REJECTED`), and persists findings to `state/pitfalls.jsonl`.
- **`statistical-auditor`**: Adversarial auditor for parametric assumptions, degrees of freedom ($df_{\text{error}} == N - k - 1$), variance deflation, and Multi-Signal Anomaly Index (MSAI).
- **`results-auditor`**: Precision auditor enforcing APA 7th Edition rules, Persian leading zero standard (`۰.۰۰۱ > p`), 3-line table borders, and OMML math preservation.
- **`evidence-auditor`**: Epistemic integrity auditor verifying bidirectional citation-to-bibliography concordance, Irandoc similarity thresholds ($< 20\%$), and robotic AI cliché removal.
- **`final-judge`**: Dissertation defense committee simulator and administrative gatekeeper. Evaluates manuscripts across 5 faculty roles, applies deterministic deductions on the Iranian 0–20 scale, and generates the Human Gate Card for Saber Admin Desk (`124911145`).
- **Additional Specialists (11 roles):** `data-curator`, `digital-saber`, `intervention-designer`, `journal-strategist`, `literature-expert`, `longitudinal-modmed-expert`, `meta-analyst`, `methodology-expert`, `psychometric-expert`, `qualitative-analyst`, `statistical-expert`.

### 2.3 Agent Dependency Graph
The dependency structure is hierarchical, non-circular, and orchestrated exclusively by the primary agent:
```text
                      academic-orchestrator (or digital-saber)
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
RESEARCH TIER               STATISTICS TIER               WRITING TIER
research-agent              data-agent                    academic-writer
├── methodology-expert      ├── data-curator              ├── intervention-designer
├── literature-expert       statistics-agent              └── journal-strategist
├── meta-analyst            ├── statistical-expert
└── qualitative-analyst     ├── psychometric-expert
                            └── longitudinal-modmed-expert
                                   │
                                   ▼
                            VALIDATION TIER
                            validation-agent
                            ├── statistical-auditor
                            ├── results-auditor
                            ├── evidence-auditor
                            ├── academic-challenger
                            └── final-judge
```

---

## 3. Skills & Deterministic Execution Layer ("The Hands")

The repository contains **43 specialized skills** under `.agents/skills/`. Each skill includes a standardized `SKILL.md` (capped at 500 lines / 40 KB under Directive 18) and a `scripts/` directory containing executable Python or R tools.

### 3.1 Execution Invariant
The LLM does not perform mental calculations. Subagents execute CLI scripts via `run_command`, writing structured JSON artifacts to disk:
$$\text{Subagent (LLM)} \xrightarrow{\text{reads spec}} \text{Skill Script (Python/R)} \xrightarrow{\text{writes}} \text{Structured JSON Artifact} \xrightarrow{\text{extracts}} \text{Triad Deliverables}$$

### 3.2 Key Execution Scripts
- `psychology_stats.py`: Comprehensive parametric tests (t-tests, ANOVA, ANCOVA, regression).
- `run_sem.py` / `run_sem.R`: Structural Equation Modeling with lavaan/semopy and 11 Hu & Bentler fit indices.
- `run_cfa.py` / `run_cfa.R`: Confirmatory Factor Analysis, factor loadings ($\lambda$), AVE, CR.
- `run_mediation.py`: Preacher & Hayes PROCESS Model 4 with 5,000 percentile bootstrap resamples.
- `candidate_falsifier_engine.py`: Deliberation engine generating competing candidates and logging rejected anti-patterns.
- `academic_state_manager.py`: Strict finite state machine governing milestones and transitions.
- `academic_event_engine.py`: Immutable, append-only event logging in `events.jsonl`.
- `academic_pitfall_registry.py`: Deterministic storage and query retrieval for failure anti-patterns in `pitfalls.jsonl`.

---

## 4. State Machine, Contracts, and Milestone Governance

State governance is divided between project-level directories (`projects/<name>/academic-state/`) and repository-level state (`state/`).

### 4.1 Milestone Lifecycle & State Machine (`scripts/academic_state_manager.py`)
Milestones follow a formal finite state transition graph:
```text
CREATED ──► SCOPED ──► PLANNED ──► READY ──► RUNNING ──► VALIDATING ──► AWAITING_APPROVAL ──► APPROVED ──► SUPERSEDED
                                                │             │                 │
                                                ▼             ▼                 ▼
                                              FAILED        FAILED           REJECTED
                                                │             │                 │
                                                └──────┬──────┘                 │
                                                       ▼                        ▼
                                                 READY / PLANNED         PLANNED / SCOPED
```

### 4.2 The 10 Canonical Milestones
- `M0_INGESTION`: Data Ingestion & Curation (`data-curator`)
- `M1_PROPOSAL`: Research Proposal Formulation (`academic-orchestrator`)
- `M2_LITERATURE_REVIEW`: Literature Review Synthesis (`literature-expert`)
- `M3_DATA_CURATION`: Data Cleaning & Demographics (`data-agent`)
- `M4_DESCRIPTIVES_RELIABILITY`: Descriptives & Scale Reliability (`statistics-agent`)
- `M5_PARAMETRIC_ASSUMPTIONS`: Assumptions & Correlations (`statistics-agent`)
- `M6_MODEL_DELIBERATION`: Candidate Falsification & Model Deliberation (`statistical-expert`)
- `M7_HYPOTHESIS_TESTING`: Deterministic Hypothesis Testing & Triads (`statistics-agent`)
- `M8_DISCUSSION`: Chapter 5 Discussion & Implication Synthesis (`academic-writer`)
- `M9_DEFENSE`: Defense Presentation & Viva Voce Simulation (`final-judge`)

### 4.3 The Contract Framework (`contracts/`)
The system is governed by 10 authoritative Draft-07 JSON schemas in `contracts/`:
1. `analysis_plan.schema.json`: Formal statistical analysis pre-registration.
2. `analysis_candidate.schema.json`: 10-field specification for competing analysis candidates.
3. `execution_manifest.schema.json`: Complete audit record of CLI commands, script hashes, dataset provenance, exit codes, and output artifacts.
4. `artifact_manifest.schema.json`: Cryptographic index of generated artifacts (SHA-256, paths, producers).
5. `milestone_state.schema.json`: State machine snapshot and transition history.
6. `validation_report.schema.json`: Fail-closed 5-tier validation verdict (`PASS`, `FAIL`, `BLOCKED`, `INCOMPLETE`, `UNKNOWN`) with required evidence.
7. `approval.schema.json`: Human-in-the-loop gate record (explicitly forbids default approval).
8. `pitfall.schema.json`: Methodological and statistical anti-pattern schema.
9. `event.schema.json`: 14 canonical lifecycle event types with strict causal timestamps.
10. `teamwork_boundary.schema.json`: Interface contract with native Antigravity Teamwork.

---

## 5. Current Logging, Tracing, and Verification Systems

### 5.1 Event Stream (`scripts/academic_event_engine.py`)
Persists append-only events to `academic-state/events.jsonl` validated against `contracts/event.schema.json`. Canonical event types:
`PROJECT_CREATED`, `MILESTONE_STARTED`, `PLAN_CREATED`, `ARTIFACT_CREATED`, `EXECUTION_STARTED`, `EXECUTION_COMPLETED`, `VALIDATION_STARTED`, `VALIDATION_FAILED`, `CRITIQUE_CREATED`, `REVISION_REQUESTED`, `MILESTONE_APPROVAL_REQUESTED`, `MILESTONE_APPROVED`, `MILESTONE_REJECTED`, `MILESTONE_FAILED`.

### 5.2 Pitfall Registry (`scripts/academic_pitfall_registry.py`)
Persists structured failure anti-patterns in `academic-state/pitfalls.jsonl` conforming to `contracts/pitfall.schema.json`. Categorizes failures into 5 domain classes:
- `methodological`: Design flaws, baseline omission, sampling bias.
- `statistical`: Parametric assumption breaches, p-hacking, incorrect tests.
- `execution`: Script crashes, timeout, missing packages.
- `evidence`: Orphaned citations, ghost references, Irandoc similarity breaches.
- `validation`: Numerical mismatch across Triad, degrees of freedom errors, typography flaws.

### 5.3 Deterministic Validator Suite (`validators/run_all_validators.py`)
Orchestrates 5 specialized validation engines:
1. `data_integrity`: Little's MCAR test, straight-lining detection, Mahalanobis $D^2$ outliers.
2. `numerical_consistency`: Degrees of freedom math ($N - k - 1$), variance deflation, MSAI computation.
3. `statistical_assumptions`: Shapiro-Wilk normality, Levene's test, regression slope homogeneity, VIF.
4. `result_consistency`: Cross-artifact numerical fidelity between `.json`, `.md`, and `.docx`.
5. `reporting_consistency`: Persian leading zero (`۰.۰۰۱`), APA 7 borders, forbidden AI clichés.

### 5.4 Antigravity Lifecycle Hook Gatekeeper (`.agents/verification/transcript_and_rule_guard.py`)
Configured in `.agents/hooks.json` across `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, and `Stop`:
- Enforces raw data immutability (blocks commands modifying `01_raw_inputs/`).
- Enforces English-only ASCII filenames (Directive 6).
- Enforces the Binary Honesty Protocol (first word "Yes" or "No" on compliance inquiries).
- Enforces Multi-Agent Truthfulness (blocks claims of multi-agent workflows if `invoke_subagent` was not physically called).
- Enforces Triad Artifact Invariant (blocks turn if `.docx`, `.md`, or `.json` is missing).
- Enforces Validation Gate (blocks turn if stage validation report is `FAIL`).

### 5.5 Case-Based Reasoning & Memory (`.agents/memory/`)
- `case_memory_engine.py`: Manages 16 historical dissertation cases in `cases/` with vector/keyword similarity retrieval.
- `decision_journal_engine.py`: Logs high-stakes research decisions to `decisions/`.
- `continuous_learning_engine.py`: Prototype 8-stage closed loop that compares AI recommendations against Human Saber's decisions and synthesizes new precedent cases on divergence.

### 5.6 Permanent Evaluation Corpus (`evals/run_eval_suite.py`)
A standalone benchmark runner testing 9 domains (`descriptive`, `reliability`, `regression`, `mediation`, `cfa`, `sem`, `network`, `writing`, `presentation`) against ground-truth datasets and schemas.

---

## 6. Systematic Audit: What Current Implementation Captures vs. Does Not Capture

| Dimension | Capture Status | Current Mechanism / Storage Location | Limitations & Gaps |
| :--- | :--- | :--- | :--- |
| **User corrections** | **PARTIALLY CAPTURED** | `continuous_learning_engine.py` (`record_human_outcome`), `approval.schema.json` (`comments`, `conditions`), `persian-thesis-revision-assistant` | Conversational corrections in chat are trapped in ephemeral `transcript.jsonl`. No automated extraction of user corrections into persistent learning signals. |
| **Agent actions** | **PARTIALLY CAPTURED** | `academic-state/events.jsonl` (14 canonical events), `execution_manifest.schema.json` | Detailed tool arguments, intermediate thinking, and reasoning steps exist only in Antigravity's session transcript; not indexed in project memory. |
| **Agent decisions** | **PARTIALLY CAPTURED** | `.agents/memory/decisions/*.json`, `academic-state/decisions.json`, `analysis_plan.json` | Captures high-stakes methodological choices and pricing; does NOT capture micro-decisions (e.g. prompt phrasing adjustments, table formatting trade-offs). |
| **Tool usage** | **PARTIALLY CAPTURED** | `transcript.jsonl` (tool_calls), `execution_manifest.schema.json` (CLI commands) | Tool usage is captured per-session by Antigravity and audited by hooks; no aggregated tool failure rate or latency telemetry in project state. |
| **Skill usage** | **PARTIALLY CAPTURED** | Pre-Flight Pipeline Declaration, `execution_manifest.schema.json` (`steps[].skill_name`) | Invocations are recorded per milestone step; no repository-level telemetry on skill invocation frequency, success rates, or execution bottlenecks. |
| **Subagent delegation** | **CAPTURED** | `invoke_subagent` logged in `transcript.jsonl`, `contracts/handoff.schema.json`, `execution_manifest.schema.json` | Fully captured in transcript and verified by `transcript_and_rule_guard.py` Stop hook. Handoff payloads are schema-validated. |
| **Artifacts** | **CAPTURED** | `contracts/artifact_manifest.schema.json`, `academic-state/artifacts.json`, `events.jsonl` (`ARTIFACT_CREATED`) | Cryptographic SHA-256 hashes, physical file paths, artifact types, and producer identities are comprehensively tracked. |
| **Validation failures** | **CAPTURED** | `contracts/validation_report.schema.json`, `validators/run_all_validators.py`, `pitfalls.jsonl` | Itemized failure reasons, failing checks, evidence objects, and overall verdicts are deterministically recorded. |
| **Challenger findings** | **CAPTURED** | `candidate_falsifier_engine.py`, `contracts/pitfall.schema.json`, `academic-state/pitfalls.jsonl` | Falsified approaches, detected problems, empirical evidence, and adapted recommendations are persisted with `reusable: true`. |
| **Successful outcomes** | **PARTIALLY CAPTURED** | `validation_report.json` (`PASS`), `MilestoneState.APPROVED`, `approval.schema.json` (`GRANTED`) | Immediate computational and typographical success is captured; external post-defense university examiner acceptance is UNKNOWN / manual. |
| **Failed outcomes** | **CAPTURED** | `MilestoneState.FAILED`, `MilestoneState.REJECTED`, `validation_report.json` (`FAIL`), `pitfalls.jsonl` | Machine and validation failures are strictly recorded; fail-closed transitions prevent advance on failure. |
| **Revision cycles** | **PARTIALLY CAPTURED** | Milestone transition `history` array, `events.jsonl` (`REVISION_REQUESTED`), `contracts/approval.schema.json` | Transition loops (`FAILED -> READY`, `REJECTED -> PLANNED`) are recorded; however, cycle counts, delta changes between revisions, and root causes are not aggregated. |
| **Final user acceptance** | **PARTIALLY CAPTURED** | `contracts/approval.schema.json` (`category: final_dissertation_release`), `final-judge` card | Administrative human sign-off from Saber Admin Desk (`124911145`) is captured; end-client post-submission feedback is UNKNOWN. |
| **Statistical metadata** | **CAPTURED** | `contracts/execution_manifest.schema.json`, `stats_results.json`, `<stage>.json` | Exact CLI command, execution environment, interpreter, dataset SHA-256 fingerprint, degrees of freedom, effect sizes, and fit indices are captured. |

---

## 7. Baseline Conclusion

AcademicSuite contains all the raw data collection, validation, and failure-auditing primitives necessary to support self-improvement. What is missing is the **connective tissue**: an automated subsystem that transforms captured trajectories and failure artifacts into diagnosed root causes, generates candidate behavioral improvements, evaluates them against regression suites, and safely promotes them.
