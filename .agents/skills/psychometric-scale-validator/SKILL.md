---
name: psychometric-scale-validator
description: >-
  Expert psychometric scale standardization and validation skill for psychology, counseling, educational assessment,
  and behavioral sciences. Conducts complete validation pipelines: WHO/ITC translation verification, quantitative
  Lawshe (1975) Content Validity Ratio (CVR) and Waltz & Bausell / Lynn (1986) Content Validity Index (CVI), Item
  Impact Scores, Exploratory Factor Analysis (EFA: KMO, Bartlett, Scree plot, Promax/Varimax), Confirmatory Factor
  Analysis (CFA: chi2/df, CFI, TLI, RMSEA, SRMR), Fornell & Larcker Convergent (AVE >= 0.50, CR >= 0.70) and
  Discriminant Validity, APA 7th Edition McDonald's Omega (ω) and Cronbach's Alpha (α), Test-Retest ICC, Norm score
  transformations (Z, T, Percentile Ranks), and clinical ROC Curve Cut-off determination (Sensitivity, Specificity,
  AUC, Youden's J). Compiles defense-ready Chapter 4 Word reports (.docx), 5-sheet Excel validation matrices, and
  300-DPI visual plots.
---

# Psychometric Scale Validator Skill (هنجاریابی، روان‌سنجی و اعتباریابی ابزارهای اندازه‌گیری)

This skill empowers Antigravity to act as an elite psychometrician, measurement specialist, and scale validation researcher. It orchestrates the entire lifecycle of **Psychometric Adaptation, Standardization, and Validation Studies** in psychology, counseling, educational measurement (سنجش و اندازه‌گیری), and behavioral sciences.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user conducts a **Scale Standardization or Validation Thesis/Dissertation (پایان‌نامه/رساله هنجاریابی و اعتباریابی مقیاس)**:
   *(«بررسی ویژگی‌های روان‌سنجی، ساختار عاملی و هنجاریابی نسخه فارسی مقیاس...»)*.
2. The user needs to evaluate **Content Validity**:
   - **Lawshe (1975) Content Validity Ratio ($CVR$)** tested against expert panel size critical thresholds ($p < .05$).
   - **Waltz & Bausell / Lynn (1986) Content Validity Index ($CVI$)**: $I\text{-}CVI \ge 0.78$ and $S\text{-}CVI/\text{Ave} \ge 0.80$.
   - **Item Impact Score**: $\ge 1.5$.
3. The user needs to verify **Construct Validity**:
   - **Exploratory Factor Analysis (EFA)**: KMO sampling adequacy, Bartlett's sphericity, Scree plot, Promax/Varimax factor loadings ($\lambda \ge 0.40$), and cumulative explained variance.
   - **Confirmatory Factor Analysis (CFA)**: Fit indices ($\chi^2/df < 3$, CFI $\ge .90$, TLI $\ge .90$, RMSEA $\le .08$, SRMR $\le .08$).
   - **Fornell & Larcker Convergent & Discriminant Validity**: $AVE \ge 0.50$, $CR \ge 0.70$, and $\sqrt{AVE} > r$.
4. The user needs to report **Modern Reliability Metrics**:
   - **McDonald's Omega ($\omega_t$ & $\omega_h$)**: Mandatory under APA 7th Edition guidelines.
   - Cronbach's Alpha ($\alpha$) with "alpha-if-item-deleted" diagnostics.
   - Test-Retest Intraclass Correlation Coefficient ($ICC$, two-way mixed model, absolute agreement).
   - Split-Half reliability (Guttman and Spearman-Brown coefficients).
5. The user needs **Norms & Clinical Cut-off Scores**:
   - Score conversion tables: Raw Score $\to$ Z-Score $\to$ T-Score $\to$ Percentile Rank ($PR$).
   - **Receiver Operating Characteristic (ROC) Curve Analysis**: Sensitivity, Specificity, Area Under the Curve ($AUC \ge 0.80$), and Youden's Index ($J$) for optimal clinical screening cut-offs.
6. The user needs a defense-ready **Chapter 4 Word report (`.docx`)**, a 5-sheet **Validation Matrix Excel (`.xlsx`)**, or 300-DPI **Scree & ROC plots (`.png`)**.

---

## 2. Methodological Standards & Decision Rules

### Pillar 1: Lawshe Critical CVR Thresholds ($p < .05$)
$$CVR = \frac{n_e - \frac{N}{2}}{\frac{N}{2}}$$
| Panel Size ($N$) | Min CVR | Panel Size ($N$) | Min CVR | Panel Size ($N$) | Min CVR |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **5** | 0.99 | **9** | 0.78 | **13** | 0.54 |
| **6** | 0.99 | **10** | 0.62 | **14** | 0.51 |
| **7** | 0.99 | **11** | 0.59 | **15** | 0.49 |
| **8** | 0.75 | **12** | 0.56 | **20** | 0.42 |

### Pillar 2: Fornell & Larcker (1981) Construct Validity
- **Average Variance Extracted ($AVE$)**:
  $$AVE = \frac{\sum \lambda_i^2}{\sum \lambda_i^2 + \sum (1 - \lambda_i^2)} \ge 0.50$$
- **Composite Reliability ($CR$)**:
  $$CR = \frac{(\sum \lambda_i)^2}{(\sum \lambda_i)^2 + \sum (1 - \lambda_i^2)} \ge 0.70$$
- **Discriminant Validity**:
  $$\sqrt{AVE_j} > r_{jk} \quad (\forall k \neq j)$$

### Pillar 3: McDonald's Omega ($\omega$) under APA 7
Unlike Cronbach's alpha, McDonald's omega does not assume tau-equivalence ($tau\text{-equivalence}$) and accurately models congeneric factor structures:
$$\omega = \frac{(\sum \lambda_i)^2}{(\sum \lambda_i)^2 + \sum \theta_i} \ge 0.70$$

### Pillar 4: Clinical Cut-off & Youden's J Index
$$J = \text{Sensitivity} + \text{Specificity} - 1$$
The score maximizing $J$ is reported as the primary clinical screening cut-off point.

---

## 3. Execution Workflow

### Step 1: Prepare the Psychometric Validation Payload
Construct `validation_payload.json` containing:
- Scale metadata and translation protocol.
- Item text and expert panel ratings ($n_e$, $relevant$, impact score).
- EFA parameters (KMO, Bartlett, loadings).
- CFA fit indices ($\chi^2/df$, CFI, TLI, RMSEA, SRMR).
- Factor metrics ($AVE$, $CR$, Cronbach's $\alpha$, McDonald's $\omega$, ICC).
- Norm data (Z, T, Percentiles) and ROC diagnostics (AUC, optimal cut-off).

### Step 2: Run the Automated Validation Engine
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json path/to/validation_payload.json \
  --out-dir path/to/output_directory \
  --lang fa
```

### Step 3: Inspect Multi-Modal Deliverables
1. `فصل_چهارم_ویژگی‌های_روان‌سنجی_و_هنجاریابی.docx`:
   - Full Chapter 4 dissertation text with authentic Iranian typography (*B Titr*, *B Nazanin*, *Times New Roman*), BiDi RTL OpenXML (`<w:bidi w:val="1"/>`), and `<w:bidiVisual/>`.
   - 7 APA 7 borderless tables:
     - Table 4-1: Face & Content Validity (Item Impact, CVR, I-CVI).
     - Table 4-2: EFA Factor Loadings, Eigenvalues, and Explained Variance.
     - Table 4-3: CFA Goodness-of-Fit Indices.
     - Table 4-4: Convergent (AVE, CR) & Discriminant Validity Matrix.
     - Table 4-5: Multi-method Reliability (Alpha, Omega, ICC, Split-half).
     - Table 4-6: Standardization & Norm Conversion (Raw $\to$ Z $\to$ T $\to$ PR).
     - Table 4-7: ROC Curve Diagnostics & Optimal Cut-off Score.
   - Embedded 300-DPI visual figure (Scree plot & ROC curve).
2. `psychometric_validation_matrix.xlsx`:
   - 5 professional sheets: `Overview & Metrics`, `Item Analysis (CVR & CVI)`, `EFA & Factor Loadings`, `CFA & Fornell-Larcker`, `Norms & ROC`.
3. `scree_and_roc_plots.png`:
   - 300-DPI dual publication graphic.
4. `psychometric_summary.json`:
   - Complete machine-readable summary schema.

---

## 4. Input Schema Specifications

```json
{
  "study_title": "عنوان پژوهش اعتباریابی و هنجاریابی",
  "study_title_en": "English Study Title",
  "scale_name": "نام مقیاس به فارسی",
  "scale_name_en": "Scale Name in English (Acronym)",
  "original_authors": "نام سازندگان اصلی مقیاس و سال",
  "sample_size": 450,
  "retest_sample_size": 60,
  "expert_panel_size": 12,
  "lawshe_critical_cvr": 0.56,
  "items": [
    {
      "item_num": 1,
      "text": "متن گویه به فارسی",
      "factor": "نام عامل مربوطه",
      "essential_votes": 12,
      "relevant_votes": 12,
      "impact_score": 4.25,
      "loading": 0.78
    }
  ],
  "factors": [
    {
      "factor_name": "نام عامل",
      "factor_name_en": "Factor English Name",
      "items_range": "گویه‌های ۱ تا ۱۰",
      "eigenvalue": 6.42,
      "variance_percent": 32.1,
      "ave": 0.542,
      "cr": 0.892,
      "cronbach_alpha": 0.894,
      "mcdonald_omega": 0.896,
      "retest_icc": 0.862,
      "split_half": 0.854
    }
  ],
  "inter_factor_correlation": 0.42,
  "efa_diagnostics": {
    "kmo": 0.884,
    "bartlett_chi2": 3428.60,
    "bartlett_df": 190,
    "bartlett_p": 0.0001
  },
  "cfa_fit_indices": {
    "chi2_df": 2.298,
    "cfi": 0.948,
    "tli": 0.942,
    "rmsea": 0.054,
    "srmr": 0.048
  },
  "norms_data": [
    { "raw_range": "20-25", "z_score": "-1.71 تا -1.28", "t_score": "33 تا 37", "percentile": "5", "clinical_status": "بسیار پایین" }
  ],
  "roc_diagnostics": {
    "auc": 0.872,
    "optimal_cutoff": 48.0,
    "sensitivity": 84.5,
    "specificity": 81.2,
    "youden_index": 0.657
  }
}
```

---

## 5. AcademicSuite Integration

- **Upstream Linkage**:
  - `persian-proposal-builder`: Generates proposal and Chapter 3 methodology for validation theses.
  - `psychometric-scale-resolver`: Queries `Questionnaires.xlsx` for original English/Persian items, factor structures, and reverse items.
  - `psychometric-data-simulator`: Simulates raw Likert response data with target factor loadings ($\mathbf{\Lambda}$) for testing and synthetic modeling.
- **Downstream Linkage**:
  - `persian-thesis-builder`: Direct ingestion as `--ch4` in full thesis compilation.
  - `academic-article-writer`: Synthesizes psychometric findings into a standardization journal article for ISI or ISC publication.
