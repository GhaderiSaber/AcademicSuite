# Thesis Revision & Examiner Rebuttal Orchestration Workflow (مدیریت و اعمال اصلاحات اساتید و داوران)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for systematically triaging, remediating, and documenting revisions requested by thesis supervisors (استاد راهنما), advisors (مشاور), or defense examination committees (هیئت داوران) for graduate dissertations and master's theses.

```text
                                     INPUT
                     Reviewed Thesis Draft (.docx) / Feedback Text
                     Committee Defense Minutes / Margin Comments
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STEP 1: DIGITAL SABER   │
                         │ Ingest & Extract Comments │
                         │ (extract_docx_comments.py)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 2: TRIAGE AUDITORS   │
                         │ 3-Tier Categorization     │
                         │(Format / Stats / Theory)  │
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                ▼                      ▼                      ▼
  ┌───────────────────────────┐ ┌─────────────┐ ┌───────────────────────────┐
  │STEP 3A: RESULTS AUDITOR   │ │STEP 3B: STAT│ │STEP 3C: LITERATURE & WRITER│
  │Tier 1: Format & APA 7     │ │Tier 2: Stats│ │Tier 3: Theory & Discussion│
  │(Typography, BiDi, Borders)│ │(Re-analysis)│ │(Citations, Mechanisms)    │
  └─────────────┬─────────────┘ └──────┬──────┘ └─────────────┬─────────────┘
                │                      │                      │
                └──────────────────────┼──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 4: ACADEMIC WRITER   │
                         │ Chapter Revisions & Draft │
                         │ Academic Rebuttal Table   │
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │   STEP 5: STATISTICAL QC  │                 │   STEP 6: EVIDENCE QC     │
  │    Statistical Auditor    │                 │     Evidence Auditor      │
  │ (Fidelity & Anomaly Check)│                 │ (Irandoc & Citation Check)│
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    STEP 7: FINAL JUDGE    │
                         │ Committee Clearance Check │
                         │ Final Sign-Off Readiness  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 8: SABER HUMAN GATE  │
                         │ Admin Desk Sign-Off       │
                         │     (ID: 124911145)       │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         FINAL APPROVED REVISION PACKAGE
```

---

## Prerequisites & Required Inputs

- **Reviewed Document**: Annotated Word document (`.docx`) containing track changes and margin comments, or raw feedback text / defense minutes (`.txt`, `.pdf`).
- **Original Thesis Chapters**: Existing chapter files (Chapters 1–5).
- **Supervisor / Committee Identity**: Names and roles (Supervisor, Advisor, Internal Examiner, External Examiner).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Master Project Lead (Comment Extraction & Scoping)
- **Agent**: `digital-saber`
- **Action**:
  - Executes comment extraction script on the reviewed document:
    ```bash
    python3 .agents/skills/persian-thesis-revision-assistant/scripts/extract_docx_comments.py \
      --file "thesis_reviewed.docx" \
      --out "extracted_comments.json"
    ```
  - Parses comment metadata: author, date, target text snippet, and surrounding paragraph context.
  - Initializes revision case in `decision_journal_engine.py`.
- **Output**: `extracted_comments.json`.

### Step 2: Triage & Delegation (3-Tier Categorization)
- **Agent**: `digital-saber` & `results-auditor`
- **Action**:
  - Classifies each comment into one of 3 operational tiers:
    1. **Tier 1: FORMAT** (Margins, fonts, half-spaces `\u200c`, APA 7 3-line tables, Latin footnotes, Persian numbering).
    2. **Tier 2: STATS & METHODOLOGY** (Requests for additional assumption tests, effect sizes $\eta_p^2$, ANCOVA slope homogeneity verification, post hoc power, mediation bootstrap CIs).
    3. **Tier 3: THEORY & DISCUSSION** (Requests for recent 2023–2026 citations, conceptual clarification, deeper psychological mechanism explanation, or expanding clinical implications).
