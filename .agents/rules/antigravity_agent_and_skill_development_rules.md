# Antigravity Agent, Subagent & Skill Development Rules

This rule document defines the operational standards and invariant rules for defining and orchestrating **Agents**, **Subagents**, and **Skills** within the Google Antigravity ecosystem.

---

## 1. Creating Primary Agents

1. **Cognitive Loop**: Every primary agent operates on the **Plan → Execute → Verify** cognitive loop.
2. **Behavioral Modes**:
   - `AgentBehavior.AUTONOMOUS`: Used for non-blocking background pipelines and automated CI/CD runs.
   - `AgentBehavior.INTERACTIVE`: Used for collaborative pair programming where clarifying questions (`ask_question`) and human-in-the-loop stage gates are enforced.
3. **Budget Controls**:
   - Always configure explicit budget ceilings (`max_model_calls`, `max_tool_calls`, `max_total_tokens`) in production pipelines to prevent runaway inference loops.
4. **Tool Whitelisting & Sandboxing**:
   - Scope capabilities using the principle of least privilege. Destructive shell execution must be sandboxed (`proceed-in-sandbox`) or gated behind human confirmation (`request-review`).

---

## 2. Creating Subagents

Subagents are isolated workers designed to execute specialized subtasks without causing "context bankruptcy" in the parent orchestrator.

### 2.1 The Three Creation Paradigms
- **Paradigm A (Declarative Workspace Subagent)**:
  - Stored in `.agents/agents/<name>.md` or `~/.gemini/config/agents/<name>.md`.
  - Must include valid YAML frontmatter:
    ```yaml
    ---
    name: <lowercase-hyphenated-name>
    description: <clear delegation criteria and capability description>
    role: <2-5 word job title>
    model: flash | pro | flash_lite | inherit
    subagent: true
    mainAgent: false
    tools:
      - <permitted_tool_1>
      - <permitted_tool_2>
    skills:
      - <skill_name>
    ---
    # Instructions
    <Detailed system instructions, behavioral boundaries, and audit criteria>
    ```
- **Paradigm B (Dynamic Runtime Subagents)**:
  - Use `define_subagent` to dynamically register bespoke subagents during a live session.
  - Invoke concurrently via `invoke_subagent` with explicit `TypeName`, `Role`, `Prompt`, `Model`, and `Workspace`.
  - Inspect, communicate with, and terminate subagents using `manage_subagents` and `send_message`.
- **Paradigm C (Programmatic Python SDK)**:
  - Use `google.antigravity.types.SubagentConfig` and `SubagentCapabilities`.
  - Enforce tree hierarchy via `max_subagent_depth` and `allowed_subagents`.

### 2.2 Workspace Isolation Standards
- **`Workspace: "inherit"`**: Direct execution in current working directory. Use strictly for read-only research or linear non-conflicting edits.
- **`Workspace: "branch"`**: Creates an ephemeral Git worktree. Mandatory for parallel code generation or risky refactors to prevent write collisions.
- **`Workspace: "share"`**: Shares repository object storage for large monorepos with zero storage duplication.

### 2.3 Model Tier Allocation
- **`flash_lite`**: File searches, regex parsing, rapid log filtering.
- **`flash`**: Standard code drafting, test runs, deterministic tool executions.
- **`pro`**: Complex architectural synthesis, adversarial auditing, formal proofs, committee defense simulation.
- **`inherit`**: Matches the parent agent's tier.

### 2.4 Reactive Wakeup vs. Polling
- **Zero Tight-Loop Polling**: Never write loops polling `status` or running `sleep`. Antigravity reactively awakens the orchestrator upon subagent message arrival or process termination.

---

## 3. Creating Skills (Agent Skills Standard)

Skills provide modular procedural knowledge, runbooks, and deterministic scripts ("The Hands").

### 3.1 Directory Structure
Every skill must reside in `.agents/skills/<skill-name>/` and follow this hierarchy:
```text
skills/<skill-name>/
├── SKILL.md            # [REQUIRED] Entrypoint instructions with YAML frontmatter
├── scripts/            # [OPTIONAL] Deterministic Python/Bash tools ("The Hands")
├── references/         # [OPTIONAL] Deep documentation, schemas, and templates
├── examples/           # [OPTIONAL] Exemplar outputs and reference implementations
└── resources/          # [OPTIONAL] Static assets, seed datasets, or templates
```

### 3.2 `SKILL.md` Anatomy & Frontmatter
```yaml
---
name: <exact-directory-name>
description: <concise summary of WHAT the skill does and EXACT TRIGGERS for when to activate it>
---

# <Skill Title>

## Overview
<Clear problem statement and operational context>

## Deterministic Execution Sequence
1. Step 1: Execute deterministic script via `run_command`.
2. Step 2: Extract verified JSON values.
3. Step 3: Format output according to institutional specifications.

## References
- For detailed technical schemas, see [references/schema_guide.md](references/schema_guide.md).
```

### 3.3 The Single-View Invariant (Directive 18)
To prevent context overflow and guarantee that any agent can ingest 100% of a skill in a single `view_file` call without truncation:
- **Maximum Lines**: $\le 500$ lines.
- **Maximum File Size**: $\le 40,000$ bytes.
- **Modularization**: Lengthy tables, extended schemas, and exemplars must be placed in `references/` and referenced via Markdown links.

### 3.4 Separation of "The Hands" vs. "The Brains"
- **The Brains (LLM / Subagent)**: Epistemic evaluation, narrative synthesis, hypothesis testing strategy.
- **The Hands (Deterministic Scripts in `scripts/`)**: Matrix math, effect size calculations, $p$-values, OpenXML document generation, and statistical modeling.
- **Absolute Rule**: Never calculate or guess statistical values in the prompt. Always run bundled scripts and extract exact numbers from output JSON files.

---

## 4. AcademicSuite Specific Repository Conventions

All agents, subagents, and skills created within the AcademicSuite repository MUST adhere to these workspace-specific conventions:

1. **Dual-Entry Subagent Architecture**:
   - Create `.agents/agents/<name>/agent.md` containing full prompt and operational modes.
   - Maintain the root-level entrypoint `.agents/agents/<name>.md` with frontmatter `skills` and `role`.
   - Optionally add `.agents/agents/<name>/contract.md` defining artifact handoffs.
2. **Constitutional Invariant Header**:
   - Every agent system prompt MUST include the mandatory Directives block from `AGENTS.md` (Directive 0 Binary Honesty, Directive 2 Deterministic Calculations, Directive 4 APA 7 & Persian Leading Zero Standard, Directive 5 BiDi OpenXML & Font Binding, Directive 6 English-Only Filenames, Directive 14 Anti-Hallucination, Directive 15 Temporal Reality Anchor: 2026).
3. **Triad Artifact Invariant (Directive 3)**:
   - Multi-stage pipelines must emit synchronized triads on disk: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats).
4. **Registration in Activation Matrix**:
   - Every newly created skill must be cataloged in `.agents/references/SKILL_ACTIVATION_MATRIX.md` with trigger conditions, inputs, outputs, and assigned subagent role.
5. **English-Only ASCII Filenames (Directive 6)**:
   - All files, directories, and scripts MUST use English ASCII characters strictly (`[a-zA-Z0-9_.-]`).

