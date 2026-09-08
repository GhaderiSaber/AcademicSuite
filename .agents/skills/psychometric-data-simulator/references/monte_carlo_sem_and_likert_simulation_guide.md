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
