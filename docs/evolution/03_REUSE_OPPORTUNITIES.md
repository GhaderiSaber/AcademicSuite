# AcademicSuite Reuse Opportunities: Leveraging Existing Infrastructure for Self-Improvement

**Document Version:** 1.0.0  
**Audit Date:** September 2026 (1405 SH)  
**Status:** Approved Architectural Inventory  
**Core Principle:** Build the self-improvement subsystem by composing and extending verified existing machinery, avoiding redundant code, duplicate schemas, or parallel state stores.

---

## 1. Executive Summary

A critical strength of the AcademicSuite codebase is that **nearly all the low-level primitives required for self-improvement already exist in production**:
- We do NOT need to design a new event logging engine; `AcademicEventEngine` already validates against `contracts/event.schema.json`.
- We do NOT need to invent a failure taxonomy; `AcademicPitfallRegistry` already classifies failures across 5 domain categories.
- We do NOT need to build new evaluators; `validators/run_all_validators.py` and `evals/run_eval_suite.py` already provide deterministic ground-truth verification across 9 academic domains.
- We do NOT need to create a human approval contract; `contracts/approval.schema.json` already enforces human sign-off.

This document details exactly how these existing components can be directly reused to construct the target continuous learning architecture (`EXPERIENCE -> DIAGNOSIS -> KNOWLEDGE -> CANDIDATE IMPROVEMENT -> EVALUATION -> PROMOTION`).

---

## 2. Comprehensive Inventory of Reusable Components

### 2.1 Contracts & Schema Validation (`contracts/`)

| Contract Schema | Existing Production Capability | Reuse in Self-Improvement Architecture |
| :--- | :--- | :--- |
| **`event.schema.json`** | Validates 14 canonical lifecycle event types with monotonic timestamps and provenance. | Reused directly as the immutable spine of **Raw Experience**. Trajectory events (`TRAJECTORY_CAPTURED`, `CANDIDATE_EVALUATED`, `IMPROVEMENT_PROMOTED`) can integrate cleanly into this schema. |
| **`pitfall.schema.json`** | Formally captures defective candidate approaches, problems, empirical evidence, detecting agents, and corrective resolutions with a `reusable` boolean flag. | Reused directly as the persistence format for **Learned Knowledge (Anti-Patterns)**. Reusable pitfalls serve as negative test cases and heuristic constraints. |
| **`validation_report.schema.json`** | 5-tier status taxonomy (`PASS`, `FAIL`, `BLOCKED`, `INCOMPLETE`, `UNKNOWN`) requiring affirmative evidence summaries and check-level itemized results. | Reused directly as the evaluation contract during the **Evaluation** stage. A candidate improvement cannot be promoted unless it produces a `PASS` validation report with zero regressions. |
| **`approval.schema.json`** | Human-in-the-loop gate contract structurally forbidding default approval (`is_approved` cannot be true unless status is `GRANTED` with approver identity). | Reused directly as the mandatory sign-off gate during the **Promotion** stage. Candidate improvements cannot alter production active behavior without human approval. |
| **`execution_manifest.schema.json`** | Full cryptographic audit of execution environment, CLI commands, script hashes, dataset provenance (SHA-256), and produced artifacts. | Reused directly to record execution provenance during candidate benchmark evaluations, ensuring benchmark reproducibility. |
| **`analysis_candidate.schema.json`** | 10-field specification for competing research methodologies. | Reused to formulate candidate methodological hypotheses and competing analytical approaches. |
| **`contract_validator.py`** | Central Python module providing fail-closed Draft-07 JSON validation utilities for all contract types. | Reused to validate all newly created experience, diagnostic, and evaluation artifacts across the self-improvement lifecycle. |

---

## 2.2 Persistent Registries & State Management

### 1. `AcademicPitfallRegistry` (`scripts/academic_pitfall_registry.py`)
- **Existing Functionality:**
  - Manages append-only persistence in `state/pitfalls.jsonl`.
  - Enforces schema validation against `contracts/pitfall.schema.json`.
  - Implements deterministic querying by `category`, `project`, `milestone`, `detected_by`, `reusable`, and text search.
  - Prevents duplicate `pitfall_id` entries.
