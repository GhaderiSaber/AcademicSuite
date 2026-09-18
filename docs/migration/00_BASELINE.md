# AcademicSuite Migration Baseline (00_BASELINE.md)

**Document Version:** 1.0.0  
**Status:** READ-ONLY BASELINE AUDIT COMPLETE  
**Operative Temporal Reality:** 2026 (1405 SH)  
**Workspace:** `/home/ghaderi-saber/Desktop/AcademicSuite`  
**Git Working Tree:** Clean (`main` branch)  

---

## 1. Executive Summary & Purpose

This document establishes the official pre-migration baseline for the architectural transformation of **AcademicSuite** from a mixed, largely flat collection of custom subagents and redundant orchestration scripts into a clean, hierarchical architecture strictly aligned with the current Google Antigravity agent model.

The audit was conducted strictly under read-only conditions:
- **Zero production code was modified.**
- **Zero agent specifications were renamed, moved, deleted, or rewritten.**
- **Zero hooks, permissions, validators, or state engines were altered.**
- **Every current agent (22 defined + 1 planned), skill (43 active), script, hook, and validator was forensically inspected.**

---

## 2. Workspace & Runtime Environment Profile

| Dimension | Measured Value | Operational Impact / Findings |
| :--- | :--- | :--- |
| **Operating System** | Linux 6.8.0-52-generic (x86_64 Ubuntu) | POSIX environment supporting native bash, symlinks, and fork-based subprocesses. |
| **Workspace Root** | `/home/ghaderi-saber/Desktop/AcademicSuite` | Single active workspace registered with Google Antigravity. |
| **Git Working Tree** | Clean (`branch main`, commit synced) | All tests and inspections executed without leaving untracked or modified artifacts. |
| **Host Python** | Python 3.14.0a3 (`/usr/bin/python3`) | Complete dependencies installed globally (`jsonschema`, `pandas`, `scipy`, `docx`, `pptx`). |
| **Local Virtualenv** | Python 3.12 (`.venv/bin/python3`) | **DEFECT DETECTED**: `jsonschema` is missing in `.venv`, causing 6 test failures when invoked via `.venv`. |
| **Antigravity Hooks** | `.agents/hooks.json` (Active) | Enforces PreToolUse, PostToolUse, PreInvocation, and Stop events via `transcript_and_rule_guard.py`. |
| **Model Context Protocol (MCP)** | 0 Active Servers | Zero MCP servers configured; all external fetching runs through deterministic scripts. |

### Baseline Test Execution Results
- **System Python (`python3 run_tests.py`)**:
  - **Tests Run:** 146
  - **Passed:** 146
  - **Failures:** 0
  - **Errors:** 0
  - **Execution Time:** 4.398s
  - **Status:** `ALL TESTS PASSED: Mathematical & constitutional invariants verified.`
- **Virtualenv Python (`.venv/bin/python3 run_tests.py`)**:
  - **Tests Run:** 137
  - **Passed:** 131
  - **Failures:** 4 (`test_05_study_act_burnout_compliance`, `test_06_academic_state_schema_conformity`, `test_07_academic_state_schema_conformity`, `test_08_academic_state_schema_conformity`)
  - **Errors:** 2 (`test_eval_suite`, `test_failure_recovery` failing on `ModuleNotFoundError: No module named 'jsonschema'`)
  - **Root Cause:** Environment disparity between host `/usr/bin/python3` and isolated `.venv`.

---

## 3. The Core Architectural Discovery: The "Two-World" Dichotomy

