# ADVERSARIAL_CRITIC_PROTOCOL.md — Adversarial Deliberation & Quality Control

This specification defines the **Generator vs. Independent Critic Separation Architecture** in Digital Saber and Google Antigravity.

---

## 1. Core Architectural Principle: Strict Generator-Critic Decoupling

Under **Directive 12**, an agent or subagent that generates content (code, data, statistics, text, or presentations) is **strictly prohibited from evaluating, verifying, or approving its own work**. 

Self-certification leads to sycophantic rationalization, masked assumption violations, and unverified outputs. Therefore, every generative operation must be counterbalanced by an independent adversarial critic.

```text
  ┌─────────────────────────┐
  │     GENERATOR ROLE      │ ──► Produces Draft Artifact
  │    (academic-writer)    │     (e.g., Chapter_4_Results.docx)
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │   ADVERSARIAL CRITIC    │ ──► Evaluates Against Rigid Criteria
  │    (results-auditor)    │     (APA 7, Leading Zero, BiDi Decoupling)
  └────────────┬────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
[❌ REJECTION]     [✅ SIGN-OFF]
Return with        Emit results_qc_checklist.json
Remediation Defs   Proceed to Final Judge
```

---

## 2. Generator-Critic Pairing Matrix

| Domain Pipeline | Generator Role ("The Maker") | Adversarial Critic ("The Auditor") | Checkpoint Artifact Required |
| :--- | :--- | :--- | :--- |
| **Statistical Analysis** | `statistical-expert` | `statistical-auditor` | `statistical_audit_report.json` |
| **Numerical & APA Format** | `academic-writer` | `results-auditor` | `results_qc_checklist.json` |
| **Literature & Citations** | `literature-expert` | `evidence-auditor` | `citation_reconciliation_report.json` |
| **Oral Defense Slides** | `academic-writer` | `final-judge` | `viva_voce_readiness_score.json` |
| **Final Dissertation Release**| `digital-saber` | `final-judge` + Human Admin Desk | `release_approval_manifest.json` |

---

## 3. Adversarial Audit Contracts

### 3.1 Statistical Audit Contract (`statistical-auditor`)
The auditor does not generate models. It inspects `stats_results.json` and evaluates:
1. **Parametric Assumptions**: Normality (Shapiro-Wilk $p > .05$, Skewness $\in [-1, +1]$), Homogeneity of Variance (Levene's $p > .05$), Sphericity (Mauchly's $p > .05$), Multicollinearity (VIF $< 5$).
2. **Degrees of Freedom**: Verifies that $df_1$ and $df_2$ perfectly match sample size $N$ and design factors ($df_{\text{error}} = N - k$).
3. **Multi-Signal Anomaly Index (MSAI)**: Flags variance deflation, unrealistic Cohen's $d > 1.40$, or anomalous reliability coefficients.
*Verdict*: `APPROVED` or `REVISE` with specific mathematical deficits.

### 3.2 Results QC Contract (`results-auditor`)
The auditor inspects the compiled `.docx` or tabular data and evaluates:
1. **Persian Leading Zero Rule**: Flags any `.۰۵` or `.۰۰۱` lacking the leading zero (`۰.۰۵`, `۰.۰۰۱` required).
2. **Numerical Decimals**: Exactly 2 decimals for means, SDs, test statistics; exactly 3 decimals for $p$-values.
3. **Table Borders**: Enforces APA 7 three horizontal lines (Top 0.75 pt, Header bottom 0.5 pt, Table bottom 0.75 pt); flags vertical borders.
4. **BiDi Decoupling**: Verifies numeric cells are set to LTR (`rtl="0"`) in `Times New Roman`.

---

## 4. Release Gate: The Final Judge & Admin Desk
Even after generator and critic sign-offs, no document may be released directly to clients without:
1. **Viva Voce Defense Simulation**: `final-judge` evaluates readiness score (0–100) and prepares cross-examination questions.
2. **Human-in-the-Loop Gate (Directive 7 & 11)**: Major deliverables and draft quotations are routed to Saber's Admin Desk (`124911145`) for human sign-off before dispatch.
