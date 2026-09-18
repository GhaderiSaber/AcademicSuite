# AcademicSuite Current Dependency Graph & Orchestration Topology (02_CURRENT_DEPENDENCY_GRAPH.md)

**Document Version:** 1.0.0  
**Status:** READ-ONLY BASELINE AUDIT COMPLETE  
**Operative Temporal Reality:** 2026 (1405 SH)  

---

## 1. Architectural Topology Overview

The AcademicSuite repository currently contains two distinct, co-existing dependency subsystems:
1. **The Script-Wired Core 6 Execution Pipeline**: Governed by deterministic Python scripts (`academic_task_router.py`, `orchestrator_dependency_resolver.py`, `academic_state_manager.py`) and wired into vertical slice tests.
2. **The Contractual 16-Specialist Cognitive Deliberation Mesh**: Governed by behavioral contracts (`contract.md`), architectural specifications (`HYBRID_MULTI_AGENT_SPEC.md`), and the Adversarial Critic Protocol (`ADVERSARIAL_CRITIC_PROTOCOL.md`).

```
                              ┌─────────────────────────┐
                              │      USER / CLIENT      │
                              └────────────┬────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────┐
                              │   digital-saber (Twin)  │
                              │  [Principal Authority]  │
                              └────────────┬────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
       ┌─────────────────────────┐                   ┌─────────────────────────┐
       │  academic-orchestrator  │                   │    16 Cognitive Roles   │
       │   [Execution Conductor] │                   │   [Deliberation Mesh]   │
       └────────────┬────────────┘                   └────────────┬────────────┘
                    │                                             │
      ┌─────────────┼─────────────┐                  ┌────────────┼────────────┐
      ▼             ▼             ▼                  ▼            ▼            ▼
 [research]     [data]      [statistics]       [methodology] [statistical] [psychometric]
  -agent        -agent         -agent             -expert       -expert       -expert
      │             │             │                  │            │            │
      └─────────────┬─────────────┘                  └────────────┼────────────┘
                    ▼                                             ▼
             [writing-agent]                               [academic-writer]
                    │                                             │
                    ▼                                             ▼
            [validation-agent]                        [Adversarial Critic Quad]
                                                      ├─ statistical-auditor
                                                      ├─ results-auditor
                                                      ├─ evidence-auditor
                                                      └─ final-judge
```

---

## 2. Inbound & Outbound Dependency Matrix

