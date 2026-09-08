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

---

## 3. CLI Execution Quick-Start

### 1. Structural Equation Model Simulation:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_config.json" \
  --n 300 \
  --seed 42 \
  --out-dir "./sim_sem_results"
```

### 2. Multi-Item Questionnaire Simulation:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode scale \
  --json "scale_config.json" \
  --n 400 \
  --seed 101 \
  --out-dir "./sim_scale_results"
```

### 3. Experimental RCT Clinical Trial Simulation:
```bash
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode rct \
  --json "rct_config.json" \
  --n 60 \
  --seed 202 \
  --out-dir "./sim_rct_results"
```

---

## 4. Output Artifacts & Formats

1. **`simulated_dataset.xlsx`**: Multi-sheet Excel workbook:
   - `Rescaled_Data`: Integer Likert items and demographic codes (ideal for importing directly into SPSS, jamovi, or JASP).
   - `Composite_Scores`: Subscale sums, means, and total scores.
   - `Latent_Continuous`: Underlying continuous standard scores for validation.
   - `Parameters_and_Fit`: Model specification, path coefficients, factor loadings, and SEM fit indices.
2. **`simulated_dataset.csv`**: Standard CSV format for R, Python, and Mplus.
3. **`lavaan_syntax.R`**: Clean, commented R script to replicate SEM analysis and output formal parameter tables.
4. **`simulation_summary.json`**: Machine-readable JSON summary of sample statistics, empirical vs. theoretical correlations, and fit indices.
