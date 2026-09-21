# Academic Suite — Current System Architecture Audit

**Document Version:** 3.0.0 (Consolidated Production Baseline)  
**Operative Date:** September 2026 (1405 SH)  
**System Status:** **AUTHORITATIVE CURRENT ARCHITECTURE (GROUND TRUTH)**  
**Classification Guide:** See [docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md](ARCHITECTURE_TAXONOMY_AND_TRUTH.md) for reconciliation with historical phase records.

---

## 1. Executive Architectural Overview

The **Academic Suite** (integrating the **Digital Saber Professional AI Twin**) is a cognitive architecture and statistical consultancy framework designed for graduate dissertations (M.A./M.Sc., Ph.D.) and academic journal publishing in psychology and the behavioral sciences.

The system enforces a strict dichotomy between **The Brains & Critics** (autonomous cognitive subagents executing within Google Antigravity) and **The Hands** (deterministic Python and R mathematical engines and OpenXML compilation scripts).

```text
+-----------------------------------------------------------------------------+
|                             USER / RESEARCHER                               |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                   ANTIGRAVITY NATIVE RUNTIME (Sole Conductor)                |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   |           Lead Orchestrator (Digital Saber Primary Twin)            |   |
|   +---------------------------------+-----------------------------------+   |
|                                     | invoke_subagent                       |
|         +---------------------------+---------------------------+           |
|         |                                                       |           |
|         v                                                       v           |
|   +-----------------------------------+   +-----------------------------+   |
|   |        Cognitive Subagents        |   |    Adversarial Auditors     |   |
|   |  - methodology-expert             |   |  - statistical-auditor      |   |
|   |  - statistical-expert             |   |  - results-auditor          |   |
|   |  - academic-writer                |   |  - evidence-auditor         |   |
|   |  - literature-expert              |   |  - final-judge              |   |
|   |  - data-curator                   |   +--------------+--------------+   |
|   |  - psychometric-expert            |                  |                  |
|   +-----------------+-----------------+                  |                  |
|                     |                                    |                  |
+---------------------|------------------------------------|------------------+
                      | run_command (Terminal CLI)         |
                      v                                    v
+-----------------------------------------------------------------------------+
|                   DETERMINISTIC EXECUTION LAYER ("The Hands")               |
|                                                                             |
|   +------------------------------+     +--------------------------------+   |
|   |    Mathematical / Stats      |     |      OpenXML Document Engine   |   |
|   | - psychology_stats.py        |     | - openxml_artifact_engine.py   |   |
|   | - data_harnessing_engine.R   |     | - generate_apa_docx.py         |   |
|   | - simdat_engine.py           |     | - compile_full_thesis.py       |   |
|   | - meta_analysis_engine.py    |     | - rtl_typography.py            |   |
|   +--------------+---------------+     +---------------+----------------+   |
|                  |                                     |                    |
+------------------|-------------------------------------|--------------------+
                   v                                     v
+-----------------------------------------------------------------------------+
|               SYNCHRONIZED ARTIFACT TRIAD (.docx + .md + .json)             |
|       Physical on-disk checkpoints (Directive 3 & One-Hypothesis-One-Stage) |
+-----------------------------------------------------------------------------+
```

---

## 2. The Five Cognitive Layers

The system is organized into five layered subsystems rooted under `.agents/`:

```
.agents/
├── identity/          <- Layer 1: Identity, Persona & Research Constitution
├── memory/            <- Layer 2: Case-Based Reasoning (CBR) & Decision Journal
├── reasoning/         <- Layer 3: Epistemic, Methodological & Statistical Reasoners
├── skills/            <- Layer 4: Specialized Capabilities (27 Modern + 10 Legacy)
└── verification/      <- Layer 5: Multi-Signal Anomaly Index (MSAI) & Quality Control
```

### Layer 1: Identity & Constitution (`.agents/identity/`)
Encodes Saber Ghaderi's research philosophy, statistical standards, and writing voice:
- `SABER_RESEARCH_CONSTITUTION.md`: Ethical boundaries, anti-hallucination protocols, and client protection rules.
- `SABER_STATISTICAL_PHILOSOPHY.md`: The 10-step parametric decision tree, rejection of median splits and Baron & Kenny stepwise mediation, requirement of Bootstrap 5,000 for indirect effects.
- `SABER_QUALITY_STANDARDS.md`: Rigorous criteria for publishable manuscripts and defense-ready dissertations.
- `SABER_DECISION_RULES.md`: Heuristics for resolving sample size, violation of normality, and model trimming.
- `SABER_ACADEMIC_WRITING_STYLE.md`: 5-part epistemic paragraph structure, natural cadence variability ($CV \ge 0.50$), and half-space typography (`\u200c`).

