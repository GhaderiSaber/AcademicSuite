# MICRO_STAGE_SEQUENCES.md — Thesis Pipeline Micro-Stage Reference Manual

This reference manual documents the complete, authoritative micro-stage breakdown, assigned subagents, deterministic execution scripts, and required physical triad artifacts (`.docx` + `.md` + `.json`) for each academic pipeline in the Academic Suite.

Per **Directive 3 (Artifact-Gated Stage Execution, Micro-Stage Granularity & Triad Artifact Invariant)** in [`AGENTS.md`](../../AGENTS.md), jumping stages without physical checkpoint files existing on disk is strictly prohibited. Every individual micro-stage must produce its synchronized triad of deliverables prior to stage-gate advancement.

---

## 1. Chapter 4: Decoupled Empirical Findings Pipeline (Phases 4A – 4D)

Chapter 4 operates strictly as a **Four-Phase Decoupled Pipeline** separating computational data engineering and inferential modeling from academic drafting. The pipeline enforces three intermediate mathematical/methodological validation gates before a single sentence of narrative text is drafted.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase 4A: Data Engineering & Curation (data-curator, psychometric-expert)               │
│ -> Reverse coding, MCAR missingness, outlier screening (D²), scale reliability (α, ω)  │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼ [Gate 1: Data Curation Passport]
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase 4B: Exploratory Analysis & Assumptions (statistics-agent, statistical-expert)    │
│ -> Demographics, univariate descriptives, parametric assumptions, bivariate matrix     │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼ [Gate 2: Assumption Compliance & Method Authorization]
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase 4C: Core Inferential Modeling & Audit (statistics-agent, statistical-auditor)    │
│ -> SEM macro fit, hypothesis testing, bootstrap mediation (5,000 BCa), MSAI QC audit   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            ▼ [Gate 3: Mathematical Admissibility & MSAI Sign-Off]
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase 4D: Scholarly Persian Drafting & Assembly (academic-writer, results-auditor)     │
│ -> Section triads (.docx, .md, .json), 3-table standard, OpenXML master compilation    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 4A: Data Engineering & Curation Gate (The Foundation)
* **Assigned Subagents**: `data-curator`, `psychometric-expert`
* **Directives & Role**: Strictly "The Hands". Ingests raw survey inputs, cleans items, resolves reverse coding, screens missing data and multivariate outliers, and locks the final dataset. ZERO narrative text is drafted.

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 4A.0** | Data Quality Screening & Outliers | `data-curator` | `data_curation_pipeline.py` / `data-audit` | `00_data_curation_report.json`, `00_data_curation_report.md` |
| **Stage 4A.1** | Reverse-Scoring & Scale Aggregation | `data-curator` + `psychometric-expert` | `psychometric_scale_resolver.py` / `data-cleaning` | `data_cleaned.xlsx`, `codebook_manifest.json` |
| **Stage 4A.2** | Baseline Scale Reliability ($\alpha, \omega$) | `statistics-agent` | `scale_reliability_runner.py` / `reliability-analysis` | `00_scale_reliability_baseline.json` |

* **Gate 1 Checkpoint**: `data_cleaned.xlsx` is permanently locked and frozen. No downstream stage may alter raw or cleaned datasets (Directive 24 / AP-2026-RAW-DATASET-MUTATION).

---

### Phase 4B: Exploratory Analysis & Assumptions Gate (The Method Gate)
* **Assigned Subagents**: `statistics-agent`, `statistical-expert`
* **Directives & Role**: Strictly "The Hands". Computes sample distributions, univariate normality, homoscedasticity, collinearity, and bivariate correlations. Prepares structured JSON payloads and verifies parametric eligibility before selecting/authorizing inferential tests.

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 4B.1** | Demographic Frequencies & Profiles | `statistics-agent` | `demographic_profiler.py` / `descriptive-statistics` | `01_demographics_payload.json` |
| **Stage 4B.2** | Univariate Descriptives ($M, SD$, Skew, Kurt) | `statistics-agent` | `descriptive_statistics_runner.py` | `02_descriptives_payload.json` |
| **Stage 4B.3** | Parametric Assumptions Verification | `statistical-expert` + `statistics-agent` | `assumption_tester.py` / `assumption-testing` | `03_assumptions_report.json`, `03_assumptions_report.md` |
| **Stage 4B.4** | Bivariate Pearson Correlation Matrix | `statistics-agent` | `correlation_matrix_builder.py` | `04_correlations_payload.json` |