- **Reuse in Self-Improvement:**
  - Serves as the primary store for **Diagnosed Negative Knowledge**.
  - When `validation-agent` or `academic-challenger` diagnoses a failure, they invoke `AcademicPitfallRegistry.create()`.
  - When candidate improvements are generated, the generator queries `AcademicPitfallRegistry.query(reusable=True)` to ensure the new candidate does not repeat known anti-patterns.

### 2. `AcademicEventEngine` (`scripts/academic_event_engine.py`)
- **Existing Functionality:**
  - Append-only event stream in `academic-state/events.jsonl`.
  - Validates causal monotonic ordering and cryptographic SHA-256 hashes of created artifacts.
  - Provides workflow reconstruction from historical event logs.
- **Reuse in Self-Improvement:**
  - Serves as the authoritative source for **Raw Experience Reconstruction**.
  - Trajectory extraction scripts replay `events.jsonl` to reconstruct the exact sequence of attempts, failures, and revisions.

### 3. `StrictStateMachine` (`scripts/academic_state_manager.py`)
- **Existing Functionality:**
  - Finite state machine governing 10 canonical research milestones (`M0` to `M9`).
  - Tracks transition history, dependencies, input/output artifacts, and approval requirements.
- **Reuse in Self-Improvement:**
  - Can incorporate an optional `EVOLUTION` or `CALIBRATION` milestone phase, or tap milestone completion transitions to trigger background evaluation sweeps.

---

## 2.3 Quality Control, Auditing & Evaluation Engines

