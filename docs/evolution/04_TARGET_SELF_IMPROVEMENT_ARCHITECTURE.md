# AcademicSuite Target Self-Improvement Architecture: Closed-Loop Behavioral Evolution

**Document Version:** 1.0.0  
**Specification Date:** September 2026 (1405 SH)  
**Status:** Target Conceptual Architecture Specification (DO NOT IMPLEMENT YET)  
**Core Invariant:** Decouple Raw Experience, Persistent Knowledge, Active Behavior, Candidate Improvements, Evaluation, and Promotion into distinct physical storage boundaries. Never collapse these into a single memory directory.

---

## 1. Architectural Philosophy & Conceptual Cycle

The self-improvement subsystem transforms AcademicSuite from a static rule-following framework into a **self-calibrating cognitive architecture** that learns from research execution, validation failures, adversarial challenges, and human supervisory feedback.

The architecture strictly adheres to the 6-stage closed-loop progression:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. EXPERIENCE                                                               │
│    Capture raw interaction trajectories, execution logs & validation results │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. DIAGNOSIS                                                                │
│    Adversarial root-cause analysis: Attribute failures to prompt, code, data │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. KNOWLEDGE                                                                │
│    Consolidate into persistent memory: Pitfalls, precedents & heuristics     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. CANDIDATE IMPROVEMENT                                                    │
│    Formulate bounded, staged modifications to prompts, skills, or rules     │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. EVALUATION                                                               │
│    Deterministic regression benchmarks, adversarial red-teaming & invariants│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. PROMOTION                                                                │
│    Fail-closed Human Gate sign-off, atomic deployment & rollback snapshots   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Strict Physical Separation of Architectural Domains

To prevent memory pollution, accidental contamination of active behavior, and loss of auditability, the architecture enforces **six distinct physical storage domains**:

```
AcademicSuite/
│
├── [DOMAIN 1: RAW EXPERIENCE] (Immutable, Append-Only Telemetry)
│   ├── state/experience/
│   │   ├── trajectories/             <- Reconstructed tool call & action sessions (.jsonl)
│   │   ├── execution_manifests/      <- Serialized CLI execution records (.json)
│   │   ├── validation_reports/       <- Historical validation verdicts (.json)
│   │   └── user_feedback/            <- Structured human corrections & overrides (.json)
│   └── projects/*/academic-state/
│       └── events.jsonl              <- Project-level causal event stream
│
├── [DOMAIN 2: PERSISTENT LEARNED KNOWLEDGE] (Curated Memory & Precedents)
│   ├── .agents/memory/
│   │   ├── cases/                    <- Curated research cases (CaseMemoryEngine)
│   │   ├── decisions/                <- Auditable high-stakes decisions (DecisionJournalEngine)
│   │   └── heuristics/               <- Calibrated domain heuristics & rule weights (.json)
│   └── state/
│       └── pitfalls.jsonl            <- Canonical failure anti-patterns (AcademicPitfallRegistry)
│
├── [DOMAIN 3: ACTIVE BEHAVIOR] (Live Production Execution - Strictly Protected)
│   ├── .agents/agents/               <- 22 production agent definitions (agent.md, contract.md)
│   ├── .agents/skills/               <- 43 production skills (SKILL.md, scripts/)
│   ├── .agents/rules/                <- Production constitutional rules (AGENTS.md)
│   └── validators/                   <- 5 deterministic validator engines
│
├── [DOMAIN 4: CANDIDATE IMPROVEMENTS] (Staged, Unpromoted Mutations)
│   └── evolution/candidates/
│       ├── CAND-2026-001/
│       │   ├── manifest.json         <- Metadata: author agent, target defect, pitfall reference
│       │   ├── diffs/                <- Proposed unified diffs against active behavior
│       │   └── staged/               <- Isolated copies of proposed agent.md or skill scripts
│
├── [DOMAIN 5: EVALUATION] (Benchmark Results & Verification Reports)
│   └── evolution/evaluations/
│       ├── EVAL-2026-001/
│       │   ├── regression_report.json<- Results from evals/run_eval_suite.py (all 9 domains)
│       │   ├── defect_test.json      <- Verification that the original failure is fixed
│       │   ├── challenger_score.json <- Adversarial red-team verdict from academic-challenger
│       │   └── evaluation_verdict.json<- Composite PASS / FAIL recommendation
│
└── [DOMAIN 6: PROMOTION] (Governance, Gate Cards & Rollback Snapshots)
    └── evolution/promotions/
        ├── promotion_ledger.jsonl    <- Immutable record of all promoted changes
        ├── approvals/                <- Signed approval contracts (Saber Admin Desk 124911145)
        └── snapshots/                <- Pre-promotion rollback tarballs of active behavior
```

