# AcademicSuite — Current System Architecture Baseline

**Document Version:** 3.0.0 (Consolidated Production Baseline)  
**Operative Date:** September 2026 (1405 SH)  
**System Status:** **AUTHORITATIVE CURRENT ARCHITECTURE (GROUND TRUTH)**  
**Classification Guide:** See [docs/ARCHITECTURE_TAXONOMY_AND_TRUTH.md](../ARCHITECTURE_TAXONOMY_AND_TRUTH.md) for full temporal reconciliation (Current Ground Truth vs. Historical Phase Records vs. Target Roadmaps).

---

## 🏛️ Foundational Architectural Rules

### Rule 1: Freeze on Horizontal Growth
> **From this point forward: No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**  
> **This prevents AcademicSuite from continuing to grow horizontally.**

### Rule 2: The Six-Part Functional Separation Invariant
> - **Agent → decides** (reasoning role, delegation, decision-making, context, responsibility, communication)  
> - **Skill → instructs** (specialized procedure, domain knowledge, decision tree, execution instructions, reusable methodology, reporting format)  
> - **Script → computes** (deterministic computation, validation, transformation, file generation, hashing, state mutation)  
> - **Hook → enforces** (enforcement, interception, safety, automatic verification)  
> - **State machine → authorizes transition** (milestone progression, event recording, state gating)  
> - **Artifact manifest → defines completion** (schema contract conformance, required files, affirmative evidence)  

---

## 1. Executive Summary

The **AcademicSuite** (incorporating the **Digital Saber Professional AI Twin**) is a comprehensive research cognitive architecture and statistical consultancy framework engineered for graduate dissertations (M.A./M.Sc., Ph.D.) and academic journal publishing in psychology and the behavioral sciences.

The system is architected around a strict division between:
1. **The Brains & Critics**: 28 autonomous cognitive agents and subagents executing within the native Google Antigravity runtime.
2. **The Hands**: 44 specialized skills containing deterministic Python and R calculation scripts, psychometric simulators, and OpenXML Word/PPTX compilation engines.
3. **The Guardrails**: Lifecycle hooks (`.agents/hooks.json`), OS-level least-privilege file permissions, and fail-closed schema validators.

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
|   |                  Digital Saber / Lead Orchestrator                  |   |
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
|   |  - literature-expert              |   |  - academic-challenger      |   |
|   |  - data-agent / data-curator      |   |  - final-judge              |   |
|   |  - psychometric-expert            |   |  - validation-agent         |   |
|   +-----------------+-----------------+   +--------------+--------------+   |
|                     |                                    |                  |
+---------------------|------------------------------------|------------------+
                      | run_command (Terminal CLI)         |
                      v                                    v
+-----------------------------------------------------------------------------+
|                   DETERMINISTIC EXECUTION LAYER ("The Hands")               |
|                                                                             |
|   +------------------------------+     +--------------------------------+   |
|   |    Mathematical / Stats      |     |      OpenXML Document Engine   |   |
|   | - run_regression.py          |     | - build_scale_validation_docx  |   |
|   | - run_sem.py                 |     | - build_experimental_triad_docx|   |
|   | - run_mediation.py           |     | - build_hypothesis_triad_docx  |   |
|   | - gpower_engine.py           |     | - assemble_master_scale_docx   |   |
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

## 2. Current Agents & Subagents (28 Roles)

Agents are defined declaratively in `.agents/agents/<name>/agent.md` with companion contracts in `contract.md` and backward-compatible discovery symlinks at `.agents/agents/<name>.md`.

### 2.1 Tier 1: Primary Orchestrators & Digital Twin (2 Agents)
1. **`digital-saber`**: Master Research Project Lead, Cognitive Architect, and Digital Twin of Saber Ghaderi. High-level client engagement, methodology formulation, and thesis strategy.
2. **`academic-orchestrator`**: Master Conductor coordinating multi-chapter pipelines, decomposing research questions into micro-stages, mapping capabilities to skills, and assembling final deliverables.

### 2.2 Tier 2: Domain Authorities (5 Agents)
3. **`methodology-expert`**: Authority for research methodology, experimental and quasi-experimental design, sampling power determination (G*Power), and internal/external validity safeguards.
4. **`statistical-expert`**: Advanced quantitative modeling authority for SEM, CFA, Preacher & Hayes bootstrap mediation, moderation interactions, and repeated measures.
5. **`academic-writer`**: Scholarly writing engine drafting Chapters 1–5, APA 7 narrative synthesis, Persian academic register, and OpenXML OMML math preservation.
6. **`evidence-auditor`**: Plagiarism detection (Irandoc/SamimNoor), reference accuracy, DOI resolution, and bibliographic library management (.enw/.ris).
7. **`final-judge`**: Impartial quality release gatekeeper certifying milestone compliance, multi-signal integrity, and defense readiness.

