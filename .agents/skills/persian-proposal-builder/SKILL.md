---
name: persian-proposal-builder
description: >-
  Expert academic research proposal (طرح تحقیق / پروپوزال) and methodology drafting skill for Iranian master's
  and doctoral students in Psychology, Counseling, and Behavioral Sciences. Guides formulating clear titles,
  structuring the problem statement (بیان مسئله) via the inverted-triangle model, formulating directional hypotheses,
  defining conceptual and operational definitions, designing rigorous methodologies (G*Power sample size,
  validated Persian instruments, statistical analysis plans), and compiling defense-ready Word (.docx) proposal documents.
---

# Persian Research Proposal Builder Skill (نگارش پروپوزال و طرح پژوهش)

This skill guides the agent in drafting defense-ready, high-acceptance **graduate research proposals (پروپوزال طرح پژوهش)** for Master's theses and Ph.D. dissertations in Psychology, Counseling, Educational Sciences, and Behavioral Health.

It conforms strictly to the standards of the Iranian Ministry of Science, Ministry of Health, and Islamic Azad University research councils, producing structured proposals that seamlessly feed into **Chapter 1 (کلیات پژوهش)** and **Chapter 3 (روش‌شناسی پژوهش)** of the master thesis compiler.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user asks to write, refine, or review a **graduate research proposal (پروپوزال / طرح تحقیق)**.
2. The user needs help formulating **hypotheses (فرضیه‌ها)**, **objectives (اهداف)**, or **conceptual and operational definitions (تعاریف نظری و عملیاتی)**.
3. The user needs to draft **Chapter 1 (کلیات پژوهش)** or **Chapter 3 (روش‌شناسی پژوهش)** of a thesis.
4. The user needs sample size calculation logic (G*Power, Kline/Hair 10-20x rule, or Krejcie-Morgan) and selection of standardized Persian psychometric instruments.
5. The user needs to formulate the methodology for **scale validation, psychometric adaptation, or test standardization (هنجاریابی و اعتبارسنجی مقیاس)**.

---

## 2. Mandatory Writing Style: Continuous Academic Prose (سیاست نثر پیوسته و آکادمیک)

> [!IMPORTANT]
> **STRICT BAN ON FRAGMENTED BULLET-POINT PARAGRAPHS:**
> Real, approved Iranian university proposals (in psychology, counseling, and behavioral sciences) are written in **mature, continuous, and connected academic paragraphs (نثر پیوسته، فخیم، منسجم و دانشگاهی)**. 
> - **NEVER** output fragmented bullet outlines or clipped, telegraphic notes for the problem statement, significance, methodology, validity, reliability, or statistical analysis.
> - **Every section must consist of full, well-developed paragraphs** with complete verbal predicates (جملات کامل با ترکیب‌های نحوی غنی دانشگاهی), theoretical depth, and formal transitional connectors (e.g., «بدین منظور...»، «در وهله نخست...»، «در ادامه جهت راستی‌آزمایی ساختار عاملی...»، «افزون بر این...»، «بر این اساس...»).
> - Bullet points are **ONLY** permitted for itemized inclusion/exclusion criteria or demographic variable lists, and even in those cases, items must be grammatically complete sentences.
> - Eliminate robotic generative AI cliches (*«شایان ذکر است که»*, *«در این راستا»*, *«به طور کلی می‌توان گفت»*, *«این امر نشان‌دهنده آن است که»*) and enforce proper Persian half-spaces (نیم‌فاصله).

---

## 3. Footnote & Terminology Standards (قواعد پانویس‌نویسی اصطلاحات و منابع)

Proposals must strictly adhere to the academic footnote rules adopted across the suite (`persian-thesis-builder` and `persian-academic-translation`):

1. **Footnote English Equivalents Instead of In-Text Parentheses (پانویس اصطلاحات به جای پرانتز در متن)**:
   - **DO NOT** clutter Persian body text with Latin phrases or abbreviations inside parentheses (e.g., avoid «عدم تحمل بلاتکلیفی (Intolerance of Uncertainty - IU)» or «تحلیل عاملی تأییدی (CFA)» in running text).
   - Write fluent Persian equivalents in the body text and place authentic English terms and acronyms in **footnotes (پانویس)** on their **first mention**:
     - *In Text*: «بدخبرگردی[^1]» $\rightarrow$ *Footnote*: `[^1]: Doomscrolling`
     - *In Text*: «تحلیل عاملی اکتشافی[^2]» $\rightarrow$ *Footnote*: `[^2]: Exploratory Factor Analysis (EFA)`
     - *In Text*: «تحلیل عاملی تأییدی[^3]» $\rightarrow$ *Footnote*: `[^3]: Confirmatory Factor Analysis (CFA)`
     - *In Text*: «کمیسیون بین‌المللی آزمون‌ها[^4]» $\rightarrow$ *Footnote*: `[^4]: International Test Commission (ITC)`