---

## 3. Detailed Specification of the 6 Stages

### Stage 1: EXPERIENCE (Raw Capture & Ingestion)
- **Goal:** Faithfully record what happened during research execution without filtering or interpretation.
- **Physical Integration:**
  - `PostToolUse` and `Stop` hooks in `.agents/hooks.json` stream tool calls, script arguments, and exit statuses into `state/experience/trajectories/`.
  - `AcademicEventEngine` records lifecycle events into `events.jsonl`.
  - `statistical_pipeline_engine.py` serializes `execution_manifest.json` with dataset hashes and execution timing.
  - `validators/run_all_validators.py` outputs `validation_report.json`.
  - Human supervisor corrections are ingested via `continuous_learning_engine.py` or `admin_desk.py` into `state/experience/user_feedback/`.
- **Invariants:**
  - Strictly read-only to active agents; append-only storage.
  - Every experience record is cryptographically indexed (SHA-256) and timestamped.

---

### Stage 2: DIAGNOSIS (Adversarial Root-Cause Analysis)
- **Goal:** Analyze experience artifacts to determine *why* a failure occurred and attribute the failure to a concrete root cause.
- **Participating Agents:**
  - `academic-challenger`: Analyzes methodological, sampling, and design errors.
  - `statistical-auditor`: Analyzes assumption violations, degrees of freedom math, and variance deflation.
  - `results-auditor`: Analyzes APA 7 table formatting and Persian typography errors.
  - `evidence-auditor`: Analyzes citation discordance and Irandoc similarity breaches.
- **Root-Cause Attribution Taxonomy:**
  1. `PROMPT_DEFICIT`: Agent system prompt lacked explicit guidance or constraint weighting.
  2. `SKILL_SCRIPT_DEFICIT`: Python/R deterministic script contained a bug, missing edge-case logic, or incorrect formatting regex.
  3. `HEURISTIC_MISMATCH`: Statistical decision rule contradicted modern psychometric standards (e.g. attempting stepwise regression).
  4. `DATA_ANOMALY`: Extreme empirical distribution (e.g. extreme skewness, severe multicollinearity) requiring fallback modeling.
  5. `CONTEXT_DEGRADATION`: Agent suffered from instruction drift due to token context saturation.
- **Deliverable:** Structured `diagnostic_report.json` detailing the root cause, failing artifact, implicated rule, and hypothesized corrective mechanism.

---

### Stage 3: KNOWLEDGE (Memory Consolidation)
- **Goal:** Synthesize diagnosed insights into durable, queryable knowledge representations.
- **Storage Subsystems:**
  - **Negative Knowledge (Anti-Patterns):** Stored in `state/pitfalls.jsonl` via `AcademicPitfallRegistry`. Records what failed, what evidence proved it failed, and what approach must NOT be repeated (`reusable: true`).
  - **Positive Precedents:** Stored in `.agents/memory/cases/` via `CaseMemoryEngine`. Records successful, validated research designs with high confidence weights.
  - **Decision Rationales:** Logged in `.agents/memory/decisions/` via `DecisionJournalEngine`. Records high-stakes trade-offs and human gate decisions.
  - **Calibrated Heuristics:** Stored in `.agents/memory/heuristics/*.json`. Encodes quantitative adjustment rules (e.g. revised sample size cutoffs for Johnson-Neyman floodlight probing).

---

### Stage 4: CANDIDATE IMPROVEMENT (Isolated Staging)
- **Goal:** Formulate an explicit, testable mutation to active behavior designed to eliminate a diagnosed root cause.
- **Physical Isolation:** Staged exclusively under `evolution/candidates/<candidate-id>/`.
- **Allowed Candidate Types:**
  1. `PROMPT_MUTATION`: A proposed patch to `.agents/agents/<role>/agent.md` (e.g. clarifying Persian leading zero rules or adding negative examples).
  2. `SKILL_ENHANCEMENT`: A proposed bugfix or refinement to `.agents/skills/<skill>/scripts/<script>.py`.
  3. `HEURISTIC_UPDATE`: A proposed modification to a decision tree rule in `.agents/reasoning/`.