* **Gate 2 Checkpoint**: `statistical-expert` issues the **Assumption Compliance Certificate**. If assumptions fail (e.g. $VIF > 5$ or extreme non-normality), the modeling plan is dynamically adjusted (e.g. robust standard errors, WLS, bootstrapping, or variable restructuring) *prior* to inferential execution.

---

### Phase 4C: Core Inferential Modeling & Anomaly Audit (The Evidence)
* **Assigned Subagents**: `statistics-agent`, `statistical-auditor`
* **Directives & Role**: Strictly "The Hands" and Adversarial Auditor. Executes approved hypothesis tests, structural models, and bootstrap indirect mediation. Evaluates the Multi-Signal Anomaly Index (MSAI) to verify degrees of freedom, variance plausibility, and admissibility.

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 4C.1** | Macro Model Fit / Structural Model | `statistics-agent` | `sem_modeler.py` / `sem_lavaan_runner.R` | `05_macro_model_payload.json`, `structural_model_diagram.png` (300 DPI) |
| **Stage 4C.2.1** | Hypothesis 1 Inferential Test | `statistics-agent` | Deterministic hypothesis runner (`regression.py`, etc.) | `06_hypothesis_1_payload.json` |
| **Stage 4C.2.k** | Hypothesis $k$ Inferential Test | `statistics-agent` | Deterministic hypothesis runner | `XX_hypothesis_k_payload.json` |
| **Stage 4C.3.1** | Indirect / Mediation Path 1 (Bootstrap 5,000) | `statistics-agent` | `bootstrap_mediation_runner.py` | `XX_mediation_1_payload.json` |
| **Stage 4C.3.k** | Indirect / Mediation Path $k$ (Bootstrap 5,000) | `statistics-agent` | `bootstrap_mediation_runner.py` | `XX_mediation_k_payload.json` |
| **Stage 4C.4** | Master Hypotheses Decision Matrix Synthesis | `statistics-agent` + `statistical-expert` | `decision_matrix_generator.py` | `master_decision_matrix.json` |
| **Stage 4C.5** | Statistical QC & MSAI Anomaly Audit | `statistical-auditor` | `msai_detector.py` / `statistical-auditor` | `empirical_findings_payload.json`, `statistical_audit_report.json` |

* **Gate 3 Checkpoint**: Mathematical Admissibility & Statistical Clearance Gate. `statistical-auditor` certifies `overall_verdict: "PASS"` on `statistical_audit_report.json`. The user and committee review empirical parameters before authoring narrative text.

---

### Phase 4D: Scholarly Persian Drafting, QC & Monograph Assembly (The Voice)
* **Assigned Subagents**: `academic-writer`, `results-auditor`, `final-judge`
* **Directives & Role**: Strictly "The Voice". Decouples drafting into **Tables First** followed by **Dynamic Epistemic Narration** for each table. Ingests the audited, immutable `empirical_findings_payload.json`. Formulates continuous Persian academic prose using Saber's 4-element epistemic framing (Context $\to$ Highlights $\to$ Table Reference $\to$ Verdict), enforces APA 7 typography, and compiles synchronized triad artifacts (`.docx` + `.md` + `.json`).

#### 💡 The Internal Writing Phase Decoupling (Tables First $\to$ Dynamic Narration)
Phase 4D strictly executes in a two-step sequence for every section and hypothesis:
1. **Step 4D-1: Deterministic Table Scaffolding (Tables First)**:
   - Scaffolds and renders exact APA 7 Word (`<w:tbl>`) and Markdown (`|---|`) tables directly from audited JSON payloads (`01_demographics_payload.json`, `06_hypothesis_1_payload.json`, etc.).
   - Strictly enforces 3 horizontal borders (Top 0.75 pt, Header bottom 0.5 pt, Table bottom 0.75 pt), zero vertical borders, italicized Latin statistical symbols ($M, SD, t, F, p, R, R^2, \beta, B$), decoupled LTR numeric runs with Persian leading zeros (`۰.۰۵`, `۰.۰۰۱`), and Persian notes defining abbreviations.
   - For regression hypotheses, strictly renders the canonical 3-table standard (Table 1: Correlations, Table 2: Model Summary & ANOVA with 11 columns, Table 3: Coefficients & Collinearity with 8 columns).
   - **Zero narrative prose is written in this step.** Tables stand as the immutable, objective empirical anchor.
