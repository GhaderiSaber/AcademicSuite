# PRISMA 2020 & Cochrane RoB 2 Methodological and Mathematical Guide

This document outlines the international reporting guidelines, risk of bias appraisal frameworks, and mathematical algorithms required for systematic reviews and quantitative meta-analyses in the behavioral and health sciences.

---

## 1. PRISMA 2020 27-Item Statement Architecture

The **PRISMA 2020 Statement (Page et al., 2021)** consists of a 27-item checklist and a 4-phase operational flow diagram.

### Core Sections:
1. **Title & Abstract**: Explicitly identify as a systematic review / meta-analysis; structured abstract detailing PICO, search span, synthesis method, and primary results with confidence intervals.
2. **Introduction**:
   - *Rationale*: Societal and scientific burden, gaps in existing reviews.
   - *Objectives*: Explicit formulation using the **PICOS** framework:
     - **P** (Population): e.g., Adult patients with diagnosed chronic pain or major depression.
     - **I** (Intervention): e.g., Acceptance and Commitment Therapy (ACT), Mindfulness-Based Cognitive Therapy (MBCT).
     - **C** (Comparator): e.g., Treatment-as-Usual (TAU), Active Control, Waitlist.
     - **O** (Outcomes): e.g., Symptom severity, psychological flexibility, quality of life.
     - **S** (Study Design): e.g., Randomized Controlled Trials (RCTs).
