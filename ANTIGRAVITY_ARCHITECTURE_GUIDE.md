# Google Antigravity Comprehensive Architecture & Engineering Guide
**Agents, Subagents, Skills, Workflows, and Runtime Topology**  
*Document Version: 2026.09.16 | Operative Date: September 16, 2026*

---

## Executive Summary & System Overview

**Google Antigravity (AGY)** is an agent-first Integrated Development Environment (IDE) and developer platform engineered to orchestrate autonomous AI agents across the code editor, terminal, browser, and background operating system processes. Operating on a continuous **Plan → Execute → Verify** cognitive loop, Antigravity structures complex software engineering and research workflows around **Agent Skills**, **Subagents**, and **Dynamic Execution Graphs**, eliminating context bloat while maintaining strict human-in-the-loop (HITL) governance.

As of September 2026, Antigravity spans four core operational surfaces:
1. **Antigravity 2.0 Desktop Application**: An Electron-based command center for multi-workspace orchestration, real-time background task monitoring, scheduled cron jobs/timers, and artifact inspection.
2. **Antigravity IDE**: Standalone or extension-based environment (e.g., VS Code integration) featuring inline code lenses, AST-aware diff reviews, and context-aware chat sidebars.
3. **Antigravity CLI (`agy`)**: A lightweight, terminal-native text user interface (TUI) and headless CLI optimized for local development and remote SSH sessions.
4. **Google Antigravity Python SDK (`google-antigravity`)**: A programmatic framework allowing developers to instantiate, configure, and orchestrate custom agents and multi-tier subagent hierarchies in code.

---

## 1. System Architecture & Runtime Topology

Antigravity operates on a multi-tiered architecture bridging developer user interfaces, an execution runtime daemon, model context engines, and isolated OS-level execution sandboxes:

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer UI (IDE / CLI)                 │
│         (/agents panel, editor lenses, interactive chat)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ IPC / gRPC
┌──────────────────────────────▼──────────────────────────────┐
│                  Antigravity Core Daemon                    │
│  ┌───────────────────────┐      ┌────────────────────────┐  │
│  │ Skill Indexer & Cache │      │ Orchestrator / Planner │  │
│  └───────────────────────┘      └───────────┬────────────┘  │
│  ┌───────────────────────┐                  │               │
│  │ Permission Broker     │◄─────────────────┘               │
│  └───────────────────────┘                                  │
└───────────────┬──────────────────────────────┬──────────────┘
                │ LSP / MCP Protocol           │ Subagent RPC
┌───────────────▼──────────────┐ ┌─────────────▼──────────────┐
│ Context Providers & Tooling  │ │ Subagent Runtime Sandbox   │
│ - Language Server (AST)      │ │ - Worktree Isolation       │
│ - Browser Engine (CDP)       │ │ - Resource Cgroups         │
│ - Local Vector Embeddings    │ │ - Ephemeral Token Budgets  │
└──────────────────────────────┘ └────────────────────────────┘
```

### 1.1 Protocol Integrations
*   **Language Server Protocol (LSP) Bridge**: Unlike legacy chat tools relying on brute-force regex or string grep, Antigravity’s orchestrator hooks directly into the active LSP. It resolves references, verifies symbol definitions, queries compiler diagnostics (type errors, linter output), and validates Abstract Syntax Tree (AST) correctness *before* committing edits to disk.
*   **Model Context Protocol (MCP) Client**: External enterprise datasources, APIs, and cloud services connect via MCP servers. Skills register MCP endpoints dynamically, enabling agents to query databases, call cloud APIs, or trigger CI/CD pipelines natively.
*   **Terminal & PTY Multiplexer**: Terminal actions run inside pseudo-terminals (PTY) managed by the core daemon. It intercepts process signals, strips ANSI control escape sequences, normalizes streaming output, and calculates token-efficient diffs of process outputs.

---

## 2. Primary Agents: Architecture & Governance

### 2.1 Foundational Pillars

Every Antigravity session is anchored by a **Primary Agent** (Lead Agent / Orchestrator). In both the core runtime and the Python SDK, three foundational pillars govern execution:

*   **Agent**: The configuration and policy interface. Manages model selection, tool permissions, capabilities, system instructions (personas), sandbox rules, and lifecycle hooks.
*   **Conversation**: The stateful session engine. Tracks step history, turns, context compaction, and handles streaming interactions (`chat()`).
*   **Connection**: The transport layer to the model backend:
    *   `LocalConnectionStrategy`: Connects to Google AI Studio (Gemini Developer API) or Gemini Enterprise Agent Platform (formerly Vertex AI; supporting Standard ADC and Express API Key modes).
    *   `LiteRTConnectionStrategy`: Runs models locally on-device using LiteRT-LM (e.g., Gemma 2/3) with zero network traffic.
    *   `LocalOpenAIConnectionStrategy`: Connects to local OpenAI-compatible inference servers (Ollama, LM Studio, vLLM).

### 2.2 Operational Execution Behaviors (`agent_behavior`)
*   **Autonomous Mode (`AgentBehavior.AUTONOMOUS`)** *(Default)*: Automated end-to-end task execution. The agent plans, calls tools, handles failures, and verifies outcomes without prompting the user for minor decisions.
*   **Interactive Mode (`AgentBehavior.INTERACTIVE`)**: Collaborative execution. The agent invokes interactive UI tools (`ask_question`) to prompt the user for design sign-offs, requirements clarification, and permission gates.

### 2.3 Python SDK Configuration Example
```python
from google.antigravity import Agent, LocalAgentConfig, types

