# AGENTS.md — Global Agent Instructions & Operational Guidelines

This repository contains the **Academic Thesis & Statistical Consultancy Skill Suite** for Google Antigravity and autonomous coding agents. It is designed to assist academic researchers and graduate students (specifically in Psychology, Counseling, and Behavioral Sciences) with translating literature, extracting citations, conducting rigorous statistical analysis, writing defense-ready Chapter 4 reports, and compiling full graduate theses.

---

## 1. Golden Rules for Any AI Agent Working in This Workspace

Every AI agent operating in this repository **MUST** strictly adhere to the following directives:

### Rule 1: Progressive Disclosure (Always Consult SKILL.md First)
- Do **not** guess workflows or procedures.
- When tasked with a job (e.g., translation, data analysis, reference extraction, or thesis assembly), your **first action** must be to read the corresponding skill's `SKILL.md` using `view_file`.
- All domain rules, scripts, and edge-case handling are encapsulated inside `.agents/skills/<skill-name>/`.

### Rule 2: Deterministic Calculation (Zero Hallucinations)
- **NEVER calculate, estimate, or hallucinate statistical numbers, $p$-values, effect sizes, or test statistics in your head.**
- Always execute the bundled Python scripts in `.agents/skills/statistical-data-analyst/scripts/` via the terminal (`run_command`) on the real dataset (`.xlsx`, `.csv`, `.sav`).
- Extract exact values from the script's output JSON/table and paste them directly into reports.

### Rule 3: Strict APA 7th Edition Typography & Formatting
All statistical results (whether in Persian or English) must comply with APA 7th Edition standards:
1. **Italicization**: Latin statistical symbols (*M, SD, t, F, p, r, R², β, B, z, SE*) **must be italicized**. Greek letters (*α, ω, η², χ²*) remain regular unless university guidelines state otherwise.
2. **Decimal Places**:
   - Means, SDs, test statistics ($t, F$), effect sizes: **2 decimal places** (e.g., $M = 24.35$, $t = 3.88$, $d = 0.78$).
   - $p$-values: **Exactly 3 decimal places** (e.g., $p = .014$).
3. **The Leading Zero Rule**:
   - Numbers bounded between 0 and 1 ($p$, $r$, $R^2$, $\eta_p^2$, $\alpha$, $\beta$) **must omit the leading zero**:
     - Correct: $p = .023$, $r = .48$, $\eta_p^2 = .19$
     - Incorrect: $p = 0.023$, $r = 0.48$, $\eta_p^2 = 0.19$
4. **Never Report $p = .000$**:
   - If a software outputs $.000$, report it strictly as **$p < .001$** (یا در فارسی: **۰/۰۰۱ > p**).
5. **APA 7 Table Rules**:
   - Tables must have **zero vertical borders**.
   - Exactly 3 horizontal borders: Top line (solid 0.75 pt), Header bottom underline (solid 0.5 pt), and Table bottom line (solid 0.75 pt).
   - Table titles/captions **above** the table; table notes/asterisks **below** the table.

### Rule 4: Persian Academic Typography & OpenXML Standards
When assembling or editing Persian Word documents (`.docx`):
- **Fonts**:
  - Chapter Titles: `B Titr` 16–18 pt Bold, Centered.
  - Headings 2 & 3: `B Titr` or `B Nazanin Bold` 13–14 pt Bold, Right-aligned.
  - Body Paragraphs: `B Nazanin` or `B Lotus` 13–14 pt Regular, Line Spacing 1.15–1.3, Justified (`WD_ALIGN_PARAGRAPH.JUSTIFY`).
  - Numbers and Statistics: `Times New Roman` 10–11 pt.
- **BiDi & OpenXML Directionality**:
  - Always enforce `<w:bidi w:val="1"/>` on Persian paragraphs and `<w:bidiVisual/>` on tables.
  - Enforce explicit font binding with `<w:rFonts w:ascii="Times New Roman" w:cs="B Nazanin"/>` to prevent font fallback corruption.
  - Maintain Persian half-spaces (نیم‌فاصله: `\u200c`) in compound words (e.g., `می‌شود`, `پیش‌آزمون`, `یافته‌ها`).

### Rule 5: Critical OpenXML Standard: Preservation of Native Word Math & OMML Formulas (`<m:oMath>`)
When inspecting, auditing, or modifying academic Word documents (`.docx`):
1. **The OMML Text Blindspot in python-docx**:
   - `paragraph.text` in `python-docx` **ONLY** reads standard `<w:t>` elements and completely ignores math text runs (`<m:t>`) embedded inside native Word equation objects (`<m:oMath>` / `<m:oMathPara>`).
   - Consequently, paragraphs containing native Word equations (e.g., $(F_{7, 367} = 9.44, p < .001)$, $(\beta = -0.173)$, $(n = 252)$) will falsely appear in `paragraph.text` as having empty parentheses `()` or missing numbers.
2. **Never Overwrite `paragraph.text` Naively**:
   - Executing `paragraph.text = "..."` replaces all child XML nodes and irrevocably deletes all `<m:oMath>` and `<m:oMathPara>` equation objects.
   - Any agent modifying a paragraph must first check whether it contains math elements:
     ```python
     has_math = any(elem.tag.endswith("}oMath") for elem in paragraph._p.iter())
     ```