2. **Step 4D-2: Dynamic Epistemic Narration Formulation (Zero Prewritten / Zero Template Invariant)**:
   - Ingests the rendered table and its exact numerical cell values.
   - Dynamically composes authentic, scholarly Persian narrative tailored specifically to that table using Saber's 4-element epistemic structure (Context $\to$ Data Highlights $\to$ In-Text Reference $\to$ Statistical Verdict).
   - **Strict Zero-Template & Anti-Boilerplate Invariant**:
     - Prewritten boilerplate, static placeholders (e.g. `در این بخش نتایج مربوط به ... گزارش می‌گردد`, `بر اساس داده‌های به دست آمده، فرضیه مورد تأیید قرار گرفت`), and mechanical fill-in-the-blank text are **strictly prohibited**.
     - Narration must be dynamically synthesized to reflect the exact empirical findings: specific construct names, effect size magnitudes ($\eta^2_p, R^2$), standardized beta weights ($\beta$), standard errors ($SE$), exact $p$-values, degrees of freedom, and psychological meaning.
     - Triad compilers and validation gates must refuse and fail any deliverable containing empty, canned, or template placeholder text.
3. **Step 4D-3: Synchronized Triad Compilation & Monograph Assembly**:
   - Pairs each dynamic narrative paragraph directly with its corresponding formatted table.
   - Compiles physical section triads (`.docx`, `.md`, `.json`).
   - DOM-based consolidation of verified triads into `Chapter_4_Results.docx` and `Chapter_4_Results.md`.

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Triad Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 4D.0** | Chapter Structural Overview & Introduction | `academic-writer` | `academic_docgen.py` | `00_chapter_overview.docx`, `00_chapter_overview.md`, `00_chapter_overview.json` |
| **Stage 4D.1** | Demographic Profiles (Tables + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `01_demographics.docx`, `01_demographics.md`, `01_demographics.json` |
| **Stage 4D.2** | Descriptives & Reliability (Tables + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `02_descriptives_and_reliability.docx`, `.md`, `.json` |
| **Stage 4D.3** | Parametric Assumptions (Tables + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `03_parametric_assumptions.docx`, `.md`, `.json` |
| **Stage 4D.4** | Bivariate Correlation Matrix (Table + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `04_bivariate_correlations.docx`, `.md`, `.json` |
| **Stage 4D.5** | Macro Model Fit & Diagram (Diagram/Table + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `05_macro_model.docx`, `.md`, `.json` |
| **Stage 4D.6.1** | Hypothesis 1 Triad (3-Table Standard + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json` |
| **Stage 4D.6.k** | Hypothesis $k$ Triad (3-Table Standard + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `XX_hypothesis_k.docx`, `XX_hypothesis_k.md`, `XX_hypothesis_k.json` |
| **Stage 4D.7.1** | Mediation Path 1 Triad (Bootstrap Table + Dynamic Narration) | `academic-writer` | `academic_docgen.py` | `XX_mediation_1.docx`, `XX_mediation_1.md`, `XX_mediation_1.json` |
| **Stage 4D.8** | Master Decision Matrix & Summary (Matrix Table + Synthesis) | `academic-writer` | `academic_docgen.py` | `XX_chapter_summary.docx`, `XX_chapter_summary.md`, `XX_chapter_summary.json` |
| **Stage 4D.9** | Results QC & APA 7 Typography Audit | `results-auditor` | `apa_typography_checker.py` | `XX_results_qc_checklist.json`, `XX_results_qc_checklist.md` |
| **Stage 4D.10** | Chapter 4 Master Monograph Consolidation | `academic-writer` | `chapter_assembler.py` | `Chapter_4_Results.docx`, `Chapter_4_Results.md` |
| **Stage 4D.11** | Committee Defense Viva Voce Brief | `final-judge` | `viva_voce_simulator.py` | `XX_defense_brief.docx`, `XX_defense_brief.md`, `XX_defense_brief.json` |

---

### 💡 The Decoupled Pipeline Invariant & Immutable Contract
1. **Computational Immunity**: Subagents executing Phases 4A, 4B, and 4C must strictly produce machine-readable JSON payloads, analysis code, and clean figures. Emitting Persian narrative draft text in Phases 4A–4C is strictly prohibited.
2. **Hallucination Prevention**: `academic-writer` in Phase 4D is physically restricted to citing parameters present in the audited `empirical_findings_payload.json`. Inventing statistics or altering numerical values during prose formulation is strictly blocked.
3. **One-Hypothesis-One-Stage Triad Invariant**: In Phase 4D, each research hypothesis is drafted in its own isolated micro-stage (producing `.docx` + `.md` + `.json`) enforcing the canonical 3-table standard (Table 1: Correlations, Table 2: Model Summary & ANOVA with 11 columns, Table 3: Coefficients & Collinearity with 8 columns).
4. **Zero-Template Dynamic Narration Invariant**: Prewritten templates, placeholder stubs, or boilerplate narrative paragraphs are strictly prohibited. Narration for each table must be dynamically generated from that table's exact cells using Saber's 4-element epistemic structure. Any deliverable containing template text will fail validation.

---

## 2. Chapter 5: Discussion & Conclusion Pipeline (Stages 5.1 – 5.10)

| Stage | Name | Assigned Subagent | Focus / Methodology | Required Physical Triad Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 5.1** | Findings Overview & Purpose Recap | `academic-writer` | Restatement of research aim and high-level summary of validated models | `01_findings_recap.docx`, `01_findings_recap.md`, `01_findings_recap.json` |
| **Stage 5.2.1** | Hypothesis 1 Deep Discussion | `academic-writer` + `literature-expert` | 4-Element Psychological Model: Verdict $\to$ Article Concordance $\to$ Mechanisms $\to$ Nuances | `02_hypothesis_1_discussion.docx`, `02_hypothesis_1_discussion.md`, `02_hypothesis_1_discussion.json` |
| **Stage 5.2.2** | Hypothesis 2 Deep Discussion | `academic-writer` + `literature-expert` | Psychological mechanisms, theoretical backing, Iranian & international alignment | `03_hypothesis_2_discussion.docx`, `03_hypothesis_2_discussion.md`, `03_hypothesis_2_discussion.json` |
| **Stage 5.2.k** | Hypothesis $k$ Deep Discussion | `academic-writer` + `literature-expert` | In-depth mechanism dissection for hypothesis $k$ seeded from parsed articles | `XX_hypothesis_k_discussion.docx`, `XX_hypothesis_k_discussion.md`, `XX_hypothesis_k_discussion.json` |
| **Stage 5.3** | Unexpected / Non-Significant Findings Analysis | `academic-writer` + `methodology-expert` | Epistemic analysis of null results, statistical power caveats, suppressor effects | `XX_non_significant_findings.docx`, `XX_non_significant_findings.md`, `XX_non_significant_findings.json` |
| **Stage 5.4** | Theoretical, Clinical & Practical Implications | `academic-writer` | Actionable recommendations for clinical practice, educational policy, and theory | `XX_implications.docx`, `XX_implications.md`, `XX_implications.json` |
| **Stage 5.5** | Methodological, Sampling & Instrument Limitations | `methodology-expert` | Internal/external validity limits, cross-sectional constraints, self-report bias | `XX_limitations.docx`, `XX_limitations.md`, `XX_limitations.json` |
| **Stage 5.6** | Future Research & Actionable Recommendations | `academic-writer` | Methodological directions, prospective longitudinal designs, experimental follow-ups | `XX_recommendations.docx`, `XX_recommendations.md`, `XX_recommendations.json` |
| **Stage 5.7** | Statistical Claim & Number Fidelity Audit | `results-auditor` | Cross-checks reported statistical numbers in narrative against Chapter 4 results | `XX_results_fidelity_report.json`, `XX_results_fidelity_report.md` |
| **Stage 5.8** | Evidence Concordance & Citation Integrity Audit | `evidence-auditor` | Zero orphaned/ghost citations, Irandoc similarity < 20%, elimination of AI clichés | `XX_evidence_audit_report.json`, `XX_evidence_audit_report.md` |
| **Stage 5.9** | Chapter 5 Consolidation & Assembly | `academic-writer` | Institutional OpenXML consolidation with pristine Persian typography | `Chapter_5_Discussion.docx`, `Chapter_5_Discussion.md` |
| **Stage 5.10** | Doctoral Defense Viva Voce Discussion Brief | `final-judge` | Committee defense cross-examination simulator & viva voce discussion brief | `XX_defense_discussion_brief.docx`, `XX_defense_discussion_brief.md`, `XX_defense_readiness.json` |

### 💡 The Two-Pass Epistemic Handshake Invariant (Stages 5.2.1 – 5.2.k)
Every discussion micro-stage strictly executes in a two-step handshake:
1. **Pass 1: Mechanism & Evidence Formulation (`literature-expert` + `methodology-expert`)**:
   Ingests Chapter 4 verified findings and local research articles (`04_references_and_lit/papers/`), running `article_enrichment_engine.py` to extract `article_enrichment_cards.json`. Identifies 3–5 concordant (همسو) and discordant (ناهمسو) empirical studies and pinpoints underlying psychological/behavioral mechanisms (Beck CBT, Hayes ACT, Bandura, Gross). Outputs structured conceptual cards with ZERO verbatim copying.
2. **Pass 2: Scholarly Rhetoric & Assembly (`academic-writer` — The Voice)**:
   Ingests the conceptual cards, formulates scholarly Persian narrative using the 4-element model, applies cadence variability ($CV \ge 0.50$), and compiles the physical triad (`.docx`, `.md`, `.json`) using `scaffold_chapter5_triad.py`. Strict prohibition: Zero verbatim plagiarism of English strings; pure scholarly Persian synthesis.

---

## 3. Chapter 2: Literature Review Pipeline (Stages 2.1 – 2.8)

| Stage | Name | Focus / Methodology | Required Triad Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage 2.1** | Theoretical Foundations & Conceptual Framework | Core theories, historical evolution, theoretical definitions | `01_theoretical_foundations.docx`, `.md`, `.json` |
| **Stage 2.2** | Bibliometric Network Analysis | VOSviewer science mapping, co-occurrence, Callon density | `02_bibliometric_network.docx`, `.md`, `.json` |
| **Stage 2.3** | International Empirical Studies (2021–2026) | Inverted-triangle synthesis of global peer-reviewed findings | `03_international_literature.docx`, `.md`, `.json` |
| **Stage 2.4** | Iranian Empirical Studies (1400–1405 SH) | Domestic empirical literature, cultural considerations | `04_iranian_literature.docx`, `.md`, `.json` |
| **Stage 2.5** | Epistemic Evidence Weighting & Synthesis | Cross-study comparative synthesis and research gap identification | `05_epistemic_synthesis.docx`, `.md`, `.json` |
| **Stage 2.6** | Summary Matrix Table | Comprehensive comparative table (Author, Year, Design, N, Measure, Finding) | `06_literature_matrix_table.docx`, `.md`, `.json` |
| **Stage 2.7** | Conceptual Model & Hypothesis Grounding | Direct and indirect conceptual grounding tying literature to hypotheses | `07_conceptual_model_grounding.docx`, `.md`, `.json` |
| **Stage 2.8** | Chapter 2 OpenXML Assembly | Master compilation with verified in-text citations and EndNote CWYW fields | `Chapter_2_Literature_Review.docx`, `.md` |

---

## 4. Research Proposal Pipeline (Stages P.1 – P.8)

| Stage | Name | Focus / Methodology | Required Triad Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage P.1** | Problem Statement & Background | Inverted-triangle problem formulation, epidemiological context, research gap | `01_problem_statement.docx`, `.md`, `.json` |
| **Stage P.2** | Research Significance & Objectives | Theoretical innovation, practical utility, primary and secondary aims | `02_significance_and_objectives.docx`, `.md`, `.json` |
| **Stage P.3** | Research Questions & Hypotheses | Directional, testable statistical hypotheses aligned with structural model | `03_questions_and_hypotheses.docx`, `.md`, `.json` |
| **Stage P.4** | Research Methodology & Design | Design classification (correlational, SEM, RCT), operational validity safeguards | `04_methodology_and_design.docx`, `.md`, `.json` |
| **Stage P.5** | Population, Sampling & Power (G*Power) | A priori statistical power calculations ($\alpha = .05, 1-\beta = .80$), sample size determination | `05_sampling_and_power.docx`, `.md`, `.json` |
| **Stage P.6** | Measurement Instruments & Psychometrics | Scale psychometric background, reliability ($\alpha, \omega$), reverse scoring rules | `06_measurement_instruments.docx`, `.md`, `.json` |
| **Stage P.7** | Implementation Procedure & Ethics | Data collection protocol, ethical codes, informed consent, data privacy | `07_procedure_and_ethics.docx`, `.md`, `.json` |
| **Stage P.8** | Proposal Compilation & Assembly | Institutional proposal assembly with standard cover page, timeline, and references | `Research_Proposal.docx`, `Research_Proposal.md` |

---

## 5. Psychometric Scale Validation Pipeline (Stages V.1 – V.9)

| Stage | Name | Focus / Methodology | Required Triad Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage V.1** | Content & Face Validity (CVR / CVI) | Lawshe CVR, Lynn CVI, expert panel scoring and item refinement | `01_content_validity.docx`, `.md`, `.json` |
| **Stage V.2** | Item Analysis & Screening | Item-total correlation ($r_{it} \ge .30$), skewness/kurtosis, floor/ceiling effects | `02_item_analysis.docx`, `.md`, `.json` |
| **Stage V.3** | Exploratory Factor Analysis (EFA) | KMO, Bartlett sphericity, scree plot, parallel analysis, Promax/Varimax rotation | `03_efa_analysis.docx`, `.md`, `.json` |
| **Stage V.4** | Confirmatory Factor Analysis (CFA) | First-order and higher-order CFA, standardized factor loadings ($\lambda \ge .50$) | `04_cfa_analysis.docx`, `.md`, `.json` |
| **Stage V.5** | Construct Validity (AVE, CR, Fornell-Larcker) | Convergent validity ($\text{AVE} \ge .50, \text{CR} \ge .70$), discriminant validity (HTMT $< .85$) | `05_construct_validity.docx`, `.md`, `.json` |
| **Stage V.6** | Measurement Invariance (Configural, Metric, Scalar) | Multigroup invariance across gender/demographics ($\Delta \text{CFI} \le .010$) | `06_measurement_invariance.docx`, `.md`, `.json` |
| **Stage V.7** | Reliability Analysis ($\alpha$, $\omega$, Test-Retest) | McDonald's omega, Cronbach's alpha, composite reliability, test-retest ICC | `07_reliability_analysis.docx`, `.md`, `.json` |
| **Stage V.8** | Item Response Theory (IRT) & ROC Curves | Graded Response Model (GRM), item information curves (IIC), sensitivity/specificity | `08_irt_and_roc.docx`, `.md`, `.json` |
| **Stage V.9** | Validation Report Assembly & Test Manual | Comprehensive test manual, normative scoring tables, and OpenXML monograph | `Scale_Validation_Report.docx`, `.md` |

---

## 6. Academic Defense Presentation Builder (Stages D.0 – D.7)

| Stage | Name | Focus / Technical Deliverable | Required Artifacts |
| :--- | :--- | :--- | :--- |
| **Stage D.0** | Findings Ingestion & Verification | Ingestion of Chapter 4/5 statistics and verification of exact numerical parameters | `00_defense_findings_payload.json` |
| **Stage D.1** | Storyboard & 14-Slide Architecture | 14-slide narrative storyboard, time allocation (20 min total), layout geometry | `01_defense_storyboard.docx`, `.md`, `.json` |
| **Stage D.2** | Dedicated Statistical & Hypothesis Triads | Dedicated slide triads for every single hypothesis, macro model, and mediation path | `02_hypothesis_slides.docx`, `.md`, `.json` |
| **Stage D.3** | Deterministic Deck Compilation | DrawingML PPTX (B Titr / B Nazanin / Times New Roman) + Standalone 16:9 HTML deck | `Defense_Presentation.pptx`, `presentation.html` |
| **Stage D.4** | Publication Structural Diagram | 300-DPI high-resolution statistical diagram with path coefficients and $p$-values | `structural_model_diagram.png` |
| **Stage D.5** | Candidate 20-Minute Defense Script & Q&A Guide | Verbatim oral script with timing cues, slide change triggers, and anticipated examiner questions | `04_defense_script.docx`, `.md`, `.json` |
| **Stage D.6** | Geometry Collision & Typography Audit | Automated bounding box collision audit, font dual-slot check, zero-emoji verification | `05_presentation_qa_audit.json`, `.md` |
| **Stage D.7** | Committee Viva Voce Oral Defense Simulation | Hostile/rigorous mock defense simulation across methodological, statistical, and clinical axes | `06_defense_committee_simulation.docx`, `.md`, `.json` |

---

## 7. Empirical Data Generation & Simulation Pipeline (Stages DS.0 – DS.5)

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Triad Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage DS.0** | Pre-Execution Model Blueprint & Confirmation Gate | `academic-orchestrator` | `orchestrator_dependency_resolver.py data-blueprint` | `00_model_blueprint.docx`, `00_model_blueprint.md`, `00_model_blueprint.json` |
| **Stage DS.1** | Simulation Specification & Power Analysis | `methodology-expert` | `gpower_engine.py` / `methodology-review` | `01_simulation_spec.docx`, `01_simulation_spec.md`, `01_simulation_spec.json` |
| **Stage DS.2** | Instrument Grounding & Factor Weights | `data-agent` | `questionnaire_resolver.py` | `02_scales_codebook.docx`, `02_scales_codebook.md`, `02_scales_codebook.json` |
| **Stage DS.3** | Monte Carlo Simulation & Model Synthesis | `data-agent` | `simdat_engine.py` / `sem_data_maker.R` | `03_simulation_report.docx`, `03_simulation_report.md`, `03_simulation_results.json`, `primary_data.xlsx`, `final_data.xlsx` |
| **Stage DS.4** | Data Quality, Distribution & Anomaly Screening | `statistical-auditor` | `data-audit` / `assumption-testing` | `04_data_audit_report.docx`, `04_data_audit_report.md`, `04_data_audit_report.json` |
| **Stage DS.5** | Data Curation, Codebook & Provenance Handoff | `data-curator` | `data_curation_pipeline.py` | `05_dataset_codebook.docx`, `05_dataset_codebook.md`, `05_data_provenance.json`, `data_curated.xlsx` |

### 💡 The Simulation Invariants (Stages DS.0 – DS.5)
0. **Pre-Execution Blueprint & User Confirmation (Stage DS.0)**: Before initiating data synthesis, the Orchestrator MUST formulate and present the complete model specification, data parameters, and micro-stage roadmap to the user, and pause for explicit approval or refinement. No simulation subagent may be launched without user confirmation.
1. **Directive 9 (Realistic Decimal Noise)**: Means must have realistic empirical decimal noise ($\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$); whole-integer means in generated Likert composite aggregates are strictly invalid.
2. **Discrete Likert Integers**: Individual item ratings must be integer-quantized within authentic rating boundaries (e.g. $[1, 5]$ or $[1, 7]$).
3. **$J$-Batch Optimization**: Structural equation models must iterate through $J$ candidate batches to guarantee mathematical convergence and optimal fit ($\text{CFI} \ge .90, \text{RMSEA} \le .08$).
4. **MSAI Screening**: Multi-Signal Anomaly Index (Directive 10) must be evaluated prior to release to confirm absence of single-point fabrication signatures.

---

## 8. Universal Academic Revision Pipeline (Stages R.0 – R.6)

The Universal Academic Revision Pipeline provides an end-to-end, multi-agent, artifact-gated workflow for remediating and documenting revisions requested by journal peer reviewers, dissertation defense examination committees, or thesis supervisors. It supports polymorphic scope spanning **Journal Articles** (`journal_article`), **Individual Chapters** (`single_chapter`), **Full Theses** (`full_thesis`), **Research Proposals** (`proposal`), and **Generic Academic Documents** (`generic_document`).

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage R.0** | Feedback Ingestion & Polymorphic Scoping | `academic-orchestrator` / `data-agent` | `extract_docx_comments.py` | `00_extracted_comments.docx`, `00_extracted_comments.md`, `00_extracted_comments.json`, `revision_scope_manifest.json` |
| **Stage R.1** | 3-Tier Multi-Domain Triage & Delegation Matrix | `academic-orchestrator` | `revision_pipeline_engine.py --triage` | `01_revision_triage_plan.docx`, `01_revision_triage_plan.md`, `01_revision_triage_plan.json` |
| **Stage R.2** | Computational Recalculations & Statistical Patches | `statistics-agent` + `statistical-auditor` | Deterministic CLI (`regression.py`, `cfa.py`, etc.) | `02_statistical_revisions.docx`, `02_statistical_revisions.md`, `02_statistical_revisions.json` |
| **Stage R.3** | Surgical In-Place Manuscript Remediation | `academic-writer` | `revision_pipeline_engine.py --remediate` | `*_Revised.docx`, `03_manuscript_remediation_log.docx`, `03_manuscript_remediation_log.md`, `03_remediation_manifest.json` |
| **Stage R.4** | Formal Point-by-Point Rebuttal Compilation | `academic-writer` | `generate_revision_response_docx.py` | `Revision_Response_Table.docx` (or `Response_to_Reviewers.docx`), `.md`, `04_resolved_comments.json` |
| **Stage R.5** | Adversarial Revision Audit & TIS Check | `validation-agent` + `thesis-integrity-auditor` | `pipeline_auditor.py --workflow academic_revision` | `05_revision_validation_report.docx`, `05_revision_validation_report.md`, `validation_report.json` |
| **Stage R.6** | Final Sign-Off & Administrative Human Gate | `final-judge` + Admin Desk (`124911145`) | `viva_voce_simulator.py` | `06_revision_clearance_dossier.docx`, `06_revision_clearance_dossier.md`, `06_final_clearance_decision.json` |

### 💡 The Universal Revision Invariants (Stages R.0 – R.6)
0. **Polymorphic Scope**: Dynamically operates on journal articles, single chapters, proposals, or full dissertations, generating scope-tailored deliverables (`Article_Revised.docx` + `Response_to_Reviewers.docx`, `Chapter_4_Revised.docx` + `Chapter_4_Revision_Response_Table.docx`, or `Thesis_Revised.docx` + `Revision_Response_Table.docx`).
1. **Universal Document Conservation Gate (LSN-2026-DOCUMENT-CONSERVATION-IN-PLACE-REVISION)**: Clean-room document replacement is strictly forbidden (Draft Obliteration Anti-Pattern `AP-2026-DRAFT-OBLITERATION-REPLACEMENT`). The output document size must satisfy $\text{output\_bytes} \ge \text{input\_bytes} \times 0.90$.
2. **Surgical Run-Level Mutation (AP-2026-PARAGRAPH-CLEAR-HIGHLIGHT-WIPEOUT)**: `paragraph.clear()` is banned during revision. Text mutations must execute at the XML run level (`<w:r>`). Existing client formatting (e.g., green highlights) must be preserved 100%, and all new revisions must be marked in yellow highlights for reviewer/committee inspection.
3. **Exhaustive Comment Coverage (LSN-2026-EXHAUSTIVE-SUPERVISOR-REVISION-AUDIT)**: 100% of extracted reviewer or supervisor comments must be explicitly accounted for, resolved, and documented in the rebuttal table. Zero selective skipping.
4. **APA 7 Tables & Persian Leading Zeros (Directives 4 & 5)**: Response tables require 3 horizontal borders, zero vertical borders, and proper Persian/English decimal typography.
5. **Fail-Closed Validation Gate (Directive 22)**: Advancement to Stage R.6 strictly requires physical `validation_report.json` on disk with `overall_verdict == "PASS"` and `checks_failed == 0`.

