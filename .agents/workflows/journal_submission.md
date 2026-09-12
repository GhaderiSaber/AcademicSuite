# Academic Journal Article & Submission Packaging Workflow (تدوین مقاله علمی-پژوهشی و بسته سابمیت به مجلات)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for extracting, condensing, polishing, and packaging graduate dissertations, master's theses, or research findings into publication-ready journal manuscripts for international (ISI, Scopus Q1–Q4, Web of Science, PubMed) and Iranian (علمی-پژوهشی / ISC) journals.

```text
                                     INPUT
                     Thesis Draft (.docx) OR Research Parameters
                     (Topic, Design, Sample N, Findings, Target Journal)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │   Master Precedent Retrieval │
                        │  (Target Journal & Scoping)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 2: ACADEMIC WRITER    │
                        │ 5,000-Word IMRaD Extraction  │
                        │ (Intro, Methods, Results,    │
                        │  Discussion & APA 7 Tables)  │
                        │  (academic-article-writer)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STEP 3: TONE POLISHER AUDIT  │
                        │ Anti-AI Cliché Filter &      │
                        │ Human Scholarly Cadence      │
                        │ (ai-academic-tone-polisher)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 4: EVIDENCE AUDITOR   │
                        │ Paraphrasing & Irandoc Check │
                        │ (< 15% Similarity Index)     │
                        │  (irandoc-plagiarism-reducer)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 5: SUBMISSION ASSISTANT│
                        │ Cover Letter to Editor,      │
                        │ 14 CRediT Roles, Highlights  │
                        │(journal-submission-assistant)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 6: FINAL JUDGE      │
                        │ Peer-Review & Desk Review    │
                        │ Simulation (Acceptance 0-100)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 7: SABER HUMAN GATE    │
                        │ Admin Desk Approval Card     │
                        │     (ID: 124911145)          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • مقاله_علمی_پژوهشی.docx / Manuscript_Main_Text.docx
               • Cover_Letter_Editor.docx
               • Title_Page_CRediT.docx
               • Highlights_and_Abstract.docx
               • submission_manifest.json
```

---

## Prerequisites & Required Inputs

- **Source Research Content**:
  - Full thesis draft (`.docx`) OR structured findings (`stats_results.json` + methodology + discussion).
- **Publication Targets**:
  - Target Journal Name (e.g., *Journal of Contextual Behavioral Science*, *BMC Psychology*, *فصلنامه مطالعات روان‌شناختی دانشگاه الزهرا*).
  - Target Language & Indexing Track:
    - `en`: International English Journal (ISI / Scopus Q1–Q2 / Web of Science).
    - `fa`: Iranian Scientific-Research (علمی-پژوهشی / ISC).
- **Authorship & Affiliations**:
  - Author names, academic ranks, institutional affiliations, ORCID IDs, and Corresponding Author designation.

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests research topic and target journal specifications.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve the top historical publication precedents in the same field.
  - Establishes word count bounds (typically 5,000–6,500 words excluding references) and author guidelines.
  - Initializes project tracking in `.agents/memory/decision_journal_engine.py`.
- **Output**: Journal publication project brief and editorial parameter ledger.

