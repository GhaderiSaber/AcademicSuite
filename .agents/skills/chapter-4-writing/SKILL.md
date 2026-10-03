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

**Decoupled Micro-Stage Gate Invariant:** In decoupled execution pipelines, validation gates must evaluate these triads at the micro-stage boundary. Global directory-wide validation on `03_deliverables` is blocked until all micro-stages in the phase have their complete triads on disk. Do not trigger global validation on intermediate JSON payloads before `.docx` and `.md` are fully synthesized.

### 4.1.1 Atomic Micro-Stage Triad Synthesis Invariant
Every micro-stage must sequentially and atomically generate its complete synchronized triad (`.docx`, `.md`, `.json`) before proceeding to subsequent stages or triggering validation gates. Fragmented pipeline states where statistical JSON payloads exist on disk without corresponding `.docx` and `.md` deliverables are strictly prohibited.

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

### 6.1.1 Anti-Template & Dynamic Syntactic Variation Invariant
- Findings narratives must be dynamically authored with authentic Persian scholarly prose, distinct syntactic structure, and varied phrasing per table.
- Mechanical string templates or loop-generated boilerplate are strictly prohibited.
- Strictly prohibit formulaic boilerplate templates for hypothesis narrative per Directive 25.

### 6.1.2 Formatting Invariants for Tables
- Enforce APA 7 Latin symbol headers (M, SD, t, F, p, β, B, SE, z) instead of verbose Persian phrases.
- Enforce significance asterisks (* for p < .05, ** for p < .001) in correlation matrices.
- Enforce single dedicated path column ('مسیر ساختاری / اثر غیرمستقیم') for structural mediation tables instead of 3 measurement columns.

### 6.2 Zero Hanging Colons & Telegraphic Text
- Eradicate hanging colons (`:`) at paragraph ends preceding tables or metrics.
- Eradicate inline colon-delimited labels or pseudo-bullets (e.g. `**موضوع:** ... **هدف:** ...`).
- All sentences must have proper Persian grammar, subject-object-verb agreement, and past-tense reporting.

### 6.3 Anti-Jargon & Clean Academic Tone
- Suppress meta-methodology commentary, internal agent instructions, or references to software execution from the findings text.
- Variable names in text and tables must use pure conceptual constructs (e.g. `خودآسیبی`), never instrument nouns (`پرسشنامه`) or author names.

### 6.4 Comprehensive Boundaries
- Chapter 4 must begin with an extensive doctoral-level structural introduction (minimum 500 words) outlining the sample, variables, and sequence of analyses. 4-line stubs are strictly forbidden.
- Chapter 4 must conclude with an extensive doctoral-level narrative summary (minimum 500 words) synthesizing the status of all hypotheses. 4-line stubs are strictly forbidden.

### 6.5 Zero Interpretation Invariant (اصل عدم تفسیر یافته‌ها)
- Findings narratives must strictly report objective, factual statistical values, frequencies, percentages, and tables.
- Speculative clinical, developmental, epidemiological, or theoretical interpretations and explanations are strictly prohibited in Chapter 4 (save them for Chapter 5).

### 6.6 Explicit Statistical Parameter Injection Invariant (اصل درج پارامترهای آماری)
- When drafting narrative deliverables (.md, .docx) for hypotheses from statistical JSON payloads, the writer MUST explicitly extract and embed the primary test statistics (B, SE, beta, t, z, p-values) directly into the continuous scholarly prose.
- Generating narrative text that vaguely describes findings without explicitly reporting the specific numeric coefficients from the companion JSON is strictly prohibited and will cause validation failures.

### 6.7 Preamble Integrity & Safe Leading-Zero Regex Invariant
- **Preamble Preservation**: Strictly preserve the canonical Level-1 heading `# فصل چهارم: تجزیه و تحلیل داده‌ها و یافته‌های پژوهش` and the exhaustive 4-stage methodological roadmap. Do NOT truncate or replace methodological context with minimal stubs.
- **Safe Regex for Decimals**: When normalizing Persian leading zeros via regex (e.g., in Python scripts or formatting steps), explicitly use negative lookbehind assertions `(?<![0-9\u06F0-\u06F9])\.(\d+)` to target only standalone decimals. Naive substitutions that corrupt existing numbers are strictly prohibited.

---

