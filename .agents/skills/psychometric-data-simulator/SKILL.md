---
name: psychometric-data-simulator
description: Monte Carlo psychometric data simulation for SEM, CFA, Likert scales, RCT pre-post repeated measures, ANCOVA, and correlated demographics. Exports SPSS XLSX/CSV.
---

# Psychometric Data Simulator Skill

This skill provides deterministic Monte Carlo data simulation algorithms ported from the SimDat suite. It simulates realistic psychological and behavioral research datasets matching complex empirical properties: latent SEM/CFA models, discrete Likert items, correlated demographics, and experimental clinical trials (RCTs).

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- Simulating realistic synthetic data for methodology workshops, power sensitivity pilots, or pipeline testing.
- Generating item-level Likert responses (`q1, q2, ...`) for established scales with realistic factor structures, reverse-coded items, and target internal consistency ($\alpha$).
- Simulating experimental trial datasets (Pre-test, Post-test, Follow-up) with calibrated Cohen's $d$ or $\eta_p^2$.
- Simulating structural equation models (SEM) or path models with specified latent covariances and structural path coefficients.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- **PRODUCTION DATA INTEGRITY MANDATE**: NEVER use this skill to fabricate or substitute data for real empirical studies, client thesis analyses, or journal submissions (Directive 0 violation).
- The user has provided real participant data (`.xlsx`, `.csv`, `.sav`) $\to$ use `data-audit`, `data-cleaning`, or `statistical-data-analyst`.
- Calculating real empirical statistics or testing hypotheses on observed data $\to$ use `statistical-data-analyst`.

## 3. REQUIRED DATA
- **Input Parameters**: JSON specification defining:
  - Sample size $N$ and random seed.
  - Mode: `sem`, `scale`, `rct`, `regression`, `anova`, or `repeated_measures`.
  - Factor loading matrix ($\mathbf{\Lambda}$) or structural path coefficients ($\mathbf{B}$).
  - Target means, standard deviations, and group separation.
- **Demographic Specifications**: Optional demographic columns (age, gender, education, SES) with correlation targets.

## 4. ASSUMPTIONS & SIMULATION GUARDRAILS
1. **Realistic Empirical Decimal Noise (Mandatory)**:
   $$\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \quad \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$$
   Zero synthetic whole-integer means (e.g., $M = 5.0000$ or $10.0000$ is strictly prohibited). Means must have natural decimal components ($M = 5.24, 10.13$).
2. **Discrete Integers for Individual Respondents**:
   $$X_{ij} \in \{\text{Min}, \text{Min}+1, \dots, \text{Max}\}$$
   Individual Likert responses must remain discrete integers (never continuous floats).
3. **Guardrail Against Astronomical Effect Sizes**:
   - Hypothesized significant group differences must calibrate to Cohen's $d \in [0.80, 1.15]$ ($\eta_p^2 \in [.12, .25]$).
   - Reject any iteration where $\eta_p^2 > .25$ or where non-significant controls yield $d > 0.12$.
4. **Assumption Compliance**: Simulated data must satisfy normality (skewness/kurtosis $\in [-1, +1]$) and variance homogeneity (Levene $p > .05$).

## 5. DECISION TREE

