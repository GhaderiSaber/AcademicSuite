# AcademicSuite Specialist Subagent Migration & Deprecation Report

**Document Version:** 1.0.0  
**Phase:** Specialist Worker Migration (Phase 5)  
**Status:** COMPLETE & VERIFIED  
**Operative Temporal Reality:** September 2026 (1405 SH)  

---

## 1. Executive Summary

All **15 Specialist Subagents** have been successfully migrated into bounded Antigravity subagents adhering to current Google Antigravity custom-agent architecture. The migration establishes:

1. Canonical directory-form packaging (`.agents/agents/<name>/agent.md` and `contract.md`).
2. Strict least-privilege boundary enforcement (`subagent: true`, `mainAgent: false`, `agents: []`, zero delegation tools).
3. Exact domain differentiation (e.g., `statistics-agent` as execution only vs `statistical-expert` as design authority; raw datasets strictly immutable for `data-agent` and `data-curator`).
4. Creation of the new `academic-challenger` adversarial falsification and red-teaming critic.
5. 100% backward-compatible relative symlinks (`.agents/agents/<name>.md -> <name>/agent.md`).

---

## 2. Inventory of Migrated Specialist Subagents (15 Roles)

| # | Subagent Name | Role Title | Model | Tools Count | Skills Bound | Key Architectural Boundary |
|---|---------------|------------|-------|-------------|--------------|----------------------------|
| 1 | `research-agent` | Scientific Literature Harvester & Research Question Architect | `flash` | 6 | 3 | Researches assigned questions; extracts N, design, scales; no executive methodology |
| 2 | `literature-expert` | Literature Synthesis & Bibliometric Matrix Specialist | `flash` | 6 | 3 | Multi-database retrieval & bibliometric networks; no primary inferential testing |
| 3 | `journal-strategist` | Academic Journal Matching & Peer-Review Rebuttal Specialist | `pro` | 6 | 2 | Journal scope matching & rebuttal tables; no calculation of new statistics |
| 4 | `meta-analyst` | PRISMA 2020 Systematic Review & Quantitative Meta-Analyst | `flash` | 6 | 2 | PRISMA screening & quantitative effect size pooling; no survey participant data |
| 5 | `data-agent` | Raw Data Screening, Reverse-Coding & Psychometric Simulator | `flash` | 6 | 4 | Ingestion, Little's MCAR, reverse-coding from 4,880 registry; **raw data strictly immutable** |
| 6 | `data-curator` | Dataset Quality Diagnostics, Outlier & Missing Data Specialist | `flash` | 6 | 3 | Multivariate outliers ($D^2$), unengaged responses, data dictionary; **raw data immutable** |
| 7 | `statistics-agent` | Inferential Modeling, Parametric Hypothesis Testing & SEM Specialist | `flash` | 6 | 6 | **Strict execution only ("The Hands")**; executes analysis plans; plan design forbidden |
| 8 | `psychometric-expert` | Psychometric Resolution, Classical Test Theory & IRT Specialist | `flash` | 6 | 4 | CVR/CVI, CFA loadings, AVE/CR, IRT Graded Response; no general chapter drafting |
| 9 | `longitudinal-modmed-expert` | 3-Wave Longitudinal Moderated Mediation Specialist | `flash` | 6 | 3 | 3-wave autoregressive controls ($T_1 \to T_2 \to T_3$), bootstrap index; no cross-sectional |
| 10 | `intervention-designer` | Clinical Protocol, Manualization & Fidelity Sheet Specialist | `pro` | 5 | 2 | Manualized clinical sessions & fidelity grids; **critic/protocol: NO `run_command`** |
| 11 | `qualitative-analyst` | Reflexive Thematic Analysis & Grounded Theory Specialist | `pro` | 6 | 1 | Braun & Clarke 6-phase analysis, Strauss & Corbin Grounded Theory, inter-coder $\kappa$ |
| 12 | `validation-agent` | Independent Quality Assurance & Pre-Flight Release Gatekeeper | `flash` | 6 | 2 | Master validator suite, Triad Invariant verification, schema compliance; no self-validation |
| 13 | `results-auditor` | APA 7 Formatting, Mathematical Precision & Typography Auditor | `flash` | 5 | 2 | APA 7 typography, Persian leading zero (`۰.۰۵`), OMML math; **critic: NO `run_command`** |
| 14 | `statistical-auditor` | Parametric Assumptions, Degrees of Freedom & MSAI Anomaly Auditor | `flash` | 6 | 2 | $df$ vs $N$ concordance, assumption audit, MSAI scoring; no single-signal fraud claims |
| 15 | `academic-challenger` | Adversarial Methodology, Bias & Statistical Challenger | `pro` | 5 | 2 | **NEW**: Red-teaming, p-hacking, publication bias, 10 harsh viva voce questions; **critic: NO `run_command`** |

---

## 3. Legacy Agent Deprecation Register: `writing-agent`

### Background
In the legacy AcademicSuite implementation, `writing-agent` served as a monolithic writing and formatting worker. In the target architecture, writing responsibilities are formally elevated to the durable agent `academic-writer` (Tier 1 Authority), supported by specialized subagents (`journal-strategist`, `results-auditor`, `validation-agent`).

### Current Status
- **Status:** `DEPRECATED (PRESERVED FOR COMPATIBILITY)`
- **Physical Location:** `.agents/agents/writing-agent/` (Directory form with `agent.md`, `contract.md`, and symlink `.agents/agents/writing-agent.md`)
- **Reason for Retention:** Multiple components in the execution layer (`scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`, `tests/test_task_router.py`, `tests/test_routing_tiers.py`) route drafting queries to `writing-agent`. Deleting or removing this agent immediately would break routing unit tests and CLI operations.
- **Retirement Roadmap:**
  1. **Phase 5 (Current):** Retain `writing-agent` with full backward compatibility; document in inventory and deprecation report.
  2. **Phase 6 (Routing Modernization):** Update `academic_task_router.py` and `orchestrator_dependency_resolver.py` to route drafting tasks to `academic-writer`.
  3. **Phase 7 (Final Cleanup):** Once all routing references and test assertions are redirected to `academic-writer`, archive `writing-agent` into `legacy/` and remove from active directories.

---

## 4. Verification Matrix

| Verification Check | Target | Result | Status |
|---|---|---|---|
| Directory Packaging | 15 specialist subagents | 15 directories on disk | ✅ PASS |
| Co-located `agent.md` | 15 files with canonical YAML | 15 files verified | ✅ PASS |
| Co-located `contract.md` | 12 constitutional sections | 15 files verified | ✅ PASS |
| Relative Discovery Symlinks | `.agents/agents/<name>.md` | 15 symlinks resolving | ✅ PASS |
| Zero Deprecated Fields | Zero `command_execution_policy` | 0 occurrences | ✅ PASS |
| Least Privilege: Tools | Zero delegation tools in workers | 0 found | ✅ PASS |
| Least Privilege: Delegation | `agents: []` across all workers | 15 verified empty | ✅ PASS |
| Critics Tool Constraints | NO `run_command` for critics | 3 critics verified | ✅ PASS |
| Master Test Suite | All tests in `run_tests.py` | 185/185 Passed (0 Failures) | ✅ PASS |