3. **Methods**:
   - *Eligibility Criteria*: Inclusion and exclusion criteria with explicit operational boundaries.
   - *Information Sources*: Databases searched (PubMed/MEDLINE, Scopus, Web of Science, PsycINFO, Cochrane Library, and Iranian databases Magiran, SID, Irandoc), search date limits, and grey literature search.
   - *Search Strategy*: Full Boolean search string for at least one major database.
   - *Selection Process*: Independent screening by at least two reviewers, inter-rater reliability (Cohen's kappa $\kappa$).
   - *Data Collection*: Standardized extraction forms for sample sizes, intervention parameters, and outcomes.
   - *Risk of Bias Assessment*: Dedicated tool (Cochrane RoB 2 for RCTs, ROBINS-I for non-randomized studies).
   - *Effect Measures*: Metric definition (SMD / Hedges' $g$, Risk Ratio, Odds Ratio).
   - *Synthesis Methods*: Fixed-effect vs. random-effects models, heterogeneity estimation ($I^2, Q, \tau^2$).
   - *Reporting Bias Assessment*: Funnel plots, Egger's regression test.
4. **Results**:
   - *Study Selection*: PRISMA Flow Diagram numbers.
   - *Study Characteristics*: Summary table of all included trials.
   - *Risk of Bias in Studies*: Domain-level ratings and traffic-light summary.
   - *Results of Syntheses*: Forest plots, pooled effect sizes, confidence intervals, heterogeneity statistics.
   - *Reporting Biases*: Funnel plot asymmetry and Egger's test results.
5. **Discussion**: Summary of main findings, GRADE certainty of evidence, limitations, and clinical implications.

---

## 2. Cochrane Risk of Bias 2 (RoB 2) Tool

The Cochrane RoB 2 tool assesses randomized trials across 5 canonical domains:

### Domain 1: Bias Arising from the Randomization Process
- *Signaling Question 1.1*: Was the allocation sequence random? (Computer random number generator vs. alternation).
- *Signaling Question 1.2*: Was the allocation sequence concealed until participants were enrolled and assigned? (Sequentially numbered opaque sealed envelopes, central web randomization).
- *Signaling Question 1.3*: Did baseline differences between intervention groups suggest a problem with the randomization process?

### Domain 2: Bias Due to Deviations from Intended Interventions
- *Signaling Question 2.1*: Were participants aware of their assigned intervention during the trial?
- *Signaling Question 2.2*: Were carers and people delivering the interventions aware of participants' assigned intervention?
- *Signaling Question 2.3*: Were there deviations from the intended intervention that arose because of the experimental context?
- *Signaling Question 2.4*: Were these deviations likely to have affected the outcome?
- *Signaling Question 2.5*: Were these deviations balanced between groups?

### Domain 3: Bias Due to Missing Outcome Data
- *Signaling Question 3.1*: Were outcome data available for all, or nearly all, participants randomized?
- *Signaling Question 3.2*: Is there evidence that the result was not biased by missing outcome data?
- *Signaling Question 3.3*: Could missingness in the outcome depend on its true value?

### Domain 4: Bias in Measurement of the Outcome
- *Signaling Question 4.1*: Was the method of measuring the outcome inappropriate?
- *Signaling Question 4.2*: Could measurement or ascertainment of the outcome have differed between intervention groups?
- *Signaling Question 4.3*: Were outcome assessors aware of the intervention received by study participants?
- *Signaling Question 4.4*: Could assessment of the outcome have been influenced by knowledge of intervention received?

### Domain 5: Bias in Selection of the Reported Result
- *Signaling Question 5.1*: Were the data that produced this result analyzed in accordance with a pre-specified analysis plan that was finalized before unblinded outcome data were available for analysis?
- *Signaling Question 5.2*: Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple outcome measurements or analyses?

### Overall Risk of Bias Judgment:
- **Low Risk of Bias**: The study is judged to be at low risk of bias for all 5 domains.
- **Some Concerns**: The study is judged to raise some concerns in at least one domain, but not at high risk in any domain.
- **High Risk of Bias**: The study is judged to be at high risk of bias in at least one domain, or to have some concerns for multiple domains in a way that substantially lowers confidence in the result.

---

## 3. Mathematical Foundations of Quantitative Meta-Analysis

### 1. Effect Size Formulation (Hedges' $g$)
For continuous outcomes with intervention group $(n_1, \bar{x}_1, s_1)$ and control group $(n_2, \bar{x}_2, s_2)$:

**Pooled Standard Deviation ($s_{pooled}$)**:
$$s_{pooled} = \sqrt{\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}$$

**Cohen's $d$**:
$$d = \frac{\bar{x}_1 - \bar{x}_2}{s_{pooled}}$$

**Small-Sample Bias Correction Factor ($J$)**:
$$J = 1 - \frac{3}{4(n_1 + n_2 - 2) - 1}$$

**Hedges' $g$**:
$$g = d \times J$$

**Variance of Hedges' $g$ ($v_g$)**:
$$v_g = \left(\frac{n_1 + n_2}{n_1 n_2} + \frac{d^2}{2(n_1 + n_2)}\right) \times J^2$$

**Standard Error ($SE_g$)**:
$$SE_g = \sqrt{v_g}$$

**Individual Study 95% Confidence Interval**:
$$95\% \text{ CI} = [g - 1.96 \cdot SE_g, \; g + 1.96 \cdot SE_g]$$

---

### 2. Fixed-Effect Model (Inverse-Variance Weighting)
Assumes all studies share a single true effect size ($\theta$).

**Study Weight ($w_i$)**:
$$w_i = \frac{1}{v_i}$$

**Pooled Effect Size ($\bar{g}_{fixed}$)**:
$$\bar{g}_{fixed} = \frac{\sum_{i=1}^k w_i g_i}{\sum_{i=1}^k w_i}$$

**Variance and Standard Error**:
$$v_{\bar{g}_{fixed}} = \frac{1}{\sum_{i=1}^k w_i}, \quad SE(\bar{g}_{fixed}) = \sqrt{v_{\bar{g}_{fixed}}}$$

**Z-Test for Statistical Significance**:
$$Z = \frac{\bar{g}_{fixed}}{SE(\bar{g}_{fixed})}, \quad p = 2 \times (1 - \Phi(|Z|))$$

---

### 3. Heterogeneity Estimation
Quantifies whether variation in effect sizes exceeds that expected from sampling error alone.

**Cochran's $Q$ Statistic**:
$$Q = \sum_{i=1}^k w_i (g_i - \bar{g}_{fixed})^2$$
Under the null hypothesis of homogeneity, $Q \sim \chi^2(df = k - 1)$.

**DerSimonian-Laird Estimator for Between-Study Variance ($\tau^2$)**:
$$C = \sum_{i=1}^k w_i - \frac{\sum_{i=1}^k w_i^2}{\sum_{i=1}^k w_i}$$
$$\tau^2 = \max\left(0, \; \frac{Q - (k - 1)}{C}\right)$$
$$\tau = \sqrt{\tau^2}$$

**Higgins' $I^2$ Statistic**:
$$I^2 = \max\left(0, \; \frac{Q - (k - 1)}{Q}\right) \times 100\%$$
- $0\% - 25\%$: Low heterogeneity
- $25\% - 75\%$: Moderate heterogeneity
- $> 75\%$: High heterogeneity

---

### 4. Random-Effects Model (DerSimonian-Laird)
Assumes true effect sizes vary across studies following a distribution with mean $\mu$ and variance $\tau^2$.

**Random-Effects Study Weight ($w_i^*$)**:
$$w_i^* = \frac{1}{v_i + \tau^2}$$

**Relative Weight Percentage ($W_i\%$)**:
$$W_i\% = \frac{w_i^*}{\sum_{j=1}^k w_j^*} \times 100\%$$

**Pooled Effect Size ($\bar{g}_{random}$)**:
$$\bar{g}_{random} = \frac{\sum_{i=1}^k w_i^* g_i}{\sum_{i=1}^k w_i^*}$$

**Variance and Standard Error**:
$$v_{\bar{g}_{random}} = \frac{1}{\sum_{i=1}^k w_i^*}, \quad SE(\bar{g}_{random}) = \sqrt{v_{\bar{g}_{random}}}$$

**Pooled 95% Confidence Interval**:
$$95\% \text{ CI}_{random} = [\bar{g}_{random} - 1.96 \cdot SE(\bar{g}_{random}), \; \bar{g}_{random} + 1.96 \cdot SE(\bar{g}_{random})]$$

---

### 5. Publication Bias Assessment

#### A. Funnel Plot
Scatter plot of study effect size ($g_i$, x-axis) against study precision ($1 / SE_i$ or standard error $SE_i$, y-axis). In the absence of publication bias, studies form an inverted symmetric funnel centered around the pooled effect size.

#### B. Egger's Linear Regression Test
Quantifies funnel plot asymmetry via weighted linear regression of the standardized effect size on study precision:

$$\frac{g_i}{SE_i} = \beta_0 + \beta_1 \left(\frac{1}{SE_i}\right) + \epsilon_i$$

Where:
- $\beta_1$ represents the true effect size.
- $\beta_0$ (the intercept) measures funnel asymmetry.
- **Decision Rule**: A statistically significant intercept ($p < .05$ for $H_0: \beta_0 = 0$) indicates publication bias (small-study effect), where smaller studies report systematically larger effect sizes.
