# AcademicSuite — Agent Taxonomy & Capability Rationalization

**Document Version:** 1.0.0 (Phase 2 Architectural Clean-up)  
**Operative Date:** September 2026 (1405 SH)  
**Governance:** Constitutional Directive 19 — The Six-Part Functional Separation Invariant  

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
> - **State machine → authorizes transition** (milestone progression, event recording, high-water mark validation)  
> - **Artifact manifest → defines completion** (schema contract conformance, required files, affirmative evidence)  

---

## 1. Complete Classification of All Existing Agents (12 Taxonomies)

Every agent in `.agents/agents/` and historical registry has been classified into exactly one authoritative category:

| Taxonomy Category | Agent Name | Tier / Role | Core Reasoning Responsibility |
|---|---|---|---|
| **ORCHESTRATOR** | `digital-saber` | Tier 1 Lead | Digital Twin of Saber Ghaderi; client consultancy, high-level research strategy, pricing, approval gates. |
| **ORCHESTRATOR** | `academic-orchestrator`| Tier 1 Lead | Master Conductor; multi-chapter thesis pipeline decomposition, micro-stage sequencing, subagent delegation. |
| **RESEARCHER** | `research-agent` | Tier 3 Worker | Literature harvesting, empirical parameter extraction, research question formulation, preliminary scoping. |
| **RESEARCHER** | `literature-expert` | Tier 3 Worker | Deep theoretical mechanism synthesis, inverted-triangle literature review, empirical background matrix. |
| **RESEARCHER** | `meta-analyst` | Tier 4 Critic | PRISMA 2020 systematic reviews, Cochrane RoB 2 risk of bias, quantitative meta-analysis & pooling. |
| **METHODOLOGIST** | `methodology-expert` | Tier 2 Authority | Research design validity, experimental & quasi-experimental controls, G*Power sampling determination. |
| **METHODOLOGIST** | `intervention-designer`| Tier 3 Worker | Psychological intervention protocol manuals (ACT, CBT, Schema, CFT, MBSR), clinical session tables. |
| **METHODOLOGIST** | `qualitative-analyst` | Tier 3 Worker | Reflexive Thematic Analysis (Braun & Clarke), Grounded Theory (Strauss & Corbin), theme hierarchies. |
| **DATA_SPECIALIST**| `data-curator` | Tier 3 Worker | Raw dataset ingestion, missing data diagnosis (MCAR/MAR/MNAR), unengaged responses, multivariate outliers. |
| **DATA_SPECIALIST**| `data-agent` | Tier 3 Worker | Reverse-coding 4,880 validated questionnaires, composite scoring, schema mapping, psychometric simulation. |
| **STATISTICIAN** | `statistical-expert` | Tier 2 Authority | Advanced quantitative modeling authority: SEM, CFA, bootstrap mediation, moderation, RM-ANOVA. |
| **STATISTICIAN** | `statistics-agent` | Tier 3 Worker | Deterministic execution of approved statistical plans, hypothesis test runners, APA 7 table compilation. |
| **STATISTICIAN** | `longitudinal-modmed-expert`| Tier 4 Specialist | 3-wave longitudinal moderated mediation modeling, autoregressive cross-lagged controls. |
| **PSYCHOMETRICIAN**| `psychometric-expert` | Tier 3 Worker | Scale construct validation (CTT, Item Response Theory GRM, CFA, convergent/discriminant validity, Omega). |
| **WRITER** | `academic-writer` | Tier 2 Authority | Scholarly thesis chapter drafting (Ch 1–5), Persian academic register, OpenXML OMML math preservation. |
| **WRITER** | `journal-strategist` | Tier 4 Specialist | Target journal matching (WoS/Scopus/ISC), author guidelines, cover letters, peer-review rebuttal tables. |
| **AUDITOR** | `validation-agent` | Tier 4 Critic | Independent fail-closed validator, cross-chapter consistency, artifact completeness, viva voce defense simulator. |
| **AUDITOR** | `statistical-auditor`| Tier 4 Critic | Adversarial auditor for statistical assumptions, degrees of freedom concordance, MSAI scoring. |
| **AUDITOR** | `results-auditor` | Tier 4 Critic | APA 7th Edition numerical precision, Persian leading zero standard (۰.۰۰۱), 3-line table borders. |
| **AUDITOR** | `evidence-auditor` | Tier 2 Authority | Epistemic integrity, bibliographic reconciliation, citation-reference alignment, Irandoc plagiarism audit. |
| **AUDITOR** | `academic-challenger`| Tier 4 Critic | Adversarial falsifier, p-hacking red-teaming, unmeasured confounding probes, 10 viva voce questions. |
| **AUDITOR** | `final-judge` | Tier 2 Authority | Final dissertation defense committee simulator, viva voce cross-examiner, administrative release gatekeeper. |
| **LEARNING** | `behavior-analyst` | Tier 5 Learning | Causal root-cause analysis of agent execution trajectories; explains behavioral successes and defects. |
| **LEARNING** | `curriculum-builder` | Tier 5 Learning | Graduated complexity training scenarios and challenge benchmark datasets targeting agent weaknesses. |
| **LEARNING** | `evaluation-agent` | Tier 5 Learning | Independently tests and benchmarks improvement candidates with zero regressions. |
| **LEARNING** | `knowledge-curator` | Tier 5 Learning | Synthesizes episodic experiences and causal diagnoses into structured knowledge items and anti-patterns. |
| **LEARNING** | `skill-evolver` | Tier 5 Learning | Formulates candidate mutations to Skills and behavioral instructions; documents projected diffs. |
| **LEARNING** | `trajectory-analyzer` | Tier 5 Learning | Reconstructs observable tool call trajectories from logs and script exits without hallucination. |
| **LEGACY** | `writing-agent` | Retired | Superseded by `academic-writer`. Archived in `legacy/`. |
| **LEGACY** | `legacy-orchestrator`| Retired | Standalone Python agent runner deprecated under Directive 12.1. Archived in `legacy/`. |
| **LEGACY** | `orchestrator-agent`| Retired | Historical orchestrator variant. Archived in `legacy/`. |
| **DUPLICATE** | Symlink mirrors | Backward Compat | 28 discovery symlinks (`.agents/agents/<name>.md` $\rightarrow$ `<name>/agent.md`) for legacy tooling compatibility. |

