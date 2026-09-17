# Skill Inventory & Execution Tools Audit

**Document Version:** 1.0.0 (Phase 1 Audit)  
**Total Skills in Registry:** 37  
**Modern Production Skills:** 27  
**Legacy Migrated Workflow Shells:** 10  
**Total Executable Scripts in Skills:** 111  

---

## 1. Executive Summary

Skills in the Academic Suite ecosystem represent the **Deterministic Hands** and domain guidelines of the platform. Under **Directive 12.1**, skills are strictly deterministic CLI instruments or reference standards executed by Antigravity agents; they do not possess autonomous agency or manage agent lifecycles.

The registry currently contains 37 skills. An architectural split exists between:
1. **27 Modern Production Skills**: Contain full implementations with executable Python/R scripts, comprehensive reference documentation, and OpenXML compilers.
2. **10 Legacy Workflow Shells**: Empty skill shells migrated from `.agents/workflows/*.md.bak` containing zero scripts and zero reference files.

---

## 2. Directory of 27 Modern Production Skills

### 1. `academic-article-writer`
- **Path:** `.agents/skills/academic-article-writer/`
- **Description:** Draft, revise, and format APA 7th Edition academic journal articles, empirical manuscripts, and peer-review rebuttal packages in psychology and behavioral sciences.
- **Scripts (2):** `compile_academic_article.py`, `verify_and_download_citation.py`
- **References (2):** `apa7_manuscript_guidelines.md`, `rebuttal_letter_templates.md`
- **Primary Inputs:** Empirical thesis findings, target journal parameters.
- **Primary Deliverables:** `Blind_Manuscript.docx`, `Title_Page.docx`, `Response_to_Reviewers.docx`.

### 2. `academic-drive-project-organizer`
- **Path:** `.agents/skills/academic-drive-project-organizer/`
- **Description:** Organize academic research projects, Google Drive folders, datasets, drafts, and bibliographic libraries into standardized thesis directory structures.
- **Scripts (1):** `organize_drive_projects.py`
- **References (4):** Standard directory taxonomy and asset archiving guidelines.
- **Primary Inputs:** Messy workspace or Google Drive folder.
- **Primary Deliverables:** Standardized thesis project folder tree (`01_admin`, `02_proposal`, `03_data`, `04_analysis`, `05_chapters`, `06_defense`).

### 3. `academic-reference-extractor`
- **Path:** `.agents/skills/academic-reference-extractor/`
- **Description:** Extract in-text citations from academic text, match against bibliographies, resolve DOIs, and export clean EndNote (.enw), RIS (.ris), and APA text files.
- **Scripts (5):** `extract_section_references.py`, `generate_endnote_suite.py`, `local_paper_extractor.py`, `reconcile_post_humanization_citations.py`, `verify_references.py`
- **References (2):** `cwyw_openxml_spec.md`, `reference_parsing_rules.md`
- **Primary Inputs:** Academic `.docx` or `.md` manuscript.
- **Primary Deliverables:** In-text citation matrix, `library.enw`, `library.ris`, DOI audit report.

### 4. `academic-suite-orchestrator`
- **Path:** `.agents/skills/academic-suite-orchestrator/`
- **Description:** Deterministic batch pipeline CLI runner executing multi-stage script sequences and artifact handoffs on disk ("The Hands").
- **Scripts (1):** `orchestrator_cli.py`
- **References (1):** Pipeline sequence specifications.
- **Primary CLI Command:** `python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py --assemble-chapter Chapter_4_Results.docx`
- **Primary Deliverables:** Consolidated multi-stage `.docx` documents.

### 5. `ai-academic-tone-polisher`
- **Path:** `.agents/skills/ai-academic-tone-polisher/`
- **Description:** Polish Persian academic text, eliminate AI clichés and inflated prose, enforce scholarly sobriety, formal register, and proper typography (half-spaces).
- **Scripts (4):** `cadence_inverter.py`, `lint_ai_risk.py`, `mask_invariants.py`, `tone_polisher_engine.py`
- **References (4):** AI cliché blocklists, cadence variability targets ($CV \ge 0.50$), Iranian academic rhetoric styleguide.
- **Primary Inputs:** Draft Persian academic text.
- **Primary Deliverables:** Polished academic text with zero robotic cliches (*«شایان ذکر است که»*), verified half-spaces, natural sentence length distribution.

