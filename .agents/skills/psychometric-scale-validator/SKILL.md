---
name: psychometric-scale-validator
description: >-
  Expert psychometric scale standardization, validation, and Item Response Theory (IRT) skill for psychology, counseling,
  educational assessment, and behavioral sciences. Conducts complete classical and modern validation pipelines: WHO/ITC
  translation verification, quantitative Lawshe (1975) Content Validity Ratio (CVR) and Waltz & Bausell / Lynn (1986)
  Content Validity Index (CVI), Item Impact Scores, Exploratory Factor Analysis (EFA: KMO, Bartlett, Scree plot, Promax/Varimax),
  Confirmatory Factor Analysis (CFA: chi2/df, CFI, TLI, RMSEA, SRMR), Fornell & Larcker Convergent (AVE >= 0.50, CR >= 0.70)
  and Discriminant Validity, APA 7th Edition McDonald's Omega (ω) and Cronbach's Alpha (α), Test-Retest ICC, Item Response
  Theory (IRT) Graded Response Model (GRM: discrimination a, category thresholds b1-b4, Infit/Outfit MNSQ, Test Information
  Function TIF, and Differential Item Functioning DIF), Norm score transformations (Z, T, Percentile Ranks), and clinical
  ROC Curve Cut-off determination (Sensitivity, Specificity, AUC, Youden's J). Compiles defense-ready Chapter 4 Word reports
  (.docx), 6-sheet Excel validation matrices, and dual 300-DPI visual plots.
---

# Psychometric Scale Validator Skill (هنجاریابی، روان‌سنجی و اعتباریابی ابزارهای اندازه‌گیری با CTT و IRT)

This skill empowers Antigravity to act as an elite psychometrician, measurement specialist, and scale validation researcher. It orchestrates the entire lifecycle of **Psychometric Adaptation, Standardization, and Validation Studies** in psychology, counseling, educational measurement (سنجش و اندازه‌گیری), and behavioral sciences under both **Classical Test Theory (CTT)** and **Modern Item Response Theory (IRT)**.

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
5. The user needs **Modern Item Response Theory (IRT) Analysis**:
   - **Samejima's Graded Response Model (GRM)** for polytomous Likert-scale data.
   - **Item Discrimination ($a$)**: Categorized according to Baker (2001) criteria ($<0.35$ Very Low to $\ge 1.70$ Very High).
   - **Category Boundary / Threshold Difficulty Parameters ($b_{ik}$)**.
   - **Item Fit Statistics**: Infit and Outfit Mean Square ($MNSQ \in [0.60, 1.40]$).
   - **Information Functions**: Item Information Functions (IIF), Test Information Function (TIF), and conditional Standard Error of Measurement ($SE(\theta) = 1/\sqrt{I(\theta)}$).
   - **Differential Item Functioning (DIF)**: Mantel-Haenszel evaluation and ETS classification (Class A, B, C) across gender or target demographic sub-groups.
6. The user needs **Norms & Clinical Cut-off Scores**:
   - Score conversion tables: Raw Score $\to$ Z-Score $\to$ T-Score $\to$ Percentile Rank ($PR$).
   - **Receiver Operating Characteristic (ROC) Curve Analysis**: Sensitivity, Specificity, Area Under the Curve ($AUC \ge 0.80$), and Youden's Index ($J$) for optimal clinical screening cut-offs.
7. The user needs a defense-ready **Chapter 4 Word report (`.docx`)** with 8 APA 7 tables, a 6-sheet **Validation Matrix Excel (`.xlsx`)**, or dual 300-DPI **Scree, ROC, TIF & CCC plots (`.png`)**.

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

### Pillar 3: Item Response Theory (IRT) & Samejima's GRM
For polytomous Likert-scale items:
$$P^*_{ik}(\theta) = \frac{1}{1 + \exp\left(-1.702 \cdot a_i (\theta - b_{ik})\right)}$$
- **Baker (2001) Discrimination ($a$)**: $<0.35$ Very Low, $0.35-0.64$ Low, $0.65-1.34$ Moderate, $1.35-1.69$ High, $\ge 1.70$ Very High.
- **Infit & Outfit $MNSQ$**: $0.60 \le MNSQ \le 1.40$ (Wright & Linacre, 1994).
- **Test Information Function (TIF)**: $I(\theta) = \sum I_i(\theta)$ with conditional error $SE(\theta) = 1/\sqrt{I(\theta)}$.
- **Differential Item Functioning (DIF)**: ETS Class A ($|\Delta \alpha| < 1.0$), Class B (Moderate), Class C (Large).

### Pillar 4: McDonald's Omega ($\omega$) under APA 7
$$\omega = \frac{(\sum \lambda_i)^2}{(\sum \lambda_i)^2 + \sum \theta_i} \ge 0.70$$

### Pillar 5: Clinical Cut-off & Youden's J Index
$$J = \text{Sensitivity} + \text{Specificity} - 1$$

---

## 3. Execution Workflow

### Step 1: Prepare the Psychometric Validation Payload
Construct `validation_payload.json` containing:
- Scale metadata and translation protocol.
- Item text and expert panel ratings ($n_e$, $relevant$, impact score).
- EFA parameters (KMO, Bartlett, loadings).
- CFA fit indices ($\chi^2/df$, CFI, TLI, RMSEA, SRMR).
- IRT parameters ($a_i$, $b_{ik}$, Infit/Outfit MNSQ, DIF status).
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
   - **8 APA 7 borderless tables**:
     - Table 4-1: Face & Content Validity (Item Impact, CVR, I-CVI).
     - Table 4-2: EFA Factor Loadings, Eigenvalues, and Explained Variance.
     - Table 4-3: CFA Goodness-of-Fit Indices.
     - Table 4-4: Convergent (AVE, CR) & Discriminant Validity Matrix.
     - Table 4-5: Multi-method Reliability (Alpha, Omega, ICC, Split-half).
     - Table 4-6: Item Response Theory (IRT) GRM Parameters, Infit/Outfit & DIF.
     - Table 4-7: Standardization & Norm Conversion (Raw $\to$ Z $\to$ T $\to$ PR).
     - Table 4-8: ROC Curve Diagnostics & Optimal Cut-off Score.
   - Embedded 300-DPI visual figures (Figure 4-1: Scree & ROC; Figure 4-2: TIF & CCC).
2. `psychometric_validation_matrix.xlsx`:
   - 6 professional sheets: `Overview & Metrics`, `Item Analysis (CVR & CVI)`, `EFA & Factor Loadings`, `CFA & Fornell-Larcker`, `IRT & Graded Response Model`, `Norms & ROC`.
3. Visual Charts:
   - `scree_and_roc_plots.png` (300 DPI Scree plot & ROC curve).
   - `irt_tif_and_ccc_plots.png` (300 DPI Test Information Function & Category Characteristic Curves).
4. `psychometric_summary.json`:
   - Complete machine-readable summary schema with IRT diagnostics.

---

## 4. AcademicSuite Integration

- **Upstream Linkage**:
  - `persian-proposal-builder`: Generates proposal and Chapter 3 methodology for validation theses.
  - `psychometric-scale-resolver`: Queries `Questionnaires.xlsx` for original English/Persian items, factor structures, and reverse items.
  - `psychometric-data-simulator`: Simulates raw Likert response data with target factor loadings ($\mathbf{\Lambda}$) for testing and synthetic modeling.
- **Downstream Linkage**:
  - `persian-thesis-builder`: Direct ingestion as `--ch4` in full thesis compilation.
  - `academic-article-writer`: Synthesizes psychometric findings into a standardization journal article for ISI or ISC publication.