### 2.3 Tier 3: Bounded Specialist Execution Subagents (8 Agents)
8. **`data-agent`**: Data discovery, schema mapping, reverse-coding from 4,880 validated instruments, variable transformations, and psychometric simulation.
9. **`data-curator`**: Raw dataset ingestion, missing data pattern diagnosis (MCAR/MAR/MNAR), unengaged response filtering, and multivariate outlier screening (Mahalanobis $D^2$).
10. **`statistics-agent`**: Executes approved statistical plans on verified data, parametric assumption tests, and APA 7 table generation.
11. **`psychometric-expert`**: Classical Test Theory (CTT), Item Response Theory (IRT), Confirmatory Factor Analysis (CFA), and construct validation.
12. **`research-agent`**: Literature harvesting, research question formulation, and epistemic evidence synthesis.
13. **`literature-expert`**: Multi-database literature harvesting, empirical parameter extraction (N, design, scales), and theoretical mechanism synthesis.
14. **`intervention-designer`**: Standardized psychological intervention protocols (ACT, CBT, Schema, CFT, MBSR) and clinical session tables.
15. **`qualitative-analyst`**: Reflexive Thematic Analysis (Braun & Clarke) and Grounded Theory (Strauss & Corbin).

### 2.4 Tier 4: Specialist Reviewers & Adversarial Critics (7 Agents)
16. **`validation-agent`**: Independent adversarial quality auditor, Viva Voce defense simulator, and institutional release gatekeeper.
17. **`statistical-auditor`**: Adversarial auditor for statistical assumptions, degrees of freedom concordance, and Multi-Signal Anomaly Index (MSAI) scoring.
18. **`results-auditor`**: Enforces APA 7th Edition numerical precision, Persian leading zero standard (۰.۰۰۱), and OpenXML 3-line table borders.
19. **`academic-challenger`**: Adversarial examiner identifying p-hacking, unmeasured confounding, sample selection bias, and statistical fragility.
20. **`journal-strategist`**: Target journal matching (WoS/Scopus/ISC), formatting guidelines, and peer-review rebuttal management.
21. **`meta-analyst`**: PRISMA 2020 systematic literature reviews, Cochrane RoB 2 risk of bias evaluations, and quantitative meta-analysis.
22. **`longitudinal-modmed-expert`**: 3-wave longitudinal moderated mediation modeling and autoregressive cross-lagged controls.

### 2.5 Tier 5: Autonomous Learning & Evolution Subagents (6 Subagents)
23. **`behavior-analyst`**: Diagnoses why agent behavior succeeded or failed via causal root-cause analysis.
24. **`curriculum-builder`**: Architects graduated training scenarios and challenge benchmark datasets.
25. **`evaluation-agent`**: Independently benchmarks improvement candidates with zero regressions.
26. **`knowledge-curator`**: Synthesizes episodic experiences and causal diagnoses into structured knowledge items and anti-patterns.
27. **`skill-evolver`**: Formulates candidate mutations to Skills and behavioral instructions.
28. **`trajectory-analyzer`**: Reconstructs observable execution trajectories from raw tool calls and script exits.

---

## 3. Current Skills (44 Skills)

Skills reside in `.agents/skills/<skill-name>/SKILL.md` and are loaded on-demand via Antigravity's progressive disclosure mechanism:

