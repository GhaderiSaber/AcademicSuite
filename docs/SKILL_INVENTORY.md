# Skill Inventory & Execution Tools Audit

**Document Version:** 3.0.0 (Phase 16 Migration Complete)  
**Total Active Production Skills:** 43 (in `.agents/skills/`)  
**Retired Workflow Shells:** 10 (Archived in `legacy/skills/`)  
**All Skills Verified:** Fully packaged with `scripts/`, `resources/`, `examples/`, `schemas/`, and `SKILL.md` satisfying Directive 18 ceilings (<= 500 lines, <= 40 KB).  

---

## 1. Executive Summary

Skills in the Academic Suite ecosystem represent the **Deterministic Hands** and domain guidelines of the platform. Under **Directive 12.1**, skills are strictly deterministic CLI instruments or reference standards executed by Antigravity agents; they do not possess autonomous agency or manage agent lifecycles.

The skills layer consists of **43 Focused Capability Packages** adhering to progressive disclosure standards. Every single skill contains:

- `SKILL.md` (bounded, single capability, strictly under 500 lines / 40 KB)
- `scripts/` (deterministic CLI execution tools)
- `resources/` (formal cutoffs, benchmark tables, and decision rules)
- `examples/` (canonical sample_input.json and sample_output.json)
- `schemas/` (JSON schemas for input specifications and output artifacts)

---

## 2. Directory of 43 Active Production Skills

