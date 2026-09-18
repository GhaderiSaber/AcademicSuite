---
name: data-cleaning
description: Reverse-code items from 4,880 validated questionnaires, aggregate subscale and composite scores, handle imputations, and export analysis-ready datasets.
---

# Data Cleaning & Scale Scoring Skill (پاک‌سازی، بازکدگذاری و نمره‌گذاری پرسشنامه‌ها)

Transforms raw survey item data into analysis-ready research datasets: reverse-coding inverted items according to official psychometric scoring keys, aggregating subscales and total construct scores, and logging exact transformation provenance.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Scoring Multi-Item Psychological Questionnaires**: Converting raw item responses into verified subscale sums or composite means.
2. **Reverse-Coding Negatively Keyed Items**: Inverting item scales (e.g., $1 \to 5, 2 \to 4, 3 \to 3, 4 \to 2, 5 \to 1$ on a 5-point Likert scale) before subscale summation.
3. **Imputation Integration**: Applying MICE-imputed values from Stage 4.0 data audit into final analysis matrices.
4. **Generating Analysis-Ready Datasets**: Creating clean, standardized datasets (`data_cleaned.xlsx`) with clearly labeled composite columns for downstream statistical modeling.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Unverified Reverse-Coding**: NEVER invent or guess which items are inverted. Scoring rules must be validated against `Questionnaires.xlsx` via `psychometric-scale-resolver`.
2. **Overwriting Raw Data Files**: Raw empirical data files must remain permanently immutable. Cleaned datasets must always be written to a distinct destination path.
3. **Summing Incompatible Measurement Scales**: Never aggregate Likert items that use disparate response anchors (e.g. Mixing 4-point and 7-point scales) without prior standardization ($z$-scoring).

---

## 3. Required Data & Input Contract
- **Input File**: Raw dataset (`.xlsx`, `.csv`, `.sav`).
- **Scoring Specification (`scale_spec.json`)**:
  ```json
  {
    "scales": [
      {
        "scale_name": "maslach_burnout_inventory",
        "item_prefix": "mbi_",
        "total_items": 22,
        "reverse_items": [4, 7, 9, 12, 17, 21],
        "scale_min": 1,
        "scale_max": 5,
        "subscales": {
          "emotional_exhaustion": [1, 2, 3, 6, 8, 13, 14, 16, 20],
          "depersonalization": [5, 10, 11, 15, 22],
          "personal_accomplishment": [4, 7, 9, 12, 17, 18, 19, 21]
        },
        "aggregation_method": "sum"
      }
    ]
  }
  ```

---

## 4. Methodological & Statistical Assumptions
1. **Item Unidimensionality**: Items assigned to a subscale must reflect a single latent psychometric dimension.
2. **Scoring Directionality**: Higher composite scores must consistently reflect higher levels of the target psychological construct across all subscales.
3. **Missing Value Threshold**: Cases with $> 20\%$ missing items on a single subscale should not be scored via simple mean substitution.

---

## 5. Method-Selection Decision Tree
```text
Scale Scoring Decision Flow:
├── Is Instrument in Psychometric Registry (4,880 Questionnaires)?
│   ├── YES: Auto-extract reverse items and subscales from psychometric-scale-resolver
│   └── NO: Require explicit scale scoring key from author / manual specification
├── Reverse-Coding Transformation:
│   └── Formula: Inverted_Score = (Scale_Min + Scale_Max) - Original_Score
└── Subscale Aggregation Strategy:
    ├── Sum Score: Total points for clinical cutoff comparisons (e.g. BDI-II >= 20)
    └── Mean Score: Preserves original Likert metric [1, 5] for regression and SEM
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/data-cleaning/scripts/clean_and_score.py \
  --data path/to/raw_data.xlsx \
  --spec path/to/scale_spec.json \
  --output-data path/to/data_cleaned.xlsx \
  --output-log path/to/01_cleaning_log.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`data_cleaned.xlsx`**: Excel workbook containing cleaned raw items, newly created reverse-coded columns (e.g. `mbi_4_r`), and calculated subscale/composite columns.
2. **`01_cleaning_log.json`**:
   - `reverse_coded_columns`: List of modified items and formula applied.
   - `created_composites`: List of composite variables, item constituents, and descriptive summaries.
   - `input_hash` and `output_hash` (SHA-256) for audit provenance.

---

## 8. Validation & Forensic Sanity Checks
- **Correlation Inversion Sanity Check**: Inverted items must correlate positively with their respective subscale total ($r \ge .30$). A negative item-total correlation indicates an erroneous reverse-coding specification.
- **Theoretical Range Conformance**: Subscale scores must fall strictly within theoretical boundaries (e.g. For a 5-item 1–5 scale, sum must fall within $[5, 25]$).