2. **Transliterate Latin Authors in Persian Text + Footnote on First Occurrence (پانویس نام مؤلفان خارجی در نخستین ارجاع)**:
   - In running text, foreign author names are transliterated into Persian, followed by year in parentheses: e.g., «شارما و همکاران[^5] (2022)».
   - Attach a footnote containing the original Latin author surname(s) on the **first occurrence only**:
     - *Footnote*: `[^5]: Sharma et al.`
     - *Footnote*: `[^6]: Kline`
     - *Footnote*: `[^7]: Hair et al.`
     - *Footnote*: `[^8]: Lawshe`
     - *Footnote*: `[^9]: Waltz & Bausell`
     - *Footnote*: `[^10]: Fornell & Larcker`
3. **Strict "First Occurrence Only" Rule (قاعده عدم تکرار پانویس)**:
   - Footnote each unique specialized term, scale, and author **exactly once** in the entire document.
   - On all subsequent occurrences, use solely the established Persian transliteration/term without adding redundant footnote markers.
4. **Unified Footnote Stream (جریان یکپارچه شماره‌گذاری)**:
   - Both in-text references (Latin author names) and technical terminology share a single continuous sequential footnote stream (۱، ۲، ۳...).
5. **Quote & Punctuation Placement (محل قرارگیری پانویس نسبت به گیومه و علائم نگارشی)**:
   - Footnote markers must always appear **immediately AFTER closing quotation marks or punctuation** (e.g., «بدخبرگردی»[^1] or «آزمون فرضیه»،[^2] — NEVER inside `«بدخبرگردی[^1]»`). Placing footnote tokens inside quotation marks splits the run and causes punctuation inversion.
6. **Native OpenXML Word Implementation (قواعد فنی تولید در Word)**:
   - Footnotes in `.docx` must be compiled as **true native OpenXML Word Footnotes** (`<w:footnoteReference>` linked to `word/footnotes.xml`), **never** raw bracket characters like `[^1]`.
   - In-text references must use Persian numerals (`<w:rStyle w:val="FootnoteReference"/>`, `<w:rtl/>`, `<w:lang w:val="fa-IR"/>`).
   - Footnote text in `footnotes.xml` must be Left-aligned (`<w:jc w:val="left"/>`), font `Times New Roman` 9.5 pt, single line spacing.
   - **Crucial BiDi Line-Break Prevention**: Every single Persian text run (`<w:r>`) in paragraphs containing footnotes must explicitly include `<w:rtl/>` in its `<w:rPr>` to prevent Word's layout engine from prematurely breaking lines around footnote markers.
   - `compatibilityMode = 15` in `word/settings.xml` must be set for modern Word layout engines.

---

## 4. Typography, Heading Hierarchy & Header Standards (قواعد عناوین، تیترها و سربرگ‌ها)

Proposals must strictly adhere to the academic heading and typography hierarchy established in `persian-thesis-builder`:

### A. Heading Hierarchy & Font Specifications

