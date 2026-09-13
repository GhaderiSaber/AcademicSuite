# Python Environment & Deterministic CLI Command Reference

## 4. Python Environment & CLI Command Reference

### Irandoc Paraphrasing & Similarity Reduction:
```bash
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_کاهش_همانندجویی.docx"
```

### Intervention Protocol Compilation (Chapter 3 Table & Appendix Manual):
```bash
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به دردهای مزمن عضلانی-اسکلتی" \
  --output-docx "پروتکل_مداخله_اکت.docx" \
  --output-json "protocol_act.json"
```

### Defense Presentation Compilation (PowerPoint .pptx):
```bash
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy
```

### Journal Submission Collateral & Rebuttal Package Compilation:
```bash
# English Submission Package (ISI / Scopus Q1-Q4)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload.json" \
  --out-dir "./submission_package_en" \
  --lang en

# Persian Submission Package (علمی-پژوهشی / ISC)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload_fa.json" \
  --out-dir "./submission_package_fa" \
  --lang fa
```

### Systematic Review & Quantitative Meta-Analysis (PRISMA 2020 & Cochrane RoB 2):
```bash
# English Synthesis (Forest Plot, Funnel Plot, APA 7 Manuscript)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload.json" \
  --out-dir "./meta_analysis_output_en" \
  --lang en

# Persian Synthesis (علمی-پژوهشی / ISC)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload_fa.json" \
  --out-dir "./meta_analysis_output_fa" \
  --lang fa
```

### Monte Carlo Psychometric & Statistical Data Simulation (All Research Paradigms):
```bash
# 1. Instant Run via Research Presets (No JSON needed!)
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset hierarchical_regression --out-dir "./sim_reg"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset moderation_model1 --out-dir "./sim_mod"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset factorial_anova --out-dir "./sim_anova"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset mixed_split_plot --out-dir "./sim_rm"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset ancova_trial --out-dir "./sim_rct"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset logistic_diagnosis --out-dir "./sim_logistic"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset efa_battery --out-dir "./sim_efa"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset non_parametric_skewed --out-dir "./sim_np"

# 2. Custom Structural Equation Modeling (SEM) / CFA Mode
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_simulation_payload.json" \
  --out-dir "./simulated_sem_data" \
  --seed 42
```

### Qualitative Data Analysis & Chapter 4 Reporting (Thematic Analysis & Grounded Theory):
```bash
# Reflexive Thematic Analysis (Braun & Clarke 6-phase thematic network)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "thematic_payload.json" \
  --out-dir "./qualitative_output_thematic" \
  --lang fa

# Grounded Theory (Strauss & Corbin 6-dimension paradigmatic model)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "grounded_theory_payload.json" \
  --out-dir "./qualitative_output_gt" \
  --lang fa
```

### Chapter 2 Literature Review & Empirical Matrix Compilation:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json "ch2_payload.json" \
  --out-dir "./chapter2_output" \
  --lang fa
```

### Psychometric Scale Standardization & Validation:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "./psychometric_validation_output" \
  --lang fa
```

### Master Thesis Compilation:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "path/to/template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "Chapter1.docx" \
  --ch2 "Chapter2.docx" \
  --ch3 "Chapter3.docx" \
  --ch4 "Chapter4.docx" \
  --ch5 "Chapter5.docx" \
  --refs "References_Compiled.docx" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire"
```

### Questionnaire Lookup & Factor Scoring:
```bash
# Search Registry (Questionnaires.xlsx) & Google Drive Library
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"

# Inspect Scale Scoring Profile, Subscales, and Reverse Keys
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# Score Raw Survey Item Responses into Factors and Scale Composites
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### Run Automated Statistical Suite:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/data.xlsx" \
  --task auto \
  --config "path/to/config.json" \
  --out "stats_results.json"
```

### Run Specific Statistical Tasks:
- **Score Scale & Factors**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data_raw.xlsx --task score_scale --scale "Connor-Davidson Resilience Scale" --prefix "Q" --out-scored data_scored.xlsx`
- **Descriptives & Normality**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task descriptives --vars "Pre_Test,Post_Test,Resilience"`
- **Scale Reliability ($\alpha$)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task reliability --items "Q1,Q2,Q3,Q4,Q5"`
- **Intervention ANCOVA**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task ancova --dv Post_Test --group Group --covar Pre_Test`
- **Hierarchical Regression**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task regression --dv Outcome --step1 "Age,Gender" --step2 "Resilience,Self_Efficacy"`
- **Bootstrap Mediation (Model 4)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task mediation --x Stress --m Resilience --y Depression --bootstraps 2000`

### Generate APA 7 Persian Word Document:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

### End-to-End Academic Pipeline Orchestration:
```bash
# 1. Run turnkey pipeline preset (thesis_empirical, scale_validation, qualitative_study, meta_analysis, thesis_to_publication, bibliometric_pipeline)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project"

