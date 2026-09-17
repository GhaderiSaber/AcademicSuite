# Artifact-Based Communication & Academic State Specification

This document specifies the **artifact-first communication architecture** for the Academic Suite. Under this model, autonomous agents coordinate through structured, schema-validated disk artifacts rather than transmitting monolithic text or unparsed numerical tables through conversational context windows.

---

## 1. Architectural Motivation

In complex multi-agent academic workflows (such as dissertation analysis, psychometric validation, and multi-chapter drafting), passing extensive intermediate calculations and draft chapters inside LLM message envelopes introduces three fatal failure modes:
1. **Context Bloat & Token Degradation**: Subagent prompt buffers become saturated with thousands of lines of raw numbers, degrading reasoning fidelity.
2. **Instruction Drift & Hallucination**: Numbers repeated across conversational turns risk subtle decimal mutations ($p = .014 \rightarrow .019$).
3. **Loss of Auditability**: Conversational claims lack verifiable provenance on physical disk.

### The Artifact-First Solution
- **The Producers ("The Hands")**: Execute deterministic Python/R scripts, write exact structured results to disk in `academic-state/`.
- **The Handoff Envelope**: Subagents emit lightweight pointer envelopes containing execution status, artifact paths, and high-level summaries.
- **The Consumers**: Downstream agents (`writing-agent`, `validation-agent`, `digital-saber`) inspect artifacts directly via `view_file` or CLI commands.
- **The Single Source of Truth**: The physical `academic-state/` directory maintains the verified state of the research project.

---

## 2. Canonical Directory Hierarchy

Every research project maintained in `projects/<project-name>/` includes a dedicated `academic-state/` directory structured as follows:

```
academic-state/
├── project.json                      # Project metadata, stage gate, orchestrator assignment
├── requirements.json                 # RQs, directional hypotheses, institutional guidelines
├── analysis_plan.json                # Statistical strategy, software engines, planned stages
├── decisions.json                    # Auditable research decisions journal (Directive 11)
│
├── data/
│   ├── data_dictionary.json          # Variable codebook, reverse-scoring keys, item ranges
│   └── data_quality.json             # Screening: missingness (MCAR), outliers, straight-lining
│
├── analysis/
│   ├── descriptive.json              # Sample parameters (M, SD, Skew, Kurtosis) & correlation matrix
│   ├── reliability.json              # Internal consistency (Cronbach's alpha, McDonald's omega)
│   ├── cfa.json                      # Factor loadings (lambda), AVE, CR, cross-loadings, fit
│   └── sem.json                      # Path coefficients, bootstrap indirect effects, 11 fit indices
│
├── validation/
│   ├── data_validation.json          # PASS/FAIL report from data integrity validator
│   ├── statistical_validation.json   # PASS/FAIL report from assumption & numerical validators
│   └── writing_validation.json       # PASS/FAIL report from APA 7 & typography validators
│
└── outputs/                          # Synchronized triads (.docx, .md, .json) & publication figures
```

---

## 3. JSON Schemas & Validation Contracts

All state artifacts are governed by Draft-07 JSON schemas stored in `.agents/shared/schemas/academic_state/`:

| Artifact | Schema File | Primary Fields & Validation Invariants |
| :--- | :--- | :--- |
| `project.json` | `project.schema.json` | `project_id`, `title`, `methodology_type`, `sample_size`, `current_stage`, `orchestrator`, `status` |
| `requirements.json` | `requirements.schema.json` | `research_questions`, `hypotheses` (IV, DV, direction), `institutional_guidelines`, `deliverables` |
| `analysis_plan.json` | `analysis_plan.schema.json` | `significance_alpha`, `power_target`, `bootstrap_resamples`, `planned_sequence`, `variables` |
| `decisions.json` | `decisions.schema.json` | `decisions` array with `decision_id`, `timestamp`, `category`, `decision`, `rationale`, `agent` |
| `data/data_dictionary.json` | `data_dictionary.schema.json` | `total_items`, `scales` (item counts, Likert range, reverse items), `columns` mapping |
| `data/data_quality.json` | `data_quality.schema.json` | `sample_n`, `missing_rate`, `mcar_test` ($\chi^2, df, p$), `outliers_detected`, `quality_verdict` |
| `analysis/descriptive.json` | `descriptive.schema.json` | `sample_size`, `variables` ($M, SD, SE, \text{Skew}, \text{Kurtosis}$), `correlations` |
| `analysis/reliability.json` | `reliability.schema.json` | `sample_size`, `scales` with `cronbach_alpha`, `mcdonald_omega`, `adequate` |
| `analysis/cfa.json` | `cfa.schema.json` | `factors` ($\lambda, SE, p$, AVE, CR), `model_fit` ($\chi^2, df, \text{CFI}, \text{TLI}, \text{RMSEA}, \text{SRMR}$) |
| `analysis/sem.json` | `sem.schema.json` | `fit_indices`, `paths` ($\beta, B, SE, t/z, p$), `indirect_effects` (BCa 95% CI), `hypotheses_verdicts` |
| `validation/*.json` | `validation_report.schema.json` | `validator`, `overall_verdict` (PASS / NEEDS_REVIEW / FAIL), `results` with errors and warnings |