config = LocalAgentConfig(
    model="gemini-3.7-flash",  # Default model; or gemini-3.8-flash / pro
    system_instructions="You are a Principal Software Architect and Research Lead.",
    capabilities=types.CapabilitiesConfig(
        agent_behavior=types.AgentBehavior.INTERACTIVE,
        enable_subagents=True,
        max_subagent_depth=3,
    ),
    budget_config=types.BudgetConfig(
        max_model_calls=50,
        max_tool_calls=100,
        max_total_tokens=500_000,
    ),
    app_data_dir="/absolute/path/to/custom/storage",  # Absolute path override
)

async def main():
    async with Agent(config=config) as agent:
        response = await agent.chat("Design the OAuth2 authentication module.")
        print(await response.text())
```

### 2.4 Permissions, Security & Sandboxing
*   **Tool Execution Policy**: `always-proceed`, `request-review`, `strict`, or `proceed-in-sandbox`.
*   **Terminal Sandbox**: Enforces restricted container/cgroup isolation on shell commands.
*   **File Access Policy**: `allow`, `ask`, or `deny` access outside the workspace root.
*   **Internet Access Policy**: Controls whether outbound web search, URL fetching, or HTTP calls are allowed.

---

## 3. Subagent Orchestration Engine

As development tasks scale, executing everything in a single conversation thread causes context poisoning, token exhaustion, and thread locking. Antigravity resolves this via **Subagents**.

### 3.1 Role & Purpose
*   **Parallel Execution**: The orchestrator spawns multiple subagents in parallel to execute isolated operations—such as codebase refactoring sweeps, test runs, and background documentation builds.
*   **Ephemeral Token Budgets**: Each subagent runs in its own thread with isolated prompt memory, preventing token bloat in the primary conversation.
*   **Task Delegation Tools**: Controlled via dedicated tools: `define_subagent`, `invoke_subagent`, and `manage_subagents`.

### 3.2 The Three Subagent Creation Paradigms

#### Paradigm A: Declarative Workspace Subagents (`.agents/agents/<name>.md`)
Subagents can be defined declaratively inside `.agents/agents/` (or `.agent/agents/`, `_agents/agents/`):

```markdown
---
name: code-reviewer
description: Expert code quality and security auditor. Audits pull requests, verifies test coverage, and enforces style guidelines.
role: Security & Code Quality Auditor
skills:
  - lint-runner
  - security-scanner
---

# Code Reviewer Subagent Instructions

