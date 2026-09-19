# AGENT_CAPABILITY_BOUNDARY.md — Agent Capability Boundaries & Contractual Demarcations

**Document Version:** 1.0.0 (Phase 0 Architecture Freeze)  
**Status:** Canonical V0 Baseline  
**Operative Date:** September 2026 (1405 SH)  
**Governance:** AcademicSuite Constitutional Architecture (Directives 0 through 19)  

---

## 1. Architectural Principles of Capability Demarcation

In AcademicSuite, capability boundaries are established by **three orthogonal mechanisms**:
1. **Behavioral Contracts (`contract.md`)**: A non-negotiable 12-section specification defining `MISSION`, `CAN`, `CANNOT`, `INPUTS`, `OUTPUTS`, `ALLOWED TOOLS`, `REQUIRED SKILLS`, `FORBIDDEN ACTIONS`, `HANDOFF FORMAT`, `VALIDATION REQUIREMENTS`, `COMPLETION CRITERIA`, and `FAILURE CONDITIONS`.
2. **Runtime Tool Declarations (`agent.md` frontmatter)**: The exact subset of Antigravity tools exposed to the agent model at runtime.
3. **The Six-Part Functional Separation Invariant (Directive 19)**:
   - **Agent → decides**: Context reasoning, stage scoping, delegation envelopes, and synthesis.
   - **Skill → instructs**: Procedures, decision trees, APA standards, and OpenXML guidelines.
   - **Script → computes**: Deterministic calculation, data transformation, OpenXML packaging, and cryptographic hashing.
   - **Hook → enforces**: Lifecycle interception, safety gates, and honesty verification (`hooks.json`).
   - **State machine → authorizes transition**: Prerequisite verification and milestone gating (`academic_state_manager.py`).
   - **Artifact manifest → defines completion**: Triad deliverables on disk (`contracts/artifact_manifest.schema.json`).

---

## 2. Five-Tier Capability Hierarchy & Boundary Map

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: MASTER ORCHESTRATION & DIGITAL TWIN                             │
│ - academic-orchestrator (Project lifecycle, micro-stage scoping)       │
│ - digital-saber (Persona, high-stakes decisions, client gate)          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 2: DOMAIN AUTHORITIES (THE ARCHITECTS)                            │
│ - methodology-expert (Research design, sampling power, validity)       │
│ - statistical-expert (Statistical method selection, assumption trees)  │
│ - academic-writer (Scholarly Persian rhetoric, chapter structure)      │
│ - evidence-auditor (Citation reconciliation, Irandoc compliance)       │
│ - final-judge (Mock defense committee, institutional gatekeeper)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 3: SPECIALIST WORKERS ("THE HANDS" COORDINATORS)                  │
│ - data-agent (Data screening, reverse-coding, imputation)              │
│ - data-curator (Missing patterns, unengaged filtering, outliers)       │
│ - statistics-agent (Inferential models, SEM, ANCOVA, RM-ANOVA)         │
│ - psychometric-expert (Scale resolution, CTT, IRT, CFA)                │
│ - research-agent (Literature harvesting, PICO, question design)        │
│ - literature-expert (Science mapping, bibliometrics, Callon maps)      │
│ - intervention-designer (Clinical manuals, session worksheets)         │
│ - qualitative-analyst (Reflexive Thematic Analysis, Grounded Theory)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 4: ADVERSARIAL REVIEWERS & CRITICS                                │
│ - statistical-auditor (MSAI Anomaly Detection, df concordance)         │
│ - results-auditor (APA 7th precision, leading zero, OMML math)        │
│ - academic-challenger (Methodology flaws, p-hacking, bias probing)     │
│ - journal-strategist (Target journal matching, peer review rebuttal)   │
│ - meta-analyst (PRISMA 2020, Cochrane RoB 2, quantitative pooling)     │
│ - longitudinal-modmed-expert (3-wave autoregressive mod-med)           │
│ - validation-agent (Pre-flight release gate, artifact verification)    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 5: CONTINUOUS LEARNING & BENCHMARKING SUBAGENTS                   │
│ - trajectory-analyzer (Reconstructs observable tool trajectories)      │
│ - behavior-analyst (Root-cause causal diagnosis of agent defects)      │
│ - knowledge-curator (Synthesizes lessons into persistent store)        │
│ - curriculum-builder (Designs graduated challenge benchmarks)          │
│ - skill-evolver (Synthesizes candidate mutations to Skills)            │
│ - evaluation-agent (Independent counterfactual testing harness)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Boundary Specifications by Tier

