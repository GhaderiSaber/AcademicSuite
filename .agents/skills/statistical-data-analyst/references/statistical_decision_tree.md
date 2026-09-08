# Psychological Statistical Decision Trees

This reference provides exact decision logic for selecting the appropriate statistical test in psychology and behavioral sciences based on study design, variable types, and distribution assumptions.

---

## 1. Experimental & Quasi-Experimental Designs (Pre-test / Post-test / Follow-up)

Common in clinical psychology, counseling, educational interventions, and psychotherapeutic trials (e.g., CBT vs. Control, Mindfulness vs. Waitlist).

```
Research Question: Did the intervention cause a significant change in the DV?
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
 [Two Groups: Exp vs Control]          [3+ Groups or 3+ Time Points]
            │                                     │
            ▼                                     ▼
 Baseline (Pre-test) measured?         Design has Repeated Measures?
   ├── YES: Check ANCOVA assumptions     ├── Between-subjects only (3+ groups)
   │        (Linearity, Homogeneity           └── One-Way ANOVA (Post-hoc: Tukey/Scheffe)
   │         of Regression Slopes)                 └── If non-normal: Kruskal-Wallis
   │        ► PRIORITY: One-Way ANCOVA   ├── Mixed Design (Group x Time)
   │          (Covariate: Pre-test,           └── Two-Way Mixed ANOVA (Split-Plot)
   │           IV: Group, DV: Post-test)           ├── Check Box's M (Covariance matrices)
   │          *Superior to gain scores*            ├── Check Mauchly's Test (Sphericity)
   │                                               └── If Sphericity violated: Greenhouse-Geisser
   └── NO (Post-test only):              └── Within-subjects only (1 group, 3+ times)
       ├── Assumptions met:                    └── Repeated Measures ANOVA
       │   ► Independent Samples t-test             └── Non-normal: Friedman Test
       └── Assumptions violated:
           ► Mann-Whitney U Test
```

### When to Choose ANCOVA over Gain-Score t-test
- In psychology, **ANCOVA is strongly preferred** over simple $t$-tests on difference scores ($Post - Pre$) because ANCOVA controls for baseline differences and statistical regression to the mean (Lord's Paradox).
- **Critical Assumption to Test**: Homogeneity of regression slopes ($Group \times Pretest$ interaction must be non-significant, $p > .05$).

---

## 2. Correlational & Structural Designs

Common in survey research, personality psychology, psychopathology, and organizational behavior.

```
Research Question: What is the relationship or predictive power among variables?
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
     [Relationships]     [Prediction/Model]   [Mediation/Moderation]
            │                  │                  │
   Both Scale & Normal?  Multiple Predictors?  Process / Path Model?
     ├── YES: Pearson r    ├── Standard OLS      ├── Simple Mediation (Model 4)
     └── NO: Spearman ρ    │   Multiple Reg        ├── Path a: X -> M
                           ├── Hierarchical Reg    ├── Path b: M -> Y (controlling X)
                           │   (Demographics in    ├── Path c': X -> Y (Direct)
                           │    Step 1; Core IVs   └── Indirect effect (ab):
                           │    in Step 2)             MUST report 95% Bootstrap CI
                           └── Check: VIF < 5,         (5,000 resamples).
                               Durbin-Watson ~ 2   └── Moderation (Model 1)
                                                       └── Center variables, test X*W
```

---

## 3. Psychometric Scale Standardization & Factor Analysis

Common in master's theses translating or standardizing foreign psychometric instruments into Persian.

```
Research Question: Is the translated instrument reliable and construct-valid?
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                     ▼
      [Reliability]                         [Validity]
            │                                     │
   Scale Type & Homogeneity?             Theoretical Factor Structure Known?
     ├── Unidimensional/Composite:         ├── YES (Verifying established scale):
     │   ► Cronbach's Alpha (α >= .70)       ► Confirmatory Factor Analysis (CFA)
     │   ► McDonald's Omega (ω >= .70)         ├── Factor Loadings (λ >= .40)
     ├── Item Diagnostics:                     ├── Model Fit Indices:
     │   ► Corrected Item-Total r >= .30       │   - χ²/df < 3.0
     │   ► "Alpha if item deleted"             │   - CFI >= .90 (ideal >= .95)
     └── Split-Half:                           │   - TLI >= .90 (ideal >= .95)
         ► Guttman / Spearman-Brown            │   - RMSEA <= .08 (ideal <= .06)
                                               │   - SRMR <= .08
                                               └── Convergent/Discriminant:
                                                   - CR >= .70, AVE >= .50
                                           └── NO (Exploring new instrument):
                                               ► Exploratory Factor Analysis (EFA)
                                                   - KMO > .70, Bartlett's p < .001
                                                   - Extraction: Principal Axis / ML
                                                   - Rotation: Promax (correlated) /
                                                               Varimax (orthogonal)
```

---

## 4. Assumption Violation Fallback Matrix

| Primary Parametric Test | Required Assumptions | Test for Assumption | Non-Parametric Fallback |
| :--- | :--- | :--- | :--- |
| **Independent $t$-test** | Normality, Homogeneity of Variance | Shapiro-Wilk ($p > .05$), Levene's Test ($p > .05$) | **Mann-Whitney $U$ Test** (or Welch's $t$ if only variance violated) |
| **Paired Samples $t$-test** | Normality of difference scores | Shapiro-Wilk on $(X_1 - X_2)$ ($p > .05$) | **Wilcoxon Signed-Rank Test** |
| **One-Way ANOVA** | Normality, Homogeneity of Variance | Shapiro-Wilk, Levene's Test | **Kruskal-Wallis $H$ Test** |
| **Repeated Measures ANOVA** | Sphericity | Mauchly's Test ($p > .05$) | **Greenhouse-Geisser / Huynh-Feldt correction** or **Friedman Test** |
| **ANCOVA** | Homogeneity of regression slopes, Linear covariate-DV relation | Group $\times$ Covariate interaction ($p > .05$), Scatterplot | **Quade's Non-parametric ANCOVA** or Rank ANCOVA |
| **Pearson Correlation ($r$)** | Bivariate Normality, Linearity | Shapiro-Wilk, Scatterplot inspection | **Spearman Rank Correlation ($\rho$)** or **Kendall's $\tau$** |
| **Multiple Regression** | Normality of residuals, No Multicollinearity, Homoscedasticity | Q-Q plot, VIF $< 5.0$, Breusch-Pagan test | **Robust Regression** (Huber/RANSAC) or **Log Transformation** |
