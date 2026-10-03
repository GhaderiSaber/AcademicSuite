# Academic Orchestrator Contractual Delegation Envelope (CDE) & Pipeline Specification

## 1. Context & Architectural Mandate

Under **Directive 11 (Interactive Stage-Gate Protocol)**, **Directive 12 (Hybrid Multi-Agent Deliberation Architecture)**, **Directive 18 (Skill Modularity Standard)**, **Directive 19 (The Six-Part Functional Separation Invariant)**, and **Directive 20 (The Orchestrator Architectural Invariants)**, the `academic-orchestrator` is strictly a managerial conductor and meta-cognitive coordinator. 

To eliminate context drift, prevent hallucinated arguments, and guarantee reproducibility:
1. **The Orchestrator MUST NEVER dispatch informal or conversational prompts to worker agents.**
2. **Every delegation (`invoke_subagent`) must contain a structured, parseable Contractual Delegation Envelope (CDE) JSON block.**
3. **Every worker execution must be bounded by explicit disk inputs and explicit required artifacts on disk.**

---

## 2. Standard CDE Schema & Field Definitions

```json
{
  "task_id": "TSK-<YYYYMMDD>-<PIPELINE>-<SLUG>-<NNN>",
  "stage": "<Pipeline Name / Micro-stage Identifier>",
  "worker_agent": "<Target Specialist Agent Name>",
  "suite_repo": "$SUITE_REPO_DIR",
  "project_workspace": "$ACTIVE_PROJECT_DIR",
  "objective": "<Atomic, unambiguous objective statement describing the exact work to perform>",
  "target_script": "<Deterministic CLI command or tool to execute>",
  "inputs": [
    "<Explicit relative path to input file 1>",
    "<Explicit relative path to input file 2>"
  ],
  "required_artifacts": [
    "<Explicit relative path to output file 1>",
    "<Explicit relative path to output file 2>"
  ],
  "acceptance_criteria": [
    "<Criterion 1: Concrete numerical, formatting, or structural assertion>",
    "<Criterion 2: Validation threshold or boundary condition>"
  ],
  "constraints": [
    "Directive 0 (Binary Honesty Protocol)",
    "Directive 2 (Deterministic Calculations via CLI)",
    "Directive 4 (APA 7th Edition Typography)",
    "Directive 6 (English ASCII Filenames)",
    "Directive 25 (Universal Anti-Shortcut, Zero-Fastpath Invariant)",
    "Universal Path Portability Mandate (resolve all paths relative to $ACTIVE_PROJECT_DIR or $SUITE_REPO_DIR)"
  ]
}
```

### Field Definitions:
- **`task_id`** *(string, required)*: Deterministic task tracking token.
- **`stage`** *(string, required)*: Identifies the active stage in the stage machine.
- **`worker_agent`** *(string, required)*: Subagent name conforming to `.agents/agents/` registry.
- **`suite_repo`** *(string, required)*: Suite repository anchor.
- **`project_workspace`** *(string, required)*: Active research project workspace anchor.
- **`objective`** *(string, required)*: Concrete operational task goal.
- **`target_script`** *(string, required)*: CLI tool or script invocation.
- **`inputs`** *(list[string], required)*: Non-empty prerequisite file paths on disk.
- **`required_artifacts`** *(list[string], required)*: Exact deliverables that must exist upon task completion.
- **`acceptance_criteria`** *(list[string], required)*: Unambiguous verification assertions evaluated by `validation-agent`.
- **`constraints`** *(list[string], required)*: Constitutional invariants and boundary rules governing execution.

---

## 3. Canonical CDE Exemplars

