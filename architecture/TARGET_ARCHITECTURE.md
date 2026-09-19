# AcademicSuite — Target Architecture & Antigravity Compatibility Specification

**Document Version:** 1.0.0 (Target Architecture)  
**Operative Date:** September 2026 (1405 SH)  
**System Status:** Authoritative Target Architecture  

---

## 🏛️ Foundational Architectural Rule
> **From this point forward: No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**  
> **This prevents AcademicSuite from continuing to grow horizontally.**

---

## 1. Architectural Philosophy: Native Antigravity Alignment

The primary technical objective of the **Target Architecture** is to establish a seamless, thin compatibility boundary with Google Antigravity. Rather than attempting to wrap, emulate, or replace Antigravity's agent runtime, AcademicSuite functions as a collection of:
1. **Declarative Antigravity-Native Agents & Subagents** (`.agents/agents/`)
2. **On-Demand Progressive Disclosure Skills** (`.agents/skills/`)
3. **Deterministic Mathematical & Document Engines** (`scripts/` and skill `scripts/`)
4. **Lifecycle Hooks & OS Security Gates** (`.agents/hooks.json` and POSIX permissions)
5. **Fail-Closed Artifact Verification Contracts** (`contracts/` and `validators/`)

```text
+-----------------------------------------------------------------------------------+
|                        GOOGLE ANTIGRAVITY AGENT RUNTIME                           |
|                                                                                   |
|  [ Antigravity Session ] <---> [ Native invoke_subagent ] <---> [ Subagents ]     |
|          |                                                             |          |
|          | Context / Memory                                            | Tools    |
|          v                                                             v          |
|  [ Progressive Skills ]                                        [ Built-in Tools ] |
|   .agents/skills/<name>/SKILL.md                               - run_command      |
|                                                                - view_file        |
|                                                                - write_to_file    |
+----------------------------------------+------------------------------------------+
                                         |
                                         | Execution Boundary (run_command / CLI)
                                         v
+-----------------------------------------------------------------------------------+
|                         ACADEMICSUITE DETERMINISTIC "HANDS"                       |
|                                                                                   |
|   +--------------------------+  +-------------------------+  +-----------------+  |
|   | Statistical Engines      |  | Psychometrics & Sizing  |  | OpenXML Word    |  |
|   | - run_regression.py      |  | - gpower_engine.py      |  | - build_triad   |  |
|   | - run_sem.py             |  | - psychometrics.py      |  | - assemble_docx |  |
|   +--------------------------+  +-------------------------+  +-----------------+  |
+----------------------------------------+------------------------------------------+
                                         |
                                         | Output Verification Boundary
                                         v
+-----------------------------------------------------------------------------------+
|                         INDEPENDENT FAIL-CLOSED VALIDATION                        |
|                                                                                   |
|   +---------------------------------------------------------------------------+   |
|   | validators/run_all_validators.py                                          |   |
|   | - data_integrity          - statistical_assumptions                       |   |
|   | - numerical_consistency   - result_consistency                            |   |
|   | - reporting_consistency   - longitudinal_modmed                           |   |
|   +---------------------------------------------------------------------------+   |
|                                                                                   |
|          Generates: Synchronized Triad Artifacts (.docx + .md + .json)            |
+-----------------------------------------------------------------------------------+
```

---

## 2. The Six-Part Functional Separation Invariant

To guarantee architectural stability, eliminate hallucinations, and prevent horizontal sprawl, AcademicSuite strictly enforces the six-part separation of concerns across every research engagement:

```text
+──────────────────────+─────────────────────────────────────────────────────────────+
| Layer                | Operational Scope & Invariant Ownership                     |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 1. Agent             | DECIDES: Reasoning role, delegation, context,               |
|                      | decision-making, responsibility, communication              |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 2. Skill             | INSTRUCTS: Domain knowledge, decision trees,                |
|                      | execution instructions, reusable procedures, APA formats    |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 3. Script            | COMPUTES: Deterministic calculation, data transformation,   |
|                      | file generation, OpenXML compilation, hashing               |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 4. Hook              | ENFORCES: Synchronous interception, safety gates,           |
|                      | tamper prevention, honesty audits, tool execution control   |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 5. State Machine     | AUTHORIZES TRANSITION: Milestone progression gating,        |
|                      | immutable event timeline logging, state persistence         |
+──────────────────────+─────────────────────────────────────────────────────────────+
| 6. Artifact Manifest | DEFINES COMPLETION: Schema contract validation,             |
|                      | required triad files (.docx+.md+.json), affirmative evidence |
+──────────────────────+─────────────────────────────────────────────────────────────+
```

---

## 3. The Native-Agent Contract

AcademicSuite defines agents purely as Antigravity-compatible Markdown files. There is **zero proprietary Python agent runtime** or wrapper class.

### 3.1 The Minimal Agent Contract
An agent is valid in Antigravity when it contains only:
```markdown
---
name: sample-agent
description: Clear, actionable description of role and delegation triggers.
---

# Agent Instructions

Detailed behavioral instructions, domain principles, and workflows.
```

### 3.2 The Progressive Capability Contract
As needs expand, the following official Antigravity fields may be added:
```markdown
---
name: statistical-expert
description: Advanced quantitative modeling authority for SEM, CFA, mediation, moderation.
role: Statistical Modeling & Latent Structural Analysis Authority
model: pro
mainAgent: true
subagent: true
tools:
  - run_command
  - view_file
  - write_to_file
  - replace_file_content
  - list_dir
  - grep_search
  - find_by_name
skills:
  - sem
  - cfa
  - mediation
  - moderation
  - regression
  - statistical-data-analyst
agents:
  - statistics-agent
  - psychometric-expert
inheritCustomizations: true
---
```