---

## 2. Per-Agent Capability Audit: "What Capability Exists Here That Cannot Be Expressed More Cleanly as a Skill?"

The foundational design question is asked of all 28 agents. This section demarcates genuine Agent cognitive ownership from Skill procedural knowledge.

---

### 2.1 Orchestrator Agents

#### 1. `digital-saber`
- **Agent Ownership (Cannot be a Skill)**:
  - Holds the conversational context of the entire research client engagement.
  - Possesses Saber Ghaderi's executive judgment, deciding on pricing quotes, accepting/rejecting dissertation topics, approving method deviations, and enforcing ethical boundaries.
  - Directly interacts with the human researcher and the Telegram Admin Desk.
- **Skill Ownership (Offloaded)**:
  - Pricing calculation formulas $\rightarrow$ `digital-twin-academic-consultant` skill + `proposal_price_estimator.py`.
  - Directory setup $\rightarrow$ `academic-drive-project-organizer`.

#### 2. `academic-orchestrator`
- **Agent Ownership (Cannot be a Skill)**:
  - Decomposes holistic thesis requirements into bounded micro-stages (Stages 4.0 through 4.12, 5.1 through 5.7, etc.).
  - Coordinates multi-agent workflows by delegating to specialist subagents via Antigravity's `invoke_subagent`.
  - Manages retry loops and adjudicates between conflicting specialist findings (e.g., when `academic-challenger` flags a defect that `statistics-agent` produced).
- **Skill Ownership (Offloaded)**:
  - Execution commands, pipeline stage tables, and CLI flags $\rightarrow$ `academic-suite-orchestrator` skill.

---

### 2.2 Researcher Agents

#### 3. `research-agent`
- **Agent Ownership (Cannot be a Skill)**:
  - Contextual boundary: Operates with an isolated context window for exploratory literature discovery so hundreds of paper titles do not pollute the primary orchestrator session.
  - Epistemic decision-making: Evaluates whether retrieved studies directly answer the researcher's specific research questions.
- **Skill Ownership (Offloaded)**:
  - Search query formulation and API fetching $\rightarrow$ `literature-harvester` skill.
  - Inverted-triangle structuring rules $\rightarrow$ `literature-review` skill.