### 6. `bibliometric-network-analyst`
- **Path:** `.agents/skills/bibliometric-network-analyst/`
- **Description:** Science mapping, co-occurrence, co-citation, and co-authorship analysis. Computes Bradford/Lotka laws, Callon diagrams, and exports VOSviewer files and plots.
- **Scripts (1):** `bibliometric_engine.py`
- **References (1):** Science mapping and bibliometric interpretation manual.
- **Primary Inputs:** Scopus / WoS / PubMed `.csv` export.
- **Primary Deliverables:** Callon centrality-density diagram, VOSviewer map files, Bradford zones distribution.

### 7. `citation-network-visualizer`
- **Path:** `.agents/skills/citation-network-visualizer/`
- **Description:** Construct and visualize citation, co-citation, and bibliographic coupling networks. Computes network centralities and exports 300-DPI publication graphs.
- **Scripts (1):** `citation_visualizer_engine.py`
- **References (1):** Citation network visualization standards.
- **Primary Inputs:** Bibliographic corpus.
- **Primary Deliverables:** 300-DPI network graph, node centrality rankings (degree, betweenness).

### 8. `digital-twin-academic-consultant`
- **Path:** `.agents/skills/digital-twin-academic-consultant/`
- **Description:** Digital Twin consultant and Telegram assistant for Saber Ghaderi. Evaluates proposals, estimates pricing in Tomans, and answers methodology/statistical queries.
- **Scripts (21):** Client triage, pricing estimators, automated Telegram response dispatchers, project brief generators.
- **References (1):** Pricing matrices and consultancy negotiation guidelines.
- **Primary Inputs:** Client inquiry or research proposal.
- **Primary Deliverables:** Formal proposal evaluation, deterministic price quotation in Tomans, client brief.

### 9. `gpower-sample-size-calculator`
- **Path:** `.agents/skills/gpower-sample-size-calculator/`
- **Description:** A priori, post hoc, and sensitivity statistical power analysis (G*Power 3.1 & Cohen 1988) for t-tests, ANOVA, ANCOVA, regression, mediation, and SEM.
- **Scripts (1):** `gpower_cli.py`
- **References (1):** G*Power parameter setting tables and Cohen's effect size conventions.
- **Primary Inputs:** Target test family, $\alpha$, power ($1-\beta$), expected effect size ($f, d, f^2$).
- **Primary Deliverables:** Minimum required sample size calculation, power curve, APA 7 sample size justification paragraph.

### 10. `irandoc-plagiarism-reducer`
- **Path:** `.agents/skills/irandoc-plagiarism-reducer/`
- **Description:** Analyze and reduce Irandoc / SamimNoor similarity percentages in Persian academic text via structural paraphrasing, synonym substitution, and citation repairs.
- **Scripts (1):** `irandoc_engine.py`
- **References (1):** SamimNoor and Irandoc algorithm evasion and ethical paraphrasing guide.
- **Primary Inputs:** Irandoc similarity report and thesis draft.
- **Primary Deliverables:** Paraphrased sections with target similarity < 20%.

### 11. `journal-submission-assistant`
- **Path:** `.agents/skills/journal-submission-assistant/`
- **Description:** Match manuscripts to target WoS/Scopus/ISC journals, format title pages and cover letters, enforce author guidelines, and prepare submission packages.
- **Scripts (1):** `journal_matcher.py`
- **References (1):** Target journal index (psychology and behavioral sciences).
- **Primary Inputs:** Empirical paper abstract and keywords.
- **Primary Deliverables:** Top 5 recommended journals with impact factors, quartile (Q1–Q4), APC fees, acceptance turnaround times.

### 12. `literature-harvester`
- **Path:** `.agents/skills/literature-harvester/`
- **Description:** Automated literature harvesting across PubMed, CrossRef, Semantic Scholar, SID, and Magiran. Extracts sample sizes, designs, and scales for Chapter 2.
- **Scripts (2):** `crossref_harvester.py`, `pubmed_harvester.py`
- **References (1):** Query formulation guidelines for psychological constructs.
- **Primary Inputs:** Keywords, Boolean operators, publication date window (2021–2026).
- **Primary Deliverables:** Harvested papers JSON database, downloaded open-access PDFs, extracted parameter tables.

