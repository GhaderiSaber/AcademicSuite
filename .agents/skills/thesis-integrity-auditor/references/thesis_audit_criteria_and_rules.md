# Thesis Integrity Audit Criteria & Verification Standards

This document establishes the official forensic auditing guidelines, mathematical consistency formulas, citation reconciliation algorithms, and APA 7th Edition compliance rules enforced by **`thesis-integrity-auditor`** for Iranian and international graduate dissertations and theses.

---

## 1. The 4-Tier Severity Classification Model

Every finding identified during the thesis integrity audit is triaged into one of four standardized severity tiers:

| Severity Level | Defense Impact | Typical Causes | Action Required |
| :--- | :--- | :--- | :--- |
| **`CRITICAL`** | **Blocks Defense / Rejection** | Discrepancy between Chapter 1 hypotheses and Chapter 4 tests; Degrees of freedom ($df$) failing to match sample size ($N$); Direct contradictions between findings and Chapter 5 discussion conclusions. | Must be fully resolved before scheduling the oral defense or submitting to the graduate council. |
| **`MAJOR`** | **Mandatory Revision** | Orphaned in-text citations (> 5 references cited in text but missing from bibliography); Over 10% ghost references; Missing essential effect sizes ($\eta_p^2, d, R^2$) or confidence intervals in empirical hypotheses. | Must be corrected during pre-defense supervisor revisions. |
| **`MINOR`** | **Editorial Polish** | APA 7th Edition statistical formatting violations (leading zeros, $p = .000$, non-italicized Latin symbols); Inconsistent spelling of author surnames between text and references; Out-of-sequence table/figure numbering. | Corrected prior to final binding and digital submission. |
| **`INFO`** | **Quality Observation** | Stylistic recommendations; High concentration of older citations (> 10 years old) in Chapter 2; Observations on statistical power and post-hoc power remarks. | Advisory notes for candidate oral defense preparation. |

---

## 2. Hypothesis-Result-Discussion Alignment Engine

In a rigorous dissertation, every empirical hypothesis follows a closed, deterministic lifecycle:

$$\text{Ch 1 Formulation } (H_k) \iff \text{Ch 3 Operationalization} \iff \text{Ch 4 Statistical Test } (T_k) \iff \text{Ch 5 Theoretical Mechanism } (D_k)$$

### Alignment Verification Matrix
1. **Orphaned Hypothesis ($H_k \in \text{Ch 1}$, but $H_k \notin \text{Ch 4}$)**:
   - *Severity*: **CRITICAL**.
   - A hypothesis was stated in the proposal and Chapter 1, but no statistical test was conducted in Chapter 4.
2. **Phantom Hypothesis / Test ($T_k \in \text{Ch 4}$, but $T_k \notin \text{Ch 1}$)**:
   - *Severity*: **MAJOR**.
   - A statistical hypothesis test appears in Chapter 4 that was never formulated or justified in Chapter 1.
3. **Verdict Contradiction ($\text{Verdict}(\text{Ch 4}) \ne \text{Verdict}(\text{Ch 5})$)**:
   - *Severity*: **CRITICAL**.
   - Example: Chapter 4 reports $F(1, 56) = 2.14, p = .149$ (Hypothesis rejected / null not rejected), but Chapter 5 discusses the hypothesis as if it were confirmed!
4. **Neglected Discussion ($H_k \in \text{Ch 4}$, but $H_k \notin \text{Ch 5}$)**:
   - *Severity*: **MAJOR**.
   - Chapter 4 tested the hypothesis, but Chapter 5 failed to discuss its theoretical mechanism, comparison with prior literature, or psychological explanation.

---

## 3. Methodology-Statistics Numerical Consistency Formulas

Examiners evaluate whether test statistics ($t, F, \chi^2$) and their associated degrees of freedom ($df$) accurately reflect the sample size ($N$) described in Chapter 3.

### 3.1 Independent Samples $t$-Test
- **Total Sample Size**: $N = n_1 + n_2$
- **Degrees of Freedom**:
  $$df = n_1 + n_2 - 2 = N - 2$$
- **Welch's Heteroscedastic $t$-Test**:
  $$df_{\text{Welch}} \le N - 2 \quad (\text{Calculated via Satterthwaite equation})$$

### 3.2 One-Way Analysis of Variance (ANOVA)
- **Between-Groups $df$**: $df_{\text{between}} = k - 1$ (where $k$ is number of groups)
- **Within-Groups (Error) $df$**: $df_{\text{within}} = N - k$
- **Total $df$**: $df_{\text{total}} = N - 1$
- **Verification Rule**: $df_{\text{between}} + df_{\text{within}} = N - 1$.

### 3.3 Analysis of Covariance (ANCOVA)
- For $k$ groups, $c$ continuous covariates, and total sample size $N$:
  $$df_{\text{group}} = k - 1$$
  $$df_{\text{error}} = N - k - c$$
  $$df_{\text{total}} = N - 1$$
- *Example*: 2 groups ($k = 2$), 1 pre-test covariate ($c = 1$), total $N = 60$:
  $$df_{\text{error}} = 60 - 2 - 1 = 57 \implies F(1, 57)$$
  If the candidate reports $F(1, 58)$ or $F(1, 56)$, an arithmetic error has occurred.