Forensic analysis of the agent definitions, scripts, and documentation revealed that the repository currently contains **two distinct, partially overlapping multi-agent architectures** co-existing simultaneously:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ACADEMIC SUITE REPOSITORY                                 │
├──────────────────────────────────────────────┬──────────────────────────────────────────────┤
│               WORLD A: "THE CORE 6"          │        WORLD B: "DIGITAL SABER & 16"         │
│          (Execution Pipeline Taxonomy)       │         (Cognitive Deliberation Mesh)        │
├──────────────────────────────────────────────┼──────────────────────────────────────────────┤
│ • Lead: academic-orchestrator                │ • Lead: digital-saber                        │
│ • Workers:                                   │ • Specialists (16 roles):                    │
│   - research-agent                           │   - methodology-expert, statistical-expert   │
│   - data-agent                               │   - data-curator, statistical-auditor        │
│   - statistics-agent                         │   - results-auditor, evidence-auditor        │
│   - writing-agent                            │   - academic-writer, final-judge             │
│   - validation-agent                         │   - psychometric-expert, qualitative-analyst │
│ • Frontmatter: Fully native Antigravity      │   - meta-analyst, intervention-designer      │
│   (tools, model, mainAgent, subagent)        │   - journal-strategist, literature-expert    │
│ • Script Integration: Directly wired into:   │   - longitudinal-modmed-expert               │
│   - scripts/academic_task_router.py          │ • Frontmatter: Outdated / Incomplete         │
│   - scripts/orchestrator_dependency_resolver │   (Missing tools list, model, mainAgent)     │
│   - scripts/academic_state_manager.py        │ • Script Integration: Zero scripts in scripts/│
│ • Scope: Broad functional umbrellas          │   invoke them directly (used in specs & docs)│
└──────────────────────────────────────────────┴──────────────────────────────────────────────┘
```

### Key Findings of the Dichotomy:
1. **Tool Whitelisting Disconnection**:
   - The 6 agents in World A explicitly declare `tools: [run_command, write_to_file, view_file, ...]`.
   - The 16 specialist agents in World B have **zero tools declared in frontmatter**. Although their contracts list extensive allowed tools, Antigravity defaults subagents without explicit frontmatter tool declarations to read-only capabilities, crippling their intended execution role.
2. **Duplicated Roles**:
   - `academic-writer` completely duplicates `writing-agent`.
   - `data-curator` duplicates `data-agent`.
   - `statistical-expert` duplicates `statistics-agent`.
   - `research-agent` bundles responsibilities that are split between `methodology-expert` and `literature-expert`.
   - `validation-agent` bundles responsibilities that are split between `statistical-auditor`, `results-auditor`, `evidence-auditor`, and `final-judge`.
3. **Dual Orchestrators**:
   - `digital-saber` is defined in its contract as Tier 1 Master Project Lead and Digital Twin of Saber Ghaderi, but lacks `mainAgent: true` and `tools: [invoke_subagent]` in its frontmatter.
   - `academic-orchestrator` possesses `mainAgent: true` and `tools: [invoke_subagent]`, functioning as the actual execution orchestrator in Python scripts.

---

## 4. Repository Inventory Summary

### 4.1 Agents (22 Defined + 1 Planned)
- **Total Physical Packages:** 22 directories in `.agents/agents/`.
- **Total Frontmatter Symlinks:** 22 symlinks (`.agents/agents/<name>.md -> <name>/agent.md`).
- **Total 12-Section Contracts:** 22 verified contract files (`.agents/agents/<name>/contract.md`).
- **Planned New Role:** `academic-challenger` (Adversarial viva voce challenger / harsh reviewer; currently 0 files and 0 references in code).

### 4.2 Skills (43 Active)
Located in `.agents/skills/`. All 43 possess valid `SKILL.md` files conforming to Directive 18 ($\le 500$ lines, $\le 40,000$ bytes).
- **Orchestration Skills:** `academic-suite-orchestrator` (contains 49 KB `orchestrator_cli.py`).
- **Statistical / Modeling Skills (13):** `descriptive-statistics`, `reliability-analysis`, `assumption-testing`, `regression`, `sem`, `cfa`, `mediation`, `moderation`, `longitudinal-moderated-mediation`, `statistical-data-analyst`, `gpower-sample-size-calculator`, `psychometric-scale-validator`, `psychometric-data-simulator`.
- **Psychometrics / Instruments (2):** `psychometric-scale-resolver`, `data-cleaning`.
- **Data Hygiene / Quality (1):** `data-audit`.
- **Writing / Academic Assembly (8):** `chapter-4-writing`, `persian-discussion-builder`, `persian-thesis-builder`, `persian-proposal-builder`, `persian-defense-presentation-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `persian-academic-translation`.
- **Literature / Bibliometrics (5):** `literature-review`, `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer`, `network-analysis`.
- **Validation / Auditing (3):** `thesis-integrity-auditor`, `apa-reporting`, `irandoc-plagiarism-reducer`.
- **Consulting / Clinical / Meta (6):** `digital-twin-academic-consultant`, `journal-submission-assistant`, `psychological-intervention-protocol-builder`, `persian-thesis-revision-assistant`, `qualitative-data-analyst`, `systematic-review-meta-analyst`.
- **Project Organization (1):** `academic-drive-project-organizer`.