| Level / Element | Persian Name | Font & Weight | Size | Alignment & Direction | Spacing (Before / After) | OpenXML Specification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Document Title (`Heading 1`)** | عنوان اصلی طرح / سربرگ | `B Titr` Bold | 16–18 pt | **Right-aligned (RTL)** | Before: 24–28 pt, After: 14–18 pt | `<w:pStyle w:val="Heading1"/>`, `<w:keepNext/>`, `<w:bidi w:val="1"/>`, `<w:jc w:val="right"/>` |
| **Major Sections (`Heading 2`)** | تیترهای اصلی بخش‌ها (۱، ۲، ۳...) | `B Titr` Bold | 14 pt | **Right-aligned (RTL)** | Before: 14 pt, After: 6 pt | `<w:pStyle w:val="Heading2"/>`, `<w:keepNext/>`, `<w:bidi w:val="1"/>`, `<w:jc w:val="right"/>` |
| **Subsections (`Heading 3`)** | تیترهای فرعی (۱-۱، ۲-۱...) | `B Nazanin Bold` (or `B Titr`) | 13 pt (or 12 pt Titr) | **Right-aligned (RTL)** | Before: 8–10 pt, After: 4 pt | `<w:pStyle w:val="Heading3"/>`, `<w:keepNext/>`, `<w:bidi w:val="1"/>`, `<w:jc w:val="right"/>` |
| **Sub-subsections (`Heading 4`)** | زیرتیترهای خرد | `B Nazanin Bold` | 12 pt | **Right-aligned (RTL)** | Before: 6 pt, After: 2 pt | `<w:pStyle w:val="Heading4"/>`, `<w:keepNext/>`, `<w:bidi w:val="1"/>`, `<w:jc w:val="right"/>` |
| **Body Paragraphs (`Normal`)** | متن اصلی پاراگراف‌ها | `B Nazanin` Regular | 12.5–13.5 pt | **Justified (RTL)** | Line spacing: 1.25–1.35, After: 6 pt | `<w:bidi w:val="1"/>`, `<w:jc w:val="both"/>`, First Line Indent: 0.35 in |
| **Table & Figure Captions** | عنوان جداول و نمودارها | `B Nazanin Bold` | 11 pt | **Right-aligned (RTL)** | Before: 8 pt, After: 4 pt | Titles above tables; notes/sources below tables |
| **Document / Page Header** | سربرگ صفحه و عنوان بالایی | `B Nazanin` Regular | 9–10 pt | **Right-aligned (RTL)** | Single line, clean academic | `<w:bidi w:val="1"/>`, `<w:jc w:val="right"/>`, zero political prefixes |

### B. Core Structural & OpenXML Directives

1. **Strictly RTL & Right-Aligned Headers (راست‌چین بودن کامل سربرگ و عناوین)**:
   - All document titles, banner titles, section headers, and running page headers must be strictly Right-to-Left (RTL) and **Right-aligned** (`WD_ALIGN_PARAGRAPH.RIGHT` in DOCX, `direction: rtl; text-align: right;` in HTML/CSS).
   - Ragged left, centered banners, or LTR alignments are unacceptable for Persian academic proposals.
2. **Elimination of State / Political Pre-Titles (حذف پیش‌عنوان‌های زائد دولتی)**:
   - Never insert generic or political pre-titles such as «جمهوری اسلامی ایران —» or bureaucratic government slogans in proposal headers.
   - Use clean, authoritative academic headers: «طرح پژوهش پایان‌نامه کارشناسی ارشد (پروپوزال)» or «راهنمای تخصصی تدوین بخش روش‌شناسی و تحلیل آماری طرح پژوهش».
3. **Native Word Navigation Pane Integration (`<w:pStyle>`)**:
   - Every heading must be linked to standard Word heading styles (`Heading 1`, `Heading 2`, `Heading 3`) so that university review panels and supervisors can navigate the proposal structure seamlessly using Word's Navigation Pane (`نمای نقشه سند`).
4. **Orphan Heading Prevention (`<w:keepNext/>`)**:
   - In OpenXML, all heading paragraphs must enforce `<w:keepNext/>` (`p.paragraph_format.keep_with_next = True` or XML node insertion). This ensures a heading never sits isolated at the bottom of a page without at least two lines of the following narrative text.
5. **Dual Font Binding Protection (`<w:rFonts>`)**:
   - Every heading run must enforce `<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="B Titr" w:eastAsia="B Titr"/>` to prevent Word fallback engines on macOS/Windows from substituting headings with system fonts like Arial or Calibri.

### C. Critical OpenXML Standards: Text Direction vs. Text Alignment (`CT_PPr` & `styles.xml`)

