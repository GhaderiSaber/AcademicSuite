---
name: chapter5
description: >-
  Epistemic synthesis, psychological mechanism explanation, empirical literature concordance, and Chapter 5 discussion drafting.
---

# Chapter 5 End-to-End Orchestration Workflow (فصل پنجم: بحث و نتیجه‌گیری)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for interpreting, theoretically grounding, auditing, and compiling **Chapter 5: Discussion & Conclusion** for graduate dissertations and master's theses in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                     Chapter 4 Results (stats_results.json)
                     Chapter 2 Theoretical Literature Review
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE 5.1: RECAP        │
                         │ Findings Overview & Recap │
                         │  (01_findings_recap.docx) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 5.2.1: HYPOTHESIS 1 │
                         │ Dedicated Deep Discussion │
                         │ (02_hypo_1_discussion)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 5.2.k: HYPOTHESIS k │
                         │ Dedicated Deep Discussion │
                         │ (XX_hypo_k_discussion)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STAGE 5.3: NON-SIGNIFICANT│
                         │ Epistemic Deep Dive       │
                         │(XX_non_significant.docx)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE 5.4: IMPLICATIONS │
                         │ Theoretical & Clinical    │
                         │   (XX_implications.docx)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │   STAGE 5.5: LIMITATIONS  │
                         │ Methodological Boundaries │
                         │   (XX_limitations.docx)   │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │STAGE 5.6: RECOMMENDATIONS │
                         │ Research & Actionable     │
                         │ (XX_recommendations.docx) │
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │   STAGE 5.7: RESULTS QC   │                 │   STAGE 5.8: EVIDENCE QC  │
  │     Results Auditor       │                 │     Evidence Auditor      │
  │  (APA 7 & Stats Fidelity) │                 │(Bidirectional Citations)  │
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 5.9: CH 5 ASSEMBLY │
                         │ OpenXML Section Assembly  │
                         │(Chapter_5_Discussion.docx)│
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │  STAGE 5.10: FINAL JUDGE  │
                         │ Viva Voce Defense Sim     │
                         │(XX_defense_brief.docx)    │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                               FINAL DELIVERABLE
