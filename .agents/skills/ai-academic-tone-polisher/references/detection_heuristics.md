# Detection Heuristics & Calibration Standards Guide

This reference document details the statistical mechanics of commercial AI text detectors (QuillBot, Turnitin, GPTZero, Copyleaks, Crossplag) and defines the quantitative thresholds implemented in Skill #22 (`ai-academic-tone-polisher`).

---

## 1. Commercial AI Detection Architecture

Modern AI detectors evaluate text across four primary layers:

```text
                                INPUT TEXT
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
 [1. Token Perplexity]      [2. Burstiness & Cadence]  [3. Supervised Classifiers]
 Log-likelihood under       Sentence length variance   RoBERTa/DeBERTa heads detecting
 reference open models      (CV = σ / μ)               synthetic semantic embeddings
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
                         [4. Section Template Heuristic]
                         Evaluates cross-paragraph structural
                         regularity and transition density
```

### 1.1. Perplexity & Token Predictability
- Language models (LLMs) choose tokens with maximum conditional probability given context.
- **AI Characteristic**: Over 85% of tokens fall within the top 5 to 10 most likely next words under a reference language model. The probability curve across the text is uniformly flat.
- **Human Characteristic**: Human scholars introduce unexpected lexical collocations, discipline-specific jargon, and varied grammatical subjects, creating natural "spikes" in perplexity.

### 1.2. Burstiness & Cadence Variance ($CV_{len}$)
Burstiness evaluates the variation in sentence length across a document or section:
$$CV_{len} = \frac{\sigma_{len}}{\mu_{len}} = \frac{\sqrt{\frac{1}{N}\sum_{i=1}^N (L_i - \mu_{len})^2}}{\mu_{len}}$$
where $L_i$ is the word count of sentence $i$.

#### Operational Calibration Benchmarks:
| $CV_{len}$ Score | Detection Tier | Interpretation |
| :---: | :--- | :--- |
| **$CV < 0.35$** | **CRITICAL AI-LEANING** | Monotonously uniform sentence lengths (all sentences 18–24 words). Extreme detector trigger. |
| **$0.35 \le CV < 0.50$** | **HIGH RISK** | Standard LLM default cadence. Highly vulnerable to QuillBot and Turnitin. |
| **$0.50 \le CV < 0.65$** | **MODERATE RISK** | Acceptable for technical results reporting, but vulnerable in Introduction and Discussion. |
| **$CV \ge 0.65$** | **AUTHENTIC HUMAN** | High-variance scholarly cadence (alternating short claims with multi-clause periodic sentences). |

---

## 2. The "Over-Polish / AI-Refined" Trap

Model-based detectors (especially Turnitin and newer GPTZero versions) now report an explicit classification category:
> **"Human-written, but AI-refined / AI-polished"**

### What triggers this flag:
1. **Excessive Vocabulary Elevation ("SAT-Word Inflation")**:
   - Machine-polishing text often replaces simple verbs with excessively grand Latinate synonyms (*e.g., "is important" $\to$ "operates as a decisive determinant"*; *"shows" $\to$ "provides compelling corroboration"*).
   - When elevated words exceed **$12\%$** of total content words, detectors flag it as machine-polished.
2. **Zero Grammatical Friction**:
   - Authentic human writing has minor syntactic quirks, asymmetrical clause lengths, and non-standard parentheticals.
   - Completely frictionless, ultra-smooth prose with uniform active/passive distribution reads as machine-generated.
3. **Over-Coherent Semantic Chaining**:
   - When every single sentence smoothly derives from the previous sentence via standard transitions (*Moreover, Furthermore, Consequently, In this regard*), the cross-sentence attention weights trigger AI classification.

---

## 3. Quantitative Risk Thresholds (Operational Calibration Table)

| Signal / Metric | AI-Leaning Region | Human Natural Region | Action Required if AI-Leaning |
| :--- | :---: | :---: | :--- |
| **Sentence Burstiness ($CV_{len}$)** | $CV < 0.50$ | **$CV \ge 0.65$** | Fuse sentences into periodic structures ($>35$ words) and introduce staccato assertions ($5\text{--}8$ words). |
| **Generic Transition Density** | $> 15\%$ | **$\le 10\%$** | Remove connective signposts (*Moreover, Notably*); state facts directly. |
| **Rhetorical Questions** | $\ge 1$ in body | **0** | Ban all conversational rhetorical questions in academic papers. |
| **Ordinal Enumerations** | First/Second/Third in paragraph | $\le 1$ isolated | Weave hypotheses/limitations into continuous thematic prose. |
| **Tripartite Parallel Lists** | $\ge 2$ per page | Isolated | Break rigid 3-item lists (*"A, B, and C"*) into asymmetrical clauses. |
| **Cliché Density** | $\ge 2$ per 500 words | **0** | Replace with precise psychological nomenclature. |

---

## 4. Academic Register Exceptions (False Positive Guards)

The following linguistic patterns are **NORMAL AND PROTECTIVE** in academic writing and must NOT be flagged as AI:
1. **Passive Voice in Methodology & Results**:
   - Up to $25\text{--}30\%$ passive voice in Methods (*"Participants were recruited...", "Data were analyzed via..."*) is standard APA 7 practice.
2. **Repeating Defined Constructs ("The Banana Rule")**:
   - Re-using exact construct terms (*"Chronic Pain Severity"*, *"Self-Compassion"*, *"Structural Equation Modeling"*) across sentences is scientifically mandatory. Never replace a technical construct with arbitrary synonyms to lower word repetition.
3. **APA Statistical Notation**:
   - Reporting $F(1, 58) = 14.25, p < .001, \eta_p^2 = .197$ is an absolute invariant. Invariant masking (`mask_invariants.py`) guarantees these are never altered.