#### 4. `literature-expert`
- **Agent Ownership (Cannot be a Skill)**:
  - Theoretical mechanism synthesis: Reasons about psychological mechanisms connecting independent and dependent variables.
  - Evaluates theoretical concordance/discordance across competing literature camps.
- **Skill Ownership (Offloaded)**:
  - Bibliometric mapping, VOSviewer formatting, Callon density calculations $\rightarrow$ `bibliometric-network-analyst` skill.
  - Empirical background table generation $\rightarrow$ `persian-literature-review-builder` skill.

#### 5. `meta-analyst`
- **Agent Ownership (Cannot be a Skill)**:
  - Evaluates risk of bias (RoB 2) requiring critical domain judgment of blinding, allocation concealment, and attrition.
  - Adjudicates between fixed-effect vs. random-effects model based on substantive clinical heterogeneity.
- **Skill Ownership (Offloaded)**:
  - PRISMA 2020 checklist, Hedges' $g$ calculation, heterogeneity statistics ($I^2, Q$), Forest/Funnel plots $\rightarrow$ `systematic-review-meta-analyst` skill.

---

### 2.3 Methodologist Agents

#### 6. `methodology-expert`
- **Agent Ownership (Cannot be a Skill)**:
  - Epistemic authority over research validity: Diagnoses threats to internal validity (history, maturation, testing effects) and external validity.
  - Justifies sample size trade-offs when target power ($1-\beta = 0.80$) cannot be met due to rare clinical populations.
- **Skill Ownership (Offloaded)**:
  - G*Power 3.1 statistical algorithms, non-centrality parameters $\rightarrow$ `gpower-sample-size-calculator` skill + `gpower_engine.py`.
  - Methodological checklists $\rightarrow$ `methodology-review` skill.

#### 7. `intervention-designer`
- **Agent Ownership (Cannot be a Skill)**:
  - Clinical reasoning: Adapts standardized psychotherapy protocols (e.g., ACT for chronic illness vs. ACT for generalized anxiety) to specific clinical samples.
  - Adjudicates ethical safeguards, distress protocols, and therapist competency requirements.
- **Skill Ownership (Offloaded)**:
  - Session structure templates, fidelity checklists, homework worksheet formats $\rightarrow$ `psychological-intervention-protocol-builder` skill.

#### 8. `qualitative-analyst`
- **Agent Ownership (Cannot be a Skill)**:
  - Hermeneutic and interpretive reasoning: Reflexive engagement with participant interview transcripts; decides inductive vs. deductive coding strategies.
  - Epistemic reflexivity: Documents researcher positionality and subjective influence.
- **Skill Ownership (Offloaded)**:
  - 6-phase Braun & Clarke procedure, Cohen's kappa inter-coder reliability formulas, thematic tree schemas $\rightarrow$ `qualitative-data-analyst` skill.

---

### 2.4 Data Specialists

#### 9. `data-curator`
- **Agent Ownership (Cannot be a Skill)**:
  - Decides whether missing data mechanism is MCAR, MAR, or MNAR based on substantive pattern examination.
  - Evaluates whether multivariate outliers ($D^2, p < .001$) represent invalid data entry or genuine extreme cases that must be retained for external validity.
- **Skill Ownership (Offloaded)**:
  - Straight-lining screening scripts, Mahalanobis distance computation, Little's MCAR test $\rightarrow$ `data-audit` skill.
  - Demographic distribution tabulations $\rightarrow$ `descriptive-statistics` skill.

#### 10. `data-agent`
- **Agent Ownership (Cannot be a Skill)**:
  - Decides variable categorization, subscale aggregation rules, and recoding strategies based on psychometric manuals.
  - Governs dataset provenance and certifies readiness for statistical analysis.
- **Skill Ownership (Offloaded)**:
  - Reverse-coding formulas and 4,880 instrument scoring algorithms $\rightarrow$ `data-cleaning` and `psychometric-scale-resolver` skills.
  - Monte Carlo noise simulation $\rightarrow$ `psychometric-data-simulator` skill.

---

### 2.5 Statisticians

#### 11. `statistical-expert`
- **Agent Ownership (Cannot be a Skill)**:
  - Primary statistical authority: Analyzes variable topology and formulates the formal Statistical Analysis Plan (SAP).
  - Evaluates model modification indices, deciding whether freeing an error covariance is substantively justified or opportunistic capitalization on chance.