### 13. `persian-academic-translation`
- **Path:** `.agents/skills/persian-academic-translation/`
- **Description:** Academic translation of papers, chapters, and scales from English to Persian with domain terminology, APA standards, and strict Persian typography rules.
- **Scripts (1):** `translation_engine.py`
- **References (2):** English-Persian psychological terminology glossary, bilingual typography rules.
- **Primary Inputs:** English paper or psychometric instrument.
- **Primary Deliverables:** High-fidelity Persian academic translation with footnote glosses for specialized Latin terms.

### 14. `persian-defense-presentation-builder`
- **Path:** `.agents/skills/persian-defense-presentation-builder/`
- **Description:** Build 16:9 thesis and dissertation defense presentations (HTML, PPTX, Google Slides) with native SmartArt RTL, decoupled LTR stats, and dedicated hypothesis slides.
- **Scripts (48):** Comprehensive layout engine, chart renderers, OMML equation injectors, visual card generators, PPTX compilers, QA validators.
- **References (49):** Complete design system, slide composition rules, presentation schema, preset contracts.
- **Primary Inputs:** Chapter 4 and Chapter 5 dissertation findings.
- **Primary Deliverables:** Defense presentation `.pptx` and standalone interactive `.html` deck.

### 15. `persian-discussion-builder`
- **Path:** `.agents/skills/persian-discussion-builder/`
- **Description:** Draft Chapter 5 (Discussion and Conclusion) synthesizing statistical findings, psychological mechanisms, literature concordance, implications, and limitations.
- **Scripts (1):** `generate_chapter5_docx.py`
- **References (2):** `discussion_framework_guide.md`, `psychology_theoretical_mechanisms.md`
- **Primary Inputs:** Chapter 4 statistical findings, Chapter 2 theoretical framework.
- **Primary Deliverables:** Synchronized triad (`.docx`, `.md`, `.json`) for Chapter 5 micro-stages.

### 16. `persian-literature-review-builder`
- **Path:** `.agents/skills/persian-literature-review-builder/`
- **Description:** Synthesize Chapter 2 (Literature Review) with theoretical foundations, inverted-triangle narrative, empirical background tables, and APA 7 Persian citations.
- **Scripts (1):** `literature_review_engine.py`
- **References (1):** `chapter2_structure_and_writing_guide.md`
- **Primary Inputs:** Harvested bibliographic corpus.
- **Primary Deliverables:** Synchronized triad (`.docx`, `.md`, `.json`) for Chapter 2 sections.

### 17. `persian-proposal-builder`
- **Path:** `.agents/skills/persian-proposal-builder/`
- **Description:** Draft defense-ready research proposals (طرح تحقیق / پروپوزال) with inverted-triangle problem statements, directional hypotheses, G*Power sampling, and DOCX export.
- **Scripts (1):** `generate_proposal_docx.py`
- **References (1):** `proposal_structure_guide.md`
- **Primary Inputs:** Approved research topic, variable model.
- **Primary Deliverables:** Institutional research proposal `.docx` meeting Islamic Azad University / State University standards.

### 18. `persian-thesis-builder`
- **Path:** `.agents/skills/persian-thesis-builder/`
- **Description:** Assemble, synthesize, format, and compile full 5-chapter Persian graduate theses (رساله / پایان‌نامه) from modular research artifacts into institutional Word DOCX.
- **Scripts (1):** `compile_full_thesis.py`
- **References (2):** `apa_bilingual_reference_rules.md`, `thesis_structure_guide.md`
- **Primary Inputs:** Micro-stage artifacts from Chapters 1–5.
- **Primary Deliverables:** Complete, formatted master thesis `.docx` with bilingual preliminary pages, TOC, list of tables, and continuous pagination.

### 19. `persian-thesis-revision-assistant`
- **Path:** `.agents/skills/persian-thesis-revision-assistant/`
- **Description:** Triage and resolve supervisor and examiner defense comments, apply Word track changes, and compile formal Point-by-Point Response Tables (جدول پاسخ به داوران).
- **Scripts (3):** `extract_docx_comments.py`, `generate_revision_response_docx.py`, `revision_triage_engine.py`
- **References (2):** `academic_rebuttal_etiquette_fa.md`, `comment_resolution_checklist.md`
- **Primary Inputs:** Marked-up examiner `.docx` or committee minutes.
- **Primary Deliverables:** Point-by-point response table `.docx`, revised dissertation draft with tracked revisions.

