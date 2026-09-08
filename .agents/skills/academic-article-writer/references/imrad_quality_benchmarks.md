# International Journal Quality Benchmarks (IMRaD & JARS Standards)

This guide specifies the international peer-review standards required by prestigious indexed journals (**Web of Science / ISI, Scopus Q1/Q2, and Iranian ISC علمی-پژوهشی**) based on the **APA 7th Edition** and **JARS (Journal Article Reporting Standards)**.

A journal article is **NOT** a copy-paste of a thesis. A thesis is exhaustive and detailed (100–200 pages); an article is a focused, high-density scientific argument (15–25 pages, 4,500–6,500 words).

---

## 1. The IMRaD Quality Funnel

```
               [INTRODUCTION]
             Broad problem context
           Theoretical framework & gap
              Explicit hypotheses
                       │
                       ▼
                    [METHOD]
           Targeted, reproducible design
         Sample size power, validated scales
                       │
                       ▼
                   [RESULTS]
         Condensed findings & APA 7 tables
              Clear hypothesis test
                       │
                       ▼
                  [DISCUSSION]
           Deep theoretical mechanisms
         Global literature & implications
              Broad societal impact
```

---

## 2. Section-by-Section Quality Benchmarks

### A. Introduction (مقدمه) — Target: 1,000–1,200 words
Must follow the **4-Paragraph Funnel**:
1. **Paragraph 1: Societal & Epidemiological Burden**:
   - Establish why this topic matters globally and locally.
   - Avoid generic openers ("Since the dawn of time..."). Start directly with epidemiological prevalence, mental health burden, or societal impact.
2. **Paragraph 2: Theoretical Framework**:
   - Ground the constructs in an established theory (e.g., Beck's Cognitive Schema, Gross's Emotion Regulation, Bandura's Social Cognitive Theory).
   - Show how the variables theoretically interact.
3. **Paragraph 3: Critical Literature Synthesis & The "Gap"**:
   - Synthesize empirical findings from the last 3–5 years (2020–2025).
   - Highlight the specific conflict, unanswered question, or unexamined mediator/moderator that existing literature has neglected.
4. **Paragraph 4: Present Study & Directional Hypotheses**:
   - State how the study addresses the gap.
   - Conclude with clear, numbered directional hypotheses based on theory.

---

### B. Method (روش پژوهش) — Target: 800–1,100 words
Reviewers evaluate reproducibility and methodological rigor:
1. **Design & Participants**:
   - Specify exact research design (e.g., randomized pretest-posttest control group, cross-sectional structural equation modeling).
   - **Sample Size Justification**: Must report formal power analysis using **G*Power 3.1** (e.g., medium effect size $f = .25$, $\alpha = .05$, power $1-\beta = .80$, minimum required $N = 30$).
   - State inclusion and exclusion criteria clearly.
2. **Measures & Instrumentation**:
   - For every scale: Author(s), year, number of items, response format (e.g., 5-point Likert from 1 = Strongly Disagree to 5 = Strongly Agree).
   - Cite sample items.
   - Report reliability in current study (Cronbach's $\alpha \ge .70$, McDonald's $\omega$) and confirmatory factor analysis (CFA) fit indices from local validation studies.
3. **Procedure & Ethical Considerations**:
   - Ethics approval committee and protocol number.
   - Informed consent and anonymized data handling.
   - Treatment protocol details (number of sessions, duration, core therapeutic modules).
4. **Statistical Analysis Plan**:
   - Software used (e.g., SPSS v26, Python `scipy`/`statsmodels`, AMOS/SmartPLS).
   - Assumption testing procedures (Shapiro-Wilk for normality, Levene for homogeneity, VIF for collinearity).
   - Primary analytical models and effect size metrics (partial $\eta^2$, Cohen's $d$, standardized $\beta$, 95% bootstrap CIs).

---

### C. Results (یافته‌ها) — Target: 800–1,000 words
High-impact results are concise, objective, and non-redundant:
1. **Preliminary Analysis**:
   - Brief summary of descriptives ($M, SD$, skewness, kurtosis) and normality confirmation.
   - Table 1: Descriptives and bivariate correlation matrix (Pearson $r$ or Spearman $\rho$) with significance asterisks (*, **).
2. **Primary Hypothesis Testing**:
   - Present hypothesis-by-hypothesis findings.
   - **Never repeat every cell of a table in the text**: Highlight only the key test statistics, $p$-values, effect sizes, and adjusted means.
   - Table 2: ANCOVA table (for experimental studies) OR Hierarchical Regression table (for predictive studies).
   - Table 3: Mediation / Path analysis with 5,000 bootstrap confidence intervals.
3. **APA 7 Table Rules**:
   - Zero vertical borders.
   - Exactly 3 horizontal borders: Top, Header underline, and Bottom.
   - Titles positioned **above** the table; notes/asterisks positioned **below**.

---

### D. Discussion (بحث) — Target: 1,200–1,500 words
Must follow the **5-Stage Interpretive Progression**:
1. **Stage 1: Brief Recap of Principal Findings**:
   - Non-technical summary of whether hypotheses were supported.
2. **Stage 2: Theoretical Mechanism (Why did this happen?)**:
   - The intellectual core of the paper. Explain the psychological mechanisms that produced the result (cognitive appraisal, attentional control, self-worth, behavioral inhibition).
3. **Stage 3: Integration with Global & Domestic Literature**:
   - Compare findings against both international (ISI) and regional studies.
   - If findings contradict prior literature, provide scientifically grounded explanations (e.g., cultural differences, clinical severity, dosage of intervention).
4. **Stage 4: Practical & Clinical Implications**:
   - Concrete applications for psychotherapists, clinical psychologists, school counselors, or health policymakers.
5. **Stage 5: Strengths, Methodological Limitations & Future Directions**:
   - Acknowledge limitations honestly (self-report bias, non-random sampling, lack of longitudinal follow-up).
   - Propose specific, actionable future research questions.
   - End with a strong, definitive **Concluding Statement**.

---

## 3. Top 5 Reasons for Reviewer Rejections & How to Prevent Them

| Common Rejection Reason | How This Skill Prevents It |
| :--- | :--- |
| **"Lack of theoretical depth in discussion"** | The skill mandates referencing established cognitive/behavioral models and explaining the psychological mechanism. |
| **"Unjustified sample size / Low statistical power"** | Requires formal G*Power sample size calculations and power estimates in the Method section. |
| **"Failure to report effect sizes and confidence intervals"** | Enforces APA 7 rules: every $F$ or $t$ test must report effect sizes ($\eta_p^2, d$) and 95% CIs. |
| **"Bloated, thesis-like writing style"** | Condenses lengthy thesis passages into tight, high-density scientific prose focused strictly on the core research questions. |
| **"Outdated literature"** | Mandates that at least 50% of cited empirical studies in Introduction and Discussion be published within the last 3–5 years. |