- **Skill Ownership (Offloaded)**:
  - Parametric decision tree, test formulas, cutoffs (Hu & Bentler, Kline) $\rightarrow$ `sem`, `cfa`, `regression`, `mediation`, `moderation` skills.

#### 12. `statistics-agent`
- **Agent Ownership (Cannot be a Skill)**:
  - Context isolation: Executes terminal scripts, monitors process outputs, extracts exact values, and structures raw statistical outputs without cluttering the orchestrator's context.
  - Reports raw execution anomalies, non-convergence flags, and runtime errors to `statistical-expert`.
- **Skill Ownership (Offloaded)**:
  - Python scripts (`run_regression.py`, `run_sem.py`, `run_mediation.py`) $\rightarrow$ skills' `scripts/` directories.
  - APA 7 table formatting rules $\rightarrow$ `apa-reporting` skill.

#### 13. `longitudinal-modmed-expert`
- **Agent Ownership (Cannot be a Skill)**:
  - Specialized reasoning over temporal precedence, autoregressive stability, and stationarity assumptions in longitudinal data.
- **Skill Ownership (Offloaded)**:
  - 3-wave longitudinal bootstrap calculation script $\rightarrow$ `longitudinal-moderated-mediation` skill.

---

### 2.6 Psychometrician

#### 14. `psychometric-expert`
- **Agent Ownership (Cannot be a Skill)**:
  - Psychometric reasoning: Interprets factor indeterminacy, cross-loadings, and decides whether an item should be purged or revised.
  - Evaluates measurement invariance (configural, metric, scalar) across groups.
- **Skill Ownership (Offloaded)**:
  - EFA/CFA calculation engines, McDonald's omega, AVE, CVR/CVI formulas, IRT Graded Response Model $\rightarrow$ `psychometric-scale-validator` skill.

---

### 2.7 Writers

#### 15. `academic-writer`
- **Agent Ownership (Cannot be a Skill)**:
  - Master academic Persian rhetorical voice: Formulates authentic scholarly paragraphs using Saber's 5-part epistemic paragraph structure with variable cadence ($CV \ge 0.50$).
  - Synthesizes findings across multiple statistical tables into a cohesive theoretical narrative without robotic AI clichés.
- **Skill Ownership (Offloaded)**:
  - OpenXML BiDi formatting, RTL paragraph properties, Persian font bindings (`B Nazanin` / `B Titr`), 3-line borders $\rightarrow$ `chapter-4-writing`, `apa-reporting`, `persian-thesis-builder` skills.

#### 16. `journal-strategist`
- **Agent Ownership (Cannot be a Skill)**:
  - Editorial strategy: Formulates strategic responses to hostile reviewers and analyzes journal aim & scope fit.
- **Skill Ownership (Offloaded)**:
  - Point-by-point response table templates, cover letter OpenXML generators $\rightarrow$ `journal-submission-assistant` skill.

---

### 2.8 Auditors & Critics

#### 17. `validation-agent`
- **Agent Ownership (Cannot be a Skill)**:
  - Independent critic perspective: Uncompromised by generation bias; evaluates completed artifacts with zero sycophancy.
  - Cross-chapter reconciliation: Compares degrees of freedom and sample sizes across Chapter 1, 3, 4, and 5.
- **Skill Ownership (Offloaded)**:
  - Deterministic consistency checks and schema validation $\rightarrow$ `thesis-integrity-auditor` skill + `validators/run_all_validators.py`.

#### 18. `statistical-auditor`
- **Agent Ownership (Cannot be a Skill)**:
  - Adversarial scrutiny of statistical findings; probes for degrees of freedom mismatches and variance deflation.
- **Skill Ownership (Offloaded)**:
  - Multi-Signal Anomaly Index (MSAI) computation and outlier formulas $\rightarrow$ `data-audit` skill + `scripts/candidate_falsifier_engine.py`.

#### 19. `results-auditor`
- **Agent Ownership (Cannot be a Skill)**:
  - Epistemic verification that reported statistical text strictly reflects the numbers in the underlying JSON checkpoints.
