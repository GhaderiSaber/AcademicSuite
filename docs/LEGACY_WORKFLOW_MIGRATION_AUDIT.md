# Architectural Audit & Classification: Legacy Workflows Migration

This audit document fulfills **Phase 16 — Migrate / Deprecate the Old System**, classifying every legacy workflow in `.agents/workflows/` into its proper modern construct (**Skill**, **Rule**, **Agent Responsibility**, **Reusable Script**, or **Validation Rule**) and verifying that all capabilities are preserved, modernized, and tested.

---

## 1. Executive Summary: Legacy Workflows vs. Academic Suite v2

| Legacy Workflow File | Status in Academic Suite v2 | Target Skill(s) | Target Agent(s) | Target Validator / Rule | Reusable Script(s) |
|:---|:---:|:---|:---|:---|:---|
| **`chapter2_literature.md`** | **Migrated** | `literature-harvester`, `bibliometric-network-analyst`, `citation-network-visualizer`, `persian-literature-review-builder` | `literature-expert`, `academic-writer` | `thesis-integrity-auditor`, Directive 14 & 15 | `openxml_artifact_engine.py` |
| **`chapter4.md`** | **Migrated** | `chapter-4-writing`, `data-audit`, `descriptive-statistics`, `reliability-analysis`, `regression`, `mediation`, `sem`, `cfa` | `data-agent`, `statistics-agent`, `results-auditor`, `statistical-auditor` | `validators/reporting_consistency/`, `validators/numerical_consistency/`, Directive 3 & 4 | `build_hypothesis_1_triad_docx.py`, `build_sem_triad_docx.py`, `build_experimental_triad_docx.py` |
| **`chapter5.md`** | **Migrated** | `persian-discussion-builder`, `chapter5` | `literature-expert`, `methodology-expert`, `academic-writer` | `thesis-integrity-auditor`, Directive 13 | `openxml_artifact_engine.py` |
| **`defense_presentation.md`** | **Migrated** | `persian-defense-presentation-builder`, `defense_presentation` | `final-judge`, `academic-writer` | `thesis-integrity-auditor`, Directive 4.1 | `compile_defense_presentation.py`, `build_experimental_triad_docx.py` |
| **`intervention_protocol.md`** | **Migrated** | `psychological-intervention-protocol-builder`, `intervention_protocol` | `intervention-designer`, `methodology-expert` | `methodology-review`, Directive 3 | `openxml_artifact_engine.py` |
| **`journal_submission.md`** | **Migrated** | `academic-article-writer`, `journal-submission-assistant`, `irandoc-plagiarism-reducer` | `journal-strategist`, `evidence-auditor` | `validators/reporting_consistency/`, Directive 16 | `generate_apa_docx.py` |
| **`proposal.md`** | **Migrated** | `persian-proposal-builder`, `gpower-sample-size-calculator`, `psychometric-scale-resolver` | `methodology-expert`, `statistical-expert` | `validators/reporting_consistency/`, Directive 7 | `proposal_price_estimator.py` |
| **`scale_validation.md`** | **Migrated** | `scale_validation`, `psychometric-scale-validator`, `cfa` | `psychometric-expert`, `statistical-auditor` | `validators/statistical_assumptions/`, Directive 3 | `run_cfa.py`, `run_item_analysis.py` |
| **`thesis_assembly.md`** | **Migrated** | `persian-thesis-builder`, `thesis_assembly`, `persian-academic-translation` | `digital-saber`, `final-judge` | `thesis-integrity-auditor`, Directive 5 | `openxml_artifact_engine.py` |
| **`thesis_revision.md`** | **Migrated** | `persian-thesis-revision-assistant`, `thesis_revision` | `digital-saber`, `final-judge` | `validators/reporting_consistency/` | `openxml_artifact_engine.py` |

---

## 2. Granular 5-Layer Classification of Each Legacy Workflow

