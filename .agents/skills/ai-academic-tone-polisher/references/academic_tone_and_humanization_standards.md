# Academic Tone & Anti-AI Linguistic Standards Guide

This reference document defines the theoretical foundations, statistical metrics, lexical catalogs, and syntactic rules implemented in the **`ai-academic-tone-polisher`** skill of the **AcademicSuite**.

---

## 1. Mathematical & Statistical Foundations of AI Text Detection

AI detection algorithms (Turnitin AI, GPTZero, ZeroGPT, CopyLeaks, SamimNoor / همانندجو) rely on two fundamental statistical properties of text: **Perplexity** and **Burstiness**.

### 1.1. Perplexity (Predictability of Word Choice)
- **Definition**: Perplexity measures how well a language model predicts a sequence of words.
  $$\text{Perplexity}(W) = \exp \left( -\frac{1}{N} \sum_{i=1}^N \ln P(w_i \mid w_1, \dots, w_{i-1}) \right)$$
- **AI Characteristics**: Large Language Models (LLMs) choose tokens with maximum conditional probability given context. As a result, LLM text has **artificially low perplexity** (extremely predictable word choices, frequent cliché transitions).
- **Human Characteristics**: Scholars employ specialized domain terminology, nuanced synonyms, disciplinary metaphors, and unexpected lexical collocations, resulting in **moderate-to-high perplexity**.

### 1.2. Burstiness (Variance in Sentence Cadence)
- **Definition**: Burstiness measures the variation in sentence length and syntactic complexity across a document, quantified by the **Coefficient of Variation ($CV_{len}$)**:
  $$CV_{len} = \frac{\sigma_{len}}{\mu_{len}} = \frac{\sqrt{\frac{1}{M}\sum_{j=1}^M (L_j - \mu_{len})^2}}{\mu_{len}}$$
  where $L_j$ is the word count of sentence $j$, and $\mu_{len}$ is the mean sentence length.
- **AI Characteristics**: LLMs generate text with remarkably homogeneous sentence lengths (typically $18 \text{--} 24$ words per sentence), yielding a low burstiness score:
  $$CV_{len} < 0.35 \implies \mathbf{Strong\ AI\ Indicator}$$
- **Human Scholar Characteristics**: Human scholars naturally fluctuate between short, emphatic thesis statements ($6 \text{--} 12$ words) and intricate, multi-clause compound-complex analytical sentences ($35 \text{--} 55$ words), yielding:
  $$CV_{len} \ge 0.50 \implies \mathbf{Authentic\ Human\ Scholarly\ Cadence}$$