### Exemplar 1: Empirical Hypothesis Testing (Multiple Regression)
```json
{
  "task_id": "TSK-2026-CH4-H1",
  "stage": "Stage 4.6 (Hypothesis 1: Multiple Regression)",
  "worker_agent": "statistics-agent",
  "suite_repo": "$SUITE_REPO_DIR",
  "project_workspace": "$ACTIVE_PROJECT_DIR",
  "objective": "Execute linear regression modeling predicting burnout from stress",
  "target_script": "python3 $SUITE_REPO_DIR/.agents/skills/regression/scripts/run_regression.py --data 02_analysis_code/cleaned_data.xlsx --dv burnout --iv stress",
  "inputs": [
    "02_analysis_code/cleaned_data.xlsx"
  ],
  "required_artifacts": [
    "03_deliverables/06_hypothesis_1.docx",
    "03_deliverables/06_hypothesis_1.md",
    "03_deliverables/06_hypothesis_1.json"
  ],
  "acceptance_criteria": [
    "Verify regression assumptions (VIF < 5.0, Durbin-Watson between 1.5 and 2.5)",
    "Report R2, F, unstandardized B (with SE), and standardized Beta",
    "Preserve Persian leading zeros (۰.۰۰۱, ۰.۰۵) and report p < .001 instead of .000"
  ],
  "constraints": [
    "Directive 2 (Deterministic calculation via CLI, zero mental math)",
    "Directive 4 (APA 7th Edition typography)",
    "Directive 6 (English ASCII filenames)",
    "Universal Path Portability (resolve all paths via $SUITE_REPO_DIR and $ACTIVE_PROJECT_DIR; zero hardcoded machine paths)"
  ]
}
```

### Exemplar 2: Continuous Learning Cascade — Trajectory Reconstruction
```json
{
  "task_id": "TSK-YYYYMMDD-LEARN-TRJ-<SLUG>-001",
  "stage": "Continuous Learning Cascade - Step 1: Trajectory Reconstruction",
  "worker_agent": "trajectory-analyzer",
  "objective": "Reconstruct the observable execution chronology, tool calls, and error trajectory for the specific defect: <DETAILED_DEFECT_DESCRIPTION>.",
  "target_script": "view_file / grep_search / write_to_file",
  "inputs": [
    "03_deliverables/Chapter_4_Results.docx",
    "02_analysis_code/compile_gold_standard_chapter4.py",
    ".agents/state/trajectory_events.jsonl"
  ],
  "required_artifacts": [
    ".agents/learning/experience/TRJ-<SLUG>-001.json",
    ".agents/learning/experience/TRJ-<SLUG>-001.md"
  ],
  "acceptance_criteria": [
    "Reconstruct observable tool calls and artifact state without fabricating private thoughts",
    "Identify exact failure points and error manifestations in input files",
    "Convert all file paths to repository-relative paths (Universal Path Portability Mandate)",
    "Output valid JSON conforming to trajectory.schema.json and companion Markdown report"
  ],
  "constraints": [
    "Directive 0 (Binary Honesty Protocol)",
    "Directive 6 (English ASCII filenames)",
    "Directive 25 (Universal Anti-Shortcut, Zero-Fastpath, No-Rush & Proper Execution Invariant)"
  ]
}
```

### Exemplar 3: Deliverable Remediation Post-Graduation
```json
{
  "task_id": "TSK-2026-REMEDIATE-REFS-LEAK-POST-GRADUATION",
  "stage": "Remediation of Bibliographic Leakage & Master Monograph Update",
  "worker_agent": "academic-writer",
  "objective": "Execute the clean remediation of references in Comprehensive_References.docx and Thesis_Final_Master.docx using evolved structural validation, purging all leaked subheadings and non-reference text",
  "target_script": "python3 02_analysis_code/restore_comprehensive_references_v2.py",
  "inputs": [
    "03_deliverables/Thesis.docx",
    "04_references_and_lit/Reference.docx",
    "03_deliverables/Thesis_Chapters1to3.docx",
    "03_deliverables/Chapter_5_Discussion.docx",
    "03_deliverables/All_Appendices.docx"
  ],
  "required_artifacts": [
    "03_deliverables/Comprehensive_References.docx",
    "03_deliverables/Thesis_Final_Master.docx",
    "03_deliverables/thesis_assembly_manifest.json"
  ],
  "acceptance_criteria": [
    "Apply graduated structural citation parsing invariants (LSN-2026-STRUCTURAL-REFERENCE-PARSING-001)",
    "Strictly exclude non-reference subheadings and section labels",
    "Regenerate 03_deliverables/Comprehensive_References.docx containing ONLY genuine references",
    "Recompile 03_deliverables/Thesis_Final_Master.docx maintaining Chapters 1-5, all footnotes, and appendices intact",
    "Verify that references section contains zero non-reference text",
    "Update 03_deliverables/thesis_assembly_manifest.json with verified reference counts"
  ],
  "constraints": [
    "Directive 4 (APA 7th Edition typography)",
    "Directive 5 (Persian Academic OpenXML Typography Standards, RTL, hanging indents)",
    "Directive 6 (English ASCII filenames)",
    "Directive 23 (Clean Workspace Root Standard: place script in 02_analysis_code/)"
  ]
}
```

