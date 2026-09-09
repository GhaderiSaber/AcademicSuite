# Iranian Graduate Research Proposal Guide (راهنمای جامع تدوین پروپوزال پژوهشی)

This reference outlines the structural, stylistic, and methodological standards required for graduate research proposals (طرح تحقیق / پروپوزال کارشناسی ارشد و دکتری) in Psychology, Counseling, and Educational Sciences across Iranian universities (وزارت علوم، تحقیقات و فناوری و دانشگاه آزاد اسلامی).

---

## 1. Stylistic Mandate: Continuous Academic Prose (سیاست نثر پیوسته و دانشگاهی)

> [!IMPORTANT]
> **Strict Prohibition Against Bullet Outlines in Narrative Sections:**
> Approved Iranian graduate proposals are formal academic manuscripts, NOT bullet-point summaries.
> - **Problem Statement, Significance, Methodology, Validity, Reliability, and Statistical Analysis MUST be written in continuous, cohesive paragraphs (نثر متصل و پخته آکادمیک).**
> - Every paragraph must be well-developed (4–8 sentences) with complete syntactic structures, scholarly tone, and smooth transitional phrases (e.g., *«بدین منظور...»*, *«در وهله نخست...»*, *«در ادامه جهت راستی‌آزمایی فرضیات...»*, *«افزون بر این...»*, *«بر این اساس...»*).
> - Sentence fragments and bulleted lists are strictly banned in narrative explanations.
> - Bullet points are only permitted for itemized inclusion/exclusion criteria or demographic attributes, and even then, each bullet must be a grammatically complete sentence.
> - Eliminate robotic generative AI clichés (*«شایان ذکر است که»*, *«در این راستا»*, *«به طور کلی می‌توان گفت»*, *«این امر نشان‌دهنده آن است که»*) and strictly enforce official Persian orthography and half-spaces (*نیم‌فاصله*).

---

## 2. Footnote Standards (قواعد پانویس‌نویسی اصطلاحات و مراجع)

Proposals adhere to the academic footnote rules from `persian-thesis-builder` and `persian-academic-translation`:

1. **English Equivalents in Footnotes**:
   - Do NOT insert English terms in parentheses inside running Persian body text.
   - Use the Persian equivalent in text and attach an English footnote on **first mention** (e.g., «بدخبرگردی[^1]» $\rightarrow$ `[^1]: Doomscrolling`).
2. **Foreign Authors**:
   - Transliterate author names in Persian text: «شارما و همکاران[^2] (2022)».
   - Footnote the Latin name on **first occurrence only**: `[^2]: Sharma et al.`.
3. **First Occurrence Only**:
   - Every unique term, construct, and author is footnoted **exactly once**. Subsequent occurrences use solely the Persian term/name.
4. **Unified Numbering Stream**:
   - Terminology and author citations share a single continuous sequential footnote stream (۱، ۲، ۳...).
5. **Punctuation & Quote Placement**:
   - Footnote markers are placed **immediately AFTER closing quotation marks or punctuation** (e.g. `«بدخبرگردی»[^1]`, never `«بدخبرگردی[^1]»`).
6. **OpenXML Word Native Footnotes**:
   - Must use native Word footnotes (`<w:footnoteReference>`), Persian numerals in text, Times New Roman 9.5 pt LTR in `footnotes.xml`, and explicit `<w:rtl/>` on every text run to avoid line-breaking bugs.

---

## 3. Standard Proposal Architecture Overview