| Agent Name | Inbound Callers / References | Outbound Invocations / Target Handoffs | Direct Script Bindings | Vertical Slice Tests |
| :--- | :--- | :--- | :--- | :---: |
| **`academic-orchestrator`** | `validation-agent` (return handoff) | `research-agent`, `data-agent`, `statistics-agent`, `writing-agent`, `validation-agent` | `academic_state_manager.py`, `orchestrator_dependency_resolver.py` | 2 |
| **`academic-writer`** | `digital-saber` | `results-auditor`, `evidence-auditor` | *None* | 1 |
| **`data-agent`** | `academic-orchestrator`, `statistics-agent` | `statistics-agent`, `validation-agent` | `academic_task_router.py`, `orchestrator_dependency_resolver.py` | 5 |
| **`data-curator`** | `digital-saber` | `statistical-expert`, `validation-agent` | *None* | 1 |
| **`digital-saber`** | External Clients (Telegram, CLI) | `methodology-expert`, `statistical-expert`, `data-curator`, `statistical-auditor`, `results-auditor`, `evidence-auditor`, `academic-writer`, `final-judge` | `digital_saber.py`, `attach_telegram_client.py` | 1 |
| **`evidence-auditor`** | `digital-saber`, `literature-expert` | *Terminal Critic* (reports to `digital-saber`) | *None* | 1 |
| **`final-judge`** | `digital-saber` | *Terminal Gatekeeper* (releases to `digital-saber`) | *None* | 2 |
| **`intervention-designer`** | `digital-saber` | `validation-agent` | *None* | 1 |
| **`journal-strategist`** | `digital-saber` | `results-auditor` | *None* | 1 |
| **`literature-expert`** | `academic-writer` | `evidence-auditor` | *None* | 1 |
| **`longitudinal-modmed-expert`** | `digital-saber` | `validation-agent` | `factory/specialist_manifest.json` | 2 |
| **`meta-analyst`** | `research-agent`, `statistics-agent` | `validation-agent` | *None* | 1 |
| **`methodology-expert`** | `digital-saber` | `validation-agent`, `statistical-expert` | *None* | 1 |
| **`psychometric-expert`** | `digital-saber` | `validation-agent` | *None* | 1 |
| **`qualitative-analyst`** | `digital-saber` | `validation-agent` | *None* | 1 |
| **`research-agent`** | `academic-orchestrator` | `statistics-agent`, `writing-agent`, `validation-agent` | `academic_task_router.py`, `orchestrator_dependency_resolver.py` | 3 |
| **`results-auditor`** | `academic-writer`, `digital-saber`, `journal-strategist` | *Terminal Critic* (reports to `digital-saber`) | *None* | 1 |
| **`statistical-auditor`** | `digital-saber`, `statistical-expert` | *Terminal Critic* (reports to `digital-saber`) | *None* | 2 |
| **`statistical-expert`** | `digital-saber`, `methodology-expert` | `statistical-auditor`, `academic-writer` | *None* | 3 |
| **`statistics-agent`** | `academic-orchestrator`, `data-agent` | `writing-agent`, `validation-agent` | `academic_task_router.py`, `orchestrator_dependency_resolver.py`, `academic_state_manager.py` | 5 |
| **`validation-agent`** | Referenced by 13 contracts & `academic-orchestrator` | `academic-orchestrator` (loop handoff) | `academic_task_router.py`, `orchestrator_dependency_resolver.py` | 4 |
| **`writing-agent`** | `academic-orchestrator`, `research-agent`, `statistics-agent` | `validation-agent` | `academic_task_router.py`, `orchestrator_dependency_resolver.py` | 5 |

---

## 3. Circular Dependencies & Handoff Loops

### Circular Loop: `academic-orchestrator` $\rightleftarrows$ `validation-agent`
- **Mechanism**:
  1. `academic-orchestrator` delegates verification to `validation-agent`.
  2. `validation-agent` runs deterministic validators.
  3. `validation-agent/contract.md` states: `"HANDOFF FORMAT: validation-agent hands off certified reports back to academic-orchestrator"`.
  4. If validation returns `FAIL`, `academic-orchestrator` must trigger a retry loop or route back to the producing agent.
- **Risk**: Without an explicit `max_retries` counter in the state JSON, an automated loop between conductor and validator can cause infinite turn recursion.

---

## 4. Shadow Orchestration Mechanisms

The repository contains three legacy deterministic orchestration engines that duplicate native Antigravity functionality:

### 4.1 Engine A: `scripts/academic_task_router.py`
- **Function**: CLI tool parsing free-text prompts with regexes and emitting an ordered JSON pipeline.
- **Flaws**:
  - Only recognizes 7 capabilities (`RESEARCH`, `METHODOLOGY`, `DATA`, `NETWORK-ANALYSIS`, `STATISTICS`, `WRITING`, `VALIDATION`).
  - Hardcoded to map strictly to the Core 6 agents (`research-agent`, `data-agent`, `statistics-agent`, `writing-agent`, `validation-agent`).
  - Completely oblivious to the 16 specialist roles in World B.
  - Imposes a rigid linear sequence (`EXECUTION_ORDER`) regardless of research design complexity.

### 4.2 Engine B: `scripts/orchestrator_dependency_resolver.py`
- **Function**: Prerequisite checker and Context Delegation Envelope generator.
- **Flaws**:
  - Implements an internal DAG (`STAGE_DEPENDENCIES`) that hardcodes 11 micro-stages.
  - Generates text blocks meant for `invoke_subagent`, but is executed as a standalone CLI script.
  - Ignores 17 of the 22 agents in its `CAPABILITY_REGISTRY`.

