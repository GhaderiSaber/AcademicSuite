# Three-Tier Execution Routing Guide: Custom Subagents vs. /boost vs. /teamwork-preview

This guide codifies the **Three-Tier Execution Architecture** for the Academic Suite, delineating when to orchestrate through Custom Subagents, when to activate `/boost`, and when to leverage `/teamwork-preview`.

---

## 1. Architectural Distinction & Philosophy

Antigravity provides distinct execution modes optimized for different cognitive demands and project scales:

```
                            Academic Suite Task
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
      Tier 1                      Tier 2                      Tier 3
  Ordinary Tasks           Hard Reasoning Dilemmas      Huge Multi-Study Theses
  (Micro-stages, triads,   (Non-converging SEM,         (20-chapter monographs,
  hypothesis testing)      mathematical proofs)         thousands of files)
         │                           │                           │
         ▼                           ▼                           ▼
  Custom Subagents                 /boost                /teamwork-preview
  (invoke_subagent)        (Multi-tier reasoning)       (Autonomous Teamwork)
```

Selecting the correct execution tier prevents two opposing failure modes:
1. **Under-Engineering**: Attempting to tackle a massive 20-chapter monograph overhaul or non-identified SEM derivation in a single linear subagent prompt.
2. **Over-Engineering**: Spawning a heavy multi-agent team or deep reasoning search for simple descriptive statistics or APA table formatting.

---

## 2. The Three-Tier Decision Matrix

| Metric / Dimension | Tier 1: Custom Subagents | Tier 2: `/boost` | Tier 3: `/teamwork-preview` |
| :--- | :--- | :--- | :--- |
| **Primary Conductor** | `academic-orchestrator` | Antigravity Multi-Tier Boost Engine | Antigravity Teamwork Runtime |
| **Target Scope** | Bounded research micro-stages | Isolated, non-linear reasoning dilemma | Massive multi-chapter project overhaul |
| **Document Scope** | 1 stage (e.g. 1 section / 1 hypothesis) | 1 complex model / theoretical derivation | Full monograph (10–20 chapters) |
| **File Count** | 1 to 10 files | 1 to 5 files | 100 to 1,000+ files |
| **Task Horizon** | Turn-by-turn interactive stage-gates | Deep multi-step thinking turn | Long-running background execution |
| **Reasoning Demand** | Standard academic & statistical | Deep strategic & adversarial verification | Distributed project coordination |
| **Artifact Contract** | Triad (`.docx`, `.md`, `.json`) in `academic-state/` | Mathematical derivation / proof / solution | Full repository directory trees |

---

## 3. Tier 1: Custom Subagents (`invoke_subagent`)

### When to Use
Standard, day-to-day operation of the Academic Suite. Any bounded empirical or methodological task that follows a known linear or stage-gated procedure.

### Typical Use Cases
- Ingesting, reverse-coding, and screening a raw dataset (`data-agent`).
- Computing sample descriptive statistics and frequency distributions (`statistics-agent`).
- Evaluating scale reliability ($\alpha, \omega$) and testing parametric assumptions (`statistics-agent`).
- Testing Hypothesis 1 via ANCOVA, regression, or SEM (`statistics-agent`).
- Drafting the scholarly findings narrative for Hypothesis 1 (`writing-agent`).
- Independent forensic audit of statistical degrees of freedom and APA tables (`validation-agent`).

### Operational Pattern
1. **Academic Orchestrator** checks prerequisites via `orchestrator_dependency_resolver.py`.
2. Emits **Contractual Delegation Envelope** via `invoke_subagent`.
3. Subagent reads input from `academic-state/`, executes deterministic Python/R script ("The Hands"), and writes triad output to `academic-state/outputs/`.
4. Subagent returns concise JSON pointer to Orchestrator.
5. Orchestrator triggers `validation-agent`, halts at stage gate, and requests user confirmation (Directive 11).

---

## 4. Tier 2: Hard Isolated Reasoning Dilemmas (`/boost`)

### When to Use
When the research problem is mathematically, psychometrically, or epistemically intractable under standard single-shot reasoning, requiring exploratory problem-solving, structural identification proofs, or alternative model specifications.

