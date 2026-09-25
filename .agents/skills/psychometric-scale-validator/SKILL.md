---
name: psychometric-scale-validator
description: Comprehensive scale validation and psychometrics including CVR/CVI, EFA, CFA, convergent/discriminant validity, Omega/Alpha, IRT Graded Response Model, and ROC curves.
---

# Psychometric Scale Validator Skill

This skill turns Antigravity into an expert psychometrician and measurement specialist. It executes end-to-end psychometric adaptation, standardization, and validation workflows under Classical Test Theory (CTT) and Modern Item Response Theory (IRT).

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Conducting scale standardization, adaptation, or psychometric validation studies.
- Evaluating Content Validity: Lawshe (1975) CVR against panel critical thresholds ($p < .05$), Waltz & Bausell / Lynn (1986) I-CVI ($\ge .78$) and S-CVI/Ave ($\ge .80$).
- Verifying Construct Validity: EFA (KMO $\ge .70$, Bartlett sphericity $p < .001$), CFA ($\chi^2/df < 3$, CFI/TLI $\ge .90$, RMSEA/SRMR $\le .08$), and Fornell-Larcker ($AVE \ge .50$, $CR \ge .70$, $\sqrt{AVE} > r$).
- Estimating Modern Reliability: McDonald's $\omega$ ($\omega_t, \omega_h \ge .70$) alongside Cronbach's $\alpha$, test-retest ICC, and split-half reliability.
- Estimating Modern IRT Parameters: Samejima's Graded Response Model (GRM) for Likert items, item discrimination ($a_i$), category thresholds ($b_{ik}$), Infit/Outfit MNSQ, IIF/TIF information functions, and Differential Item Functioning (DIF).
- Determining Clinical Cut-offs: Receiver Operating Characteristic (ROC) curve analysis, Area Under Curve (AUC $\ge .80$), and Youden's $J$ index.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- The task is simply scoring an established questionnaire using fixed scoring keys $\to$ use `psychometric-scale-resolver`.
- The task tests structural relations, mediation, or regression between established constructs rather than measuring tool properties $\to$ use `statistical-data-analyst`, `mediation`, or `sem`.
- The task requires raw data cleaning, reverse item coding, or missing value imputation without psychometric evaluation $\to$ use `data-cleaning`.

## 3. REQUIRED DATA
- **Raw Item Matrix**: Item-level responses (`.xlsx`, `.csv`) with $N \ge 200\text{--}300$ for EFA/CFA, or $N \ge 300\text{--}500$ for IRT GRM estimation.
- **Expert Ratings**: Content validity ratings from expert panel ($N \ge 5\text{--}15$ judges) for CVR/CVI calculation.
- **Retest Subsample**: 2-4 week retest data ($n \ge 30\text{--}50$) for test-retest ICC.
- **Criterion/Gold Standard**: Binary diagnostic classification for ROC curve analysis.