- **Output**: `triaged_comments.json`.

### Step 3: Targeted Remediation by Domain Subagents
- **Step 3A: Format & Typography Remediation**:
  - **Agent**: `results-auditor`
  - Corrects table borders to strict APA 7 (3 horizontal lines, zero vertical lines).
  - Enforces OpenXML directionality `<w:bidi w:val="1"/>`, `B Nazanin` 13 pt, and Persian half-spaces.
  - Checks native Word math `<m:oMath>` elements to prevent equation erasure.
- **Step 3B: Statistical Re-Analysis**:
  - **Agent**: `statistical-expert`
  - Re-executes statistical scripts in `.agents/skills/statistical-data-analyst/scripts/` to calculate missing metrics requested by examiners.
  - Updates `stats_results.json` with exact recalculated outputs (zero mental calculation).
- **Step 3C: Literature & Theoretical Expansion**:
  - **Agent**: `literature-expert` & `methodology-expert`
  - Harvests requested peer-reviewed studies (via PubMed, CrossRef, Magiran).
  - Formulates expanded theoretical explanations (Beck, Gross, Hayes, Bandura).

### Step 4: Academic Writer Subagent (Chapter Editing & Rebuttal Table Compilation)
- **Agent**: `academic-writer`
- **Action**:
  - Inserts all approved corrections directly into the respective chapter documents (Chapters 1–5), noting exact page and line numbers.
  - Formulates courteous, scholarly rebuttals for each comment following academic etiquette:
    - Expressing gratitude for the examiner's keen observation (*«با تشکر و سپاس از دقت‌نظر و پیشنهاد ارزشمند استاد محترم...»*).
    - Concisely specifying what was revised, recalculated, or added.
    - Explicitly documenting the page number, section, and table in the revised thesis.
  - Compiles the official university submission table via:
    ```bash
    python3 .agents/skills/persian-thesis-revision-assistant/scripts/generate_revision_response_docx.py \
      --json "resolved_comments.json" \
      --out "جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx"
    ```
- **Output**: Revised chapter files and `جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx`.

### Step 5: Statistical QC Subagent (Recalculation Fidelity & Anomaly Check)
- **Agent**: `statistical-auditor`
- **Action**:
  - Re-audits modified statistical tables using the Multi-Signal Anomaly Index (MSAI).
  - Verifies that new degrees of freedom and effect sizes match sample size $N$.
  - Confirms zero $p = .000$ occurrences and strict adherence to leading zero omission.
- **Output**: `revision_stats_audit.json`.

### Step 6: Evidence QC Subagent (Irandoc & Citation Re-Verification)
- **Agent**: `evidence-auditor`
- **Action**:
  - Cross-checks all newly added citations in the text against the reference list.
  - Runs Irandoc similarity scan on newly rewritten sections to guarantee $< 20\%$ similarity.
  - Ensures absolute elimination of generic AI phrasing.
- **Output**: `revision_evidence_audit.json`.

### Step 7: Final Judge Subagent (Committee Re-Defense Clearance Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Evaluates whether all committee comments have been comprehensively and respectfully answered.
  - Checks if any unresolved ambiguities remain that could prompt examiner objection.
  - Computes Committee Sign-Off Approval Readiness Score ($0\text{--}100\%$).
- **Output**: `committee_clearance_report.json`.

### Step 8: Saber Human Gate Sign-off (Rule 11)
- **Agent**: `digital-saber`
- **Action**:
  - Transmits Final Revision Approval Card to Saber's Admin Desk (`124911145`):
    - Total Comments Triaged & Resolved (Format, Stats, Theory).
    - Key Modifications & Methodological Adjustments.
    - Committee Sign-Off Approval Readiness Score.
    - Attached Deliverables: `جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx` + Revised Chapters.
    - Commands: `/approve_revision` or `/adjust_revision`.
  - Upon sign-off, updates project status to `COMPLETED_AND_RELEASED` in `decision_journal_engine.py`.
