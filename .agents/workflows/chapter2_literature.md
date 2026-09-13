# Chapter 2 End-to-End Orchestration Workflow (فصل دوم: مبانی نظری، پیشینه پژوهش و نقشه‌نگاری دانش)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for multi-database literature harvesting, scientometric science mapping (VOSviewer), algorithmic historiography (HistCite chronomaps), empirical parameter extraction, and OpenXML compilation for **Chapter 2: Theoretical Foundations & Literature Review** in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                     Research Topic / Variables / Domain
                     Search Strings / Databases (PubMed, SID, etc.)
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │    STEP 1: DIGITAL SABER     │
                        │   Master Precedent Retrieval │
                        │  (Case Memory Search & Brief)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 2: LITERATURE EXPERT  │
                        │ Multi-Database Harvesting &  │
                        │ Parameter Extraction (N, Des)│
                        │    (literature-harvester)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 3: BIBLIOMETRIC EXPERT │
                        │ VOSviewer Keyword Mapping,   │
                        │ Bradford/Lotka, Callon 4-Quad│
                        │(bibliometric-network-analyst)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 4: CITATION EXPERT    │
                        │ HistCite Chronomap & Garfield│
                        │ Main Path Analysis (MPA)     │
                        │(citation-network-visualizer) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 5: EVIDENCE AUDITOR   │
                        │ Bidirectional APA 7 Matching,│
                        │ Plagiarism & Ref Extraction  │
                        │(academic-reference-extractor)│
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STEP 6: ACADEMIC WRITER    │
                        │ 5-Part Epistemic Paragraphs  │
                        │ OpenXML BiDi Chapter 2 DOCX  │
                        │(persian-literature-builder)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │     STEP 7: FINAL JUDGE      │
                        │ Literature Gap & Viva Voce   │
                        │ Simulation (Readiness 0-100) │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │  STEP 8: SABER HUMAN GATE    │
                        │ Admin Desk Approval Card     │
                        │     (ID: 124911145)          │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • فصل_دوم_پیشینه_پژوهش.docx
               • bibliometric_network_map.png & thematic_strategic_map.png
               • citation_chronomap.png & main_path_trajectory.png
               • literature_references.ris & .enw
               • literature_synthesis.json
