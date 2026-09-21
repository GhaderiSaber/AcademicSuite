---
name: academic-adaptive-context
description: "Retrieve targeted active behavioral context (lessons, anti-patterns, exemplars, calibrated defaults) relevant to the current task from the persistent learning store without dumping irrelevant records."
---

# Academic Adaptive Context Skill (بازیابی بافت رفتاری تطبیقی)

Connects the repository's persistent knowledge store directly to live agent execution:
$$\text{PERSISTENT KNOWLEDGE} \longrightarrow \text{ADAPTIVE AGENT CONTEXT} \longrightarrow \text{EXECUTABLE TASK}$$

Provides agents with a compact, high-signal behavioral briefing containing active lessons, anti-patterns to avoid, gold-standard exemplars to emulate, and known failure modes before commencing any research, statistical, or drafting task.

---

---


## 1. When to Use (Activation Criteria)

Activate this skill **immediately prior to starting execution** on any task involving:
1. **Inferential Statistical Modeling**: Before running ANCOVA, regression, bootstrap mediation, or SEM, to retrieve failure modes (e.g. non-positive definite matrices, slope violations) and calibrated CLI defaults.
2. **Data Cleaning & Psychometrics**: Before item aggregation, reverse-coding, or scale validation, to retrieve known questionnaire pitfalls and imputation invariants.
3. **Academic Writing & Reporting**: Before drafting Chapter 4 findings, Chapter 5 discussions, or proposals, to retrieve formatting mandates (leading zero rules, APA 7 borders) and prohibited cliches.
4. **Adversarial Auditing & Review**: During `validation-agent`, `statistical-auditor`, or `academic-challenger` checks, to retrieve cataloged anti-patterns and previous examiner critique patterns.

---

## 2. When NOT to Use (Exclusion Criteria)

Do **NOT** activate this skill for:
1. Pure file manipulation or git commands (e.g. committing, moving files, viewing directory trees).
2. Trivial factual questions that do not perform academic, statistical, or drafting execution.
3. Overriding explicit user instructions with outdated project-specific preferences.

---

## 3. The Deterministic Execution Boundary Pipeline (Phase 28)

Under Phase 28, context retrieval is **mechanically guaranteed at the execution boundary** via the `PreInvocation` lifecycle hook (`.agents/hooks/learning_hooks.py`) and subagent dispatch boundary (`scripts/academic_adaptive_context_boundary.py`).

**Zero Voluntary Retrieval Rule**:
Agents no longer need to "remember" to execute manual CLI retrieval. Whenever an academic turn or subagent delegation begins, the system deterministically executes:

```
Academic task begins
       ↓
context retrieval (Two-Stage Engine)
       ↓
Stage 1: Hard Filtering (capability, domain, skill, task, failure type, scope)
       ↓
Stage 2: Semantic Ranking (relevance, context similarity, evidence, recency, confidence, contradiction)
       ↓
relevant lessons
       ↓
known pitfalls
       ↓
applicable methodology rules
       ↓
agent execution
```

### The Two-Stage Knowledge Retrieval Engine (Phase 29)
To prevent semantic search from retrieving an academically inappropriate lesson merely because vocabulary looks similar (e.g., qualitative thematic coding retrieved for quantitative SEM), retrieval executes in two strict stages:

1. **Stage 1: Hard Filtering (Fail-Closed Structural Boundary Gate)**:
   - **`capability`**: Canonical capability matching; incompatible capabilities are pruned.
   - **`domain`**: Enforces quantitative vs qualitative vs writing vs methodology domain isolation.
   - **`skill`**: Matches `target_skill`, `related_skills`, or `applicability.target_skills`.
   - **`task`**: Enforces task category compatibility.
   - **`failure_type`**: Filters anti-patterns and defect signatures.
   - **`scope`**: Enforces ADR-014 scope containment (project rules never leak to other projects).
   - Any candidate failing a structural boundary is dropped immediately with documented rejection rationale.