3. **Mandatory Full Text Extraction Protocol**:
   - To inspect the true visible text of any paragraph including equations, always extract text from both `<w:t>` and `<m:t>`:
     ```python
     full_text = "".join([e.text or "" for e in paragraph._p.iter() if e.tag.endswith("}t")])
     ```
4. **Mandatory Pre-Edit Backup**:
   - Before applying any programmatic edits or replacements to user documents (`.docx`), always save a timestamped backup copy to `drafts_archive/` or a pre-edit file.

### Rule 6: English Language Primary for Agent-User Pairing
- **Default Interaction Language**: Agents must always communicate, reason, explain plans, and report status to the user in **English** by default.
- **Persian Artifacts**: Persian is strictly reserved for client-facing communications, academic thesis chapters, Persian proposals, and Persian presentation deliverables, or when Persian response is explicitly requested.

### Rule 7: Digital Twin Persona & Client Interaction Protocol
When acting as Saber Ghaderi's Digital Twin (`@GhaderiSaber`, Telegram ID: `124911145`) or processing client messages, proposals, and questionnaire inquiries:
1. **Scholarly, Reassuring Tone**: Communicate in authentic, polite, authoritative yet encouraging academic Persian. Enforce Persian half-spaces (نیم‌فاصله) and strictly eliminate robotic AI cliches (*«شایان ذکر است که»*, *«در این راستا»*, *«به عنوان یک مدل هوش مصنوعی»*).
2. **Deterministic Proposal Evaluation & Pricing**: Never invent or arbitrarily quote prices. Always run `proposal_price_estimator.py` to extract research design, sample size $N$, variables, scales, and required statistical software. Use the established pricing matrix in Tomans and generate itemized, transparent quotations.
3. **Human-in-the-Loop Admin Approval**: All draft quotations and major client commitments must be submitted to Saber's Admin Desk (`124911145`) for one-click approval (`/approve_Q101`) or price adjustment (`/adjust_Q101_<price>`) prior to client delivery, unless `--auto-quote` is explicitly set.
4. **Questionnaire Registry Resolution**: Resolve psychometric questionnaire inquiries against the 4,880 instruments in `Questionnaires.xlsx` using `questionnaire_resolver.py`. Deliver verified item counts, subscale structures, scoring ranges, and reverse-scoring keys.

### Rule 8: Mandatory Git Commit & Push Lifecycle (Zero Unpushed Changes)
- **Automatic End-of-Turn Synchronization**: After completing any user request, modifying code, updating documentation, or adding/refining skills or rules, the AI agent **MUST** automatically stage all changed project files, create a conventional semantic commit message, and push the changes directly to GitHub remote (`origin main` or active branch).
- **Conventional Commit Standards**:
  - `feat(...)`: For new features, presentation paths, scripts, or skill enhancements.
  - `fix(...)`: For bug fixes, typographic adjustments, or calculation corrections.
  - `docs(...)`: For documentation, guidelines, AGENTS.md, or SKILL.md updates.
  - `refactor(...)`: For code cleaning, structural reorganization, or optimization.
- **Strict Prohibition Against Dirty Working Trees**: An agent must never conclude a user request turn leaving uncommitted or unpushed modifications behind in the workspace. Always execute `git status` to verify a clean working tree and up-to-date tracking with `origin`.

### Rule 9: Realistic Empirical Decimal Noise in Psychometric Simulation (Zero Synthetic Whole-Integer Means)
When generating or simulating synthetic research data, questionnaire Likert responses, or experimental/multivariate datasets:
1. **The Synthetic Integer Trap (قاعده ضد میانگین‌های تصنعی رند)**:
   - In authentic empirical research, participants answer discrete integer items, but the sample mean $\bar{X} = \frac{1}{N}\sum X_i$ across tens or hundreds of respondents **never** comes out to an exact whole integer (such as $M = 5.000$, $10.000$, or $4.000$).
   - Reporting exact whole-integer means in thesis tables, APA 7 reports, or SPSS outputs is an immediate indicator of synthetic manipulation and will trigger suspicion during academic defense and peer review.
2. **Organic Bounded Decimal Perturbations**:
   - When given a nominal target mean $\mu_{\text{target}}$ by the client, supervisor, or proposal (e.g. Healthy = 5, Self-Harm = 10):
   - Never force the group sum to hit $\mu_{\text{target}} \times N$ exactly.
   - Always inject bounded random empirical decimal noise:
     $$\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \quad \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25), \quad |\text{round}(\mu_{\text{empirical}}) - \mu_{\text{empirical}}| \ge 0.05$$
   - A target of $5.0$ must naturally emerge as $M = 5.24$, $4.88$, or $5.15$; a target of $10.0$ must emerge as $M = 10.13$, $9.89$, or $10.82$.
3. **Discrete Integer Participant Responses**:
   - While group means have realistic decimal fractions, individual participant responses must strictly remain valid discrete integers within each scale's theoretical minimum and maximum bounds ($Min \le X_{ij} \le Max$). Never output fractional numbers for survey item ratings.
4. **Natural Non-Identical Standard Deviations**:
   - Standard deviations must reflect realistic, non-identical sample variance ($SD = 1.76, 1.94, 2.12$).
