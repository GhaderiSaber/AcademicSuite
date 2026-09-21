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
4. **Component Exclusion & Structural Isolation (`excludeDefaultComponents: true`)**:
   By setting `excludeDefaultComponents: true` across custom agents, agents opt out of default platform prompts (generic developer personas, shell suggestions) and uninvited built-in tools. Each agent sees strictly its declared tools while preserving post-invocation and lifecycle hooks (`hooks.json`), transitioning the architecture from reactive hook interception to structural platform-level containment.

---

## 2. Planar Capability Architecture (6 Operational Planes + 1 Administrative Plane)

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. CONTROL PLANE (Conductor & Strategic Advisors)                       │
│ - academic-orchestrator (Sole Conductor: invoke_subagent, NO write/run) │
│ - methodology-expert (Consultative Advisor: NO delegation, NO write)   │
│ - statistical-expert (Consultative Advisor: NO delegation, NO write)   │
│ - digital-saber (Executive Persona, pricing & high-stakes decisions)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. RESEARCH PLANE (Literature & Epistemic Evidence)                    │
│ - research-agent (Literature synthesis & design worker)                │
│ - literature-expert (Bibliometrics, harvesting & mapping worker)       │
│ - evidence-auditor (Citation & plagiarism critic: NO file write)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. DATA PLANE (Ingestion & Quality Screening)                          │
│ - data-agent (Data screening, reverse-coding, imputation)              │
│ - data-curator (Missing patterns, unengaged filtering, outliers)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. STATISTICS PLANE (Computational Inference & Modeling)               │
│ - statistics-agent (Inferential models, SEM, ANCOVA, RM-ANOVA)         │
│ - psychometric-expert (Scale resolution, CTT, IRT, CFA)                │
│ - longitudinal-modmed-expert (3-wave autoregressive mod-med)           │
│ - qualitative-analyst (Reflexive Thematic Analysis, Grounded Theory)   │
│ - meta-analyst (PRISMA 2020, Cochrane RoB 2, quantitative pooling)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 5. WRITING PLANE (Synthesis & Scholarly Documentation)                 │
│ - academic-writer (Scholarly Persian rhetoric, OpenXML packaging)      │
│ - intervention-designer (Clinical manuals, session worksheets)         │
│ - journal-strategist (Target journal matching, peer review packages)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 6. VALIDATION PLANE (Adversarial Quality Control & Release Gates)      │
│ - validation-agent (Pre-flight release gate, artifact verification)    │
│ - statistical-auditor (MSAI Anomaly Detection, df audit: NO write)     │
│ - results-auditor (APA 7th precision, leading zero: NO write)          │
│ - academic-challenger (Methodology flaws, bias probing: NO write)      │
│ - final-judge (Mock defense committee, release gate: NO write)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 7. ADMINISTRATIVE PLANE (Continuous Learning & Evolution)              │
│ - trajectory-analyzer (Reconstructs observable tool trajectories)      │
│ - behavior-analyst (Root-cause causal diagnosis of agent defects)      │
│ - knowledge-curator (Synthesizes lessons into persistent store)        │
│ - curriculum-builder (Designs graduated challenge benchmarks)          │
│ - skill-evolver (Synthesizes candidate mutations to Skills)            │
│ - evaluation-agent (Independent counterfactual testing harness)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Boundary Specifications by Plane

### Control Plane
- **`academic-orchestrator`**:
  - **CAN**: Decompose multi-chapter thesis pipelines into micro-stages, invoke specialist subagents via `invoke_subagent`, verify triad artifacts (`.docx`, `.md`, `.json`), execute deterministic state manager transitions, emit Stage Completion Reports.
  - **CANNOT**: Hold code execution tools (`run_command`) or file mutation tools (`write_to_file`, `replace_file_content`) under Directive 20. Must coordinate all work via delegation.
- **`methodology-expert` & `statistical-expert` (Advisors)**:
  - **CAN**: Provide domain consultative advice, verify research designs, formulate statistical analysis plans.
  - **CANNOT**: Delegate to subagents (`can_delegate: false`) or mutate files (`can_write_files: false`).
- **`digital-saber`**:
  - **CAN**: Serve as the high-level executive persona of Saber Ghaderi, conduct proposal pricing, authorize client releases, log high-stakes decisions in the Decision Journal (`.agents/memory/decisions/`).
  - **CANNOT**: Bypass stage validation, forge supervisor comments, falsify pricing algorithms.

---

### Research Plane
- **`research-agent` & `literature-expert`**:
  - **CAN**: Query scientific literature databases, extract sample sizes and effect sizes, build Callon co-occurrence maps, generate bibtex/RIS libraries.
  - **CANNOT**: Fabricate sources, compute inferential models.
- **`evidence-auditor` (Critic)**:
  - **CAN**: Reconcile in-text citations against reference libraries, verify external claims via CrossRef/PubMed API, audit Irandoc similarity percentages (< 20%).
  - **CANNOT**: Mutate files on disk (`can_write_files: false`), modify empirical statistical numbers, rewrite methodology designs.