2. **Stage 2: Semantic Ranking (Multi-Factor Scholarly Scoring)**:
   - Evaluates only survivors of Stage 1 across 6 weighted factors:
     $$\text{Final Score} = 0.25 \cdot \text{relevance} + 0.25 \cdot \text{similarity} + 0.15 \cdot \text{evidence} + 0.10 \cdot \text{recency} + 0.25 \cdot \text{confidence} - P_{\text{ctd}}$$
   - **`relevance`**: Deterministic metadata, tag matches, and validated status weighting.
   - **`context_similarity`**: Lexical and semantic token overlap with statistical keyword boosts.
   - **`evidence_strength`**: Empirical backing and benchmark fidelity from Phase 26.
   - **`recency`**: Temporal decay relative to calendar anchor (2026-09-19).
   - **`confidence`**: Evidence-derived confidence score ($0.01 \le \text{confidence} \le 0.99$).
   - **`contradiction`**: Penalty deductions for active/unresolved conflicts under Phase 27.


### Dynamic Context Token Budgeting (Phase 41)
To prevent context bloat, eliminate rule interference, and respect agent context budgets, context retrieval enforces **Dynamic Context Token Budgeting**:
- **Turn Pre-Flight Default Budget**: `800 tokens` (comprehensive guidance without context dilution).
- **Subagent Dispatch Default Budget**: `500 tokens` (leaner context protecting subagent focus).
- **Priority-Weighted Knapsack Allocation**:
  $$\text{Value Density} = \frac{\text{PriorityWeight} \times \text{Score}}{\text{Estimated Tokens}}$$
  - **Tier 1 (1.5x)**: Known Pitfalls & Anti-Patterns (safety floor: top pitfall always preserved).
  - **Tier 2 (1.4x)**: Calibrated Defaults (high leverage, tiny token footprint).
  - **Tier 3 (1.2x)**: Relevant Active Lessons (instructional mandates).
  - **Tier 4 (1.0x)**: Methodology Rules & Contradictions (boundary conditions).
  - **Tier 5 (0.8x)**: Gold-Standard Exemplars (included only if $\ge 150$ tokens remain).
- **Dual Compression Modes**:
  - `STANDARD` ($\ge 500$ tokens): Full mandates, generalizations, remedies, and exemplars.
  - `COMPACT` ($< 500$ tokens): Lean single-line mandates, compact anti-patterns, zero exemplars.
- **Budget Badge & Telemetry**: Header displays `[Budget: ~used/max tokens (%)]` with audit metrics in `budget_telemetry`.

### Execution Boundary Retrieval Flow:
1. **Turn Execution Boundary (`PreInvocation` Hook)**:
   - Intercepts turn initiation before LLM reasoning or tool calls.
   - Automatically maps incoming user intent/prompt to target capability, domain, and primary agent.
   - Queries `AcademicKnowledgeManager.retrieve_pre_task_context()` with 800-token budget and injects the briefing directly into the agent's ephemeral context.
2. **Delegation Boundary (`PreToolUse` & Task Router)**:
   - Enriches dispatched subagents with role-specific boundary context budgeted to 500 tokens.
3. **Manual / CLI Diagnostic Inspection ("The Hands")**:
   - For debugging, testing, or offline verification, the standalone CLI tool remains available:
   ```bash
   python3 .agents/skills/academic-adaptive-context/scripts/retrieve_adaptive_context.py \
     --capability <capability> \
     --task <task_type> \
     --agent <agent_name> \
     --project-id <project_id> \
     --max-tokens 800 \
     --format markdown
   ```

### Step 3: Parse & Respect Applicability and Exclusion Conditions
Examine the returned briefing:
- Verify that every lesson's `applicability_conditions` match the current dataset and study design (e.g., sample size criteria, experimental design).
- Check `exclusions`: If the current study meets an exclusion condition (e.g. large sample asymptotic normality overriding formal tests), **do not apply the lesson**.