You are the dedicated Code Reviewer for this repository.
When delegated a task:
1. Run static analysis tools before manual inspection.
2. Verify that unit test coverage does not decrease.
3. Check for OWASP Top 10 vulnerabilities.
4. Report findings in a structured table: Severity | File | Issue | Proposed Fix.
```

#### Paradigm B: Dynamic Runtime Subagents (Antigravity Tools)
During an ongoing session, the orchestrator invokes subagents dynamically:

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `define_subagent` | `name`, `description`, `system_prompt`, `enable_write_tools`, `enable_subagent_tools`, `enable_mcp_tools` | Dynamically registers a new subagent type for the session. |
| `invoke_subagent` | `Subagents` array: `TypeName`, `Role`, `Prompt`, `Model`, `Workspace` | Spawns one or more subagents concurrently. |
| `manage_subagents` | `Action` (`list`, `kill`, `kill_all`), `ConversationIds` | Monitors states (`running`, `idle`, `errored`) or terminates executions. |
| `send_message` | `Recipient` (conversation ID), `Message` | Inter-agent messaging between orchestrator and subagents. |

*   **Model Selection**: `inherit` (default), `flash_lite` (lightweight lookups), `flash` (standard tasks), `pro` (complex reasoning).
*   **Workspace Strategy**: `inherit` (same directory), `branch` (isolated clone), `share` (git worktree).

#### Paradigm C: Programmatic Hierarchies in Python SDK
```python
from google.antigravity import Agent, LocalAgentConfig, types

fact_checker = types.SubagentConfig(
    name="fact_checker",
    description="Verifies claims against internal data.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[types.BuiltinTools.VIEW_FILE],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

lead_researcher = types.SubagentConfig(
    name="lead_researcher",
    description="Conducts domain research and delegates verification.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[types.BuiltinTools.VIEW_FILE, types.BuiltinTools.START_SUBAGENT],
        allowed_subagents=["fact_checker"],
    ),
)

root_config = LocalAgentConfig(
    subagents=[lead_researcher, fact_checker],
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,
        max_subagent_depth=3,
        allowed_subagents=["lead_researcher"],
    ),
)
```

### 3.3 The Subagent Invocation Contract & Response Envelope

#### Invocation Contract (JSON Payload)
```json
{
  "name": "invoke_subagent",
  "arguments": {
    "role": "code-auditor",
    "goal": "Scan all controllers in src/api/ for unauthenticated routes.",
    "workspace_strategy": "git_worktree",
    "token_budget": 16000,
    "timeout_seconds": 300,
    "input_artifacts": [
      "src/api/v1/auth.ts",
      "src/api/v1/billing.ts"
    ],
    "context_briefing": "Focus exclusively on missing @RequireAuth() decorators. Ignore rate-limiting checks."
  }
}
```

#### Subagent Response Envelope
```json
{
  "status": "completed",
  "exit_code": 0,
  "execution_time_ms": 14200,
  "token_usage": {
    "prompt_tokens": 12840,
    "completion_tokens": 890
  },
  "summary": "Audited 14 controllers. Found 2 unauthenticated endpoints in billing.ts.",
  "patch_ref": "git:refs/worktrees/subagent-auditor-17a4",
  "artifacts": [
    {
      "path": "reports/audit-findings.json",
      "action": "created"
    }
  ]
}
```

### 3.4 Git Worktree Isolation Mechanics
To prevent subagents from creating merge conflicts, breaking active builds, or corrupting uncommitted user changes:

1. **Worktree Provisioning**: The daemon executes:
   ```bash
   git worktree add .agents/worktrees/agent-<id> -b agent-branch-<id> HEAD
   ```
2. **Context Anchoring**: The subagent's root working directory is pinned to this auxiliary directory. Reads and writes cannot mutate the active working tree directly.
3. **Automated Conflict-Free Staging**:
   * The subagent commits changes locally to `agent-branch-<id>`.
   * A structural AST diff is compiled against the main branch.
   * The orchestrator presents the changes to the user in the UI as a unified diff.
4. **Pruning**: On merge or rejection, the worktree is dismantled via `git worktree remove --force`.

### 3.5 Permission Bubbling & Security Attenuation
*   **Principle of Least Privilege**: A subagent inherits only a subset of the primary agent’s capabilities.
*   **Permission Bubbling**: When a subagent hits a capability boundary (e.g., executing an unapproved command or accessing sensitive files):
    1. The subagent suspends execution via RPC `YIELD_PERMISSION_WAIT`.
    2. The primary agent captures the suspension.
    3. A high-priority event registers in the `/agents` panel for human approval:
       ```text
       [Subagent: Performance-Tester] 
       Requesting approval: Execute shell command
       Command: `docker run -d -p 5432:5432 postgres:16-alpine`
       Risk Tier: Medium | Worktree: .agents/worktrees/agent-98ef
       [Approve] [Deny] [Terminate Subagent]
       ```
    4. Execution resumes only after explicit user intervention.

---

## 4. Agent Skills: The Modern Production Standard

### 4.1 What are Skills?
**Skills** are modular, directory-based instruction packages adhering to the open **Agent Skills Standard** (`agentskills.io`). They serve as runbooks teaching agents how to perform specific domain workflows without context bloat.

### 4.2 The Three-Tier Progressive Disclosure Pipeline
```
Tier 1: Static Metadata Index (~50–100 tokens per skill)
  Loaded on IDE boot. Formats high-level routing tables in the system prompt.
       │
       ▼ (Condition: Prompt match or deliberate agent lookup)