### 4.3 Engine C: `.agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py`
- **Function**: 49 KB batch script runner executing sequential Python/R scripts on disk.
- **Flaws**:
  - Embeds full workflow orchestration logic inside a Skill directory, violating the separation of Brains vs. Hands.
  - Defines 6 pre-baked pipeline presets (`thesis_empirical`, `scale_validation`, `qualitative_study`, `meta_analysis`, `thesis_to_publication`, `bibliometric_pipeline`).
  - Contains silent fallbacks to `info["default_sample"]` across 17 skills when input data is missing.

---

## 5. Complete Skill-to-Agent Binding Matrix (43 Skills)

| Skill Name | Declared by Agent Frontmatter | Declared in Agent Contracts | Primary CLI Script ("The Hands") |
| :--- | :--- | :--- | :--- |
| `academic-article-writer` | `academic-writer`, `intervention-designer`, `journal-strategist`, `meta-analyst`, `writing-agent` | Same | `article_compiler.py` |
| `academic-drive-project-organizer` | *None* (Unbound Skill) | *None* | `drive_organizer.py` |
| `academic-reference-extractor` | `literature-expert`, `validation-agent`, `evidence-auditor` | Same | `reference_extractor.py` |
| `academic-suite-orchestrator` | `academic-orchestrator`, `digital-saber` | Same | `orchestrator_cli.py` |
| `ai-academic-tone-polisher` | `academic-writer`, `journal-strategist`, `writing-agent` | Same | `tone_polisher.py` |
| `apa-reporting` | *None* (Unbound in FM) | `data-agent`, `statistics-agent`, `writing-agent` | `table_formatter.py` |
| `assumption-testing` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `verify_assumptions.py` |
| `bibliometric-network-analyst` | `literature-expert`, `research-agent` | Same | `bibliometric_analyst.py` |
| `cfa` | `psychometric-expert` | `statistical-expert`, `statistics-agent` | `run_cfa.py`, `cfa_lavaan.R` |
| `chapter-4-writing` | `academic-writer`, `digital-saber`, `longitudinal-modmed-expert`, `results-auditor`, `statistical-auditor`, `statistical-expert` | Same | `chapter4_writer.py` |
| `citation-network-visualizer` | `literature-expert`, `research-agent` | Same | `citation_visualizer.py` |
| `data-audit` | *None* (Unbound in FM) | `data-agent`, `data-curator` | `run_data_audit.py` |
| `data-cleaning` | *None* (Unbound in FM) | `data-agent`, `data-curator` | `clean_dataset.py` |
| `descriptive-statistics` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `compute_descriptives.py` |
| `digital-twin-academic-consultant` | `academic-orchestrator`, `digital-saber` | Same | `proposal_price_estimator.py` |
| `gpower-sample-size-calculator` | `methodology-expert`, `research-agent` | Same | `gpower_engine.py` |
| `irandoc-plagiarism-reducer` | `evidence-auditor`, `validation-agent` | Same | `plagiarism_reducer.py` |
| `journal-submission-assistant` | `journal-strategist`, `writing-agent` | Same | `submission_assistant.py` |
| `literature-harvester` | `literature-expert`, `research-agent` | Same | `harvester.py` |
| `literature-review` | *None* (Unbound in FM) | `research-agent` | `literature_review.py` |
| `longitudinal-moderated-mediation` | `longitudinal-modmed-expert` | Same | `run_longitudinal_modmed.py` |
| `mediation` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `run_mediation.py` |
| `methodology-review` | `methodology-expert` | `research-agent` | `methodology_review.py` |
| `moderation` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `run_moderation.py` |
| `network-analysis` | *None* (Unbound in FM) | `statistics-agent` | `network_analysis.py` |
| `persian-academic-translation` | `journal-strategist` | Same | `translate_academic.py` |
| `persian-defense-presentation-builder` | `final-judge`, `writing-agent` | Same | `generate_defense_deck.py` |
| `persian-discussion-builder` | `academic-writer`, `digital-saber`, `writing-agent` | Same | `generate_chapter5_docx.py` |
| `persian-literature-review-builder`| `literature-expert`, `research-agent` | Same | `literature_review_engine.py` |
| `persian-proposal-builder` | `methodology-expert`, `research-agent` | Same | `generate_proposal_docx.py` |
| `persian-thesis-builder` | `academic-writer`, `writing-agent` | Same | `compile_full_thesis.py` |
| `persian-thesis-revision-assistant`| `digital-saber`, `final-judge`, `validation-agent` | Same | `revision_triage_engine.py` |
| `psychological-intervention-protocol-builder` | `intervention-designer`, `writing-agent` | Same | `protocol_builder.py` |
| `psychometric-data-simulator` | `data-agent`, `methodology-expert`, `statistics-agent` | Same | `simdat_engine.py` |
| `psychometric-scale-resolver` | `data-agent`, `data-curator`, `psychometric-expert`, `statistical-expert` | Same | `questionnaire_resolver.py` |
| `psychometric-scale-validator` | `data-agent`, `psychometric-expert`, `statistical-expert`, `statistics-agent` | Same | `psychometric_validator_engine.py` |
| `qualitative-data-analyst` | `qualitative-analyst`, `research-agent` | Same | `qualitative_engine.py` |
| `regression` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `run_regression.py` |
| `reliability-analysis` | `psychometric-expert` | `statistical-expert`, `statistics-agent` | `cronbach_alpha.py` |
| `sem` | *None* (Unbound in FM) | `statistical-expert`, `statistics-agent` | `run_sem.py`, `run_sem.R` |
| `statistical-data-analyst` | `data-agent`, `data-curator`, `longitudinal-modmed-expert`, `results-auditor`, `statistical-auditor`, `statistical-expert`, `statistics-agent` | Same | `psychology_stats.py`, `generate_apa_docx.py` |
| `systematic-review-meta-analyst` | `meta-analyst`, `research-agent`, `statistics-agent` | Same | `meta_engine.py` |
| `thesis-integrity-auditor` | `academic-orchestrator`, `digital-saber`, `final-judge`, `results-auditor`, `statistical-auditor`, `validation-agent` | Same | `audit_thesis_integrity.py` |

