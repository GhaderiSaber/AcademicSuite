---
name: chapter2_literature
description: >-
  Multi-database literature harvesting, science mapping, Callon diagram clustering, and Chapter 2 theoretical framework synthesis.
---

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
                        │   STAGE 2.1: FOUNDATIONS     │
                        │ Theoretical & Definitions    │
                        │ (01_theoretical_found.docx)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE 2.2: BIBLIOMETRICS   │
                        │ Callon Strategic Map / Net   │
                        │ (02_bibliometrics.docx)      │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE 2.3: INTL STUDIES      │
                        │ Foreign Empirical Review     │
                        │ (03_intl_studies.docx)       │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE 2.4: IRANIAN STUDIES   │
                        │ Iranian Empirical Review     │
                        │ (04_iranian_studies.docx)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE 2.5: SYNTHESIS & MODEL │
                        │ Research Gap & Concept Model │
                        │ (05_synthesis_model.docx)    │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE 2.6: MATRIX TABLE      │
                        │ Comprehensive Empirical Table│
                        │ (06_literature_matrix.docx)  │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │ STAGE 2.7: CH 2 ASSEMBLY     │
                        │ OpenXML Section Assembly     │
                        │(Chapter_2_Lit_Review.docx)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────────┐
                        │   STAGE 2.8: FINAL JUDGE     │
                        │ Literature Gap Defense Sim   │
                        │(XX_lit_defense_brief.docx)   │
                        └──────────────┬───────────────┘
                                       │
                                       ▼
                              FINAL DELIVERABLES
               • Chapter_2_Literature_Review.docx
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

### Micro-Stage Execution Sequence & Anti-Shortcut Protocol (Directive 3 & 11)

To prevent shortcutting, Chapter 2 literature review drafting is strictly partitioned into independent micro-stages:

#### Stage 2.1: Theoretical Foundations & Conceptual Definitions
- **Agent**: `academic-writer`
- **Output**: `01_theoretical_foundations.docx` (Foundational theories, historical evolution, operational constructs).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.2: Bibliometrics & Callon Strategic Thematic Mapping
- **Agent**: `bibliometric-network-analyst`
- **Output**: `02_bibliometrics.docx` + `bibliometric_network_map.png` + `thematic_strategic_map.png`.
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.3: International Empirical Studies Review
- **Agent**: `literature-expert` + `academic-writer`
- **Output**: `03_intl_studies.docx` (Foreign studies structured with Saber's 5-Part Epistemic Chain).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.4: Iranian Empirical Studies Review
- **Agent**: `literature-expert` + `academic-writer`
- **Output**: `04_iranian_studies.docx` (Iranian domestic empirical research with 5-Part Epistemic Chain).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.5: Inverted-Triangle Synthesis, Research Gap & Conceptual Model
- **Agent**: `academic-writer`
- **Output**: `05_synthesis_model.docx` (Inverted-triangle synthesis, explicit empirical gaps, conceptual framework).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.6: Comprehensive Empirical Literature Matrix Table
- **Agent**: `literature-expert`
- **Output**: `06_literature_matrix.docx` + `empirical_literature_matrix.xlsx` (Full comparative table of studies).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.7: Chapter Assembly & OpenXML Merging
- **Agent**: Execution Layer via `orchestrator_cli.py --assemble-chapter Chapter_2_Literature_Review.docx`
- **Output**: `Chapter_2_Literature_Review.docx` (Concatenated from verified section documents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 2.8: Final Committee Defense Simulator
- **Agent**: `final-judge`
- **Output**: `XX_lit_defense_brief.docx` (Scrutiny on theoretical gaps, sample benchmarks, and divergent findings).
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

---

## Antigravity Multi-Agent Execution Architecture (Directive 12, 12.1 & PURE_ANTIGRAVITY_DELIBERATION_PROTOCOL)

1. **The Hands**: Deterministic tools (`literature_review_engine.py`, `extract_section_references.py`, `vosviewer_exporter.py`) run via CLI to harvest parameters, generate VOSviewer maps, extract RIS/ENW files, and compile OpenXML Word tables on disk.
2. **The Brains & Critics**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `literature-expert`: Harvests multi-database literature and synthesizes theoretical mechanisms.
   - `evidence-auditor`: Executes bidirectional citation matching and predicts Irandoc similarity ($< 20\%$).
   - `academic-writer`: Compiles the 5-part empirical chain narrative in pristine Persian typography.
   - `final-judge`: Simulates external defense committee scrutiny on theoretical gaps and methodology precedents.
3. **Sole Orchestrator**: Subagents and execution instruments are orchestrated directly and exclusively by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and the Critic-Generator Barrier.

