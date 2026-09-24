# Chapter 4 Architecture & Statistical Reporting Specification (Directives 3, 3.1, 4)

Canonical structural and reporting standards for Chapter 4 (یافته‌های پژوهش / Research Findings).

---

## 1. Regression & Association Hypotheses (3-Table Suite)

For every linear prediction or multiple regression hypothesis, three synchronized tables are required:
1. **Table 1: Bivariate Correlation Matrix**: Pearson $r$, significance $p$, sample size $N$, and descriptive statistics ($M, SD$).
2. **Table 2: Model Summary & ANOVA**: Multiple $R, R^2$, Adjusted $R^2, SE$, and ANOVA test statistics ($F, df_1, df_2, p$).
3. **Table 3: Regression Coefficients**: Unstandardized ($B, SE$), standardized beta ($\beta$), $t$-statistic, $p$-value, and collinearity diagnostics (Tolerance, VIF).
- **Narrative Requirement**: Substantive 4-element academic interpretation positioned immediately above each table caption. [Enforcement: `academic_writer_guard.py`]

---

## 2. Structural Equation Modeling (SEM) Macro-to-Micro Protocol

1. **Macro SEM Evaluation (Reported First)**:
   - **Table A (Goodness-of-Fit)**: 11 Hu & Bentler (1999) indices ($\chi^2, df, \chi^2/df, p$, CFI, TLI, GFI, AGFI, NFI, RMSEA 90% CI, SRMR).
   - **Figure B (Path Diagram)**: High-resolution visual model with standardized coefficients ($\beta$) and $R^2$.
   - **Table C (Direct Paths)**: Parameter estimates ($B, SE, \beta, z, p$) for all direct structural paths.
   - **Table D (Indirect Paths)**: 5,000 BCa bootstrap resamples with 95% confidence intervals [LLCI, ULCI] and exact $p$-values.
2. **Micro Hypothesis Subsections**:
   - Each structural hypothesis must possess a dedicated subsection evaluating effect size, non-zero interval inclusion, and formal empirical verdict.

---

## 3. Chapter 4 Summary & Decision Matrix

Chapter 4 concludes with an extensive 1-to-2 page empirical synthesis:
1. **Sample Demographic Profile**: Disaggregated demographic frequency tables.
2. **Master Decision Matrix Table (`جدول ماتریس جمع‌بندی نهایی فرضیات`)**:
   - Columns: Hypothesis Number, Conceptual Statement, Statistical Test, Key Parameters ($F/t/\beta$), $p$-value, Final Verdict (تأیید / عدم تأیید).
3. **Conceptual Transition Bridge**: Empirical transition paragraph preparing findings for Chapter 5 synthesis.

---

## 4. Empirical Boundary Invariant (Strict Chapter Separation)
- **Zero Literature Citations in Chapter 4**: Theoretical concordance and comparisons to external empirical literature (e.g. Bandura, Beck, Gross) belong exclusively in **Chapter 5**.
- **Prose-Only Chapter 5 Invariant (Directive 3.1)**: Chapter 4 houses 100% of statistical tables; Chapter 5 strictly prohibits tables (`|---|` or `<w:tbl>`). [Enforcement: `academic_writer_guard.py`]