```text
پروپوزال طرح پژوهش
├── بخش الف: اطلاعات عمومی طرح (عنوان فارسی و انگلیسی، مشخصات دانشجو، اساتید راهنما و مشاور)
├── بخش ب: بیان مسئله و اهمیت موضوع (Problem Statement & Significance)
│   ├── ۱. بیان مسئله اساسی (مدل هرم وارونه در قالب پاراگراف‌های متصل)
│   ├── ۲. اهمیت و ضرورت پژوهش (ضرورت نظری و کاربردی در پاراگراف‌های تفصیلی)
│   ├── ۳. اهداف پژوهش (هدف اصلی و اهداف اختصاصی)
│   ├── ۴. فرضیه‌ها یا سؤالات پژوهش (فرضیه‌های جهت‌دار و مشخص)
│   └── ۵. تعاریف نظری و عملیاتی متغیرها (تعریف نظری با ارجاع به نظریه‌پرداز اصلی، تعریف عملیاتی با نمرات ابزار)
├── بخش ج: روش‌شناسی پژوهش (Methodology)
│   ├── ۱. طرح پژوهش و چارچوب روش‌شناختی (Taxonomy دقیق بر حسب هدف، ماهیت و روش گردآوری داده‌ها)
│   ├── ۲. جامعه آماری، حجم نمونه و منطق علمی برآورد (G*Power، کلاین/هیر، و معیارهای ورود و خروج)
│   ├── ۳. روش نمونه‌گیری و شیوه اجرای میدانی
│   ├── ۴. ابزارهای گردآوری اطلاعات (معرفی تاریخچه، ابعاد، طیف نمره‌گذاری، نمرات معکوس، و جدول دوزبانه گویه‌ها)
│   ├── ۵. پروتکل ترجمه و انطباق فرهنگی (در پژوهش‌های هنجاریابی: پروتکل ۴ مرحله‌ای رفت‌وبرگشت ITC و WHO)
│   ├── ۶. روش احراز روایی ابزار (روایی صوری کمی/کیفی با شاخص تأثیر، روایی محتوایی CVR و CVI، روایی سازه EFA/CFA، روایی همگرا/تشخیصی و ملاکی)
│   ├── ۷. روش ارزیابی پایایی ابزار (همسانی درونی با آلفای کرونباخ و امگای مک‌دونالد، ثبات زمانی با بازآزمایی و ICC)
│   └── ۸. روش‌ها و ابزارهای تجزیه‌وتحلیل داده‌ها (آمار توصیفی، بررسی پیش‌فرض‌های پارامتریک، آمار استنباطی، و نرم‌افزارهای SPSS و AMOS)
├── بخش د: ملاحظات اخلاقی (کد اخلاق، رضایت آگاهانه، رازداری، حق انصراف، بیانیه هلسینکی)
└── بخش هـ: فهرست منابع و مآخذ (منابع فارسی و انگلیسی مطابق با APA 7th Edition)
```

---

## 4. Section-by-Section Drafting Blueprint

### A. Statement of the Problem (بیان مسئله اساسی)
Must follow the **Inverted Triangle Model (مدل هرم وارونه)** in continuous prose:
1. **Introduction & Macro Context (مقدمه و بستر موضوع)**: Introduce the broad behavioral/psychological domain (e.g., mental health in digital environments, marital burnout, transdiagnostic constructs).
2. **Construct Conceptualization (تعریف و ابعاد متغیرها)**: Thoroughly define the independent and dependent variables citing foundational theorists.
3. **Epidemiological Manifestation & Pathology in Iran (شیوع، نشانگان و پیامدها در جامعه ایران)**: Discuss clinical, educational, or societal repercussions supported by national and international literature.
4. **Theoretical & Empirical Gaps (خلاء پژوهشی)**: Explicitly demonstrate what previous studies lacked (e.g., absence of standardized Iranian instruments, conflicting findings, lack of structural mediation).
5. **The Proposed Solution (چرایی و رسالت پژوهش حاضر)**: Formulate how the current research addresses and resolves this gap.

### B. Significance & Necessity (اهمیت و ضرورت پژوهش)
Must develop two distinct, robust paragraphs:
- **Theoretical Importance (اهمیت نظری)**: Deepening psychometric and conceptual boundaries, testing theoretical mechanisms, bridging Western models into Iranian socio-cultural context.
- **Applied/Practical Importance (اهمیت کاربردی)**: Direct utilities for university counseling centers, clinical psychologists, policymakers, schools, and mental health interventions.

### C. Conceptual vs. Operational Definitions (تعاریف نظری و عملیاتی متغیرها)
- **Conceptual Definition (تعریف نظری)**: Written as a complete paragraph citing the primary author/theorist defining the latent construct.
- **Operational Definition (تعریف عملیاتی)**: Written as a complete paragraph specifying the exact instrument, total item count, Likert scoring format (e.g., 1 to 5 or 1 to 7), theoretical score range (Min–Max), and psychological interpretation of higher/lower scores.

---

## 5. Methodology Blueprints by Study Archetype

### Archetype 1: Scale Standardization & Psychometric Adaptation (هنجاریابی و اعتبارسنجی مقیاس)
1. **Design**: Descriptive psychometric cross-sectional validation conforming to International Test Commission (ITC, 2017) guidelines.
2. **Sampling Logic**:
   - Minimum 10–20 participants per item (Kline, 2016; Hair et al., 2019).
   - Cross-Validation / Split-Half split: $N \approx 350–400$ ($N_1 = 175$ for EFA; $N_2 = 175$ for CFA).
   - Power analysis justification using G*Power 3.1 ($\alpha = .05, 1-\beta = .95$).
3. **Cross-Cultural Adaptation Protocol**:
   - Forward translation by 2 independent bilingual psychologists $\to$ Reconciliation meeting $\to$ Backward translation by 2 blind bilingual translators $\to$ Harmonization and expert committee sign-off.
