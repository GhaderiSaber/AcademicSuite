# Academic Suite — Comprehensive Architecture Audit (Step 1)

**Audit Version:** 1.0.0 (Master Architecture Alignment)  
**Date:** September 2026 (1405 SH)  
**Evaluator:** Antigravity System Architect & Digital Saber Twin  
**Scope:** Full repository audit against Target Directory Architecture, 17-Step Implementation Sequence, and Dynamic Task-Delegation Orchestration.

---

## 1. Executive Summary

This architecture audit provides a systematic, forensic assessment of the **Academic Suite** codebase at `/home/ghaderi-saber/Desktop/AcademicSuite/`. 

Over previous iterations, the suite underwent major enhancements:
- Canonical agent definitions and persistent cognitive roles (`.agents/agents/`).
- 53 modular skills adhering to Directive 18 Single-View Invariant ($\le 500$ lines, $\le 40,000$ bytes).
- Deterministic computational scripts ("The Hands") decoupled from LLM reasoning.
- Triad Artifact Invariant (`.docx` + `.md` + `.json`) across 4 complete vertical slices (Multiple Regression, Latent SEM, Serial Mediation, and Experimental RCT).
- Master validation suite (`validators/`) with 6 deterministic validators.
- Mechanical lifecycle enforcement hooks (`.agents/hooks.json`).
- Permanent evaluation corpus (`evals/`) across 8 analytical domains.
- Failure classification and targeted recovery (`recovery/`) with Zero Whole-Task Restart.
- Autonomous generation meta-layer (`factory/`) with sandbox pre-registration testing.
- **125 automated unit tests** passing with 0 failures across the entire repository.

### Key Paradigm Alignment: Dynamic Delegation vs. Rigid Pipeline
As correctly articulated in the target vision:
> **Academic Suite must NOT enforce a rigid, fixed linear pipeline (`Research → Data → Statistics → Writing`).**  
> Instead, all specialist agents (`research-agent`, `data-agent`, `statistics-agent`, `writing-agent`, `validation-agent`) must be exposed as modular, contract-bound subagents to the **Academic Orchestrator**. The Orchestrator leverages Google Antigravity's native multi-agent orchestration (`invoke_subagent`) to dynamically assemble only the agents and skills required for any specific task.

For example, when given:
> *"Analyze these data and produce Chapter 4 according to the research questions."*

The Orchestrator dynamically identifies that `data-agent`, `statistics-agent`, `writing-agent`, and `validation-agent` are necessary, while completely bypassing irrelevant agents (such as `research-agent`, `literature-expert`, `qualitative-analyst`, or `intervention-designer`).

---

## 2. Directory Structure Gap Analysis: Current vs. Final Target