### 20. `psychological-intervention-protocol-builder`
- **Path:** `.agents/skills/psychological-intervention-protocol-builder/`
- **Description:** Design standardized evidence-based psychological intervention manuals and Chapter 3 session tables (ACT, CBT, Schema, CFT, MBSR) with clinical worksheets in DOCX.
- **Scripts (2):** `compile_intervention_protocol.py`, `generate_consort_flowchart.py`
- **References (1):** `evidence_based_protocols_catalog.md`
- **Primary Inputs:** Intervention modality, target population, session count (typically 8–12 sessions).
- **Primary Deliverables:** Clinical intervention manual `.docx`, Chapter 3 session protocol table, CONSORT flowchart.

### 21. `psychometric-data-simulator`
- **Path:** `.agents/skills/psychometric-data-simulator/`
- **Description:** Monte Carlo psychometric data simulation for SEM, CFA, Likert scales, RCT pre-post repeated measures, ANCOVA, and correlated demographics. Exports SPSS XLSX/CSV.
- **Scripts (1):** `simdat_engine.py`
- **References (1):** `monte_carlo_sem_and_likert_simulation_guide.md`
- **Primary Inputs:** Target construct structure, correlation matrix, sample size, measurement scales.
- **Primary Deliverables:** Simulated discrete Likert dataset (`.xlsx`, `.csv`) with bounded decimal noise (Directive 9).

### 22. `psychometric-scale-resolver`
- **Path:** `.agents/skills/psychometric-scale-resolver/`
- **Description:** Search, extract, reverse-code, and compute subscale and composite scores from 4,880 validated psychological questionnaires in Questionnaires.xlsx and Drive library.
- **Scripts (1):** `questionnaire_resolver.py`
- **References (1):** `questionnaire_scoring_and_factor_guide.md`
- **Primary Inputs:** Questionnaire name or abbreviation.
- **Primary Deliverables:** Item scoring keys, reverse-coded item indices, subscale aggregation formulas, Cronbach's alpha benchmarks.

### 23. `psychometric-scale-validator`
- **Path:** `.agents/skills/psychometric-scale-validator/`
- **Description:** Comprehensive scale validation and psychometrics: CVR/CVI, EFA, CFA, convergent/discriminant validity, Omega/Alpha, IRT Graded Response Model, and ROC curves.
- **Scripts (1):** `psychometric_validator_engine.py`
- **References (1):** `psychometric_standards_and_validation_guide.md`
- **Primary Inputs:** Item-level dataset.
- **Primary Deliverables:** CVR/CVI expert panel table, EFA/CFA factor loadings, convergent validity (AVE, CR), discriminant validity (Fornell-Larcker & HTMT), McDonald's $\omega$.

### 24. `qualitative-data-analyst`
- **Path:** `.agents/skills/qualitative-data-analyst/`
- **Description:** Execute Braun & Clarke Reflexive Thematic Analysis and Strauss & Corbin Grounded Theory. Computes inter-coder reliability, theme hierarchies, and DOCX reports.
- **Scripts (1):** `qualitative_engine.py`
- **References (1):** `qualitative_methodology_and_coding_guide.md`
- **Primary Inputs:** Interview transcripts (.txt, .docx).
- **Primary Deliverables:** Open coding book, axial coding paradigm model, theme frequency table, Holsti / Cohen's $\kappa$ agreement index.

### 25. `statistical-data-analyst`
- **Path:** `.agents/skills/statistical-data-analyst/`
- **Description:** Execute hypothesis tests (ANCOVA, Repeated Measures, regression, bootstrap mediation), verify parametric assumptions, and generate APA 7 Chapter 4 reports in DOCX.
- **Scripts (6):** `chapter4_table_scaffolder.py`, `data_curator_engine.py`, `data_harnessing_engine.R`, `generate_apa_docx.py`, `psychology_stats.py`, `visualize_stats.py`
- **References (2):** `apa7_psychology_reporting_guide.md`, `statistical_decision_tree.md`
- **Primary CLI Command:** `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data <file> --spec <spec.json>`
- **Primary Deliverables:** `stats_results.json`, formatted APA 7 3-line tables in `.docx`.

