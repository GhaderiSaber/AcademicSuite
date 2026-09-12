# Experimental Clinical Intervention Protocol & Session Manual Workflow (طراحی و تدوین پروتکل مداخله و بسته آموزشی/درمانی)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for designing, structuring, and compiling standardized, evidence-based psychological and educational intervention protocols for Master's and Doctoral experimental and quasi-experimental dissertations in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
               Clinical Framework / Preset (ACT, CBT, Schema, CFT, MBSR, Positive)
               Target Population, Session Count (8-12), Session Duration (60-90m)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │ Master Precedent Retrieval   │
                        │ (Approach, Setting & Budget) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 2: METHODOLOGY EXPERT  │
                        │ CONSORT 2010 Flowchart &     │
                        │ G*Power Sample Size Modeling │
                        │ (gpower-sample-size-calc)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 3: ACADEMIC WRITER    │
                        │ 6-Phase Pedagogical Structure│
                        │ & Method Triad (Mot/Des/Adv) │
                        │(psych-intervention-builder) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STEP 4: OPENXML COMPILATION  │
                        │ Publication-Grade Word Manual│
                        │ APA 7 Session Summary Table  │
                        │ (openxml_artifact_engine)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 5: FINAL JUDGE      │
                        │ Clinical Safety & Committee  │
                        │ Fidelity Cross-Examination   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 6: SABER HUMAN GATE    │
                        │ Admin Desk Approval Card     │
                        │     (ID: 124911145)          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • پروتکل_مداخله_درمانی.docx (Full Appendix Clinical Manual)
               • جدول_خلاصه_جلسات_مداخله.docx (Chapter 3 APA 7 Summary Table)
               • consort_flowchart.png (300-DPI Clinical Trial Flowchart)
               • protocol_blueprint.json (Machine-Readable Session Architecture)