> [!CAUTION]
> **TWO DISTINCT CONTROLS IN MICROSOFT WORD: DIRECTION vs. ALIGNMENT**
> In Microsoft Word, there are two separate and independent paragraph controls:
> 1. **Text Direction (جهت متن)**: Left-to-Right (LTR) vs. Right-to-Left (RTL / راست‌به‌چپ).
> 2. **Text Alignment (تراز متن)**: Left (چپ‌چین), Center (وسط‌چین), Right (راست‌چین), and Justify (هم‌تراز/تراز دوطرفه).
>
> **The BiDi Alignment Inversion Rule in Microsoft Word:**
> - When a paragraph is given RTL direction via `<w:bidi w:val="1"/>`, Microsoft Word's natural leading-edge alignment is **RIGHT**.
> - If `<w:jc w:val="right"/>` is explicitly added to an RTL paragraph, Word's rendering engine interprets `w:val="right"` as the trailing edge, causing Word on macOS/Windows to flip the alignment to **ALIGN LEFT (چپ‌چین)**!
> - **The Golden Rule for RTL Right-Aligned Headings & Headers**:
>   - Set `<w:bidi w:val="1"/>` for Direction.
>   - **OMIT** `<w:jc>` entirely for Right Alignment. Word will naturally and strictly align it to the RIGHT.
>   - For Justified narrative text: emit `<w:jc w:val="both"/>`.
>   - For Centered titles/tables: emit `<w:jc w:val="center"/>`.
>   - For LTR English references: omit `<w:bidi>` and emit `<w:jc w:val="left"/>`.
>
> **Strict Child Element Sequencing (`CT_PPr`):**
> Under ISO/IEC 29500-1 / ECMA-376, `<w:pPr>` children must follow this exact order:
> `w:pStyle` $\to$ `w:keepNext` $\to$ `w:bidi` $\to$ `w:spacing` $\to$ `w:ind` $\to$ `w:jc`
> - Always construct `<w:pPr>` using a unified XML generator (`set_strict_pPr`) enforcing this sequence.
> - Always inject enhanced RTL definitions (`<w:bidi w:val="1"/>`, `<w:rtl/>`, and `B Titr`/`B Nazanin` font bindings) directly into `Normal`, `Heading1`, `Heading2`, `Heading3`, and `Heading4` within `word/styles.xml`, omitting `<w:jc w:val="right"/>`.
> - Always ensure `<w:sectPr>` contains `<w:bidi/>` at section level.
> - For all tables, always append `<w:bidiVisual/>` to `table._tbl.tblPr` and enforce `set_strict_pPr` on cell paragraphs.

## 5. Proposal Architecture & Key Components

The proposal follows the standard Iranian university template:

| Section | Title in Persian | Purpose & Core Content |
| :--- | :--- | :--- |
| **Header** | **اطلاعات عمومی طرح** | Exact title (Persian & English), Student, Supervisor, and Advisor details. |
| **Section 1** | **بیان مسئله اساسی** | Inverted Triangle: Context $\to$ Construct definitions $\to$ Pathology/Prevalence in Iran $\to$ Research gap $\to$ Study purpose (in full continuous prose). |
| **Section 2** | **اهمیت و ضرورت** | Theoretical necessity (deepening scientific literature) and Practical necessity (applications for clinics, schools, organizations) in separate cohesive paragraphs. |
| **Section 3** | **اهداف پژوهش** | General objective (هدف کلی) + Specific objectives (اهداف اختصاصی/ویژه). |
| **Section 4** | **فرضیه‌ها و سؤالات** | Directional hypotheses (فرضیه‌های جهت‌دار) for all direct, comparative, and mediation pathways. |
| **Section 5** | **تعاریف نظری و عملیاتی** | **نظری**: Continuous paragraph citing original theorist. **عملیاتی**: Full paragraph explaining the exact questionnaire, Likert range, min/max score, and interpretation. |
| **Section 6** | **روش‌شناسی پژوهش** | Research design, Target population, Sampling logic (G*Power & Kline/Hair ratios), Psychometric instruments with bilingual tables, Cultural adaptation protocol, Validity protocol (Face, CVR, CVI, EFA, CFA), Reliability protocol (Alpha, Omega, Test-Retest ICC), and Statistical analysis plan (SPSS & AMOS). |
| **Section 7** | **ملاحظات اخلاقی** | Informed consent, confidentiality, right to withdraw, Helsinki code compliance. |
| **Section 8** | **منابع و مآخذ** | APA 7th Edition bilingual bibliography (Persian and English). |

---

## 6. Methodological Design Guardrails by Study Type

### A. Scale Standardization & Psychometric Adaptation (طرح‌های هنجاریابی و روان‌سنجی)
For proposals validating, adapting, or standardizing a psychometric instrument:
1. **Research Design**: Fundamental-applied, descriptive psychometric and cross-sectional scale validation design adhering to International Test Commission (ITC, 2017) and WHO guidelines.
2. **Sample Size Determination**:
   - Rule of thumb (Kline, 2016; Hair et al., 2019): 10 to 20 participants per item/observed variable (e.g., 15 items $\to$ 150–300 participants).
   - Cross-Validation / Split-Half logic: Recommended total $N = 350–400$, enabling division into two independent subsamples ($N_1 \approx 175$ for EFA, and $N_2 \approx 175$ for CFA).
   - Statistical power: G*Power 3.1 justification ($\alpha = .05, 1-\beta = .95$, medium effect size $w = .30$ or $f^2 = .15$).
