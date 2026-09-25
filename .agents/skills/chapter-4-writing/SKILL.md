---
name: chapter-4-writing
description: End-to-end orchestration for Chapter 4 findings, enforcing One-Hypothesis-One-Stage micro-stages, Triad Artifact Invariant (.docx, .md, .json), and Master Decision Matrix.
---

# Chapter 4 Writing Skill (تدوین فصل چهارم یافته‌های پژوهش)

This skill governs the end-to-end orchestration and scholarly drafting of Chapter 4 (Findings / یافته‌های پژوهش) in Persian graduate theses and dissertations, strictly enforcing micro-stage execution, the Triad Artifact Invariant (`.docx` + `.md` + `.json`), and institutional reporting standards.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Orchestrating or drafting Chapter 4 sections (Stages 4.0 through 4.12).
- Implementing the One-Hypothesis-One-Stage invariant for individual hypotheses or research questions.
- Generating synchronized triad deliverables (`.docx`, `.md`, `.json`) for empirical findings.
- Reporting Multiple Regression, Hierarchical Regression, SEM, ANCOVA, or mediation findings in APA 7.
- Formatting the Master Hypotheses Decision Matrix Table.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- Drafting Chapter 5 (Discussion & Conclusion) $\to$ use `chapter-5-writing` or `persian-discussion-builder`.
- Running raw computational scripts or statistical modeling $\to$ use `regression`, `sem`, or `statistical-data-analyst`.
- Conducting preliminary psychometric scale resolution or data cleaning $\to$ use `data-cleaning` or `data-audit`.

---

## 3. MICRO-STAGE PIPELINE ARCHITECTURE (Stages 4.0 to 4.12)
Chapter 4 execution strictly follows the 13-stage micro-stage sequence codified in `MICRO_STAGE_SEQUENCES.md`:
- **Stage 4.0**: Chapter Overview & Structural Introduction
- **Stage 4.1**: Data Quality Screening, Missing Data Diagnostics & Outlier Treatment
- **Stage 4.2**: Demographic Profiles & Frequency Distributions
- **Stage 4.3**: Univariate Descriptive Statistics ($M, SD$, Skewness, Kurtosis)
- **Stage 4.4**: Bivariate Pearson Correlation Matrix of Study Variables
- **Stage 4.5**: Parametric Assumptions Verification (Normality, Homogeneity, Linearity, Collinearity)
- **Stage 4.6 to 4.k**: Dedicated Individual Hypothesis Stages (One-Hypothesis-One-Stage)
- **Stage 4.11**: Master Hypotheses Decision Matrix & Summary Synthesis
- **Stage 4.12**: Chapter Concluding Summary & Final Triad Compilation

---

## 4. CORE INSTITUTIONAL INVARIANTS

### 4.1 Triad Artifact Invariant (اصل سه‌گانه مستندسازی)
Every micro-stage and hypothesis stage MUST produce a synchronized triad of physical files on disk before advancing:
1. **`.docx`**: Institutional Word deliverable with strict Persian typography (`B Nazanin` 13–14 pt, `B Titr` 12–18 pt, decoupled LTR numbers in `Times New Roman`).
2. **`.md`**: Scholarly Markdown narrative with clean APA 7 tables for immediate inspection and diffing.
3. **`.json`**: Exact statistical parameters, test statistics, and audit checklists.

### 4.2 One-Hypothesis-One-Stage Invariant (اصل یک فرضیه = یک مرحله مجزا)
Every individual research hypothesis or question must have its own dedicated, isolated micro-stage producing its own independent triad artifacts (e.g. `06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json`). Never lump multiple hypotheses into a single calculation or drafting step.

### 4.3 Strict Section Decoupling & Heading Isolation
- Each research question or hypothesis section must begin with clean Persian titles: `سوال اول: ...` or `فرضیه اول: ...`.
- The introductory paragraph and blockquotes in each decoupled section must strictly introduce that specific question/hypothesis.
- Never allow legacy multi-question introductions, leaked blockquotes of other questions, or orphaned subsection numbers to remain.

---

## 5. CANONICAL REGRESSION REPORTING STANDARDS

### 5.1 Canonical 3-Table Regression Standard
Every regression hypothesis must be reported through exactly three separate, dedicated tables (fail-closed structural invariant):
1. **Table 1: Bivariate Pearson Correlation Matrix**: Predictors and criterion correlation matrix with Col 1 (`ردیف`), Col 2 (`متغیر`), Col 3 (`مؤلفه`). Asterisks permitted only here.
2. **Table 2: Model Summary & ANOVA Table (11 Columns)**: Model summary and analysis of variance combined into an 11-column table ($SS, df, MS, F, p, R, R^2, \text{Adj } R^2, SE_{\text{est}}, DW$).
3. **Table 3: Regression Coefficients & Collinearity Table (8 Columns)**: Parameter estimates and collinearity diagnostics (Predictor, $B, SE, \beta, t, p$, Tolerance, VIF).