### 3.4 Multivariate Analysis of Variance / Covariance (MANOVA / MANCOVA)
- Hypothesis $df_1 = p \times (k - 1)$ (where $p$ is number of dependent variables)
- Residual $df_2$ must match Wilks' Lambda approximate $F$-distribution degrees of freedom.

### 3.5 Multiple Linear Regression
- For sample size $N$ and $k$ predictor variables:
  $$df_{\text{regression}} = k$$
  $$df_{\text{residual}} = N - k - 1$$
  $$df_{\text{total}} = N - 1$$
- *Example*: Predicting Depression from Stress, Anxiety, and Coping ($k = 3$) with $N = 120$:
  $$df_{\text{residual}} = 120 - 3 - 1 = 116 \implies F(3, 116)$$

### 3.6 Pearson Correlation ($r$)
- **Degrees of Freedom**:
  $$df = N - 2$$
- $t$-transformation: $t = \frac{r\sqrt{N-2}}{\sqrt{1-r^2}}$ with $df = N - 2$.

---

## 4. In-Text Citation & Bibliographic Reconciliation

The auditor conducts exhaustive bidirectional reconciliation between all in-text citations and the bibliography list.

### 4.1 Citation Extraction Patterns
- **Parenthetical Citation (English)**: `(Author, Year)` or `(Author & Author, Year)` or `(Author et al., Year)`
- **Narrative Citation (English)**: `Author (Year)` or `Author and Author (Year)` or `Author et al. (Year)`
- **Persian In-Text Citation**:
  - `(نام‌خانوادگی، سال)` — e.g. `(فتحی‌آشتیانی، ۱۳۹۸)`
  - `نام‌خانوادگی (سال)` — e.g. `بک و همکاران (۲۰۱۹)`
  - Dual English/Persian citations: `(Beck et al., 2020; قاسم‌زاده، ۱۳۹۹)`

### 4.2 Reconciliation Status Definitions
1. **`MATCHED` (Valid)**: In-text citation corresponds to exactly one matching entry in the References list (author surname and publication year match).
2. **`ORPHANED_IN_TEXT` (Critical/Major)**: Citation appears in body text but has **no matching entry** in the References list.
3. **`SUPERFLUOUS_REFERENCE` (Major/Minor)**: Reference appears in the bibliography list but was **never cited** anywhere in the body text (Ghost reference).
4. **`YEAR_DISCREPANCY` (Minor)**: Author surname matches, but publication year differs (e.g. text says `2018`, reference entry says `2019`).
5. **`SPELLING_DISCREPANCY` (Minor)**: Very close string distance / Levenshtein similarity $\ge 0.85$ between in-text author and reference author.

---

## 5. APA 7th Edition Statistical Typography Checks

The auditor scans all paragraphs and table cells for violations of APA 7th Edition statistical rules:

1. **Leading Zero Rule**:
   - Numbers that cannot exceed 1.0 ($p$-values, correlations $r$, $R^2$, $\eta_p^2$, Cronbach's $\alpha$, McDonald's $\omega$, factor loadings $\lambda$, beta weights $\beta$) must **omit** the leading zero:
     - Correct: $p = .014$, $r = .48$, $\eta_p^2 = .19$.
     - Violation: $p = 0.014$, $r = 0.48$, $\eta_p^2 = 0.19$.
2. **Illegal Software Output ($p = .000$)**:
   - Statistical software (SPSS, SAS) prints `.000` when $p < .0005$.
   - Reporting $p = .000$ is strictly forbidden by APA 7 and Iranian dissertation councils.
   - It must be reported as $p < .001$ (یا در فارسی: $p < ۰/۰۰۱$).
3. **Italicization of Latin Statistical Symbols**:
   - $M, SD, t, F, p, r, R^2, z, SE, d, k, N, n$ must be italicized.
   - Greek letters ($\alpha, \beta, \eta^2, \chi^2, \omega, \lambda, \theta$) remain non-italic.
4. **Decimal Precision**:
   - Means, standard deviations, test statistics ($t, F$), effect sizes: 2 decimal places.
   - $p$-values: exactly 3 decimal places (e.g. $p = .038$).
5. **Missing Effect Sizes**:
   - Significant findings ($p < .05$) must report an effect size ($d$ for $t$-test, $\eta_p^2$ for ANOVA/ANCOVA, $R^2$ for regression).

---

## 6. Composite Thesis Integrity Score Formula

The auditor computes an overall **Thesis Integrity Score (TIS)** on a $0 - 100\%$ scale:

$$\text{TIS} = 100 - \left( 15 \times N_{\text{critical}} + 5 \times N_{\text{major}} + 1 \times N_{\text{minor}} \right)$$

$$\text{Final TIS} = \max(0, \min(100, \text{TIS}))$$

### Readiness Tiers:
- **$90 - 100\%$ (Defense Ready - آماده دفاع)**: Excellent coherence. No critical or major discrepancies. Minor polish only.
- **$75 - 89\%$ (Supervisor Review Ready - نیازمند بازبینی استاد راهنما)**: Some citation or formatting issues. Core findings intact.
- **$50 - 74\%$ (Substantial Revision Required - نیازمند اصلاحات اساسی)**: Missing statistical tests, $df$ mismatches, or high orphan citation count.
- **$< 50\%$ (Critical Discrepancies - عدم انطباق ساختاری)**: Fundamental disconnect between hypotheses, analyses, and conclusions.
