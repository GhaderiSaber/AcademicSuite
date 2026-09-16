---
name: proposal
description: >-
  Research proposal design, inverted-triangle problem statements, G*Power sampling, and academic proposal compilation.
---

# Research Proposal Orchestration Workflow (طرح تحقیق / پروپوزال)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for designing, justifying, psychometrically specifying, and compiling graduate research proposals (*پروپوزال طرح پژوهش*) for master's and doctoral councils in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                       Research Topic / Target Population
                       Independent & Dependent Variables
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STEP 1: DIGITAL SABER   │
                         │   Master Lead Assessment  │
                         │  (Precedent CBR Retrieval)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 2: METHODOLOGY EXPERT│
                         │ Inverted-Triangle Problem │
                         │ G*Power 3.1 Sample Power  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 3: STATISTICAL EXPERT│
                         │ Hypotheses Formulation &  │
                         │   Analysis Plan Design    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 4: LITERATURE EXPERT │
                         │ Psychometric Instruments  │
                         │ (Questionnaires.xlsx Res) │
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │ STEP 5: RESULTS QC        │                 │   STEP 6: EVIDENCE QC     │
  │     Results Auditor       │                 │     Evidence Auditor      │
  │ (APA 7 & Council Rules)   │                 │ (Citation Integrity)      │
                         ┌───────────────────────────┐
                         │ STAGE P.1: PROBLEM & GAP  │
                         │ Inverted-Triangle Context │
                         │ (01_problem_statement)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE P.2: SIGNIFICANCE │
                         │ Theoretical & Practical   │
                         │   (02_significance.docx)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE P.3: HYPOTHESES    │
                         │ Directional Hypotheses    │
                         │  (03_hypotheses.docx)     │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE P.4: METHODOLOGY  │
                         │ Design & G*Power Sampling │
                         │ (04_methodology_samp.docx)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE P.5: INSTRUMENTS  │
                         │ Questionnaires & Validity │
                         │   (05_instruments.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE P.6: ETHICS & PLAN  │
                         │ Statistical Analysis Plan │
                         │   (06_analysis_plan.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE P.7: PROPOSAL ASSM  │
                         │ OpenXML Section Assembly  │
                         │  (Research_Proposal.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE P.8: COUNCIL REVIEW │
                         │ Council Readiness Sim     │
                         │ (XX_council_readiness)    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                            APPROVED PROPOSAL PACKAGE
```

---

## Prerequisites & Required Inputs

- **Research Idea**: General research topic, target population, clinical setting.
- **Variables**: Independent variable (e.g. intervention model), Dependent variable(s), potential Mediators/Moderators.
- **Academic Degree Level**: Master's (M.A./M.Sc.) or Doctoral (Ph.D.).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (CBR Precedent Matching)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests proposed research variables and population.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve the top historical proposal precedents.
  - Formulates initial project brief and logs entry in `decision_journal_engine.py`.
- **Output**: Proposal scoping brief with precedent guidance.

### Step 2: Methodology Expert Subagent (Problem Statement & G*Power Sampling)
- **Agent**: `methodology-expert`
- **Action**:
  - Structures the Problem Statement (*بیان مسئله*) using the **Inverted-Triangle Model**:
    1. Broad societal/clinical epidemiological burden.
    2. Specific construct interactions and theoretical gaps.
    3. The focal intervention or predictive model justification.
  - Calculates exact statistical power via `gpower-sample-size-calculator`:
    - Fixes $\alpha = .05$, Power $(1 - \beta) = .80$ or $.95$, effect size $f = 0.25$ or $f^2 = 0.15$.
    - Justifies final sample size ($N$) with 15% attrition buffer.
  - Defines internal and external validity safeguards for Chapter 3.
- **Output**: `proposal_methodology_blueprint.json`.

### Step 3: Statistical Expert Subagent (Directional Hypotheses & Analysis Plan)
- **Agent**: `statistical-expert`
- **Action**:
  - Formulates formal directional research hypotheses (*فرضیه‌های پژوهش*) based on theoretical mechanisms.
  - Specifies conceptual and operational definitions (*تعاریف مفهومی و عملیاتی*) for each variable.
  - Formulates the statistical analysis plan (ANCOVA, Hayes PROCESS, SEM/CFA) and prerequisite assumption tests.
- **Output**: `proposal_hypotheses_and_plan.json`.

### Step 4: Literature Expert Subagent (Instrument Resolution)
- **Agent**: `literature-expert`
- **Action**:
  - Searches the 4,880 psychometric instruments in `Questionnaires.xlsx` via `psychometric-scale-resolver`.
  - Extracts verified item counts, subscale factor structures, Likert response ranges, and reported Persian psychometric reliability ($\alpha$) and validity indices.
  - Harvests 15–20 foundational empirical citations from PubMed, CrossRef, and SID.ir.
- **Output**: `instruments_and_literature_matrix.json`.

### Step 5 & 6: QC Audit Cascade (Council Guidelines & Citation Check)
- **Agents**: `results-auditor` & `evidence-auditor`
- **Action**:
  - Verifies university review council compliance (*فرم پروپوزال مصوب دانشگاه*).
  - Checks bidirectional citation consistency: all cited authors are present in references.
  - Checks for elimination of AI boilerplate clichés.
- **Output**: `proposal_audit_report.json`.

### Micro-Stage Execution Sequence & Triad Artifact Invariant (Directive 3 & 11)

To prevent shortcutting, research proposal drafting is strictly partitioned into independent micro-stages. Monolithic execution is prohibited. **Triad Artifact Invariant**: Every stage generates `.docx` (APA 7 OpenXML), `.md` (Markdown narrative & tables), and `.json` (structured data/audit).

#### Stage P.1: Problem Statement & Research Gap
- **Agent**: `methodology-expert` + `academic-writer`
- **Output**: `01_problem_statement.docx`, `01_problem_statement.md`, `01_problem_statement.json` (Inverted-triangle contextual grounding, epidemiologic burden, documented research gap).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.2: Theoretical & Practical Significance
- **Agent**: `academic-writer`
- **Output**: `02_significance.docx`, `02_significance.md`, `02_significance.json` (Theoretical contributions, scientific novelty, clinical/organizational benefits).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.3: Objectives, Research Questions & Directional Hypotheses
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `03_hypotheses.docx`, `03_hypotheses.md`, `03_hypotheses.json` (Primary/secondary objectives, formal hypotheses with operationalized variables).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.4: Methodological Design & G*Power Sampling
- **Agent**: `methodology-expert`
- **Output**: `04_methodology_samp.docx`, `04_methodology_samp.md`, `04_methodology_samp.json` (Design taxonomy, G*Power 3.1 power curves, attrition adjustment).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.5: Measurement Instruments & Psychometrics
- **Agent**: `psychometric-expert` + `academic-writer`
- **Output**: `05_instruments.docx`, `05_instruments.md`, `05_instruments.json` (Questionnaires, subscale items, scoring protocols, psychometric precedents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.6: Data Analysis Plan & Ethical Considerations
- **Agent**: `statistical-expert` + `academic-writer`
- **Output**: `06_analysis_plan.docx`, `06_analysis_plan.md`, `06_analysis_plan.json` (Inferential statistical sequence, parametric verification, IR.REC ethics approval guidelines).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.7: Proposal Assembly & Merging
- **Agent**: Execution Layer via `orchestrator_cli.py --assemble-chapter Research_Proposal.docx`
- **Output**: `Research_Proposal.docx` + `Research_Proposal.md` (Concatenated from verified section documents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage P.8: Graduate Council Review Simulation
- **Agent**: `final-judge`
- **Output**: `XX_proposal_council_brief.docx`, `XX_proposal_council_brief.md`, `proposal_council_readiness_score.json` (Review council defense challenges & approval index).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

---

### Interactive Stage-Gate Communication Format (Directive 11)
At the completion of each micro-stage above, the agent MUST output:
```markdown
### 🏁 Stage X Completion Report: <Stage Name>
- **What Was Done**: Subagent used, deterministic scripts executed, exact numbers verified, and physical disk artifacts generated.
- **What Will Be Done Next**: Target next stage name, assigned subagent, input prerequisites, and expected deliverables.

> **Awaiting Confirmation**: Please review the above stage results. Reply to confirm or adjust, and I will proceed to **Stage X+1: `<Next Stage Name>`**.
```
The agent **MUST STOP and wait for user confirmation** before advancing. Monolithic multi-stage execution in a single turn is prohibited.

---

## Antigravity Multi-Agent Execution Architecture (Directive 12, 12.1 & PURE_ANTIGRAVITY_DELIBERATION_PROTOCOL)

1. **The Hands**: Deterministic tools (`gpower_engine.py`, `generate_proposal_docx.py`) run via CLI to compute sample power curves, format APA 7 tables, and inject OpenXML Persian typography on disk.
2. **The Brains & Critics**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `methodology-expert`: Structures inverted-triangle problem statements and samples.
   - `statistical-expert`: Formulates directional hypotheses and analytical designs.
   - `evidence-auditor`: Reconciles APA 7 bibliographic references and cross-checks instruments.
   - `results-auditor`: Audits council guidelines and eliminates AI cliches.
   - `academic-writer`: Compiles publication-grade Persian proposal sections (`.docx`).
   - `final-judge`: Simulates graduate review council cross-examination and scores approval readiness.
3. **Sole Orchestrator**: Subagents and execution instruments are orchestrated directly and exclusively by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and the Critic-Generator Barrier.