### 26. `systematic-review-meta-analyst`
- **Path:** `.agents/skills/systematic-review-meta-analyst/`
- **Description:** PRISMA 2020 systematic reviews and meta-analysis: PICO search, Cochrane RoB 2, Hedges' g pooling, heterogeneity, publication bias, and Forest/Funnel plot generation.
- **Scripts (2):** `generate_prisma_flowchart.py`, `meta_analysis_engine.py`
- **References (1):** `prisma_2020_and_rob2_guide.md`
- **Primary Inputs:** Extracted study effect sizes and sample sizes.
- **Primary Deliverables:** PRISMA 2020 flowchart, Cochrane RoB 2 traffic light plot, Forest plot, Funnel plot with Egger's test, pooled effect size table.

### 27. `thesis-integrity-auditor`
- **Path:** `.agents/skills/thesis-integrity-auditor/`
- **Description:** Forensic cross-chapter consistency audit (Ch 1 vs Ch 4 vs Ch 5), hypothesis-result alignment, df verification, citation-reference reconciliation, and APA 7 QC.
- **Scripts (1):** `audit_engine.py`
- **References (1):** `thesis_audit_criteria_and_rules.md`
- **Primary Inputs:** Draft thesis document (.docx) or individual chapter artifacts.
- **Primary Deliverables:** Forensic cross-chapter alignment matrix, degrees of freedom check report, statistical discrepancy flags.

---

## 3. Directory of 10 Legacy Migrated Workflow Shells

The following 10 skills were migrated into `.agents/skills/` from legacy `.agents/workflows/*.md.bak` files. None contain dedicated executable scripts or reference assets; each consists solely of a legacy orchestration `SKILL.md`:

| Legacy Skill Name | Path | Scripts | Refs | Modern Functional Replacement |
|---|---|---|---|---|
| `chapter2_literature` | `.agents/skills/chapter2_literature/` | 0 | 0 | `persian-literature-review-builder` + `literature-harvester` |
| `chapter4` | `.agents/skills/chapter4/` | 0 | 0 | `statistical-data-analyst` + `academic-suite-orchestrator` |
| `chapter5` | `.agents/skills/chapter5/` | 0 | 0 | `persian-discussion-builder` |
| `defense_presentation` | `.agents/skills/defense_presentation/` | 0 | 0 | `persian-defense-presentation-builder` |
| `intervention_protocol` | `.agents/skills/intervention_protocol/` | 0 | 0 | `psychological-intervention-protocol-builder` |
| `journal_submission` | `.agents/skills/journal_submission/` | 0 | 0 | `journal-submission-assistant` + `academic-article-writer` |
| `proposal` | `.agents/skills/proposal/` | 0 | 0 | `persian-proposal-builder` + `gpower-sample-size-calculator` |
| `scale_validation` | `.agents/skills/scale_validation/` | 0 | 0 | `psychometric-scale-validator` + `psychometric-scale-resolver` |
| `thesis_assembly` | `.agents/skills/thesis_assembly/` | 0 | 0 | `persian-thesis-builder` |
| `thesis_revision` | `.agents/skills/thesis_revision/` | 0 | 0 | `persian-thesis-revision-assistant` |

---

## 4. Analysis Code & Script Distribution

The 111 executable scripts distributed across modern skills fulfill specific mathematical and OpenXML compilation functions:

- **Statistical Analysis & Inference (Python/R):** 7 scripts (`psychology_stats.py`, `data_harnessing_engine.R`, `data_curator_engine.py`, `meta_analysis_engine.py`, `psychometric_validator_engine.py`, `simdat_engine.py`, `qualitative_engine.py`).
- **Data Harvesting & Resolution:** 5 scripts (`crossref_harvester.py`, `pubmed_harvester.py`, `questionnaire_resolver.py`, `local_paper_extractor.py`, `extract_section_references.py`).
- **OpenXML Word & PPTX Compilers:** 55 scripts (`openxml_artifact_engine.py`, `compile_full_thesis.py`, `generate_apa_docx.py`, `generate_chapter5_docx.py`, `compile_intervention_protocol.py`, and 48 presentation builder scripts).
- **Text Polishing & Plagiarism Auditing:** 5 scripts (`tone_polisher_engine.py`, `cadence_inverter.py`, `lint_ai_risk.py`, `mask_invariants.py`, `irandoc_engine.py`).
- **Audit & Triage Tools:** 5 scripts (`audit_engine.py`, `revision_triage_engine.py`, `extract_docx_comments.py`, `verify_references.py`, `reconcile_post_humanization_citations.py`).
- **Consultancy & Telegram Suite:** 21 scripts in `digital-twin-academic-consultant`.
