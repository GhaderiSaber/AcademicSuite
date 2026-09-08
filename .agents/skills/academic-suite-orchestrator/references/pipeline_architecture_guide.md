# AcademicSuite Pipeline Architecture & Inter-Skill Data Contracts Guide
## (راهنمای معماری پایپ‌لاین‌ها و قراردادهای تبادل داده میان مهارت‌های پژوهشی)

This guide documents the orchestration architecture, inter-skill data exchange contracts, and execution lifecycle for the **AcademicSuite Master Orchestrator**.

---

## 1. Architectural Overview & Design Philosophy

The AcademicSuite comprises 18 specialized, domain-tailored skills covering the complete academic research lifecycle in psychology, counseling, educational assessment, and behavioral sciences.

The **AcademicSuite Orchestrator (`academic-suite-orchestrator`)** serves as the **Master Automation Engine** (مهندس و فرمانده پایپ‌لاین‌های پژوهشی). It connects individual atomic skills into cohesive, automated, and reproducible research workflows.

```
                           [Project Config (JSON)]
                                      │
                                      ▼
                      [Master Orchestrator Engine]
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
 [Pipeline A: Thesis]     [Pipeline B: Validation]     [Pipeline C: Publishing]
  1. Proposal Builder      1. Translation               1. Thesis Ingestion
  2. Data Simulator        2. Scale Resolver            2. Plagiarism Reduction
  3. Statistical Analyst   3. Scale Validator (CTT/IRT) 3. Article Writer
  4. Discussion Builder    4. Article Writer            4. Submission Assistant
  5. Thesis Compiler       5. Submission Assistant
  6. Defense Slide Deck
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      ▼
                       [Centralized Outputs & Artifacts]
                       ├── orchestrator_manifest.json (Audit log & timestamps)
                       └── PROJECT_DASHBOARD.md (Executive summary & links)
```

---

## 2. Standard Built-In Turnkey Pipelines

### Pipeline 1: `thesis_empirical` (Full Empirical Thesis & Defense)
* **Goal**: Conducts a complete quantitative/empirical graduate thesis from proposal to defense presentation.
* **Execution Sequence**:
  1. **`proposal` (`persian-proposal-builder`)**: Compiles problem statement, directional hypotheses, G*Power sample size calculation, Chapter 1, and Chapter 3 methodology.
  2. **`simulation` (`psychometric-data-simulator`)**: Generates realistic Monte Carlo response data (`.xlsx`, `.csv`) and executable R `lavaan` script based on the proposed model.
  3. **`statistics` (`statistical-data-analyst`)**: Ingests dataset, verifies assumptions, executes hypothesis tests (ANCOVA, regression, mediation), and produces Chapter 4 Word report + `stats_results.json`.
  4. **`discussion` (`persian-discussion-builder`)**: Ingests `stats_results.json`, evaluates confirmed/rejected hypotheses, explains psychological mechanisms (Beck, Bandura, Gross, etc.), limitations, and implications into Chapter 5 (`.docx`).
  5. **`thesis` (`persian-thesis-builder`)**: Fuses institutional template with Proposal (Ch 1/3), Literature Review (Ch 2), Statistics (Ch 4), Discussion (Ch 5), and References into the complete thesis (`.docx`).
  6. **`defense` (`persian-defense-presentation-builder`)**: Ingests the compiled thesis and generates defense slide deck (`.pptx`) with RTL OpenXML and candidate oral Speaker Notes.

---

### Pipeline 2: `scale_validation` (Psychometric Standardization & Publishing)
* **Goal**: Adapts, translates, standardizes, and validates a psychological instrument using CTT and IRT, preparing a journal publication.
* **Execution Sequence**:
  1. **`translation` (`persian-academic-translation`)**: Forward-backward translation and semantic equivalence verification.
  2. **`scale_lookup` (`psychometric-scale-resolver`)**: Extracts subscale structures and scoring formulas from master questionnaires registry (`Questionnaires.xlsx`).
  3. **`validation` (`psychometric-scale-validator`)**: Computes Lawshe CVR, Waltz CVI, EFA/CFA, McDonald's omega, Item Response Theory (IRT: Samejima GRM, TIF, DIF), Norms, and ROC Curve cut-offs. Generates Chapter 4 (`.docx`), 6-sheet Excel matrix, and dual 300-DPI plots.
  4. **`article` (`academic-article-writer`)**: Converts validation findings into an APA 7 journal manuscript (`.docx`) for ISI/Scopus or ISC.
  5. **`submission` (`journal-submission-assistant`)**: Compiles submission package: Cover Letter, Title Page (14 CRediT roles), Highlights ($\le 85$ chars), and declarations.

---