5. **Preservation of Hypotheses & Statistical Assumptions**:
   - The introduction of decimal noise must strictly preserve all univariate and multivariate statistical assumptions:
     - Univariate Normality (Skewness and Kurtosis strictly within $[-0.85, +0.85]$).
     - Homogeneity of Variance (Levene's test $p > .05$).
     - Homogeneity of Covariance Matrices (Box's M test $p > .05$).
     - Multivariate Significance (MANOVA Wilks' Lambda $p < .001$).
     - Hypothesized contrasts (significant differences where expected; $p > .05$ on controlled baseline or non-significant dimensions).

### Rule 10: Realistic Empirical Effect Sizes in Psychometric Simulation (Zero Astronomical $\eta_p^2$ / Anti-Over-Separation Guardrail)
When simulating group-difference or experimental research datasets (ANOVA, MANOVA, independent $t$-tests, clinical trials):
1. **The Astronomical Effect Size Trap (قاعده ضد اندازه اثرهای نجومی و مصنوعی)**:
   - In real-world psychological, behavioral, and clinical research, human constructs are continuous, multi-determined, and subject to natural overlap between groups.
   - Even when comparing severe clinical populations with healthy controls, genuine empirical effect sizes rarely exceed Cohen's $d = 1.00 - 1.25$ or partial eta squared $\eta_p^2 \approx .20 - .25$ (Cohen, 1988; Miles & Shevlin, 2001).
   - A naive simulation that separates target group means too far (e.g., $M = 5.0$ vs. $10.0$ on a scale with $SD = 1.80$) produces $\Delta M = 5.0 \implies d \approx 2.78$. In moderate-to-large samples ($N \ge 300 - 500$), this inflates $t$-statistics to $30 - 65$ and $\eta_p^2$ to $.60 - .89$.
   - Reporting $\eta_p^2 = .70 - .89$ indicates that group membership accounts for 70% to 89% of the variance, implying virtually zero distribution overlap. This is an immediate red flag that will trigger accusations of data fabrication during thesis defenses and peer review.
2. **Mandatory Bounded Target Differences**:
   - For all hypothesized significant contrasts ($p < .001$), calibrate the target mean difference to:
     $$\Delta \mu \approx (0.80 \text{ to } 1.15) \times SD \implies d \in [0.80, 1.15], \quad \eta_p^2 \in [.12, .25]$$
   - This ensures robust statistical significance ($p < .001$) while remaining completely credible and defensible in psychological literature.
3. **Strict Bounds on Control/Non-Significant Dimensions**:
   - For dimensions hypothesized to show no significant difference (e.g. baseline controls, specific non-differentiating subscales):
     $$d \le 0.12, \quad \eta_p^2 \le .005, \quad p > .05$$
4. **Automated Iteration Filter**:
   - All Monte Carlo simulation scripts must explicitly compute $\eta_p^2 = \frac{t^2}{t^2 + df_{\text{error}}}$ on candidate samples and discard any sample where $\eta_p^2 > .25$ on any subscale.

---

## 2. Skill Inventory & Activation Matrix

| Skill Name | Path | When to Activate | Core Inputs | Primary Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **`persian-proposal-builder`** | [.agents/skills/persian-proposal-builder/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-proposal-builder) | User requests writing or refining a graduate research proposal (پروپوزال), drafting Chapter 1 or Chapter 3, or calculating sample size. | Research topic, variables, population, instruments | `پروپوزال_طرح_پژوهش.docx` meeting university review council rules. |
| **`psychological-intervention-protocol-builder`** | [.agents/skills/psychological-intervention-protocol-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychological-intervention-protocol-builder) | User requests drafting or compiling an experimental intervention protocol (ACT, CBT, Schema, CFT, MBSR, Positive Psychotherapy) for Chapter 3 or thesis appendix. | Treatment approach, target population, session count | `پروتکل_مداخله.docx` (Ch 3 table + Appendix manual) + `protocol_summary.json`. |
| **`persian-academic-translation`** | [.agents/skills/persian-academic-translation/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-academic-translation) | User requests translating English papers, book chapters, or theoretical frameworks into academic Persian. | English PDF / DOCX / TXT papers | `*_fa.docx` formatted with academic terminology and preserved citations. |
| **`academic-reference-extractor`** | [.agents/skills/academic-reference-extractor/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-reference-extractor) | User needs EndNote/Zotero citations for a translated paper or specific thesis chapter. | Translated text with citations + Master paper bibliography | `.enw` (EndNote), `.ris` (Zotero/Mendeley), and `.txt` (APA list). |
| **`psychometric-scale-resolver`** | [.agents/skills/psychometric-scale-resolver/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver) | User needs to identify questionnaires, extract subscale factor structures, scoring methods, reverse-scoring keys, or score raw survey items. | Raw items (`Q1..Q40`) or Scale query + `Questionnaires.xlsx` | `data_scored.xlsx` + factor subscales + Cronbach's $\alpha$. |
| **`statistical-data-analyst`** | [.agents/skills/statistical-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst) | User provides data (`.sav`, `.xlsx`, `.csv`) and requests analysis, hypothesis testing, or Chapter 4 writing. | Scored dataset + Hypotheses / Research Questions | `فصل چهارم: یافته‌های پژوهش.docx` + `stats_results.json` + APA 7 tables. |
| **`persian-discussion-builder`** | [.agents/skills/persian-discussion-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-discussion-builder) | User requests writing Chapter 5 (بحث و نتیجه‌گیری) interpreting statistical findings against literature. | Chapter 4 results (`stats_results.json`) + Chapter 2 literature | `فصل پنجم: بحث و نتیجه‌گیری.docx` with clinical implications and limitations. |
| **`persian-thesis-builder`** | [.agents/skills/persian-thesis-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-builder) | User wants to compile, merge, format, or assemble all modular thesis parts into a unified university document. | Master `.docx` template + Chapters 1-5 + References + Scales | `Thesis_Compiled.docx` (Complete dissertation meeting university formatting rules). |
| **`irandoc-plagiarism-reducer`** | [.agents/skills/irandoc-plagiarism-reducer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/irandoc-plagiarism-reducer) | User needs to reduce Irandoc (همانندجو) similarity score below 20% or 30%, rewrite flagged literature/discussion text, or eliminate cliches. | Flagged `.docx` or text + Irandoc report | `*_paraphrased.docx` + side-by-side comparison report (`.docx`). |
| **`persian-thesis-revision-assistant`** | [.agents/skills/persian-thesis-revision-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-revision-assistant) | User needs to review, extract, and resolve supervisor/examiner comments and produce the formal response table. | Reviewed `.docx` with comments or feedback text | `جدول_پاسخ_به_نظرات_اساتید.docx` + revised chapters. |
| **`persian-defense-presentation-builder`** | [.agents/skills/persian-defense-presentation-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-defense-presentation-builder) | User requests creating defense slides across 3 paths (html, .pptx, google_slides) or preparing for viva voce oral defense. **MANDATORY RULE**: Agent must ask user which path to take before generation unless explicitly pre-specified. | Completed thesis / chapters / stats_results.json | `جلسه_دفاع.pptx` (16:9 widescreen, RTL OpenXML, OMML math) / `presentation.html` / `Defense_Presentation_Brief.docx` & Google Drive sync. |
| **`academic-article-writer`** | [.agents/skills/academic-article-writer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer) | User requests drafting, structuring, or compiling an academic journal article from thesis chapters and project data for ISI/Scopus (English) or ISC (Persian). | Full project artifacts (Proposal, Lit Review, Stats JSON, Ch 5) | `Academic_Article_Manuscript.docx` (English) or `مقاله_علمی_پژوهشی.docx` (Persian) meeting IMRaD & APA 7 standards. |
| **`journal-submission-assistant`** | [.agents/skills/journal-submission-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/journal-submission-assistant) | User needs journal submission collateral (Cover Letter, Title Page with 14 CRediT roles, Highlights <= 85 chars, Declarations) or Point-by-Point Response to Reviewers for Revise & Resubmit. | Manuscript draft, metadata, or reviewer comments | `Cover_Letter.docx`, `Title_Page.docx`, `Highlights.docx`, `Response_to_Reviewers.docx`. |
| **`systematic-review-meta-analyst`** | [.agents/skills/systematic-review-meta-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/systematic-review-meta-analyst) | User conducts or reports systematic review or meta-analysis (PRISMA 2020 & Cochrane RoB 2), pooling Hedges' g, calculating heterogeneity (Q, I², τ²), testing publication bias (Egger), or generating Forest & Funnel plots. | Trial outcome datasets (means, SDs, Ns) or screening numbers | `Meta_Analysis_Report.docx` + `forest_plot.png` + `funnel_plot.png` + `meta_analysis_statistics.json`. |
| **`psychometric-data-simulator`** | [.agents/skills/psychometric-data-simulator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-data-simulator) | User requests synthetic psychometric datasets, Monte Carlo SEM/CFA data generation, multi-item discrete Likert scale responses with reverse items, or randomized clinical trial (RCT) repeated-measures pre/post data. | Structural model parameters ($\mathbf{B}, \mathbf{\Gamma}$), factor loadings ($\mathbf{\Lambda}$), or RCT trial specifications | Multi-sheet Excel workbook (`.xlsx`), CSV dataset, executable R `lavaan` script (`lavaan_syntax.R`), and simulation summary JSON. |
| **`qualitative-data-analyst`** | [.agents/skills/qualitative-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/qualitative-data-analyst) | User provides interview transcripts, focus groups, or qualitative data requiring Braun & Clarke Reflexive Thematic Analysis, Strauss & Corbin Grounded Theory, Paradigmatic Model (6 dimensions), or Chapter 4 qualitative reporting. | Interview transcripts / quotes / coding payload | `فصل_چهارم_یافته‌های_کیفی.docx` + `thematic_matrix.xlsx` + `thematic_network.png` (300 DPI) + `qualitative_summary.json`. |
| **`persian-literature-review-builder`** | [.agents/skills/persian-literature-review-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-literature-review-builder) | User requests drafting, synthesizing, or compiling Chapter 2 (فصل دوم: مبانی نظری و پیشینه پژوهش), translating English theoretical foundations, organizing Iranian/international empirical studies, or building APA 7 summary tables. | Foreign dissertations/theses, variables, empirical study records | `فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx` + `empirical_literature_matrix.xlsx` + `literature_summary.json`. |
| **`psychometric-scale-validator`** | [.agents/skills/psychometric-scale-validator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-validator) | User conducts scale adaptation, standardization, psychometric validation (Lawshe CVR, Waltz-Bausell CVI, EFA, CFA, McDonald's omega, Fornell-Larcker, Item Response Theory [IRT] Graded Response Model [GRM], Infit/Outfit MNSQ, Test Information Function [TIF], Differential Item Functioning [DIF], and ROC cut-offs) or writes psychometric Chapter 4 reports. | Raw survey items, expert panel ratings, scale structure | `فصل_چهارم_ویژگی‌های_روان‌سنجی_و_هنجاریابی.docx` (8 APA 7 tables) + `psychometric_validation_matrix.xlsx` (6 sheets) + dual 300-DPI plots (`scree_and_roc_plots.png`, `irt_tif_and_ccc_plots.png`) + `psychometric_summary.json`. |
| **`academic-suite-orchestrator`** | [.agents/skills/academic-suite-orchestrator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-suite-orchestrator) | User requests running end-to-end multi-stage research workflows, turnkey academic pipelines (empirical thesis, scale validation, qualitative study, meta-analysis, publication preparation, bibliometric pipeline), or managing research project dashboards. | Project config JSON or preset (`thesis_empirical`, `scale_validation`, `qualitative_study`, `meta_analysis`, `thesis_to_publication`, `bibliometric_pipeline`) | Coordinated stage deliverables + `orchestrator_manifest.json` + `PROJECT_DASHBOARD.md`. |
| **`thesis-integrity-auditor`** | [.agents/skills/thesis-integrity-auditor/](file:///Users/saber/Desktop/academic_suite/.agents/skills/thesis-integrity-auditor) | User requests auditing, checking, or verifying a graduate thesis, proposal, or research project for hypothesis-result alignment, degrees of freedom ($df$) consistency, citation reconciliation (orphaned vs ghost references), or APA 7 compliance. | Master thesis document (`.docx`) or audit JSON payload | `گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx` + `annotated_citations.xlsx` + `thesis_audit_summary.json` with computed Integrity Score (TIS). |
| **`gpower-sample-size-calculator`** | [.agents/skills/gpower-sample-size-calculator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/gpower-sample-size-calculator) | User requests determining required sample size ($N$), computing a priori/post hoc power, modeling effect sizes (Cohen's $d, f, f^2$), rendering power curve figures ($1-\beta$ vs $N$), or writing Chapter 3 G*Power methodology justifications. | Target design, alpha, desired power, effect size, or study config JSON | `گزارش_محاسبه_حجم_نمونه_جی‌پاور.docx` + `power_curve_plot.png` (300 DPI) + `sample_size_calculator_matrix.xlsx` + `gpower_results.json`. |
| **`ai-academic-tone-polisher`** | [.agents/skills/ai-academic-tone-polisher/](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher) | User requests humanizing AI-generated academic text, optimizing sentence cadence and burstiness ($CV \ge 0.50$), removing robotic LLM cliches (شایان ذکر است که، delve into), or refining Persian half-spaces (نیم‌فاصله) while preserving citations and statistics. | AI draft text (`.docx` / `.txt` / JSON) | `متن_ویراسته_و_دانشگاهی.docx` + `tone_burstiness_plot.png` (300 DPI) + `academic_tone_audit_matrix.xlsx` + `tone_polish_results.json`. |
| **`literature-harvester`** | [.agents/skills/literature-harvester/](file:///Users/saber/Desktop/academic_suite/.agents/skills/literature-harvester) | User requests automated literature search, extracting empirical parameters (sample size N, design, scales, findings) from PubMed, CrossRef, Semantic Scholar, SID, or Magiran, or compiling Chapter 2 empirical review matrices and RIS citation files. | Research keywords or search query payload | `گزارش_جامع_پیشینه_پژوهش_استخراج‌شده.docx` + `harvested_empirical_studies.xlsx` + `harvested_citations.ris` + `harvested_studies.json`. |
| **`bibliometric-network-analyst`** | [.agents/skills/bibliometric-network-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/bibliometric-network-analyst) | User requests science mapping, keyword co-occurrence analysis, Bradford's Law journal scattering, Lotka's author productivity, NetworkX centralities, Callon's 4-quadrant strategic diagram, or VOSviewer native map/network exports. | Literature payload (`.json`, `.csv`, `.ris`) | `گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx` + `bibliometric_network_map.png` + `thematic_strategic_map.png` + `vosviewer_map.txt` + `vosviewer_network.txt` + `bibliometric_matrix.xlsx` (5 sheets). |
| **`citation-network-visualizer`** | [.agents/skills/citation-network-visualizer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/citation-network-visualizer) | User requests direct citation analysis, algorithmic historiography (HistCite chronomaps), Local Citation Score (LCS) vs Global Citation Score (GCS), Search Path Count (SPC) edge weights, or Main Path Analysis (MPA). | Direct citation payload (`.json` or `.csv`) | `گزارش_تحلیل_مسیر_اصلی_و_نگاشت_تاریخی_استنادات.docx` + `citation_chronomap.png` (300 DPI) + `main_path_trajectory.png` (300 DPI) + `citation_matrix.xlsx` (5 sheets). |
| **`digital-twin-academic-consultant`** | [.agents/skills/digital-twin-academic-consultant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/digital-twin-academic-consultant) | Automates Telegram client interactions, live MTProto userbot (`@GhaderiSaber`), automatic Google Drive project provisioning (4-tier taxonomy), proposal analysis & pricing quotation in Tomans, psychometric scale lookup, admin review desk (ID: 124911145), and chat export FAQ calibration. | Student proposal (.docx/.pdf/text), Telegram export (result.json), or Telegram queries | Standardized 4-tier Google Drive project folder, itemized pricing card (`telegram_card.txt`), `proposal_quote.md`, `quote_summary.json`, `calibrated_knowledge.json`. |
| **`academic-drive-project-organizer`** | [.agents/skills/academic-drive-project-organizer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-drive-project-organizer) | Organizes, audits, and tidies academic research projects across Google Drive (Pending, My Work, Finished), synchronizes Duzen backups, provisions standard 4-tier folders, and manages lifecycle transitions. | Target folder / Google Drive root / Duzen backup | Standardized 4-tier folders + `PROJECTS_AUDIT_REPORT.md` + `MASTER_PROJECT_CATALOG.xlsx` & `.md` + `reorganize_manifest.json`. |

---

## 3. Data & Artifact Workflow Architecture

The skills are modular and designed to pass standard artifacts between each other across the entire research, defense, and publication lifecycle:

```
[Research Idea / Variables] ──► (persian-proposal-builder)         ──► Proposal / Ch 1 & 3 (.docx)
            │                                                                   │
            ├─────────────────► (psychological-intervention-protocol-builder) ─┤ ──► Ch 3 Table & Protocol Manual
            │                                                                   ▼
[Foreign Theses / Studies]  ──► (persian-literature-review-builder)  ──► Chapter 2 Lit (.docx) + Matrix (.xlsx)
                                                                                │
                                                                                ▼
[In-Text Citations]         ──► (academic-reference-extractor)        ──► .enw / .ris / .txt
                                                                                │
                                                                                ▼
[SEM/CFA Model or RCT Design] ──► (psychometric-data-simulator)       ──► Simulated Data (.xlsx / .csv / lavaan.R)
                                                                                │
                                                                                ▼
[Raw Survey Responses]      ──► (psychometric-scale-resolver)         ──► data_scored.xlsx (Factors + Alphas)
                                                                                │
                                                                                ▼
[Scored Dataset + Hypo]     ──► (statistical-data-analyst)            ──► Chapter 4 Quant (.docx) + stats_results.json
                                                                                │
[Interviews / Focus Groups] ──► (qualitative-data-analyst)            ──► Chapter 4 Qual (.docx) + Matrix (.xlsx) + Diagram (.png)
                                                                                │
                                                                                ▼
[Findings + Lit Review]     ──► (persian-discussion-builder)          ──► Chapter 5 (.docx)
                                                                                │
                                                                                ▼
[All Chapters + Template]   ──► (persian-thesis-builder)              ──► Master Thesis (.docx)
                                                                                │
                                        ┌───────────────────────────────────────┴───────────────────────────────────────┐
                                        ▼                                                                               ▼
[Irandoc Flagged Thesis] ──► (irandoc-plagiarism-reducer)                                       [Completed Thesis & Data]
                                        │                                                                               │
                                        ▼                                                                               ▼
                            فصل_بازنویسی_ایرانداک.docx                                          (academic-article-writer)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Supervisor/Jury Review] ──► (persian-thesis-revision-assistant)                                Journal Manuscript (.docx)
                                        │                                                                               │
                                        ▼                                                                               ▼
                            Response Table (.docx)                                              (journal-submission-assistant)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Defense Session Prep]   ──► (persian-defense-presentation-builder)                             Submission Package (.docx)
                                        │                                                       ├── 1. Cover Letter
                                        ▼                                                       ├── 2. Title Page & CRediT
                            جلسه_دفاع.pptx (RTL OpenXML + Speaker Notes)                        ├── 3. Highlights (<= 85 chars)
                                                                                                └── 4. Response to Reviewers (R&R)
```

---

## 4. Python Environment & CLI Command Reference

### Irandoc Paraphrasing & Similarity Reduction:
```bash
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_کاهش_همانندجویی.docx"
```

### Intervention Protocol Compilation (Chapter 3 Table & Appendix Manual):
```bash
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به دردهای مزمن عضلانی-اسکلتی" \
  --output-docx "پروتکل_مداخله_اکت.docx" \
  --output-json "protocol_act.json"
```

### Defense Presentation Compilation (PowerPoint .pptx):
```bash
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy
```

### Journal Submission Collateral & Rebuttal Package Compilation:
```bash
# English Submission Package (ISI / Scopus Q1-Q4)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload.json" \
  --out-dir "./submission_package_en" \
  --lang en

# Persian Submission Package (علمی-پژوهشی / ISC)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload_fa.json" \
  --out-dir "./submission_package_fa" \
  --lang fa
```

### Systematic Review & Quantitative Meta-Analysis (PRISMA 2020 & Cochrane RoB 2):
```bash
# English Synthesis (Forest Plot, Funnel Plot, APA 7 Manuscript)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload.json" \
  --out-dir "./meta_analysis_output_en" \
  --lang en

# Persian Synthesis (علمی-پژوهشی / ISC)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload_fa.json" \
  --out-dir "./meta_analysis_output_fa" \
  --lang fa
```

### Monte Carlo Psychometric & Statistical Data Simulation (All Research Paradigms):
```bash
# 1. Instant Run via Research Presets (No JSON needed!)
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset hierarchical_regression --out-dir "./sim_reg"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset moderation_model1 --out-dir "./sim_mod"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset factorial_anova --out-dir "./sim_anova"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset mixed_split_plot --out-dir "./sim_rm"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset ancova_trial --out-dir "./sim_rct"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset logistic_diagnosis --out-dir "./sim_logistic"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset efa_battery --out-dir "./sim_efa"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset non_parametric_skewed --out-dir "./sim_np"

# 2. Custom Structural Equation Modeling (SEM) / CFA Mode
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_simulation_payload.json" \
  --out-dir "./simulated_sem_data" \
  --seed 42
```

### Qualitative Data Analysis & Chapter 4 Reporting (Thematic Analysis & Grounded Theory):
```bash
# Reflexive Thematic Analysis (Braun & Clarke 6-phase thematic network)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "thematic_payload.json" \
  --out-dir "./qualitative_output_thematic" \
  --lang fa

# Grounded Theory (Strauss & Corbin 6-dimension paradigmatic model)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "grounded_theory_payload.json" \
  --out-dir "./qualitative_output_gt" \
  --lang fa
```

### Chapter 2 Literature Review & Empirical Matrix Compilation:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json "ch2_payload.json" \
  --out-dir "./chapter2_output" \
  --lang fa
```

### Psychometric Scale Standardization & Validation:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "./psychometric_validation_output" \
  --lang fa
```

### Master Thesis Compilation:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "path/to/template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "Chapter1.docx" \
  --ch2 "Chapter2.docx" \
  --ch3 "Chapter3.docx" \
  --ch4 "Chapter4.docx" \
  --ch5 "Chapter5.docx" \
  --refs "References_Compiled.docx" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire"
```

### Questionnaire Lookup & Factor Scoring:
```bash
# Search Registry (Questionnaires.xlsx) & Google Drive Library
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"

# Inspect Scale Scoring Profile, Subscales, and Reverse Keys
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# Score Raw Survey Item Responses into Factors and Scale Composites
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### Run Automated Statistical Suite:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/data.xlsx" \
  --task auto \
  --config "path/to/config.json" \
  --out "stats_results.json"
```

### Run Specific Statistical Tasks:
- **Score Scale & Factors**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data_raw.xlsx --task score_scale --scale "Connor-Davidson Resilience Scale" --prefix "Q" --out-scored data_scored.xlsx`
- **Descriptives & Normality**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task descriptives --vars "Pre_Test,Post_Test,Resilience"`
- **Scale Reliability ($\alpha$)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task reliability --items "Q1,Q2,Q3,Q4,Q5"`
- **Intervention ANCOVA**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task ancova --dv Post_Test --group Group --covar Pre_Test`
- **Hierarchical Regression**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task regression --dv Outcome --step1 "Age,Gender" --step2 "Resilience,Self_Efficacy"`
- **Bootstrap Mediation (Model 4)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task mediation --x Stress --m Resilience --y Depression --bootstraps 2000`

### Generate APA 7 Persian Word Document:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

### End-to-End Academic Pipeline Orchestration:
```bash
# 1. Run turnkey pipeline preset (thesis_empirical, scale_validation, qualitative_study, meta_analysis, thesis_to_publication, bibliometric_pipeline)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project"

# 2. Run turnkey bibliometric preset (harvest -> bibliometrics -> historiography -> article -> submission)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --out-dir "./my_bibliometric_project" \
  --lang fa

# 3. Dry-run validation (inspect execution plan and dependency DAG without running)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --dry-run

# 4. Custom project configuration with custom step payloads
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --config "project_config.json" \
  --out-dir "./custom_academic_study"

# 5. Granular checkpointing & step control
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --resume-from statistics

python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --step discussion
```

### Thesis Integrity & Cross-Chapter Forensic Audit:
```bash
# Persian Audit (گزارش ممیزی رساله، همخوانی فرضیات و درجات آزادی، و تطبیق مراجع)
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --lang fa

# English / ISI Audit Mode
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results_en" \
  --lang en
```

### G*Power Sample Size & Statistical Power Calculation:
```bash
# 1. ANCOVA Sample Size Determination (Chapter 3 Methodology Text & Power Curve)
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test ancova \
  --groups 2 \
  --covariates 1 \
  --power 0.85 \
  --effect-size 0.25 \
  --out-dir "./sample_size_ancova" \
  --lang fa

# 2. Multiple Linear Regression Sample Size Determination
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test regression \
  --predictors 3 \
  --power 0.80 \
  --effect-size 0.15 \
  --out-dir "./sample_size_regression" \
  --lang fa

# 3. Comprehensive Multi-Design & SEM Power Analysis via JSON Payload
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --json "gpower_payload.json" \
  --out-dir "./gpower_results" \
  --lang fa
```

#### Run Academic Tone Polisher & Anti-AI Refiner (Skill #22):
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --json .agents/skills/ai-academic-tone-polisher/examples/sample_ai_text_payload.json \
  --sample persian_draft \
  --out-dir "./tone_results" \
  --lang fa
```

#### Run Literature Harvester & Empirical Metadata Extractor (Skill #23):
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "درمان مبتنی بر پذیرش و تعهد انعطاف‌پذیری روان‌شناختی فرسودگی شغلی" \
  --out-dir "./harvested_ch2" \
  --limit 10 \
  --lang fa
```

#### Run Bibliometric Science Mapping & Network Analyst (Skill #24):
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input .agents/skills/bibliometric-network-analyst/examples/sample_bibliometric_payload.json \
  --output-dir "./biblio_results" \
  --language fa \
  --min-freq 1 \
  --top-n 30
```

#### Run Citation Network Visualizer & Main Path Analysis (Skill #25):
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input .agents/skills/citation-network-visualizer/examples/sample_citation_network_payload.json \
  --output-dir "./historiography_results" \
  --language fa \
  --main-path global
```

#### Run Digital Twin Academic Consultant & Telegram Bot (Skill #26):
```bash
# 1. Analyze proposal and generate itemized quote in Tomans
python3 .agents/skills/digital-twin-academic-consultant/scripts/proposal_price_estimator.py \
  --input /path/to/proposal.docx \
  --telegram-card --admin

# 2. Ingest Telegram export to calibrate consulting FAQs
python3 .agents/skills/digital-twin-academic-consultant/scripts/telegram_chat_analyzer.py \
  --input /path/to/result.json --update-persona

# 3. Run MTProto userbot listener & Google Drive project manager
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --listen

# 4. List or sync managed projects in Google Drive
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --list-projects
```

#### Run Academic Drive Project Organizer (Skill #27):
```bash
# 1. Audit Pending Works and identify loose files & fragmented folders
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --audit -o .agents/skills/academic-drive-project-organizer/references

# 2. Cross-reference Duzen milestones and generate Master Catalog (.xlsx and .md)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --sync-duzen -o .agents/skills/academic-drive-project-organizer/references

# 3. Tidy a project folder into the 4-tier taxonomy (dry-run first, then apply)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --tidy --project "Client Name" --apply --clean-junk

# 4. Provision a new standard project folder
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --new-project "Client Name" --topic "Topic"
```

---

## 5. Defense Committee Quality Checklist

Before delivering any Chapter 4 or statistical output to a student, verify:
- [ ] Normality (Shapiro-Wilk) and Homogeneity of Variance (Levene) were formally checked and reported.
- [ ] For experimental studies, ANCOVA slope homogeneity ($Group \times Pretest$, $p > .05$) was tested.
- [ ] For mediation models, 95% bootstrap confidence intervals were reported (not Sobel test).
- [ ] All table numbers in the narrative match the table captions (`جدول ۱-۴`, `جدول ۲-۴`).
- [ ] All tables contain only 3 horizontal lines (no vertical lines).
- [ ] All $p$-values omit the leading zero ($p = .012$, not $p = 0.012$).
- [ ] Every hypothesis has an unambiguous concluding sentence affirming or rejecting it.

---

## 6. Questionnaire Registry & Psychometric Scale Directives

When preparing datasets, writing research proposals, or drafting methodology chapters:
1. **3-Tier Hierarchy**:
   - **Tier 1 (Project Folder)**: Prioritize client-provided questionnaires and project files.
   - **Tier 2 (Excel Registry - `Questionnaires.xlsx`)**: 4,880 rows mapping English/Persian names, subscales, items, Likert anchors, theoretical means, and reverse items.
   - **Tier 3 (Google Drive Library - `Pending Works/Questionnaire`)**: 2,206 original `.pdf`, `.docx`, and `.doc` instruments for item texts and scoring manuals.
2. **Reverse Scoring Formula**:
   - Always transform negatively keyed items using $Item_{\text{rev}} = (Min + Max) - Item$ before computing subscale sums, means, or Cronbach's alpha.
3. **Subscale & Total Composite Reporting**:
   - Report Cronbach's $\alpha$ for each subscale and total scale separately.
   - Confirm theoretical score ranges and midpoints ($Mean_{\text{theor}} = \frac{Min + Max}{2}$) in the narrative.

---

## 7. Digital Twin Academic Consultant & Telegram Operations

When operating the Telegram consultant daemon or handling client interactions:
1. **Proposal Ingestion & Extraction**: Support `.docx`, `.pdf`, and direct text proposals. Deterministically parse the research title, degree level, research design, sample size $N$ (normalizing Persian/Arabic digits), questionnaires, and required statistical packages.
2. **Modular Itemized Pricing**: Pricing quotations must be calculated and itemized in Tomans across standard phases (Chapter 3 Methodology, SimDat Data Simulation, Chapter 4 Statistics, Chapter 5 Discussion, Defense Slides, Integrity Audit) so students can commission individual modules or complete bundles.
3. **Telegram Message Layout**: Always format quotation cards with standard emojis, clear section dividers, itemized breakdowns in Tomans, and candidate guarantees (APA 7 compliance, free revisions for supervisor comments).
4. **Admin Approval Desk**: All draft quotations generated from proposals must be routed to Saber's Admin Desk (`124911145`) with actionable commands (`/approve_<ID>`, `/adjust_<ID>_<price>`) before final delivery.
5. **Persona & FAQ Calibration**: Periodically ingest Telegram Desktop exports (`result.json`) via `telegram_chat_analyzer.py --update-persona` to calibrate FAQs and ensure authentic reflection of Saber's consulting style.