- **Skill Ownership (Offloaded)**:
  - Decimal precision regex, Persian leading zero formatting (۰.۰۰۱), p-value inequality rules $\rightarrow$ `apa-reporting` skill.

#### 20. `evidence-auditor`
- **Agent Ownership (Cannot be a Skill)**:
  - Citation integrity judgment: Resolves ambiguous references and verifies evidence provenance against authentic literature databases.
- **Skill Ownership (Offloaded)**:
  - In-text citation regex extraction, EndNote/RIS formatting, Irandoc structural paraphrasing rules $\rightarrow$ `academic-reference-extractor` and `irandoc-plagiarism-reducer` skills.

#### 21. `academic-challenger`
- **Agent Ownership (Cannot be a Skill)**:
  - Adversarial red-teaming: Formulates aggressive viva voce defense cross-examinations simulating hostile examiners.
  - Stress-tests marginal significance clusters ($p = .041 - .049$) against competing theoretical explanations.
- **Skill Ownership (Offloaded)**:
  - Pitfall reporting schema $\rightarrow$ `contracts/pitfall.schema.json` and `methodology-review` skill.

#### 22. `final-judge`
- **Agent Ownership (Cannot be a Skill)**:
  - Final institutional gatekeeping: Weighs findings from all auditors (`statistical-auditor`, `results-auditor`, `academic-challenger`) and issues an irrevocable release decision (ACCEPT, REVISE, REJECT).
- **Skill Ownership (Offloaded)**:
  - Viva voce evaluation rubric and defense brief triad format $\rightarrow$ `persian-defense-presentation-builder` skill.

---

### 2.9 Learning Subagents

#### 23. `behavior-analyst`
- **Agent Ownership**: Conducts causal root-cause analysis on execution transcripts to explain behavioral drift or defects.
- **Skill Ownership**: Analytical heuristics $\rightarrow$ `academic-adaptive-context`.

#### 24. `curriculum-builder`
- **Agent Ownership**: Designs targeted challenge scenarios to stress-test diagnosed weaknesses.
- **Skill Ownership**: Benchmark generation schemas $\rightarrow$ `psychometric-data-simulator`.

#### 25. `evaluation-agent`
- **Agent Ownership**: Acts as an impartial benchmark judge verifying candidate mutations with zero regressions.
- **Skill Ownership**: Evaluation harness $\rightarrow$ `contracts/evolution/evaluation_case.schema.json`.

#### 26. `knowledge-curator`
- **Agent Ownership**: Synthesizes verified lessons into versioned knowledge items, resolving semantic contradictions.
- **Skill Ownership**: Knowledge schemas $\rightarrow$ `contracts/evolution/knowledge_item.schema.json`.

#### 27. `skill-evolver`
- **Agent Ownership**: Synthesizes surgical instruction mutations for skills based on curated knowledge.
- **Skill Ownership**: Diff generation format $\rightarrow$ `contracts/evolution/improvement_candidate.schema.json`.

#### 28. `trajectory-analyzer`
- **Agent Ownership**: Reconstructs observable tool call trajectories without confabulation.
- **Skill Ownership**: Trace parsing rules $\rightarrow$ `contracts/evolution/trajectory.schema.json`.

---

## 3. Potential Horizontal Consolidations (Roadmap for Phase 3/4)

Our capability audit reveals that AcademicSuite can achieve identical or superior functionality with fewer agents by migrating procedural capabilities into skills:

1. **Longitudinal Modeling Consolidation**:
   - `longitudinal-modmed-expert` is an over-specialized agent. Its procedural expertise is already captured in the `longitudinal-moderated-mediation` skill. `statistical-expert` can own the reasoning, delegating to `statistics-agent`.
2. **Data Ingestion & Curation Consolidation**:
   - `data-agent` and `data-curator` share 80% of their operational scope. Consolidating into a single `data-curator` that utilizes `data-cleaning`, `data-audit`, and `psychometric-scale-resolver` skills will streamline data pipeline handoffs.
3. **Auditing Consolidation**:
   - `results-auditor` and `statistical-auditor` execute checks that are 90% deterministic calculations (MSAI, leading zero regex, df consistency). These can be fully automated in `validators/run_all_validators.py` and `thesis-integrity-auditor` skill, leaving `validation-agent` and `academic-challenger` as the cognitive audit authorities.