- **Candidate Manifest (`manifest.json`):**
  - `candidate_id`: e.g. `CAND-2026-CH4-TYPO-001`.
  - `target_pitfall_id`: Reference to the diagnosed pitfall in `state/pitfalls.jsonl`.
  - `target_component`: Path to the active behavior component targeted for modification.
  - `author_agent`: Diagnostician agent that formulated the candidate.
  - `hypothesized_effect`: Concrete measurable outcome expected (e.g. "Eliminates 100% of missing leading zero errors in Chapter 4 tables").
  - `risk_assessment`: Potential side-effects on other workflows.

---

### Stage 5: EVALUATION (Deterministic Benchmarking & Adversarial Red-Teaming)
- **Goal:** Rigorously verify that the candidate improvement fixes the targeted defect **WITHOUT causing regressions** in any existing capability.
- **The Four Evaluation Gates:**
  1. **Gate 1: Targeted Defect Verification:** Re-executes the exact scenario that triggered the original failure using the candidate component. Must produce a 100% `PASS` verdict.
  2. **Gate 2: Permanent Regression Suite:** Executes `evals/run_eval_suite.py` across all 9 domains (`cfa`, `descriptive`, `mediation`, `network`, `presentation`, `regression`, `reliability`, `sem`, `writing`). **Invariant: Exactly ZERO test failures permitted.**
  3. **Gate 3: Adversarial Red-Teaming:** `academic-challenger` stress-tests the candidate with edge-case inputs (e.g. boundary sample sizes, non-normal distributions) to detect gaming or fragility.
  4. **Gate 4: Constitutional Invariance Audit:**
     - Directive 0: Binary Honesty Protocol compliance.
     - Directive 3: Triad Artifact Invariant (.docx + .md + .json).
     - Directive 4: APA 7 & Persian leading zero typography.
     - Directive 6: English-only ASCII filenames.
     - Directive 18: Skill size ceilings (max 500 lines, 40 KB via `skill_size_guard.py`).
- **Deliverable:** `evolution/evaluations/<eval-id>/evaluation_verdict.json` containing complete empirical evidence.

---

### Stage 6: PROMOTION (Gated Deployment & Rollback)
- **Goal:** Safely deploy an evaluated candidate into production active behavior, with fail-closed security and instant rollback capability.
- **Fail-Closed Human Gate:**
  - Promotion CANNOT occur autonomously.
  - Requires explicit review and sign-off by **Saber Ghaderi's Admin Desk (`124911145`)** via `contracts/approval.schema.json`.
  - The agent generates the Human Promotion Card detailing:
    - Target component and unified diff.
    - Diagnosed pitfall resolved.
    - Evaluation benchmark results (100% regression pass rate).
    - Adversarial red-team sign-off.
- **Atomic Promotion Procedure:**
  1. Create a pre-promotion snapshot of target components in `evolution/promotions/snapshots/`.
  2. Apply the validated diff/file atomically to `.agents/agents/` or `.agents/skills/`.
  3. Append an entry to `evolution/promotions/promotion_ledger.jsonl` with git commit hash, timestamp, and approver signature.
  4. Execute an immediate smoke test (`run_tests.py`) to confirm repository health.
  5. If any test fails: **Atomic Rollback** restores the snapshot immediately.

---

## 4. Architectural Safeguards: Preventing Runaway & Degraded Behavior

| Threat | Architectural Safeguard |
| :--- | :--- |
| **Instruction Drift / Degraded Prompts** | Any candidate prompt modification must pass the permanent 9-domain evaluation suite with zero regressions. Prompts that degrade benchmark scores are permanently rejected. |
| **Autonomous Self-Modification Loop** | Agents are strictly forbidden from writing directly to active behavior (`.agents/agents/`, `.agents/skills/`). All candidate changes are staged in `evolution/candidates/` and require Human Gate clearance. |
| **Context Saturation (Skill Bloat)** | `skill_size_guard.py` enforces Directive 18 (max 500 lines / 40,000 bytes) during evaluation. Skills that exceed single-view limits cannot be promoted. |
| **Deceptive Evaluation Claims** | `validation_report.schema.json` structurally forbids a `PASS` verdict unless affirmative evidence items are present. Machine hooks in `transcript_and_rule_guard.py` verify that evaluation scripts physically ran. |
| **Sole Orchestrator Mandate Breach** | Evaluation and self-improvement tasks run as standard, visible Antigravity turns or explicit CLI scripts; no standalone Python agent dispatchers or unmonitored background threads are permitted. |

---

## 5. Summary

The target continuous behavioral self-improvement architecture provides a principled, scientific evolution cycle. By strictly separating **Experience**, **Knowledge**, **Active Behavior**, **Candidates**, **Evaluation**, and **Promotion**, AcademicSuite guarantees that every behavioral improvement is empirically justified, mathematically verified, and institutionally authorized.