### 5.2 Regression ANOVA Option A Standard
In regression ANOVA tables with multiple criterion variables:
- **Column 1**: `متغیر ملاک` (Criterion variable name).
- **Column 2**: `منبع تغییرات` (Strictly `رگرسیون`, `باقیمانده`, `کل`).
- **Row Labels**: Regression rows are labeled with the dependent construct. Residual and total rows must be labeled simply as `باقیمانده` and `کل`. Never append parenthetical variable names to residual or total rows (e.g. prohibited: `باقیمانده (رفتارهای خودآسیبی)`).
- **Coefficients Criterion Column**: When reporting multiple criteria in a coefficients table, Column 1 must specify `متغیر ملاک`.

---

## 6. SCHOLARLY NARRATIVE PROSE STANDARDS

### 6.1 Continuous Scholarly Prose (Zero Bullets)
- All findings narratives must be composed as continuous, cohesive academic paragraphs.
- Bullet points, hyphens, and numbered listicles are strictly prohibited in the Chapter 4 narrative body.

### 6.2 Zero Hanging Colons & Telegraphic Text
- Eradicate hanging colons (`:`) at paragraph ends preceding tables or metrics.
- Eradicate inline colon-delimited labels or pseudo-bullets (e.g. `**موضوع:** ... **هدف:** ...`).
- All sentences must have proper Persian grammar, subject-object-verb agreement, and past-tense reporting.

### 6.3 Anti-Jargon & Clean Academic Tone
- Suppress meta-methodology commentary, internal agent instructions, or references to software execution from the findings text.
- Variable names in text and tables must use pure conceptual constructs (e.g. `خودآسیبی`), never instrument nouns (`پرسشنامه`) or author names.

### 6.4 Comprehensive Boundaries
- Chapter 4 must begin with a comprehensive structural introduction outlining the sample, variables, and sequence of analyses.
- Chapter 4 must conclude with a comprehensive narrative summary synthesizing the status of all hypotheses.

---

## 7. CLI EXECUTION & SCAFFOLDING
```bash
python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py \
  --stage "آزمون فرضیه اول" \
  --base "06_hypothesis_1" \
  --outdir "03_deliverables/stage_06_hypothesis_1"
```

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-20260925-A4DD06)**: Standard compliance: 🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~583/600 tokens (97.2%)]
- **Target Capability**: `CHAPTER4` | **Task**: `chapter_4_drafting` | **Agent**: `academic-writer` | **Project**: `cross-project`


⚠️ Known Pitfalls (Anti-Patterns to Avoid):
- **Lesson (LSN-2026-SCHOLARLY-CONTINUOUS-PROSE-001)**: Write all narrative findings as continuous scholarly paragraphs. Never use bullets, hyphens, or numbered lists in the narrative body. Ensure table captions are 12pt B Nazanin Regular (non-bold). [Enforcement: results_auditor_guard.py]
  Approved Remedy: Enforce strict heading naming standard ('سوال اول: ...', 'فرضیه اول: ...'), strip parenthetical duplicates, remove raw markdown tokens from markdown source, and equip the OpenXML renderer with robust parsing.
- **Lesson (LSN-2026-NO-INLINE-COLON-LISTICLES-001)**: Never use inline colon-delimited labels or telegraphic pseudo-bullets (**موضوع:** ... **موضوع بعدی:** ...) in formal academic prose. Always weave empirical parameters into flowing, cohesive narrative paragraphs using scholarly transitions. [Enforcement: results_auditor_guard.py]
  Approved Remedy: When an academic tone issue is flagged, conduct a global chapter-wide sweep to apply the validated scholarly standard across all sections uniformly.
- **Lesson (LSN-2026-REGRESSION-ANOVA-ROW-LABELS-001)**: In all regression ANOVA tables (خلاصه مدل و تحلیل واریانس), format source of variance rows as: [Variable Name], 'باقیمانده', 'کل' for each criterion variable, strictly omitting parenthetical variable names on residual and total rows. [Enforcement: results_auditor_guard.py]
  Approved Remedy: Use concise APA Latin symbols in table headers, define them in Persian in the note, and ensure pure Persian prose without raw English words.

💡 Relevant Active Lessons:
- [LSN-2026-PERSIAN-SCRIPT-ONLY-WITH-ENGLISH-FOOTNOTES-001] Mandate: Enforce zero Latin script in Persian body text. Transliterate all author names to Persian, use Persian equivalents for technical terms, and provide original English text strictly via footnotes.
  Generalization: Running Persian academic text must strictly contain zero Latin script words.

⚖️ Applicable Methodology Rules & Boundary Conditions:
- No conflicting paradigms active. Follow primary statistical decision tree.

