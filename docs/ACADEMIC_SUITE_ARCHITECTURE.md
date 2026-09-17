# Academic Suite Canonical Architecture Specification

**Document Version:** 2.0.0 (Canonical Architecture)  
**Operative Date:** September 2026 (1405 SH)  
**Status:** Approved Reference Standard  
**Orchestration Paradigm:** Pure Antigravity Native Orchestration (Zero External Workflow Engines)  

---

## 1. Architectural Mandate & Guiding Philosophy

The **Academic Suite** (incorporating the **Digital Saber Professional AI Twin**) is built on a single, uncompromising architectural principle:

> **Antigravity is the sole agent runtime and orchestration engine.**  
> There is no custom Python workflow engine, no external agent dispatcher loop, and no simulated agent communication layer. All agent delegation, nesting, concurrency, and context isolation are provided natively by Google Antigravity. Python and R scripts are strictly deterministic execution tools ("The Hands").

### Key Architectural Tenets:
1. **Zero Standalone Workflow Engines:** Legacy script dispatchers and loop managers (e.g. legacy functions in `digital_saber.py`) are fully deprecated. Multi-agent flows execute exclusively via Antigravity's native `invoke_subagent` and `/teamwork-preview`.
2. **Strict Dichotomy of Brains vs. Hands:** Agents reason, plan, formulate hypotheses, synthesize literature, and audit results ("The Brains"). Python and R scripts perform mathematical computation, statistical modeling, and OpenXML compilation ("The Hands").
3. **Adversarial Critic Architecture:** Content generators (`academic-writer`, `statistical-expert`) never audit their own outputs. Independent validation subagents (`statistical-auditor`, `results-auditor`, `evidence-auditor`, `final-judge`) must independently verify deliverables before stage advancement.
4. **Triad Artifact Invariant:** Every micro-stage and individual hypothesis produces a physical on-disk triad: `.docx` (OpenXML Word), `.md` (Markdown narrative & tables), and `.json` (numerical/audit data).

---

## 2. The Canonical Agent Hierarchy

```text
                           PRIMARY AGENT
                       ACADEMIC ORCHESTRATOR
                          (digital-saber)
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
       RESEARCH              STATISTICS              WRITING
       SUBAGENT               SUBAGENT               SUBAGENT
          │                      │                      │
          ▼                      ▼                      ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  methodology-    │   │  data-curator    │   │  academic-writer │
│     expert       │   │  statistical-    │   │  intervention-   │
│  literature-     │   │     expert       │   │     designer     │
│     expert       │   │  psychometric-   │   │  journal-        │
│  meta-analyst    │   │     expert       │   │     strategist   │
│  qualitative-    │   │                  │   │                  │
│     analyst      │   │                  │   │                  │
└─────────┬────────┘   └─────────┬────────┘   └─────────┬────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                          VALIDATION LAYER
                                 │
               ┌─────────────────┴─────────────────┐
               ▼                                   ▼
      ADVERSARIAL CRITICS                 DEFENSE SIMULATOR
    - statistical-auditor                 - final-judge
    - results-auditor                     - MSAI Anomaly Detector
    - evidence-auditor                    - Committee Simulator
               │                                   │
               └─────────────────┬─────────────────┘
                                 │
                            HOOKS / RULES
               ┌─────────────────┴─────────────────┐
               │  - .agents/hooks.json             │
               │  - transcript_and_rule_guard.py   │
               │  - Constitutional Directives 0–18 │
               │  - .agents/rules/*.md             │
               └───────────────────────────────────┘
```

---

## 3. Tier-by-Tier Specification

### Tier 1: Primary Agent (Academic Orchestrator / `digital-saber`)
- **Persona & Identity:** Digital Twin of Saber Ghaderi ([`.agents/identity/`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/identity/)).
- **Execution Role:** Operates in the main Antigravity conversation context.
- **Responsibilities:**
  - Client engagement, requirement intake, and project scoping.
  - Case-Based Reasoning (CBR) retrieval from historical dissertations (`case_memory_engine.py`).
  - High-stakes decision logging in `.agents/memory/decisions/` (`decision_journal_engine.py`).
  - High-level pipeline decomposition and stage-gate control (Directive 11).
  - Native orchestration of Domain Subagents via `invoke_subagent` and `/teamwork-preview`.
  - Final deliverable sign-off and administrative gatekeeping.

