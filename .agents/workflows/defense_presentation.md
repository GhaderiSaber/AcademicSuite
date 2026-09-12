# Viva Voce Oral Defense Presentation & Committee Simulator Workflow (جلسه دفاع از پایان‌نامه و شبیه‌ساز جلسه داوری)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for extracting thesis findings, compiling publication-grade oral defense presentation slide decks across **3 distinct paths** (`html`, `pptx`, and `google_slides`), generating word-for-word candidate oral scripts with slide timing meters, and simulating viva voce defense committee cross-examinations.

```text
                                     INPUT
               Dissertation Chapters (1–5) OR Research Parameters
               (Topic, Design, Sample N, Findings, Candidate & Committee)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │ Master Precedent Retrieval   │
                        │ (Defense Timing & Scoping)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 2: RESULTS AUDITOR    │
                        │ Cross-Chapter Integrity QC   │
                        │ (thesis-integrity-auditor)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 3: ACADEMIC WRITER    │
                        │ 20-Slide Defense Storyboard  │
                        │ (Problem, Design, Stats,     │
                        │  Mechanisms & APA 7 Tables)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STEP 4: PRESENTATION EXPERT  │
                        │ Tri-Path Deck Compilation    │
                        │ • Path A: Interactive HTML   │
                        │ • Path B: Native PPTX + OMML │
                        │ • Path C: Word Speaker Notes │
                        │(persian-defense-presentation)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 5: FINAL JUDGE      │
                        │ Viva Voce Oral Defense Sim   │
                        │ (20 Committee Q&A Scenarios) │
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
               • اسلایدهای_جلسه_دفاع.pptx (16:9 Presentation Canvas)
               • defense_presentation.html (Interactive Reveal.js Deck)
               • متن_نطق_ارائه_دفاع.docx (Full Candidate Oral Script)
               • defense_committee_qa_card.json (20 Viva Voce Scenarios)
               • defense_manifest.json (Defense Timing & Presentation Ledger)
```

---

## Prerequisites & Required Inputs

- **Research Artifacts**:
  - Full dissertation draft (`.docx`) OR structured findings (`stats_results.json` + methodology + discussion).
