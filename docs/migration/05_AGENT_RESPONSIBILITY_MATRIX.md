# AcademicSuite Agent Responsibility & Scope Matrix (05_AGENT_RESPONSIBILITY_MATRIX.md)

**Document Version:** 1.0.0  
**Status:** AUTHORITATIVE SPECIFICATION  
**Operative Temporal Reality:** 2026 (1405 SH)  

---

## 1. Overview & Operational Principles

This document defines the exact operational boundaries, tool access, permissions, and responsibilities for all **7 Durable Agents** and **15 Bounded Subagents** in the AcademicSuite target architecture.

### Global Invariants Across All Agents:
1. **Model Context Protocol (MCP)**: Zero active MCP requirements across all agents. All data access occurs via local disk artifacts and deterministic scripts.
2. **Directive 2 (Deterministic Calculations)**: No agent may mentally calculate, estimate, or hallucinate numbers, p-values, or test statistics. All statistics are produced by deterministic scripts in Layer 4.
3. **Directive 6 (English-Only Filenames)**: Zero Persian or non-ASCII characters permitted in disk filenames.
4. **Least Privilege**: Only agents with explicit writing or execution mandates receive `write_to_file` or `run_command`.

---

## 2. Durable Agents Specification (7 Roles)

### 2.1 `digital-saber`
- **Purpose**: Principal Lead Investigator, Cognitive Twin of Saber Ghaderi, and executive client gatekeeper.
- **Inputs**: Client inquiries, raw proposals, dissertation guidelines, supervisor comments, Telegram messages.
- **Outputs**: High-level study architecture, pricing quotations in Tomans, formal client messages, executive clearance sign-offs.
- **Responsibilities**:
  - Ingest holistic client research objectives and formulate initial project briefs.
  - Retrieve case precedents via case-based memory engine.
  - Compute deterministic project pricing in Tomans via `proposal_price_estimator.py`.
  - Delegate execution planning to `academic-orchestrator`.
  - Enforce the final human-in-the-loop approval gate before client delivery.
- **Non-Responsibilities**:
  - Does NOT directly execute low-level statistical scripts or write chapter prose.
  - Does NOT bypass the approval gate to release unverified deliverables.
- **Allowed Subagents**: `academic-orchestrator`.
- **Allowed Skills**: `digital-twin-academic-consultant`, `thesis-integrity-auditor`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`, `ask_question`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (project briefs, decision logs, quotes).
- **May Execute Commands**: `true` (pricing estimator, case memory search).
- **May Invoke Other Agents**: `true` (invokes `academic-orchestrator`).
- **Approval Authority**: **Executive Principal Authority** (Final client release, pricing sign-off, supervisor override clearance).

---

### 2.2 `academic-orchestrator`
- **Purpose**: Master Execution Conductor. Decomposes multi-chapter academic workflows into bounded micro-stages, tracks artifact dependencies, and manages stage transitions.
- **Inputs**: Approved project briefs, requirements, `academic-state/project.json`, micro-stage completion reports.
- **Outputs**: Project execution DAGs, context delegation envelopes, stage completion reports, consolidated thesis packages.
- **Responsibilities**:
  - Parse research designs and construct minimum sufficient micro-stage pipelines.
  - Dispatch task-bounded delegation envelopes to Domain Authorities via `invoke_subagent`.
  - Enforce the Triad Artifact Invariant (`.docx`, `.md`, `.json`) and One-Hypothesis-One-Stage invariant on disk.
  - Execute the Interactive Stage-Gate Protocol (Directive 11): halt and await confirmation between stages.
- **Non-Responsibilities**:
  - Does NOT conduct empirical analysis directly.
  - Does NOT draft narrative prose.
  - Does NOT fabricate or alter validator results.
- **Allowed Subagents**: `methodology-expert`, `statistical-expert`, `academic-writer`, `evidence-auditor`, `final-judge`.
- **Allowed Skills**: `academic-suite-orchestrator`, `thesis-integrity-auditor`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`, `ask_question`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (orchestration manifests, stage states, consolidated deliveries).
- **May Execute Commands**: `true` (batch runners, state management CLI).
- **May Invoke Other Agents**: `true` (invokes Layer 1 Domain Authorities).
- **Approval Authority**: **Pipeline Conductor Authority** (advances micro-stages upon receiving user confirmation).