### Layer 2: Memory & Precedents (`.agents/memory/`)
Provides persistent institutional memory across research engagements:
- `case_memory_engine.py`: Case-Based Reasoning (CBR) indexing 16 real psychological dissertation cases in `cases/`. Matches incoming research questions against historical precedents.
- `decision_journal_engine.py`: Immutable audit log in `decisions/` tracking high-stakes statistical decisions (e.g. data trimming, non-parametric fallbacks, price quotations).
- `continuous_learning_engine.py`: Post-defense feedback ingestion.
- `case_harvester.py` & `harvest_saber_style.py`: Scrapers and indexers for historical theses.

### Layer 3: Reasoning Engines (`.agents/reasoning/`)
Modular Python classes encapsulating domain reasoning rules:
- `statistical_reasoner.py`: Analyzes variable topologies, scales of measurement, and maps hypotheses to statistical tests.
- `research_methodology_reasoner.py`: Validates experimental/quasi-experimental designs, internal/external validity threats.
- `epistemic_literature_reasoner.py`: Evaluates empirical weight of literature and synthesizes theoretical mechanisms.
- `writing_reasoner.py`: Evaluates paragraph cadence, vocabulary diversity, and Iranian academic register.

### Layer 4: Specialized Skills & Hands (`.agents/skills/`)
The practical execution modules (44 active production skills):
- **44 Focused Production Skills**: Complete capabilities containing deterministic Python/R scripts, reference guidelines, canonical example payloads, and input/output JSON schemas.
- **10 Retired Legacy Workflow Shells**: Archived to `.agents/legacy/skills/` with documentation (detailed in `docs/LEGACY_INVENTORY.md` and `docs/SKILL_INVENTORY.md`).

### Layer 5: Quality Control & Defense Committee (`.agents/verification/`)
Adversarial quality gates protecting deliverable integrity:
- `multi_signal_anomaly_detector.py`: Multi-Signal Anomaly Index (MSAI) calculating effect size plausibility, variance deflation, and degrees of freedom concordance.
- `defense_committee_simulator.py`: Simulates 5 distinct academic examiner personas (The Methodologist, The Statistician, The Epistemic Theorist, The Pedant, The Clinical Pragmatist) for oral defense preparation.
- `pipeline_auditor.py` & `audit_transcript.py`: Verifies pipeline execution against required checkpoint artifacts.
- `transcript_and_rule_guard.py`: Mechanical lifecycle hook script backing `.agents/hooks.json`.
- `skill_size_guard.py`: Enforces Directive 18 (single-view context budget ceiling: 500 lines / 40 KB).

---

## 3. Physical Directory Map

```text
AcademicSuite/
├── .agents/                               # Consolidated Digital Saber Cognitive Subsystem
│   ├── agents/                            # 30 Packaged Agents (28 Production Roles + 2 Verification Roles)
│   ├── skills/                            # 44 Active Production Skills (scripts, resources, examples, schemas)
│   ├── contracts/                         # 51 Authoritative Schemas & Behavioral Policy Contracts
│   ├── scripts/                           # Deterministic Orchestration, State & Routing Engines
│   ├── validators/                        # Deterministic Gatekeepers (Data, Reporting, Numerical, Assumptions)
│   ├── tools/                             # Computational Engines ("The Hands": Python & R)
│   ├── factory/                           # Agent & Skill Generative Meta-Factory
│   ├── recovery/                          # Failure Recovery & State Diagnostics Engine
│   ├── learning/                          # Autonomous Agent Evolution, Lessons & Behavioral Memory
│   ├── state/                             # Persistent State Ledger & Milestone Progression
│   ├── legacy/                            # Retired Components Archive (10 workflows & legacy skills)
│   ├── rules/                             # Constitutional Directives & Guardrails
│   ├── hooks/                             # Antigravity Lifecycle Hook Runner Scripts
│   ├── hooks.json                         # Hooks Configuration Manifest
│   ├── identity/                          # Digital Saber Persona & Core Constitution
│   ├── memory/                            # Case-Based Reasoning (16 cases) & Decision Journal
│   └── verification/                      # MSAI Anomaly Detector & Committee Viva Voce Simulator
├── docs/                                  # Centralized Documentation, Contracts & Architecture Blueprints
├── evals/                                 # Permanent Evaluation Benchmark Suite
├── tests/                                 # 1,060+ Automated Pytest Tests (100% Green Signal)
├── webapp/                                # Academic Suite Interactive Web Console
├── projects/                              # Active Thesis Projects & Study Workspaces
├── Questionnaires.xlsx                    # Psychometric database (4,880 validated instruments)
├── AGENTS.md                              # Repository Root Constitutional Directives (Directives 0-20)
├── ANTIGRAVITY_ARCHITECTURE_GUIDE.md      # Google Antigravity Platform Guide
├── requirements.txt                       # Python dependencies (scipy, pingouin, python-docx, etc.)
├── run_tests.py                           # Master test runner with pre-flight compilation check
└── README.md                              # Project overview and installation documentation
```