### Step 4: Screen for Known Anti-Patterns & Defect Traps
Inspect the `⚠️ Critical Anti-Patterns to Avoid` section:
- Verify that the planned analysis or narrative does not implement any listed defective pattern (e.g. median split of continuous moderators, reporting $p = .000$, omitting Persian leading zeros).
- Adopt the specified `Approved Remedy`.

### Step 5: Adopt Calibrated Defaults & Emulate Exemplars
- Inspect `🎯 Calibrated Parameter Defaults`: Use learned CLI flags (e.g. `--bootstrap 5000 --estimator MLR`) to maximize first-pass validation success.
- Review `🏆 Verified Gold-Standard Exemplars` as concrete benchmarks for output structure.

---

## 4. Input & Output Contract

### Input Parameters (CLI):
- `--capability`: Canonical capability key (`mediation`, `SEM`, `psychometrics`, etc.).
- `--task`: Specific task identifier (`bootstrap_mediation`, `homogeneity_of_slopes`, `chapter_4_table`).
- `--agent`: Agent role executing the task (`statistics-agent`, `academic-writer`, etc.).
- `--project-id`: Active research project ID to enforce scope isolation.
- `--format`: `markdown` (default for prompt uptake) or `json` (for programmatic parsing).

### Output Briefing Contract:
A compact markdown block (typically 15–35 lines) structured as:
```markdown
### 🧠 Active Learned Behavioral Context (<CAPABILITY>)
- **Target Capability**: `<cap>` | **Task**: `<task>` | **Agent**: `<agent>` | **Project Scope**: `<proj>`

#### ⚠️ Critical Anti-Patterns to Avoid:
- **[AP-ID] Avoid**: <defective pattern>
  *Approved Remedy*: <corrective remedy>

#### 💡 Active Learned Lessons:
- **[LSN-ID] Mandate**: <desired behavior>
  *Generalization*: <rule>
  *Rationale*: <methodological justification>

#### 🏆 Verified Gold-Standard Exemplars to Emulate:
- **[EXM-ID] (<task_type>)**: <why exemplary>

#### 🎯 Calibrated Parameter Defaults & Known Operational Bounds:
- **Learned Parameter Defaults**: `<json defaults>`
- **Historical Telemetry**: N runs | N passed | N failed.
```

---

## 5. Scope Safeguards & Quarantine Rules

1. **Quarantine of Local Nuances**:
   - Lessons marked with `scope: project` or `scope: global-in-project` are strictly quarantined to queries matching their specific `--project-id`.
   - If `--project-id` is omitted or does not match, local lessons are **filtered out** to prevent leakage.
2. **Promoted Invariants Only**:
   - Only lessons with `scope: cross-project` or `scope: domain` are made available across multiple research projects.
3. **Contradiction Transparency**:
   - When competing paradigms exist (e.g. Baron & Kenny vs Preacher & Hayes bootstrap), the briefing surfaces the approved approach alongside the rejection rationale for the superseded method.

---

## 6. Proactive Human Mentorship & Direct Ingestion (Phase 42)

In addition to reactive, post-failure learning loops, the repository supports **Proactive Human Mentorship**:
- **Direct CLI Ingestion**:
  ```bash
  python3 .agents/scripts/academic_human_mentor.py teach \
    --category principle \
    --statement "<Methodological or statistical rule>" \
    --capability <capability> \
    --scope cross-project
  ```
- **Conversational Directive**:
  When the researcher (Saber) says *"Remember that..."* or *"Learn this..."*, the agent executes `AcademicHumanMentor.teach_from_natural_language()`.
- **Immediate Cross-Project Synchronization**:
  Human-taught items default to `scope: cross-project`, committed to Git, and automatically ingested into subsequent agent pre-flight briefings under `⚖️ Applicable Methodology Rules & Boundary Conditions:`.
