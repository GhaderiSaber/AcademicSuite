---
name: longitudinal-moderated-mediation
description: Execute 3-wave longitudinal moderated mediation modeling, autoregressive baseline controls, and 5,000 bootstrap index estimation.
---

# Longitudinal Moderated Mediation Skill

This skill provides deterministic estimation and reporting for time-lagged conditional process models across three or more longitudinal measurement waves. It evaluates whether the indirect effect of a Time 1 predictor ($X_{T1}$) on a Time 3 outcome ($Y_{T3}$) through a Time 2 mediator ($M_{T2}$) is moderated by a Time 1 boundary condition ($W_{T1}$), while controlling for baseline autoregressive stability ($M_{T1}, Y_{T1}$).

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill when:
- The research design contains at least 3 distinct measurement waves ($T_1, T_2, T_3$).
- Testing conditional indirect effects (moderated mediation, PROCESS Model 7 longitudinal adaptation).
- Establishing temporal precedence: $X_{T1} \to M_{T2} \to Y_{T3}$ to guard against cross-sectional mediation bias (Maxwell & Cole, 2007).
- Estimating the Index of Moderated Mediation with 5,000 bootstrap resamples.

## 2. WHEN NOT TO USE (Exclusion Criteria)
Do NOT use this skill when:
- Data was collected concurrently in a single cross-sectional survey wave $\to$ use `mediation` or `moderation`.
- Only 2 measurement waves exist $\to$ autoregressive mediation cannot establish full 3-point temporal sequencing; consider difference score or residualized gain analysis.
- The model contains reciprocal cross-lagged structural paths ($X \rightleftarrows M \rightleftarrows Y$) or latent constructs $\to$ use `sem`.
- Missing wave attrition exceeds 20% and requires full random-slopes growth modeling $\to$ consider Linear Mixed Models (LMM).

## 3. REQUIRED DATA
- **Dataset Structure**: Wide format containing columns:
  - `x_t1`: Predictor at Wave 1.
  - `w_t1`: Moderator at Wave 1.
  - `m_t1`: Mediator baseline at Wave 1 (Autoregressive control).
  - `m_t2`: Mediator at Wave 2.
  - `y_t1`: Outcome baseline at Wave 1 (Autoregressive control).
  - `y_t3`: Outcome at Wave 3.
- **Sample Size**: Minimum $N \ge 150\text{--}250$ to achieve adequate power ($\ge .80$) for conditional indirect effect detection with 5,000 bootstraps.

## 4. ASSUMPTIONS
1. **Temporal Precedence**: $X$ measured strictly prior to $M$, and $M$ measured strictly prior to $Y$.
2. **Autoregressive Control**: Prior equilibrium variance of $M$ and $Y$ at $T_1$ must be statistically adjusted to estimate genuine change.
3. **No Unmeasured Confounding**: Residuals across equation stages are uncorrelated conditional on baseline controls.
4. **Linearity and Normality of Residuals**: Residuals in OLS equations are normally distributed with homogeneous variance.
5. **Non-Normal Product Distribution**: Indirect and moderated mediation indices do not follow a normal distribution; 5,000 bias-corrected bootstrap resamples are mandatory.

## 5. DECISION TREE

```
Longitudinal Mediation / Moderation Design
  │
  ├─► Measurement Waves Available:
  │     ├─► 1 Wave (Cross-Sectional):
  │     │     └─► HALT: Cannot run longitudinal modeling.
  │     │           └─► Cross-sectional mediation (warn about parameter bias)
  │     │
  │     ├─► 2 Waves (Pre-test / Post-test):
  │     │     └─► Half-longitudinal model (cannot establish full X -> M -> Y sequence)
  │     │
  │     └─► 3+ Waves (Time 1, Time 2, Time 3):
  │           ├─► Baseline Autoregressive Controls (M_T1, Y_T1) Available?
  │           │     ├─► YES:
  │           │     │     └─► [3-Wave Autoregressive Moderated Mediation]
  │           │     │           - Equation 1: M_T2 ~ X_T1 + W_T1 + (X_T1 × W_T1) + M_T1
  │           │     │           - Equation 2: Y_T3 ~ M_T2 + X_T1 + Y_T1
  │           │     │           - Index = a3 × b1
  │           │     │           - 5,000 Bootstrap Resamples for 95% BCa CI
  │           │     └─► NO:
  │           │           └─► WARNING: High risk of inflated indirect effect due to
  │           │               uncontrolled baseline stability. Flag in methodology notes.
  │           │
  │           └─► Attrition / Missingness across Waves:
  │                 ├─► Missing < 5%: Listwise or MICE imputation acceptable
  │                 └─► Missing > 5%: Linear Mixed Models (LMM) with FIML required
```

## 6. EXECUTION SCRIPT
Execute deterministic 3-wave conditional process modeling:
```bash
python3 .agents/skills/longitudinal-moderated-mediation/scripts/run_longitudinal_modmed.py \
  --data "data_longitudinal.xlsx" \
  --output "longitudinal_modmed_results.json"
```

## 7. OUTPUT CONTRACT
The calculation produces `longitudinal_modmed_results.json`:
```json
{
  "model_type": "Longitudinal Moderated Mediation (Wave 1 -> Wave 2 -> Wave 3)",
  "sample_size": 280,
  "mediator_model": {
    "r_squared": 0.3842,
    "f_stat": 42.15,
    "p_value": 0.0001,
    "interaction_coeff_a3": 0.1845,
    "interaction_p_value": 0.0124
  },
  "outcome_model": {
    "r_squared": 0.4125,
    "f_stat": 48.32,
    "p_value": 0.0001,
    "b1_coeff": 0.3421,
    "b1_p_value": 0.0002
  },
  "moderated_mediation_index": {
    "index": 0.0631,
    "bootstrap_samples": 5000,
    "ci_95_lower": 0.0142,
    "ci_95_upper": 0.1285,
    "significant": true
  },
  "verdict": "SUPPORTED"
}
```

## 8. VALIDATION
- Bootstrap 95% confidence interval must not cross zero for statistical significance of the moderated mediation index.
- Baseline autoregressive coefficients ($M_{T1}, Y_{T1}$) must be verified and reported.
- Collinearity diagnostics (VIF) between main terms and interaction term must be checked ($VIF < 5$ after mean-centering if needed).
- All numbers in narrative tables must strictly match `longitudinal_modmed_results.json`.