### 3.3 Strict Frontmatter Policy Elimination
- **`commandExecutionPolicy` is strictly forbidden in frontmatter**.
- Antigravity's agent loader rejects frontmatter with unknown fields, hiding the agent from the IDE dropdown and subagent registry.
- Security is instead enforced through the multi-layered security architecture described in Section 5.

---

## 4. Subagent & MainAgent Semantics

In Antigravity:
- **`mainAgent: true`**: Agent appears in the primary workspace agent selector / chat interface.
- **`subagent: true`**: Agent appears in the available subagents registry for the `invoke_subagent` tool.
- **`mainAgent: true, subagent: true`** (Dual-Role Authority): Specialist authorities (such as `methodology-expert`, `statistical-expert`, `academic-writer`) can be selected by the user for direct interactive chat OR spawned dynamically by `academic-orchestrator` as subagents.
- **`mainAgent: false, subagent: true`** (Pure Specialist Subagent): Pure workers and critics (such as `statistics-agent`, `data-curator`, `results-auditor`) are invoked solely by orchestrators and authorities.

---

## 5. Multi-Layered Defense-in-Depth Security

In place of unsupported frontmatter policy flags, execution restrictions are enforced mechanically across four independent layers:

```text
Layer 1: Antigravity Platform & IDE Permissions
   │     Workspace settings, user confirmation prompts on untrusted commands.
   ▼
Layer 2: POSIX / OS Least-Privilege File Permissions
   │     scripts/permission_manager.py marks raw datasets as 0444 (Read-Only).
   ▼
Layer 3: Constitutional Lifecycle Hooks (.agents/hooks.json)
   │     PreToolUse blocks destructive shell commands, non-ASCII filenames, and dataset mutation.
   │     Stop hook inspects transcript.jsonl to enforce Binary Honesty and invoke_subagent truth.
   ▼
Layer 4: Deterministic Scripts & Agent Instructions
         Domain scripts fail-closed on unauthorized inputs; agent contracts forbid out-of-scope actions.
```

---

## 6. The Triad Artifact Invariant & Stage-Gate Granularity

Under Constitutional Directive 3:
1. **Zero Monolithic Generations**: Generating an entire chapter or dissertation in a single un-audited prompt is strictly forbidden.
2. **Synchronized Triad Artifacts**: Every micro-stage and individual hypothesis must produce three synchronized physical files on disk:
   - **`.json`**: Exact numerical parameters, test statistics, and audit flags.
   - **`.md`**: Human-readable narrative, APA 7 tables, and statistical interpretations for immediate diffing.
   - **`.docx`**: Institutional OpenXML document with RTL typography, Persian font bindings (`B Nazanin` / `B Titr`), decoupled LTR numbers, and native Word OMML math equations.
3. **One-Hypothesis-One-Stage**: Every hypothesis in Chapter 4 and Chapter 5 has an independent micro-stage directory (`06_hypothesis_1.docx`, `06_hypothesis_1.md`, `06_hypothesis_1.json`).

---

## 7. Continuous Learning & Self-Improvement Boundaries

The self-improvement subsystem (`learning/` and `contracts/evolution/`) operates under strict containment:
1. **Zero Runtime Self-Modification**: Learning subagents cannot directly mutate active skill files (`SKILL.md`) or agent specifications (`agent.md`).
2. **Candidate Mutation Protocol**: Improvements are drafted as structured candidates (`improvement_candidate.schema.json`) and benchmarked against frozen evaluation suites (`evaluation_case.schema.json`).
3. **Human-in-the-Loop Promotion**: Promotion requires explicit verification by `evaluation-agent` and final human approval. 

---

## 8. Capability-Driven Orchestration Architecture (Phase 3)

### 8.1 Resolution Architecture
AcademicSuite replaces static linear progression chains (`stage 1 → stage 2 → ... → statistics-agent`) with dynamic, capability-based resolution:

```text
Task Prompt
     │
     ▼
Research Objective & Empirical Design Derivation
     │  - study_type: RCT, correlational_structural, scale_validation, qualitative, meta_analysis
     │  - group_structure: multi-group, single-group, factorial
     │  - temporal_dynamics: repeated measures, cross-sectional, single-point
     │  - waves: follow-up, pre-post, cross-sectional
     │  - factors: ["RCT", "multi-group", "repeated measures", "follow-up"]
     ▼
Required Capabilities Matrix
     │  - design-methodology
     │  - longitudinal-analysis
     │  - assumption-checking
     │  - effect-size
     │  - post-hoc/comparison
     │  - statistical-execution
     │  - results-writing
     │  - audit
     ▼
Dynamic Antigravity Subagent Team Assembly
     │  - Lead Orchestrator: academic-orchestrator
     │  - Minimal Assembled Subagents: [methodology-expert, data-curator, statistical-expert,
     │                                  statistics-agent, academic-writer, statistical-auditor,
     │                                  academic-challenger, validation-agent]
     │  - Pruned Agents: Explicitly accounts for and excludes unneeded workspace agents
     │                   with documented scientific rationale
     ▼
Native Antigravity Execution via `invoke_subagent`
```

### 8.2 Architectural Invariants
1. **Deterministic Resolver as "The Hands"**: `scripts/academic_task_router.py` and `scripts/capability_resolver.py` compute design parameters, capability requirements, and team compositions deterministically. They never execute agents or simulate orchestration.
2. **Antigravity as Sole Conductor**: `academic-orchestrator` is the sole orchestrator, dynamically invoking only the resolved subagent roles via native `invoke_subagent`.
3. **Fail-Closed Safety**: Out-of-domain, non-academic, or unsupported requests are blocked with `status: BLOCKED` and `escalation_required: true`. Ambiguous requests return candidate capabilities and clarification prompts rather than guessing.