---

### Tier 2: Core Domain Subagents (The Triumvirate)

The Primary Agent delegates to three major domain coordinators, each operating in an isolated context:

#### 1. Research Subagent
- **Domain Scope:** Research epistemology, experimental/quasi-experimental designs, literature mapping, and qualitative analysis.
- **Direct Sub-Specialists Coordinated:** `methodology-expert`, `literature-expert`, `meta-analyst`, `qualitative-analyst`.
- **Primary Deliverables:** Methodology specifications, PICO search frameworks, Callon science maps, qualitative theme codebooks.

#### 2. Statistics Subagent
- **Domain Scope:** Data hygiene, psychometrics, inferential testing, SEM modeling, and statistical simulation.
- **Direct Sub-Specialists Coordinated:** `data-curator`, `statistical-expert`, `psychometric-expert`.
- **Primary Deliverables:** Clean datasets (`data_cleaned.xlsx`), psychometric validation reports, raw statistical tables, `stats_results.json`.

#### 3. Writing Subagent
- **Domain Scope:** Dissertation chapter drafting (Ch 1–5), clinical intervention protocols, journal article packaging, and Persian academic rhetoric.
- **Direct Sub-Specialists Coordinated:** `academic-writer`, `intervention-designer`, `journal-strategist`.
- **Primary Deliverables:** Synchronized triad artifacts (`.docx`, `.md`, `.json`), clinical intervention manuals, blind journal manuscripts.

---

### Tier 3: Specialist Subagents

Specialist subagents are focused cognitive agents equipped with domain guidelines and deterministic execution tools:

| Specialist Agent | Domain Parent | Cognitive Specialization | Primary Deterministic Skills ("The Hands") |
|---|---|---|---|
| **`methodology-expert`** | Research | Experimental designs, sampling power, validity safeguards | `gpower-sample-size-calculator`, `persian-proposal-builder` |
| **`literature-expert`** | Research | Database harvesting, bibliometrics, Chapter 2 synthesis | `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer` |
| **`meta-analyst`** | Research | PRISMA 2020 systematic reviews, Cochrane RoB 2, meta-analysis | `systematic-review-meta-analyst`, `literature-harvester` |
| **`qualitative-analyst`** | Research | Thematic Analysis (Braun & Clarke), Grounded Theory | `qualitative-data-analyst` |
| **`data-curator`** | Statistics | Data hygiene, Little's MCAR, Mahalanobis $D^2$, screening | `statistical-data-analyst`, `psychometric-scale-resolver` |
| **`statistical-expert`** | Statistics | Parametric assumption tree, inferential testing, SEM fit | `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator` |
| **`psychometric-expert`** | Statistics | 4,880-scale resolver, CTT/IRT, CFA, psychometric simulation | `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator` |
| **`academic-writer`** | Writing | Chapter drafting, Saber 5-part epistemic paragraph structure | `persian-thesis-builder`, `persian-discussion-builder`, `academic-article-writer`, `ai-academic-tone-polisher` |
| **`intervention-designer`**| Writing | Standardized psychological protocols (ACT, CBT, Schema) | `psychological-intervention-protocol-builder` |
| **`journal-strategist`** | Writing | Manuscript extraction, journal selection, rebuttal tables | `academic-article-writer`, `journal-submission-assistant`, `ai-academic-tone-polisher` |

---

### Tier 4: Validation Layer (Adversarial Critics & Defense Committee)

Outputs from Tier 3 specialists MUST pass through the Validation Layer before any stage is marked complete:

```text
Specialist Output Draft
          │
          ├──> statistical-auditor ──> MSAI Anomaly Detection (Effect size, SD, df)
          │
          ├──> results-auditor     ──> APA 7 & Typography Audit (Leading zero ۰.۰۰۱, OMML)
          │
          ├──> evidence-auditor    ──> In-Text Citation Concordance & Irandoc Risk (< 20%)
          │
          └──> final-judge         ──> Mock Viva Voce Oral Defense Cross-Examination
```