| # | Skill Name | Domain / Purpose | Deterministic Scripts Bundled |
|---|---|---|---|
| 1 | `academic-adaptive-context` | Dynamic context retrieval | Context search & calibration |
| 2 | `academic-article-writer` | Empirical journal manuscripts | Manuscript section compilers |
| 3 | `academic-drive-project-organizer`| Project filesystem hierarchy | Standard directory scaffolding |
| 4 | `academic-reference-extractor` | Citation extraction & DOI lookup | Ref extractor & CWYW builder |
| 5 | `academic-suite-orchestrator` | CLI batch runner for pipelines | Pipeline orchestration scripts |
| 6 | `ai-academic-tone-polisher` | Persian academic style & half-spaces | Typography polishers |
| 7 | `apa-reporting` | APA 7 tables, leading zero standard | OpenXML 3-line table generator |
| 8 | `assumption-testing` | Parametric assumption verification | Shapiro-Wilk, Levene, VIF |
| 9 | `bibliometric-network-analyst` | Bibliometric mapping, VOSviewer | Bradford/Lotka, Callon density |
| 10 | `cfa` | Confirmatory Factor Analysis | Factor loading & AVE/CR script |
| 11 | `chapter-4-writing` | Chapter 4 micro-stage drafting | Stage-gate builders & tables |
| 12 | `citation-network-visualizer` | 300-DPI citation graphs | Citation network graphers |
| 13 | `data-audit` | Screening straight-lining, MCAR | Little's MCAR & Mahalanobis |
| 14 | `data-cleaning` | Reverse-coding 4,880 questionnaires| Instrument scoring engines |
| 15 | `descriptive-statistics` | Descriptive parameters (M, SD, Skew)| Univariate descriptives calculator |
| 16 | `digital-twin-academic-consultant`| Proposal pricing & consulting | `proposal_price_estimator.py` |
| 17 | `gpower-sample-size-calculator` | Statistical power & sample sizing | G*Power 3.1 calculation engine |
| 18 | `irandoc-plagiarism-reducer` | SamimNoor/Irandoc similarity repair | Structural paraphrasing engine |
| 19 | `journal-submission-assistant` | Journal matching & author guidelines| Submission packaging scripts |
| 20 | `literature-harvester` | CrossRef, PubMed, SID harvester | Harvester CLI runners |
| 21 | `literature-review` | Inverted-triangle literature review | Literature synthesizer |
| 22 | `longitudinal-moderated-mediation`| 3-wave longitudinal modmed | Longitudinal bootstrap engine |
| 23 | `mediation` | PROCESS Model 4 bootstrap mediation | Preacher & Hayes 5,000 bootstrap |
| 24 | `methodology-review` | Methodology validity audit | Design audit checklists |
| 25 | `moderation` | PROCESS Model 1 moderation | Simple slopes & Johnson-Neyman |
| 26 | `network-analysis` | Bibliometric & citation networks | Co-occurrence network scripts |
| 27 | `persian-academic-translation` | Academic translation with APA rules | Translation terminology mapper |
| 28 | `persian-defense-presentation-builder`| 16:9 defense slides (PPTX + HTML) | DrawingML SmartArt generator |
| 29 | `persian-discussion-builder` | Chapter 5 Discussion & Mechanisms | Mechanism & concordance builder |
| 30 | `persian-literature-review-builder`| Chapter 2 Review & Background table| Background empirical matrix |
| 31 | `persian-proposal-builder` | Graduate research proposals | Proposal OpenXML generator |
| 32 | `persian-thesis-builder` | 5-chapter thesis compilation | Master Word compiler |
| 33 | `persian-thesis-revision-assistant`| Examiner response tables & diffs | Track changes & response table |
| 34 | `psychological-intervention-protocol-builder`| Intervention manuals (ACT, CBT) | Session table OpenXML compiler |
| 35 | `psychometric-data-simulator` | Monte Carlo realistic data simulation| Realistic decimal noise engine |
| 36 | `psychometric-scale-resolver` | 4,880 questionnaires resolver | Questionnaire database query |
| 37 | `psychometric-scale-validator` | CVR/CVI, EFA, CFA, Omega, IRT | Psychometric validation pipeline |
| 38 | `qualitative-data-analyst` | Thematic analysis & Grounded Theory | Inter-coder reliability calculator |
| 39 | `regression` | Hierarchical & stepwise regression | Multiple regression engine |
| 40 | `reliability-analysis` | Cronbach's alpha & McDonald's omega | Reliability calculation engine |
| 41 | `sem` | Structural Equation Modeling | Latent SEM & Hu & Bentler fit |
| 42 | `statistical-data-analyst` | Hypothesis testing & APA 4 report | Hypothesis test runners |
| 43 | `systematic-review-meta-analyst` | PRISMA 2020 & Hedges' g pooling | Forest/Funnel plot generators |
| 44 | `thesis-integrity-auditor` | Forensic cross-chapter audit | df & citation reconciliation |

*(Built-in Antigravity skills mounted automatically: `agy-customizations`, `antigravity_guide`, `generative_ui`, `migrate-workflows`, `google-antigravity-sdk`).*

---

## 4. Current Orchestration Modules

