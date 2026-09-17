# Master Academic Orchestrator Architecture

This document specifies the **canonical architecture, decision pipeline, and execution standards** of the **Academic Orchestrator** in the Academic Suite.

---

## 1. Executive Summary & Core Philosophy

The Academic Orchestrator serves as the **master conductor** and cognitive lead for graduate dissertations and academic statistical consultancy.

### Core Architectural Invariants
1. **The Orchestrator Does NOT Contain Every Statistical Method**: The Orchestrator does not embed statistical formulas, regression algorithms, or psychometric calculations in its context.
2. **Skills are the Procedures ("The Method")**: Explicit methodologies, checklists, and commands reside in `.agents/skills/` (< 500 lines, < 40 KB per Directive 18).
3. **Python & R Scripts are the Instruments ("The Hands")**: Deterministic computation is strictly executed via CLI scripts (`python3`, `Rscript`).
4. **Subagents are the Specialist Workers ("The Brains")**: Autonomous domain agents (`data-agent`, `statistics-agent`, `writing-agent`, `validation-agent`, `research-agent`) execute bounded tasks in isolated contexts.
5. **Antigravity is the Sole Conductor (Directive 12.1)**: Orchestration occurs natively through Antigravity's `invoke_subagent` tool. Standalone Python agent dispatchers or loop emulators are strictly prohibited.

---

## 2. The 8-Step Master Decision Pipeline

Every research assignment or pipeline micro-stage progresses through this sequential decision lifecycle:

```text
User Task
   │
   ▼
1. Understand Task ────────────► Deconstruct requirements, degree level, variable topology
   │
   ▼
2. Determine Capabilities ─────► Identify required domain operations (e.g. SEM, APA table)
   │
   ▼
3. Find Suitable Skills ───────► Match capabilities against .agents/skills/ registry
   │
   ▼
4. Select Specialist Agent ────► Choose designated domain role (data, stats, writing, val)
   │
   ▼
5. Delegate (Isolated Context) ─► invoke_subagent with Contractual Delegation Envelope
   │
   ▼
6. Collect Artifacts ──────────► Verify physical Triad Invariant (.docx, .md, .json)
   │
   ▼
7. Adversarial Validation ─────► Route to validation-agent + deterministic validator suite
   │
   ▼
8. Resolve Failures / Synthesize► PASS: Advance stage in academic-state/ & emit report
                                 FAIL: Trigger diagnostic retry loop (max 3 attempts)
```

---

## 3. Capability-to-Skill-to-Agent Registry

The Orchestrator resolves task requirements using the deterministic registry in `scripts/orchestrator_dependency_resolver.py`:

| Capability Key | Domain Scope | Bound Skill | Specialist Agent | Expected Output |
| :--- | :--- | :--- | :--- | :--- |
| `data_cleaning` | Instrument scoring, reverse-coding | `data-cleaning` | `data-agent` | `data_cleaned.xlsx` |
| `data_audit` | Screening unengaged respondents, MCAR | `data-audit` | `data-agent` | `data_quality.json` |
| `descriptive_statistics`| Demographics, $M, SD, SE$, skewness | `descriptive-statistics` | `statistics-agent` | `descriptive.json` |
| `reliability_analysis` | Cronbach's $\alpha$, McDonald's $\omega$ | `reliability-analysis` | `statistics-agent` | `reliability.json` |
| `assumption_testing` | Levene, Shapiro-Wilk, VIF multicollinearity | `assumption-testing` | `statistics-agent` | `assumptions.json` |
| `sem` | SEM path modeling, 11 fit indices | `sem` | `statistics-agent` | `sem.json` |
| `cfa` | Confirmatory Factor Analysis, AVE, CR | `cfa` | `statistics-agent` | `cfa.json` |
| `mediation` | Bootstrap 5,000 resamples, 95% BCa CI | `mediation` | `statistics-agent` | `mediation.json` |
| `moderation` | PROCESS Model 1, simple slopes | `moderation` | `statistics-agent` | `moderation.json` |
| `regression` | Multiple hierarchical regression | `regression` | `statistics-agent` | `regression.json` |
| `apa_reporting` | APA 7 3-line tables, Persian leading zero | `apa-reporting` | `writing-agent` | Table `.docx` + `.md` |
| `chapter_4_writing` | Findings narrative, One-Hypothesis-One-Stage | `chapter-4-writing` | `writing-agent` | Triad artifacts |
| `literature_review` | Theoretical synthesis, empirical tables | `literature-review` | `research-agent` | Chapter 2 draft |
| `methodology_review` | Design validity, G*Power sampling | `methodology-review` | `research-agent` | Chapter 3 draft |
| `validation_audit` | Independent audit of df, data, stats | `thesis-integrity-auditor`| `validation-agent`| `validation_report.json`|