### Typical Use Cases
- **Empirical Underidentification**: An SEM model fails to converge ($df \le 0$, singular information matrix, or feedback loops in non-recursive models).
- **High-Order Moderated Mediation**: Complex 3-way interaction probing with non-normal indirect bootstrapping dilemmas.
- **Novel Mathematical Derivation**: Formulating customized IRT item-characteristic curves or propensity-score weighting proofs.
- **Severe Multicollinearity Dilemma**: Resolving perfect or near-perfect collinearity ($VIF > 10$) without sacrificing theoretical constructs.
- **Heckman Selection Correction Dilemma**: Designing instrumental exclusion restrictions for non-random sample attrition.

### Operational Pattern
- When the Orchestrator diagnoses a non-converging or empirically underidentified problem, it outputs:
  > "This modeling problem involves non-recursive structural feedback loops and empirical underidentification. I recommend activating `/boost` to engage Antigravity's multi-tier deep reasoning architecture."
- User types `/boost`.
- Antigravity deploys deep multi-perspective reasoning, evaluates structural rank and order conditions, derives identification equations, and produces verified mathematical solutions.

---

## 5. Tier 3: Huge Long-Running Projects (`/teamwork-preview`)

### When to Use
When the project scope spans whole multi-chapter monographs, multi-dataset longitudinal projects, or repository-wide thesis overhauls that would saturate single-agent contexts or require long-running multi-hour autonomous coordination.

### Typical Use Cases
- **20-Chapter Monograph Overhaul**: Restructuring, reconciling, and reformatting a 500-page institutional thesis with cross-chapter citations.
- **Multi-Wave Longitudinal Dataset Restructuring**: Managing 5 waves of panel data with thousands of raw interview transcripts and survey spreadsheets.
- **Systematic Review & Meta-Analysis PRISMA Pipeline**: Screening 5,000 harvested literature records across PubMed, Scopus, and SID, extracting effect sizes, and risk-of-bias coding.
- **Complete Institutional Dissertation Turnkey Pipeline**: Autonomous coordination from Proposal to Final Defense Slides across 20+ specialized steps.

### Operational Pattern
- When the user requests a multi-chapter or repository-wide overhaul, the Orchestrator outputs:
  > "This task involves a comprehensive 20-chapter thesis restructuring across thousands of source files. I recommend activating `/teamwork-preview` to launch an autonomous multi-agent team with persistent task graphs."
- User types `/teamwork-preview`.
- Antigravity Teamwork launches persistent task trees, coordinates specialized agents concurrently, monitors dependencies, and performs independent background verification.

---

## 6. Deterministic Task Routing CLI

The Orchestrator provides a deterministic command in `scripts/orchestrator_dependency_resolver.py`:

```bash
python3 scripts/orchestrator_dependency_resolver.py route-task \
  --description "<task description>" \
  [--chapter-count <int>] \
  [--file-count <int>]
```

### Exemplar CLI Outputs

#### Tier 1 Example
```bash
python3 scripts/orchestrator_dependency_resolver.py route-task \
  --description "Run ANCOVA on 60 ICU nurses to test hypothesis 1"
```
```json
{
  "tier": "tier_1_custom_subagents",
  "recommended_mechanism": "invoke_subagent",
  "primary_conductor": "academic-orchestrator",
  "assigned_subagent": "statistics-agent"
}
```

#### Tier 2 Example
```bash
python3 scripts/orchestrator_dependency_resolver.py route-task \
  --description "Derive identification equations for non-converging non-recursive SEM with feedback loops"
```
```json
{
  "tier": "tier_2_boost",
  "recommended_mechanism": "/boost",
  "slash_command": "/boost",
  "primary_conductor": "Antigravity Multi-Tier Boost Engine"
}
```

#### Tier 3 Example
```bash
python3 scripts/orchestrator_dependency_resolver.py route-task \
  --description "Restructure 20-chapter monograph with thousands of source files"
```
```json
{
  "tier": "tier_3_teamwork",
  "recommended_mechanism": "/teamwork-preview",
  "slash_command": "/teamwork-preview",
  "primary_conductor": "Antigravity Teamwork Multi-Agent System"
}
```
