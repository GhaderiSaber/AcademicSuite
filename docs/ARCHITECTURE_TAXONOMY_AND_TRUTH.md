# Architectural Taxonomy & Single Source of Truth
**Current vs. Historical vs. Target Architecture Baseline**

- **Document Version**: `3.0.0 (Authoritative Ground Truth)`
- **Operative Date**: September 2026 (1405 SH)
- **Status**: **AUTHORITATIVE CURRENT ARCHITECTURE — ACTIVE PRODUCTION BASELINE**

---

## 🏛️ Executive Purpose

As AcademicSuite evolved across 38 development phases, documentation accumulated milestone reports, phase audits, red-team evaluations, and transitional roadmaps. This created apparent internal numerical and structural drift across documents written at different points in time:

| Metric / Aspect | Historical Phase Docs | Transitory Docs | **Current Ground Truth (As-Built)** |
| :--- | :--- | :--- | :--- |
| **Agents** | 22 persistent roles | 28 production agents | **31 Agents** (29 Production + 2 Verification) |
| **Skills** | 43 production skills | 44 active skills | **44 Production Skills** in `.agents/skills/` |
| **Legacy Directory** | Root `legacy/` | Root symlink `legacy/` | **`.agents/legacy/`** (Consolidated in `.agents/`) |
| **Scripts Directory** | Root `scripts/` | Symlink `scripts -> .agents` | **`.agents/scripts/`** (Zero root symlinks) |
| **Contracts** | 29 contracts | 35 contracts | **51 Contracts** in `.agents/contracts/` |
| **Tracked Files** | 7,102 files (uncleaned) | 1,402–1,445 files | **~1,445 Tracked Git Files** |

To prevent AI agents from reading historical phase reports and treating them as current operational policy, this document formally codifies the **Three Architectural Tiers** and establishes the single source of truth for the codebase.

---

## 🧭 The Three Architectural Tiers

Every document and architectural reference in AcademicSuite belongs to exactly one of three temporal tiers:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CURRENT ARCHITECTURE (Ground Truth — As-Built)                            │
│    • Active operational policy enforced by hooks, code, and test harness    │
│    • Canonical files: AGENTS.md, README.md, docs/CURRENT_ARCHITECTURE.md    │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲
                               │ Replaces & Consolidates