```
Psychometric Data Simulation Architecture
  │
  ├─► Purpose Check:
  │     ├─► Real Thesis / Empirical Study:
  │     │     └─► HALT: Data simulation prohibited on real empirical research.
  │     └─► Testing / Methodology / Workshop:
  │           └─► Proceed with Simulation Engines:
  │
  ├─► Study Design Engine Selection:
  │     ├─► Latent Construct / Factor Analysis:
  │     │     ├─► SEM Data Making Engine (R & Python): [sem_data_maker.R / --mode sem]
  │     │     │     ├─► DAG propagation: exogenous (eta) & endogenous (phi, theta via f1, f2, f3)
  │     │     │     ├─► Indicator measurement model: y_i = lambda_i * Latent + e_i
  │     │     │     ├─► J-iteration candidate selection loop (lavaan::sem ML)
  │     │     │     ├─► Empirical rescaling: rescale(y, mean, sd) = round(y * sd + mean)
  │     │     │     └─► Deliverables: primary_data.xlsx, final_data.xlsx, sem_results.json, sem_plot.pdf
  │     │     ├─► Confirmatory Factor Analysis: [--mode cfa] (Target factor loadings lambda >= .50)
  │     │     └─► Discrete Survey Scales: [--mode scale] (Rescaling continuous z -> discrete Likert 1-5)
  │     │
  │     ├─► Experimental / Clinical Trials:
  │     │     ├─► Pre-Post with Control: [--mode rct] (Calibrated Cohen's d in [0.80, 1.15], pretest balance)
  │     │     └─► Multi-Wave Longitudinal: [--mode repeated_measures] (AR(1) temporal covariance, sphericity epsilon)
  │     │
  │     └─► Predictive & Correlational:
  │           ├─► Multiple / Hierarchical: [--mode regression] (Step 1 controls -> Step 2 psychological predictors)
  │           └─► Moderation Model 1: [--mode moderation] (Mean-centered X, W, X*W interaction)
  │
  └─► Quality & Noise Verification:
        ├─► Verify |round(Mean) - Mean| >= 0.05 (No whole integers)
        ├─► Verify eta_p^2 in [0.12, 0.25] (No astronomical effect sizes)
        └─► Verify discrete Likert integers for every individual
```

## 6. EXECUTION SCRIPT
Deterministic simulation CLI commands:
```bash
# 1. Native R SEM Simulation (Direct execution using Rscript):
Rscript .agents/skills/psychometric-data-simulator/scripts/sem_data_maker.R \
  --preset p13_pies \
  --n 206 \
  --J 5 \
  --seed 451 \
  --out-dir "output_r_sem"

# 2. SEM Simulation via Python Engine (Delegating to R or pure Python):
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset sem_p13_pies \
  --out-dir "sim_p13_results"

# 3. Simulate dataset via research preset:
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset hierarchical_regression \
  --out-dir "sim_hierarchical_results"

# 4. Simulate experimental clinical trial (RCT):
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --preset ancova_trial \
  --out-dir "sim_ancova_results"

# 5. Custom JSON specification:
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode regression \
  --json "sim_config.json" \
  --n 300 \
  --seed 42 \
  --out-dir "custom_sim_output"
```

## 7. OUTPUT CONTRACT
The engine generates:
- `primary_data.xlsx` / `primary_data.csv`: Continuous standardized manifest indicator scores.
- `final_data.xlsx` / `final_data.csv`: Rescaled observed variables with empirical target means and SDs.
- `simulated_<mode>_dataset.xlsx`: Multi-sheet SPSS-ready workbook (`Dataset`, `Composite_Scores`, `Parameters_and_Fit`).
- `sem_results.json`: Complete fit indices (CFI, TLI, RMSEA, SRMR), mediation indirect effects (`:=`), and correlation matrix.
- `sem_plot.pdf`: Path diagram rendered via `semPlot::semPaths`.
- `replicate_sem_analysis.R`: Executable R script replicating the exact model with `mimic = 'EQS'`.

## 8. VALIDATION
- Reject datasets where sample means equal integer values ($M = 5.000$).
- Reject datasets where effect size exceeds empirical reality ($\eta_p^2 > .25$ for psychology).
- Individual participant values must be strictly discrete integers matching Likert bounds.
- Datasets must include complete metadata and never be passed into production without synthetic tagging.

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-NO-CHAPTER-WRITING-IN-DATA-MAKING-001)**: During data generation and SEM/statistical model verification phases, suppress Chapter 4 document compilation. Present only empirical findings: summary statistics, R/Python notebooks, regression/SEM tables, and visualization diagrams. [Enforcement: data_agent_guard.py]