---

## 4. Context Isolation in Antigravity

To preserve context bandwidth and prevent instruction drift across complex theses:
1. **Subagent Context Encapsulation**:
   - Calling `invoke_subagent` spawns a dedicated subagent process with an isolated conversation context.
   - The subagent inherits the workspace path and agent contract, but does **not** inherit redundant parent conversation tokens.
2. **Lean Delegation Envelopes**:
   - The Orchestrator passes only:
     - Assigned Role
     - Stage Identifier
     - Required Skill path (`view_file` mandate)
     - Physical input artifact path in `academic-state/`
     - Bounded task instructions
3. **Lightweight Handoff Returns**:
   - The subagent returns a concise JSON pointer upon completion, directing the Orchestrator to inspect disk artifacts in `academic-state/`.
4. **Antigravity Native Teamwork Modes**:
   - For long-running or multifaceted tasks, recommend `/boost` (multi-perspective verification) or `/teamwork-preview` (multi-agent autonomous team coordination).

---

## 5. Artifact Dependency Graph & Prerequisite Checking

No stage may execute until its input dependencies are verified on disk. The dependency graph enforced by `scripts/orchestrator_dependency_resolver.py` is:

```
[Raw Data on Disk]
       │
       ▼
00_data_curation ──► Produces data_cleaned.xlsx & data_quality.json
       │
       ├────────────────────────┬────────────────────────┐
       ▼                        ▼                        ▼
01_demographics          02_reliability          03_parametric_assumptions
       │                        │                        │
       └────────────────────────┴────────────────────────┘
                                │
                                ▼
                    04_bivariate_correlations
                                │
                                ▼
                          05_macro_model
                                │
       ┌────────────────────────┴────────────────────────┐
       ▼                                                 ▼
06_hypothesis_1 ... 06_hypothesis_k               07_mediation_paths
       │                                                 │
       └────────────────────────┬────────────────────────┘
                                │
                                ▼
                       08_chapter_summary
                                │
                                ▼
                      09_validation_audit
                                │
                                ▼
                       10_chapter_assembly
```

Before delegating any stage, run:
```bash
python3 scripts/orchestrator_dependency_resolver.py check-prerequisites <stage_id> --state-dir <path>
```

---

## 6. Failure Resolution & Retry Budget Protocol

When `validation-agent` or deterministic validators emit `FAIL`:
1. **Failure Diagnosis**:
   - Parse exact failed validator checks (e.g. degrees of freedom mismatch, Shapiro-Wilk violation, table missing leading zero).
2. **Retry Budget Enforcement**:
   - Maximum **3 retries** per micro-stage.
   - If 3 retries are exhausted without a `PASS` verdict, execution halts and escalates to the user / Saber Admin Desk (`124911145`).
3. **Targeted Re-Delegation**:
   - Re-delegate only to the responsible agent with specific diagnostic error instructions.
   - Do not re-run previously validated stages.
4. **Audit Logging**:
   - Record retry attempts and remediation rationales in `academic-state/decisions.json` via `academic_state_manager.py record-decision`.

---

## 7. Interactive Stage-Gate Release (Directive 11)

At the completion of each micro-stage:
1. Advance the stage gate:
   ```bash
   python3 scripts/academic_state_manager.py set-stage <path> --stage <next_stage> --status in_progress
   ```
2. Emit the **Stage Completion Report**:
   - What Was Done (agent invoked, scripts run, exact statistics verified, disk artifacts produced).
   - What Will Be Done Next (next stage, assigned agent, prerequisites).
3. **STOP and await explicit user confirmation** before initiating the next stage.