1. **`statistical-auditor`:** Evaluates the Multi-Signal Anomaly Index (MSAI) on all calculated test statistics, checks degrees of freedom concordance ($df_{\text{error}} = N - k - 1$), verifies absence of variance deflation ($SD < 0.10 \times Range$), and flags synthetic anomalies.
2. **`results-auditor`:** Enforces APA 7th Edition rules: mandatory Persian leading zero preservation (`۰.۰۰۱`, `۰.۰۵`), elimination of $p = .000$ ($p < ۰.۰۰۱$), 3-line table borders, Latin symbol italicization (*M, SD, t, F, p*), and preservation of native Word OMML math equations (`<m:oMath>`).
3. **`evidence-auditor`:** Cross-checks all in-text citations against the physical reference library, verifies external claims via CrossRef/PubMed API, audits Irandoc/SamimNoor similarity risk (< 20%), and removes robotic AI clichés.
4. **`final-judge`:** Simulates a 5-examiner academic defense committee (The Methodologist, The Statistician, The Epistemic Theorist, The Pedant, The Clinical Pragmatist), cross-examining findings and generating the Viva Voce Defense Card.

---

### Tier 5: Hooks & Rules Layer (Constitutional Governance)

The foundation of the architecture is mechanically enforced by Antigravity lifecycle hooks:

```text
.agents/hooks.json
  │
  ├── PreToolUse    ──> transcript_and_rule_guard.py --event PreToolUse
  │                     Enforces Directive 6 (English ASCII filenames)
  │                     Blocks unauthorized write/execute patterns
  │
  ├── PostToolUse   ──> transcript_and_rule_guard.py --event PostToolUse
  │                     Verifies physical generation of stage artifacts
  │
  ├── PreInvocation ──> transcript_and_rule_guard.py --event PreInvocation
  │                     Injects active constitutional reminders
  │
  └── Stop          ──> transcript_and_rule_guard.py --event Stop
                        Enforces Directive 0 (Binary Honesty Protocol)
                        Enforces Directive 12.1 (Multi-agent truthfulness)
                        Enforces Directive 18 (skill_size_guard.py context ceiling)
```

#### Rule Base:
- **Global Directives:** [`AGENTS.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/AGENTS.md) (Directives 0 through 18).
- **Domain Rules:** [`.agents/rules/`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/rules/):
  - `radical_honesty_and_pipeline_enforcement.md`
  - `file_naming_rules.md`
  - `git_lifecycle_rules.md`
  - `persian_font_rules.md`
  - `digital_twin_rules.md`
  - `chapter4_hypothesis_and_sem_structure_rules.md`
- **Plugin Governance:** [`.agents/plugins/academic-suite/rules/AGENTS.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/plugins/academic-suite/rules/AGENTS.md).

---

## 4. Antigravity Native Orchestration Mechanisms

The Academic Suite leverages the full spectrum of Google Antigravity's native orchestration capabilities:

### 1. Isolated Contexts & Concurrency
- When `invoke_subagent` is called, Antigravity creates an independent subagent conversation context. This prevents context exhaustion and isolates complex statistical logs, literature search dumps, and drafting runs from the Lead Orchestrator's prompt budget.
- Antigravity supports concurrent subagent invocation in a single tool call, enabling parallel literature harvesting across PubMed and CrossRef, or parallel auditing by `statistical-auditor` and `results-auditor`.

### 2. Multi-Tier Nesting
- The Lead Orchestrator (`digital-saber`) invokes Domain Subagents (e.g. `Statistics Subagent`), which in turn invoke Specialist Subagents (e.g. `data-curator`, `statistical-expert`).
- Domain Subagents pass structured specifications (`spec.json`, `data_path`) down to specialists and aggregate verified artifact paths back to the Orchestrator.

### 3. Agent Communication
- Subagents report results asynchronously to their caller.
- When cross-agent consultation is needed (e.g., `academic-writer` asking `statistical-expert` to clarify an interaction term), the native `send_message` tool facilitates inter-agent communication.