### Tier 1: Master Orchestrators
- **`academic-orchestrator`**:
  - **CAN**: Decompose multi-chapter thesis pipelines into micro-stages, invoke specialist subagents via `invoke_subagent`, verify triad artifacts (`.docx`, `.md`, `.json`), execute deterministic state manager transitions, emit Stage Completion Reports.
  - **CANNOT**: Perform statistical computation in mental memory, draft long narrative text directly, perform raw data screening directly, pass final dissertation grades.
  - **Constitutional Conflict**: Possesses `run_command` in frontmatter. In V0 baseline, this causes the orchestrator to run Python calculation scripts directly instead of delegating to Tier 3 specialists.

- **`digital-saber`**:
  - **CAN**: Serve as the high-level executive persona of Saber Ghaderi, conduct proposal pricing, authorize client releases, log high-stakes decisions in the Decision Journal (`.agents/memory/decisions/`).
  - **CANNOT**: Bypasses stage validation, forge supervisor comments, falsify pricing algorithms.

---

### Tier 2: Domain Authorities
- **`methodology-expert`**:
  - **CAN**: Formulate research questions, select experimental / quasi-experimental designs, calculate G*Power sample sizes, delegate to `research-agent` and `qualitative-analyst`.
  - **CANNOT**: Perform statistical modeling directly, draft full Chapter 4 findings.

- **`statistical-expert`**:
  - **CAN**: Select appropriate statistical tests, design parametric assumption verification sequences, delegate execution to `statistics-agent`, `psychometric-expert`, `data-agent`.
  - **CANNOT**: Execute code directly (`can_execute_code: false`). Must delegate all computational tasks to workers.
  - **Constitutional Alignment**: Perfect least-privilege alignment. By lacking `run_command`, it cannot bypass workers.

- **`academic-writer`**:
  - **CAN**: Draft defense-ready thesis chapters using Saber's 5-part epistemic paragraph structure, construct APA 7 markdown tables, apply Persian academic typography.
  - **CANNOT**: Calculate statistical values, forge empirical results, invent citations, pass quality audits on its own drafts.

- **`evidence-auditor`**:
  - **CAN**: Reconcile in-text citations against reference libraries, verify external claims via CrossRef/PubMed API, audit Irandoc similarity percentages (< 20%).
  - **CANNOT**: Modify empirical statistical numbers, rewrite methodology designs.

- **`final-judge`**:
  - **CAN**: Simulate 5-member dissertation defense committees, generate viva voce challenge cards, enforce institutional acceptance gates.
  - **CANNOT**: Silently modify drafts, override verified statistical violations.

---

### Tier 3: Specialist Workers
- **`data-agent` & `data-curator`**:
  - **CAN**: Ingest raw datasets, run missing value diagnostics (Little's MCAR), reverse-code validated scales from 4,880 instruments, screen multivariate outliers (Mahalanobis $D^2$).
  - **CANNOT**: Delegate to other agents (`can_delegate: false`), draft chapter narratives, select inferential hypotheses.

- **`statistics-agent`**:
  - **CAN**: Execute deterministic Python/R statistical engines (`psychology_stats.py`, Pingouin, Lavaan/SEM, PROCESS bootstrap mediation), generate raw output JSON checkpoints.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`), draft qualitative discussions, approve deliverables.

- **`psychometric-expert`**:
  - **CAN**: Perform Classical Test Theory (CTT), Cronbach's $\alpha$, McDonald's $\omega$, CFA, Item Response Theory (IRT Graded Response Model), ROC curve analysis.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`).

- **`research-agent` & `literature-expert`**:
  - **CAN**: Query scientific literature databases, extract sample sizes and effect sizes, build Callon co-occurrence maps, generate bibtex/RIS libraries.
  - **CANNOT**: Fabricate sources, compute inferential models.

- **`intervention-designer`**:
  - **CAN**: Format standardized evidence-based intervention manuals (ACT, CBT, CFT, Schema Therapy), create session fidelity checklists.
  - **CANNOT**: Execute statistical code (`can_execute_code: false`), delegate to subagents.

