---
name: thesis-integrity-auditor
description: Automated academic jury, forensic proofreader, and cross-chapter consistency verification engine for graduate theses and dissertations in psychology, counseling, educational measurement, and behavioral sciences. Audits hypothesis-result-discussion alignment (Chapter 1 <-> Chapter 4 <-> Chapter 5), verifies methodology sample sizes and degrees of freedom (t-test, ANOVA, ANCOVA, regression df), executes bidirectional in-text citation and bibliography reconciliation (orphaned citations vs ghost references, year mismatches), and enforces APA 7th Edition statistical formatting rules (leading zeroes, p = .000 violations, effect sizes). Generates publication-grade defense audit reports (.docx), 5-sheet citation reconciliation workbooks (.xlsx), and machine-readable JSON summaries.
---

# `thesis-integrity-auditor` — Academic Thesis & Cross-Chapter Integrity Auditor (Skill #20)

`thesis-integrity-auditor` is the automated forensic proofreader, mock jury auditor, and quality-assurance engine of the **AcademicSuite**. It cross-audits graduate theses and dissertations across all 5 chapters, statistical calculations, and bibliography lists prior to submission to supervisors, dissertation examiners, defense councils, or Irandoc.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user requests **auditing, checking, or verifying a graduate thesis, dissertation, or research project** for consistency and errors.
- The user asks: *"Check if all my hypotheses in Chapter 1 are tested in Chapter 4 and discussed in Chapter 5."*
- The user wants to **verify degrees of freedom ($df$) and sample sizes ($N$)** across statistical tests.
- The user asks to **reconcile in-text citations against the reference list** (finding orphaned citations or ghost bibliography entries).
- The user asks to **audit APA 7th Edition compliance** for statistical notation (leading zeros, $p = .000$, non-italic symbols).
- The user asks for a **pre-defense readiness audit** or **mock examiner check** before submitting to the defense committee.

---

## 2. Core Forensic Dimensions & Discrepancy Taxonomy

### 1. Hypothesis-Result-Discussion Alignment (همخوانی فرضیه‌ها، یافته‌ها و بحث)
- **Untested / Orphan Hypothesis (`CRITICAL`)**: Hypothesis stated in Chapter 1 has no corresponding test in Chapter 4.
- **Phantom Statistical Test (`MAJOR`)**: Test conducted in Chapter 4 with no formal hypothesis formulated in Chapter 1.
- **Verdict Contradiction (`CRITICAL`)**: Chapter 4 confirms/rejects a hypothesis, but Chapter 5 discusses the opposite outcome.
- **Neglected Discussion (`MAJOR`)**: Hypothesis tested in Chapter 4 has no dedicated theoretical discussion in Chapter 5.

### 2. Methodology & Numerical Statistical Verification (روش‌شناسی و درجات آزادی)
- **Sample Size Breakdown Discrepancy (`CRITICAL`)**: Sum of group sizes ($n_1 + n_2$) fails to match total $N$.
- **ANCOVA Degrees of Freedom Error (`CRITICAL`)**: Error degrees of freedom does not match $df_{\text{error}} = N - k - c$.
- **Multiple Regression Degrees of Freedom Error (`MAJOR`)**: Residual degrees of freedom does not match $df_{\text{residual}} = N - k - 1$.
- **$t$-Test Degrees of Freedom Error (`MAJOR`)**: Independent $t$-test $df$ fails to equal $N - 2$.

### 3. Bidirectional Citation Reconciliation (صحت‌سنجی دوطرفه مراجع)
- **Orphaned In-Text Citation (`CRITICAL`/`MAJOR`)**: Cited in body text but missing from the References section.
- **Ghost Reference in Bibliography (`MAJOR`/`MINOR`)**: Listed in References but never cited anywhere in text.
- **Year Discrepancy (`MINOR`)**: Publication year differs between body citation and bibliography entry.
- **Author Surname Spelling Mismatch (`MINOR`)**: Slight typographic variation in author name.

### 4. APA 7th Edition Statistical Typography (استانداردهای نگارش آمار)
- **Leading Zero Violations (`MINOR`)**: Number bounded by 1.0 ($p, r, R^2, \eta_p^2$) reporting zero before decimal point ($p = 0.024$).
- **Illegal Software Output (`MINOR`)**: Reporting $p = .000$ instead of $p < .001$.
- **Missing Effect Sizes (`MAJOR`/`MINOR`)**: Significant finding without $d, \eta_p^2$, or $R^2$.

---

## 3. Thesis Integrity Score (TIS) & Readiness Thresholds

$$\text{TIS} = \max(0, 100 - (15 \times N_{\text{critical}} + 5 \times N_{\text{major}} + 1 \times N_{\text{minor}}))$$

- **$90 - 100\%$**: **Defense Ready (آماده جلسه دفاع)** — Excellent internal coherence; minor editorial polish only.
- **$75 - 89\%$**: **Supervisor Revision Required (نیازمند بازبینی استاد راهنما)** — Core findings intact; citation or $df$ adjustments needed.
- **$50 - 74\%$**: **Substantial Revision Required (نیازمند اصلاحات اساسی)** — Missing tests or degrees of freedom errors block defense.
- **$< 50\%$**: **Critical Discrepancies (عدم انطباق ساختاری)** — Severe structural disconnect requiring comprehensive re-analysis.

---

## 4. CLI Command Reference

### Standard Run (Persian Output):
```bash
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --lang fa
```

### English Run (International Journal / ISI Thesis Mode):
```bash
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results_en" \
  --lang en
```

### Custom Passing Score Threshold:
```bash
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --threshold 85.0
```

---

## 5. Generated Deliverables

1. **`گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx`** (or `Thesis_Integrity_Audit_Report.docx`):
   - Professional Word document formatted with native RTL OpenXML BiDi and authentic Iranian typography (*B Titr*, *B Nazanin*).
   - Executive TIS scorecard, 4 domain finding tables with severity badges, diagnostic details, actionable fixes, and pre-defense checklist.
2. **`annotated_citations.xlsx`**:
   - 5-sheet master workbook: `Overview & Summary`, `Matched Citations`, `Orphaned In-Text`, `Ghost Bibliography`, `Year Mismatches`.
3. **`thesis_audit_summary.json`**:
   - Machine-readable audit ledger for CI/CD pipelines, dashboard integration, and orchestrator workflows.