### Pipeline 3: `qualitative_study` (Qualitative Research & Grounded Theory)
* **Goal**: Conducts interview coding, thematic network extraction, model construction, and thesis compilation for qualitative research.
* **Execution Sequence**:
  1. **`proposal` (`persian-proposal-builder`)**: Qualitative inquiry framing and phenomenological/grounded theory design.
  2. **`qualitative_analysis` (`qualitative-data-analyst`)**: Braun & Clarke Reflexive Thematic Analysis or Strauss & Corbin Grounded Theory Paradigmatic Model. Generates Chapter 4 (`.docx`), 5-sheet coding matrix, and 300-DPI network diagram.
  3. **`discussion` (`persian-discussion-builder`)**: Qualitative synthesis and conceptual grounded model discussion.
  4. **`thesis` (`persian-thesis-builder`)**: Assembles complete qualitative dissertation.
  5. **`defense` (`persian-defense-presentation-builder`)**: Compiles qualitative defense presentation.

---

### Pipeline 4: `meta_analysis` (PRISMA 2020 Systematic Review & Meta-Analysis)
* **Goal**: Executes quantitative meta-analysis and prepares a publication manuscript.
* **Execution Sequence**:
  1. **`meta_analysis` (`systematic-review-meta-analyst`)**: PRISMA 2020 protocol, Cochrane RoB 2, Hedges' $g$, pooled effects (Fixed/Random), heterogeneity ($Q, I^2, \tau^2$), Egger's test, Forest and Funnel plots.
  2. **`article` (`academic-article-writer`)**: Compiles systematic review manuscript in English or Persian.
  3. **`submission` (`journal-submission-assistant`)**: Produces Cover Letter, Title Page, Highlights, and PRISMA checklist.

---

### Pipeline 5: `thesis_to_publication` (Dissertation to Publication Package)
* **Goal**: Takes an existing thesis document, lowers similarity on Irandoc, drafts a journal paper, and packages submission collateral.
* **Execution Sequence**:
  1. **`plagiarism_reduction` (`irandoc-plagiarism-reducer`)**: Deep clause inversion and paraphrasing to lower Irandoc similarity below 20%.
  2. **`article` (`academic-article-writer`)**: Condenses the 100+ page thesis into a publication-ready 25-page IMRaD manuscript.
  3. **`submission` (`journal-submission-assistant`)**: Packages Editor-in-Chief Cover Letter, Title Page with CRediT taxonomy, Highlights, and Data Availability Statement.

---

## 3. Data Contracts & Intermediate Artifact Routing

The Orchestrator automatically handles state transfers between upstream and downstream skills:

| Upstream Producer | Produced Artifact | Downstream Consumer | Ingested Parameter / Role |
| :--- | :--- | :--- | :--- |
| `persian-proposal-builder` | `پروپوزال_تست.docx` | `persian-thesis-builder` | Supplies Chapter 1 problem statement & Chapter 3 methodology. |
| `psychometric-data-simulator` | `simulated_dataset.xlsx` | `statistical-data-analyst` | Primary raw empirical survey dataset (`--data`). |
| `statistical-data-analyst` | `stats_results.json` | `persian-discussion-builder` | Ingested via `--stats-json` to populate confirmed/rejected hypotheses. |
| `statistical-data-analyst` | `فصل_چهارم_یافته‌های_پژوهش.docx` | `persian-thesis-builder` | Ingested via `--ch4` in full thesis assembly. |
| `persian-discussion-builder` | `فصل_پنجم_تست.docx` | `persian-thesis-builder` | Ingested via `--ch5` in full thesis assembly. |
| `persian-thesis-builder` | `رساله_کامل.docx` | `persian-defense-presentation-builder` | Source document for defense slides and candidate speaker notes. |
| `persian-thesis-builder` | `رساله_کامل.docx` | `academic-article-writer` | Source document for condensing into journal article. |
| `academic-article-writer` | `مقاله_علمی_پژوهشی.docx` | `journal-submission-assistant` | Target manuscript for cover letter & highlights extraction. |

---

## 4. Execution Lifecycle & CLI Controls

1. **Validation & Dry-Run (`--dry-run`)**:
   - Parses the project configuration JSON.
   - Verifies the availability of all required skill engines (`scripts/*.py`).
   - Checks input file paths and dependencies.
   - Prints the visual DAG and execution schedule without running sub-processes.
2. **Sequential Step Execution**:
   - Each step is executed in an isolated sub-process with stdout/stderr capture and real-time terminal progress indicators.
   - Intermediate outputs are registered in the global execution context.
3. **Resilience & Checkpointing (`--resume-from <step>`)**:
   - If a step needs adjustments or fails, the user can resume the pipeline from that specific step without re-running earlier completed stages.
4. **Single-Step Execution (`--step <step>`)**:
   - Executes only one specified phase of the pipeline within the project context.
5. **Audit Logging & Reporting**:
   - Generates `orchestrator_manifest.json` containing timestamps, durations, exit codes, and output file paths.
   - Generates `PROJECT_DASHBOARD.md` providing an executive summary with clickable markdown links to all produced deliverables.
