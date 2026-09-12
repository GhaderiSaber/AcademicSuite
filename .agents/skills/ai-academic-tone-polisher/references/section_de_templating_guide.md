# Section-Level De-Templating Guide for Academic Manuscripts

When AI detectors flag academic papers, the primary culprit is often **macro-structural template repetition** across paragraphs, rather than isolated words. Large Language Models naturally fall into rigid functional templates, repeating the same paragraph recipe 4 or 5 times in succession.

This guide provides concrete, field-tested de-templating methods for the four most vulnerable manuscript sections: **Introduction Aims, Methodology Measures, Results Reporting, and Discussion Limitations**.

---

## 1. Introduction Aims & Hypotheses De-Templating

### The AI Template Trap:
The LLM writes an introductory sentence followed by a rigid ordinal list:
> ❌ *"Our investigation was guided by four specific hypotheses: First, neuroticism will predict higher pain (H1). Second, personality traits will predict self-compassion (H2). Third, self-compassion will negatively predict pain severity (H3). Finally, self-compassion will mediate the relationship between personality and pain (H4)."*

### The De-Templated Human Restructuring:
Weave the hypotheses into an integrated conceptual rationale, varying the entry point:
> ✅ *"We formulated four primary hypotheses reflecting this structural framework. We hypothesized that dispositional neuroticism would directly exacerbate chronic pain severity, whereas adaptive traits—conscientiousness, extraversion, and agreeableness—would predict lower pain ratings (H1). In parallel, we expected personality traits to predict a student’s self-compassionate coping capacity (H2). Furthermore, drawing on Gilbert’s evolutionary model of affect regulation, we anticipated that self-compassion would directly dampen pain severity (H3), while partially accounting for the indirect pathway linking broad personality vulnerabilities to subjective pain intensity (H4)."*

---

## 2. Methodology Measures De-Templating

### The AI Template Trap:
Every single instrument is described using the identical 5-part recipe:
$$\text{[Construct Name]} \longrightarrow \text{[Author Citation]} \longrightarrow \text{[Item Count]} \longrightarrow \text{[Likert Scale]} \longrightarrow \text{[Cronbach's } \alpha\text{]}$$
When repeated across 3 or 4 instruments, detectors flag the section with > 90% confidence.

### The De-Templated Human Restructuring:
Vary the grammatical subject and organizational focus across instruments:
- **Instrument 1 (Focus on Physiological Anchor)**:
  > *"To capture average physical discomfort over the preceding four weeks, participants completed the 10-cm Visual Analogue Scale (Price et al., 1983). The tool provides a continuous measure bounded by 'no pain at all' (0) and 'worst imaginable pain' (10), demonstrating robust sensitivity across chronic pain populations (r = .97; Delgado et al., 2018)."*
- **Instrument 2 (Focus on Theoretical Taxonomy)**:
  > *"Personality architecture was operationalized via the NEO-FFI short form (Costa & McCrae, 1992). The 60-item inventory samples the Five-Factor framework across 12-item subscales (Neuroticism, Extraversion, Openness, Agreeableness, and Conscientiousness), rated along a 5-point Likert gradient (0 to 4). Persian adaptations confirm sound psychometric stability among Iranian university cohorts, with subscale alphas spanning .74 to .86 (Roshan et al., 2006)."*
- **Instrument 3 (Focus on Self-Regulatory Facets)**:
  > *"Self-compassionate responding was evaluated using Raes and colleagues’ (2011) 12-item SCS-SF. The scale evaluates six balanced affective dimensions (Self-Kindness, Self-Judgment, Common Humanity, Isolation, Mindfulness, and Over-Identification) on a 1-to-5 frequency metric. Negatively keyed items are inverted before calculating a composite total. Shahbazi and colleagues (2015) corroborated the Persian version's high internal consistency (α = .86) and near-perfect convergence with the full 26-item scale (r ≥ .97)."*

---

## 3. Results Narrative De-Templating

### The AI Template Trap:
Repeating the same test reporting sequence:
$$\text{[Test Purpose]} \longrightarrow \text{[Statistical Metric]} \longrightarrow \text{[Hypothesis Verdict]}$$

### The De-Templated Human Restructuring:
1. **Rotate the Sentence Entry Point**:
   - Paragraph 1: Open with the sample demographic profile.
   - Paragraph 2: Open with the empirical range and normality indices.
   - Paragraph 3: Open with the primary theoretical correlation (*"Chronic pain severity demonstrated a robust, statistically significant inverse association with self-compassion (r = -.513, p < .001)..."*).
   - Paragraph 4: Open with the measurement model verification and factor loadings before reporting the structural model.
2. **Weave Mediation Pathways Analytically**:
   - Rather than mechanical path labels (*"Path a was significant, Path b was significant"*), describe the psychological mechanism:
     > *"Structural equation modeling confirmed that personality vulnerability eroded self-compassionate capacity (β = -.544, p < .001), which in turn directly relieved pain severity (β = -.344, p < .001). Crucially, the indirect effect through self-compassion reached statistical significance (indirect β = .187, z = 4.512, p < .001), accounting for roughly 32.6% of the total effect."*

---

## 4. Discussion Limitations De-Templating

### The AI Template Trap:
The classic 4-point ordinal limitation paragraph:
> ❌ *"Certain methodological limitations should be considered. First, because our design was cross-sectional... Second, we relied on self-report questionnaires... Third, our sample was recruited via convenience sampling from a single university... Finally, our study captured general pain severity with the VAS..."*

### The De-Templated Human Restructuring:
Integrate limitations into an analytical discussion of methodological boundary conditions, eliminating all ordinal markers (*First, Second, Third, Finally*):
> ✅ *"Several methodological considerations qualify these findings. Most notably, the cross-sectional architecture precludes definitive causal claims regarding whether self-compassion precedes pain reduction or whether chronic agony progressively depletes self-compassionate resources over time. Prospective longitudinal cohorts or randomized compassion-training trials will be essential to establish directional causality. Furthermore, reliance on retrospective self-report inventories introduces potential recall and social desirability biases, although guaranteed anonymity helped temper response distortions. Readers must also interpret demographic generalizability with care: our cohort was drawn from a single Iranian medical sciences university and comprised predominantly female participants (73.7%). While this profile reflects national healthcare enrollment, whether these affective pathways operate identically across non-medical students or different cultural ecologies warrants systematic cross-validation. Lastly, evaluating global pain severity via the VAS leaves etiology-specific nuances—such as tension headache versus lumbar strain—unexplored, suggesting a fruitful avenue for future clinical sub-typing."*
