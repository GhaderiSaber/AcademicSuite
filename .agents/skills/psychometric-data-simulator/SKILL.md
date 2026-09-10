---
name: psychometric-data-simulator
description: >-
  Advanced Monte Carlo psychometric simulation engine ported from GhaderiSaber/SimDat.
  Generates synthetic structural equation models (SEM) and Confirmatory Factor Analysis (CFA)
  datasets, discrete Likert-scale questionnaire item responses (1-5, 1-7, 1-10) with specified
  factor loadings and target Cronbach's alpha, randomized clinical trial (RCT) pre-post-followup
  repeated measures with ANCOVA effect sizes, and correlated demographic attributes. Exports
  SPSS-ready multi-sheet Excel files (.xlsx), CSV, and executable R lavaan analysis scripts.
---

# Psychometric Data Simulator Skill (شبیه‌ساز داده‌های روان‌سنجی و معادلات ساختاری)

This skill equips Antigravity to act as an elite quantitative psychometrician and Monte Carlo simulation engineer. Based on algorithms ported from the [`GhaderiSaber/SimDat`](https://github.com/GhaderiSaber/SimDat.git) suite, it simulates realistic psychological research datasets matching complex empirical properties: latent structural equation models (SEM), confirmatory factor analysis (CFA), discrete Likert questionnaire items, correlated demographics, and experimental randomized clinical trials (RCTs).

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user needs to **simulate realistic psychological data** for a thesis, dissertation, pilot study, or methodological workshop.
2. The user needs to generate **item-level Likert responses** (`q1, q2, ...`) for established questionnaires (e.g., from `Questionnaires.xlsx`) with realistic factor structures, reverse scoring, and target Cronbach's $\alpha$.
3. The user needs to simulate a **Structural Equation Model (SEM)** or **Path Model** with defined exogenous predictors, mediators, criteria, structural path coefficients ($\beta, \gamma$), and indirect mediation effects ($a \times b$).
4. The user needs to simulate an **Experimental Randomized Controlled Trial (RCT)** with intervention vs. control groups across repeated measurement occasions (Pretest, Posttest, Follow-up) and pre-specified effect sizes ($d, \eta_p^2$).
5. The user needs **SPSS-ready Excel files** (`.xlsx` with discrete integers and value labels), CSV datasets, or executable **R `lavaan` analysis scripts**.

---

## 1.1 The Golden Rule of Psychometric Simulation: Realistic Empirical Decimal Noise

### 1. The Core Scientific Problem
When clients, supervisors, or research proposals specify target group parameters like:
> *"The mean for healthy should be 5, for self-harm should be 10"*

A naive simulation algorithm might enforce $\sum X_i = \mu_{\text{target}} \times N$, producing empirical sample means like $M = 5.0000$ and $M = 10.0000$. **In authentic empirical research, this never happens.** When tens or hundreds of respondents answer discrete Likert items, sample means naturally possess fractional decimal components (e.g., $M = 5.24, SD = 1.97$; $M = 10.13, SD = 1.93$). Whole-integer group means in an APA 7 table immediately reveal that the data was synthetically manufactured and raise red flags during defense examination or journal peer review.

### 2. Mandatory Simulation Protocol
Whenever generating synthetic psychometric data, the simulation engine and agent **MUST** enforce the following 5 requirements:

1. **Apply Bounded Organic Decimal Noise to Target Means**:
   $$\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \quad \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$$
   Ensure that:
   $$|\text{round}(\mu_{\text{empirical}}) - \mu_{\text{empirical}}| \ge 0.05$$
   This guarantees that no variable has a whole-integer mean (such as `.000`). For instance, a requested mean of $5.0$ must naturally emerge as $M = 5.24$, $4.88$, or $5.15$; a requested mean of $10.0$ must emerge as $M = 10.13$, $9.89$, or $10.82$.

2. **Preserve Discrete Integers for Individuals**:
   While group means have realistic decimal fractions, individual participant responses must strictly remain valid discrete integers:
   $$X_{ij} \in \{Min, Min+1, \dots, Max\}$$
   Never output fractional or floating-point item ratings for individual survey respondents.

3. **Natural Non-Identical Standard Deviations**:
   Allow standard deviations to vary naturally across dimensions ($SD \in [1.50, 3.50]$ depending on scale range), avoiding artificially identical standard deviations across subscales.

4. **Calibrated Alignment for Non-Significant Dimensions**:
   If the study design or supervisor specifies that certain dimensions have *no significant difference* between groups (e.g., `CERQ_PR` and `CERQ_PRE`, or `CP_TP` and `CP_AP`):
   - Keep the noise offsets for both groups closely matched: $|\mu_1 - \mu_2| \le 0.15$.
   - Confirm that the resulting independent $t$-test or ANOVA yields $p > .05$.

5. **Strict Statistical Assumptions Compliance**:
   Adding decimal noise must never compromise core psychometric and inferential assumptions:
   - **Univariate Normality**: Skewness & Kurtosis $\in [-0.85, +0.85]$ (or $[-1, +1]$).
   - **Homogeneity of Variance**: Levene's test $p > .05$ across all subscales.
   - **Homogeneity of Covariance Matrices**: Box's M test $p > .05$ across all multivariate batteries.
   - **Multivariate Effects (MANOVA)**: Wilks' Lambda $p < .001$ for hypothesized differences.

---

## 2. Four Specialized Simulation Engines

```
                           [User Configuration / JSON Payload]
                                            │
         ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
         ▼                  ▼                               ▼                  ▼
   [1. SEM / CFA]    [2. Scale Items]                [3. RCT Trial]     [4. Demographics]
   ├── Cholesky     ├── Multi-item Likert           ├── Pre/Post/FU     ├── Age & Income
   ├── Path DAG β   ├── Factor loadings λ           ├── Control vs Int  ├── Gender & SES
   ├── Mediation    ├── Cronbach's α noise          ├── ANCOVA d & η²   ├── Education
   └── Fit indices  └── Reverse item keying         └── Slope balance   └── Construct r
         │                  │                               │                  │
         └──────────────────┴───────────────┬───────────────┴──────────────────┘
                                            │
                                            ▼
                           [Multi-Format Exporter]
                           ├── 1. Excel Workbook (.xlsx)
                           │   ├── Sheet 1: Rescaled_Data (SPSS Integer Likert Items)
                           │   ├── Sheet 2: Composite_Scores (Subscale Sums & Means)
                           │   ├── Sheet 3: Latent_Continuous (Underlying Standardized z)
                           │   └── Sheet 4: Parameters_and_Fit (Loadings, Paths, Fit)
                           ├── 2. CSV Dataset (.csv)
                           ├── 3. R lavaan Analysis Script (.R)
                           └── 4. Simulation Summary Metrics (.json)
```

### Engine 1: Structural Equation Modeling & CFA (`--mode sem`)
- **Latent Factor Generation**: Uses Cholesky factorization of population correlation matrices ($\mathbf{\Sigma} = \mathbf{L}\mathbf{L}^T$) for CFA models.
- **Structural Path Propagation**: Directed Acyclic Graph (DAG) recursive propagation:
  $$\eta_{crit} = \sum \beta \eta_{pred} + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \sigma^2_\epsilon)$$
