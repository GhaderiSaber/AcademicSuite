# Chapter 5 End-to-End Orchestration Workflow (فصل پنجم: بحث و نتیجه‌گیری)

This workflow defines the **Antigravity-Native Multi-Agent Orchestration Sequence** for interpreting, theoretically grounding, auditing, and compiling **Chapter 5: Discussion & Conclusion** for graduate dissertations and master's theses in psychology, counseling, and behavioral sciences.

```text
                                     INPUT
                     Chapter 4 Results (stats_results.json)
                     Chapter 2 Theoretical Literature Review
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
                         │ STEP 2: STATISTICAL EXPERT│
                         │ Hypothesis Status Triage  │
                         │ (Confirmed vs. Rejected)  │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 3: LITERATURE EXPERT │
                         │ Empirical Concordance Map │
                         │ (Iranian & International) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │STEP 4: METHODOLOGY EXPERT │
                         │ Limitations & Implications│
                         │ (Internal/External Validity)
                         └─────────────┬─────────────┘
                                       │
                ┌──────────────────────┴──────────────────────┐
                ▼                                             ▼
  ┌───────────────────────────┐                 ┌───────────────────────────┐
  │   STEP 5: RESULTS QC      │                 │   STEP 6: EVIDENCE QC     │
  │     Results Auditor       │                 │     Evidence Auditor      │
  │  (APA 7 & Stats Fidelity) │                 │(Bidirectional Citations)  │
  └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                │                                             │
                └──────────────────────┬──────────────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │ STEP 7: ACADEMIC WRITER   │
                         │4-Element Discussion Model │
                         │ (فصل پنجم_بحث_نتیجه‌گیری) │
                         └─────────────┬─────────────┘
                                       │
                                       ▼
                         ┌───────────────────────────┐
                         │    STEP 8: FINAL JUDGE    │
                         │ Viva Voce Defense Sim     │
                         │ Approval Readiness (0-100)│
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
                               FINAL DELIVERABLE
```

---

## Prerequisites & Required Inputs

- **Quantitative Findings**: Verified `stats_results.json` or final `فصل چهارم: یافته‌های پژوهش.docx`.
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

### Step 7: Academic Writer Subagent (Drafting Chapter 5 in Academic Persian)
- **Agent**: `academic-writer`
- **Action**:
  - Synthesizes Chapter 5 into the standard 6-part Iranian university architecture:
    1. **۵-۱. مقدمه** (Brief recap of problem, research questions, and chapter roadmap).
    2. **۵-۲. بحث پیرامون یافته‌ها** (Hypothesis-by-hypothesis synthesis using the **4-Element Psychological Discussion Model**):
       - *عنصر ۱: بیان فرضیه و یافته آماری دقیق* (Test stat, $p$-value, effect size).
       - *عنصر ۲: مقایسه با پیشینه تجربی داخلی و خارجی* (Concordant & divergent studies).
       - *عنصر ۳: تبیین سازوکار روان‌شناختی و نظری* (Cognitive, behavioral, emotional, and neurobiological mechanisms via Beck, Bandura, Gross, Hayes, Bowlby, Gilbert).
       - *عنصر ۴: توجیه روش‌شناختی یافته‌های ناهمسو یا غیرمعنادار*.
    3. **۵-۳. پیامدهای کاربردی و بالینی** (Direct clinical and practical translations).
    4. **۵-۴. محدودیت‌های پژوهش** (Honest methodological boundaries).
    5. **۵-۵. پیشنهادهای پژوهش** (Rigidly partitioned into research vs. applied recommendations).
    6. **۵-۶. نتیجه‌گیری نهایی** (Holistic closing synthesis of scientific contribution).
  - Enforces Persian half-spaces (`\u200c`), natural sentence cadence ($CV \ge 0.50$), and OpenXML RTL typography (`B Nazanin` 13 pt, `B Titr` headings, Line spacing 1.25).
  - Compiles Word deliverable via `generate_chapter5_docx.py`.
- **Output**: `فصل پنجم: بحث و نتیجه‌گیری.docx`.

### Step 8: Final Judge Subagent (Defense Committee Viva Voce Simulator)
- **Agent**: `final-judge`
- **Action**:
  - Simulates external defense examiner challenges specifically scrutinizing the discussion:
    - *«چرا فرضیه سوم تأیید نشد و تبیین روان‌شناختی شما چیست؟»*
    - *«چگونه اثر ابزار خودگزارش‌دهی را از اثر واقعی مداخله تفکیک کردید؟»*
    - *«تفاوت تبیین نظری مدل شما با مدل‌های سنتی در چیست؟»*
  - Provides bulletproof APA 7 supported student answers.
  - Calculates Discussion Defense Readiness Index ($0\text{--}100\%$).
- **Output**: `defense_discussion_qa.docx` and readiness index.

### Step 9: Saber Human Gate Sign-off (Rule 11)
- **Agent**: `digital-saber`
- **Action**:
  - Transmits Admin Desk Approval Card to Saber (`124911145`):
    - Topic, Hypotheses Count, Confirmed/Rejected Breakdown.
    - Key Theoretical Mechanisms & Literature Concordance Summary.
    - Defense Readiness Index.
    - Interactive commands: `/approve_chapter5` or `/adjust_chapter5`.
  - Upon human sign-off, records completed decision in `decision_journal_engine.py` with status `RELEASED`.