# 2. Run turnkey bibliometric preset (harvest -> bibliometrics -> historiography -> article -> submission)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --out-dir "./my_bibliometric_project" \
  --lang fa

# 3. Dry-run validation (inspect execution plan and dependency DAG without running)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --dry-run

# 4. Custom project configuration with custom step payloads
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --config "project_config.json" \
  --out-dir "./custom_academic_study"

# 5. Granular checkpointing & step control
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --resume-from statistics

python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --step discussion
```

### Thesis Integrity & Cross-Chapter Forensic Audit:
```bash
# Persian Audit (گزارش ممیزی رساله، همخوانی فرضیات و درجات آزادی، و تطبیق مراجع)
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --lang fa

# English / ISI Audit Mode
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results_en" \
  --lang en
```

### G*Power Sample Size & Statistical Power Calculation:
```bash
# 1. ANCOVA Sample Size Determination (Chapter 3 Methodology Text & Power Curve)
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test ancova \
  --groups 2 \
  --covariates 1 \
  --power 0.85 \
  --effect-size 0.25 \
  --out-dir "./sample_size_ancova" \
  --lang fa

# 2. Multiple Linear Regression Sample Size Determination
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test regression \
  --predictors 3 \
  --power 0.80 \
  --effect-size 0.15 \
  --out-dir "./sample_size_regression" \
  --lang fa

# 3. Comprehensive Multi-Design & SEM Power Analysis via JSON Payload
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --json "gpower_payload.json" \
  --out-dir "./gpower_results" \
  --lang fa
```

#### Run Academic Tone Polisher & Anti-AI Refiner (Skill #22):
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --json .agents/skills/ai-academic-tone-polisher/examples/sample_ai_text_payload.json \
  --sample persian_draft \
  --out-dir "./tone_results" \
  --lang fa
```

#### Run Literature Harvester & Empirical Metadata Extractor (Skill #23):
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "درمان مبتنی بر پذیرش و تعهد انعطاف‌پذیری روان‌شناختی فرسودگی شغلی" \
  --out-dir "./harvested_ch2" \
  --limit 10 \
  --lang fa
```

#### Run Bibliometric Science Mapping & Network Analyst (Skill #24):
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input .agents/skills/bibliometric-network-analyst/examples/sample_bibliometric_payload.json \
  --output-dir "./biblio_results" \
  --language fa \
  --min-freq 1 \
  --top-n 30
```

#### Run Citation Network Visualizer & Main Path Analysis (Skill #25):
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input .agents/skills/citation-network-visualizer/examples/sample_citation_network_payload.json \
  --output-dir "./historiography_results" \
  --language fa \
  --main-path global
```

#### Run Digital Twin Academic Consultant & Telegram Bot (Skill #26):
```bash
# 1. Analyze proposal and generate itemized quote in Tomans
python3 .agents/skills/digital-twin-academic-consultant/scripts/proposal_price_estimator.py \
  --input /path/to/proposal.docx \
  --telegram-card --admin

# 2. Ingest Telegram export to calibrate consulting FAQs
python3 .agents/skills/digital-twin-academic-consultant/scripts/telegram_chat_analyzer.py \
  --input /path/to/result.json --update-persona

# 3. Run MTProto userbot listener & Google Drive project manager
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --listen

# 4. List or sync managed projects in Google Drive
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --list-projects
```

#### Run Academic Drive Project Organizer (Skill #27):
```bash
# 1. Audit Pending Works and identify loose files & fragmented folders
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --audit -o .agents/skills/academic-drive-project-organizer/references

# 2. Cross-reference Duzen milestones and generate Master Catalog (.xlsx and .md)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --sync-duzen -o .agents/skills/academic-drive-project-organizer/references

# 3. Tidy a project folder into the 4-tier taxonomy (dry-run first, then apply)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --tidy --project "Client Name" --apply --clean-junk

# 4. Provision a new standard project folder
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --new-project "Client Name" --topic "Topic"
```

---

