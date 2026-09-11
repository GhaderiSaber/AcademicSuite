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
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 7: ACADEMIC WRITER   │
                         │ Proposal Compilation      │
                         │ (پروپوزال_طرح_پژوهش.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    STEP 8: FINAL JUDGE    │
                         │ Review Council Readiness  │
                         │ Committee Defense Index   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 9: SABER HUMAN GATE  │
                         │ Admin Desk Sign-Off       │
                         │     (ID: 124911145)       │
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

### Step 7: Academic Writer Subagent (Proposal Compilation)
- **Agent**: `academic-writer`
- **Action**:
  - Compiles the full proposal document in academic Persian (`پروپوزال_طرح_پژوهش.docx`).
  - Sections:
    1. مشخصات دانشجو و استاد راهنما
    2. بیان مسئله (Problem Statement)
    3. ضرورت و اهمیت پژوهش (Significance)
    4. پیشینه پژوهش (Empirical Background)
    5. اهداف و فرضیه‌های پژوهش (Aims & Hypotheses)
    6. تعاریف مفهومی و عملیاتی (Definitions)
    7. روش‌شناسی، جامعه، نمونه و ابزارهای پژوهش (Methodology & Scales)
    8. روش تحلیل داده‌ها (Statistical Plan)
    9. فهرست منابع بر اساس APA 7 (References)
  - Enforces Persian half-spaces (`\u200c`), B Nazanin/B Titr typography, and OpenXML `<w:bidi/>` directionality.
- **Output**: `پروپوزال_طرح_پژوهش.docx`.

### Step 8: Final Judge Subagent (Council Review Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Cross-examines proposal against university council rejection risks (e.g. insufficient sample size, unvalidated instrument, ambiguous operational definition).
  - Calculates Review Council Approval Index ($0\text{--}100\%$).
- **Output**: `proposal_council_readiness_score.json`.

### Step 9: Saber Human Gate Sign-off (Rule 11)
- **Agent**: `digital-saber`
- **Action**:
  - Generates Admin Desk Approval Card for Saber (`124911145`):
    - Proposed Topic, Design, $N$, Instruments, Council Readiness Index.
    - One-click commands: `/approve_proposal` or `/adjust_proposal`.
  - Upon approval, proposal is released to client.