```

---

## Prerequisites & Required Inputs

- **Research Specification**:
  - Research Topic & Title (Persian & English).
  - Identified Variables (Independent, Dependent, Mediators, Moderators, Covariates).
  - Target Population (Clinical, Students, Industrial/Organizational, General).
- **Optional Inputs**:
  - Seed bibliography file (`.bib`, `.ris`, `.txt`, `.docx`).
  - Specific theoretical models to prioritize (e.g., Beck's Cognitive Model, Hayes' Relational Frame Theory / ACT Hexaflex, Gross' Emotion Regulation, Bowlby's Attachment Theory).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Master Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests research topic and constructs.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve the top historical precedents sharing similar constructs and theoretical foundations.
  - Generates the literature scoping matrix with bilingual query tokens.
  - Initializes project tracking in `.agents/memory/decision_journal_engine.py`.
- **Output**: Literature project scoping ledger.

### Step 2: Literature Expert Subagent (Multi-Database Harvesting & Parameter Extraction)
- **Agent**: `literature-expert`
- **Action**:
  - Activates `.agents/skills/literature-harvester/`.
  - Executes multi-database search across PubMed / NCBI Entrez, CrossRef, Semantic Scholar, SID.ir, and Magiran.
  - Runs `EmpiricalParameterExtractor` to parse:
    - Sample sizes ($N$) and populations.
    - Research designs (RCT, Quasi-Experimental, SEM, Correlational).
    - Measurement instruments (standardized psychometric questionnaires).
    - Key statistical findings and effect directions.
- **Output**: `literature_harvested.json` and 4-sheet Excel matrix (`ماتریس_پیشینه_پژوهش.xlsx`).

### Step 3: Bibliometric Expert Subagent (VOSviewer Science Mapping & Thematic Clusters)
- **Agent**: `literature-expert` (wielding `bibliometric-network-analyst`)
- **Action**:
  - Runs `bibliometric_engine.py` on the harvested dataset.
  - Computes:
    - Keyword co-occurrence network and NetworkX centrality metrics (Degree, Betweenness, Closeness).
    - Bradford's Law journal scattering (Core Zone 1, Zone 2, Zone 3).
    - Lotka's Law author productivity coefficient.
    - Callon's 4-Quadrant Strategic Diagram (Motor Themes, Niche Themes, Emerging/Declining Themes, Basic/Transversal Themes).
  - Exports native VOSviewer files (`vosviewer_map.txt`, `vosviewer_network.txt`).
  - Generates 300-DPI visual figures: `bibliometric_network_map.png` and `thematic_strategic_map.png`.
- **Output**: Visual science maps and `bibliometric_summary.json`.

### Step 4: Citation Network Expert Subagent (HistCite Chronomap & Main Path Analysis)
- **Agent**: `literature-expert` (wielding `citation-network-visualizer`)
- **Action**:
  - Runs `citation_visualizer_engine.py`.
  - Calculates Eugene Garfield's Local Citation Score (LCS) vs Global Citation Score (GCS).
  - Performs Hummon & Doreian's (1989) Main Path Analysis (MPA) using Search Path Count (SPC) algorithms.
  - Generates chronological citation graph (chronomap) tracing paradigm shifts from seminal theoretical foundations to contemporary empirical trials.
  - Generates 300-DPI visual figures: `citation_chronomap.png` and `main_path_trajectory.png`.
- **Output**: Historical citation chronomap and `citation_summary.json`.

### Step 5: Evidence Auditor Subagent (APA 7 Bidirectional Matching & Reference Packaging)
- **Agent**: `evidence-auditor` (wielding `academic-reference-extractor`)
- **Action**:
  - Runs `extract_section_references.py` to match all cited works against the master bibliography.
  - Resolves DOIs, missing publisher metadata, and volume/issue numbers.
  - Formats citations strictly according to APA 7th Edition rules (Rule 3).
  - Produces standard reference packages for reference managers:
    - EndNote library format (`literature_references.enw`).
    - Zotero / Mendeley format (`literature_references.ris`).
    - Clean text bibliography (`literature_references.txt`).
- **Output**: Verified reference bundles and audit clearance.

### Step 6: Academic Writer Subagent (5-Part Formula Narrative & OpenXML DOCX Compilation)
- **Agent**: `academic-writer` (wielding `persian-literature-review-builder`)
- **Action**:
  - Assembles the complete Chapter 2 narrative following Saber Ghaderi's **5-Part Epistemic Chain**:
    1. **Context & Objective**: *هدف پژوهشگر(ان) و پیوند با مبانی نظری*.
    2. **Sample & Target Population**: *جامعه آماری و حجم نمونه ($N$)*.
    3. **Methodology & Design**: *طرح پژوهش (پیش‌آزمون-پس‌آزمون، کوواریانس، معادلات ساختاری)*.
    4. **Psychometric Instruments**: *ابزارهای سنجش و پرسشنامه‌های استاندارد*.
    5. **Empirical Findings & Effect**: *یافته‌های تجربی و جهت‌گیری آماری نتایج*.
  - Compiles Word document with OpenXML BiDi RTL standards:
    - `<w:bidi w:val="1"/>` on all paragraphs and `<w:bidiVisual/>` on tables.
    - True font binding (`Times New Roman` for Latin/numbers, `B Nazanin` for body, `B Titr` for headings).
    - Preserved native OMML equations (`<m:oMath>`) and zero vertical borders on APA 7 tables.
    - Persian half-spaces (نیم‌فاصله: `\u200c`) in all compound words.
- **Output**: `Chapter_2_Literature_Review.docx`.

### Step 7: Final Judge Subagent (Viva Voce Literature Defense Simulation)
- **Agent**: `final-judge`
- **Action**:
  - Simulates the external defense examiner questioning:
    - *Theoretical Gap*: Why does the empirical evidence warrant this specific study?
    - *Methodological Precedent*: How does the chosen sample size ($N$) align with literature benchmarks?
    - *Contradictory Findings*: How are divergent findings in prior literature accounted for?
  - Scores Literature Defense Readiness on 100-point scale (Methodological Coverage, Theoretical Integration, Bibliographic Accuracy, BiDi Compliance).
- **Output**: Defense examination card and readiness assessment.

### Step 8: Digital Saber Human-in-the-Loop Sign-Off (Admin Desk ID: 124911145)
- **Agent**: `digital-saber`
- **Action**:
  - Generates the Admin Desk summary card for Saber Ghaderi (`124911145`).
  - Appends record to `.agents/memory/decisions/dec_*.json` via `decision_journal_engine.py`.
  - Holds final client delivery pending one-click approval (`/approve_L201`).
- **Output**: Final deliverable package ready for supervisor/client review.

---

## Deliverables Checklist

| # | Artifact | Description | Target Path |
|---|---|---|---|
| 1 | **`Chapter_2_Literature_Review.docx`** | Complete Chapter 2 thesis document with theoretical foundations, empirical review, and APA 7 table. | `output/` |
| 2 | **`bibliometric_network_map.png`** | 300-DPI VOSviewer keyword co-occurrence science mapping plot. | `output/` |
| 3 | **`thematic_strategic_map.png`** | 300-DPI Callon 4-quadrant strategic thematic diagram. | `output/` |
| 4 | **`citation_chronomap.png`** | 300-DPI HistCite chronological citation chronomap. | `output/` |
| 5 | **`main_path_trajectory.png`** | 300-DPI Hummon & Doreian Main Path Analysis intellectual trajectory plot. | `output/` |
| 6 | **`literature_references.ris`** | Standard RIS citation package for Zotero / Mendeley. | `output/` |
| 7 | **`literature_references.enw`** | Standard EndNote import citation package. | `output/` |
| 8 | **`literature_synthesis.json`** | Structured machine-readable empirical parameter ledger ($N$, designs, tools). | `output/` |
