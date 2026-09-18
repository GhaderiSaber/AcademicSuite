# AcademicSuite Authoritative Target Architecture (04_TARGET_ARCHITECTURE.md)

**Document Version:** 1.0.0  
**Status:** AUTHORITATIVE TARGET ARCHITECTURE SPECIFICATION  
**Operative Temporal Reality:** 2026 (1405 SH)  
**Execution Mode:** Read-Only Design (Pre-Migration)  

---

## 1. Executive Summary & Paradigm Shift

The AcademicSuite repository is transitioning from a largely flat, partially redundant collection of 22 subagents and shadow Python orchestration scripts into an authoritative, hierarchical **4-Layer Cognitive Architecture** native to Google Antigravity.

### 1.1 The Four Distinct Layers

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: DURABLE ACADEMIC SUITE AGENTS (7 ROLES)                                             │
│ Persistent primary contexts holding domain authority, high-level reasoning, and governance.│
│ • digital-saber (Principal & Twin)        • academic-orchestrator (Conductor)                │
│ • methodology-expert                      • statistical-expert                               │
│ • academic-writer                         • evidence-auditor                                 │
│ • final-judge                                                                               │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │ Delegates bounded subtasks via invoke_subagent
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: BOUNDED SPECIALIST SUBAGENTS (15 ROLES)                                            │
│ Task-bounded, stateless or ephemeral workers executing narrow domain operations.           │
│ • research-agent          • literature-expert         • journal-strategist                  │
│ • meta-analyst            • data-agent                • data-curator                        │
│ • statistics-agent        • psychometric-expert       • longitudinal-modmed-expert          │
│ • intervention-designer   • qualitative-analyst       • validation-agent                    │
│ • results-auditor         • statistical-auditor       • academic-challenger (NEW)           │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │ Invokes domain capability procedures
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: REUSABLE SKILLS (43 STANDARDIZED SKILLS)                                           │
│ Modular procedural knowledge, runbooks, schemas, and templates ("The Runbooks").            │
│ Strictly stateless, single-view compliant (<= 500 lines, <= 40 KB), zero orchestration.     │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │ Executes deterministic command-line tools
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 4: DETERMINISTIC EXECUTION SCRIPTS & TOOLS ("THE HANDS")                              │
│ Python, R, and OpenXML scripts executing matrix math, psychometrics, and document assembly. │
│ Zero mental hallucination; exact numeric extraction into structured JSON and DOCX triads.   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Architectural Principles & Invariants

### 2.1 Principle of Decoupled Epistemic Reasoning vs. Deterministic Execution
A foundational flaw identified in the baseline audit is the blurring of roles where statistical reasoning agents attempt to execute ad-hoc python scripts or calculate numbers mentally, while execution scripts embed workflow logic.
Under the target architecture:
1. **The Expert Brains (Layer 1)**: Decide **WHAT** must be done.
   - `statistical-expert` determines statistical tests, assumption sequences, and model architectures.
   - `methodology-expert` determines research design, threats to validity, and sampling power.
   - `academic-writer` determines narrative rhetoric, epistemic paragraph structure, and thesis synthesis.
   - `evidence-auditor` and `final-judge` determine compliance criteria and acceptance standards.
   - **Constraint**: Durable expert agents do NOT act as unrestricted script-running workers.
2. **The Specialist Subagents (Layer 2)**: Execute bounded tasks and invoke specific Skills.
   - `statistics-agent` deterministically executes approved statistical scripts on the verified dataset.
   - `data-agent` executes cleaning, reverse coding, and Little's MCAR diagnostics.
3. **The Deterministic Scripts (Layer 4)**: Strictly perform computation ("The Hands").
   - Extract exact parameters into structured JSON checkpoints. Zero LLM mental math.

### 2.2 Sole Orchestration Mandate (Elimination of Shadow Orchestrators)
- **Native Antigravity Conduction**: All workflow orchestration belongs strictly to Antigravity agents executing native `invoke_subagent`.
- **Prohibition of Skill-Level Orchestrators**: Skills must never own workflows. `academic-suite-orchestrator` is refactored from a 49 KB monolithic script runner into a standardized batch tool executing an explicit pipeline manifest provided by the agent.
- **De-escalation of CLI Routing Scripts**: `scripts/academic_task_router.py` and `scripts/orchestrator_dependency_resolver.py` are relegated to read-only DAG verification utilities ("The Hands"), stripped of simulated agent dispatch logic.