### 4. Large Project Scaling via `/teamwork-preview`
- For massive, multi-week deliverables (such as full 5-chapter doctoral dissertations or comprehensive systematic review packages), the Primary Agent utilizes the `/teamwork-preview` slash command to coordinate persistent, specialized agent teams with synchronized artifact handoffs.

### 5. Deterministic Execution via Terminal Tools
- Subagents execute mathematical models, G*Power calculations, data cleaning, and OpenXML compilation via `run_command`. Under **Directive 2**, agents never perform statistical calculations in their LLM memory.

---

## 5. Modern Skill Distribution Across the Canonical Hierarchy

The 27 modern production skills map directly into the canonical hierarchy:

```text
ACADEMIC ORCHESTRATOR
  ├── academic-suite-orchestrator
  ├── digital-twin-academic-consultant
  └── thesis-integrity-auditor

RESEARCH SUBAGENT & SPECIALISTS
  ├── methodology-expert:
  │     ├── gpower-sample-size-calculator
  │     └── persian-proposal-builder
  ├── literature-expert:
  │     ├── literature-harvester
  │     ├── persian-literature-review-builder
  │     ├── bibliometric-network-analyst
  │     └── citation-network-visualizer
  ├── meta-analyst:
  │     ├── systematic-review-meta-analyst
  │     └── literature-harvester
  └── qualitative-analyst:
        └── qualitative-data-analyst

STATISTICS SUBAGENT & SPECIALISTS
  ├── data-curator:
  │     ├── statistical-data-analyst (data_curator_engine.py)
  │     └── psychometric-scale-resolver
  ├── statistical-expert:
  │     ├── statistical-data-analyst (psychology_stats.py, generate_apa_docx.py)
  │     ├── psychometric-scale-resolver
  │     └── psychometric-scale-validator
  └── psychometric-expert:
        ├── psychometric-scale-resolver
        ├── psychometric-scale-validator
        └── psychometric-data-simulator

WRITING SUBAGENT & SPECIALISTS
  ├── academic-writer:
  │     ├── persian-thesis-builder
  │     ├── persian-discussion-builder
  │     ├── academic-article-writer
  │     └── ai-academic-tone-polisher
  ├── intervention-designer:
  │     └── psychological-intervention-protocol-builder
  └── journal-strategist:
        ├── academic-article-writer
        ├── journal-submission-assistant
        └── ai-academic-tone-polisher

VALIDATION LAYER
  ├── statistical-auditor:
  │     └── thesis-integrity-auditor (MSAI Anomaly Detection)
  ├── results-auditor:
  │     └── thesis-integrity-auditor (APA 7 & OMML Typography)
  ├── evidence-auditor:
  │     ├── academic-reference-extractor
  │     └── irandoc-plagiarism-reducer
  └── final-judge:
        ├── thesis-integrity-auditor
        ├── persian-defense-presentation-builder
        └── persian-thesis-revision-assistant
```

---

## 6. Execution Lifecycle: The Triad Stage-Gate Flow

Every micro-stage in the Academic Suite proceeds through the following deterministic cycle:

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. PRE-FLIGHT GATE (Directive 1)                              │
│    view_file SKILL.md -> Emit Pre-Flight Pipeline Declaration │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. DETERMINISTIC COMPUTATION ("The Hands", Directive 2)       │
│    run_command python3 .agents/skills/.../scripts/<script.py> │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. TRIAD ARTIFACT GENERATION (Directive 3)                    │
│    Physical creation of: [stage].docx + [stage].md + [stage].json
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. ADVERSARIAL VALIDATION (Tier 4 Critics)                    │
│    statistical-auditor (MSAI) / results-auditor / evidence-auditor
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│ 5. INTERACTIVE STAGE-GATE PAUSE (Directive 11)                │
│    Emit Stage Completion Report -> HALT for User Confirmation │
└───────────────────────────────────────────────────────────────┘
```

This ensures complete visibility, zero unverified hallucinations, and absolute compliance with institutional academic standards.
