---
name: academic-adaptive-context
description: "Retrieve targeted active behavioral context (lessons, anti-patterns, exemplars, calibrated defaults) relevant to the current task from the persistent learning store without dumping irrelevant records."
---

# Academic Adaptive Context Skill (بازیابی بافت رفتاری تطبیقی)

Connects the repository's persistent knowledge store directly to live agent execution:
$$\text{PERSISTENT KNOWLEDGE} \longrightarrow \text{ADAPTIVE AGENT CONTEXT} \longrightarrow \text{EXECUTABLE TASK}$$

Provides agents with a compact, high-signal behavioral briefing containing active lessons, anti-patterns to avoid, gold-standard exemplars to emulate, and known failure modes before commencing any research, statistical, or drafting task.

---

## 🛑 Strict Architectural Non-Goals & Boundaries

1. **NOT an Orchestration Skill**:
   - This skill **never** dispatches subagents, transitions state machine milestones, or creates project plans. That is the exclusive domain of `academic-orchestrator`.
2. **NOT a Statistical Execution Engine**:
   - This skill **never** calculates numbers, $p$-values, effect sizes, or runs regressions in its head or in Python. Statistical execution belongs to specialized skills (`mediation`, `sem`, `regression`, `apa-reporting`).
3. **NOT Self-Mutating**:
   - This skill **never** modifies its own instructions, prompts, or code. Knowledge evolution occurs through formal promotion gates (`promotion_decision`).
4. **Anti-Dump Invariant (Zero Prompt Flooding)**:
   - **Never** dump the entire learning repository into the prompt. Agents must query strictly for the active capability, task, and project.
5. **Strict Scope Containment**:
   - Project-specific rules from Project A **must never** be applied as universal rules in Project B. Only cross-project invariants and domain-wide principles generalize.

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

## 3. The 5-Step Adaptive Context Protocol

Whenever an agent is tasked with executing a capability, it MUST execute the following deterministic protocol:

### Step 1: Identify Target Capability & Task
Determine the core research capability from the 8 canonical capabilities:
- `longitudinal-analysis`
- `mediation`
- `moderation`
- `SEM`
- `psychometrics`
- `chapter4`
- `chapter5`
- `evidence`

### Step 2: Execute Deterministic Context Retrieval
Run the bundled retrieval CLI via terminal (`run_command`):
```bash
python3 .agents/skills/academic-adaptive-context/scripts/retrieve_adaptive_context.py \
  --capability <capability> \
  --task <task_type> \
  --agent <agent_name> \
  --project-id <project_id> \
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