### 1. `academic-article-writer`
- **Path:** `.agents/skills/academic-article-writer/`
- **Description:** Draft, revise, and format APA 7th Edition academic journal articles,
- **Scripts (2):** `compile_academic_article.py`, `verify_and_download_citation.py`
- **Resources (1):** `academic_article_writer_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 2. `academic-drive-project-organizer`
- **Path:** `.agents/skills/academic-drive-project-organizer/`
- **Description:** Organize academic research projects, Google Drive folders, datasets,
- **Scripts (1):** `organize_drive_projects.py`
- **Resources (1):** `academic_drive_project_organizer_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 3. `academic-reference-extractor`
- **Path:** `.agents/skills/academic-reference-extractor/`
- **Description:** Extract in-text citations from academic text, match against bibliographies,
- **Scripts (5):** `extract_section_references.py`, `generate_endnote_suite.py`, `local_paper_extractor.py`, `reconcile_post_humanization_citations.py`, `verify_references.py`
- **Resources (1):** `academic_reference_extractor_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 4. `academic-suite-orchestrator`
- **Path:** `.agents/skills/academic-suite-orchestrator/`
- **Description:** Deterministic batch pipeline CLI runner executing multi-stage script
- **Scripts (1):** `orchestrator_cli.py`
- **Resources (1):** `academic_suite_orchestrator_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 5. `ai-academic-tone-polisher`
- **Path:** `.agents/skills/ai-academic-tone-polisher/`
- **Description:** Polish Persian academic text, eliminate AI clichés and inflated prose,
- **Scripts (4):** `cadence_inverter.py`, `lint_ai_risk.py`, `mask_invariants.py`, `tone_polisher_engine.py`
- **Resources (1):** `ai_academic_tone_polisher_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 6. `apa-reporting`
- **Path:** `.agents/skills/apa-reporting/`
- **Description:** Generate strictly formatted APA 7th Edition 3-line tables, enforce statistical symbol italicization, Persian leading zero standard (۰.۰۰۱), and OpenXML LTR numeric decoupling.
- **Scripts (1):** `scaffold_apa_tables.py`
- **Resources (1):** `apa7_typography_and_border_specs.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 7. `assumption-testing`
- **Path:** `.agents/skills/assumption-testing/`
- **Description:** Verify parametric assumptions: Shapiro-Wilk normality, Levene's test for equality of variance, regression slope homogeneity, Mauchly's sphericity, and collinearity VIF/Tolerance.
- **Scripts (1):** `verify_assumptions.py`
- **Resources (1):** `parametric_decision_tree.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 8. `bibliometric-network-analyst`
- **Path:** `.agents/skills/bibliometric-network-analyst/`
- **Description:** Science mapping, co-occurrence, co-citation, and co-authorship analysis.
- **Scripts (1):** `bibliometric_engine.py`
- **Resources (1):** `bibliometric_network_analyst_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 9. `cfa`
- **Path:** `.agents/skills/cfa/`
- **Description:** Execute Confirmatory Factor Analysis (CFA), factor loadings (lambda), construct reliability (CR/omega), convergent validity (AVE), and model fit.
- **Scripts (2):** `run_cfa.R`, `run_cfa.py`
- **Resources (1):** `cfa_cutoffs_and_validity_rules.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 10. `chapter-4-writing`
- **Path:** `.agents/skills/chapter-4-writing/`
- **Description:** End-to-end orchestration for Chapter 4 findings, enforcing One-Hypothesis-One-Stage micro-stages, Triad Artifact Invariant (.docx, .md, .json), and Master Decision Matrix.
- **Scripts (1):** `scaffold_chapter4_triad.py`
- **Resources (1):** `chapter4_micro_stage_master_sequence.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 11. `citation-network-visualizer`
- **Path:** `.agents/skills/citation-network-visualizer/`
- **Description:** Construct and visualize citation, co-citation, and bibliographic coupling
- **Scripts (1):** `citation_visualizer_engine.py`
- **Resources (1):** `citation_network_visualizer_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 12. `data-audit`
- **Path:** `.agents/skills/data-audit/`
- **Description:** Audit raw dataset quality, screen unengaged responses (straight-lining), diagnose missingness patterns (Little's MCAR), and detect multivariate outliers (Mahalanobis D2).
- **Scripts (1):** `audit_dataset.py`
- **Resources (1):** `missingness_and_outliers_guide.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 13. `data-cleaning`
- **Path:** `.agents/skills/data-cleaning/`
- **Description:** Reverse-code items from 4,880 validated questionnaires, aggregate subscale and composite scores, handle imputations, and export analysis-ready datasets.
- **Scripts (1):** `clean_and_score.py`
- **Resources (1):** `scoring_and_reverse_coding_rules.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 14. `descriptive-statistics`
- **Path:** `.agents/skills/descriptive-statistics/`
- **Description:** Calculate univariate sample descriptive parameters (N, Mean, SD, Min, Max, Skewness, Kurtosis, SE) and demographic frequency distributions.
- **Scripts (1):** `compute_descriptives.py`
- **Resources (1):** `normality_and_descriptives_cutoffs.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 15. `digital-twin-academic-consultant`
- **Path:** `.agents/skills/digital-twin-academic-consultant/`
- **Description:** Digital Twin consultant and Telegram assistant for Saber Ghaderi. Evaluates
- **Scripts (23):** `academic_inquiry_classifier.py`, `backfill_topics_digest.py`, `bot_config.example.json`, `copilot_bridge.py`, `deliverable_dispatcher.py`, `financial_ledger.py`, `group_topics.py`, `manage_service.sh`, `math_formatter.py`, `milestone_tracker.py`, `morning_briefing.py`, `project_drive_manager.py`, `proposal_price_estimator.py`, `saber_second_userbot.session`, `saber_second_userbot.session-journal`, `saber_userbot.session`, `telegram_bot_daemon.py`, `telegram_chat_analyzer.py`, `telethon_config.example.json`, `telethon_config.json`, `telethon_userbot.py`, `vip_clients.example.json`, `voice_transcriber.py`
- **Resources (1):** `digital_twin_academic_consultant_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 16. `gpower-sample-size-calculator`
- **Path:** `.agents/skills/gpower-sample-size-calculator/`
- **Description:** A priori, post hoc, and sensitivity statistical power analysis (G*Power
- **Scripts (1):** `gpower_engine.py`
- **Resources (1):** `gpower_sample_size_calculator_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 17. `irandoc-plagiarism-reducer`
- **Path:** `.agents/skills/irandoc-plagiarism-reducer/`
- **Description:** Analyze and reduce Irandoc / SamimNoor similarity percentages in Persian
- **Scripts (1):** `paraphrase_engine.py`
- **Resources (1):** `irandoc_plagiarism_reducer_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 18. `journal-submission-assistant`
- **Path:** `.agents/skills/journal-submission-assistant/`
- **Description:** Match manuscripts to target WoS/Scopus/ISC journals, format title pages
- **Scripts (1):** `compile_submission_package.py`
- **Resources (1):** `journal_submission_assistant_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 19. `literature-harvester`
- **Path:** `.agents/skills/literature-harvester/`
- **Description:** Automated literature harvesting across PubMed, CrossRef, Semantic Scholar,
- **Scripts (2):** `harvester_engine.py`, `paper_downloader.py`
- **Resources (1):** `offline_benchmark_corpus.json`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 20. `literature-review`
- **Path:** `.agents/skills/literature-review/`
- **Description:** Multi-database query formulation (PubMed, CrossRef, SID), empirical parameter extraction, and inverted-triangle Chapter 2 review structuring.
- **Scripts (1):** `harvest_and_synthesize.py`
- **Resources (1):** `inverted_triangle_literature_framework.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 21. `longitudinal-moderated-mediation`
- **Path:** `.agents/skills/longitudinal-moderated-mediation/`
- **Description:** >-
- **Scripts (1):** `run_longitudinal_modmed.py`
- **Resources (1):** `longitudinal_moderated_mediation_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 22. `mediation`
- **Path:** `.agents/skills/mediation/`
- **Description:** Execute Preacher & Hayes bootstrap mediation (PROCESS Model 4) with 5,000 resamples, generating 95% BCa confidence intervals for indirect effects.
- **Scripts (2):** `run_mediation.R`, `run_mediation.py`
- **Resources (1):** `bootstrap_mediation_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 23. `methodology-review`
- **Path:** `.agents/skills/methodology-review/`
- **Description:** Audit research design validity, internal/external validity safeguards, statistical power (G*Power), and Chapter 3 methodology scaffolding.
- **Scripts (1):** `audit_methodology.py`
- **Resources (1):** `experimental_validity_checklists.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 24. `moderation`
- **Path:** `.agents/skills/moderation/`
- **Description:** Execute moderation interaction analysis (PROCESS Model 1), mean-centering predictors, simple slopes (-1 SD, Mean, +1 SD), and Johnson-Neyman regions.
- **Scripts (1):** `run_moderation.py`
- **Resources (1):** `moderation_simple_slopes_guide.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 25. `network-analysis`
- **Path:** `.agents/skills/network-analysis/`
- **Description:** Construct and analyze bibliometric, keyword co-occurrence, and citation networks, computing Callon centrality-density coordinates and VOSviewer exports.
- **Scripts (1):** `run_network_analysis.py`
- **Resources (1):** `callon_and_bibliometric_manual.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 26. `persian-academic-translation`
- **Path:** `.agents/skills/persian-academic-translation/`
- **Description:** Academic translation of papers, chapters, and scales from English to
- **Scripts (1):** `create_persian_docx.py`
- **Resources (1):** `persian_academic_translation_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 27. `persian-defense-presentation-builder`
- **Path:** `.agents/skills/persian-defense-presentation-builder/`
- **Description:** Build 16:9 thesis and dissertation defense presentations (HTML, PPTX,
- **Scripts (48):** `academic_brief_adapter.py`, `ai_advised_eval.py`, `batch_theme_extractor.py`, `browser_geometry_qa.py`, `chart_renderer.py`, `check_overlaps.py`, `check_style_fidelity.py`, `compare-skill-eval-baseline.py`, `compare_demo_parity.py`, `compare_eval_reports.py`, `compile_defense_presentation.py`, `content_planner.py`, `eval-quality.py`, `export_smoke.py`, `extract_template.py`, `generate.py`, `generate_gemini_slides_brief.py`, `generate_preset_eval_matrix.py`, `generate_theme_visual_cards.py`, `generation_eval.py`, `inject_omml.py`, `layout_engine.py`, `low_context.py`, `pptx_export_smoke.py`, `presentation_schema.py`, `preset_capabilities.py`, `preset_contracts.py`, `preset_profile_renderer.py`, `preset_profile_specs.py`, `preset_release_gate.py`, `preset_runtime_qa.py`, `preset_supervisor_sidebar.py`, `preset_support.py`, `promotion_gate.py`, `qa_validator.py`, `quality_eval.py`, `render-from-brief.py`, `render_diagrams.py`, `render_preview.py`, `rtl_typography.py`, `run-skill-evals.py`, `run_evals.py`, `screenshot-demos.py`, `style_signature_eval.py`, `title_browser_qa.py`, `title_profiles.py`, `validate-brief.py`, `validate_html.py`
- **Resources (1):** `persian_defense_presentation_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 28. `persian-discussion-builder`
- **Path:** `.agents/skills/persian-discussion-builder/`
- **Description:** Draft Chapter 5 (Discussion and Conclusion) synthesizing statistical
- **Scripts (1):** `generate_chapter5_docx.py`
- **Resources (1):** `persian_discussion_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 29. `persian-literature-review-builder`
- **Path:** `.agents/skills/persian-literature-review-builder/`
- **Description:** Synthesize Chapter 2 (Literature Review) with theoretical foundations,
- **Scripts (1):** `literature_review_engine.py`
- **Resources (1):** `persian_literature_review_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 30. `persian-proposal-builder`
- **Path:** `.agents/skills/persian-proposal-builder/`
- **Description:** Draft defense-ready research proposals (طرح تحقیق / پروپوزال) with inverted-triangle
- **Scripts (1):** `generate_proposal_docx.py`
- **Resources (1):** `persian_proposal_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 31. `persian-thesis-builder`
- **Path:** `.agents/skills/persian-thesis-builder/`
- **Description:** Assemble, synthesize, format, and compile full 5-chapter Persian graduate
- **Scripts (1):** `compile_full_thesis.py`
- **Resources (1):** `persian_thesis_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 32. `persian-thesis-revision-assistant`
- **Path:** `.agents/skills/persian-thesis-revision-assistant/`
- **Description:** Triage and resolve supervisor and examiner defense comments, apply Word
- **Scripts (3):** `extract_docx_comments.py`, `generate_revision_response_docx.py`, `revision_triage_engine.py`
- **Resources (1):** `persian_thesis_revision_assistant_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 33. `psychological-intervention-protocol-builder`
- **Path:** `.agents/skills/psychological-intervention-protocol-builder/`
- **Description:** Design standardized evidence-based psychological intervention manuals
- **Scripts (2):** `compile_intervention_protocol.py`, `generate_consort_flowchart.py`
- **Resources (1):** `psychological_intervention_protocol_builder_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 34. `psychometric-data-simulator`
- **Path:** `.agents/skills/psychometric-data-simulator/`
- **Description:** Monte Carlo psychometric data simulation for SEM, CFA, Likert scales,
- **Scripts (1):** `simdat_engine.py`
- **Resources (1):** `psychometric_data_simulator_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 35. `psychometric-scale-resolver`
- **Path:** `.agents/skills/psychometric-scale-resolver/`
- **Description:** Search, extract, reverse-code, and compute subscale and composite scores
- **Scripts (1):** `questionnaire_resolver.py`
- **Resources (1):** `psychometric_scale_resolver_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 36. `psychometric-scale-validator`
- **Path:** `.agents/skills/psychometric-scale-validator/`
- **Description:** Comprehensive scale validation and psychometrics: CVR/CVI, EFA, CFA,
- **Scripts (1):** `psychometric_validator_engine.py`
- **Resources (1):** `psychometric_scale_validator_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 37. `qualitative-data-analyst`
- **Path:** `.agents/skills/qualitative-data-analyst/`
- **Description:** Execute Braun & Clarke Reflexive Thematic Analysis and Strauss & Corbin
- **Scripts (1):** `qualitative_engine.py`
- **Resources (1):** `qualitative_data_analyst_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 38. `regression`
- **Path:** `.agents/skills/regression/`
- **Description:** Execute standard, hierarchical, and stepwise multiple regression modeling, evaluating R2, delta R2, F-change, standardized beta, and collinearity diagnostics.
- **Scripts (1):** `run_regression.py`
- **Resources (1):** `regression_reporting_rules.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 39. `reliability-analysis`
- **Path:** `.agents/skills/reliability-analysis/`
- **Description:** Calculate scale internal consistency reliability including Cronbach's alpha, McDonald's omega, item-total correlations, and alpha-if-item-deleted.
- **Scripts (1):** `compute_reliability.py`
- **Resources (1):** `reliability_benchmarks_and_formulas.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 40. `sem`
- **Path:** `.agents/skills/sem/`
- **Description:** Execute Structural Equation Modeling (SEM), evaluating latent structural paths and 11 Goodness-of-Fit indices against Hu & Bentler (1999) cutoffs.
- **Scripts (2):** `run_sem.R`, `run_sem.py`
- **Resources (1):** `hu_bentler_1999_fit_indices_guide.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 41. `statistical-data-analyst`
- **Path:** `.agents/skills/statistical-data-analyst/`
- **Description:** Execute hypothesis tests (ANCOVA, Repeated Measures, regression, bootstrap
- **Scripts (6):** `chapter4_table_scaffolder.py`, `data_curator_engine.py`, `data_harnessing_engine.R`, `generate_apa_docx.py`, `psychology_stats.py`, `visualize_stats.py`
- **Resources (1):** `statistical_data_analyst_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 42. `systematic-review-meta-analyst`
- **Path:** `.agents/skills/systematic-review-meta-analyst/`
- **Description:** PRISMA 2020 systematic reviews and meta-analysis: PICO search, Cochrane
- **Scripts (2):** `generate_prisma_flowchart.py`, `meta_analysis_engine.py`
- **Resources (1):** `systematic_review_meta_analyst_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

### 43. `thesis-integrity-auditor`
- **Path:** `.agents/skills/thesis-integrity-auditor/`
- **Description:** Forensic cross-chapter consistency audit (Ch 1 vs Ch 4 vs Ch 5), hypothesis-result
- **Scripts (1):** `audit_engine.py`
- **Resources (1):** `thesis_integrity_auditor_guidelines.md`
- **Examples & Schemas:** `examples/sample_input.json`, `examples/sample_output.json`, `schemas/input_schema.json`, `schemas/output_schema.json`

---

## 3. Directory of 10 Retired Legacy Workflow Shells (Archived in `legacy/skills/`)

The following 10 legacy workflow-converted shells were retired from `.agents/skills/` under Phase 16. All agent frontmatters and behavioral contracts have been re-bound to active production skills:

| Retired Legacy Skill | Historical Path | Modern Canonical Replacement |
| :--- | :--- | :--- |
| `chapter2_literature` | `legacy/skills/chapter2_literature/` | `persian-literature-review-builder` + `literature-harvester` |
| `chapter4` | `legacy/skills/chapter4/` | `chapter-4-writing` + `statistical-data-analyst` |
| `chapter5` | `legacy/skills/chapter5/` | `persian-discussion-builder` |
| `defense_presentation` | `legacy/skills/defense_presentation/` | `persian-defense-presentation-builder` (48 scripts, DrawingML, RTL SmartArt) |
| `intervention_protocol` | `legacy/skills/intervention_protocol/` | `psychological-intervention-protocol-builder` |
| `journal_submission` | `legacy/skills/journal_submission/` | `journal-submission-assistant` + `academic-article-writer` |
| `proposal` | `legacy/skills/proposal/` | `persian-proposal-builder` + `gpower-sample-size-calculator` |
| `scale_validation` | `legacy/skills/scale_validation/` | `psychometric-scale-validator` + `psychometric-scale-resolver` |
| `thesis_assembly` | `legacy/skills/thesis_assembly/` | `persian-thesis-builder` |
| `thesis_revision` | `legacy/skills/thesis_revision/` | `persian-thesis-revision-assistant` |

---

## 4. Script Distribution & Architectural Roles

Across the 43 active production skills, 133 deterministic scripts are maintained:
- **Statistical Inference & Modeling:** `psychology_stats.py`, `run_regression.py`, `run_mediation.py`, `run_moderation.py`, `run_cfa.py`, `run_sem.py`, `compute_descriptives.py`, `compute_reliability.py`, `test_assumptions.py`, `simdat_engine.py`.
- **Psychometric Validation & Scale Scoring:** `psychometric_validator_engine.py`, `questionnaire_resolver.py`, `extract_section_references.py`.
- **OpenXML Academic Document Compilers:** `openxml_artifact_engine.py`, `generate_apa_docx.py`, `compile_full_thesis.py`, `compile_academic_article.py`, and 48 presentation builder scripts.
- **Academic Tone, Plagiarism & Verification:** `tone_polisher_engine.py`, `cadence_inverter.py`, `lint_ai_risk.py`, `irandoc_engine.py`, `audit_engine.py`.
- **Consultancy & Telegram Suite:** 26 scripts in `digital-twin-academic-consultant`.