### 4.3 Deterministic Execution Layer ("The Hands")
- `factory/`: `agent_factory.py`, `meta_factory.py`, `skill_factory.py`, `validator_factory.py`, `cli.py`, `specialist_manifest.json`.
- `scripts/`:
  - Orchestration & Routing: `academic_task_router.py`, `orchestrator_dependency_resolver.py`, `academic_state_manager.py`, `attach-suite.py`.
  - Triad Generators: `build_experimental_triad_docx.py`, `build_hypothesis_1_triad_docx.py`, `build_mediation_triad_docx.py`, `build_moderation_triad_docx.py`, `build_scale_validation_triad_docx.py`, `build_sem_triad_docx.py`, `build_defense_brief_triad.py`.
  - Data Generators: `generate_experimental_benchmark_data.py`, `generate_mediation_benchmark_data.py`, `generate_moderation_benchmark_data.py`, `generate_scale_validation_benchmark_data.py`, `generate_sem_benchmark_data.py`.
- `validators/`: 6 validator engines (`reporting_consistency`, `numerical_consistency`, `data_integrity`, `statistical_assumptions`, `result_consistency`, `longitudinal_modmed`) orchestrated via `run_all_validators.py`.

---

## 5. Verification of the Proposed Architectural Classification

The user provided an architectural hypothesis classifying roles into **Durable AGENTs** and **Bounded SUBAGENTs**. We evaluated this hypothesis against physical dependencies, contracts, and execution paths:

### 5.1 Durable AGENTS (Target Hypothesis vs. Ground Truth)

| Proposed Durable Agent | Current Role in Codebase | Verification Assessment | Recommended Action |
| :--- | :--- | :--- | :--- |
| **`digital-saber`** | Digital Twin of Saber Ghaderi, pricing estimator, Telegram consultant, case-based reasoner. | **CONFIRMED DURABLE**. Serves as the primary user-facing principal agent representing the human PI. | Upgrade frontmatter to include `mainAgent: true`, `model: pro`, and native `tools` whitelisting. |
| **`academic-orchestrator`** | Master conductor for pipeline stage decomposition and artifact tracking. | **CONFIRMED DURABLE (OR CO-LEAD)**. Currently holds `mainAgent: true` and is wired into all CLI routing tools. | Retain as durable execution orchestrator, operating in tandem with `digital-saber` (Principal + Conductor pattern). |
| **`methodology-expert`** | Research design, G*Power sampling, threats to validity, proposal architecture. | **CONFIRMED DURABLE**. Essential persistent authority across study inception, Chapter 3 design, and defense cross-examination. | Upgrade frontmatter with explicit tools whitelisting. |
| **`statistical-expert`** | Statistical decision tree, assumption testing architect, inferential modeling strategy. | **CONFIRMED DURABLE**. Essential persistent authority for statistical philosophy and hypothesis verification. | Upgrade frontmatter with explicit tools whitelisting. Absorbs `statistics-agent`. |
| **`academic-writer`** | Persian rhetoric, 5-part epistemic paragraph structure, OpenXML formatting. | **CONFIRMED DURABLE**. Primary persistent drafting authority across all 5 chapters, articles, and revisions. | Upgrade frontmatter with explicit tools whitelisting. Absorbs `writing-agent`. |
| **`evidence-auditor`** | Epistemic integrity, bidirectional citation-reference matching, Irandoc plagiarism audit. | **CONFIRMED DURABLE**. Persistent adversarial gatekeeper for literature and integrity. | Upgrade frontmatter with explicit tools whitelisting. |
| **`final-judge`** | Defense committee simulation (Viva Voce), administrative approval gatekeeper. | **CONFIRMED DURABLE**. Persistent clearance authority for dissertation defense and supervisor comment triage. | Upgrade frontmatter with explicit tools whitelisting. |

