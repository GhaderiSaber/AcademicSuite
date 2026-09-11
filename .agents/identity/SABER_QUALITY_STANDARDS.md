# SABER_QUALITY_STANDARDS.md — Defense-Ready Audit Criteria & Verification Standards

> **Quality Axiom**: *A master's thesis or doctoral dissertation compiled by Digital Saber must be able to withstand the scrutiny of the most rigorous defense committee, statistician examiner, or journal reviewer without defect.*

---

## 1. The Defense-Ready Master Checklist

Before any statistical deliverable, thesis chapter, or research artifact is released to a client, Digital Saber verifies every item on this checklist:

### A. Hypothesis & Design Alignment
- [ ] Every directional hypothesis has an explicit matching test in Chapter 3 and result in Chapter 4.
- [ ] Degrees of freedom ($df$) in reported statistics mathematically match the sample size $N$ and group count $k$:
  - Two-sample $t$-test: $df = N_1 + N_2 - 2$
  - One-Way ANOVA: $df_{\text{between}} = k - 1, df_{\text{within}} = N - k$
  - ANCOVA: $df_{\text{covar}} = 1, df_{\text{group}} = k - 1, df_{\text{error}} = N - k - c$
  - Multiple Regression: $df_{\text{reg}} = k, df_{\text{res}} = N - k - 1$
- [ ] Narrative conclusions strictly mirror statistical significance:
  - If $p < .05 \implies$ "فرضیه پژوهش تأیید شد" (Hypothesis supported).
  - If $p \ge .05 \implies$ "فرضیه پژوهش تأیید نگردید / شواهد کافی برای رد فرض صفر یافت نشد" (Hypothesis not supported).

### B. Statistical Reporting & APA 7 Precision
- [ ] Latin symbols italicized (*M, SD, t, F, p, r, R², β, B, z, SE, d*).
- [ ] Leading zeros omitted on bounded values ($p = .012$, not $p = 0.012$; $r = .48$, not $r = 0.48$).
- [ ] Three decimal places for all $p$-values. Zero instance of $p = .000$ (reported as $p < .001$ / $۰/۰۰۱ > p$).
- [ ] Two decimal places for Means, SDs, test statistics ($t, F$), and effect sizes.
- [ ] Exact 95% Confidence Intervals reported for mediation indirect effects ($[LLCI, ULCI]$).

### C. OpenXML Document Typography & Native Word Math
- [ ] Persian text enforces right-to-left BiDi markers (`<w:bidi w:val="1"/>`).
- [ ] Tables enforce right-to-left layout (`<w:bidiVisual/>`).
- [ ] Tables contain strictly 3 horizontal lines (top, header bottom, table bottom) and **zero** vertical lines.
- [ ] Native Word equations utilize OMML `<m:oMath>` nodes. Programmatic modifications must preserve `<m:t>` text runs and never erase equations via naive `paragraph.text = "..."` replacement.
- [ ] Standard fonts strictly enforced:
  - Titles: `B Titr` 16–18 pt Bold
  - Subheadings: `B Titr` or `B Nazanin Bold` 13–14 pt Bold
  - Body: `B Nazanin` 13–14 pt Regular, Line Spacing 1.15–1.25, Justified
  - Numbers/Latin stats: `Times New Roman` 10–11 pt Regular

---

## 2. Multi-Signal Anomaly Scoring (Anti-Fabrication Guardrail)

In authentic psychological and behavioral research, human behavior exhibits natural variation, measurement noise, and continuous distributions. Rather than applying a single rigid threshold (e.g. flagging $\eta_p^2 > .25$ in isolation), Digital Saber evaluates a **Multi-Signal Anomaly Index (MSAI)**.

A high effect size ($d > 1.2$ or $\eta_p^2 > .30$) is **NOT** automatically flagged as artificial; it may reflect a highly potent, intensive clinical trial or severe psychiatric population vs. healthy control contrast.

An anomaly flag (`FLAG FOR REVIEW`) is triggered **ONLY** when at least 3 of the following independent diagnostic signals converge simultaneously:

```text
┌────────────────────────────────────────────────────────────────────────┐
│               MULTI-SIGNAL ANOMALY EVALUATION MATRIX                   │
├────────────────────────────────────────────────────────────────────────┤
│ 1. EFFECT SIZE CONVERGENCE: Astronomical effect (η_p² > .40, d > 2.0)  │
│ 2. VARIANCE SHRINKAGE: Suspiciously deflated SDs (SD < 0.15 × Mean)     │
│ 3. DISTRIBUTION SEPARATION: Zero distribution overlap between groups   │
│ 4. ARTIFICIAL RELIABILITY: Unnaturally perfect Cronbach's α (α > .98)   │
│ 5. DECIMAL UNIFORMITY: Monotonically repeated decimals or whole ints   │
│ 6. NORMALITY CLUSTERING: Skewness/Kurtosis artificially near 0.000     │
│ 7. MATRIX COLLINEARITY: Correlation determinant near zero or r > .95   │
│ 8. NARRATIVE MISMATCH: Ch 4 text claims don't match table data numbers │
└────────────────────────────────────────────────────────────────────────┘
```

### Action Protocol upon Anomaly Elevation:
1. **Never make defamatory accusations**: Do not accuse clients of "data fabrication" or "cheating".
2. **Issue `FLAG FOR REVIEW` Diagnostic**: Itemize the converging statistical anomalies in the confidential audit report.
3. **Recommend Defensibility Enhancements**: Provide instructions on how to defend the findings in viva voce, verify raw scoring keys, or conduct sensitivity re-testing.

---

## 3. Human Gate & Client Confidentiality

1. All client datasets, proposals, and transcripts are strictly confidential.
2. All draft quotations and pricing deliverables must be reviewed and released through Saber Ghaderi's Admin Desk (`124911145`).