- **Mediation & Defined Parameters**: Calculates indirect effects ($a \times b$), total effects ($c = c' + a \times b$), and Sobel test statistics.
- **Goodness-of-Fit Estimation**: Evaluates sample implied covariance against empirical covariance, reporting $\chi^2$, $df$, $p$-value, CFI, TLI, RMSEA, and SRMR.
- **R `lavaan` Scripting**: Generates ready-to-run R scripts with `cfa()` or `sem()` syntax.

### Engine 2: Questionnaire & Likert Item Simulator (`--mode scale`)
- **Item Rescaling & Quantization**: Converts continuous latent scores into discrete Likert integer responses (1–5, 1–7, or 1–10):
  $$y^*_{ij} = \lambda_j \eta_i + \epsilon_{ij}, \quad \epsilon_{ij} \sim \mathcal{N}(0, \theta_j)$$
  $$y_{ij} = \text{clip}\left(\text{round}\left(\frac{y^*_{ij}}{\sqrt{\lambda_j^2 + \theta_j}} \cdot \sigma_{item} + \mu_{item}\right), \; Min, \; Max\right)$$
- **Reverse Scoring Keying**: Accurately simulates negatively worded items using $(Min + Max) - Item$ algebra.
- **Cronbach's $\alpha$ Control**: Regulates indicator measurement error variances ($\theta_j$) to guarantee target internal consistency ($\alpha \approx .75 - .92$).

### Engine 3: Experimental Clinical Trial Simulator (`--mode rct`)
- **Repeated Measures Design**: Generates multivariate data for experimental and control groups across Pretest, Posttest, and 3-month Follow-up.
- **Effect Size Injection**: Shifts intervention posttest distributions by pre-specified Cohen's $d$ ($0.50$ medium, $0.80$ large) or partial eta squared ($\eta_p^2 = 0.14 - 0.35$).
- **ANCOVA Assumptions Built-In**: Maintains baseline homogeneity ($p > .05$ on pretest) and homogeneity of regression slopes.

### Engine 4: Demographic Correlates (`--demographics`)
- **Continuous Features**: Age ($\mathcal{N}(\mu, \sigma)$ clipped to realistic bounds), Monthly Income, Work Experience.
- **Categorical Features**: Gender (e.g., Male/Female/Other), Educational Level (High School, Bachelor's, Master's, Ph.D.), Socioeconomic Status (Low, Middle, High), Marital Status.
- **Latent Construct Correlations**: Connects demographics to psychological variables (e.g., Age positively correlated with Resilience, SES negatively correlated with Psychological Distress).

### Engine 5: Multiple & Hierarchical Regression (`--mode regression`)
- **Multiple Regression**: Target $R^2$, standardized $\beta$ coefficients, and controlled VIF multicollinearity.
- **Hierarchical Regression**: Step 1 (Demographics / Control covariates) $\to$ Step 2 (Main psychological predictors) with $\Delta R^2$, $F$, and $\Delta F$ $p$-value.
- **Moderated Regression (PROCESS Model 1)**: Mean-centered predictors $X$, $W$, and interaction $X \times W$ with conditional simple slopes at $-1 SD$, Mean, and $+1 SD$.

### Engine 6: ANOVA Family & Mean Differences (`--mode anova`)
- **Independent & Paired $t$-tests**: 2 groups with target Cohen's $d$ or paired pre-post correlation with $d_z$.
- **One-Way ANOVA**: 3+ groups with planned post-hoc contrasts (Tukey HSD pairwise comparisons).
- **Two-Way Factorial ANOVA ($A \times B$)**: Main effect Factor A, Main effect Factor B, Interaction effect ($A \times B$), and Partial $\eta^2$.
- **MANOVA**: Multiple correlated DVs with specified inter-correlation matrix across groups, reporting Wilks' Lambda ($\Lambda$).

### Engine 7: Mixed Split-Plot Repeated Measures (`--mode repeated_measures`)
- **Between Factor $\times$ Within Factor**: Groups (e.g., Intervention vs. Control) $\times$ Time waves (Pre, Post, 1-mo FU, 3-mo FU).
- **Temporal Covariance**: Autoregressive AR(1) or compound symmetry structure with sphericity parameter control ($\epsilon$).
- **Dual Formats**: Generates both wide format (SPSS) and long format (mixed-effects models).

### Engine 8: Binary Logistic Regression (`--mode logistic`)
- **Logit Inversion**: Simulates binary endpoints ($0/1$, e.g., Clinical Diagnosis, Treatment Remission, Relapse) from log-odds $z_i = \beta_0 + \sum \beta_j X_{ij}$.
- **Odds Ratios (OR)**: Calibrated directly from specified target odds ratios $\exp(\beta_j)$.
- **Classification Metrics**: Confusion matrix, classification accuracy, sensitivity, and specificity.

### Engine 9: Exploratory Factor Analysis (`--mode efa`)
- **Multi-Factor Structure**: Primary factor loadings ($\ge .50$), cross-loadings ($[.15, .35]$), and communalities ($h^2$).
- **Psychometric Diagnostics**: Kaiser-Meyer-Olkin (KMO) sampling adequacy, Bartlett's test of sphericity, and eigenvalues.

### Engine 10: Non-Parametric & Categorical (`--mode non_parametric`)
- **Skewed Continuous Data**: Gamma and Log-normal distributions for testing Mann-Whitney $U$, Wilcoxon Signed-Rank, and Kruskal-Wallis $H$.
- **Contingency Tables**: $r \times c$ categorical cross-tabulations for Pearson Chi-Square ($\chi^2$) and Cramér's $V$.

---

## 3. Built-in Research Presets (`--preset <name>`)

Instantly generate publication-ready synthetic datasets with one command:
| Preset Flag | Analysis / Design | Sample Size | Primary Output |
| :--- | :--- | :--- | :--- |
| **`--preset hierarchical_regression`** | Demographics (Age, Gender) $\to$ Resilience, Self-Efficacy predicting Wellbeing | $N = 250$ | Step 1/2 $\Delta R^2$, $\Delta F$, coefficients |
| **`--preset moderation_model1`** | Stress $\to$ Burnout moderated by Social Support | $N = 200$ | $X \times W$ interaction & simple slopes at $\pm 1 SD$ |
| **`--preset factorial_anova`** | $2 \times 3$ Factorial ANOVA (Gender $\times$ Treatment [Waitlist, CBT, ACT]) on QoL | $N = 180$ | Main effects A & B, interaction $A \times B$, $\eta_p^2$ |
| **`--preset mixed_split_plot`** | $2 \times 4$ Mixed Repeated Measures (Group $\times$ Pre, Post, 1m FU, 3m FU) on Pain | $N = 60$ | Time, Group, Time $\times$ Group, Sphericity $\epsilon$ |
| **`--preset ancova_trial`** | RCT Pre-Post Clinical Trial on Anxiety & Depression | $N = 60$ | Baseline balance, Cohen's $d = 1.15$ posttest |
| **`--preset logistic_diagnosis`** | Trauma, Sleep, Family History predicting Depression Diagnosis (0/1) | $N = 200$ | Odds Ratios, Confusion Matrix, ROC-AUC |
| **`--preset efa_battery`** | 3-factor 15-item survey with cross-loadings & communalities | $N = 350$ | KMO, Bartlett's $\chi^2$, Eigenvalues |
| **`--preset non_parametric_skewed`** | Skewed clinical severity scores across 3 severity groups | $N = 120$ | Kruskal-Wallis $H$, Medians, and IQRs |

---

## 4. CLI Execution Examples

### 1. Instant Run via Research Preset:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset hierarchical_regression \
  --out-dir "./sim_hierarchical_results"
```

### 2. Factorial ANOVA Simulation:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset factorial_anova \
  --out-dir "./sim_factorial_results"
```

### 3. Mixed Split-Plot Repeated Measures:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset mixed_split_plot \
  --out-dir "./sim_repeated_measures_results"
```

### 4. Custom JSON Configuration:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode regression \
  --json "my_regression_config.json" \
  --n 300 \
  --seed 42 \
  --out-dir "./custom_sim_output"
```

---

## 5. Output Artifacts & Formats

1. **`simulated_<mode>_dataset.xlsx`**: Multi-sheet Excel workbook tailored to the design:
   - `Dataset` / `Rescaled_Data`: Clean SPSS-ready dataset.
   - `Summary_and_Tests`: Descriptive statistics, ANOVA tables, regression steps, and fit indices.
   - `Parameters_and_Effects`: Standardized coefficients, effect sizes ($R^2$, $\eta_p^2$, Cohen's $d$, OR), and loadings.
2. **`simulated_<mode>_dataset.csv`**: Standard CSV format for SPSS, jamovi, JASP, R, and Python.
3. **`simulation_summary.json`**: Complete structured JSON summary of empirical statistics and effect sizes.
4. **`lavaan_syntax.R`** *(for SEM/CFA)*: Executable R script replicating the latent model.