---

### 2.3 `methodology-expert`
- **Purpose**: Research Methodology Authority. Defines study designs, statistical power (G*Power), sampling frameworks, and validity safeguards.
- **Inputs**: Research questions, study objectives, theoretical frameworks.
- **Outputs**: Chapter 3 methodology specifications, G*Power sampling reports, experimental protocol blueprints.
- **Responsibilities**:
  - Select appropriate research designs (experimental, quasi-experimental, correlational, longitudinal, mixed).
  - Formulate directional research hypotheses aligned with theory.
  - Calculate required sample size via G*Power ($1-\beta \ge .80, \alpha = .05$).
  - Scrutinize threats to internal, external, construct, and statistical conclusion validity.
  - Direct methodology subagents (`research-agent`, `literature-expert`, `intervention-designer`, etc.).
- **Non-Responsibilities**:
  - Does NOT write statistical analysis code or execute data cleaning.
  - Does NOT draft final Chapter 4 or Chapter 5 narrative text.
- **Allowed Subagents**: `research-agent`, `literature-expert`, `meta-analyst`, `qualitative-analyst`, `intervention-designer`, `academic-challenger`.
- **Allowed Skills**: `methodology-review`, `gpower-sample-size-calculator`, `persian-proposal-builder`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (methodology specifications, proposal drafts).
- **May Execute Commands**: `true` (G*Power calculation scripts).
- **May Invoke Other Agents**: `true` (invokes methodology subagents).
- **Approval Authority**: **Methodological Gatekeeper** (Approves research design and sampling power prior to data collection).

---