┌──────────────────────────────┴──────────────────────────────────────────────┐
│ 2. HISTORICAL ARCHITECTURE (Archived Phase Records)                         │
│    • Point-in-time snapshot records of completed development phases          │
│    • Canonical files: docs/migration/*, docs/evolution/*, docs/history/*    │
│    • Status: ARCHIVED / HISTORICAL (Do NOT execute as current policy)       │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲
                               │ Preceded by
┌──────────────────────────────┴──────────────────────────────────────────────┐
│ 3. TARGET ARCHITECTURE (Roadmap & Design Proposals)                         │
│    • Forward-looking design documents and unmerged architectural proposals  │
│    • Canonical files: docs/architecture/TARGET_ARCHITECTURE.md               │
│    • Status: PROPOSAL / ROADMAP (Governed by Freeze on Horizontal Growth)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Tier 1: Current Architecture (Ground Truth Specification)

### 1. Agents Directory: Exactly 31 Agents on Disk ([`.agents/agents/`](../.agents/agents/))
The filesystem contains exactly 31 packaged agent directories, categorized into:
- **6 Core Primary Cognitive Roles**:
  `academic-orchestrator`, `research-agent`, `data-agent`, `statistics-agent`, `academic-writer`, `validation-agent`.
- **17 Specialized Domain Roles**:
  `digital-saber`, `methodology-expert`, `statistical-expert`, `statistical-auditor`, `results-auditor`, `academic-challenger`, `literature-expert`, `evidence-auditor`, `final-judge`, `psychometric-expert`, `qualitative-analyst`, `meta-analyst`, `journal-strategist`, `intervention-designer`, `data-curator`, `project-organizer`, `longitudinal-modmed-expert`.
- **6 Continuous Learning & Evolution Roles**:
  `behavior-analyst`, `curriculum-builder`, `evaluation-agent`, `knowledge-curator`, `skill-evolver`, `trajectory-analyzer`.
- **2 Minimal Verification Test Agents**:
  `test-orchestrator`, `test-worker` (used in Phase 29/30 architectural invariant tests to verify pure delegation and execution privilege boundaries without domain overhead).
- **Total Production Agents**: **29** (`test-orchestrator` and `test-worker` are reserved for test harness verification).
- **Total Registered Agents on Disk**: **31**.

#### 1.1 The Planar Architecture Model (6 Operational Planes + 1 Administrative Plane)
To eliminate mesh authority sprawl where secondary planners spawned sub-agents and critics mutated files they audited, the 30 agents are strictly partitioned into **6 Operational Planes** and **1 Administrative Plane**:

1. **CONTROL PLANE** (Coordination & Strategy):
   - `academic-orchestrator` (Conductor): Holds `invoke_subagent`. Strictly prohibited from file mutation and code execution (Directive 20).
   - `digital-saber` (Advisory Twin & Consultant): Principal cognitive twin and consultant. Strictly prohibited from delegation and execution (Model A Invariant).
   - `methodology-expert` (Advisor): Domain consultative authority. Strictly prohibited from delegation and file mutation.
   - `statistical-expert` (Advisor): Domain consultative authority. Strictly prohibited from delegation and file mutation.
2. **RESEARCH PLANE** (Epistemic Evidence & Literature):
   - `research-agent`: Literature synthesis and research design worker.
   - `literature-expert`: Bibliometric mapping and automated harvesting worker.
   - `evidence-auditor`: Citation, plagiarism, and evidence integrity critic. Strictly prohibited from file mutation.
3. **DATA PLANE** (Ingestion & Quality):
   - `data-agent`: Data ingestion, cleaning, imputation, and psychometric scaling.
   - `data-curator`: Missing value diagnostics, unengaged filtering, and outlier screening.
4. **STATISTICS PLANE** (Computational Inference & Modeling):
   - `statistics-agent`: General inferential modeling, SEM, ANCOVA, and hypothesis testing.
   - Specialist statistical workers: `psychometric-expert`, `longitudinal-modmed-expert`, `qualitative-analyst`, `meta-analyst`.
5. **WRITING PLANE** (Synthesis & Scholarly Documentation):
   - `academic-writer`: Chapter drafting, synthesis, and OpenXML packaging.
   - `intervention-designer`: Clinical intervention manuals and protocol drafting.
   - `journal-strategist`: Manuscript packaging and submission strategy.
6. **VALIDATION PLANE** (Independent Verification & Adversarial Audit):
   - `validation-agent`: Comprehensive quality assurance and pre-flight gatekeeper.
   - `statistical-auditor`: Parametric assumptions and MSAI auditor (read/verify only, no file mutation).
   - `results-auditor`: APA 7 numerical and table format auditor (strictly prohibited from file mutation).
   - `academic-challenger`: Adversarial methodology challenger (strictly prohibited from file mutation).
   - `final-judge`: Viva voce simulator and institutional release gatekeeper (strictly prohibited from file mutation).
7. **ADMINISTRATIVE PLANE** (Continuous Learning & Evolution):
   - Meta-cognitive layer for continuous self-improvement and behavioral refinement:
     - `trajectory-analyzer`: Reconstructs observable tool execution trajectories (read-only).
     - `behavior-analyst`: Root-cause causal diagnosis of agent defects (read-only).
     - `knowledge-curator`: Synthesizes reusable lessons, exemplars, and anti-patterns.
     - `skill-evolver`: Formulates candidate modifications to skills and instructions.
     - `evaluation-agent`: Runs counterfactual benchmarks and regression suites.
     - `curriculum-builder`: Designs graduated challenge benchmarks and test datasets.

**Structural Invariants of the Planar Model**:
- **Sole Orchestration**: `academic-orchestrator` is the sole conductor in the operational pipeline; advisors (`digital-saber`, `methodology-expert`, `statistical-expert`) advise but never delegate (`can_delegate: false`).
- **Critic Immutability**: No critic or auditor possesses file mutation tools (`write_to_file`, `replace_file_content`). Critics evaluate and verify; they never silently rewrite deliverables.
- **Least-Privilege Authority Surface**: Slashed delegation from 5 agents to 2 (`academic-orchestrator` and test fixture `test-orchestrator`). Slashed file writing from 26 agents to 18 (12 agents are strictly read/audit/conduct).

### 2. Skills Directory: Exactly 44 Active Production Skills ([`.agents/skills/`](../.agents/skills/))
- Exactly 44 domain capabilities reside in `.agents/skills/`.
- Every skill conforms to Directive 18 (single-view context budget: $\le 500$ lines, $\le 40,000$ bytes per `SKILL.md`).
- 10 historical workflow-converted shells are retired and preserved in [`.agents/legacy/skills/`](../.agents/legacy/skills/) for backward compatibility and test verification.

### 3. Contracts Directory: 51 Schemas & Contracts ([`.agents/contracts/`](../.agents/contracts/))
- Master analysis plans, stage manifests, execution envelopes, and statistical provenance contracts are stored in `.agents/contracts/`.
- Historical references to "29 contracts" reflected Phase 17 prior to the addition of statistical provenance contracts, learning contracts, and presentation manifests.

### 4. Consolidated Subsystem Architecture (`.agents/` Enclosure)
In accordance with Directive 19 and the root-cleanliness invariant:
- All framework code, scripts, contracts, hooks, and legacy assets reside strictly inside `.agents/`:
  - `.agents/agents/` — 30 Cognitive Roles
  - `.agents/skills/` — 44 Production Capabilities
  - `.agents/contracts/` — 51 Schema & Manifest Contracts
  - `.agents/scripts/` — Deterministic Orchestration & State Engines
  - `.agents/validators/` — Gatekeeper Validators (Data, Numbers, Reporting)
  - `.agents/tools/` — Computational Engines (Python & R)
  - `.agents/factory/` — Meta-Agent & Skill Generative Factory
  - `.agents/recovery/` — Diagnostic & State Repair Engine
  - `.agents/learning/` — Autonomous Agent Evolution & Behavioral Memory
  - `.agents/state/` — Persistent State Machine Ledger
  - `.agents/legacy/` — Retired Workflows and Skill Shells Archive
- **Root Directory Cleanliness**: Zero `scripts/`, `tools/`, `contracts/`, `validators/`, or `legacy/` symlinks or directories exist in the root repository. Python path resolution is enforced deterministically by `tests/conftest.py` and `run_tests.py`.

### 5. Repository File Count Reconciliation
- An earlier historical document (`CODEBASE_INVENTORY_AUDIT.md`) reported "7,102 repository files". That audit scanned an uncleaned development environment containing untracked build artifacts, temporary directories, and git objects.
- In the active, clean production repository, exactly **~1,445 tracked files** exist in git version control, with 100% of Python files passing AST parsing and bytecode compilation.

---

## 📜 Tier 2: Historical Architecture (Archived Phase Records)

Documents located in:
- `docs/migration/` (Reports 00 through 14)
- `docs/evolution/` (Reports 00 through 08)
- `docs/architecture/CODEBASE_INVENTORY_AUDIT.md`

Are **permanent historical audit records** of specific milestones in the evolution of AcademicSuite. They reflect the exact state of the codebase at the time that phase was completed. 

**Rule for Autonomous Agents**:
> **NEVER override current directives in `AGENTS.md` or `docs/CURRENT_ARCHITECTURE.md` using numbers, paths, or rules from historical phase reports.**

---

## 🔭 Tier 3: Target Architecture (Roadmaps & Proposals)

Documents such as:
- `docs/architecture/TARGET_ARCHITECTURE.md`
- `docs/evolution/04_TARGET_SELF_IMPROVEMENT_ARCHITECTURE.md`

Represent forward-looking blueprints and target state proposals. Features in Target Architecture documents that are not implemented on disk in `.agents/` are subject to **Rule 1 (Freeze on Horizontal Growth)**: they may only be implemented if they fill an empirically validated gap.

---

## 🛑 Authority Hierarchy

When any conflict arises between documents, resolve strictly in this order:

1. **Constitutional Law**: [`.agents/AGENTS.md`](../AGENTS.md) and repository [`AGENTS.md`](../AGENTS.md).
2. **Current Architecture Specification**: [`docs/CURRENT_ARCHITECTURE.md`](CURRENT_ARCHITECTURE.md) and this document ([`docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md`](ARCHITECTURE_TAXONOMY_AND_TRUTH.md)).
3. **Active Schemas & Contracts**: [`.agents/contracts/`](../.agents/contracts/).
4. **Target Architecture Roadmaps**: [`docs/architecture/TARGET_ARCHITECTURE.md`](architecture/TARGET_ARCHITECTURE.md).
5. **Historical Milestone Reports**: [`docs/migration/`](migration/) and [`docs/evolution/`](evolution/) (historical context only).
