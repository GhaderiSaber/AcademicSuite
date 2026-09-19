# AcademicSuite — Architectural Decision Records (ADRs)

**Document Version:** 1.0.0  
**Operative Date:** September 2026 (1405 SH)  
**Status:** Approved & Binding  

---

## Index of Architectural Decision Records

| ADR ID | Title | Status | Date |
|---|---|---|---|
| [ADR-001](#adr-001-antigravity-native-runtime-as-sole-multi-agent-orchestrator) | Antigravity Native Runtime as Sole Multi-Agent Orchestrator | Accepted | 2026-09-16 |
| [ADR-002](#adr-002-elimination-of-commandexecutionpolicy-from-agent-frontmatter) | Elimination of `commandExecutionPolicy` from Agent Frontmatter | Accepted | 2026-09-17 |
| [ADR-003](#adr-003-subagent-and-mainagent-discovery-semantics) | Subagent and MainAgent Discovery Semantics | Accepted | 2026-09-19 |
| [ADR-004](#adr-004-the-triad-artifact-invariant-and-one-hypothesis-one-stage) | The Triad Artifact Invariant and One-Hypothesis-One-Stage Granularity | Accepted | 2026-09-15 |
| [ADR-005](#adr-005-multi-layered-defense-in-depth-security-architecture) | Multi-Layered Defense-in-Depth Security Architecture | Accepted | 2026-09-18 |
| [ADR-006](#adr-006-hard-boundary-against-horizontal-growth-and-sprawl) | Hard Boundary Against Horizontal Growth & Architectural Sprawl | Accepted | 2026-09-19 |

---

## ADR-001: Antigravity Native Runtime as Sole Multi-Agent Orchestrator

### Context
Previous iterations explored custom Python wrappers and dispatcher scripts to emulate multi-agent communication loops, subagent queues, and turn coordination. This created a dual-runtime conflict with Google Antigravity's built-in execution engine, leading to tool desynchronization, unmonitored subagents, and violation of the native Antigravity lifecycle.

### Decision
Antigravity is declared the **sole agent runtime and multi-agent orchestrator** (Directive 12.1).
- All subagents must be invoked natively via Antigravity's `invoke_subagent` tool.
- Python scripts are classified strictly as "The Hands" (deterministic CLI tools executed via `run_command`).
- Developing or executing standalone Python agent emulators is strictly prohibited.

### Consequences
- **Positive**: Native UI visibility in Antigravity IDE, correct transcript logging, full lifecycle hook enforcement, zero duplicate event loops.
- **Negative**: Coordination logic cannot use bespoke Python multithreading; must rely on Antigravity subagent mechanisms.

---

## ADR-002: Elimination of `commandExecutionPolicy` from Agent Frontmatter

### Context
Historical templates included `commandExecutionPolicy: request-review` (or snake_case `command_execution_policy`) inside agent YAML frontmatter. Antigravity's agent loader uses a strict parser schema for Markdown agents. Unknown frontmatter fields cause the parser to drop the agent silently, hiding it from the IDE `/agents` dropdown and subagent registry.

### Decision
`commandExecutionPolicy` and all variant spellings are completely removed and barred from agent YAML frontmatter.
- Agent specifications contain only valid Antigravity frontmatter properties.
- Execution restrictions and shell safety are enforced via workspace permissions, native OS permissions, and `.agents/hooks.json`.

### Consequences
- **Positive**: 100% agent discoverability across all Antigravity surfaces.
- **Negative**: Frontmatter cannot declare per-agent execution policies; must rely on tool lists and lifecycle hooks.

---

## ADR-003: Subagent and MainAgent Discovery Semantics

### Context
In Antigravity, the agent loader uses two boolean flags in frontmatter:
- `mainAgent`: Controls whether the agent appears in the top-level chat / user persona picker.
- `subagent`: Controls whether the agent is mounted in the `invoke_subagent` tool registry.
Previously, Tier 1 and Tier 2 domain authorities (`methodology-expert`, `statistical-expert`, `academic-writer`, `evidence-auditor`, `final-judge`) were marked `mainAgent: true, subagent: false`. Consequently, when `academic-orchestrator` attempted to delegate tasks to these domain authorities, Antigravity blocked the call because they were excluded from the subagent registry.

### Decision
All specialist domain authorities that can be delegated to by the lead orchestrator must have `subagent: true`.
- Orchestrators and domain authorities can have `mainAgent: true, subagent: true` (dual-role: interactive chat or callable worker).
- Pure execution workers and critics have `mainAgent: false, subagent: true`.
- The `agent_integrity` validator strictly checks that any agent listed in another agent's `agents:` array has `subagent: true`.

### Consequences
- **Positive**: `academic-orchestrator` can seamlessly invoke all 22 domain agents and 6 learning subagents natively.
- **Negative**: Specialist authorities will appear in both the main agent picker and the subagents list.

---

## ADR-004: The Triad Artifact Invariant and One-Hypothesis-One-Stage

### Context
Monolithic LLM generation of academic chapters leads to severe hallucinations, loss of statistical precision, omission of negative results, and typography errors in complex Persian BiDi layouts.

### Decision
Under Directive 3, every micro-stage and individual hypothesis must produce a **synchronized physical triad of artifacts on disk**:
1. **`.json`**: Machine-readable statistics, parameters, and audit checklists.
2. **`.md`**: Scholarly narrative, APA 7 tables, and interpretations for instant inspection and diffing.
3. **`.docx`**: Institutional OpenXML document with strict typography (`B Nazanin` / `B Titr`), decoupled LTR numbers, and native Word OMML math.
Furthermore, under the One-Hypothesis-One-Stage invariant, each hypothesis has its own isolated micro-stage directory.

### Consequences
- **Positive**: Complete auditability, diffable outputs, zero mental statistical calculation, fail-closed validation.
- **Negative**: Higher disk space and multi-stage orchestration overhead.

---

## ADR-005: Multi-Layered Defense-in-Depth Security Architecture

### Context
Protecting raw empirical datasets from accidental mutation or tampering is an existential requirement in academic consulting. Frontmatter declarations alone cannot prevent tool misuse or malicious scripts.

### Decision
Security is implemented across four independent layers:
1. **Platform Layer**: Antigravity tool permissions and interactive confirmation gates.
2. **OS Layer**: `scripts/permission_manager.py` enforces POSIX `0444` (read-only) modes on raw input datasets.
3. **Hook Layer**: `.agents/hooks.json` intercepts `PreToolUse` to block destructive commands (`rm -rf`, `chmod`) and raw data writes, and `Stop` to enforce the Binary Honesty Protocol.
4. **Execution Layer**: Deterministic scripts check file existence and fail closed on unauthorized paths.

### Consequences
- **Positive**: Full tamper resistance, zero risk of raw data loss, cross-platform POSIX/Windows support.
- **Negative**: Development scripts must explicitly stage derived files in `02_clean_and_scored/` rather than modifying raw inputs.

---

## ADR-006: Hard Boundary Against Horizontal Growth & Architectural Sprawl

### Context
AcademicSuite has expanded to 28 agents, 44 skills, and 29 contracts. Unchecked proliferation of specialized agents and wrapper abstractions increases cognitive overhead, maintenance burden, and context fragmentation.

### Decision
A permanent freeze on horizontal growth is instituted:
> **No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**
- Any new component requires an Architectural Gap Justification filed in `architecture/CURRENT_ARCHITECTURE.md`.
- Default preference must be to refine existing deterministic scripts ("The Hands") or update existing skills rather than creating new agents or skills.

### Consequences
- **Positive**: Focused refinement, deep stability, predictable behavior, zero feature bloat.
- **Negative**: Developers cannot create ad-hoc experimental agents without formal justification.
