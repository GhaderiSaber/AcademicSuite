---
name: moderation
description: Execute moderation interaction analysis (PROCESS Model 1), mean-centering predictors, simple slopes (-1 SD, Mean, +1 SD), and Johnson-Neyman regions.
---

# Moderation Analysis Skill (تحلیل تعدیل‌گری و بررسی اثرات متقابل)

Executes linear moderation interaction analysis (PROCESS Model 1), mean-centering continuous predictors, calculating the interaction term ($X \times W$), estimating conditional effects across moderator values (simple slopes at $-1\text{ SD}, \text{Mean}, +1\text{ SD}$), and probing Johnson-Neyman floodlight regions of significance.

---

## 1. When to Use (Activation Criteria)
Activate this skill when:
1. **Testing Conditional Effects & Boundary Conditions**: Evaluating whether the strength or direction of an association between an independent predictor ($X$) and a dependent outcome ($Y$) changes as a function of a moderator variable ($W$).
2. **Hypothesis Testing for Interaction Effects**: Testing hypotheses such as: "Cognitive flexibility moderates the relationship between occupational stress and depressive symptoms."
3. **Probing Simple Slopes**: Determining at what levels of the moderator the effect of $X$ on $Y$ is statistically significant.
4. **Johnson-Neyman Floodlight Analysis**: Identifying the exact continuous threshold value of the moderator where the effect transitions between significance and non-significance.

---

## 2. When Not to Use (Exclusion Criteria)
Do **NOT** use this skill when:
1. **Uncentered Continuous Predictors**: Never run moderation without mean-centering $X$ and $W$ ($X_c = X - \bar{X}$, $W_c = W - \bar{W}$). Using uncentered variables introduces artificial non-essential multicollinearity between first-order terms and the interaction term ($X \times W$).
2. **Dichotomous Outcome Variables**: If $Y$ is binary, standard OLS moderation is invalid; use Moderated Logistic Regression.
3. **Nonlinear Latent Interactions with Multiple Items**: For latent interaction constructs, use Latent Moderated Structural Equations (LMS via Mplus or lavaan).
4. **Confusing Moderation with Mediation**: Moderation asks *when* or *for whom* an effect occurs (boundary condition); mediation asks *how* or *why* an effect occurs (underlying mechanism).

---

## 3. Required Data & Input Contract
- **Input File**: Cleaned dataset (`.xlsx`, `.csv`, `.sav`).
- **Variables**:
  - $X$: Focal independent continuous predictor.
  - $W$: Moderator variable (continuous or binary).
  - $Y$: Continuous outcome variable.
  - Optional Covariates: $C_1, C_2$.
- **Minimum Sample Size**: $N \ge 120$ (interactions typically require $2\text{--}4\times$ the sample size of main effects for adequate statistical power).

---

## 4. Methodological & Statistical Assumptions
1. **Linearity**: The interaction effect is assumed to change linearly across levels of $W$.
2. **Absence of Severe Multicollinearity**: Evaluated after mean-centering; variance inflation factor $\text{VIF} < 5.0$.
3. **Homoscedasticity of Residuals**: Verified via Breusch-Pagan test.
4. **Normality of Residuals**: Standardized residuals approximately normally distributed.

---

## 5. Method-Selection Decision Tree
```text
Moderator (W) Measurement Level:
├── Categorical / Binary (e.g., Treatment vs Control, Gender):
│   ├── Dummy code W (0, 1)
│   ├── Regression Model: Y = b0 + b1(X) + b2(W) + b3(X * W) + e
│   └── Simple Slopes: Evaluate slope of X for Group 0 and Group 1
└── Continuous Variable (e.g., Age, Emotion Regulation Score):
    ├── Step 1: Mean-Center Predictors -> X_c = X - Mean(X), W_c = W - Mean(W)
    ├── Step 2: Form Cross-Product -> Interaction = X_c * W_c
    ├── Step 3: Hierarchical Regression:
    │   ├── Block 1: Y on X_c + W_c (Main Effects, R1^2)
    │   └── Block 2: Add Interaction (X_c * W_c, R2^2)
    │       └── Test Delta R^2 and F-change (p < .05 confirms moderation)
    └── Step 4: Probing Interaction:
        ├── Pick-a-Point: Simple slopes at -1 SD (Low), Mean (Average), +1 SD (High)
        └── Floodlight: Johnson-Neyman technique (exact value of W where p = .05)
```

---

## 6. Execution Script ("The Hands")
```bash
python3 .agents/skills/moderation/scripts/run_moderation.py \
  --data path/to/cleaned_data.xlsx \
  --iv stress \
  --moderator cognitive_flexibility \
  --dv depression \
  --center \
  --output path/to/08_moderation_results.json
```

---

## 7. Output Contract & Artifacts
The script produces:
1. **`XX_moderation.json`**:
   - `model_summary`: $R^2, \Delta R^2, F_{\text{change}}, p_{\Delta F}$.
   - `coefficients`: Unstandardized ($B, SE$), standardized ($\beta$), $t, p$ for $X_c, W_c$, and $X_c \times W_c$.
   - `simple_slopes`: Slopes at Low ($-1\text{ SD}$), Medium ($\text{Mean}$), High ($+1\text{ SD}$) with $t, p$, and 95% CI.
   - `johnson_neyman`: Cutoff value(s) of moderator and percentage of sample falling in significant region.
2. **APA 7 OpenXML Word Table**: 3-line hierarchical moderation table reporting Block 1 main effects, Block 2 interaction, $\Delta R^2$, and simple slopes.

---

## 8. Validation & Forensic Sanity Checks
- **Mean-Centering Verification**: Confirm that the correlation between centered main effects and interaction term is substantially lower than between uncentered terms.
- **$\Delta R^2$ Significance**: Moderation claim requires statistically significant interaction coefficient ($b_3$) AND significant $\Delta R^2$ $F$-change ($p < .05$).
- **Bounded Plot Range**: Simple slope visualizations must be plotted only within the observed empirical range of the data (no extrapolations beyond $\pm 3\text{ SD}$).
