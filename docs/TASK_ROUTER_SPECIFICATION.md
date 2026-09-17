# Academic Task Router Specification: Intelligent Capability Routing

This specification establishes the deterministic **Academic Task Router Engine** within the Academic Suite. The Task Router inspects user requests, recognizes academic research intent, and dynamically configures the minimum sufficient, strictly ordered pipeline of specialist subagents and Skills—eliminating blind agent spawning, context bloat, and redundant overhead.

---

## 1. Executive Summary & Core Architectural Principle

In naive multi-agent systems, an orchestrator often spawns every available agent regardless of the user's actual requirements, leading to excessive token consumption, coordination latency, and instruction drift.

In the Academic Suite:
> **"The router chooses capabilities, not blindly invokes every agent."**

When presented with a prompt:
1. The **Academic Orchestrator** analyzes the prompt using `scripts/academic_task_router.py`.
2. The router identifies the exact required capabilities (e.g. `DATA`, `STATISTICS`, `WRITING`).
3. The router generates an ordered, dependency-verified execution pipeline.
4. Only the necessary specialist subagents (`data-agent`, `statistics-agent`, `writing-agent`, `research-agent`, `validation-agent`) are invoked via Antigravity's native `invoke_subagent`.
5. Unneeded capabilities and agents are completely pruned.

---

## 2. Canonical Exemplar Mappings

The router is tuned against five canonical academic research archetypes:

```
┌──────────────────────────────────────┬───────────────────────────────────────────────────────────┐
│ User Prompt                          │ Minimal Sufficient Capability Pipeline                    │
├──────────────────────────────────────┼───────────────────────────────────────────────────────────┤
│ "Analyze this dataset"               │ DATA ──► STATISTICS                                       │
│ "Write Chapter 4"                    │ STATISTICS ──► WRITING ──► VALIDATION                     │
│ "Find research gaps"                 │ RESEARCH ──► METHODOLOGY                                  │
│ "Perform CFA and SEM"                │ DATA ──► STATISTICS ──► VALIDATION                        │
│ "Analyze these network data"         │ DATA ──► NETWORK-ANALYSIS ──► STATISTICS ──► VALIDATION   │
└──────────────────────────────────────┴───────────────────────────────────────────────────────────┘
```

### Detailed Canonical Breakdown:
1. **"Analyze this dataset"**
   - **Formula**: `DATA + STATISTICS`
   - **Rationale**: Requires dataset ingestion, reverse-coding, missing value screening (`data-agent`), followed by sample descriptives, reliability, and inferential tests (`statistics-agent`). Does not trigger writing or formal defense validation unless requested.
2. **"Write Chapter 4"**
   - **Formula**: `STATISTICS + WRITING + VALIDATION`
   - **Rationale**: Drafting findings requires certified statistical models (`statistics-agent`), scholarly APA 7 prose drafting (`writing-agent`), and mandatory adversarial verification of degrees of freedom and APA tables (`validation-agent`).
3. **"Find research gaps"**
   - **Formula**: `RESEARCH + METHODOLOGY`
   - **Rationale**: Investigates existing empirical literature across PubMed/CrossRef (`research-agent`), identifies theoretical contradictions, and formulates rigorous research questions and methodological safeguards (`research-agent`).
4. **"Perform CFA and SEM"**
   - **Formula**: `DATA + STATISTICS + VALIDATION`
   - **Rationale**: Structural equation modeling requires verified clean indicator data (`data-agent`), latent factor measurement and structural path estimation (`statistics-agent`), and independent fit index verification against Hu & Bentler cutoffs (`validation-agent`).
5. **"Analyze these network data"**
   - **Formula**: `DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION`
   - **Rationale**: Requires bibliographic/relational data curation (`data-agent`), science mapping, Callon centrality, and co-occurrence graphs (`statistics-agent` via `network-analysis`), inferential centrality statistics, and data-graph consistency auditing (`validation-agent`).

---

## 3. Strict Pipeline Ordering Invariant

Regardless of the order words appear in the user prompt, capabilities **MUST** execute strictly according to their ontological dependency sequence:

```
RESEARCH ──► METHODOLOGY ──► DATA ──► NETWORK-ANALYSIS ──► STATISTICS ──► WRITING ──► VALIDATION
```

### Ordering Rationale:
- **`RESEARCH`** must precede **`METHODOLOGY`** so questions and theoretical frameworks inform design.
- **`METHODOLOGY`** must precede **`DATA`** to define instruments, scales, and sampling parameters.
- **`DATA`** must precede **`STATISTICS`** and **`NETWORK-ANALYSIS`** because calculations cannot operate on uncleaned, unverified data.
- **`NETWORK-ANALYSIS`** feeds relational metrics and matrix structures into **`STATISTICS`**.
- **`STATISTICS`** must precede **`WRITING`** because scholarly narrative must describe verified, deterministic empirical output, never hallucinated numbers.
- **`WRITING`** must precede **`VALIDATION`** because institutional documents, tables, and narrative claims must be audited for df and numerical consistency.

---

## 4. Capability Registry & Artifact Contracts

Every capability maps directly to a specialist subagent, a primary Skill, and explicit input/output artifacts in `academic-state/`:

| Capability | Assigned Subagent | Primary Skill | Input Artifact | Output Checkpoint Artifact |
| :--- | :--- | :--- | :--- | :--- |
| **`RESEARCH`** | `research-agent` | `literature-review` | `academic-state/requirements.json` | `academic-state/requirements.json` |
| **`METHODOLOGY`** | `research-agent` | `methodology-review` | `academic-state/requirements.json` | `academic-state/analysis_plan.json` |
| **`DATA`** | `data-agent` | `data-cleaning` | `projects/*/01_raw_inputs/*` | `academic-state/data/data_quality.json` |
| **`NETWORK-ANALYSIS`** | `statistics-agent` | `network-analysis` | `academic-state/data/data_dictionary.json` | `academic-state/analysis/network_results.json` |
| **`STATISTICS`** | `statistics-agent` | `sem` | `academic-state/data/data_quality.json` | `academic-state/analysis/sem.json` |
| **`WRITING`** | `writing-agent` | `chapter-4-writing` | `academic-state/analysis/sem.json` | `academic-state/outputs/Chapter_4_Results.docx` |
| **`VALIDATION`** | `validation-agent` | `thesis-integrity-auditor` | `academic-state/outputs/*` | `academic-state/validation/statistical_validation.json` |

---

## 5. Intent Recognition Grammar & Contextual Rules

The router employs a multi-tiered recognition grammar:

1. **Macro Pattern Matching**: High-confidence regular expressions for standardized academic workflows (e.g. `\b(?:write|draft|generate)\s+chapter\s*4\b`).
2. **Domain Keyword Heuristics**: If no macro archetype triggers, individual keyword clusters (`literature`, `g*power`, `reverse code`, `sem`, `ancova`, `table`, `audit`) are extracted.
3. **Contextual Invariant Complements**:
   - *Invariant A (Writing Integrity)*: Any request to draft Chapter 4, results, or findings automatically includes `STATISTICS` and `VALIDATION` to ensure findings are grounded and audited.
   - *Invariant B (Modeling Integrity)*: Any complex modeling request (CFA, SEM) formulated from scratch automatically includes `DATA` curation and independent `VALIDATION`.
4. **Fallback Safety**: If no recognizable intent is detected, defaults to safe baseline data screening and descriptives (`DATA + STATISTICS`).

---

## 6. Deterministic CLI Tooling ("The Hands")

In compliance with **Directive 12.1 (Sole Orchestrator Mandate)**, all pattern matching and pipeline construction logic is implemented as a deterministic Python tool in `scripts/academic_task_router.py`:

```bash
# 1. Generate JSON pipeline specification
python3 scripts/academic_task_router.py route "Perform CFA and SEM"

# 2. Print formatted human-readable summary
python3 scripts/academic_task_router.py explain "Write Chapter 4"

# 3. List canonical archetypes
python3 scripts/academic_task_router.py list-patterns
```

### Sample Output (`route`):
```json
{
  "task_prompt": "Perform CFA and SEM",
  "capabilities_formula": "DATA + STATISTICS + VALIDATION",
  "capabilities": [
    "DATA",
    "STATISTICS",
    "VALIDATION"
  ],
  "total_steps": 3,
  "pipeline": [
    {
      "step": 1,
      "capability": "DATA",
      "agent": "data-agent",
      "skill": "data-cleaning",
      "skill_path": ".agents/skills/data-cleaning/SKILL.md",
      "description": "Raw dataset ingestion, scale reverse-coding, missing value screening, and quality auditing",
      "input_artifact": "projects/*/01_raw_inputs/*",
      "output_artifact": "academic-state/data/data_quality.json"
    },
    {
      "step": 2,
      "capability": "STATISTICS",
      "agent": "statistics-agent",
      "skill": "sem",
      "skill_path": ".agents/skills/sem/SKILL.md",
      "description": "Deterministic inferential modeling (SEM, CFA, ANCOVA, regression, mediation, reliability)",
      "input_artifact": "academic-state/data/data_quality.json",
      "output_artifact": "academic-state/analysis/sem.json"
    },
    {
      "step": 3,
      "capability": "VALIDATION",
      "agent": "validation-agent",
      "skill": "thesis-integrity-auditor",
      "skill_path": ".agents/skills/thesis-integrity-auditor/SKILL.md",
      "description": "Independent adversarial verification of df, numerical consistency, and APA reporting rules",
      "input_artifact": "academic-state/outputs/*",
      "output_artifact": "academic-state/validation/statistical_validation.json"
    }
  ],
  "orchestration_directive": "The Academic Orchestrator will execute 3 sequential stages: data-agent ──► statistics-agent ──► validation-agent. Unneeded agents are pruned to preserve context bandwidth."
}
```

---

## 7. Context Isolation & Orchestrator Integration

When the **Academic Orchestrator** processes user tasks:
1. It queries `scripts/academic_task_router.py route "<user prompt>"`.
2. It parses the resulting JSON pipeline.
3. For each step in the pipeline:
   - It issues a lean **Contractual Delegation Envelope** via `invoke_subagent` exclusively to the assigned agent.
   - The subagent calls `view_file` on its bound `SKILL.md` (Directive 1).
   - The subagent executes deterministic scripts and deposits triad artifacts (`.docx`, `.md`, `.json`) into `academic-state/outputs/` (Directive 3).
   - The subagent returns a concise handoff envelope with artifact pointers.
4. At the conclusion of the stage, the Orchestrator emits the **Stage Completion Report** and pauses for user confirmation (Directive 11).
