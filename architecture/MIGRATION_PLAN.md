# AcademicSuite — Migration & Stabilization Roadmap

**Document Version:** 1.0.0 (Migration Plan)  
**Operative Date:** September 2026 (1405 SH)  
**System Status:** Execution in Progress — Phase 1 Underway  

---

## 🏛️ Foundational Architectural Rule
> **From this point forward: No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**  
> **This prevents AcademicSuite from continuing to grow horizontally.**

---

## 1. Migration Overview & Objectives

AcademicSuite has developed extensive capabilities across 28 agents, 44 skills, and 29 artifact contracts. To ensure long-term architectural stability and flawless compatibility with Google Antigravity, this migration plan transitions the system from historical ad-hoc components to a hardened, minimal, and fully native Antigravity architecture.

```text
[ Current State ] ────────► [ Phase 1 ] ────────► [ Phase 2 ] ────────► [ Phase 3 ] ────────► [ Phase 4 ] ────────► [ Phase 5 ]
- 28 Agents                Compatibility         Discovery Path        Runtime Purity        Environment           Anti-Sprawl
- 44 Skills                Boundary              Consolidation         Enforcement           Stabilization         Governance
- Redundant Symlinks       - agent_integrity     - Folder-first        - Sole Orchestrator   - Venv / Py 3.14      - Freeze Rule
- commandExecutionPolicy   - Discovery tests       unification         - No Py emulators     - Fail-closed CI      - Release Gate
```

---

## 2. Phase Breakdown

### Phase 1: Establish the Antigravity Compatibility Boundary (Current Phase)
**Goal:** Guarantee that every agent is 100% discoverable and executable by Antigravity's native engine.
- **1.1 Define Native-Agent Contract**:
  - AcademicSuite agents defined as declarative Markdown with YAML frontmatter.
  - Minimal contract: `name` and `description`.
  - Progressive capabilities: `role`, `model`, `mainAgent`, `subagent`, `tools`, `skills`, `agents`, `inheritCustomizations`.
- **1.2 Frontmatter Policy Elimination**:
  - Verify zero occurrences of `commandExecutionPolicy` or `command_execution_policy` in `.agents/agents/`.
  - Enforce execution boundaries via Antigravity permissions, OS mode bits, and `hooks.json`.
- **1.3 Automated Agent Integrity Layer (`validators/agent_integrity.py`)**:
  - Implement comprehensive validator checking:
    1. File location (`.agents/agents/<name>.md` or `<name>/agent.md`)
    2. YAML syntax validity
    3. Required `name` (lowercase ASCII kebab-case)
    4. Required `description` (non-empty)
    5. Unique name across all agents
    6. Discoverability by Antigravity loader
    7. Valid tool names against Antigravity whitelist
    8. Valid Skill references resolving on disk or built-in
    9. Valid MCP references
    10. No circular dependencies in `agents:` delegation graph
    11. No duplicate canonical agents
    12. Correct `mainAgent` / `subagent` semantics (ensuring delegated agents have `subagent: true`)
- **1.4 Test Discovery Suite (`tests/test_agent_discovery.py`)**:
  - Automated test harness verifying discovery, subagent invocation readiness, and minimal agent parsing.

---

### Phase 2: Discovery Path Consolidation
**Goal:** Eliminate redundant discovery paths and ensure consistent agent loading across all IDE surfaces.
- **Problem**: Both `.agents/agents/<name>/agent.md` and symlinks `.agents/agents/<name>.md` exist. Certain IDE versions or filesystem watchers can detect symlinks as duplicate agents or encounter symlink traversal issues on non-POSIX platforms (Windows).
- **Actions**:
  1. Standardize on canonical directory packaging: `.agents/agents/<name>/agent.md`.
  2. Retain symlinks only where backward compatibility with legacy tooling is proven necessary.
  3. Validate that Antigravity's `/agents` picker lists exactly 28 unique agents with zero duplicates.

---

### Phase 3: Runtime Purity & Sole Orchestrator Enforcement
**Goal:** Completely eliminate any legacy Python scripts that emulate agent loops.
- **Constitutional Directive 12.1 Compliance**:
  - Antigravity is the sole agent runtime and multi-agent orchestrator.
  - Subagents must be invoked natively via the `invoke_subagent` tool.
- **Actions**:
  1. Audit `scripts/` for any legacy dispatching or agent emulation classes.
  2. Confirm `scripts/suite_cli.py` and `scripts/academic_task_router.py` act purely as deterministic CLI runners for "The Hands", leaving all agent orchestration to Antigravity.
  3. Archive any obsolete migration or dispatch scripts to `legacy/`.

---

### Phase 4: Environment & Dependency Stabilization
**Goal:** Ensure all deterministic scripts and test harnesses run reliably across development and production environments.
- **Problem**: System Python 3.14 lacks data science packages (`pandas`, `numpy`, `openpyxl`), causing import errors in specific vertical slice tests.
- **Actions**:
  1. Formalize virtual environment bootstrap: `scripts/bootstrap_env.sh` creating `.venv/` with pinned versions in `requirements.txt`.
  2. Ensure all core validators and discovery tests remain zero-dependency (relying strictly on standard library Python).
  3. Provide clear fallback diagnostics when data science libraries are missing from the host Python.

---

### Phase 5: Verification, Gatekeeping & Anti-Sprawl Governance
**Goal:** Lock down the architecture against horizontal sprawl.
- **Actions**:
  1. Enforce the **Horizontal Growth Freeze Rule**:
     - Pull requests or changes introducing a new agent or skill must provide an Architectural Gap Justification.
     - New agents or skills cannot be merged without corresponding updates to `architecture/CURRENT_ARCHITECTURE.md`.
  2. Integrate `validators/agent_integrity.py` into the Antigravity `Stop` hook and CI test runner.
  3. Maintain full test suite pass rate.
