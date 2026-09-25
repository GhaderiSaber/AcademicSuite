# Antigravity Agent, Subagent & Skill Specification (Directives 12, 18, 19, 20)

Architectural standards for Agents, Subagents, Skills, and Lifecycle Hooks in Antigravity 2.17.

---

## 1. Primary Architecture & Dropdown Taxonomy

- **Track 1 (Main Default Agent)**: Software engineering, code authoring, and test execution (`pytest`). Exempt from research directives.
- **Track 2 (`academic-orchestrator`)**: Sole domain orchestrator (`mainAgent: true, subagent: true`). Possesses `invoke_subagent` and strictly lacks execution tools (`run_command`, `write_to_file`). [Enforcement: `academic_orchestrator_guard.py`]
- **Specialist Subagents (30 agents)**: Declared `mainAgent: false, subagent: true`. Domain workers and read-only critics invoked strictly via `invoke_subagent`.

---

## 2. Dedicated 1:1 Lifecycle Hooks & ASAM Co-Location (Antigravity 2.17)
- Every agent is an **Atomic Self-Contained Agent Module (ASAM)** co-located inside `.agents/agents/<agent_name>/`:
  1. `agent.md`: Persona instructions and frontmatter configuration.
  2. `contract.md`: Contractual Delegation Envelope (CDE) specification and tool boundary.
  3. `guard.py`: Dedicated executable lifecycle guard intercepting runtime operations.
  4. `hooks.json`: Scoped hook definition binding lifecycle events directly to `guard.py`.
- Hook binding is declared directly in `agent.md` frontmatter using the native relative path:
  ```yaml
  hooks:
    - ./hooks.json
  ```
- Execution intercepted synchronously via `PreToolUse` (circuit-breaker) and `Stop` (deliverable quality gate).
- Backward compatibility is maintained via symlink bridges in `.agents/hooks/agents/`.

---

## 3. Skill Standard & Context Ceilings (Directive 18)

- **Hierarchy**: Entrypoint `.agents/skills/<skill>/SKILL.md`, deterministic scripts in `scripts/`, reference guides in `references/`.
- **Single-View Invariant (Directive 18)**:
  - Strict ceiling: $\le 500$ lines and $\le 40,000$ bytes per file.
  - Large tables and rubrics modularized into `references/`. [Enforcement: `skill_size_guard.py`]
- **Functional Separation (Directive 19)**:
  - Agent decides | Skill instructs | Script computes ("The Hands") | Hook enforces ("The Brakes").