## 4. ASSUMPTIONS
1. **Unidimensionality**: Each factor/subscale reflects a single dominant latent trait (essential for IRT and McDonald's $\omega$).
2. **Local Independence**: Conditioning on the latent trait, item responses are statistically independent ($Q_3 < .20$).
3. **Monotonicity**: Probability of endorsing higher categories increases monotonically with latent trait $\theta$.
4. **Adequate Sampling Adequacy**: KMO $> .70$ and significant Bartlett's test ($p < .001$).
5. **No Multicollinearity among Indicators**: Indicator correlations $r < .85$.

## 5. DECISION TREE

```
Scale Validation & Psychometric Assessment
  │
  ├─► Qualitative / Expert Phase:
  │     ├─► Lawshe CVR: Test against panel size critical threshold (p < .05)
  │     └─► Lynn I-CVI (>= .78) & S-CVI/Ave (>= .80)
  │
  ├─► Factor Structure Evaluation:
  │     ├─► Exploratory / First-Time Adaptation:
  │     │     └─► [EFA (Exploratory Factor Analysis)]
  │     │           - Check KMO (>= .70) & Bartlett (p < .001)
  │     │           - Extraction: Principal Axis Factoring (PAF) or Maximum Likelihood
  │     │           - Rotation: Oblimin / Promax (correlated factors)
  │     │           - Retain factors: Parallel Analysis / Scree inflection
  │     │           - Factor loadings: lambda >= .40, cross-loadings < .30
  │     │
  │     └─► Established Theoretical Structure:
  │           └─► [CFA (Confirmatory Factor Analysis)]
  │                 - Fit indices: Chi2/df < 3, CFI >= .90, TLI >= .90, RMSEA <= .08
  │                 - Convergent: AVE >= .50, CR >= .70
  │                 - Discriminant: sqrt(AVE) > inter-construct r (or HTMT < .85)
  │
  ├─► Item Response Theory (IRT) Evaluation:
  │     ├─► Polytomous Likert Items (3+ ordinal categories):
  │     │     └─► [Samejima Graded Response Model (GRM)]
  │     │           - Baker (2001) discrimination: a >= 0.65 (Moderate to Very High)
  │     │           - Infit / Outfit MNSQ: 0.60 to 1.40
  │     │           - Test Information Function (TIF) & conditional SE(theta)
  │     │           - Differential Item Functioning (DIF) across demographics
  │     │
  │     └─► Dichotomous Items (Correct / Incorrect):
  │           └─► [2-PL / 3-PL IRT or Rasch Model]
  │
  └─► Diagnostic Cut-off Determination:
        └─► [ROC Curve Analysis]
              - AUC >= .80, Youden's J = Sensitivity + Specificity - 1
              - Generate Z-score, T-score, and Percentile Rank norms
```

## 6. EXECUTION SCRIPT
Execute deterministic psychometric calculations:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "output_psychometrics" \
  --lang fa
```

## 7. OUTPUT CONTRACT
The skill produces:
- `psychometric_summary.json`:
  ```json
  {
    "scale_name": "Example Resilience Scale",
    "sample_size": 350,
    "cvr_cvi": {"mean_cvr": 0.85, "s_cvi_ave": 0.92},
    "cfa": {"chi2_df": 2.14, "cfi": 0.942, "tli": 0.931, "rmsea": 0.057, "srmr": 0.048},
    "construct_validity": {"ave": 0.54, "cr": 0.82, "fornell_larcker_pass": true},
    "reliability": {"cronbach_alpha": 0.86, "mcdonald_omega": 0.88, "icc": 0.84},
    "irt_grm": {"mean_discrimination": 1.42, "infit_mnsq_range": [0.82, 1.18]},
    "roc": {"auc": 0.89, "optimal_cutoff": 28.5, "sensitivity": 0.86, "specificity": 0.82}
  }
  ```
- Physical institutional OpenXML Word report: `Chapter_4_Psychometrics.docx`.
- Master 6-sheet Excel matrix: `psychometric_validation_matrix.xlsx`.
- 300-DPI visual charts: `scree_and_roc_plots.png`, `irt_tif_and_ccc_plots.png`.

## 8. VALIDATION
- CVR values verified against Lawshe critical tables matching panel size $N$.
- S-CVI/Ave must exceed $.80$ and I-CVI must exceed $.78$.
- Factor loadings must exceed $.40$ without cross-loading discrepancies.
- AVE $\ge .50$ and CR $\ge .70$ mandatory for claiming convergent validity.
- McDonald's $\omega$ mandatory under APA 7th Edition guidelines.
- Item fit statistics for IRT must fall within $[0.60, 1.40]$.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-DETERMINISTIC-REVERSE-CODING-001)**: Deterministically verify and extract reverse-coded item indices from Questionnaires.xlsx via psychometric-scale-resolver before computing subscale sums. [Enforcement: dynamic_invariant_guard.py (LSN-2026-DETERMINISTIC-REVERSE-CODING-001)]