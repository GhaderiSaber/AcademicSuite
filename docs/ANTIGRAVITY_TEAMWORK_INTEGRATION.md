# AcademicSuite & Native Antigravity Teamwork Integration Architecture

This document defines the formal integration boundary between **AcademicSuite** and **native Antigravity Teamwork**.

---

## 1. Core Architectural Philosophy: Domain Pattern vs. Runtime

Antigravity natively provides an autonomous multi-agent Teamwork runtime (`/teamwork-preview`) optimized for complex software projects, massive research sweeps, and long-running distributed workflows. It provides structured planning, concurrent worker dispatching, isolated git/workspace trees (`branch`/`share`), and background verification.

**AcademicSuite does NOT duplicate or replace Antigravity's runtime orchestration.** Instead, AcademicSuite provides the **DOMAIN PATTERN**: research contracts, psychometric models, deterministic statistical tools ("The Hands"), artifact schemas, forensic auditing, and academic defense acceptance criteria.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ANTIGRAVITY TEAMWORK RUNTIME                          │
│  - Dynamic Team Formation             - Concurrent Worker Management        │
│  - Isolated Workspaces (branch/share) - Runtime Orchestration & Task Trees │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                         BOUNDARY CONTRACT (L0–L4)
                      contracts/teamwork_boundary.schema.json
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        ACADEMICSUITE DOMAIN PATTERN                         │
│  - Research Contracts & Plans         - Statistical Execution ("The Hands") │
│  - Artifact Schemas & Triad Invariant - Multi-Signal Anomaly Index (MSAI)  │
│  - Raw Dataset Provenance (SHA-256)   - Viva Voce Defense Simulator         │
│  - Academic Acceptance Criteria       - Human Approval Gate (Saber Desk)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ownership Boundary: What Crosses the Interface

To prevent architectural bleeding, responsibilities are partitioned strictly:

### A. AcademicSuite Owns (Domain Governance)
1. **Research Contracts**: Authoritative JSON schemas (`analysis_plan.schema.json`, `execution_manifest.schema.json`, `milestone_state.schema.json`).
2. **Analysis Plans**: Mandatory, pre-registered analytical specifications before empirical execution.
3. **Artifact Schemas & Triad Invariant**: Mandatory generation of synchronized `.docx`, `.md`, and `.json` artifacts per micro-stage.
4. **Dataset Provenance**: Cryptographic SHA-256 fingerprinting, schema validation, and read-only enforcement (`0444`).
5. **Statistical Execution**: Deterministic calculation scripts in `.agents/skills/<skill>/scripts/` ("The Hands"). Mental statistical hallucination is prohibited under Directive 2.
6. **Validation & Auditing**: Multi-Signal Anomaly Index (MSAI), degree-of-freedom checking, 3-table standard, and Persian typography standards.
7. **Academic Acceptance Criteria**: Institutional thesis and doctoral committee readiness standards.
8. **Human Approval**: Saber Admin Desk (`124911145`) approval gates for high-stakes deliverables.

### B. Antigravity Teamwork Owns (Runtime Execution)
1. **Dynamic Team Formation**: Sizing and mobilizing autonomous subagents according to task complexity and capability requirements.
2. **Concurrent Worker Management**: Scheduling parallel tasks and background execution loops without deadlock.
3. **Isolated Workspaces**: Managing workspace sandboxes (`Workspace: 'branch' | 'share'`) to prevent dirty state collisions.
4. **Runtime Task Orchestration**: Managing runtime task trees, retry policies, and step execution.

---

## 3. Complexity Levels (L0 to L4)

AcademicSuite categorizes tasks into 5 graduated complexity levels, determining the degree of multi-agent mobilization:

| Level | Scope | Description | Team Formation Mode | Workspaces | Slash Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **L0** | Simple Question | Conceptual inquiries, terminology queries, APA rule lookups without data analysis. | `none` (no subagent team needed) | Inherit | None |
| **L1** | Single Analysis | Single bounded statistical or psychometric calculation on approved data. | `bounded_single` (1 Worker) | Inherit | None |
| **L2** | Multi-Analysis Project | Interdependent models (e.g. ANCOVA + mediation, SEM + CFA, multiple regression with assumptions). | `sequential_audited` (Explorer + Worker + Challenger + Auditor) | Inherit | None |
| **L3** | Thesis/Paper Milestone | Full milestone workflow (Chapter 4 Findings, Scale Validation study, PRISMA Review, Proposal). | `full_milestone_pipeline` (Full AcademicSuite micro-stage sequence) | Inherit / Stage Dirs | None |
| **L4** | Full Research Project | 20-chapter monograph overhaul, multi-wave longitudinal panel, repository-wide empirical reorganization. | `dynamic_teamwork` (Dynamic multi-agent team) | `branch` / `share` (Isolated) | `/teamwork-preview` |

---

## 4. Teamwork-Style Role Mappings

Antigravity Teamwork's abstract multi-agent roles map directly to AcademicSuite cognitive specializations. **Worker counts are never hard-coded; they adapt dynamically to the resolved capability DAG:**