### 1. Unified Validator Suite (`validators/run_all_validators.py`)
- **Existing Functionality:**
  - Master runner orchestrating 5 deterministic validator engines:
    1. `data_integrity/validator.py` (Little's MCAR, straight-lining, Mahalanobis $D^2$)
    2. `numerical_consistency/validator.py` (Degrees of freedom, variance deflation, MSAI)
    3. `statistical_assumptions/validator.py` (Normality, homoscedasticity, slope homogeneity, VIF)
    4. `result_consistency/validator.py` (Cross-artifact numerical consistency across Triad)
    5. `reporting_consistency/validator.py` (Persian leading zeros, APA 7 borders, cliches)
  - Emits schema-compliant `validation_report.json`.
- **Reuse in Self-Improvement:**
  - Serves as the **Automated Evaluation Gate** for any candidate improvement targeting writing, reporting, or statistical modeling.
  - Evaluates candidate deliverables generated under modified prompts or scripts to verify that known failure modes are eliminated.

### 2. Permanent Evaluation Runner (`evals/run_eval_suite.py`)
- **Existing Functionality:**
  - Discovers and runs permanent benchmark test cases across 9 domains (`cfa`, `descriptive`, `mediation`, `network`, `presentation`, `regression`, `reliability`, `sem`, `writing`).
  - Evaluates outputs against ground-truth datasets and cutoffs.
  - Supports comparative version benchmarking (v1 vs v2 vs v3).
- **Reuse in Self-Improvement:**
  - Serves as the **Regression Test Suite** for behavioral candidates.
  - Before any candidate prompt, rule, or script change is promoted, `run_eval_suite.py` executes across all 9 domains to ensure **Zero Regressions**.

### 3. Multi-Signal Anomaly Index (`.agents/verification/multi_signal_anomaly_detector.py`)
- **Existing Functionality:**
  - Evaluates datasets and models across 5 anomaly dimensions: effect size plausibility ($d > 1.40$), variance deflation ($SD < 0.10 \times \text{range}$), group overlap, and alpha consistency.
- **Reuse in Self-Improvement:**
  - Acts as an adversarial fitness function: candidate data curation or statistical skills must not inflate MSAI scores.

---

## 2.4 Case-Based Reasoning & Memory Layer (`.agents/memory/`)

### 1. `CaseMemoryEngine` (`.agents/memory/case_memory_engine.py`)
- **Existing Functionality:**
  - Manages a curated library of 16 real-world dissertation cases in `cases/`.
  - Calculates TF-IDF and keyword similarity scores between new proposals and historical precedents.
  - Implements `reinforce_case()` to increase confidence weights on validated decisions.
- **Reuse in Self-Improvement:**
  - Represents the **Persistent Learned Knowledge** store for positive methodological precedents.
  - When an innovative research design is validated and approved, it is synthesized into a new case in `cases/` with high initial confidence.

### 2. `DecisionJournalEngine` (`.agents/memory/decision_journal_engine.py`)
- **Existing Functionality:**
  - Immutable JSON logging of strategic research decisions in `decisions/`.
  - Records context, selected option, rejected alternatives, confidence score, and human gate status.
- **Reuse in Self-Improvement:**
  - Reused to journal **Meta-Decisions** during self-improvement (e.g. decision to adopt a new heuristic, rejection of an unviable candidate prompt).

### 3. `ContinuousLearningEngine` (`.agents/memory/continuous_learning_engine.py`)
- **Existing Functionality:**
  - Implements an 8-stage closed-loop prototype:
    1. Ingest case $\rightarrow$ 2. Retrieve precedents $\rightarrow$ 3. Generate candidate paths $\rightarrow$ 4. Apply Saber reasoning $\rightarrow$ 5. Recommend & journal $\rightarrow$ 6. Record human outcome $\rightarrow$ 7. Compare AI vs Human $\rightarrow$ 8. Update knowledge base.
  - On agreement: reinforces precedent case weights.
  - On divergence: automatically synthesizes a new calibrated case in `.agents/memory/cases/`.
- **Reuse in Self-Improvement:**
  - The algorithmic logic of Stages 6–8 (comparing AI recommendation against human choice, computing congruence, and synthesizing calibrated records) provides the conceptual blueprint for the target architecture's **Diagnosis** and **Knowledge** stages.

---

## 2.5 Lifecycle Enforcement & Machine Guards (`.agents/verification/`)

### 1. `transcript_and_rule_guard.py`
- **Existing Functionality:**
  - Python engine executed by Antigravity lifecycle hooks (`.agents/hooks.json`).
  - PreInvocation: Injects ephemeral constitutional reminders.
  - PreToolUse / PostToolUse: Enforces raw data immutability and English-only ASCII filenames.
  - Stop: Audits transcript for Binary Honesty Protocol and multi-agent truthfulness; audits disk for Triad Artifact Invariant and passing validation reports.
- **Reuse in Self-Improvement:**
  - Reused as the **Machine Gatekeeper** protecting active production behavior.
  - Can inspect candidate promotion packages at the `Stop` hook to guarantee that no un-evaluated candidate files have modified production `agent.md` or `contract.md` files.

### 2. `skill_size_guard.py`
- **Existing Functionality:**
  - Audits all `SKILL.md` files against Directive 18 single-view ceilings (max 500 lines, 40,000 bytes).
- **Reuse in Self-Improvement:**
  - Reused to ensure that candidate skill extensions never violate context budget constraints.

---

## 3. Reuse Matrix Across the 6-Stage Target Architecture

| Target Architecture Stage | Primary Reused Components | Reused Artifacts & Schemas |
| :--- | :--- | :--- |
| **1. EXPERIENCE** | `transcript_and_rule_guard.py` (`PostToolUse`), `AcademicEventEngine`, `StrictStateMachine` | `events.jsonl`, `execution_manifest.json`, `transcript.jsonl` |
| **2. DIAGNOSIS** | `validators/run_all_validators.py`, `AcademicChallenger`, `statistical-auditor` | `validation_report.json`, `pitfalls.jsonl`, `contracts/pitfall.schema.json` |
| **3. KNOWLEDGE** | `AcademicPitfallRegistry`, `CaseMemoryEngine`, `DecisionJournalEngine` | `state/pitfalls.jsonl`, `cases/*.json`, `decisions/*.json` |
| **4. CANDIDATE IMPROVEMENT** | `CandidateDeliberationEngine`, `contracts/analysis_candidate.schema.json` | `candidate_spec.json`, staged prompt diffs |
| **5. EVALUATION** | `evals/run_eval_suite.py`, `validators/run_all_validators.py`, `final-judge` | `evals/eval_schema.json`, `validation_report.json`, benchmark scorecards |
| **6. PROMOTION** | `contracts/approval.schema.json`, `admin_desk.py`, `transcript_and_rule_guard.py` | `approval.json`, Human Gate Cards, Git commit hooks |

---

## 4. Summary: Zero Unnecessary Machinery

By systematically leveraging the 9 components above, the self-improvement subsystem can be introduced **with zero modifications to production execution pipelines**. Every requirement of self-improvement—telemetry, failure categorization, regression testing, and gated sign-off—is anchored in proven, existing code.