---

## 4. Canonical Academic Pipeline Presets & Execution Sequences

Detailed stage-by-stage architectures for full academic workflows:

1. **Chapter 4 Findings (`chapter4_micro`, Phases 4A–4D Decoupled)**:
   - `Phase 4A: Data Engineering & Curation (4A.0–4A.2)` $	o$ `[Gate 1: Data Passport]`
   - `Phase 4B: Assumptions & Descriptives (4B.1–4B.4)` $	o$ `[Gate 2: Assumption Authorization]`
   - `Phase 4C: Inferential Modeling & Anomaly Audit (4C.1–4C.5)` $	o$ `[Gate 3: Mathematical Admissibility Sign-Off]`
   - `Phase 4D: Scholarly Drafting (Tables First -> Dynamic Non-Template Narration -> 4D.0–4D.11)`

2. **Chapter 5 Discussion (`chapter5_micro`, Stages 5.1–5.10)**:
   - `5.1 Recap` $	o$ `5.2 Deep Discussion (5.2.1, ...)` $	o$ `5.3 Null Results` $	o$ `5.4 Implications` $	o$ `5.5 Limitations` $	o$ `5.6 Recommendations` $	o$ `5.7 Fidelity Audit` $	o$ `5.8 Citation QC` $	o$ `5.9 Assembly` $	o$ `5.10 Viva Voce`

3. **Chapter 2 Literature Review (`persian-literature-review-builder`, Stages 2.1–2.8)**:
   - `2.1 Foundations` $	o$ `2.2 Bibliometrics` $	o$ `2.3 International Lit` $	o$ `2.4 Iranian Lit` $	o$ `2.5 Synthesis` $	o$ `2.6 Matrix Table` $	o$ `2.7 Model Grounding` $	o$ `2.8 Assembly`

4. **Research Proposal (`persian-proposal-builder`, Stages P.1–P.8)**:
   - `P.1 Problem` $	o$ `P.2 Significance` $	o$ `P.3 Hypotheses` $	o$ `P.4 Design` $	o$ `P.5 Power (G*Power)` $	o$ `P.6 Instruments` $	o$ `P.7 Ethics` $	o$ `P.8 Assembly`

5. **Scale Validation (`scale_validation`, Stages V.1–V.9)**:
   - `V.1 CVR/CVI` $	o$ `V.2 Item Analysis` $	o$ `V.3 EFA` $	o$ `V.4 CFA` $	o$ `V.5 Construct Validity` $	o$ `V.6 Invariance` $	o$ `V.7 Reliability` $	o$ `V.8 IRT/ROC` $	o$ `V.9 Monograph`

6. **Defense Presentation (`persian-defense-presentation-builder`, Stages D.0–D.7)**:
   - `D.0 Ingestion` $	o$ `D.1 Storyboard` $	o$ `D.2 Hypothesis Slides` $	o$ `D.3 PPTX/HTML` $	o$ `D.4 Diagram` $	o$ `D.5 Script` $	o$ `D.6 Collision QA` $	o$ `D.7 Viva Voce`

7. **Data Simulation (`data_generation`, Stages DS.0–DS.5)**:
   - `DS.0 Blueprint Gate` $	o$ `DS.1 Spec & Power` $	o$ `DS.2 Scales` $	o$ `DS.3 Monte Carlo` $	o$ `DS.4 Anomaly Screening` $	o$ `DS.5 Curation & Provenance`

8. **Universal Academic Revision (`academic_revision`, Stages R.0–R.6)**:
   - `R.0 Ingestion & Scoping` $	o$ `R.1 3-Tier Multi-Domain Triage` $	o$ `R.2 Stats Recalculation` $	o$ `R.3 Surgical In-Place Remediation (Document Conservation >= 90% & Highlights)` $	o$ `R.4 Response Table Compilation` $	o$ `R.5 Adversarial Audit (Fail-Closed)` $	o$ `R.6 Committee / Journal Sign-Off`