### 1. `chapter2_literature`
- **What was the legacy workflow doing?** Monolithically searching databases, plotting VOSviewer networks, extracting empirical parameters, and drafting literature review text.
- **Classification breakdown**:
  - **Skill (Deterministic Tools & Procedures)**:
    - `literature-harvester`: Automated API querying of PubMed, CrossRef, and Iranian portals.
    - `bibliometric-network-analyst`: Louvain clustering, Bradford/Lotka laws, and Callon strategic diagrams.
    - `citation-network-visualizer`: HistCite chronomaps and Garfield Main Path Analysis.
    - `persian-literature-review-builder`: Scaffolding of inverted-triangle theoretical background.
  - **Rule (Constitutional Invariant)**:
    - `Directive 3`: Stages 2.1 to 2.8 micro-stage triad generation (`.docx`, `.md`, `.json`).
    - `Directive 14`: Anti-Hallucination & Zero Ghost Citations protocol.
    - `Directive 15`: Temporal reality anchor (2021–2026 / ۱۴۰۰–۱۴۰۵).
  - **Agent Responsibility (Persistent Cognitive Role)**:
    - `literature-expert`: Epistemic evidence weighting and theoretical mechanism synthesis.
    - `academic-writer`: Iranian academic rhetoric and 5-part epistemic paragraph formulation.
  - **Reusable Script**:
    - `.agents/skills/bibliometric-network-analyst/scripts/run_bibliometrics.py`
    - `openxml_artifact_engine.py`
  - **Validation Rule**:
    - `validators/reporting_consistency/validator.py`: Verifies zero AI clichés and in-text citation format.

---

### 2. `chapter4`
- **What was the legacy workflow doing?** Attempting to execute data curation, assumption checking, inferential modeling, and narrative drafting in a single monolithic prompt.
- **Classification breakdown**:
  - **Skill**:
    - `chapter-4-writing`: Dedicated micro-stage orchestration for Chapter 4 findings.
    - `data-audit`: Screening unengaged responses and multivariate outliers ($D^2$).
    - `descriptive-statistics`: Sample parameters ($M, SD, SE, \text{Skew}, \text{Kurt}$).
    - `reliability-analysis`: Scale Cronbach's $\alpha$ and McDonald's $\omega$.
    - `regression`, `mediation`, `moderation`, `sem`, `cfa`: Exact statistical models.
    - `apa-reporting`: Strict APA 7 3-line tables.
  - **Rule**:
    - `Directive 3`: The **One-Hypothesis-One-Stage Invariant** (each hypothesis gets a dedicated stage) + **Triad Artifact Invariant** (`.docx`, `.md`, `.json`).
    - `Directive 4`: Strict APA 7 typography, Persian leading zero (`۰.۰۰۱ > p`, `۰.۰۵`), standard dot (`.`).
    - `Directive 9`: Realistic empirical decimal noise in psychometric data.
  - **Agent Responsibility**:
    - `data-agent`: Ingestion, data dictionary, and data cleaning.
    - `statistics-agent`: Deterministic model execution and results extraction.
    - `statistical-auditor`: Adversarial assumption and degrees of freedom auditing.
    - `results-auditor`: APA 7 typography and OMML preservation gatekeeper.
    - `writing-agent`: Authentic academic Persian results drafting.
  - **Reusable Script**:
    - `scripts/build_hypothesis_1_triad_docx.py`
    - `scripts/build_sem_triad_docx.py`
    - `scripts/build_experimental_triad_docx.py`
  - **Validation Rule**:
    - `validators/data_integrity/validator.py`
    - `validators/numerical_consistency/validator.py`
    - `validators/reporting_consistency/validator.py`
    - `validators/result_consistency/validator.py`

---

### 3. `chapter5`
- **What was the legacy workflow doing?** Drafting Chapter 5 discussion while mixing hypothesis status checking, literature concordance, and practical implications in one shot.
- **Classification breakdown**:
  - **Skill**:
    - `persian-discussion-builder`: Dedicated Chapter 5 micro-stage sequence (Stages 5.1 to 5.7).
  - **Rule**:
    - `Directive 3`: One-Hypothesis-One-Stage deep discussion triads.
    - `Directive 13`: Epistemic honesty on non-significant findings ($p > .05$).
  - **Agent Responsibility**:
    - `literature-expert`: Concordance mapping against recent empirical literature (2021–2026).
    - `methodology-expert`: Methodological, sampling, and instrument limitation dissection.
    - `academic-writer`: Psychological mechanism formulation (Beck, Hayes, Bandura).
  - **Reusable Script**:
    - `scripts/build_discussion_triad_docx.py` (or `openxml_artifact_engine.py`).
  - **Validation Rule**:
    - `validators/reporting_consistency/validator.py`: Enforcing authentic academic tone and absence of AI clichés.