> [!WARNING]
> **Orphaned / Unbound Skills**: 10 skills (`academic-drive-project-organizer`, `apa-reporting`, `assumption-testing`, `data-audit`, `data-cleaning`, `descriptive-statistics`, `literature-review`, `mediation`, `moderation`, `network-analysis`, `regression`, `sem`) are NOT declared in ANY agent's frontmatter YAML `skills: [...]` block! They are invoked purely via shell scripts or CLI calls.

---

## 6. Data & State Management Topology (`academic-state/`)

Every empirical project in `projects/*/` maintains a standardized state directory (`academic-state/`) conforming to strict JSON schemas:

```
academic-state/
├── project.json                      # Project ID, methodology type, current stage, orchestrator status
├── requirements.json                 # Research questions, hypotheses, institutional guidelines
├── analysis_plan.json                # Significance alpha, statistical sequence, variable mappings
├── decisions.json                    # Auditable Decision Journal (DEC-001, rationale, agent, approval)
├── data/
│   ├── data_dictionary.json          # Item names, scale IDs, reverse coding keys, score ranges
│   └── data_quality.json             # Sample N, missing rate, Little's MCAR chi2/df/p, outliers
├── analysis/
│   ├── descriptive.json              # Mean, SD, Skewness, Kurtosis, SE for all study variables
│   ├── reliability.json              # Cronbach's alpha, McDonald's omega, item-total correlations
│   ├── cfa.json                      # Factor loadings, construct reliability, AVE, fit indices
│   └── sem.json                      # Direct paths, indirect mediation BCa bootstrap CI, macro fit
├── validation/
│   ├── data_validation.json          # Data integrity validator report
│   ├── statistical_validation.json   # Numerical & assumption validator report
│   └── writing_validation.json       # APA 7 & typography validator report
└── outputs/                          # Assembled DOCX and MD deliverables
```

### State Transition Protocol:
- Managed deterministically via `scripts/academic_state_manager.py`.
- **Flaw Detected**: `set_stage(project_path, stage)` updates `current_stage` in `project.json` without validating that prerequisite files exist on disk or that previous stage validation passed.