---

### Data Plane
- **`data-agent` & `data-curator`**:
  - **CAN**: Ingest raw datasets, run missing value diagnostics (Little's MCAR), reverse-code validated scales from 4,880 instruments, screen multivariate outliers (Mahalanobis $D^2$).
  - **CANNOT**: Delegate to other agents (`can_delegate: false`), draft chapter narratives, select inferential hypotheses.

---

### Statistics Plane
- **`statistics-agent`**:
  - **CAN**: Execute deterministic Python/R statistical engines (`psychology_stats.py`, Pingouin, Lavaan/SEM, PROCESS bootstrap mediation), generate raw output JSON checkpoints.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`), draft qualitative discussions, approve deliverables.
- **`psychometric-expert`**:
  - **CAN**: Perform Classical Test Theory (CTT), Cronbach's $\alpha$, McDonald's $\omega$, CFA, Item Response Theory (IRT Graded Response Model), ROC curve analysis.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`).
- **`longitudinal-modmed-expert`**:
  - **CAN**: Execute 3-wave longitudinal moderated mediation models with 5,000 bootstrap resamples.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`).
- **`qualitative-analyst`**:
  - **CAN**: Conduct Reflexive Thematic Analysis (Braun & Clarke) and Grounded Theory (Strauss & Corbin), compute inter-coder reliability (Cohen's $\kappa$).
  - **CANNOT**: Delegate to other agents (`can_delegate: false`).
- **`meta-analyst`**:
  - **CAN**: Conduct PRISMA 2020 quantitative synthesis, calculate Hedges' $g$, generate Forest and Funnel plots.
  - **CANNOT**: Delegate to other agents (`can_delegate: false`).

---

### Writing Plane
- **`academic-writer`**:
  - **CAN**: Draft defense-ready thesis chapters using Saber's 5-part epistemic paragraph structure, construct APA 7 markdown tables, apply Persian academic typography, run OpenXML packaging scripts.
  - **CANNOT**: Calculate statistical values in mental memory, forge empirical results, invent citations, pass quality audits on its own drafts, delegate to other agents.
- **`intervention-designer`**:
  - **CAN**: Format standardized evidence-based intervention manuals (ACT, CBT, CFT, Schema Therapy), create session fidelity checklists.
  - **CANNOT**: Execute statistical code (`can_execute_code: false`), delegate to subagents.
- **`journal-strategist`**:
  - **CAN**: Match manuscripts to WoS/Scopus/ISC journal scopes, prepare cover letters and rebuttal response tables.
  - **CANNOT**: Execute code directly, alter empirical dataset findings, delegate to other agents.

---

### Validation Plane (All Critics: Read-Only / No File Mutation)
- **`validation-agent`**:
  - **CAN**: Run full deterministic pre-flight test suites across `.docx`, `.md`, `.json`, issue formal `PASS` / `FAIL` certificates.
  - **CANNOT**: Silently auto-fix failed artifacts without failing the stage gate.
- **`statistical-auditor`**:
  - **CAN**: Compute Multi-Signal Anomaly Index (MSAI), verify degrees of freedom concordance, audit variance deflation ($SD < 0.10 \times \text{Range}$).
  - **CANNOT**: Mutate files on disk (`can_write_files: false`), modify statistical outputs, delegate to workers.
- **`results-auditor`**:
  - **CAN**: Enforce APA 7th Edition numerical formatting, Persian leading zero standard (`۰.۰۰۱`), OMML math equation preservation.
  - **CANNOT**: Mutate files on disk (`can_write_files: false`), execute code (`can_execute_code: false`), delegate to workers.
- **`academic-challenger`**:
  - **CAN**: Adversarially challenge methodology, identify unmeasured confounding, probe $p$-hacking risks and publication bias.
  - **CANNOT**: Mutate files on disk (`can_write_files: false`), issue final acceptance certificates.
- **`final-judge`**:
  - **CAN**: Simulate 5-member dissertation defense committees, generate viva voce challenge cards, enforce institutional acceptance gates.
  - **CANNOT**: Mutate files on disk (`can_write_files: false`), silently modify drafts, override verified statistical violations.

---

### Administrative Plane (Continuous Learning & Evolution)
- **`trajectory-analyzer`**:
  - **CAN**: Reconstruct chronological tool executions, exit codes, and output artifacts strictly from disk logs.
  - **CANNOT**: Write files (`can_write_files: false`), execute code (`can_execute_code: false`), delegate (`can_delegate: false`). Strictly passive forensic read-only observer.
- **`behavior-analyst`**:
  - **CAN**: Perform causal root-cause analysis on diagnosed agent failures, classify behavioral defects.
  - **CANNOT**: Write files (`can_write_files: false`), execute code (`can_execute_code: false`), modify canonical skills directly.
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