Tier 2: Active Instructions & Dynamic Prompts (~500–2,500 tokens)
  The core SKILL.md body, parameter definitions, and guidelines inject into working context.
       │
       ▼ (Condition: Step requires external logic / deterministic tool)
Tier 3: Execution Assets & Scripts (0 context tokens)
  Bundled scripts, schemas, and binaries execute directly in the OS/subshell;
  only their structured stdout/stderr passes back into the context.
```

### 4.3 Production Skill Directory Anatomy
```text
.agents/skills/db-schema-migration/
├── SKILL.md                  # Entrypoint, frontmatter metadata, execution guidelines
├── config.json               # Default parameters & environment requirements
├── schemas/
│   └── migration-spec.json   # JSON-schema for validating output structures
├── scripts/
│   ├── dry_run.py            # Local deterministic dry-run verification
│   └── rollback_check.sh     # Safety validator for backwards compatibility
└── templates/
    └── migration.sql.jinja   # Deterministic code templates
```

### 4.4 Complete `SKILL.md` Specification
```yaml
---
name: db-schema-migration
version: 1.2.0
description: |
  Analyzes, drafts, and safely validates PostgreSQL schema migrations.
  Invoked when altering tables, creating indexes, or updating ORM models.
tools:
  - execute_bash
  - lsp_find_references
  - ask_question
allowed-subagents:
  - migration-tester
  - performance-evaluator
parameters:
  type: object
  properties:
    target_table:
      type: string
      description: The primary database table undergoing changes.
    destructive:
      type: boolean
      default: false
      description: Set to true if columns or tables are being dropped.
  required: [target_table]
---

# Database Schema Migration Protocol

## Phase 1: Impact Analysis
1. Inspect the target model definition using `lsp_find_references`.
2. Locate all consuming code paths (services, repositories, APIs).
3. If `destructive == true`, trigger `ask_question` to require developer sign-off.

## Phase 2: Generating Migration Script
1. Apply templates from `./templates/migration.sql.jinja`.
2. Run `./scripts/dry_run.py` to ensure migration runs in transaction mode without locking active writes.