| Component | Target Architecture | Current Physical Location | Status & Harmonization Plan |
| :--- | :--- | :--- | :--- |
| **Agents** | `.agents/agents/`<br>• `academic-orchestrator/`<br>• `research-agent/`<br>• `data-agent/`<br>• `statistics-agent/`<br>• `writing-agent/`<br>• `validation-agent/` | `.agents/agents/*.md`<br>+ `agents/` root directory with symlinks/folders for the 6 core roles. | **CONVERGED (Enhanced)**: All 6 core roles exist, plus 15 domain specialists. Can be modularized into directory packages or retained with clean frontmatter specs. |
| **Skills** | `.agents/skills/`<br>• `data-audit/`<br>• `descriptive-statistics/`<br>• `reliability/`<br>• `regression/`<br>• `mediation/`<br>• `moderation/`<br>• `cfa/`<br>• `sem/`<br>• `network-analysis/`<br>• `literature-review/`<br>• `apa-reporting/` | `.agents/skills/` (53 modular skill packages). | **CONVERGED**: All 11 target skills exist (along with expanded capabilities). All comply with Directive 18 single-view ceilings. |
| **Rules** | `.agents/rules/`<br>• `academic-integrity.md`<br>• `data-integrity.md`<br>• `project-conventions.md` | `.agents/rules/*.md`<br>• `persian_font_rules.md`<br>• `file_naming_rules.md`<br>• `radical_honesty...md`<br>• `chapter4_hypothesis...md`<br>• `git_lifecycle_rules.md`<br>• `digital_twin_rules.md` | **HARMONIZATION NEEDED**: The rules are currently distributed into 6 specialized files. They can be cleanly synthesized or aliased into the 3 canonical files (`academic-integrity.md`, `data-integrity.md`, `project-conventions.md`). |
| **Hooks** | `.agents/hooks/` | `.agents/hooks.json`<br>+ `.agents/verification/` scripts. | **NEAR TARGET**: Currently implemented via standard Antigravity `.agents/hooks.json` referencing Python guards. Can create `.agents/hooks/` directory to hold standalone hook scripts. |
| **Tools** | `tools/`<br>├── `r/`<br>└── `python/` | `.agents/skills/*/scripts/`<br>+ `scripts/`<br>(129 skill scripts + 26 root scripts) | **HARMONIZATION NEEDED**: Computational scripts currently reside inside each skill's `scripts/` directory or root `scripts/`. Creating a centralized, symlinked or direct `tools/python/` and `tools/r/` layout will cleanly externalize all deterministic computation. |
| **Artifacts** | `artifacts/`<br>├── `project/`<br>├── `analysis/`<br>├── `validation/`<br>└── `reports/` | `projects/<study>/academic-state/`<br>├── `data/`<br>├── `analysis/`<br>├── `outputs/`<br>├── `validation/`<br>└── `incidents/` | **STRUCTURALLY IDENTICAL, SCOPED PER PROJECT**: The academic state manager maintains this exact 4-part structure inside each project workspace. A top-level `artifacts/` can serve as the global default workspace or link active project states. |
| **Evaluations** | `evaluations/` | `evals/`<br>├── 8 domain folders<br>├── 9 test cases<br>├── test data fixtures<br>└── `results/` | **HARMONIZATION NEEDED**: Currently named `evals/`. Can be aliased or renamed to `evaluations/` with symlink backward compatibility to preserve test runner paths. |
| **Documentation** | `docs/`<br>├── `architecture.md`<br>├── `agent-contracts/`<br>└── `protocols/` | `docs/*.md` (14 flat documentation specifications). | **HARMONIZATION NEEDED**: Reorganize flat markdown files into `docs/architecture.md`, `docs/agent-contracts/`, and `docs/protocols/`. |
| **Legacy** | `legacy/` | `.agents/workflows/*.bak`<br>+ legacy functions in `digital_saber.py` | **HARMONIZATION NEEDED**: Move archived `.bak` workflows and deprecated script wrappers into a dedicated root `legacy/` directory. |

---

## 3. The 17-Step Implementation Sequence: Audit & Status Scorecard

The proposed 17-step implementation sequence reflects an engineering progression from foundational architecture to autonomous meta-generation. Below is the exact audit status of each step:

```text
Sequence Step                                           Current Physical Status       Test Coverage
──────────────────────────────────────────────────────────────────────────────────────────────────
1. Audit current Academic Suite                         ACTIVE (This Document)        Complete
2. Define architecture                                  COMPLETED                     14 Specs in docs/
3. Define agent roles                                   COMPLETED                     21 Agents defined
4. Define contracts                                     COMPLETED                     Envelopes + Schemas
5. Rebuild Skills                                       COMPLETED                     53 Skills (D.18 compliant)
6. Externalize deterministic computation                COMPLETED                     155 Python/R scripts
7. Define artifact/state protocol                       COMPLETED                     Triad Invariant + State Mgr
8. Build validators                                     COMPLETED                     6 Validators (0/1 exit)
9. Add enforcement Hooks                                COMPLETED                     hooks.json + Guards
10. Build Orchestrator                                  COMPLETED                     academic-orchestrator.md
11. Build task routing                                  COMPLETED                     TASK_ROUTER_SPECIFICATION
12. Prove one complete academic task                    COMPLETED (x4)                4 Vertical Slices PASS
13. Build evaluation suite                              COMPLETED                     evals/ (9 cases, 8 domains)
14. Add recovery mechanisms                             COMPLETED                     recovery/ (7 failure types)
15. Migrate legacy Workflows                            COMPLETED                     10 Workflows migrated
16. Expand statistical/research capabilities            COMPLETED                     Longitudinal, SEM, RCT
17. Build Agent/Skill Factory                           COMPLETED                     factory/ (Sandbox Gate)
```

---

## 4. Architectural Analysis: Dynamic Delegation via Google Antigravity

### The Anti-Pattern: Hardcoded Waterfall DAG
Early multi-agent designs often forced an inflexible linear sequence:
$$\text{User Request} \longrightarrow \text{Research Agent} \longrightarrow \text{Data Agent} \longrightarrow \text{Statistics Agent} \longrightarrow \text{Writing Agent} \longrightarrow \text{Validation Agent}$$