### 5.2 Bounded SUBAGENTs (Target Hypothesis vs. Ground Truth)

| Proposed Subagent | Current Role in Codebase | Verification Assessment | Recommended Action |
| :--- | :--- | :--- | :--- |
| **`research-agent`** | Umbrella research agent currently binding 8 skills. | **CONFIRMED SUBAGENT**. Best suited as a bounded worker executing specific literature harvesting tasks under `methodology-expert`. | Narrow scope; delegate specialized synthesis to subagents. |
| **`literature-expert`** | Database queries (PubMed, CrossRef, SID), parameter extraction. | **CONFIRMED SUBAGENT**. High-focus worker for literature extraction. | Retain as bounded worker. |
| **`journal-strategist`** | Journal matching, cover letters, submission packaging. | **CONFIRMED SUBAGENT**. Task-bounded worker for post-thesis journal publication. | Retain as bounded worker. |
| **`meta-analyst`** | PRISMA 2020 screening, RoB 2 risk of bias, forest/funnel plots. | **CONFIRMED SUBAGENT**. Specialized numerical worker. | Retain as bounded worker. |
| **`data-agent`** | Data ingestion, missingness diagnostics, reverse-coding. | **CONFIRMED SUBAGENT**. Bounded worker for Stage 4.0 data curation. | Consolidate duplicate features with `data-curator`. |
| **`data-curator`** | Missingness patterns, unengaged respondents, Mahalanobis D2. | **CONFIRMED SUBAGENT**. Highly bounded data hygiene worker. | Retain or merge into unified `data-agent`. |
| **`statistics-agent`** | Execution runner for SPSS/R scripts and APA 7 tables. | **MERGE CANDIDATE**. Complete duplicate of `statistical-expert`. | Merge operational execution tools into `statistical-expert` or retain as execution worker. |
| **`psychometric-expert`**| CVR/CVI, CTT, IRT, EFA, CFA, and construct validity. | **CONFIRMED SUBAGENT**. Bounded worker for scale standardization. | Retain as bounded worker. |
| **`longitudinal-modmed-expert`**| 3-wave longitudinal moderated mediation modeling. | **CONFIRMED SUBAGENT**. Highly specialized modeling worker. | Retain as bounded worker. |
| **`intervention-designer`**| Clinical manual and intervention session protocol builder. | **CONFIRMED SUBAGENT**. Bounded worker for experimental study interventions. | Retain as bounded worker. |
| **`qualitative-analyst`**| Braun & Clarke thematic analysis, Grounded Theory coding. | **CONFIRMED SUBAGENT**. Bounded qualitative worker. | Retain as bounded worker. |
| **`validation-agent`** | Umbrella quality gatekeeper checking df, reporting, and formatting. | **CONFIRMED SUBAGENT (CRITIC)**. Bounded adversarial quality auditor. | Re-align as worker under `final-judge` or `evidence-auditor`. |
| **`results-auditor`** | APA 7 numerical precision, leading zero rule, OMML math preservation. | **CONFIRMED SUBAGENT (CRITIC)**. Bounded formatting/reporting auditor. | Retain as specialized critic worker. |
| **`statistical-auditor`**| Degrees of freedom, assumption violations, MSAI anomaly scoring. | **CONFIRMED SUBAGENT (CRITIC)**. Bounded mathematical integrity auditor. | Retain as specialized critic worker. |
| **`academic-challenger`**| (Planned new role). | **CONFIRMED NEW SUBAGENT (CRITIC)**. Harsh examiner / adversarial challenger role for Viva Voce stress-testing. | Scaffold new role during migration. |