## Phase 3: Subagent Verification
Spawn `migration-tester` to execute rollback tests against local Docker test instances.
```

### 4.5 State Hydration & Scratchpad Pattern
Skills support local disk-backed state serialization. If a multi-step procedure is interrupted:
* Intermediate planning state is saved to `.agents/cache/<skill-name>/state.json`.
* Upon resumption, runtime hooks re-inject this JSON payload into the active context buffer, preventing drift and hallucinations.

---

## 5. Workflows: Architecture, DAGs & Legacy Migration

### 5.1 Dynamic Execution Graphs (Workflow Architecture)

Antigravity executes complex engineering tasks as dynamic Directed Acyclic Graphs (DAGs), coordinating multiple subagents and skills in parallel:

```
                   User Request: "Migrate auth system to OAuth2"
                                      │
                                      ▼
                        [Orchestrator Agent]
                                      │
              Loads Skill: `oauth2-implementation-protocol`
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         │                                                         │
         ▼ (Worktree A)                                            ▼ (Worktree B)
 [Subagent 1: Backend Refactor]                          [Subagent 2: Test Generator]
 - Updates Express handlers                               - Drafts mock OAuth providers
 - Injects token validators                               - Generates integration tests
         │                                                         │
         └────────────────────────────┬────────────────────────────┘
                                      │ (Both branches complete)
                                      ▼
                        [Orchestrator Verification]
                                      │
                                      ▼ (Isolated Sandbox)
                         [Subagent 3: Runner & Auditor]
                         - Merges Worktree A + Worktree B
                         - Executes: `npm run test:e2e`
                                      │
                      ┌───────────────┴───────────────┐
                      │ PASS                          │ FAIL
                      ▼                               ▼
            [Interactive Sign-Off]       [Orchestrator Self-Heal]
            - Surfaces final diff        - Injects test error logs
            - Commits to main branch     - Instructs Subagent 1 to fix
```

### 5.2 Legacy Workflows vs. Modern Agent Skills

| Feature | Legacy Workflows | Modern Agent Skills |
| :--- | :--- | :--- |
| **Format** | Single monolithic `.md` file | Directory bundle (`SKILL.md` + scripts/references/schemas) |
| **Workspace Location** | `.agents/workflows/<name>.md` | `.agents/skills/<name>/SKILL.md` |
| **Context Loading** | Entire file loaded at once | **Progressive disclosure** (metadata first, body on-demand) |
| **Interoperability** | Proprietary Antigravity format | Open Agent Skills Standard (`agentskills.io`) |
| **Subagent Integration** | Linear prompt flow | Deep integration: triggers tools, subagents, and worktrees |
| **Status** | Deprecated (Sunset: Nov 1, 2026) | Current official standard |

### 5.3 Automated Migration via `/migrate-workflows`
Type `/migrate-workflows` in the chat canvas or CLI:
1. Automatically scans workspace and global directories for legacy `.md` workflows and manifests.
2. Formats YAML frontmatter (`name`, `description`).
3. Writes target `skills/<name>/SKILL.md` with overwrite protection.
4. Safely renames legacy files to `<name>.md.bak`.

---

## 6. Advanced Antigravity CLI (`agy`) Usage

The `agy` CLI provides low-level, scriptable control over the Antigravity engine for terminal power users and headless CI/CD automation:

```bash
# 1. Run a skill directly with JSON parameters
agy run skill db-schema-migration --params '{"target_table": "users", "destructive": false}'

# 2. Inspect running subagents
agy agents list --detailed
```
*Output sample:*
```text
ID         ROLE             STATUS     TOKENS    MEMORY    WORKTREE
sub-481    react-generator  RUNNING    4.2k/32k  128MB     .agents/worktrees/agent-sub-481
sub-482    test-runner      IDLE       1.1k/16k  64MB      .agents/worktrees/agent-sub-482
```

```bash
# 3. Stream real-time subagent logs
agy agents logs sub-481 --follow --format=json

# 4. Lint and validate custom skills
agy skill lint .agents/skills/db-schema-migration