```

---

## Prerequisites & Required Inputs

- **Clinical Approach / Framework**:
  - Supported presets: `act` (Acceptance & Commitment Therapy), `cbt` (Cognitive Behavioral Therapy), `schema` (Schema Therapy), `cft` (Compassion-Focused Therapy), `mbsr` (Mindfulness-Based Stress Reduction), `positive` (Positive Psychotherapy), `mindful_parenting` (Mindful Parenting), or a custom theoretical blueprint.
- **Target Population & Clinical Setting**:
  - Target group (e.g. healthcare workers with occupational burnout, adolescents with non-suicidal self-injury, adults with generalized anxiety, Type II diabetes patients).
  - Format: Group therapy or individual psychotherapy.
  - Number of sessions: 8, 10, or 12 sessions.
  - Session duration: 60 to 90 minutes per session.
- **Dependent Variables & Target Processes**:
  - Target pathology / behavioral symptoms (e.g. emotional exhaustion, experiential avoidance, early maladaptive schemas).
  - Theoretical mechanism to be cultivated (e.g. psychological flexibility, self-compassion, cognitive defusion).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Evaluates research proposal and theoretical framework.
  - Queries `.agents/memory/case_memory_engine.py` for similar clinical intervention studies (e.g. `case_001_act_burnout`, `case_014_anita_montazeri_choice_theory`, `case_015_ailin_ghasemi_schema_eating_disorder`, `case_022_act_diabetes`).
  - Establishes clinical intervention boundaries, session duration, and safety parameters.
- **Output**: Clinical intervention specification brief.

### Step 2: Methodology Expert Subagent (CONSORT 2010 Flowchart & Sampling Power)
- **Agent**: `methodology-expert` (wielding `gpower-sample-size-calculator` and `psychological-intervention-protocol-builder`)
- **Action**:
  - Determines participant allocation and attrition buffer (minimum 15% recommended for clinical dropouts).
  - Generates CONSORT 2010 clinical trial flow diagram (`consort_flowchart.png`) across 4 standard phases:
    1. Enrollment (Assessed for eligibility, excluded).
    2. Allocation (Randomized to Experimental vs Control / Waitlist).
    3. Follow-up (Intervention attendance, loss to follow-up).
    4. Analysis (Analysed per-protocol and intention-to-treat).
- **Output**: 300-DPI publication CONSORT diagram.

### Step 3: Academic Writer Subagent (6-Phase Session Structure & Method Triad)
- **Agent**: `academic-writer` (wielding `psychological-intervention-protocol-builder`)
- **Action**:
  - Structures each session according to the mandatory 6 pedagogical phases:
    1. Phase 1: Review & Mood Check (10–15 min) — برقراری ارتباط و بازبینی تکالیف.
    2. Phase 2: Psychoeducation & Conceptual Rationale (15–20 min) — مفهوم‌بندی و آموزش نظری.
    3. Phase 3: Experiential Technique or Metaphor (20–25 min) — تمرین تجربی و استعاره بالینی.
    4. Phase 4: In-Session Worksheet / Group Practice (15–20 min) — کاربرگ عملی و تمرین کلاسی.
    5. Phase 5: Behavioral Homework Assignment (10 min) — تکلیف خانگی ساختاریافته.
    6. Phase 6: Session Summary & Feedback (5 min) — جمع‌بندی و بازخورد پایانی.
  - Articulates the **Method Triad** for every major clinical technique:
    - **Motivation**: Why this technique is essential; the underlying avoidance or pathology targeted.
    - **Design**: Step-by-step procedure of how the technique is executed and internalized.
    - **Advantage**: Methodological and clinical superiority over traditional alternatives.
- **Output**: Session-by-session clinical blueprint with metaphors, worksheets, and homework.

### Step 4: OpenXML Physical Document Compilation
- **Agent**: `academic-writer` (wielding `openxml_artifact_engine`)
- **Action**:
  - Compiles `پروتکل_مداخله_درمانی.docx` (Complete dissertation Appendix manual):
    - Persian typography: `B Titr` 16–18 pt (Titles), `B Nazanin` 13–14 pt (Body), `Times New Roman` (Latin/Stats).
    - Dual-tone callout boxes for clinical metaphors and Method Triad summaries.
    - Full procedural worksheets and homework logs for participants.
  - Compiles `جدول_خلاصه_جلسات_مداخله.docx`:
    - Clean, 3-border APA 7 summary table summarizing Session Number, Objective, Core Techniques, and Homework for direct insertion into Chapter 3.
  - Exports `protocol_blueprint.json` containing the machine-readable ledger of all sessions.
- **Output**: Binding-ready Word documents and JSON ledger.

### Step 5: Final Judge Subagent (Clinical Safety & Committee Defense Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Simulates hostile clinical committee examination:
    - Verifies therapist adherence and treatment fidelity safeguards.
    - Audits potential counter-therapeutic risks (e.g. emotional dysregulation during imagery rescripting or defusion exercises).
    - Confirms homework compliance strategies and absence of coercive clinical techniques.
  - Computes Clinical Protocol Fidelity Index (Target: $\ge 95\%$).
- **Output**: Committee defense verdict and fidelity clearance report.

### Step 6: Digital Saber Master Agent (Human Gate Sign-off)
- **Agent**: `digital-saber`
- **Action**:
  - Enforces **Rule 11**: Generates Saber Admin Desk Card (`124911145`).
  - Logs decision in `DecisionJournalEngine` (`.agents/memory/decisions/`).
- **Output**: Verified, locked clinical intervention suite.

---

## Deliverables Checklist
- [ ] `پروتکل_مداخله_درمانی.docx` — Complete session-by-session clinical manual for thesis Appendix.
- [ ] `جدول_خلاصه_جلسات_مداخله.docx` — Defense-ready APA 7 summary table for Chapter 3 / Proposal.
- [ ] `consort_flowchart.png` — 300-DPI CONSORT 2010 participant allocation flowchart.
- [ ] `protocol_blueprint.json` — Structured JSON schema of the intervention.
