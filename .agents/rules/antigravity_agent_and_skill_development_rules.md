# Antigravity Agent, Subagent & Skill Specification (Directives 12, 18, 19, 20)

Architectural standards for Agents, Subagents, Skills, and Lifecycle Hooks in Antigravity 2.17.

---

## 1. Primary Architecture & Dropdown Taxonomy

- **Track 1 (Main Default Agent)**: Software engineering, code authoring, and test execution (`pytest`). Exempt from research directives.
- **Track 2 (`academic-orchestrator`)**: Sole domain orchestrator (`mainAgent: true, subagent: true`). Possesses `invoke_subagent` and strictly lacks execution tools (`run_command`, `write_to_file`). [Enforcement: `academic_orchestrator_guard.py`]
- **Specialist Subagents (30 agents)**: Declared `mainAgent: false, subagent: true`. Domain workers and read-only critics invoked strictly via `invoke_subagent`.

---

## 2. Dedicated 1:1 Lifecycle Hooks (Antigravity 2.17)
- Every agent is mapped 1:1 to a dedicated guard (`.agents/hooks/agents/<name_snake>_guard.py`) and config (`.agents/hooks/agents/<name_snake>_hook.json`).
- Hook binding is declared directly in `agent.md` frontmatter:
  ```yaml
  hooks:
    - .agents/hooks/agents/<name_snake>_hook.json
  ```
- Execution intercepted synchronously via `PreToolUse` (circuit-breaker) and `Stop` (deliverable quality gate).

---

## 3. Skill Standard & Context Ceilings (Directive 18)

- **Hierarchy**: Entrypoint `.agents/skills/<skill>/SKILL.md`, deterministic scripts in `scripts/`, reference guides in `references/`.
- **Single-View Invariant (Directive 18)**:
  - Strict ceiling: $\le 500$ lines and $\le 40,000$ bytes per file.
  - Large tables and rubrics modularized into `references/`. [Enforcement: `skill_size_guard.py`]
- **Functional Separation (Directive 19)**:
  - Agent decides | Skill instructs | Script computes ("The Hands") | Hook enforces ("The Brakes").