- **`qualitative-analyst`**:
  - **CAN**: Conduct Reflexive Thematic Analysis (Braun & Clarke) and Grounded Theory (Strauss & Corbin), compute inter-coder reliability (Cohen's $\kappa$).
  - **CANNOT**: Delegate to subagents.

---

### Tier 4: Adversarial Reviewers & Critics
- **`statistical-auditor`**:
  - **CAN**: Compute Multi-Signal Anomaly Index (MSAI), verify degrees of freedom concordance, audit variance deflation ($SD < 0.10 \times \text{Range}$).
  - **CANNOT**: Modify statistical outputs, delegate to workers.

- **`results-auditor`**:
  - **CAN**: Enforce APA 7th Edition numerical formatting, Persian leading zero standard (`۰.۰۰۱`), OMML math equation preservation.
  - **CANNOT**: Execute code (`can_execute_code: false`), delegate to workers.

- **`validation-agent`**:
  - **CAN**: Run full deterministic pre-flight test suites across `.docx`, `.md`, `.json`, issue formal `PASS` / `FAIL` certificates.
  - **CANNOT**: Silently auto-fix failed artifacts without failing the stage gate.

- **`academic-challenger`**:
  - **CAN**: Adversarially challenge methodology, identify unmeasured confounding, probe $p$-hacking risks and publication bias.
  - **CANNOT**: Issue final acceptance certificates.

- **`journal-strategist`**:
  - **CAN**: Match manuscripts to WoS/Scopus/ISC journal scopes, prepare cover letters and rebuttal response tables.
  - **CANNOT**: Alter empirical dataset findings.

- **`meta-analyst`**:
  - **CAN**: Conduct PRISMA 2020 quantitative synthesis, calculate Hedges' $g$, generate Forest and Funnel plots.
  - **CANNOT**: Delegate to other agents.

- **`longitudinal-modmed-expert`**:
  - **CAN**: Execute 3-wave longitudinal moderated mediation models with 5,000 bootstrap resamples.
  - **CANNOT**: Delegate to other agents.

---

### Tier 5: Continuous Learning Subagents
- **`trajectory-analyzer`**:
  - **CAN**: Reconstruct chronological tool executions, exit codes, and output artifacts strictly from disk logs.
  - **CANNOT**: Write files (`can_write: false`), execute code (`can_execute_code: false`), delegate (`can_delegate: false`). Strictly passive forensic read-only observer.

- **`behavior-analyst`**:
  - **CAN**: Perform causal root-cause analysis on diagnosed agent failures, classify behavioral defects.
  - **CANNOT**: Execute code (`can_execute_code: false`), modify canonical skills directly.

- **`knowledge-curator`**:
  - **CAN**: Synthesize episodic failures and exemplars into structured knowledge items and anti-patterns (`state/pitfalls.jsonl`).
  - **CANNOT**: Directly promote candidate mutations to production skills.

- **`curriculum-builder`**:
  - **CAN**: Design graduated benchmark scenarios and challenge datasets targeting diagnosed agent defects.
  - **CANNOT**: Execute code (`can_execute_code: false`).

- **`skill-evolver`**:
  - **CAN**: Generate candidate diffs to Skills and behavioral prompts in staging sandboxes (`learning/candidates/`).
  - **CANNOT**: Overwrite production skills in `.agents/skills/` without formal evaluation gate approval.

- **`evaluation-agent`**:
  - **CAN**: Run deterministic evaluation test suites against candidate mutations, benchmark zero regressions.
  - **CANNOT**: Propose candidate diffs (maintains separation between generation and evaluation).

---

## 4. Identified Capability Leaks & Boundary Failures in V0

During the Phase 0 baseline evaluation, three critical architectural boundary defects were uncovered:

1. **The Orchestrator's Code Execution Leakage**:
   - `academic-orchestrator` has `run_command` in its allowed tools.
   - When requested to *"Analyze this dataset"* (Task 1) or *"Calculate repeated-measures"* (Task 2), the LLM bypassed both `data-agent` and `statistics-agent`, writing and executing ad-hoc Python scripts in its own process.
   - **Remediation Requirement**: Strip `run_command` and `write_to_file` from `academic-orchestrator` or enforce a strict lifecycle hook blocking orchestrator computation scripts.

2. **Delegation Inconsistency**:
   - For writing and validation tasks (Task 3), `academic-orchestrator` correctly dispatched `academic-writer` and `validation-agent`.
   - For analytical and computational tasks (Tasks 1 & 2), the orchestrator failed to delegate, proving that delegation behavior currently depends on prompt heuristics rather than architectural constraints.

3. **Subagent Polling Anti-Pattern**:
   - When delegating to `academic-writer`, `academic-orchestrator` repeatedly called `manage_subagents(Action="list")` in a busy-wait loop (Steps 13, 15, 17 in Task 3) instead of stopping its turn and allowing Antigravity's reactive message wakeup mechanism to resume execution.