---

## 4. Subagent Handoff Protocol

When an Antigravity subagent finishes an execution micro-stage, it returns a **lightweight handoff envelope** instead of conversational text dumping.

### Producer Handoff Envelope
```json
{
  "sender": "statistics-agent",
  "recipient": "academic-orchestrator",
  "status": "STAGE_COMPLETED",
  "stage_id": "03_sem_model",
  "artifacts_produced": [
    "academic-state/analysis/sem.json",
    "academic-state/outputs/05_macro_model.docx",
    "academic-state/outputs/05_macro_model.md"
  ],
  "summary": "SEM structural model estimated via R lavaan. Model fit: chi2/df=1.84, CFI=.962, RMSEA=.048. Hypotheses 1 and 2 supported.",
  "validation_required": true
}
```

### Downstream Consumer Consumption
1. **Writing Agent (`writing-agent`)**:
   - Calls `view_file` on `academic-state/analysis/sem.json`.
   - Extracts exact $\beta$, $t$, and $p$-values.
   - Formulates APA 7 narrative and 3-line tables adhering to Persian leading zero standard (`۰.۰۰۱ > p`).
2. **Validation Agent (`validation-agent`)**:
   - Runs `validators/run_all_validators.py --stage-dir academic-state/outputs`.
   - Compares reported values in `.md` against `academic-state/analysis/sem.json`.
   - Writes verdict to `academic-state/validation/statistical_validation.json`.
3. **Academic Orchestrator (`academic-orchestrator`)**:
   - Inspects validation verdict.
   - Executes `python3 scripts/academic_state_manager.py set-stage --stage 06_hypothesis_1`.

---

## 5. State Manager CLI Engine ("The Hands")

The deterministic state manager engine is located at `scripts/academic_state_manager.py`.

### Available CLI Commands

#### 1. Initialize a Project State Hierarchy
```bash
python3 scripts/academic_state_manager.py init <project_path> \
  --title "Study Title" \
  --methodology sem \
  --n 300
```
Creates the entire `academic-state/` folder structure, populating baseline schema-compliant starter templates.

#### 2. Validate Project State Against Schemas
```bash
python3 scripts/academic_state_manager.py validate <project_path>
```
Inspects all JSON artifacts in `academic-state/` using `jsonschema` against official schemas in `.agents/shared/schemas/academic_state/`. Returns exit code `0` on PASS, `1` on FAIL.

#### 3. View Executive Dashboard Status
```bash
python3 scripts/academic_state_manager.py status <project_path>
```
Outputs an executive status object showing current stage, completed analyses, active validation verdicts, and output counts.

#### 4. Record an Auditable Decision
```bash
python3 scripts/academic_state_manager.py record-decision <project_path> \
  --category statistical_modeling \
  --decision "Adopted BCa 5,000 bootstrap resamples for indirect effects" \
  --rationale "Addresses asymmetry in the sampling distribution of ab" \
  --agent statistical-expert
```
Appends a permanent decision record (`DEC-XXX`) with UTC timestamp to `decisions.json`.

#### 5. Advance Stage Gate
```bash
python3 scripts/academic_state_manager.py set-stage <project_path> \
  --stage "04_bivariate_correlations" \
  --status "in_progress"
```

---

## 6. Automated Testing & Compliance

The test suite in `tests/test_academic_state.py` verifies:
- File and folder scaffolding integrity.
- JSON schema conformity for initialized projects.
- Auditable decision recording and sequence numbering.
- Stage advancement and metadata mutations.
- Real-world project compliance against `projects/study_act_burnout/academic-state/`.

Run the test suite:
```bash
python3 tests/test_academic_state.py
```