4. **Validity Protocol**:
   - **Face Validity**: Qualitative review + Quantitative Item Impact Score $\ge 1.5$ (Frequency % $\times$ Importance Mean on 5-point scale).
   - **Content Validity**: 
     * Lawshe (1975) CVR: Essential rating by 10–15 experts, using formula $CVR = \frac{N_e - N/2}{N/2}$; cut-off $> 0.49$ for $N=15$.
     * Waltz & Bausell (1981) CVI: Relevance, Clarity, Simplicity on 4-point scale; $I-CVI \ge 0.78$, $S-CVI/Ave \ge 0.90$.
   - **Construct Validity**:
     * EFA in SPSS: KMO $\ge 0.80$, Bartlett's Test $p < .001$, Maximum Likelihood / Principal Axis Factoring with Promax rotation, Scree plot inspection, factor loading threshold $\ge .40$.
     * CFA in AMOS: Structural Equation Modeling with standard goodness-of-fit indices: $\chi^2/df < 3.0$, $CFI \ge .95$, $TLI \ge .95$, $RMSEA \le .06$, $SRMR \le .08$.
     * Convergent & Discriminant: Fornell & Larcker (1981) Average Variance Extracted ($AVE \ge .50$) and Composite Reliability ($CR \ge .70$).
     * Criterion Validity: Pearson correlation against validated criterion scales (e.g., BAI Anxiety, FOMO).
5. **Reliability Protocol**:
   - Internal Consistency: Cronbach's $\alpha \ge .80$ and McDonald's $\omega \ge .80$, Corrected Item-Total Correlation $> .40$.
   - Temporal Stability: Test-Retest on $N = 30–50$ subsample across 2–4 weeks, Intraclass Correlation Coefficient ($ICC \ge .75$).
6. **Data Analysis Plan**:
   - Continuous paragraph detailing univariate normality screening (Skewness & Kurtosis within $\pm 2$), descriptive statistics, EFA, CFA, and correlation matrices via SPSS 28 and AMOS 26.

### Archetype 2: Correlational & Structural Equation Modeling (مدل‌یابی معادلات ساختاری)
- Sample size: $N = 200–350$ (5–15 participants per observed parameter).
- Statistical analysis: Multivariate normality screening, Pearson r matrix, SEM path coefficients, Bootstrap mediation with 5,000 resamples and 95% bias-corrected confidence intervals in AMOS.

### Archetype 3: Experimental & Quasi-Experimental (طرح‌های آزمایشی و نیمه‌آزمایشی)
- Design: Pretest-posttest with control group (and 1–2 month follow-up).
- Sample size: Minimum 15–20 participants per cell calculated via G*Power 3.1 ($F$-test ANCOVA, $\alpha = .05, 1-\beta = .80, f = .25$).
- Protocol: Itemized clinical intervention sessions (ACT, CBT, Schema Therapy, MBSR) complete with theoretical rationale, experiential techniques, and homework.
- Statistical analysis: Univariate or Multivariate Analysis of Covariance (ANCOVA/MANCOVA) in SPSS after testing assumptions (homogeneity of slopes, Levene's test, Shapiro-Wilk).

---

## 6. Proposal Acceptance Defense Checklist (چک‌لیست کنترل کیفیت پیش از تحویل)

Before submitting or sharing proposals:
- [ ] Title accurately reflects Independent, Dependent, and Target Population.
- [ ] Problem Statement follows the inverted triangle model in continuous prose without fragmented bullet points.
- [ ] Footnote English equivalents instead of in-text parentheses on first mention (`[^1]: Doomscrolling`).
- [ ] Transliterate foreign authors in Persian with Latin surname footnoted on first mention only (`[^2]: Sharma et al.`).
- [ ] Enforce the "First Occurrence Only" rule and maintain a single continuous footnote numbering stream.
- [ ] Place footnote markers immediately AFTER closing quotation marks (`«سازه»¹`, never inside).
- [ ] Conceptual definitions cite seminal theorists; operational definitions specify exact scales, scoring, and score ranges.
- [ ] Sample size is mathematically justified (G*Power, Kline/Hair rules, or Krejcie-Morgan) with detailed inclusion/exclusion criteria.
- [ ] Scale tables include English original text, standardized Persian translation, and baseline psychometric properties.
- [ ] Validity and reliability protocols include exact cut-off thresholds (CVR, CVI, EFA loading, CFA fit indices, alpha, omega, ICC).
- [ ] Statistical analysis plan explicitly names software versions (SPSS 28, AMOS 26) and specific statistical procedures.
- [ ] Ethical clearance principles (informed consent, anonymity, right to withdraw, data protection) are fully articulated.
- [ ] Document typography adheres strictly to *B Titr* (headings), *B Nazanin* 12–13 pt (body text), 1.35 line spacing, 0.35-inch first-line indent, and zero awkward page breaks.
- [ ] Word file compiled with native OpenXML footnotes (`<w:footnoteReference>`), `w:rtl` on all text runs, and `compatibilityMode = 15`.