# 5. Force merge a subagent worktree after validation
agy agents merge sub-481 --strategy=theirs --clean
```

---

## 7. Debugging, Observability & The Inspection Stack

1. **Deterministic Event Replay**:
   Every event (tool dispatch, LSP response, subagent spawn, human prompt) writes to `.agents/sessions/<session-id>.jsonl`. The IDE session player allows developers to step forward and backward through execution history, inspecting the exact context frame at every step.

2. **Context Window Allocation Heatmaps**:
   The `/agents` inspector visually breaks down token allocation within the model's active context window:
   * **System Prompt & Personas**: ~1,200 tokens (Static configuration)
   * **Skill Injections (Tier 2)**: ~2,400 tokens (Loaded via progressive disclosure)
   * **LSP Metadata / AST Snapshots**: ~4,800 tokens
   * **Conversation History**: ~12,000 tokens (Managed with rolling FIFO truncation)
   * **Subagent Briefing Buffers**: ~2,000 tokens

3. **Subagent Recursion Guard (`ERR_AGENT_RECURSION_LIMIT_EXCEEDED`)**:
   If Subagent A spawns Subagent B, which recursively invokes Subagent C, Antigravity tracks the recursion stack. At **depth 10**, the runtime halts execution, dumps the call stack frame, and alerts the developer, preventing infinite token drain.

---

## 8. Ecosystem Extensions: Rules, Hooks, and Plugins

### 8.1 Workspace & Directory Rules (`AGENTS.md` / `GEMINI.md`)
*   **Scope**: Placed in project root or subdirectories; automatically inherited downward.
*   **Application**: Applies coding conventions, architectural bans, and compliance standards unconditionally or conditionally.
*   **Deduplication**: Automatically deduplicated across directory paths.

### 8.2 Lifecycle Hooks (`hooks.json`)
Hooks execute deterministic shell scripts on agent lifecycle events via JSON stdin/stdout:
*   `PreToolUse`: Gating or modifying tool arguments (`"decision": "deny" | "ask" | "allow"`, `"overwrite": {...}`).
*   `PostToolUse`: Post-processing, running auto-formatters, or running linters.
*   `PreInvocation`: Injecting ephemeral system prompts or reminders.
*   `PostInvocation`: Forcing continuation (`"terminationBehavior": "force_continue"`).
*   `Stop`: Enforcing completion criteria before allowing the agent to exit (`"decision": "continue"`).

### 8.3 Plugins (`plugin.json`)
Plugins package skills, rules, hooks, and MCP configurations into a single distributable directory (`plugins/<name>/`) for team-wide sharing.

---

## 9. Summary Comparison Matrix

| Component | Primary Location | Activation Mechanism | Key Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Agent** | IDE / CLI / SDK Config | Started on session launch | High-level goal decomposition, orchestration, and developer interaction. |
| **Subagent** | `.agents/agents/<name>.md` or runtime tools | Delegated via `invoke_subagent` | Isolated execution (research, test sweeps, builds) using Git worktrees and ephemeral token budgets. |
| **Skill** | `.agents/skills/<name>/SKILL.md` | Semantic intent discovery or slash command `/<name>` | Modular procedural runbook with 3-tier progressive disclosure and helper scripts. |
| **Legacy Workflow** *(Deprecated)* | `.agents/workflows/<name>.md` | Manual slash command | Legacy monolithic prompt template; superseded by Skills (sunset Nov 1, 2026). |
| **Rule** | `AGENTS.md` / `GEMINI.md` | Contextual directory walk | Behavioral constraints, coding standards, and compliance rules. |
| **Hook** | `.agents/hooks.json` | Agent lifecycle events | Deterministic external shell scripts guarding tool calls and turn termination. |
| **Plugin** | `.agents/plugins/<name>/` | Config enablement | Distributable bundle combining skills, rules, hooks, and MCP servers. |

---

## 10. Hands-on Implementation Walkthrough

### Step 1: Create a Custom Subagent
Create `.agents/agents/qa-engineer.md`:
```markdown
---
name: qa-engineer
description: Dedicated testing agent. Runs test suites, identifies regressions, and verifies edge cases.
role: Quality Assurance Specialist
skills:
  - test-runner
---

# QA Engineer System Prompt
You are the Quality Assurance Specialist. Your job is to execute unit and integration tests, parse failures, and report reproducible reproduction steps.
```

### Step 2: Create a Custom Skill
Create `.agents/skills/test-runner/SKILL.md`:
```markdown
---
name: test-runner
description: Executes project unit test suites and outputs structured test results. Use whenever testing code changes.
---

# Test Runner Skill

## Procedures
1. Run test suite:
   `npm test -- --json --outputFile=test_results.json`
2. Inspect `test_results.json` to verify zero failing suites.
3. If failures occur, report the exact assertions and stack traces.
```

### Step 3: Verify the Customizations
*   In the chat interface, type `/test-runner` to test slash command execution.
*   Prompt the agent: *"Use your QA Engineer to run tests and verify that the authentication module passes."*
*   The primary agent detects the subagent, invokes it with `TypeName: "qa-engineer"`, and mounts the `test-runner` skill into the subagent's execution context.
