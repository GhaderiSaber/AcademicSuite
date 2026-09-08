# Monte Carlo SEM, CFA & Likert Scale Simulation Mathematical Guide

This reference guide documents the statistical and linear algebra methods powering the `psychometric-data-simulator` engine, ported from the [`GhaderiSaber/SimDat`](https://github.com/GhaderiSaber/SimDat.git) architecture.

---

## 1. Latent Factor Generation via Cholesky Factorization

When simulating Confirmatory Factor Analysis (CFA) or correlated exogenous predictors, latent factors must exhibit exact target inter-factor correlations ($\mathbf{R}$).

Given a $K \times K$ target correlation matrix $\mathbf{R}$:
1. Ensure $\mathbf{R}$ is positive semi-definite (eigenvalues $\ge 0$).
2. Compute the lower-triangular Cholesky factor $\mathbf{L}$ such that:
   $$\mathbf{R} = \mathbf{L} \mathbf{L}^T$$
3. For sample size $N$, draw $K$ independent standard normal vectors:
   $$\mathbf{Z} \sim \mathcal{N}(\mathbf{0}, \mathbf{I}_{K \times N})$$
4. The correlated latent factor matrix $\mathbf{H}$ is given by:
   $$\mathbf{H} = \mathbf{L} \mathbf{Z}$$
   Where $\text{Cov}(\mathbf{H}) \approx \mathbf{R}$.

---

## 2. Structural Equation Modeling (SEM) Recursive DAG Propagation

In full structural equation models, relationships follow a Directed Acyclic Graph (DAG) partitioned into **Exogenous Predictors ($\xi$)**, **Mediators ($\eta_{med}$)**, and **Endogenous Criteria ($\eta_{crit}$)**:

$$\mathbf{\eta} = \mathbf{B} \mathbf{\eta} + \mathbf{\Gamma} \mathbf{\xi} + \mathbf{\zeta}$$

Where:
- $\mathbf{\xi} \sim \mathcal{N}(\mathbf{0}, \mathbf{\Phi})$ represents exogenous latent predictors.
- $\mathbf{B}$ is the matrix of structural path coefficients among endogenous constructs (sub-diagonal for recursive models).
- $\mathbf{\Gamma}$ is the matrix of path coefficients from exogenous to endogenous constructs.
- $\mathbf{\zeta} \sim \mathcal{N}(\mathbf{0}, \mathbf{\Psi})$ is the vector of structural disturbance terms (residual error variances).

### Mediation & Defined Parameters:
- Direct effect: $c'$
- Specific indirect effect: $ab = a \times b$
- Total effect: $c = c' + ab$
- Standardized indirect effect: $\beta_{ab} = \beta_a \times \beta_b$

---

## 3. Discrete Likert Questionnaire Item Simulation & Quantization

Classical Test Theory (CTT) and factor analytic measurement models define the observed continuous response $y^*_{ij}$ of individual $i$ to item $j$ of construct $\eta$:

$$y^*_{ij} = \lambda_j \eta_i + \epsilon_{ij}, \quad \epsilon_{ij} \sim \mathcal{N}(0, \theta_j)$$

Where:
- $\lambda_j$ is the standardized factor loading of item $j$ (typically $.60 \le \lambda_j \le .85$).
- $\theta_j = 1 - \lambda_j^2$ is the unique residual variance (measurement error).

### Quantization into Discrete Likert Categories:
To transform continuous $y^*_{ij}$ into realistic integers (e.g., a 5-point Likert scale $1, 2, 3, 4, 5$ with theoretical mean $\mu_{item} = 3.0$ and item standard deviation $\sigma_{item} = 1.0$):

1. **Standardize Raw Indicator**:
   $$\tilde{y}_{ij} = \frac{y^*_{ij}}{\sqrt{\lambda_j^2 + \theta_j}}$$
2. **Rescale to Item Bounds**:
   $$y_{ij} = \text{round}\left(\tilde{y}_{ij} \cdot \sigma_{item} + \mu_{item}\right)$$
3. **Truncate / Bound to Category Limits**:
   $$y_{ij} = \max\left(Min, \; \min\left(Max, \; y_{ij}\right)\right)$$

### Reverse-Keyed / Negatively Worded Items:
If item $j$ is negatively keyed (e.g., in depression or anxiety scales), the raw simulated score is inverted before assembling composite totals:
$$y^{\text{recoded}}_{ij} = (Min + Max) - y_{ij}$$

---

## 4. Internal Consistency & Target Cronbach's Alpha ($\alpha$)

Cronbach's $\alpha$ is a function of the number of items ($k$) and the average inter-item correlation ($\bar{r}$):

$$\alpha = \frac{k \cdot \bar{r}}{1 + (k - 1)\bar{r}}$$

Under a tau-equivalent or congeneric factor model with average loading $\bar{\lambda}$, the expected average inter-item correlation is $\bar{r} \approx \bar{\lambda}^2$. By tuning indicator loadings $\lambda_j \in [0.65, 0.85]$ and error variances $\theta_j$, target internal consistency ($\alpha \ge .80$) is mathematically guaranteed.

---

## 5. Experimental RCT Clinical Trial Simulation

For randomized controlled trials with repeated measurement occasions (Pretest, Posttest, Follow-up):

$$\mathbf{Y}_{ij} = \mu_j + \beta_{\text{group}} \cdot \text{Group}_i + \beta_{\text{time}} \cdot \text{Time}_j + \beta_{\text{interaction}} \cdot (\text{Group}_i \times \text{Time}_j) + u_i + \epsilon_{ij}$$

Where:
- $\text{Group}_i \in \{0 = \text{Control}, 1 = \text{Intervention}\}$.
- Baseline Pretest: $\beta_{\text{group}} = 0$ (confirming baseline equivalence, $p > .05$).
- Posttest Intervention Effect: $\beta_{\text{interaction}} = d \cdot \sigma_{pooled}$.
- $u_i \sim \mathcal{N}(0, \sigma^2_u)$ represents individual random subject intercepts ensuring realistic test-retest autocorrelation ($r \approx .60 - .80$).

---

## 6. SEM Goodness-of-Fit Metric Derivations

Let $\mathbf{S}$ be the empirical sample covariance matrix ($p \times p$), and $\mathbf{\Sigma}(\hat{\theta})$ be the model-implied covariance matrix:

1. **Maximum Likelihood Discrepancy Function ($F_{ML}$)**:
   $$F_{ML} = \ln|\mathbf{\Sigma}| - \ln|\mathbf{S}| + \text{tr}(\mathbf{S}\mathbf{\Sigma}^{-1}) - p$$
2. **Model Chi-Square ($\chi^2$)**:
   $$\chi^2 = (N - 1) F_{ML}, \quad df = \frac{p(p + 1)}{2} - q$$
   Where $q$ is the number of estimated free parameters.
3. **Comparative Fit Index (CFI)**:
   $$CFI = 1 - \frac{\max(0, \; \chi^2_M - df_M)}{\max(0, \; \chi^2_B - df_B)}$$
   Where subscript $B$ denotes the baseline / independence null model.
4. **Root Mean Square Error of Approximation (RMSEA)**:
   $$RMSEA = \sqrt{\max\left(0, \; \frac{\chi^2_M - df_M}{(N - 1) df_M}\right)}$$
5. **Standardized Root Mean Square Residual (SRMR)**:
   $$SRMR = \sqrt{\frac{2 \sum_{i \le j} \left(\frac{s_{ij} - \sigma_{ij}}{\sqrt{s_{ii} s_{jj}}}\right)^2}{p(p + 1)}}$$

**Standard Academic Fit Benchmarks**:
- $CFI \ge 0.95$ (Good), $\ge 0.90$ (Acceptable)
- $TLI \ge 0.95$ (Good), $\ge 0.90$ (Acceptable)
- $RMSEA \le 0.06$ (Good), $\le 0.08$ (Acceptable)
- $SRMR \le 0.08$ (Good)

---

## 7. Multiple & Hierarchical Linear Regression Simulation

### A. OLS Model Formulation:
$$\mathbf{y} = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(\mathbf{0}, \sigma^2_\epsilon \mathbf{I})$$

To calibrate to a target population coefficient of determination $R^2$:
$$\sigma^2_y = \boldsymbol{\beta}^T \mathbf{\Sigma}_{xx} \boldsymbol{\beta} + \sigma^2_\epsilon \implies \sigma^2_\epsilon = \boldsymbol{\beta}^T \mathbf{\Sigma}_{xx} \boldsymbol{\beta} \left(\frac{1 - R^2}{R^2}\right)$$

### B. Hierarchical Regression ($\Delta R^2$ and $\Delta F$):
- **Model 1 (Step 1)**: Control variables / Demographics ($k_1$ predictors) $\implies R_1^2, F_1$.
- **Model 2 (Step 2)**: Added primary psychological predictors ($k_2$ predictors) $\implies R_2^2, F_2$.
- **Incremental Variance Explained**:
  $$\Delta R^2 = R_2^2 - R_1^2$$
  $$\Delta F = \frac{\Delta R^2 / k_2}{(1 - R_2^2) / (N - k_1 - k_2 - 1)}$$
  With $df_1 = k_2, \; df_2 = N - k_1 - k_2 - 1$.

---

## 8. Moderation Analysis (Hayes PROCESS Model 1) & Simple Slopes

For focal predictor $X$ and moderator $W$:
1. **Mean-Center Predictors**:
   $$X_c = X - \bar{X}, \quad W_c = W - \bar{W}, \quad XW = X_c \cdot W_c$$
2. **Moderated Regression Model**:
   $$\hat{Y} = b_0 + b_1 X_c + b_2 W_c + b_3 (XW)$$
   Where $b_3$ captures the moderation interaction.
3. **Conditional Simple Slopes**:
   Re-arranging: $\hat{Y} = (b_0 + b_2 W_c) + (b_1 + b_3 W_c) X_c$.
   - **Low Moderator** ($W_c = -1 SD_W$): $\text{Slope}_{\text{Low}} = b_1 + b_3(-SD_W)$
   - **Mean Moderator** ($W_c = 0$): $\text{Slope}_{\text{Mean}} = b_1$
   - **High Moderator** ($W_c = +1 SD_W$): $\text{Slope}_{\text{High}} = b_1 + b_3(+SD_W)$

---

## 9. Factorial ANOVA & MANOVA Simulation

### A. Two-Way Factorial ANOVA ($A \times B$):
$$Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \epsilon_{ijk}$$
- Main effect Factor A: $F_A = \frac{MS_A}{MS_{Error}}, \quad \eta_p^2(A) = \frac{SS_A}{SS_A + SS_{Error}}$
- Main effect Factor B: $F_B = \frac{MS_B}{MS_{Error}}, \quad \eta_p^2(B) = \frac{SS_B}{SS_B + SS_{Error}}$
- Interaction effect: $F_{AB} = \frac{MS_{AB}}{MS_{Error}}, \quad \eta_p^2(AB) = \frac{SS_{AB}}{SS_{AB} + SS_{Error}}$

### B. Multivariate ANOVA (MANOVA):
For $m$ continuous correlated DVs across $k$ groups:
$$\mathbf{Y}_{ig} \sim \mathcal{N}_m(\boldsymbol{\mu}_g, \mathbf{\Sigma}_{within})$$
- Hypothesis sum-of-squares and cross-products: $\mathbf{H} = \sum_{g=1}^k n_g (\bar{\mathbf{y}}_g - \bar{\mathbf{y}})(\bar{\mathbf{y}}_g - \bar{\mathbf{y}})^T$
- Error sum-of-squares and cross-products: $\mathbf{E} = \sum_{g=1}^k \sum_{i=1}^{n_g} (\mathbf{y}_{ig} - \bar{\mathbf{y}}_g)(\mathbf{y}_{ig} - \bar{\mathbf{y}}_g)^T$
- **Wilks' Lambda**:
  $$\Lambda = \frac{|\mathbf{E}|}{|\mathbf{H} + \mathbf{E}|}$$

---

## 10. Repeated Measures & Autoregressive AR(1) Temporal Covariance

For longitudinal designs with $T$ measurement waves (Pre, Post, Follow-up 1, Follow-up 2):
$$\mathbf{\Sigma}_{time} = \sigma^2 \begin{bmatrix}
1 & \rho & \rho^2 & \dots & \rho^{T-1} \\
\rho & 1 & \rho & \dots & \rho^{T-2} \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
\rho^{T-1} & \rho^{T-2} & \rho^{T-3} & \dots & 1
\end{bmatrix}$$
Where $\rho \in [0.50, 0.75]$ reflects test-retest autocorrelation.
Greenhouse-Geisser sphericity estimate $\hat{\epsilon}$ measures departure from circularity:
$$\hat{\epsilon} = \frac{T^2 (\bar{s}_{ii} - \bar{s}_{\cdot\cdot})^2}{(T - 1) \left(\sum \sum s_{ij}^2 - 2 T \sum \bar{s}_{i\cdot}^2 + T^2 \bar{s}_{\cdot\cdot}^2\right)}$$

---

## 11. Binary Logistic Regression Simulation

For dichotomous outcomes $Y_i \in \{0, 1\}$ (e.g., Clinical Diagnosis, Treatment Remission):
1. **Linear Predictor (Log-Odds)**:
   $$z_i = \beta_0 + \sum_{j=1}^p \beta_j X_{ij} = \beta_0 + \sum_{j=1}^p \ln(OR_j) \cdot X_{ij}$$
2. **Sigmoid / Logit Inversion**:
   $$P(Y_i = 1 \mid \mathbf{X}_i) = \frac{1}{1 + \exp(-z_i)}$$
3. **Bernoulli Outcome Draw**:
   $$Y_i \sim \text{Bernoulli}(P(Y_i = 1))$$

---

## 12. Non-Parametric Skewed Distributions & Categorical Contingency

### A. Gamma Skewed Continuous Generation:
For clinical constructs (depression, panic) exhibiting heavy positive skewness:
$$X \sim \text{Gamma}(\kappa, \theta) + c$$
Where shape $\kappa = 2.0$ yields skewness $\gamma_1 = \frac{2}{\sqrt{\kappa}} = 1.41$, evaluated via **Mann-Whitney $U$** or **Kruskal-Wallis $H$**.

### B. Categorical Contingency Matrix ($r \times c$):
Multinomial draws from specified joint cell probabilities:
$$\chi^2 = \sum_{i=1}^r \sum_{j=1}^c \frac{(O_{ij} - E_{ij})^2}{E_{ij}}, \quad V = \sqrt{\frac{\chi^2}{N \min(r-1, c-1)}}$$