- **Candidate & Committee Metadata**:
  - Candidate Name, Academic Degree (Master's / Ph.D.).
  - Thesis Title (Persian & English).
  - Supervisor (*استاد راهنما*), Advisor (*استاد مشاور*), and Department/Faculty Affiliation.
  - Target Defense Duration: Default 25–30 minutes (allocated across slides).
- **Preferred Presentation Track**:
  - `pptx`: Native Microsoft PowerPoint presentation with DrawingML RTL, native OMML formulas, and 300-DPI diagrams.
  - `html`: Modern browser presentation with glassmorphism, responsive animations, and timing meters.
  - `google_slides`: Google Drive @Document Bridge brief with Gemini slide prompts.

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests research topic, candidate profile, and thesis methodology.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve historical defense precedents and committee examiner profiles.
  - Establishes strict defense parameters:
    - Slide canvas: 16:9 widescreen.
    - Strict typography: Persian font `B Titr` (titles 28–36 pt), `B Nazanin` (body $\ge 20$ pt), and `Times New Roman` for statistics.
    - Time budgeting: 25 minutes total ($\approx 1.2$ minutes per slide).
- **Output**: Defense scoping brief and time-allocation matrix.

### Step 2: Results Auditor Subagent (Cross-Chapter Integrity & MSAI Screening)
- **Agent**: `results-auditor` (wielding `thesis-integrity-auditor`)
- **Action**:
  - Audits cross-chapter consistency before building slides:
    - Chapter 1 hypotheses match Chapter 4 statistical tests.
    - Chapter 3 sample size $N$ matches Chapter 4 degrees of freedom ($df$).
    - Zero synthetic integer means (Rule 9 compliance).
    - Multi-Signal Anomaly Index (MSAI) confirms zero unhedged data issues.
- **Output**: Pre-defense integrity clearance certificate.

### Step 3: Academic Writer Subagent (Defense Storyboard Scaffolding)
- **Agent**: `academic-writer`
- **Action**:
  - Translates a 150-page dissertation into an authoritative 18–22 slide storyboard:
    1. **Slide 1**: Title & Cover (Institutional branding, candidate & committee).
    2. **Slide 2**: Agenda & Committee Overview.
    3. **Slide 3**: Problem Statement (Inverted-triangle model & epidemiological burden).
    4. **Slide 4**: Theoretical Gap & Core Research Questions.
    5. **Slide 5**: Conceptual Model & Directional Hypotheses.
    6. **Slide 6**: Methodological Architecture & G*Power Sample Size Justification.
    7. **Slide 7**: CONSORT Participant Flow & Inclusion/Exclusion Criteria.
    8. **Slide 8**: Psychometric Measurement Instruments & Reliabilities ($\alpha$).
    9. **Slide 9**: Clinical/Experimental Intervention Timeline (Session breakdown).
    10. **Slide 10**: Descriptive Statistics & Baseline Equivalence.
    11. **Slide 11**: Univariate/Multivariate Statistical Findings (ANCOVA/MANOVA) with APA 7 borderless tables and native OMML math.
    12. **Slide 12**: Structural Equation Modeling / Mediation Path Trajectories.
    13. **Slide 13**: Longitudinal Stability & Follow-Up Analysis.
    14. **Slide 14**: Hypothesis Testing Decision Matrix (Confirmed/Rejected).
    15. **Slide 15**: Psychological Mechanisms (Beck, Hayes, Gross, Bandura).
    16. **Slide 16**: Theoretical Concordance (Iranian & International Literature).
    17. **Slide 17**: Clinical & Institutional Applied Implications.
    18. **Slide 18**: Methodological Limitations & Future Research Directions.
    19. **Slide 19**: Closing Appreciation & Defense Dedication.
- **Output**: Structured defense storyboard payload with slide archetypes.

### Step 4: Presentation Expert Subagent (Tri-Path Compilation & OpenXML Formatting)
- **Agent**: `presentation-expert` (wielding `persian-defense-presentation-builder`)
- **Action**:
  - Compiles the presentation across the target paths:
    - **Path A (HTML)**: Interactive single-file Reveal.js deck with dark/navy academic theme, responsive layouts, and slide-level timer indicators.
    - **Path B (PPTX)**: Native 16:9 PowerPoint file using `compile_defense_presentation.py` with RTL text direction, 300-DPI rendered diagrams, native Microsoft Office Math (`<m:oMath>`) equations, and geometric collision auditing.
    - **Path C (Speaker Notes)**: Word document (`متن_نطق_ارائه_دفاع.docx`) containing word-for-word candidate speech scripts for each slide, specifying exact transition phrases (*«همان‌گونه که در اسلاید بعد ملاحظه می‌فرمایید...»*) and time budget markers.
- **Output**: `اسلایدهای_جلسه_دفاع.pptx`, `defense_presentation.html`, `متن_نطق_ارائه_دفاع.docx`.

### Step 5: Final Judge Subagent (Defense Committee Viva Voce Simulator)
- **Agent**: `final-judge`
- **Action**:
  - Simulates the oral examination by internal and external examiners:
    - Generates 20 sharp, critical defense questions across Methodology, Statistical Assumptions, Clinical Validity, and Theoretical Generalizability.
    - Formulates model high-confidence answers with citation backing and page references.
    - Evaluates Committee Approval Probability Index (0–100%).
- **Output**: `defense_committee_qa_card.json` and viva voce defense strategy guide.

### Step 6: Digital Saber Human Gate Sign-Off (Admin Desk ID: 124911145)
- **Agent**: `digital-saber`
- **Action**:
  - Generates Admin Desk card for Saber Ghaderi (`124911145`).
  - Logs execution in `.agents/memory/decisions/dec_*.json` via `decision_journal_engine.py`.
  - Holds final client delivery pending one-click approval (`/approve_D401`).
- **Output**: Final verified defense package ready for candidate presentation.

---

## Deliverables Checklist

| # | Artifact | Description | Target Path |
|---|---|---|---|
| 1 | **`اسلایدهای_جلسه_دفاع.pptx`** | Native 16:9 PowerPoint slide deck with RTL typography, APA 7 borderless tables, OMML formulas, and embedded 300-DPI diagrams. | `output/` |
| 2 | **`defense_presentation.html`** | Interactive browser-based Reveal.js slide deck with glassmorphism, slide transitions, and presentation timer. | `output/` |
| 3 | **`متن_نطق_ارائه_دفاع.docx`** | Word-for-word candidate oral speech script for each slide with time budget markers and smooth transitions. | `output/` |
| 4 | **`defense_committee_qa_card.json`** | 20 anticipated viva voce examiner questions and structured authoritative responses. | `output/` |
| 5 | **`defense_manifest.json`** | Machine-readable defense metadata (slide count, duration, committee, integrity index). | `output/` |