---
### Executable Task Assignment:
### Contractual Delegation Envelope (CDE)
```json
{
  "task_id": "TSK-2026-REMEDIATE-REFS-LEAK-POST-GRADUATION",
  "stage": "Remediation of Bibliographic Leakage & Master Monograph Update",
  "worker_agent": "academic-writer",
  "objective": "Execute the clean remediation of references in Comprehensive_References.docx and Thesis_Final_Master.docx using evolved structural validation, purging all leaked subheadings and non-reference text",
  "target_script": "python3 02_analysis_code/restore_comprehensive_references_v2.py",
  "inputs": [
    "03_deliverables/Thesis.docx",
    "04_references_and_lit/Reference.docx",
    "03_deliverables/Thesis_Chapters1to3.docx",
    "01_raw_inputs/فصل 4 خانم مرضیه ابراهیمی (1).docx",
    "03_deliverables/Chapter_5_Discussion.docx",
    "03_deliverables/All_Appendices.docx"
  ],
  "required_artifacts": [
    "03_deliverables/Comprehensive_References.docx",
    "03_deliverables/Thesis_Final_Master.docx",
    "03_deliverables/thesis_assembly_manifest.json"
  ],
  "acceptance_criteria": [
    "Apply the graduated structural citation parsing invariants (LSN-2026-STRUCTURAL-REFERENCE-PARSING-001): every reference entry MUST have author-year markers (e.g. 4-digit solar/Gregorian year)",
    "Strictly exclude subheadings such as 'الف) منابع و مآخذ فارسی (کتب و مقالات)', 'ب) منابع و مآخذ انگلیسی (لاتین)', and any section labels or note lines",
    "Regenerate 03_deliverables/Comprehensive_References.docx containing ONLY genuine references, categorized into 'الف) منابع فارسی' and 'ب) منابع انگلیسی'",
    "Recompile 03_deliverables/Thesis_Final_Master.docx incorporating the purified bibliography, maintaining Chapters 1-5, all 222 OpenXML footnotes, and appendices intact",
    "Verify that the references section contains zero non-reference text",
    "Update 03_deliverables/thesis_assembly_manifest.json with verified pure reference counts"
  ],
  "constraints": [
    "Directive 4 (APA 7th Edition typography)",
    "Directive 5 (Persian Academic OpenXML Typography Standards, RTL, hanging indents)",
    "Directive 6 (English ASCII filenames)",
    "Directive 23 (Clean Workspace Root Standard: place script in 02_analysis_code/)"
  ]
}
```

Please execute `02_analysis_code/restore_comprehensive_references_v2.py` and return structured completion metrics.


The current local time is: 2026-09-25T19:13:18+03:30. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-STRICT-QUESTION-SECTION-DECOUPLING-001)**: When Chapter 4 sections are decoupled so that each research question or hypothesis has its own dedicated section, the section's introductory paragraph and blockquotes must strictly and exclusively introduce that specific question. Never allow legacy multi-question introductions, leaked blockquotes of subsequent questions, or orphaned subsection numbers (e.g. ## ۵-۴-۴ appearing after ## ۴-۵) to remain. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-QUESTION-HYPOTHESIS-HEADINGS-AND-CLEAN-DOCX-001)**: Enforce 'سوال اول: ...' and 'فرضیه اول: ...' section titles, clean non-redundant subheadings, and complete elimination of raw markdown artifacts in Word output. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-MANDATORY-BLANK-LINE-BEFORE-HEADINGS-001)**: Ensure an explicit blank line precedes every heading across Markdown source and Word DOCX deliverables. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-REGRESSION-ANOVA-OPTION-A-STANDARD-001)**: In all regression ANOVA tables with multiple criterion variables, use a two-column structure: Column 1 ('متغیر ملاک') and Column 2 ('منبع تغییرات' with 'رگرسیون', 'باقیمانده', 'کل'). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-NO-CHAPTER-WRITING-IN-DATA-MAKING-001)**: During data generation and SEM/statistical model verification phases, suppress Chapter 4 document compilation. Present only empirical findings: summary statistics, R/Python notebooks, regression/SEM tables, and visualization diagrams. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-STARS-ONLY-IN-CORRELATION-TABLES-001)**: Restrict asterisk usage in tables exclusively to correlation matrices; purge all asterisks from non-correlation table cells, headers, and notes. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-HIERARCHICAL-TABLE-VARIABLE-SUBSCALE-LAYOUT-001)**: In two-column variable-and-subscale tables, always output: Row(Parent Variable) -> subsequent Rows(blank Col 0, Subscale in Col 1) -> Row(Next Parent Variable). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-VARIABLE-COMPOSITE-ROW-INVARIANT-001)**: Always populate parent variable rows with overall/composite metrics; never create an empty parent row followed by a separate 'total' row. [Enforcement: results_auditor_guard.py]