### 2.3 Human Approval as an Explicit State/Event Model
In the legacy implementation, human approval was either assumed (`supervisor_approval = True` by default) or enforced reactively by blocking execution in the Antigravity `Stop` lifecycle hook. 
The target architecture introduces a **Deterministic State-Event Approval Lifecycle**:
1. **Formal Approval States**:
   - `APPROVAL_NOT_REQUIRED`: Routine micro-stages (e.g. data curation, descriptive stats).
   - `APPROVAL_PENDING`: High-stakes inflection points (e.g. pricing, overriding supervisor comments, release of final dissertation).
   - `APPROVAL_GRANTED`: Explicitly affirmed by human PI (via Saber Admin Desk or chat interaction).
   - `APPROVAL_REJECTED`: Explicitly denied; triggers branch rollback.
2. **State Storage**: Approval events are persisted in `academic-state/decisions.json` and `academic-state/project.json` with timestamps, approving identity, and rationale.
3. **Decoupled from Hooks**: Hooks only inspect that physical approval records exist on disk before permitting release; they do not attempt to manage conversational approval state.

### 2.4 The Adversarial Critic Architecture
Generation and validation are strictly separated into adversarial pairs:
- **Generator**: `academic-writer` $\longrightarrow$ **Critics**: `results-auditor` (APA 7, OMML) & `evidence-auditor` (citations, plagiarism).
- **Generator**: `statistics-agent` $\longrightarrow$ **Critic**: `statistical-auditor` (df, assumptions, MSAI).
- **Candidate Defense Presentation** $\longrightarrow$ **Committee**: `final-judge` & `academic-challenger`.

---

## 3. Target Role Taxonomy & Dispositions

### 3.1 Durable AcademicSuite AGENTS (7 Roles)

Durable agents are primary, persistent cognitive authorities. They maintain long-term reasoning context, direct the bounded subagents, and maintain institutional standards.

| Durable Agent | Architectural Scope | Primary Cognitive Mandate | Subagents Governed |
| :--- | :--- | :--- | :--- |
| **`digital-saber`** | Principal Authority / AI Twin | Client intake, case-based memory, pricing in Tomans, executive governance, and final human approval interface. | `academic-orchestrator` |
| **`academic-orchestrator`** | Master Conductor | Decomposes research tasks into DAGs, tracks artifact dependencies, isolates delegation envelopes, coordinates retries. | All 5 Domain Authorities (`methodology-expert`, `statistical-expert`, `academic-writer`, `evidence-auditor`, `final-judge`) |
| **`methodology-expert`** | Research Design Authority | Formulates research questions, experimental/quasi-experimental designs, G*Power sampling, and threats to validity. | `research-agent`, `literature-expert`, `meta-analyst`, `qualitative-analyst`, `intervention-designer`, `academic-challenger` |
| **`statistical-expert`** | Statistical Architecture Authority | Decides statistical testing sequence, parametric assumption hierarchy, and SEM/regression models. | `data-agent`, `data-curator`, `statistics-agent`, `psychometric-expert`, `longitudinal-modmed-expert`, `statistical-auditor`, `academic-challenger` |
| **`academic-writer`** | Master Chapter Drafter & Rhetoric Authority | Persian scholarly rhetoric, 5-part epistemic paragraph structure, OpenXML layout, and dissertation assembly. | `journal-strategist`, `results-auditor`, `validation-agent` |
| **`evidence-auditor`** | Epistemic Integrity Authority | Bidirectional citation-to-bibliography matching, Irandoc similarity compliance (< 20%), ghost citation elimination. | `research-agent`, `literature-expert`, `validation-agent` |
| **`final-judge`** | Defense Committee & Clearance Gatekeeper | Viva Voce oral defense simulation, supervisor comment triage, defense readiness scoring (>= 95%), institutional sign-off. | `evidence-auditor`, `statistical-auditor`, `results-auditor`, `academic-challenger` |

### 3.2 Bounded Specialist SUBAGENTS (15 Roles)

Bounded subagents operate with strict context isolation. They receive a structured Context Delegation Envelope, execute deterministic tools or Skills, emit synchronized disk artifacts, and terminate.