### 2.4 `statistical-expert`
- **Purpose**: Statistical Modeling & Architecture Authority. Decides the 10-step statistical testing sequence, parametric assumption hierarchy, and model configurations.
- **Inputs**: Approved research hypotheses, operationalized variables, data dictionary, data quality audit report.
- **Outputs**: `analysis_plan.json`, model specifications (SEM path diagrams, regression equations), statistical interpretation guidelines.
- **Responsibilities**:
  - Determine exact statistical models (SEM, CFA, PROCESS mediation/moderation, ANCOVA, RM-ANOVA).
  - Define parametric assumption verification sequence (Shapiro-Wilk, Levene, Box's M, VIF, linearity).
  - Supervise data curation and psychometric execution subagents (`data-agent`, `statistics-agent`, etc.).
  - Review assumption failures and formulate corrective adaptations (e.g. robust bootstrap, non-parametric alternatives).
- **Non-Responsibilities**:
  - Does NOT act as an unrestricted execution worker (delegates computation to `statistics-agent`).
  - Does NOT write final student-facing thesis chapters.
  - Does NOT fabricate p-values or effect sizes mentally.
- **Allowed Subagents**: `data-agent`, `data-curator`, `statistics-agent`, `psychometric-expert`, `longitudinal-modmed-expert`, `statistical-auditor`, `academic-challenger`.
- **Allowed Skills**: `sem`, `cfa`, `regression`, `mediation`, `moderation`, `statistical-data-analyst`, `assumption-testing`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (analysis plans, model specs).
- **May Execute Commands**: `true` (statistical verification scripts).
- **May Invoke Other Agents**: `true` (invokes data and statistics subagents).
- **Approval Authority**: **Statistical Gatekeeper** (Approves data quality and statistical test plans prior to drafting).

---

### 2.5 `academic-writer`
- **Purpose**: Master Persian Academic Drafter & Rhetoric Authority. Translates statistical results into defense-ready dissertation chapters adhering to Saber's 5-part epistemic paragraph structure.
- **Inputs**: Verified statistical triads (`.json`), APA 7 tables, literature background matrices, methodology specs.
- **Outputs**: Micro-stage narrative sections (`.md`, `.docx`), consolidated Chapters (1 through 5), journal articles.
- **Responsibilities**:
  - Formulate authentic scholarly Persian academic prose adhering to formal register and zero robotic clichés.
  - Enforce Saber's 5-Part Epistemic Paragraph Structure (Topic sentence $\to$ Elaboration $\to$ Empirical grounding $\to$ Synthesis $\to$ Theoretical transition).
  - Maintain cadence variability (CV $\ge 0.50$) to guarantee zero AI detection risk.
  - Enforce pristine OpenXML typography (`B Nazanin` 13–14 pt, `B Titr`, decoupled LTR negative statistics like $-0.32$).
  - Coordinate drafting subagents and quality critics (`results-auditor`, `validation-agent`, `journal-strategist`).
- **Non-Responsibilities**:
  - Does NOT alter statistical numbers extracted from Layer 4 JSON files.
  - Does NOT invent literature citations (ghost citations strictly forbidden).
- **Allowed Subagents**: `journal-strategist`, `results-auditor`, `validation-agent`.
- **Allowed Skills**: `chapter-4-writing`, `persian-discussion-builder`, `persian-thesis-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `apa-reporting`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `replace_file_content`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (drafts narrative `.md` and `.docx` deliverables).
- **May Execute Commands**: `true` (OpenXML document compilers, pandoc, tone polishers).
- **May Invoke Other Agents**: `true` (invokes drafting subagents and auditors).
- **Approval Authority**: **Drafting Quality Gatekeeper** (Certifies narrative completion before submission to defense committee).

---

### 2.6 `evidence-auditor`
- **Purpose**: Epistemic Integrity & Provenance Authority. Conducts forensic verification of citations, references, and originality.
- **Inputs**: Draft chapters, extracted reference libraries (`.bib`, `.enw`, `.ris`), Irandoc similarity reports.
- **Outputs**: Epistemic Integrity Audit Reports (`evidence_audit.json`), Citation Concordance Matrices, Plagiarism Mitigation Guides.
- **Responsibilities**:
  - Perform 100% bidirectional concordance matching: every in-text citation must resolve to bibliography, and vice-versa.
  - Eliminate ghost citations by verifying DOIs and bibliographic entries against CrossRef/PubMed/SID.
  - Audit Irandoc / SamimNoor similarity percentages, enforcing strict $< 20\%$ threshold.
  - Enforce 2026 Temporal Reality Anchor: ensure empirical literature reflects the 2021–2026 window.
- **Non-Responsibilities**:
  - Does NOT rewrite thesis narrative directly (issues specific revision directives to `academic-writer`).
  - Does NOT validate statistical degrees of freedom (handled by `statistical-auditor`).
- **Allowed Subagents**: `research-agent`, `literature-expert`, `validation-agent`.
- **Allowed Skills**: `academic-reference-extractor`, `irandoc-plagiarism-reducer`, `thesis-integrity-auditor`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (audit reports, citation resolution files).
- **May Execute Commands**: `true` (reference extractors, DOI lookup scripts).
- **May Invoke Other Agents**: `true` (invokes research workers for verification).
- **Approval Authority**: **Epistemic Clearance Gatekeeper** (Blocks release if ghost citations or $> 20\%$ similarity detected).

---

### 2.7 `final-judge`
- **Purpose**: Defense Committee Simulator & Institutional Release Gatekeeper. Simulates viva voce cross-examinations and provides final clearance.
- **Inputs**: Complete 5-chapter dissertation package, candidate defense slide deck, supervisor defense feedback.
- **Outputs**: Viva Voce Defense Interrogation Dossiers, Defense Readiness Certification, Supervisor Point-by-Point Response Tables.
- **Responsibilities**:
  - Simulate rigorous internal and external defense committee cross-examinations across 4 core scenarios.
  - Score defense readiness index: release requires strictly $\ge 95\%$ composite readiness.
  - Triage supervisor defense comments into actionable tracked changes.
  - Direct the adversarial challenger (`academic-challenger`) and quality critics.
- **Non-Responsibilities**:
  - Does NOT draft original thesis chapters.
  - Does NOT perform primary statistical analysis.
- **Allowed Subagents**: `evidence-auditor`, `statistical-auditor`, `results-auditor`, `academic-challenger`.
- **Allowed Skills**: `thesis-integrity-auditor`, `persian-thesis-revision-assistant`, `persian-defense-presentation-builder`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`, `invoke_subagent`, `manage_subagents`, `send_message`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (defense briefs, revision tables, clearance certificates).
- **May Execute Commands**: `true` (presentation builders, validator suites).
- **May Invoke Other Agents**: `true` (invokes critics and challenger).
- **Approval Authority**: **Institutional Release Gatekeeper** (Issues final defense clearance certificate).

---

## 3. Bounded Specialist Subagents Specification (15 Roles)

### 3.1 `research-agent`
- **Purpose**: Focused research worker executing empirical literature extraction.
- **Parent Authority**: `methodology-expert`.
- **Inputs**: Search queries, inclusion/exclusion criteria.
- **Outputs**: Literature extraction tables (`.xlsx`, `.json`), study parameter summaries.
- **Responsibilities**: Extract sample size, design, and scales from targeted papers.
- **Non-Responsibilities**: Does NOT formulate overall methodology or write final chapters.
- **Allowed Subagents**: None.
- **Allowed Skills**: `literature-harvester`, `persian-literature-review-builder`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (literature tables).
- **May Execute Commands**: `true` (harvesting scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.2 `literature-expert`
- **Purpose**: Academic literature search and bibliometric mapping specialist.
- **Parent Authority**: `methodology-expert`.
- **Inputs**: Research keywords, database credentials.
- **Outputs**: Harvested `.ris` / `.bib` files, VOSviewer co-occurrence matrices.
- **Responsibilities**: Query PubMed, CrossRef, and SID; compute Callon centrality coordinates.
- **Non-Responsibilities**: Does NOT conduct inferential modeling.
- **Allowed Subagents**: None.
- **Allowed Skills**: `literature-harvester`, `bibliometric-network-analyst`, `citation-network-visualizer`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (bibliographic libraries).
- **May Execute Commands**: `true` (bibliometric scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.3 `journal-strategist`
- **Purpose**: Academic journal article packaging and rebuttal specialist.
- **Parent Authority**: `academic-writer`.
- **Inputs**: Completed thesis chapters, author guidelines.
- **Outputs**: Formatted journal manuscript, cover letter, title page (CRediT format).
- **Responsibilities**: Format articles for WoS/Scopus/ISC target journals.
- **Non-Responsibilities**: Does NOT perform new statistical tests.
- **Allowed Subagents**: None.
- **Allowed Skills**: `journal-submission-assistant`, `academic-article-writer`, `persian-academic-translation`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (manuscript files).
- **May Execute Commands**: `true` (formatting tools).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.4 `meta-analyst`
- **Purpose**: PRISMA 2020 systematic review and quantitative meta-analysis specialist.
- **Parent Authority**: `methodology-expert`.
- **Inputs**: Extracted effect sizes, study sample sizes, RoB 2 risk of bias scores.
- **Outputs**: Pooled effect sizes (Hedges' g), heterogeneity indices ($I^2, Q$), Forest and Funnel plots.
- **Responsibilities**: Deterministically pool effect sizes using fixed/random-effects models.
- **Non-Responsibilities**: Does NOT analyze primary survey data.
- **Allowed Subagents**: None.
- **Allowed Skills**: `systematic-review-meta-analyst`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (meta-analysis reports, plot PNGs).
- **May Execute Commands**: `true` (R/Python meta-analysis scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.5 `data-agent`
- **Purpose**: Raw dataset ingestion, reverse coding, and baseline quality screening.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: Raw data files (`.xlsx`, `.csv`, `.sav`), questionnaire scoring keys.
- **Outputs**: `data_cleaned.xlsx`, `data_quality.json`, `data_dictionary.json`.
- **Responsibilities**: Ingest raw data, reverse code items against 4,880 questionnaire registry, screen Little's MCAR.
- **Non-Responsibilities**: Does NOT modify raw data files on disk (writes to new cleaned files).
- **Allowed Subagents**: None.
- **Allowed Skills**: `data-cleaning`, `data-audit`, `psychometric-scale-resolver`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (creates cleaned files only; raw data is immutable).
- **May Execute Commands**: `true` (data cleaning and Little's MCAR scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.6 `data-curator`
- **Purpose**: Specialist for advanced multivariate outlier diagnostics and demographic standardization.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: `data_cleaned.xlsx`, variable lists.
- **Outputs**: Outlier diagnostic report (`Mahalanobis D2`, Cook's distance), imputed datasets.
- **Responsibilities**: Detect multivariate outliers, screen unengaged respondents (straight-lining).
- **Non-Responsibilities**: Does NOT run inferential hypothesis models.
- **Allowed Subagents**: None.
- **Allowed Skills**: `data-audit`, `statistical-data-analyst`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (diagnostic reports).
- **May Execute Commands**: `true` (outlier detection scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.7 `statistics-agent`
- **Purpose**: Deterministic execution runner for inferential statistical engines and APA 7 tables.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: `data_cleaned.xlsx`, `analysis_plan.json`.
- **Outputs**: `stats_results.json`, APA 7 tables (`.docx`, `.md`), 300-DPI publication plots (`.png`).
- **Responsibilities**: Execute Python/R scripts (ANCOVA, RM-ANOVA, PROCESS bootstrap mediation, SEM) on verified data.
- **Non-Responsibilities**: Does NOT decide statistical strategy (executes instructions from `statistical-expert`).
- **Allowed Subagents**: None.
- **Allowed Skills**: `statistical-data-analyst`, `sem`, `cfa`, `regression`, `mediation`, `moderation`, `reliability-analysis`, `descriptive-statistics`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (analysis output files).
- **May Execute Commands**: `true` (deterministic statistical scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.8 `psychometric-expert`
- **Purpose**: Scale standardization and psychometric validation specialist.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: Questionnaire item responses, scale specifications.
- **Outputs**: CVR/CVI tables, EFA factor loading matrices, CFA fit indices, IRT Graded Response curves.
- **Responsibilities**: Execute Classical Test Theory (Lawshe CVR, Cronbach $\alpha$, McDonald $\omega$) and Item Response Theory.
- **Non-Responsibilities**: Does NOT draft non-psychometric dissertation chapters.
- **Allowed Subagents**: None.
- **Allowed Skills**: `psychometric-scale-validator`, `cfa`, `reliability-analysis`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (validation reports).
- **May Execute Commands**: `true` (psychometric validator scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.9 `longitudinal-modmed-expert`
- **Purpose**: 3-wave longitudinal moderated mediation modeling specialist.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: Multi-wave panel dataset, model specification.
- **Outputs**: Longitudinal path coefficients, autoregressive baselines, 5,000 bootstrap index of moderated mediation.
- **Responsibilities**: Estimate Cole & Maxwell longitudinal mediation and conditional indirect effects over time.
- **Non-Responsibilities**: Does NOT analyze cross-sectional data.
- **Allowed Subagents**: None.
- **Allowed Skills**: `longitudinal-moderated-mediation`, `statistical-data-analyst`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (model outputs).
- **May Execute Commands**: `true` (longitudinal scripts).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.10 `intervention-designer`
- **Purpose**: Standardized psychological intervention manual and protocol builder.
- **Parent Authority**: `methodology-expert`.
- **Inputs**: Intervention theoretical orientation (ACT, CBT, Schema, CFT), target population, session count.
- **Outputs**: Chapter 3 intervention session tables, clinical manual (`.docx`), fidelity checklists.
- **Responsibilities**: Design standardized session-by-session clinical manuals and client worksheets.
- **Non-Responsibilities**: Does NOT analyze empirical outcome data.
- **Allowed Subagents**: None.
- **Allowed Skills**: `psychological-intervention-protocol-builder`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (protocol documents).
- **May Execute Commands**: `false`.
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.11 `qualitative-analyst`
- **Purpose**: Qualitative research and thematic analysis specialist.
- **Parent Authority**: `methodology-expert`.
- **Inputs**: Interview transcripts, qualitative coding guidelines.
- **Outputs**: Braun & Clarke theme hierarchy, Grounded Theory Paradigmatic Model, inter-coder reliability ($k$).
- **Responsibilities**: Perform open, axial, and selective coding; compute Cohen's kappa across coders.
- **Non-Responsibilities**: Does NOT run quantitative inferential tests.
- **Allowed Subagents**: None.
- **Allowed Skills**: `qualitative-data-analyst`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (qualitative matrices).
- **May Execute Commands**: `true` (thematic engine).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.12 `validation-agent`
- **Purpose**: Deterministic validator suite executor and cross-chapter consistency auditor.
- **Parent Authority**: `academic-writer`.
- **Inputs**: Generated stage artifacts (`.docx`, `.md`, `.json`).
- **Outputs**: `validation_report.json`, cross-chapter consistency audit report.
- **Responsibilities**: Execute `validators/run_all_validators.py` and verify physical artifact completeness.
- **Non-Responsibilities**: Does NOT author thesis content or modify statistical numbers.
- **Allowed Subagents**: None.
- **Allowed Skills**: `thesis-integrity-auditor`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (validation reports only).
- **May Execute Commands**: `true` (validator suite runner).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.13 `results-auditor`
- **Purpose**: Adversarial critic enforcing APA 7 typography, numeric precision, and OpenXML equation preservation.
- **Parent Authority**: `academic-writer`.
- **Inputs**: Draft markdown and docx artifacts.
- **Outputs**: Typography audit report, formatting checklist (`results_qc_checklist.json`).
- **Responsibilities**: Verify 2-decimal reporting, exact 3-decimal p-values ($p < .001$), Persian leading zero (۰.۰۵), and OMML equation preservation.
- **Non-Responsibilities**: Does NOT rewrite narrative text or recalculate statistics.
- **Allowed Subagents**: None.
- **Allowed Skills**: `apa-reporting`, `thesis-integrity-auditor`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (QC reports).
- **May Execute Commands**: `false`.
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.14 `statistical-auditor`
- **Purpose**: Adversarial quality auditor for degrees of freedom, parametric assumptions, and MSAI anomaly detection.
- **Parent Authority**: `statistical-expert`.
- **Inputs**: `stats_results.json`, `data_cleaned.xlsx`, draft results text.
- **Outputs**: `statistical_audit_report.json`, MSAI Anomaly Score report.
- **Responsibilities**: Verify statistical df against sample size $N$, detect variance deflation, compute Multi-Signal Anomaly Index (MSAI).
- **Non-Responsibilities**: Does NOT re-run statistical models directly.
- **Allowed Subagents**: None.
- **Allowed Skills**: `thesis-integrity-auditor`, `assumption-testing`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`, `run_command`.
- **MCP Requirements**: None.
- **Model Requirements**: `flash`.
- **May Modify Files**: `true` (audit reports).
- **May Execute Commands**: `true` (MSAI detector script).
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.

---

### 3.15 `academic-challenger` (NEW ROLE)
- **Purpose**: Adversarial Committee Interrogator & Harsh Reviewer. Simulates aggressive viva voce defense examiners and critical journal reviewers.
- **Parent Authority**: `final-judge` (also callable by `methodology-expert` and `statistical-expert` during stress-testing).
- **Inputs**: Research proposals, completed empirical chapters, defense slide decks.
- **Outputs**: Adversarial Challenge Dossiers (10 hard defense questions, methodological counter-arguments, supervisor traps).
- **Responsibilities**:
  - Uncover methodological vulnerabilities, alternative explanations, and unaddressed confounds.
  - Formulate rigorous, adversarial viva voce questions designed to test the candidate's mastery.
  - Stress-test non-significant findings ($p > .05$) and marginal effect sizes.
- **Non-Responsibilities**:
  - Does NOT approve or certify deliverables (purely an adversarial challenger).
  - Does NOT rewrite drafts or execute computations.
- **Allowed Subagents**: None.
- **Allowed Skills**: `thesis-integrity-auditor`, `methodology-review`.
- **Allowed Tools**: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`.
- **MCP Requirements**: None.
- **Model Requirements**: `pro`.
- **May Modify Files**: `true` (challenge dossiers only).
- **May Execute Commands**: `false`.
- **May Invoke Other Agents**: `false`.
- **Approval Authority**: None.