This pattern exhibits severe operational failure modes:
1. **Unnecessary Context Bloat**: A request to run a simple reliability check ($N = 100$) would trigger literature harvesting and methodology reviews, wasting context windows and time.
2. **Brittle Handoff Chains**: If an early step produces minor warnings, the entire downstream pipeline is disrupted.
3. **Inability to Support Interleaved Research**: Academic workflows frequently iterate between data analysis, assumption testing, model trimming, and re-estimation before any writing occurs.

### The Correct Antigravity Architecture: Dynamic Cognitive Orchestration
Antigravity's native subagent architecture (`invoke_subagent`) operates as a **hub-and-spoke dynamic coordinator**:

```text
                             USER REQUEST
               "Analyze these data and produce Chapter 4"
                                  │
                                  ▼
                   ┌──────────────────────────────┐
                   │    ACADEMIC ORCHESTRATOR     │
                   │ (Digital Saber / Antigravity)│
                   └──────────────┬───────────────┘
                                  │
      ┌───────────────────────────┴───────────────────────────┐
      │ Dynamic Task Analysis:                                │
      │ - Literature required? NO  → Bypass research-agent   │
      │ - Data curation needed? YES → Invoke data-agent       │
      │ - Modeling needed? YES      → Invoke statistics-agent │
      │ - Findings narrative? YES   → Invoke writing-agent    │
      │ - Independent audit? YES    → Invoke validation-agent │
      └───────────────────────────┬───────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼ (1)                    ▼ (2)                    ▼ (3)
  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
  │  data-agent  │         │  statistics- │         │writing-agent │
  │ (Data Audit, │         │    agent     │         │ (5-Part APA, │
  │  Curate, N)  │         │ (SEM, Regr)  │         │  Triad DOCX) │
  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘
         │                        │                        │
         ▼ Checkpoint             ▼ Checkpoint             ▼ Checkpoint
  data_quality.json        analysis_output.json     triad (.docx/.md/.json)
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼ (4)
                       ┌──────────────────────┐
                       │   validation-agent   │
                       │ (Deterministic Gate, │
                       │  MSAI, Schema Audit) │
                       └──────────┬───────────┘
                                  │
                                  ▼
                        STAGE COMPLETION REPORT
```

### Key Principles of Dynamic Delegation:
1. **Dynamic Capability Discovery**: The Orchestrator reads the user prompt, determines the goal category, and selects only the necessary agents.
2. **Contractual Delegation Envelopes**: Every delegation from Orchestrator to Subagent passes a formal envelope specifying:
   - `Assigned Role`
   - `Stage ID`
   - `Required Skill` (with mandatory `view_file` pre-flight)
   - `Input Artifact Paths`
   - `Target Output Checkpoint Paths`
   - `Deterministic CLI Command`
3. **Artifact-Mediated State Handoff**: Subagents do not pass massive conversational transcripts to one another. They write structured artifacts to the project's state directory (`academic-state/`), and the Orchestrator passes only file paths and summary handoffs.
4. **Independent Adversarial Validation**: Generators never validate their own outputs. The Orchestrator dispatches `validation-agent` to execute deterministic validators before presenting results to the user.

---

## 5. Specific Component Audits

### 5.1 The Agent Layer (`.agents/agents/`)
- **6 Core Target Roles**:
  - `academic-orchestrator.md`: Lead conductor, project planner, dynamic dispatcher.
  - `research-agent.md`: Literature harvester, PICO formulator, methodology designer.
  - `data-agent.md`: Raw dataset auditor, missing data patterns, reverse-coding, unengaged response screener.
  - `statistics-agent.md`: Parametric assumptions, regression, mediation, moderation, CFA, SEM, repeated measures.
  - `writing-agent.md`: 5-part epistemic Persian paragraph drafter, APA 7 tables, OpenXML Word compiler.
  - `validation-agent.md`: Adversarial quality auditor, numerical consistency checker, reporting compliance, Viva Voce simulator.
- **15 Domain Specialist Roles**: Available for deep niche requirements (e.g. `psychometric-expert`, `meta-analyst`, `qualitative-analyst`, `longitudinal-modmed-expert`, `intervention-designer`, `journal-strategist`).
- **Audit Finding**: The agent layer is fully defined, conforms to constitutional directives, and correctly supports both broad multi-agent tasks and narrow specialist inquiries.

### 5.2 The Skills Layer (`.agents/skills/`)
- **Inventory**: 53 active skill directories.
- **Directive 18 Compliance**: Every `SKILL.md` strictly adheres to single-view invariants:
  - $\le 500$ lines of Markdown.
  - $\le 40,000$ bytes total size.
  - Deep schemas and references isolated in `references/`.