---

### 4. `defense_presentation`
- **What was the legacy workflow doing?** Outlining slides and simulating oral defense in an unstructured text file.
- **Classification breakdown**:
  - **Skill**:
    - `persian-defense-presentation-builder`: Tri-path deck generator (`pptx`, `html`, `docx` speaker notes).
    - `defense_presentation`: Viva voce oral defense simulation.
  - **Rule**:
    - `Directive 4.1`: Presentation visual standards (Zero emojis, zero English words in Persian slides, widescreen 16:9, native RTL SmartArt).
    - `Directive 11`: Human Gate Admin Desk approval card (`124911145`).
  - **Agent Responsibility**:
    - `final-judge`: Simulates skeptical external examiner with 4–20 targeted hostile questions.
    - `academic-writer`: Formulates high-confidence literature-grounded candidate responses.
  - **Reusable Script**:
    - `scripts/compile_defense_presentation.py`
    - `scripts/build_experimental_triad_docx.py defense ...`
  - **Validation Rule**:
    - `validators/thesis-integrity-auditor/`: Verification of degrees of freedom, sample sizes, and slide timing.

---

### 5. `intervention_protocol`
- **What was the legacy workflow doing?** Creating clinical treatment manuals in text without standardized session templates.
- **Classification breakdown**:
  - **Skill**:
    - `psychological-intervention-protocol-builder`: Standardized 8–12 session manual architecture (ACT, CBT, Schema, MBSR).
  - **Rule**:
    - `Directive 3`: Methodological session triad (Rationale, Session Objectives, Homework Worksheets).
  - **Agent Responsibility**:
    - `intervention-designer`: Clinical intervention manual architect.
    - `methodology-expert`: CONSORT 2010 flow diagram and clinical fidelity safeguards.
  - **Reusable Script**:
    - `openxml_artifact_engine.py`
  - **Validation Rule**:
    - `methodology-review`: Fidelity and clinical safety screening.

---

### 6. `journal_submission`
- **What was the legacy workflow doing?** Converting theses to articles without target journal guidelines, CRediT authorship roles, or anti-plagiarism filters.
- **Classification breakdown**:
  - **Skill**:
    - `academic-article-writer`: 5,000-word IMRaD manuscript extraction.
    - `journal-submission-assistant`: Journal matching, cover letters, and CRediT roles.
    - `irandoc-plagiarism-reducer`: Paraphrasing and similarity index reduction ($< 15\%$).
  - **Rule**:
    - `Directive 16`: EndNote CWYW compatibility (`.enw`, `.ris`, native Word `ADDIN EN.CITE`).
  - **Agent Responsibility**:
    - `journal-strategist`: WoS/Scopus/ISC journal selection and reviewer rebuttal strategy.
    - `evidence-auditor`: Irandoc similarity compliance and citation integrity.
  - **Reusable Script**:
    - `generate_apa_docx.py`
  - **Validation Rule**:
    - `validators/reporting_consistency/validator.py`: Enforcing journal word counts and abstract structures.

---

### 7. `proposal`
- **What was the legacy workflow doing?** General proposal drafting without psychometric questionnaire linkage or deterministic pricing.
- **Classification breakdown**:
  - **Skill**:
    - `persian-proposal-builder`: Structured research proposal scaffolding (Stages P.1 to P.8).
    - `gpower-sample-size-calculator`: Statistical power calculation ($1 - \beta = .80, \alpha = .05$).
    - `psychometric-scale-resolver`: Automatic lookup in 4,880 validated instruments.
  - **Rule**:
    - `Directive 7`: Deterministic pricing in Tomans based on methodology and instruments.
  - **Agent Responsibility**:
    - `methodology-expert`: G*Power sample size justification and threat mitigation.
    - `academic-writer`: Problem statement formulation (inverted-triangle model).
  - **Reusable Script**:
    - `proposal_price_estimator.py`
  - **Validation Rule**:
    - `validators/reporting_consistency/validator.py`: Checking hypothesis directional formulation.