### 1.3. Lexical Diversity (Type-Token Ratio & MTLD)
- **Type-Token Ratio (TTR)**: $TTR = \frac{V}{N}$ where $V$ is unique words (types) and $N$ is total tokens.
- **Root TTR (Guiraud's Index)**: $R = \frac{V}{\sqrt{N}}$ (corrects for text length).
- **Measure of Textual Lexical Diversity (MTLD)**: Mean length of sequential word strings maintaining $TTR \ge 0.72$. Authentic academic writing exhibits higher MTLD due to rich disciplinary nomenclature.

---

## 2. Persian Academic Tone: AI Cliches vs. Authentic Academic Substitutions

Standard LLMs translating or generating Persian academic prose rely heavily on predictable filler phrases and literal syntactic calques (گرته‌برداری ساختاری). Below is the canonical transformation catalog:

| # | AI Robotic Filler / Cliche | Disciplinary Issue | Authentic Academic Scholarly Alternative |
| :---: | :--- | :--- | :--- |
| 1 | **شایان ذکر است که...** | Overused empty filler | *«یافته‌های حاضر مؤید آن است که...»* / *«از منظری تحلیلی، ...»* / ادغام مستقیم در جمله |
| 2 | **در این راستا...** | Mechanical transition | *«در همین چارچوب مفهومی،...»* / *«به منظور تبیین این سازوکار،...»* / *«در پرتو این شواهد،...»* |
| 3 | **به طور کلی می‌توان گفت که...** | Weak, evasive generalization | *«مجموعه شواهد تجربی دلالت بر آن دارند که...»* / *«برآیند یافته‌ها نشان می‌دهد...»* |
| 4 | **این امر نشان‌دهنده آن است که...** | Passive demonstrative calque | *«این الگو بازتاب‌دهنده...»* / *«این پدیده با تکیه بر نظریه [...] حاکی از...»* |
| 5 | **همان‌طور که می‌دانیم...** | Presumptuous, non-scholarly | *«بر پایه ادبیات نظری مستقر،...»* / *«مفروضات بنیادین این الگو تصریح می‌کنند که...»* |
| 6 | **نقش بسیار مهمی ایفا می‌کند** | English calque (*plays a crucial role*) | *«نقشی کانونی/تعیین‌کننده در [...] ایفا می‌نماید»* / *«سهم عمده‌ای در تبیین [...] دارد»* |
| 7 | **لازم به یادآوری است که...** | Didactic filler | *«توجه به این نکته ضروری است که...»* / *«در امتداد این استدلال،...»* |
| 8 | **از این رو / بدین ترتیب (پیاپی)** | Monotonous causal chaining | تنوع‌بخشی با *«بنابراین»*، *«نتیجتاً»*، *«از پیامدهای این فرایند...»* |
| 9 | **انجام گردیده شد / نشان داده شده است** | Redundant Persian passives | *«به اجرا درآمد»* / *«انجام پذیرفت»* / *«شواهد نشان داد»* |
| 10 | **به چالش کشیده می‌شود** | Literal calque (*is challenged*) | *«مورد تردید قرار می‌گیرد»* / *«با چالش‌های نظری روبه‌روست»* |
| 11 | **یک تصویر واضح ارائه می‌دهد** | Literal calque (*provides a clear picture*) | *«تصویری روشن از سازوکارهای [...] ترسیم می‌کند»* |
| 12 | **به عنوان یک عامل موثر عمل می‌کند** | Verbose calque (*acts as an effective factor*) | *«در مقام عاملی اثرگذار، زمینه [...] را فراهم می‌آورد»* |
| 13 | **تاثیرات مثبت / منفی زیادی دارد** | Vague, colloquial | *«اثرات معنادار و افزاینده‌ای بر [...] بر جای می‌گذارد»* |
| 14 | **پژوهشگران به این نتیجه رسیدند که** | Conversational reporting | *«بررسی‌های تجربی حاکی از استنتاجی همسو مبنی بر [...] است»* |
| 15 | **هدف این پژوهش بررسی این بود که** | Monotonous teleological phrasing | *«پژوهش حاضر با هدف واکاوی نقادانه [...] سامان یافته است»* |

---

## 3. English Academic Tone: AI Cliches vs. Authentic Academic Substitutions

| # | AI Overused Trope | Disciplinary Issue | Authentic Academic Scholarly Alternative |
| :---: | :--- | :--- | :--- |
| 1 | **delve into / delving into** | Notorious ChatGPT marker | *investigate, examine, scrutinize, probe, explore the nuances of* |
| 2 | **a testament to** | Over-dramatic AI cliché | *evidence of, indicative of, corroborates, substantiates* |
| 3 | **plays a crucial/pivotal role** | Repetitive filler | *is central to, underpins, modulates, significantly mediates* |
| 4 | **multifaceted tapestry / landscape** | Flowery LLM metaphor | *complex framework, multidimensional construct, dynamic matrix* |
| 5 | **moreover / furthermore (at every sentence start)** | Rigid robotic cadence | Vary transition placement: *adverbial clauses, semicolons, "consequently", "specifically"* |
| 6 | **it is important/crucial to note that** | Wordy filler | *Notably, ...* / *Crucially, ...* / direct integration |
| 7 | **underscores / highlights (repetitive)** | Lexical fatigue | *accentuates, elucidates, reinforces, exemplifies, demystifies* |
| 8 | **in conclusion / to sum up** | High-school formulaic | *Taken together, these empirical findings demonstrate that...* |

---

## 4. Academic Integrity & Invariant Preservation Rules

Any academic rewriting engine MUST respect absolute invariants:

1. **APA 7th Edition In-Text Citations**:
   - English: `(Beck et al., 2020)`, `(Smith & Jones, 2018, p. 45)`, `Bandura (1997)`
   - Persian: `(بک و همکاران، ۱۳۹۹)`، `(سلیگمن، ۲۰۰۶)`، `شکوهی‌یکتا و پرند (۱۳۸۷)`
   - **Rule**: Must be masked using unique regex placeholders (e.g. `__CIT_001__`) prior to lexical/syntactic transformation and reinstated verbatim.
2. **Statistical Formulas & Parameter Reporting**:
   - APA formats: `F(1, 58) = 14.25, p < .001, \eta_p^2 = .197`, `t(58) = 3.42, p = .001, d = 0.88`, `M = 24.50, SD = 4.12`
   - **Rule**: Masked using `__STAT_001__` to prevent altering numerical values, degrees of freedom, or mathematical symbols.
3. **Table & Figure Captions**:
   - `جدول ۱. میانگین و انحراف استاندارد...` / `Table 1. Descriptive statistics...`
   - Must remain intact.

---

## 5. Persian Typography & Orthography Standards (نیم‌فاصله)

Authentic Iranian academic publications enforce strict orthographic rules (*فرهنگستان زبان و ادب فارسی* and *ویراستاران*):

1. **Verbal Prefixes**:
   - `می` and `نمی` must be separated from verbs by a zero-width non-joiner (`\u200c` / نیم‌فاصله):
     - `می شود` $\to$ `می‌شود`
     - `نمی توان` $\to$ `نمی‌توان`
2. **Plural Suffixes**:
   - `ها` and `های`:
     - `پژوهش ها` $\to$ `پژوهش‌ها`
     - `متغیر های پژوهش` $\to$ `متغیرهای پژوهش`
3. **Comparative & Superlative Suffixes**:
   - `تر` and `ترین`:
     - `موثر تر` $\to$ `مؤثرتر`
     - `مهم ترین` $\to$ `مهم‌ترین`
4. **Indefinite Enclitics (ی)**:
   - Words ending in silent `ه` take `\u200cای`:
     - `جامعه ای` $\to$ `جامعه‌ای`
     - `نظریه ای` $\to$ `نظریه‌ای`
5. **Punctuation Spacing**:
   - No space before commas, periods, colons, or semicolons; exactly one space after.
   - Quotation marks and parentheses attach to text inside without internal spaces: `(پژوهش)` not `( پژوهش )`.

---

## 6. Syntactic Restructuring & Burstiness Optimization Workflow

```
[Raw Draft Text (Low Burstiness, AI Markers)]
                      │
                      ▼
            [1. Entity Masking]
     Mask APA Citations & Statistical Formulas
                      │
                      ▼
         [2. Metric Diagnostic Scan]
     Compute CV_len, Perplexity, Lexical TTR
     Flag Robotic Cliches with String Offsets
                      │
                      ▼
     [3. Academic Transformation Pass]
  ├── Replace Robotic Cliches with Scholarly Idioms
  ├── Syntactic Burstiness Inversion (Combine/Split)
  ├── Nominalization & Fronted Adverbials
  └── Persian Half-Space (نیم‌فاصله) Enforcement
                      │
                      ▼
           [4. Entity Unmasking]
     Reinsert APA Citations & Exact Statistics
                      │
                      ▼
         [5. Post-Optimization Audit]
     Recompute CV_len (Target >= 0.50)
     Confirm 0% Citation/Stat Corruption
                      │
                      ▼
             [6. Multi-Modal Export]
     Word (.docx), Excel Matrix, PNG & JSON
```