```

---

## Prerequisites & Required Inputs

- **Quantitative Findings**: Verified `stats_results.json` or final `Chapter_4_Results.docx`.
- **Empirical & Theoretical Literature**: Chapter 2 citations and theoretical frameworks (CBT, ACT, EFT, Attachment, Schema Therapy, Self-Determination Theory).
- **Target Population & Context**: Exact sample characteristics (clinical, educational, organizational).

---

## Step-by-Step Subagent Execution Protocol

### Step 1: Digital Saber Master Project Lead (Scoping & Precedent Retrieval)
- **Agent**: `digital-saber`
- **Action**:
  - Ingests `stats_results.json` and research topic.
  - Queries `.agents/memory/case_memory_engine.py` to retrieve discussion precedents for similar construct relationships.
  - Initializes discussion tracking in `decision_journal_engine.py`.
- **Output**: Chapter 5 synthesis brief and precedent mechanism mappings.

### Step 2: Statistical Expert Subagent (Hypothesis Status Triage)
- **Agent**: `statistical-expert`
- **Action**:
  - Classifies each formal hypothesis as **Confirmed (تأییدشده)** or **Rejected / Non-significant (ردشده / عدم معناداری)**.
  - Tabulates exact inferential metrics: test statistics ($F, t, z$), exact $p$-values (strictly adhering to $p < .001$ and no leading zero), and effect sizes ($\eta_p^2, d, R^2, \beta$).
  - Evaluates clinical significance versus purely statistical significance.
- **Output**: `hypothesis_status_matrix.json`.

### Step 3: Literature Expert Subagent (Empirical Concordance Mapping)
- **Agent**: `literature-expert`
- **Action**:
  - Evaluates empirical concordance without cherry-picking:
    - Identifies 3–5 **concordant studies (پژوهش‌های همسو)** from both Iranian (SID.ir / Magiran) and international literature (PubMed / CrossRef).
    - Identifies **divergent/conflicting studies (پژوهش‌های ناهمسو)** and prepares theoretical explanations for divergence (differences in culture, dosage, baseline severity, or measurement instruments).
- **Output**: `literature_concordance_map.json`.

### Step 4: Methodology Expert Subagent (Validity Limitations & Implications)
- **Agent**: `methodology-expert`
- **Action**:
  - Outlines methodological limitations:
    - Non-random sampling or single-center constraints.
    - Self-report common method bias.
    - Lack of longitudinal follow-up (پیگیری).
  - Formulates practical implications across therapeutic, educational, and clinical settings.
  - Generates bifurcated recommendations:
    - **پیشنهادهای پژوهشی** (methodological & scientific directions for future scholars).
    - **پیشنهادهای کاربردی** (actionable protocols for practitioners, clinics, and policymakers).
- **Output**: `methodology_implications_and_limitations.json`.

### Step 5: Results QC Subagent (APA 7 & Chapter 4 Cross-Fidelity Audit)
- **Agent**: `results-auditor`
- **Action**:
  - Cross-checks all statistical numbers cited in the discussion narrative against Chapter 4 `stats_results.json`.
  - Verifies APA 7th Edition formatting: italicized symbols (*F, p, t, d*), leading zeros omitted ($p < .001, \eta_p^2 = .32$), and rounded to 2 decimal places (3 for $p$).
  - Ensures no mismatch between statistical direction and narrative interpretation.
- **Output**: `results_fidelity_report.json`.

### Step 6: Evidence QC Subagent (Bidirectional Citation & Plagiarism Audit)
- **Agent**: `evidence-auditor`
- **Action**:
  - Cross-verifies all in-text citations against the thesis master bibliography (zero orphaned citations).
  - Screens narrative for AI clichés (*«شایان ذکر است که»*, *«در این راستا»*, *«به عنوان یک هوش مصنوعی»*).
  - Ensures Irandoc similarity compliance ($< 20\%$).
- **Output**: `evidence_audit_report.json`.

### Micro-Stage Execution Sequence & Triad Artifact Invariant (Directive 3 & 11)

To prevent shortcutting, Chapter 5 discussion drafting is strictly partitioned into independent micro-stages. Monolithic execution is prohibited. **Triad Artifact Invariant**: Every stage generates `.docx` (APA 7 OpenXML), `.md` (Markdown narrative & tables), and `.json` (structured data/audit).

#### Stage 5.1: Problem Recap & Empirical Findings Summary
- **Agent**: `academic-writer`
- **Output**: `01_findings_recap.docx`, `01_findings_recap.md`, `01_findings_recap.json` (Problem overview, research questions roadmap, holistic summary of empirical outcomes).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.2.1: Hypothesis 1 Deep Discussion (One-Hypothesis-One-Stage Invariant)
- **Agent**: `academic-writer`
- **Output**: `02_hypothesis_1_discussion.docx`, `02_hypothesis_1_discussion.md`, `02_hypothesis_1_discussion.json` (The 4-Element Psychological Discussion Model: exact stats, Iranian/international empirical concordance, underlying cognitive/behavioral/neurobiological mechanisms via Beck/Hayes/Bandura/Gross, and methodological nuances).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.2.k: Hypothesis k Deep Discussion (Dedicated Independent Stages)
- **Agent**: `academic-writer`
- **Output**: `XX_hypothesis_k_discussion.docx`, `XX_hypothesis_k_discussion.md`, `XX_hypothesis_k_discussion.json` (Each subsequent hypothesis is analyzed and drafted in its own dedicated stage).
- **Stage-Gate**: Emit Completion Report and await user confirmation after each hypothesis.

#### Stage 5.3: Unexpected & Non-Significant Findings Epistemic Analysis
- **Agent**: `methodology-expert` + `academic-writer`
- **Output**: `XX_non_significant_findings.docx`, `XX_non_significant_findings.md`, `XX_non_significant_findings.json` (Deep epistemological dive into unconfirmed hypotheses or anomalous effect sizes).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.4: Theoretical, Clinical & Practical Implications
- **Agent**: `academic-writer`
- **Output**: `XX_implications.docx`, `XX_implications.md`, `XX_implications.json` (Actionable translational guidance for clinicians, organizations, educators, and theorists).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.5: Methodological & Sampling Limitations
- **Agent**: `academic-writer`
- **Output**: `XX_limitations.docx`, `XX_limitations.md`, `XX_limitations.json` (Candid appraisal of internal validity, sampling constraints, measurement artifacts, and generalizability boundaries).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.6: Future Research & Actionable Recommendations
- **Agent**: `academic-writer`
- **Output**: `XX_recommendations.docx`, `XX_recommendations.md`, `XX_recommendations.json` (Rigidly partitioned into research suggestions vs. practical/clinical recommendations).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.7: Results QC (APA 7 & Cross-Fidelity Audit)
- **Agent**: `results-auditor`
- **Output**: `XX_results_fidelity_report.json`, `XX_results_fidelity_report.md` (Cross-checks all numerical mentions against Chapter 4 results).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.8: Evidence QC (Bidirectional Citation & Plagiarism Audit)
- **Agent**: `evidence-auditor`
- **Output**: `XX_evidence_audit_report.json`, `XX_evidence_audit_report.md` (Zero orphaned citations, Irandoc similarity < 20%, elimination of AI clichés).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.9: Chapter Assembly & Merging
- **Agent**: Execution Layer via `orchestrator_cli.py --assemble-chapter Chapter_5_Discussion.docx`
- **Output**: `Chapter_5_Discussion.docx` + `Chapter_5_Discussion.md` (Concatenated from verified section documents).
- **Stage-Gate**: Emit Completion Report and await user confirmation.

#### Stage 5.10: Final Committee Defense Simulator
- **Agent**: `final-judge`
- **Output**: `XX_defense_discussion_brief.docx`, `XX_defense_discussion_brief.md`, `defense_readiness.json` (Examiner cross-examination questions & defense model answers).
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

1. **The Hands**: Deterministic tools (`generate_chapter5_docx.py`, `literature_concordance_engine.py`) run via CLI to compile OpenXML Word documents and map statistical findings to empirical literature.
2. **The Brains & Critics**: Antigravity subagents execute specialized cognitive roles via `invoke_subagent`:
   - `literature-expert`: Synthesizes theoretical mechanisms (Beck, Hayes, Bandura) and empirical literature concordance.
   - `methodology-expert`: Formulates methodological justifications for non-significant or divergent findings.
   - `academic-writer`: Drafts the 6-part chapter structure with natural sentence cadence ($CV \ge 0.50$).
   - `results-auditor`: Verifies that reported statistical parameters in narrative strictly match Chapter 4 results.
   - `final-judge`: Simulates viva voce oral defense cross-examination and scores discussion defense readiness.
3. **Sole Orchestrator**: Subagents and execution instruments are orchestrated directly and exclusively by the Antigravity Lead Agent in the conversation using `invoke_subagent`, enforcing physical artifact gates and the Critic-Generator Barrier.