## 7. CLI EXECUTION & SCAFFOLDING
```bash
python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py \
  --stage "آزمون فرضیه اول" \
  --base "06_hypothesis_1" \
  --outdir "03_deliverables/stage_06_hypothesis_1"
```

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-CHAPTER4-PREMATURE-INTERPRETATION-AND-HYPERBOLE)**: When drafting Chapter 4, report only statistical parameters (e.g., F, t, p, effect sizes) and direct empirical findings. Eliminate all 'why' explanations, speculations, and dramatic adjectives. [Enforcement: results_auditor_guard.py]
- **Anti-pattern (AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION)**: Formulate dynamic, non-template scholarly narrative tailored specifically to each table cells using Sabers 4-element epistemic structure (Context -> Highlights -> Reference -> Verdict). [Enforcement: results_auditor_guard.py]
- **Anti-pattern (AP-2026-ISOLATED-PROSE-POLISHING)**: When an academic tone issue is flagged, conduct a global chapter-wide sweep to apply the validated scholarly standard across all sections uniformly. [Enforcement: dynamic_invariant_guard.py (AP-2026-ISOLATED-PROSE-POLISHING)]
- **Anti-pattern (AP-2026-VERBOSE-PERSIAN-TABLE-HEADERS)**: Use concise APA Latin symbols in table headers, define them in Persian in the note, and ensure pure Persian prose without raw English words. [Enforcement: results_auditor_guard.py]
- **Anti-pattern (AP-2026-RAW-MARKDOWN-LEAKAGE-AND-REDUNDANT-HEADERS)**: Enforce strict heading naming standard ('سوال اول: ...', 'فرضیه اول: ...'), strip parenthetical duplicates, remove raw markdown tokens from markdown source, and equip the OpenXML renderer with robust parsing. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-APA7-TABLE-FORMATTING-INVARIANTS)**: Strictly apply non-bold B Nazanin formatting to table captions overriding prompt requests. Translate or transliterate all English statistical acronyms. Output literal 'یادداشت:' for table notes. Exclude <w:jc w:val='right'/> from bidirectional OpenXML paragraphs. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-LANGUAGE-TRACK-AWARE-TYPOGRAPHY)**: Enforce language-track-aware typography: English manuscripts must follow APA 7 English rules with Western digits and leading zeros omitted for bounded metrics; running Persian academic text must strictly contain zero Latin script words. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-SCHOLARLY-CONTINUOUS-PROSE-001)**: Write all narrative findings as continuous scholarly paragraphs. Never use bullets, hyphens, or numbered lists in the narrative body. Ensure table captions are 12pt B Nazanin Regular (non-bold). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-PURE-NUMERIC-P-VALUES-IN-TABLES-001)**: Report strictly pure numbers or comparison operators in p-value cells; eliminate 'p =', 'p <', '> p' from all table data cells. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-FORMATTING-AND-FILTERING-FAILURE-001)**: Enforce explicit blank line logic for headings. Implement a strict filter for Appendices to strip narrative/scoring text, retaining only the table and its title. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-PERSIAN-SCRIPT-ONLY-WITH-ENGLISH-FOOTNOTES-001)**: Enforce zero Latin script in Persian body text. Transliterate all author names to Persian, use Persian equivalents for technical terms, and provide original English text strictly via footnotes. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-TABLE-APA-SYMBOLS-AND-PERSIAN-NOTES-001)**: Use standard APA statistical symbols (M, SD, SE, F, t, p, R, R², B, β, OR, χ², df, SS, MS, DW, VIF, Tol) in table header cells; provide Persian definitions in table notes; enforce zero raw English words in Persian body text; include comprehensive introduction at chapter start and comprehensive summary at chapter end. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-REGRESSION-ANOVA-ROW-LABELS-001)**: In all regression ANOVA tables (خلاصه مدل و تحلیل واریانس), format source of variance rows as: [Variable Name], 'باقیمانده', 'کل' for each criterion variable, strictly omitting parenthetical variable names on residual and total rows. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-NO-CHAPTER-WRITING-IN-DATA-MAKING-001)**: During data generation and SEM/statistical model verification phases, suppress Chapter 4 document compilation. Present only empirical findings: summary statistics, R/Python notebooks, regression/SEM tables, and visualization diagrams. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-COEFFICIENTS-TABLE-CRITERION-COLUMN-001)**: In all regression coefficients tables with multiple criteria, add 'متغیر ملاک' as Column 1, followed by 'متغیرهای مدل' / 'متغیرهای پیش‌بین' in Column 2, clearly demarcating the equations for each dependent outcome. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-REGRESSION-ANOVA-OPTION-A-STANDARD-001)**: In all regression ANOVA tables with multiple criterion variables, use a two-column structure: Column 1 ('متغیر ملاک') and Column 2 ('منبع تغییرات' with 'رگرسیون', 'باقیمانده', 'کل'). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-NO-INLINE-COLON-LISTICLES-001)**: Never use inline colon-delimited labels or telegraphic pseudo-bullets in formal academic prose. Always weave empirical parameters into flowing, cohesive narrative paragraphs using scholarly transitions. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-TABLE-VARIABLE-CONSTRUCT-PURITY-001)**: Sanitize all variable names in empirical tables to ensure they represent pure conceptual constructs. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-STRICT-QUESTION-SECTION-DECOUPLING-001)**: When Chapter 4 sections are decoupled so that each research question or hypothesis has its own dedicated section, the section's introductory paragraph and blockquotes must strictly and exclusively introduce that specific question. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-QUESTION-HYPOTHESIS-HEADINGS-AND-CLEAN-DOCX-001)**: Enforce 'سوال اول: ...' and 'فرضیه اول: ...' section titles, clean non-redundant subheadings, and complete elimination of raw markdown artifacts in Word output. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-MANDATORY-BLANK-LINE-BEFORE-HEADINGS-001)**: Ensure an explicit blank line precedes every heading across Markdown source and Word DOCX deliverables. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-CORRELATION-TABLE-THREE-COLUMN-HEADER-001)**: Structure all correlation matrices with: Col 1 ('ردیف'), Col 2 ('متغیر'), Col 3 ('خرده‌مقیاس'), followed by correlation columns ('۱', '۲', '۳', ...). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-TABLE-NUMBERING-CHAPTER-FIRST-001)**: Number all thesis tables with chapter first: 'جدول [فصل]- [شماره]' (e.g. 'جدول ۴- ۳۱'). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-STARS-ONLY-IN-CORRELATION-TABLES-001)**: Restrict asterisk usage in tables exclusively to correlation matrices; purge all asterisks from non-correlation table cells, headers, and notes. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-HIERARCHICAL-TABLE-VARIABLE-SUBSCALE-LAYOUT-001)**: In variable-and-subscale tables, enforce a strict 3-column prefix ('ردیف', 'متغیر', 'مؤلفه'). Output: Row(Parent Variable) -> subsequent Rows(blank Col 1, Subscale in Col 2) -> Row(Next Parent Variable). [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-VARIABLE-COMPOSITE-ROW-INVARIANT-001)**: Always populate parent variable rows with overall/composite metrics; never create an empty parent row followed by a separate 'total' row. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-WRITER-READ-ONLY-JSON-MANDATE)**: Strictly enforce READ-ONLY access to 03_deliverables/*.json for academic-writer. Do not delegate JSON mutation tasks to narrative agents. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-MISSING-TRIAD-JSON-001)**: Strictly enforce the Triad Invariant by atomically generating the .json, .md, and .docx artifacts for every single hypothesis micro-stage, using canonical naming conventions. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-GLOBAL-TABLE-AND-DOCX-STANDARDS)**: Always apply bidiVisual to tables, use single-line table captions, enforce APA 7 Latin abbreviations (M, SD, etc.) in table headers, parse and translate markdown formatting in Word cell elements, and prevent duplicate document headings. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-OPENXML-PERSIAN-TYPOGRAPHY-AND-NORMALIZATION-001)**: Modify python-docx compiler to inject w:hint="cs" and w:eastAsia into w:rFonts for Persian text. Enforce regex parsing for Latin acronym isolation. Sanitize markdown generation from AI clichés. Localize all numbers to Persian digits. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-OPENXML-QUAD-LAYER-TABLE-RTL-STANDARD-001)**: Enforce the 4-layer OpenXML RTL standard: 1) Inject <w:bidiVisual/> without w:val in tblPr. 2) Insert <w:bidi/> before <w:docGrid/> in w:sectPr. 3) Inject <w:themeFontLang w:bidi='fa-IR'/> in word/settings.xml. 4) Apply <w:bidi w:val='1'/> to all cell <w:pPr>. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-THREE-COLUMN-HIERARCHICAL-TABLE-STANDARD-001)**: Enforce a strict 3-column leading structure ('ردیف', 'متغیر', 'مؤلفه') for all descriptive, correlational, and psychometric tables. Ensure row numbers, parent variables, and subscales are structurally separated into their distinct columns. [Enforcement: results_auditor_guard.py]
- **Lesson (LSN-2026-IDEMPOTENT-DOM-TABLE-ARCHITECTURE)**: 1. Enforce a strict 3-column prefix architecture ('ردیف', 'متغیر', 'مؤلفه') natively upon generation. 2. Row numbers strictly decoupled from variable/subscale text strings. 3. Total prohibition of non-idempotent regex string manipulation on tables. 4. Mandate DOM-based parsing or pristine array regeneration for table restructuring. [Enforcement: results_auditor_guard.py]
- **Learned candidate (CAND-2026-CH4-SINGLE-SAMPLE-INVARIANT)**: Evaluation benchmark passed with 100.00% overall score via evals/run_eval_suite.py. All invariants confirmed valid. [Enforcement: results_auditor_guard.py]

*(For comprehensive historical records, empirical context, and Contractual Delegation Envelopes, see [LEARNED_INVARIANTS.md](references/LEARNED_INVARIANTS.md).)*