### Step 2: Academic Writer Subagent (IMRaD Manuscript Extraction)
- **Agent**: `academic-writer` (wielding `academic-article-writer`)
- **Action**:
  - Condenses a 150-page dissertation into standard IMRaD format:
    1. **Title & Abstract**: Informative, non-declarative title; 250-word structured abstract (Background, Methods, Results, Conclusions) + 5 MeSH-compliant keywords.
    2. **Introduction**: 3-paragraph inverted triangle highlighting the theoretical gap (Beck, Hayes, Gross, Bandura) and directional hypotheses.
    3. **Methods**: Precise description of participants, experimental/correlational design, G*Power sampling justification, psychometric instruments (Cronbach's $\alpha$, scoring), and analytic software strategy.
    4. **Results**: APA 7th Edition three-line borderless tables, effect sizes ($\eta_p^2$, Cohen's $d$, $\beta$), exact $p$-values ($p < .001$ without leading zero).
    5. **Discussion**: 4-element psychological interpretation, empirical concordance mapping (Iranian + ISI literature), clinical implications, and methodological limitations.
- **Output**: Draft manuscript payload and claim-evidence matrix.

### Step 3: Tone Polisher Subagent (Anti-AI Clichés & Cadence Optimization)
- **Agent**: `academic-writer` (wielding `ai-academic-tone-polisher`)
- **Action**:
  - Scans draft against Kristin Sainani (Stanford University) medical/academic writing principles:
    - Eliminates robotic AI cliches: *«شایان ذکر است که»*, *«در این راستا»*, *«delve into»*, *«tapestry»*, *«beacon»*.
    - Replaces passive verbosity with energetic academic verbs (*«واکاوی نمود»*, *«تبیین گردید»*, *«نشان داد»*).
    - Balances sentence lengths (cadence index: alternating 15-word short declarative statements with 30-word complex analytical propositions).
- **Output**: Tone-cleansed manuscript with verified scholarly authenticity.

### Step 4: Evidence Auditor Subagent (Deep Paraphrasing & Irandoc/iThenticate Clearance)
- **Agent**: `evidence-auditor` (wielding `irandoc-plagiarism-reducer`)
- **Action**:
  - Applies deep structural paraphrasing to theoretical and literature review paragraphs:
    - Protects native citation tags `(Hayes et al., 2019)` and `<m:oMath>` equations via entity shielding.
    - Employs syntactic voice inversion, academic synonym transformation, and Persian half-space (`\u200c`) normalization.
    - Estimates similarity reduction, ensuring predicted Irandoc / iThenticate similarity remains strictly below 15%.
  - Verifies 100% bidirectional concordance between in-text citations and the reference list.
- **Output**: Plagiarism-cleared manuscript text with audit certificate.

### Step 5: Submission Assistant Subagent (Editorial Collateral Packaging)
- **Agent**: `journal-assistant` (wielding `journal-submission-assistant`)
- **Action**:
  - Compiles standard journal submission collateral:
    1. **Cover Letter**: Addressed to Editor-in-Chief highlighting paper novelty, alignment with journal aims & scope, confirmation of non-concurrent submission, and suggested peer reviewers.
    2. **Title Page**: Complete author list, academic affiliations, email addresses, ORCID IDs, corresponding author details, and 14 CRediT authorship taxonomy roles.
    3. **Highlights**: Exactly 3 to 5 core bullet points, strictly validated to $\le 85$ characters per bullet including spaces.
    4. **Data Availability & Ethics Declarations**: Compliant with standard ICMJE / COPE ethical statements.
    5. **R&R Rebuttal Table**: Formats point-by-point response template for Revise & Resubmit decisions.
- **Output**: `Cover_Letter_Editor.docx`, `Title_Page_CRediT.docx`, `Highlights_and_Abstract.docx`.

### Step 6: Final Judge Subagent (Peer-Review & Desk Review Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Simulates the Editor-in-Chief desk review:
    - Evaluates Aims & Scope alignment.
    - Evaluates method rigor and effect size reporting.
    - Anticipates peer-reviewer methodological challenges (e.g. self-report bias, non-random sampling, missing follow-up).
  - Calculates Overall Journal Acceptance Probability Index (0–100%).
- **Output**: Peer-review simulator verdict and pre-submission audit score.

### Step 7: Digital Saber Human Gate Sign-Off (Admin Desk ID: 124911145)
- **Agent**: `digital-saber`
- **Action**:
  - Generates Admin Desk card for Saber Ghaderi (`124911145`).
  - Logs execution in `.agents/memory/decisions/dec_*.json` via `decision_journal_engine.py`.
  - Holds final client delivery pending one-click approval (`/approve_P301`).
- **Output**: Final verified journal submission package ready for editorial portal upload.

---

## Deliverables Checklist

| # | Artifact | Description | Target Path |
|---|---|---|---|
| 1 | **`مقاله_علمی_پژوهشی.docx` / `Manuscript_Main_Text.docx`** | Complete 5,000–6,500 word publication manuscript with abstract, introduction, methods, results (APA 7 tables), and discussion. | `output/` |
| 2 | **`Cover_Letter_Editor.docx`** | Formal, courteous Cover Letter to the Editor-in-Chief highlighting paper novelty and ethical declarations. | `output/` |
| 3 | **`Title_Page_CRediT.docx`** | Separate title page with author affiliations, corresponding author details, and 14 standard CRediT authorship taxonomy roles. | `output/` |
| 4 | **`Highlights_and_Abstract.docx`** | 3–5 bullet point highlights strictly validated to $\le 85$ characters, plus bilingual abstracts. | `output/` |
| 5 | **`submission_manifest.json`** | Machine-readable submission metadata (word counts, author taxonomy, similarity scores, readiness index). | `output/` |