AcademicSuite coordinates complex pipelines through deterministic orchestrator scripts:
1. **`scripts/suite_cli.py`**: Unified command-line interface for the Academic Suite.
2. **`scripts/academic_task_router.py` & `scripts/capability_resolver.py`**: Modern deterministic capability resolver and CLI engine deriving empirical research design parameters, capability requirements, and dynamically assembled minimal native Antigravity subagent teams with fail-closed gates.
3. **`scripts/teamwork_boundary_adapter.py`**: Enforces strict boundary conditions, context isolation, and clean handoffs between agents.
4. **`scripts/orchestrator_dependency_resolver.py`**: Resolves prerequisite dependencies, validating required prior stage outputs.
5. **`scripts/statistical_pipeline_engine.py`**: Batch statistical executor running parametric sequences.
6. **`scripts/academic_dual_loop_engine.py`**: Coordinates rapid execution loop with offline deliberative reflection.
7. **`digital_saber.py`**: Root entry point and interactive CLI facade for the digital twin persona.

---

## 5. Current Lifecycle Hooks (`.agents/hooks.json`)

Antigravity executes hooks synchronously around agent events to enforce system invariants mechanically:
- **`PreToolUse`**: Intercepts `run_command`, `write_to_file`, `replace_file_content`, `apply_diff`, `invoke_subagent`. Denies destructive shell commands (`rm -rf`, `chmod`), protects raw datasets from mutation, and enforces Directive 6 (English-only ASCII filenames).
- **`PostToolUse`**: Sanitizes arguments and writes structured audit logs to `state/audit_log.jsonl`.
- **`PreInvocation`**: Injects ephemeral constitutional reminders (Directive 0 Binary Honesty, Directive 3 Triad Artifacts, Directive 11 Stage-Gate Protocol).
- **`PostInvocation`**: Evaluates stage directory outputs against validation manifests.
- **`Stop`**: Forensic transcript analyzer (`transcript_and_rule_guard.py`) inspecting `transcript.jsonl`. Mechanically blocks turn completion (`"decision": "continue"`) if the agent failed the Binary Honesty Protocol or falsely claimed multi-agent execution without invoking subagents.

---

## 6. Current State Machine & Persistence

AcademicSuite tracks project progression via an append-only event-sourcing model:
- **`scripts/academic_state_manager.py`**: Central state engine managing milestones and stage transitions.
- **`scripts/academic_event_engine.py`**: Appends immutable state transition records.
- **`state/events.jsonl`**: Immutable timeline of all system events.
- **`state/milestones.jsonl`**: High-water mark state tracking completed micro-stages.
- **`state/audit_log.jsonl`**: Cryptographic audit trace of tool executions.

---

## 7. Current Artifact Contracts (30 Schemas)

All inter-stage communications and learning records are governed by strict JSON schemas in `contracts/`:

### 7.1 Core Pipeline Contracts (`contracts/` — 14 Schemas)
1. `analysis_candidate.schema.json`
2. `analysis_plan.schema.json`
3. `approval.schema.json`
4. `artifact_manifest.schema.json`
5. `event.schema.json`
6. `execution_manifest.schema.json`
7. `handoff.schema.json`
8. `methodology_decision_record.schema.json`
9. `milestone_state.schema.json`
10. `pitfall.schema.json`
11. `statistical_executor_contract.schema.json`
12. `statistical_execution_result.schema.json`
13. `teamwork_boundary.schema.json`
14. `validation_report.schema.json`
(Validated by `contract_validator.py`)

### 7.2 Self-Improvement & Evolution Contracts (`contracts/evolution/` — 17 Schemas)
13. `anti_pattern.schema.json`
14. `behavioral_profile.schema.json`
15. `capability_profile.schema.json`
16. `contradiction_record.schema.json`
17. `curriculum_task.schema.json`
18. `drift_report.schema.json`
19. `evaluation_case.schema.json`
20. `evaluation_result.schema.json`
21. `exemplar.schema.json`
22. `experience.schema.json`
23. `feedback.schema.json`
24. `improvement_candidate.schema.json`
25. `knowledge_item.schema.json`
26. `lesson.schema.json`
27. `promotion_decision.schema.json`
28. `skill_memory_record.schema.json`
29. `trajectory.schema.json`

---

## 8. Current Statistical Executors

Deterministic Python and R scripts located in `.agents/skills/*/scripts/` and `scripts/`:
- `run_regression.py`: Standard, hierarchical, stepwise regression with collinearity diagnostics.
- `run_sem.py`: Latent structural equations, CFA, and 11 fit indices.
- `run_mediation.py`: Preacher & Hayes bootstrap mediation (5,000 resamples).
- `run_experimental_analysis.py`: Repeated measures ANOVA, 2x2 mixed factorial, ANCOVA.
- `run_scale_validation_analysis.py`: EFA, CFA, McDonald's omega, average variance extracted (AVE).
- `data_curation_engine.py`: Reverse-coding and composite scoring.
- `gpower_engine.py`: Statistical power calculations for t-test, F-test, regression, SEM.

---

## 9. Current Methodology & Writing Modules