---

## 6. Identification of Duplications & Anti-Patterns

### 6.1 Duplicate Agents
1. **`writing-agent` vs. `academic-writer`**: Both are defined as "Persian Academic Chapter Drafter & Rhetoric Specialist". They share identical missions, skills (`persian-thesis-builder`, `persian-discussion-builder`, `academic-article-writer`, `ai-academic-tone-polisher`), and guidelines. `writing-agent` has frontmatter tools; `academic-writer` has none.
2. **`statistics-agent` vs. `statistical-expert`**: Both are defined as statistical modeling and hypothesis testing architects. `statistics-agent` has frontmatter tools and is wired into scripts; `statistical-expert` has deep domain prompts but zero frontmatter tools.
3. **`data-agent` vs. `data-curator`**: Both handle missing data, Little's MCAR, straight-lining, and scale reverse-coding.

### 6.2 Duplicate Skills
1. **Literature Skills**: `literature-review` (24 lines) vs. `persian-literature-review-builder` (21 lines) vs. `literature-harvester` (24 lines). All three handle literature extraction and review drafting with minor parameter variations.
2. **Network Analysis Skills**: `network-analysis` (24 lines) vs. `bibliometric-network-analyst` (23 lines) vs. `citation-network-visualizer` (24 lines). Substantial overlap in science mapping and VOSviewer/Callon exports.
3. **Statistical Modeling Skills**: `statistical-data-analyst` (106 lines, 7 scripts) bundles regression, mediation, and ANCOVA scripts, overlapping with standalone skills `regression`, `mediation`, `moderation`, and `cfa`.

### 6.3 Orchestration Logic Leaking into Skills
- **`academic-suite-orchestrator`**: Defined as a skill in `.agents/skills/academic-suite-orchestrator/`, but contains `scripts/orchestrator_cli.py` (927 lines, 49,334 bytes). This script acts as a hardcoded workflow runner chaining 18 different skills and defining pre-baked pipeline presets (`thesis_empirical`, `scale_validation`, etc.). This duplicates native Antigravity orchestrator responsibilities.

### 6.4 Custom Orchestration Duplicating Antigravity Functionality
- `scripts/academic_task_router.py`: Custom regex-based capability detector and DAG builder.
- `scripts/orchestrator_dependency_resolver.py`: Custom dependency graph resolver and delegation envelope formatter.
- These scripts represent custom middleware attempting to simulate multi-agent orchestration via deterministic CLI scripts rather than native Antigravity dynamic subagent dispatch.

---

## 7. Next Documents in Migration Series

- [01_CURRENT_AGENT_INVENTORY.md](file:///home/ghaderi-saber/Desktop/AcademicSuite/docs/migration/01_CURRENT_AGENT_INVENTORY.md): Exhaustive 13-point audit for every individual agent.
- [02_CURRENT_DEPENDENCY_GRAPH.md](file:///home/ghaderi-saber/Desktop/AcademicSuite/docs/migration/02_CURRENT_DEPENDENCY_GRAPH.md): Comprehensive topology of dependencies, handoffs, and call graphs.
- [03_CURRENT_RISK_REGISTER.md](file:///home/ghaderi-saber/Desktop/AcademicSuite/docs/migration/03_CURRENT_RISK_REGISTER.md): Forensic register of all fail-open paths, silent fallbacks, and security risks.