---

## 4. Antigravity System Integration & Runtime Model

### Lead Agent vs. Subagent Mechanics
1. **The Lead Conductor**: Antigravity is the sole orchestration engine. The main conversation runs as the lead agent (`digital-saber`), communicating in English with the researcher, directing tasks, and managing stage gates.
2. **Subagent Spawning**: Specialized cognitive roles are invoked natively via `invoke_subagent` (e.g. `invoke_subagent(TypeName="statistical-expert", ...)`).
3. **Deterministic Hands**: Subagents and the lead agent execute Python/R CLI scripts via `run_command`. Under **Directive 2**, agents never compute statistics mentally.
4. **Interactive Stage-Gate Protocol**: Under **Directive 11**, the system halts at every micro-stage, reports what was done and what is next, and waits for human confirmation.
5. **Artifact Triad**: Under **Directive 3**, every stage outputs `.docx` (OpenXML Word), `.md` (Markdown tables & narrative), and `.json` (structured numerical data).

---

## 5. Tooling & MCP Server Topology

| Tool Category | Status | Implementation Detail |
|---|---|---|
| **Antigravity Built-in Tools** | **Active (17 Tools)** | `run_command`, `write_to_file`, `replace_file_content`, `view_file`, `list_dir`, `grep_search`, `find_by_name`, `read_url_content`, `search_web`, `invoke_subagent`, `manage_subagents`, `send_message`, `schedule`, `manage_task`, `ask_question`, `generate_image`, `define_subagent` |
| **Model Context Protocol (MCP)** | **Zero (0) Active** | No MCP servers configured in `.agents/`, `.agents/plugins/`, or `~/.gemini/antigravity/antigravity_state.pbtxt`. All external data interactions are executed via deterministic scripts (`requests`, `urllib`, `beautifulsoup4`) invoked via `run_command`. |
| **Python Statistical Environment** | **Active** | Local virtual environment (`.venv/`) with `pingouin`, `scipy`, `pandas`, `statsmodels`, `openpyxl`, `python-docx`. |
| **R Statistical Environment** | **Active (Optional)** | `data_harnessing_engine.R` (lavaan, psych) executed via `Rscript` when SEM bootstrapping is required. |
| **Document Compiler** | **Active** | `openxml_artifact_engine.py` directly generating and manipulating Word `.docx` OpenXML package components. |

---

## 6. Lifecycle Hooks & Rule Enforcement

Antigravity lifecycle hooks configured in `.agents/hooks.json` mechanically enforce constitutional compliance:

```text
Antigravity Lifecycle Event
  │
  ├── PreToolUse (run_command, write_to_file, replace_file_content)
  │     └── transcript_and_rule_guard.py --event PreToolUse
  │           -> Blocks non-ASCII Persian filenames (Directive 6)
  │           -> Blocks prohibited file deletions / dangerous shell patterns
  │
  ├── PostToolUse (run_command, write_to_file)
  │     └── transcript_and_rule_guard.py --event PostToolUse
  │           -> Validates artifact generation on disk
  │
  ├── PreInvocation
  │     └── transcript_and_rule_guard.py --event PreInvocation
  │           -> Injects ephemeral constitutional reminders (Directives 0, 3, 11, 12.1)
  │
  └── Stop
        └── transcript_and_rule_guard.py --event Stop
              -> Audits conversation transcript for Binary Honesty Protocol
              -> Audits for uninvoked multi-agent claims
              -> Enforces skill context budget (skill_size_guard.py)
```

---

## 7. Current Architecture Health & Overlap Summary
1. **Agent Governance**: Exactly 30 agents packaged into Option-1 directories in `.agents/agents/` (28 production cognitive roles [22 domain + 6 learning] + 2 minimal verification roles), each governed by a 12-section `contract.md`.
2. **Skills Consolidation**: Exactly 44 active production skills in `.agents/skills/`. The 10 legacy workflow-converted shells are safely retired to `.agents/legacy/skills/`.
3. **Contracts & Schemas**: Exactly 51 schema and policy contracts in `.agents/contracts/`.
4. **Sole Orchestrator Mandate (Directive 12.1 Enforced)**: Antigravity is the sole agent orchestrator. Python scripts operate strictly as deterministic computational tools ("The Hands"). Standalone emulators are permanently deprecated.
5. **Architectural Ground Truth**: Reconciled and classified in [docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md](ARCHITECTURE_TAXONOMY_AND_TRUTH.md).