### 9.1 Methodology Modules
- `methodology-review`: Research design validity audits and sampling verification.
- `gpower-sample-size-calculator`: Exact a priori sample size determination.
- `persian-proposal-builder`: Comprehensive thesis proposal scaffolding.

### 9.2 Writing & Document Compilation Modules
- `chapter-4-writing`: One-Hypothesis-One-Stage narrative and APA 7 table generator.
- `persian-literature-review-builder`: Theoretical foundations and empirical synthesis matrix.
- `persian-discussion-builder`: Deep mechanisms, non-significant findings, and clinical implications.
- `persian-thesis-builder`: Master 5-chapter thesis document compiler.
- `build_hypothesis_1_triad_docx.py`, `build_mediation_triad_docx.py`, `build_moderation_triad_docx.py`, `build_scale_validation_triad_docx.py`, `build_sem_triad_docx.py`: Dedicated OpenXML document generators preserving RTL and OMML math.

---

## 10. Current Validation Subsystem

Validation operates on a **fail-closed** architecture where PASS requires explicit affirmative evidence:
- **`validators/run_all_validators.py`**: Master orchestrator executing validation across 6 domains:
  - `data_integrity`: Checks missing values, unengaged responses, and score ranges.
  - `statistical_assumptions`: Verifies normality, homoscedasticity, multicollinearity.
  - `numerical_consistency`: Audits cross-table numbers, sample sizes, and degrees of freedom.
  - `result_consistency`: Verifies that conclusions align with test statistics and p-values.
  - `reporting_consistency`: Enforces APA 7 format, 3-line tables, and Persian leading zeros.
  - `longitudinal_modmed`: Verifies time-lagged paths and autoregressive controls.
- **`validators/manifest_registry.py`**: Formal manifest of expected artifacts per stage.
- **`scripts/candidate_falsifier_engine.py`**: Adversarial falsification engine testing sensitivity to noise and edge cases.
- **`test_fail_closed_validation.py`**: Verifies that any missing artifact immediately triggers FAIL.

---

## 11. Current Learning Subsystem (14 Modules)

The self-improvement architecture records, analyzes, and learns from real interactions:
- `academic_experience_recorder.py`: Automatically logs conversation trajectory and tool calls.
- `academic_correction_detector.py`: Detects user corrections and dissatisfaction signals.
- `academic_lesson_distiller.py`: Distills causal lessons from execution failures.
- `academic_knowledge_manager.py`: Organizes versioned knowledge items and anti-patterns.
- `academic_candidate_generator.py`: Proposes targeted behavioral diffs.
- `academic_curriculum_builder.py`: Constructs progressive challenge benchmark scenarios.
- `academic_evaluation_lab.py`: Evaluates candidate mutations against frozen benchmarks.
- `academic_counterfactual_evaluator.py`: Tests counterfactual alternatives.
- `academic_regression_synthesizer.py`: Detects unintended performance degradation.
- `academic_promotion_engine.py`: Governs formal staging of improvements.
- `academic_behavior_drift_monitor.py`: Monitors runtime drift against constitutional baselines.
- `academic_behavior_consolidator.py`: Merges and indexes active knowledge.
- `academic_pitfall_registry.py`: Registry of known methodological pitfalls and traps.
- `academic_integrated_learning_hub.py`: Unified API coordinating the learning subsystem.

---

## 12. Current Automated Test Verification
The workspace includes **1,064+ automated tests** across `tests/`:
- **100% Passing Green Signal**: Zero failures, zero errors, zero warnings.
- **Pre-Flight AST & Compilation Integrity**: `compileall` and AST parser verify 100% of 440+ Python files across the repository (`test_repository_syntax_integrity.py`).
- **Privilege-Safe Least Privilege**: Root/unprivileged test runner helpers assert mode-bit and DAC constraints safely across Docker and bare-metal environments.
- **Self-Healing Fixtures**: On-the-fly dynamic fixture initialization for all 9 benchmark studies (`generate_test_fixtures.py`).

---

## 13. Legacy Components & Isolation
1. **`.agents/legacy/` Directory**: Historical workflow definitions and 10 legacy workflow-converted skill shells are safely isolated under `.agents/legacy/` (zero root-level legacy sprawl).
2. **Historical Migration Scripts**: `.agents/scripts/migrate_durable_agents.py` and `.agents/scripts/migrate_specialist_workers.py` are preserved for historical provenance and verified by dedicated regression tests.
3. **Sole Orchestrator Mandate (Directive 12.1)**: Antigravity is the sole agent conductor. Standalone Python agent emulators are permanently deprecated.