3. **Cross-Cultural Adaptation Protocol**:
   - 4-stage Forward-Backward Translation Protocol (Forward translation by 2 independent experts $\to$ Synthesis & reconciliation $\to$ Backward translation to English by 2 blind bilinguals $\to$ Harmonization & expert committee review).
4. **Validity Protocol**:
   - **Face Validity**: Qualitative (10–15 target users) + Quantitative (Item Impact Score $\ge 1.5$ on 5-point importance scale).
   - **Content Validity**: Qualitative (expert panel of 10–15 university professors) + Quantitative (Lawshe's CVR with formula and cut-off table, e.g., CVR $> 0.49$ for 15 experts; and Waltz & Bausell CVI with $I-CVI \ge 0.78$ and $S-CVI/Ave \ge 0.90$).
   - **Construct Validity**: 
     * EFA: KMO ($\ge .80$), Bartlett's Test of Sphericity ($p < .001$), Maximum Likelihood or PAF extraction, Promax/Varimax rotation, Scree plot, minimum loading $\ge .40$.
     * CFA: Structural equation modeling in AMOS/LISREL with multi-index fit thresholds ($\chi^2/df < 3.0$, $CFI \ge .95$, $TLI \ge .95$, $RMSEA \le .06$, $SRMR \le .08$).
     * Convergent & Discriminant: Fornell & Larcker criteria ($AVE \ge .50, CR \ge .70$) and criterion validity with Pearson correlation against established scales.
5. **Reliability Protocol**:
   - Internal Consistency: Cronbach's $\alpha \ge .80$ and McDonald's $\omega \ge .80$ (essential modern psychometrics), plus corrected item-total correlation $> .40$.
   - Temporal Stability: Test-Retest on a 30–50 participant subsample with 2–4 weeks interval and Intraclass Correlation Coefficient ($ICC \ge .75$ under Two-way Random Effects Model).
6. **Data Analysis Plan**:
   - Descriptive statistics (Mean, SD, Skewness and Kurtosis within $\pm 2$ for normality screening, frequency/percentage distributions).
   - Inferential statistics (KMO, Bartlett, EFA, CFA, CVR, CVI, Pearson r, Cronbach's alpha, McDonald's omega, ICC).
   - Software specification: SPSS 28 and AMOS 26.

### B. Correlational / Structural Equation Modeling (طرح‌های همبستگی و معادلات ساختاری)
- Sample size: Minimum $N = 200–350$ or 10–20 participants per observed variable.
- Instruments: Query `Questionnaires.xlsx` for validated Persian scales with reported Iranian alpha and validity.
- Analysis: SPSS for descriptive/correlations, AMOS for SEM path analysis, bootstrap mediation (5,000 resamples).

### C. Experimental / Intervention Studies (طرح‌های آزمایشی و نیمه‌آزمایشی)
- Design: Pretest-posttest with control group (and optional follow-up).
- Sample size: Minimum 15–20 participants per group calculated via G*Power 3.1 ($F$-test ANCOVA, $\alpha = .05$, Power $= .80$, $f = .25$).
- Protocol: Standardized clinical manual (ACT, CBT, Mindfulness) summarized session by session.
- Analysis: Univariate or Multivariate Analysis of Covariance (ANCOVA/MANCOVA) in SPSS after testing assumptions (homogeneity of regression slopes, Levene's test, Shapiro-Wilk).

---

## 6. Execution Workflow

1. **Intake Research Variables**:
   Gather the research topic, variables, target population, and proposed design.
2. **Consult Reference Guides**:
   - Read [proposal_structure_guide.md](file:///Users/saber/.gemini/config/plugins/academic_suite/skills/persian-proposal-builder/references/proposal_structure_guide.md) for detailed structural standards and continuous prose models.
3. **Formulate Comprehensive Continuous Prose**:
   Draft every section in mature, flowing academic paragraphs adhering to Section 2 and Section 4 above.
4. **Generate Word Document**:
   Run the document generation script:
   ```bash
   python3 .agents/skills/persian-proposal-builder/scripts/generate_proposal_docx.py \
     --json "proposal_input.json" \
     --out "پروپوزال_طرح_پژوهش.docx"
   ```
5. **Quality Review**:
   Verify Persian typography (*B Titr* for headings, *B Nazanin* 12–13 pt for body text, 1.35 line spacing, 0.35-inch first-line indent, RTL OpenXML flags, and zero trailing page spillovers).