---

### 8. `scale_validation`
- **What was the legacy workflow doing?** Running scale validation in ad-hoc steps without micro-stage checkpoints.
- **Classification breakdown**:
  - **Skill**:
    - `psychometric-scale-validator`: Comprehensive psychometrics (CVR/CVI $\to$ Item Analysis $\to$ EFA $\to$ CFA $\to$ Invariance $\to$ IRT $\to$ ROC).
    - `cfa`: Confirmatory Factor Analysis measurement modeling.
  - **Rule**:
    - `Directive 3`: Stages V.1 to V.9 micro-stage sequence with synchronized triads.
  - **Agent Responsibility**:
    - `psychometric-expert`: Psychometric auditor for CTT, IRT (Samejima GRM), and ROC.
  - **Reusable Script**:
    - `.agents/skills/cfa/scripts/run_cfa.py`
    - `scripts/build_scale_validation_triad_docx.py`
  - **Validation Rule**:
    - `validators/numerical_consistency/validator.py`: Checking factor loading thresholds ($\lambda \ge 0.40$) and fit indices.

---

### 9. `thesis_assembly`
- **What was the legacy workflow doing?** Concatenating chapters without OpenXML typography preservation or BiDi enforcement.
- **Classification breakdown**:
  - **Skill**:
    - `persian-thesis-builder`: Master thesis compiler with bilingual front matter.
    - `persian-academic-translation`: Translating abstracts and titles into authentic English/Persian.
  - **Rule**:
    - `Directive 5`: Persian Academic Typography & OpenXML Standards (BiDi `<w:bidi/>`, `B Nazanin` 13–14 pt, `B Titr` 12–18 pt, OMML Math `<m:oMath>`).
    - `Directive 6`: Universal English-only ASCII filenames.
  - **Agent Responsibility**:
    - `digital-saber`: Master thesis quality and defense readiness sign-off.
  - **Reusable Script**:
    - `openxml_artifact_engine.py`
  - **Validation Rule**:
    - `thesis-integrity-auditor`: Forensic cross-chapter alignment (Ch 1 vs Ch 4 vs Ch 5).

---

### 10. `thesis_revision`
- **What was the legacy workflow doing?** Unstructured editing of defense committee feedback.
- **Classification breakdown**:
  - **Skill**:
    - `persian-thesis-revision-assistant`: Point-by-point response tables and Word track changes.
  - **Rule**:
    - `Directive 11`: Human-in-the-loop gate before delivering revisions to supervisors.
  - **Agent Responsibility**:
    - `final-judge`: Examiner critique triaging and defensive argumentation.
  - **Reusable Script**:
    - `openxml_artifact_engine.py`
  - **Validation Rule**:
    - `validators/reporting_consistency/validator.py`: Point-by-point concordance verification.

---

## 3. Deprecation & Cleanup Verification

1. **Active Skills in Production**: All 10 legacy workflows have been fully decomposed, upgraded, and distributed across 37 specialized skills in `.agents/skills/`.
2. **Subagents & Cognitive Roles**: All 15 persistent roles in `.agents/agents/` carry the precise cognitive mandates originally outlined in the legacy workflows.
3. **Automated Validators**: The deterministic validation suite in `validators/` mechanically enforces every rule and invariant that was previously an unenforced text suggestion in legacy workflows.
4. **Permanent Test Suite**: The Phase 14 Permanent Evaluation Suite (`evals/`) and Phase 15 Failure Recovery Engine (`recovery/`) guarantee regression-free execution across all domains.
5. **Safe Archival**: The legacy `.md.bak` files in `.agents/workflows/` have served their transitional purpose and are safely archived. No active `.md` workflow files remain in the runtime path.
