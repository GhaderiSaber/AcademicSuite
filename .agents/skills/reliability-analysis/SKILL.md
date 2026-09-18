---
name: reliability-analysis
description: Calculate scale internal consistency reliability including Cronbach's alpha, McDonald's omega, item-total correlations, and alpha-if-item-deleted.
---

# Reliability Analysis Skill (تحلیل پایایی و همسانی درونی ابزارها)

Computes classical and modern psychometric internal consistency reliability: Cronbach's alpha ($\alpha$), McDonald's omega ($\omega_t$ and $\omega_h$), corrected item-total correlations, and alpha-if-item-deleted diagnostic profiles for psychometric scales and subscales.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Stage 4.2 Scale Reliability Verification**: Determining whether multi-item survey instruments exhibit satisfactory internal consistency ($\alpha \ge .70, \omega \ge .70$) in the target study sample.
2. **Item-Level Psychometric Diagnostics**: Evaluating corrected item-total correlations ($r_{\text{it}} \ge .30$) and "alpha if item deleted" to identify defective or non-discriminating survey items.
3. **Addressing Tau-Equivalence Violations**: Computing McDonald's omega ($\omega$) when factor loadings are unequal across items.
4. **Validation Studies (Stage V.6)**: Establishing psychometric reliability as a prerequisite for construct validity and factor analysis.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Multidimensional Scale Bundles**: Never calculate a single omnibus Cronbach's alpha across all items of a multidimensional inventory (e.g. Maslach Burnout Inventory). Reliability must be calculated independently for each unidimensional subscale.
2. **Two-Item Measures**: Cronbach's alpha is mathematically distorted on 2-item scales. Use the Spearman-Brown split-half coefficient or Pearson inter-item correlation ($r \ge .15\text{--}.50$) instead.
3. **Test-Retest Temporal Stability**: Internal consistency measures item homogeneity across a single administration, not temporal stability over time.
4. **Formative or Index Scales**: Items that define a composite index rather than reflect an underlying latent construct (e.g. Life Events Stress Checklist) should not be subjected to internal consistency checks.

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**: Item columns belonging to a single unidimensional subscale or construct.
- **Minimum Sample Size**: $N \ge 50$ (ideally $N \ge 100$).
- **CLI Parameters**:
  - `--data`: Path to cleaned data file.
  - `--items`: Comma-separated list of item column names (e.g. `"mbi_1,mbi_2,mbi_3,mbi_6,mbi_8"`).
  - `--scale-name`: Scholarly name of the target construct.
  - `--output`: Destination path for `02_reliability.json`.

---

## 4. Methodological & Statistical Assumptions
1. **Unidimensionality**: Items reflect a single continuous latent construct.
2. **Essential Tau-Equivalence (for Cronbach's $\alpha$)**: Every item has equal true-score factor loadings ($\lambda_1 = \lambda_2 = \dots = \lambda_k$) and equal item error variances. When violated, Cronbach's $\alpha$ underestimates true reliability, requiring McDonald's $\omega$.
3. **Uncorrelated Item Measurement Errors**: No residual covariances between item pairs.

---

## 5. Method-Selection Decision Tree
```text
Scale Length & Factor Loading Equality:
├── Scale Length:
│   ├── Exactly 2 Items:
│   │   └── USE: Spearman-Brown Split-Half or Inter-Item Correlation r
│   └── 3 or More Items:
│       ├── Check Factor Loadings Equality (Tau-Equivalence):
│       │   ├── Equal Factor Loadings (lambda_1 = lambda_2 = ...):
│       │   │   └── USE: Cronbach's Alpha (alpha >= .70 acceptable, >= .80 good)
│       │   └── Unequal Factor Loadings (Congeneric Model):
│       │       └── USE: McDonald's Omega (omega_total >= .70) alongside Cronbach's alpha
│       └── Item Diagnostic Review:
│           ├── Corrected Item-Total Correlation r_it < .30:
│           │   └── Flag item as defective / candidate for deletion
│           └── Alpha if Item Deleted > Current Alpha + .05:
│               └── Item degrades overall scale internal consistency
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/reliability-analysis/scripts/compute_reliability.py \
  --data path/to/cleaned_data.xlsx \
  --items "burnout_1,burnout_2,burnout_3,burnout_4,burnout_5" \
  --scale-name "Job Burnout" \
  --output path/to/02_reliability.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`02_reliability.json`**:
   - `scale_name`: Construct name.
   - `number_of_items`: $k$.
   - `cronbach_alpha`: Float formatted to 2 decimal places ($0.86$).
   - `mcdonald_omega`: Float formatted to 2 decimal places ($0.88$).
   - `item_diagnostics`: List of items with `mean`, `sd`, `corrected_item_total_r`, and `alpha_if_deleted`.
2. **APA 7 OpenXML Word Table**: 3-line reliability table embedded into Chapter 4 / Stage 4.2 deliverables.

---

## 8. Validation & Forensic Sanity Checks
- **Alpha Upper/Lower Bounds**: $0.0 \le \alpha \le 1.0$. Negative alpha indicates reverse-coded items were omitted from recoding.
- **Reporting Standard (Directive 4)**: Report alpha as $\alpha = .86$ (in English APA) or $\alpha = ۰.۸۶$ (in Persian with mandatory leading zero).
- **Zero Hallucinated Alphas**: Alphas must be calculated deterministically from the real covariance matrix; mental calculation is strictly prohibited.