| Teamwork Role | AcademicSuite Cognitive Role | Primary Responsibilities | Associated Skills |
| :--- | :--- | :--- | :--- |
| **Explorer** | `data-agent`, `research-agent`, `methodology-expert`, `data-curator`, `literature-expert` | Ingest and screen raw data, verify SHA-256 provenance, harvest literature, formulate inverted-triangle research problem. | `data-audit`, `data-cleaning`, `methodology-review`, `literature-harvester` |
| **Worker** | `statistics-agent`, `academic-writer`, `psychometric-expert`, `qualitative-analyst`, `meta-analyst` | Execute deterministic Python/R mathematical scripts ("The Hands"), compile OpenXML triads (`.docx`, `.md`, `.json`), format tables. | `statistical-data-analyst`, `chapter-4-writing`, `cfa`, `sem`, `regression` |
| **Critic** | `results-auditor`, `validation-agent`, `evidence-auditor` | Audit APA 7 table borders, verify degree-of-freedom consistency, check Persian typography (leading zeros `۰.۰۰۱`, B Nazanin), reconcile citations. | `apa-reporting`, `thesis-integrity-auditor` |
| **Challenger** | `academic-challenger` | Adversarially probe parametric assumptions, detect synthetic sample-data leakage, and audit/log findings in `state/pitfalls.jsonl`. | `assumption-testing` |
| **Auditor** | `statistical-auditor`, `thesis-integrity-auditor` | Calculate Multi-Signal Anomaly Index (MSAI), audit variance deflation, check effect size inflation, and verify mathematical reproducibility. | `contracts/validation_report.schema.json`, `data-audit` |
| **Success Auditor** | `final-judge` | Conduct Viva Voce defense simulation, evaluate dissertation readiness across all 5 chapters, and issue institutional pass/fail verdict. | `Layer 5: Quality Control & Defense Committee` |

---

## 5. The Boundary Contract (`contracts/teamwork_boundary.schema.json`)

When an L4 project is initiated or a boundary package is requested, `scripts/teamwork_boundary_adapter.py` emits an authoritative, schema-validated payload.

### Boundary Schema Structure
```json
{
  "boundary_version": "1.0.0",
  "task_id": "task_longitudinal_burnout_overhaul",
  "task_description": "Execute 3-wave longitudinal moderated mediation across 5 hospital cohorts",
  "complexity_level": "L4",
  "governance": {
    "research_contracts": ["analysis_plan", "execution_manifest", "validation_report", "milestone_state"],
    "analysis_plan_required": true,
    "artifact_schemas": ["artifact_manifest", "validation_report", "pitfall"],
    "provenance_required": true,
    "statistical_execution_contract": "deterministic_hands_only",
    "validation_rules": [
      "directive_0_binary_honesty",
      "directive_3_triad_invariant",
      "directive_6_english_filenames",
      "msai_anomaly_threshold",
      "three_table_standard"
    ],
    "academic_acceptance_criteria": [
      "Strict APA 7th edition table formatting (zero vertical borders)",
      "Persian leading zero retention (۰.۰۰۱)",
      "Decoupled LTR numeric values with Times New Roman",
      "Multi-Signal Anomaly Index (MSAI) < 0.60",
      "Zero synthetic sample leakage into production deliverables"
    ],
    "human_approval_required": true
  },
  "teamwork_runtime": {
    "team_formation_mode": "dynamic_teamwork",
    "isolated_workspaces": true,
    "recommended_slash_command": "/teamwork-preview",
    "role_roster": [
      {
        "teamwork_role": "Explorer",
        "academicsuite_agent": "data-agent",
        "purpose": "Verify raw dataset provenance, schema integrity, and explore variable distributions.",
        "required_skills": ["data-audit", "data-cleaning"],
        "workspace_mode": "branch"
      },
      {
        "teamwork_role": "Worker",
        "academicsuite_agent": "statistics-agent",
        "purpose": "Execute deterministic statistical engines and OpenXML triad compilation.",
        "required_skills": ["statistical-data-analyst", "longitudinal-moderated-mediation"],
        "workspace_mode": "branch"
      },
      {
        "teamwork_role": "Challenger",
        "academicsuite_agent": "academic-challenger",
        "purpose": "Adversarially challenge methodological validity, detect sample leakage, and log to state/pitfalls.jsonl.",
        "required_skills": ["assumption-testing"],
        "workspace_mode": "branch"
      },
      {
        "teamwork_role": "Auditor",
        "academicsuite_agent": "statistical-auditor",
        "purpose": "Forensic audit of effect sizes, variance deflation, and Multi-Signal Anomaly Index (MSAI).",
        "required_skills": ["data-audit", "apa-reporting"],
        "workspace_mode": "branch"
      },
      {
        "teamwork_role": "Success Auditor",
        "academicsuite_agent": "final-judge",
        "purpose": "Simulate doctoral Viva Voce defense committee and issue institutional acceptance verdict.",
        "required_skills": ["thesis-integrity-auditor"],
        "workspace_mode": "branch"
      }
    ],
    "max_concurrent_workers": null
  },
  "deliverables": {
    "expected_triads": [".docx", ".md", ".json"],
    "output_directory": "projects/task_longitudinal_burnout_overhaul/03_deliverables"
  }
}
```

---

## 6. CLI Tools & Developer Usage

### A. Classifying Complexity (L0 to L4)
```bash
python3 scripts/teamwork_boundary_adapter.py classify \
  --description "Analyze dataset with ANCOVA and bootstrap mediation" \
  --chapter-count 1 \
  --file-count 5
```

### B. Building a Validated Teamwork Boundary Package
```bash
python3 scripts/teamwork_boundary_adapter.py package \
  --description "Restructure 20-chapter monograph with thousands of source files" \
  --chapter-count 20 \
  --file-count 120 \
  --output state/teamwork_boundary_manifest.json
```

### C. Capability Resolver Boundary Inspection
```bash
python3 scripts/academic_task_router.py resolve \
  "Run 3-wave longitudinal moderated mediation" \
  --teamwork-boundary
```