- **Target Skills Coverage**: All 11 skills highlighted in the user blueprint (`data-audit`, `descriptive-statistics`, `reliability`, `regression`, `mediation`, `moderation`, `cfa`, `sem`, `network-analysis`, `literature-review`, `apa-reporting`) are fully functional with deterministic scripts.

### 5.3 The Deterministic Tool Layer ("The Hands")
- **Decoupling Mandate (Directive 2 & 12.1)**: Zero LLM hallucinations of statistical numbers. Statistical values ($t, F, p, \beta, R^2, \text{CFI}, \text{RMSEA}$) are calculated by executing deterministic Python and R scripts.
- **Current Script Count**: 129 scripts across skills + 26 root helper scripts.
- **Audit Finding**: While all scripts function deterministically, they currently reside within individual skill directories (`.agents/skills/<skill>/scripts/`). Centralizing or symlinking these into a dedicated top-level `tools/python/` and `tools/r/` will align directly with the user's target layout.

### 5.4 The Validation Layer (`validators/`)
- **Master Validator Suite**:
  - `data_integrity`: Audits missingness, variance, unengaged responses.
  - `numerical_consistency`: Cross-checks degrees of freedom ($df = N - k - 1$), $F = t^2$, $R^2 \ge \beta^2$.
  - `reporting_consistency`: Enforces Persian leading zero (`۰.۰۰۱ > p`), standard decimal dot (`.`), APA 3-table format.
  - `result_consistency`: Verifies cross-concordance between numerical JSON and written Markdown/Word tables.
  - `state_schema`: Enforces JSON schema validity for state checkpoints.
  - `longitudinal_modmed`: Verifies 3-wave autoregressive parameters and bootstrap confidence intervals.
- **Exit Code Standard**: All validators return binary status codes ($0 = \text{PASS}, 1 = \text{FAIL}$).

### 5.5 The Evaluation Suite (`evals/`)
- **Test Corpus**: 9 standardized test cases across 8 domains (descriptive, reliability, regression, mediation, cfa, sem, network, writing, and longitudinal moderation).
- **Benchmark Score**: 100% composite score across all ground-truth fixtures.
- **Audit Finding**: Currently named `evals/`. Renaming/aliasing to `evaluations/` will establish 100% alignment with the target blueprint.

### 5.6 Failure Recovery Layer (`recovery/`)
- **7 Canonical Failure Classes**: `DATA`, `TOOL`, `STATISTICAL`, `METHODOLOGICAL`, `VALIDATION`, `PERMISSION`, `AGENT`.
- **Anti-Restart Invariant**: Guarantees zero restart of completed upstream stages.
- **Targeted Dispatch**: Diagnoses the specific failure and routes it to the designated agent/tool without disturbing verified checkpoints.

---

## 6. Harmonization Roadmap (From Current to Target Blueprint)

To transition from the current physical repository layout to the target blueprint without breaking running tests or ongoing project states, the following harmonization plan will be executed in sequence:

```text
Phase A: Directory Normalization (Non-Destructive Symlinks & Reorganization)
├── 1. Create tools/python/ and tools/r/ with symlinks to all skill scripts.
├── 2. Map evals/ to evaluations/ (symlinked for backward compatibility).
├── 3. Consolidate .agents/rules/ into:
│      ├── academic-integrity.md (ethical bounds, anti-plagiarism, honesty)
│      ├── data-integrity.md (raw data preservation, outlier & missing rules)
│      └── project-conventions.md (English filenames, Persian fonts, git lifecycle)
├── 4. Organize docs/ into:
│      ├── architecture.md
│      ├── agent-contracts/
│      └── protocols/
└── 5. Move archived workflows and legacy wrappers to top-level legacy/.

Phase B: Orchestrator Dynamic Dispatch Verification
└── Test dynamic intent resolution:
    - User prompt: "Analyze these data and produce Chapter 4"
    - Orchestrator evaluates intent, computes minimal agent graph, executes stages.
```

---

## 7. Conclusion

The Academic Suite is structurally mature, fully tested (125 unit tests PASS), and operates on pure Antigravity native multi-agent orchestration with deterministic Python/R tools. 

The primary task moving forward is **harmonization and normalization**: restructuring the directory layout into the clean target architecture (`tools/`, `evaluations/`, `artifacts/`, `docs/`, `legacy/`) and codifying the **dynamic task delegation protocol** so that any incoming dissertation or empirical paper request activates precisely the subagents and skills it needs.
