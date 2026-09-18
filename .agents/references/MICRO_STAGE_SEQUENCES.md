# MICRO_STAGE_SEQUENCES.md — Thesis Pipeline Micro-Stage Reference Manual

This reference manual documents the complete, authoritative micro-stage breakdown, assigned subagents, deterministic execution scripts, and required physical triad artifacts (`.docx` + `.md` + `.json`) for each academic pipeline in the Academic Suite.

Per **Directive 3 (Artifact-Gated Stage Execution, Micro-Stage Granularity & Triad Artifact Invariant)** in [`AGENTS.md`](file:///AGENTS.md), jumping stages without physical checkpoint files existing on disk is strictly prohibited. Every individual micro-stage must produce its synchronized triad of deliverables prior to stage-gate advancement.

---

## 1. Chapter 4: Empirical Findings Pipeline (Stages 4.0 – 4.12)

| Stage | Name | Assigned Subagent | Official Script / Capability | Required Physical Triad Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 4.0** | Data Curation & Preprocessing | `data-curator` | `data_curation_pipeline.py` | `00_data_curation_report.json`, `00_data_curation_report.md`, `data_cleaned.xlsx` |
| **Stage 4.1** | Demographics Profiling | `statistics-agent` | `demographic_profiler.py` | `01_demographics.docx`, `01_demographics.md`, `01_demographics.json` |
| **Stage 4.2** | Descriptives & Reliability ($\alpha, \omega$) | `statistics-agent` | `scale_reliability_runner.py` | `02_descriptives_and_reliability.docx`, `02_descriptives_and_reliability.md`, `02_descriptives_and_reliability.json` |
| **Stage 4.3** | Parametric Assumptions Verification | `statistical-expert` | `assumption_tester.py` | `03_parametric_assumptions.docx`, `03_parametric_assumptions.md`, `03_parametric_assumptions.json` |
| **Stage 4.4** | Bivariate Correlation Matrix Analysis | `statistics-agent` | `correlation_matrix_builder.py` | `04_bivariate_correlations.docx`, `04_bivariate_correlations.md`, `04_bivariate_correlations.json` |
| **Stage 4.5** | Macro Model Fit / Primary Structural Model | `statistics-agent` | `sem_modeler.py` / `sem_lavaan_runner.R` | `05_macro_model.docx`, `05_macro_model.md`, `05_macro_model.json` |
| **Stage 4.6.1** | Hypothesis 1 Testing & Narrative Dissection | `statistics-agent` + `academic-writer` | Deterministic hypothesis runner | `06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json` |
| **Stage 4.6.2** | Hypothesis 2 Testing & Narrative Dissection | `statistics-agent` + `academic-writer` | Deterministic hypothesis runner | `07_hypothesis_2.docx`, `07_hypothesis_2.md`, `07_hypothesis_2.json` |
| **Stage 4.6.k** | Hypothesis $k$ Testing & Narrative Dissection | `statistics-agent` + `academic-writer` | Deterministic hypothesis runner | `XX_hypothesis_k.docx`, `XX_hypothesis_k.md`, `XX_hypothesis_k.json` |
| **Stage 4.7.1** | Indirect / Mediation Path 1 (Bootstrap 5,000) | `statistics-agent` | `bootstrap_mediation_runner.py` | `XX_mediation_1.docx`, `XX_mediation_1.md`, `XX_mediation_1.json` |
| **Stage 4.8** | Master Decision Matrix & Chapter Summary | `academic-writer` | `decision_matrix_generator.py` | `XX_chapter_summary.docx`, `XX_chapter_summary.md`, `XX_chapter_summary.json` |
| **Stage 4.9** | Statistical QC & MSAI Anomaly Audit | `statistical-auditor` | `msai_detector.py` | `XX_statistical_audit_report.json`, `XX_statistical_audit_report.md` |
| **Stage 4.10** | Results QC & APA 7 Typography Audit | `results-auditor` | `apa_typography_checker.py` | `XX_results_qc_checklist.json`, `XX_results_qc_checklist.md` |
| **Stage 4.11** | OpenXML & Markdown Chapter Assembly | `academic-writer` | `chapter_assembler.py` | `Chapter_4_Results.docx`, `Chapter_4_Results.md` |
| **Stage 4.12** | Committee Defense Viva Voce Simulation | `final-judge` | `viva_voce_simulator.py` | `XX_defense_brief.docx`, `XX_defense_brief.md`, `XX_defense_brief.json` |

---

## 2. Chapter 5: Discussion & Conclusion Pipeline (Stages 5.1 – 5.7)

| Stage | Name | Assigned Subagent | Focus / Methodology | Required Physical Triad Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 5.1** | Findings Overview & Purpose Recap | `academic-writer` | Restatement of research aim and high-level summary of validated models | `01_findings_recap.docx`, `01_findings_recap.md`, `01_findings_recap.json` |
| **Stage 5.2.1** | Hypothesis 1 Deep Discussion | `academic-writer` + `literature-expert` | Psychological mechanisms, epistemic interpretation, literature concordance/discordance | `02_hypothesis_1_discussion.docx`, `02_hypothesis_1_discussion.md`, `02_hypothesis_1_discussion.json` |
| **Stage 5.2.2** | Hypothesis 2 Deep Discussion | `academic-writer` + `literature-expert` | Psychological mechanisms, theoretical backing, Iranian & international alignment | `03_hypothesis_2_discussion.docx`, `03_hypothesis_2_discussion.md`, `03_hypothesis_2_discussion.json` |
| **Stage 5.2.k** | Hypothesis $k$ Deep Discussion | `academic-writer` + `literature-expert` | In-depth mechanism dissection for hypothesis $k$ | `XX_hypothesis_k_discussion.docx`, `XX_hypothesis_k_discussion.md`, `XX_hypothesis_k_discussion.json` |
| **Stage 5.3** | Unexpected / Non-Significant Findings Analysis | `academic-writer` + `methodology-expert` | Epistemic analysis of null results, statistical power caveats, suppressor effects | `XX_non_significant_findings.docx`, `XX_non_significant_findings.md`, `XX_non_significant_findings.json` |
| **Stage 5.4** | Theoretical, Clinical & Practical Implications | `academic-writer` | Actionable recommendations for clinical practice, educational policy, and theory | `XX_implications.docx`, `XX_implications.md`, `XX_implications.json` |
| **Stage 5.5** | Methodological, Sampling & Instrument Limitations | `methodology-expert` | Internal/external validity limits, cross-sectional constraints, self-report bias | `XX_limitations.docx`, `XX_limitations.md`, `XX_limitations.json` |
| **Stage 5.6** | Future Research & Actionable Recommendations | `academic-writer` | Methodological directions, prospective longitudinal designs, experimental follow-ups | `XX_recommendations.docx`, `XX_recommendations.md`, `XX_recommendations.json` |
| **Stage 5.7** | Chapter 5 Consolidation & Assembly | `academic-writer` | Institutional OpenXML consolidation with pristine Persian typography | `Chapter_5_Discussion.docx`, `Chapter_5_Discussion.md` |

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