| Subagent | Parent Authority | Operational Mandate |
| :--- | :--- | :--- |
| **`research-agent`** | `methodology-expert` | Scopes literature requirements, extracts empirical parameters (N, design, instruments). |
| **`literature-expert`** | `methodology-expert` | Executes multi-database harvesting (PubMed, CrossRef, SID), constructs bibliometric networks. |
| **`journal-strategist`** | `academic-writer` | Formulates journal submission packages, matches Scopus/WoS journals, drafts cover letters. |
| **`meta-analyst`** | `methodology-expert` | Executes PRISMA 2020 workflows, Cochrane RoB 2 risk of bias, and meta-analytic effect pooling. |
| **`data-agent`** | `statistical-expert` | Ingests raw data, reverse codes Likert items, screens missingness (Little's MCAR), exports cleaned data. |
| **`data-curator`** | `statistical-expert` | Specialized subagent for Mahalanobis D2 multivariate outliers and complex imputation audits. |
| **`statistics-agent`** | `statistical-expert` | Executes deterministic Python/R statistical engines (ANCOVA, regression, mediation, SEM) on verified data. |
| **`psychometric-expert`** | `statistical-expert` | Executes Classical Test Theory (CVR/CVI, EFA, Omega) and Item Response Theory (GRM, ROC curves). |
| **`longitudinal-modmed-expert`** | `statistical-expert` | Executes 3-wave longitudinal moderated mediation models and panel autoregressive baselines. |
| **`intervention-designer`** | `methodology-expert` | Designs standardized evidence-based psychological intervention protocols and clinical session tables. |
| **`qualitative-analyst`** | `methodology-expert` | Executes Braun & Clarke Reflexive Thematic Analysis and Strauss & Corbin Grounded Theory coding. |
| **`validation-agent`** | `academic-writer` | Runs deterministic validator suite on generated artifacts, verifying degrees of freedom and tables. |
| **`results-auditor`** | `academic-writer` | Enforces APA 7 typography, Persian leading zero rule (۰.۰۵), and OpenXML OMML equation formatting. |
| **`statistical-auditor`** | `statistical-expert` | Forensic auditor for parametric assumption violations, degrees of freedom, and MSAI anomaly index. |
| **`academic-challenger`** | `final-judge` | **NEW ROLE**: Adversarial defense examiner and harsh peer reviewer for stress-testing defenses and manuscripts. |

---

## 4. Resolution of Baseline Duplications & Overlaps

1. **`writing-agent` $\longrightarrow$ Consolidated into `academic-writer`**:
   - `writing-agent` was an exact duplicate of `academic-writer`. Under the target architecture, `academic-writer` is designated as the sole Durable Writing Authority. `writing-agent` is deprecated and aliased to `academic-writer`.
2. **`data-curator` $\longrightarrow$ Subagent under `statistical-expert`**:
   - Rather than acting as a parallel independent agent, `data-curator` is retained as a specialized bounded subagent focused strictly on complex outlier diagnostics (Mahalanobis D2, Cook's distance), while `data-agent` handles general ingestion and scale scoring.
3. **`statistics-agent` $\longrightarrow$ Decoupled from `statistical-expert`**:
   - `statistical-expert` is the Durable Authority deciding models and parameters. `statistics-agent` is the bounded execution subagent that deterministically runs the scripts.

---

## 5. Architectural Dataflow & Execution Lifecycle

```
[Client Request] ──► digital-saber (Precedent Retrieval & Scoping)
                             │
                             ▼
                    academic-orchestrator (DAG Resolution & State Initialization)
                             │
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
 methodology-expert                       statistical-expert
 (Design & Power Analysis)                (Model Architecture)
        │                                         │
        ├─► research-agent                        ├─► data-agent (Cleaning & Scoring)
        ├─► literature-expert                     ├─► statistics-agent (Python/R Exec)
        └─► intervention-designer                 └─► statistical-auditor (MSAI Audit)
                                                          │
                                                          ▼
                                                  academic-writer
                                                  (Narrative & APA 7 Drafting)
                                                          │
                                                          ├─► results-auditor
                                                          └─► validation-agent
                                                                  │
                                                                  ▼
                                                             final-judge
                                                  (Viva Voce Defense & Clearance)
                                                                  │
                                                                  ├─► academic-challenger
                                                                  ▼
                                                      [Human Approval Gate]
                                                                  │
                                                                  ▼
                                                      [Deliverable Release]
```

### 5.1 Stage Execution Invariants
1. **Triad Artifact Invariant (Directive 3)**: Every micro-stage must generate `.docx`, `.md`, and `.json` synchronously on disk before proceeding.
2. **One-Hypothesis-One-Stage Invariant (Directive 3)**: Every individual hypothesis in Chapter 4 and Chapter 5 has a dedicated micro-stage triad (`06_hypothesis_1.docx`, `.md`, `.json`).
3. **Interactive Stage-Gate Protocol (Directive 11)**: Conductor halts after each stage report, awaiting explicit human confirmation before dispatching the next stage.
