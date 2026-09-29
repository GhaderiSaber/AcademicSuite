# Google Antigravity 2.18.1 Architecture & Control Manual
## Definitive Reference: Agents, Subagents, Rules, Lifecycle Hooks & Multi-Agent Orchestration

**Platform Version:** Google Antigravity 2.18.1 (Latest Release: September 28, 2026)  
**Authoritative Documentation Source:** `https://antigravity.google/docs`  
**Operative Environment:** Antigravity 2.0 (Desktop), Antigravity CLI (`agy`), Antigravity IDE, Google Antigravity Python SDK (`google-antigravity`)

---

## Table of Contents
1. [Platform State & 2.18.1 Innovations](#1-platform-state--2181-innovations)
2. [Primary & Custom Agents](#2-primary--custom-agents)
   - [2.1 Architectural Pillars (Agent, Conversation, Connection)](#21-architectural-pillars)
   - [2.2 Execution Modes & Sandboxing](#22-execution-modes--sandboxing)
   - [2.3 Custom Primary Agents (`.agents/agents/<name>.md`)](#23-custom-primary-agents)
   - [2.4 Agent Frontmatter Specification](#24-agent-frontmatter-specification)
   - [2.5 Modular Tool & Prompt Toggling](#25-modular-tool--prompt-toggling)
3. [Subagents: Architecture, Creation & Management](#3-subagents-architecture-creation--management)
   - [3.1 Architectural Principles & Anti-Bloat Strategy](#31-architectural-principles--anti-bloat-strategy)
   - [3.2 The 10-Level Nesting Ceiling](#32-the-10-level-nesting-ceiling)
   - [3.3 Paradigm A: Declarative Workspace Subagents](#33-paradigm-a-declarative-workspace-subagents)
   - [3.4 Paradigm B: Dynamic Runtime Subagents (`define_subagent`, `invoke_subagent`, `manage_subagents`)](#34-paradigm-b-dynamic-runtime-subagents)
   - [3.5 Paradigm C: Programmatic Python SDK Subagents](#35-paradigm-c-programmatic-python-sdk-subagents)
   - [3.6 Workspace Isolation Modes (`inherit`, `branch`, `share`)](#36-workspace-isolation-modes)
   - [3.7 Subagent Lifecycle States & Auto-Wake Mechanics](#37-subagent-lifecycle-states--auto-wake-mechanics)
   - [3.8 Monitoring, Teleporting (`Alt+J`) & Fast-Path Approvals (`Ctrl+K`)](#38-monitoring-teleporting--fast-path-approvals)
4. [Rules (`AGENTS.md`, `GEMINI.md` & Modular Rules)](#4-rules-agentsmd-geminimd--modular-rules)
   - [4.1 Hierarchy & Scopes](#41-hierarchy--scopes)
   - [4.2 Root Files vs. Modular Rule Files](#42-root-files-vs-modular-rule-files)
   - [4.3 Trigger Modes (`always_on`, `model_decision`, `glob`, `manual`)](#43-trigger-modes)
   - [4.4 Budgets, 24 KB File Cap & Demotion Protocol](#44-budgets-24-kb-file-cap--demotion-protocol)
5. [Lifecycle Hooks (`hooks.json`)](#5-lifecycle-hooks-hooksjson)
   - [5.1 Hook Execution Mechanics & Locations](#51-hook-execution-mechanics--locations)
   - [5.2 Lifecycle Events Matrix (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`)](#52-lifecycle-events-matrix)
   - [5.3 Tool Matcher Syntax](#53-tool-matcher-syntax)
   - [5.4 Protocol Contract: Stdin & Stdout Payloads](#54-protocol-contract-stdin--stdout-payloads)
   - [5.5 Tool Argument Rewriting (`overwrite`) & Gating](#55-tool-argument-rewriting-overwrite--gating)
   - [5.6 Agent-Scoped Hooks (`hooks:` in Frontmatter)](#56-agent-scoped-hooks-hooks-in-frontmatter)
6. [Cutting-Edge Multi-Agent Orchestration Patterns](#6-cutting-edge-multi-agent-orchestration-patterns)
   - [6.1 Boost Deep Reasoning (`/boost`)](#61-boost-deep-reasoning-boost)
   - [6.2 Teamwork Agent Teams (`/teamwork-preview`)](#62-teamwork-agent-teams-teamwork-preview)
   - [6.3 Sidecars (`sidecar.json`) & Background Daemons](#63-sidecars-sidecarjson--background-daemons)
   - [6.4 The Sunset of Legacy Workflows & Migration to Skills](#64-the-sunset-of-legacy-workflows--migration-to-skills)
   - [6.5 Remote Control & Cross-Surface Steering (`antigravity.google.com`)](#65-remote-control--cross-surface-steering-antigravitygooglecom)
   - [6.6 Headless Execution & CI/CD Pipelines (`agy --headless`)](#66-headless-execution--cicd-pipelines-agy---headless)
   - [6.7 Plugin CLI Operations & Marketplace Sync](#67-plugin-cli-operations--marketplace-sync)
7. [Comprehensive Configuration Blueprint](#7-comprehensive-configuration-blueprint)

---

## 1. Platform State & 2.18.1 Innovations

Google Antigravity **2.18.1** (released September 28, 2026) establishes a robust, highly modular foundation for agent-first engineering. Key capabilities introduced in versions 2.15.0 through 2.18.1 include:

*   **Plugin Discovery & In-App Management (2.18.1):** A dedicated *Customizations Tab* and marketplace allow discovering, installing, enabling, and disabling plugins. Slash commands provided by plugins dynamically surface plugin attribution badges and hover metadata.
*   **Decoupled Multi-Tier Token Budgets (2.18.1):** Token usage is visually and mechanically broken down into separate budgets. Always-on rules operate against a dedicated **20,000-token rules budget (`defaultRulesBudget`)**, independent of the customization budget (skills, subagents, and MCP tools). Over-budget rules are demoted from full inline text to file path pointers with descriptions.
*   **Git Worktree Isolation Boundary (2.18.1):** Hardened isolation for subagents operating with `Workspace: "branch"`. Subagent Git worktrees are decoupled from conversation artifact directories to prevent accidental tracking or collision.
*   **Syntax-Highlighted Terminal Approvals (2.18.1):** Interactive permission prompts for terminal execution feature full syntax highlighting and collapsed-by-default execution telemetry.
*   **Agent-Scoped Lifecycle Hooks (2.17.0):** Markdown-defined agents can declare private hook files directly in their YAML frontmatter (`hooks:`), establishing agent-specific security boundaries.
*   **"Plan Before You Build" (`/plan`) & Review Policies (2.17.0):** Native integration for drafting structured implementation plans with configurable review policies (`review every plan`, `review when agent deems worthwhile`, or `skip review`).
*   **Centralized Configuration Migration (2.17.0):** Per-project repository customization settings are read exclusively from `<workspace>/.gemini/config.json`. Legacy `.agents/settings.json` has been formally retired.
*   **Live Subagent Cards & Telemetry (2.16.0):** Subagent runs render as interactive cards in conversation streams with real-time status badges (`running`, `waiting`, `completed`), instant stop controls, and single-click side-pane drilldowns.
*   **Native Office Document Ingestion (2.16.0):** Drag-and-drop ingestion of Microsoft Word (`.docx`), Excel (`.xlsx`), and PowerPoint (`.pptx`) documents into prompts, with native multi-modal model parsing.
*   **Modular Prompt & Tool Toggling (2.15.0):** Custom agents can selectively disable default system prompt blocks and default tools, exposing only explicitly declared capabilities.

---

## 2. Primary & Custom Agents

### 2.1 Architectural Pillars
Under the Antigravity architecture, every session is driven by three foundational components:
1.  **Agent:** Encapsulates the behavioral policy, system prompt, tool definitions, capabilities, sandbox rules, and lifecycle hooks.
2.  **Conversation:** The stateful session engine. Manages multi-turn conversation history, compaction, context budgeting, and event streaming.
3.  **Connection:** The transport layer to the model backend:
    *   `LocalConnectionStrategy`: Cloud connection to Gemini Developer API / Vertex AI / Gemini Enterprise.
    *   `LiteRTConnectionStrategy`: Local on-device execution via LiteRT-LM (e.g., Gemma 2/3 variants) with zero external network traffic.
    *   `LocalOpenAIConnectionStrategy`: Local connection to any OpenAI-compatible API (Ollama, vLLM, LM Studio).

### 2.2 Execution Modes & Sandboxing
Agents operate in two primary execution postures:
*   **Autonomous Mode (`AgentBehavior.AUTONOMOUS`):** Plans, executes tools, iterates on compiler/runtime errors, and verifies outputs independently without prompting for intermediate approvals.
*   **Interactive Mode (`AgentBehavior.INTERACTIVE`):** Leverages interactive primitives (e.g., `ask_question`) to clarify ambiguous requirements, confirm architectural choices, and pause before major operations.

#### Sandboxing & Permissions Presets (macOS / Linux)
Configured under **Settings → General → Permission Settings** or overridden per workspace in `.gemini/config.json`:
*   `Default`: Commands execute automatically inside the **Terminal Sandbox**. Commands escaping sandbox isolation require explicit user approval. File read/write is unrestricted within workspace and `/tmp`.
*   `Request Review`: Terminal sandbox is disabled; **every** terminal command requires user authorization.
*   `Turbo`: Unrestricted execution without sandboxing or approval prompts (for isolated container environments).

### 2.3 Custom Primary Agents
Custom primary agents are declared as Markdown files inside:
*   **Workspace:** `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md`
*   **Global:** `~/.gemini/config/agents/<name>.md`
*   **Plugins:** `plugins/<plugin_name>/agents/<name>.md`

When `mainAgent: true` is set, the agent appears in the Antigravity UI model/agent dropdown selector and can be launched via `/agents`.

### 2.4 Agent Frontmatter Specification

```yaml
---
name: security-architect
description: Senior Security Architect agent specialized in threat modeling, static analysis, and zero-trust verification.
role: Security Architect
tools:
  - view_file
  - run_command
  - replace_file_content
  - ask_question
mainAgent: true
subagent: true
model: pro
commandExecutionPolicy: sandbox
skills:
  - skills/threat-modeling
  - skills/cve-scanner
hooks:
  - ./hooks/security_audit_guard.py
mcpServers:
  - name: local-semgrep
    command: semgrep
    args: ["mcp"]
---

# Security Architect System Prompt

You are the Senior Security Architect for this repository. Your mission is to identify vulnerabilities, verify least-privilege configurations, and enforce defense-in-depth principles.

## Operational Directives
1. Never propose hardcoded credentials, JWT secrets, or insecure default tokens.
2. Run automated static security scanners (`semgrep`, `bandit`) before certifying code changes.
3. Every finding must be classified according to OWASP Top 10 and CVSS v3.1 severity metrics.
```

#### Frontmatter Parameter Reference
| Property | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | *(Required)* | Unique ASCII identifier (`^[a-zA-Z0-9_.-]+$`). |
| `description` | `string` | *(Required)* | Detailed description used by planners and routers for task delegation. |
| `role` | `string` | `name` | Human-readable role title displayed on live status badges and telemetry cards. |
| `tools` | `string[]` | `[]` | Explicit whitelist of enabled tools. If omitted, default tools are mounted. |
| `mainAgent` | `boolean` | `true` | Allows selecting this agent as the primary conversational agent. |
| `subagent` | `boolean` | `true` | Allows this agent to be invoked via `invoke_subagent`. |
| `model` | `string` | `inherit` | Model tier: `inherit`, `flash_lite`, `flash`, or `pro`. |
| `commandExecutionPolicy` | `string` | `sandbox` | Execution policy: `sandbox`, `auto`, `eager`, or `off`. |
| `skills` | `string[]` | `[]` | Specific skills pre-mounted into this agent's context. |
| `hooks` | `string[]` | `[]` | Agent-scoped lifecycle hook scripts (relative or absolute paths). |
| `mcpServers` | `object[]` | `[]` | Dedicated MCP server definitions bound exclusively to this agent. |

### 2.5 Modular Tool & Prompt Toggling
Antigravity allows custom agents to strip default system prompt segments (such as default persona instructions) and disable default tool bindings. By specifying an explicit `tools:` whitelist, developers can construct strictly read-only auditors, pure conductors without code-mutation privileges, or sandboxed database agents.

---

## 3. Subagents: Architecture, Creation & Management

### 3.1 Architectural Principles & Anti-Bloat Strategy
Subagents are semi-isolated, specialized workers spawned by a lead agent to execute focused tasks. They solve three fundamental engineering challenges:
1.  **Context Window Hygiene:** Extensive multi-step operations (running test suites, scanning hundreds of repository files, harvesting external literature) take place in an isolated context window, preventing prompt bloat and degradation in the primary conversation.
2.  **Epistemic Specialization:** Each subagent is provisioned with a dedicated persona, tailored tool permissions (e.g., read-only vs. code-mutation), and an appropriate model tier.
3.  **Concurrency & Throughput:** Multiple subagents execute concurrently in the background without blocking the developer's interactive chat loop.

### 3.2 The 10-Level Nesting Ceiling
To prevent uncontrolled runaway recursion, Antigravity enforces a strict physical ceiling of **10 nested subagent levels** (`Primary Agent → Subagent 1 → Subagent 2 ... → Subagent 10`). Attempts to spawn subagents beyond depth 10 fail-closed with a resource boundary error.

### 3.3 Paradigm A: Declarative Workspace Subagents
Subagents stored as `.agents/agents/<name>.md` with `subagent: true` can be invoked by name by the primary agent or peer agents.

### 3.4 Paradigm B: Dynamic Runtime Subagents
During runtime, the lead agent uses a specialized toolset to manage workers on the fly:

```
┌────────────────────────────────────────────────────────┐
│                   Lead Agent / UI                      │
└───────┬────────────────────┬───────────────────┬───────┘
        │                    │                   │
        ▼                    ▼                   ▼
 define_subagent      invoke_subagent     manage_subagents
 (Registers worker)   (Spawns execution)  (list | kill)
                             │
                             ▼
                    ┌─────────────────┐
                    │ Running Worker  │◄──── send_message
                    └────────┬────────┘      (Follow-up)
                             │
                             ▼
                    ┌─────────────────┐
                    │   Idle Worker   │────── Auto-wake on
                    └─────────────────┘       new message
```

#### Runtime Tool Definitions
1.  **`define_subagent`**: Dynamically creates a new subagent type in session memory:
    *   `name`: Unique subagent identifier.
    *   `description`: Instructions for when to invoke.
    *   `system_prompt`: Behavioral persona and operational instructions.
    *   `enable_write_tools` (`bool`): Grants `write_to_file`, `replace_file_content`, `run_command`.
    *   `enable_subagent_tools` (`bool`): Permits spawning further subagents.
    *   `enable_mcp_tools` (`bool`): Grants access to configured MCP servers.
2.  **`invoke_subagent`**: Spawns one or more subagents in the background:
    *   `TypeName`: The registered agent identifier (e.g. `research`, `code-auditor`, or custom).
    *   `Role`: Concise 2–5 word description of the assignment.
    *   `Prompt`: Actionable instructions for the worker.
    *   `Model`: `inherit`, `flash_lite`, `flash`, or `pro`.
    *   `Workspace`: `inherit`, `branch`, or `share`.
3.  **`manage_subagents`**: Administrative controller:
    *   `Action`: `list` (inspect live states, conversation IDs, transcripts), `kill` (terminate specific ID), `kill_all`.
4.  **`send_message`**: Sends instructions or queries to active or idle subagents using their unique `conversationId`.

### 3.5 Paradigm C: Programmatic Python SDK Subagents
When utilizing the `google-antigravity` Python SDK, subagent delegation graphs and recursion ceilings are defined programmatically:

```python
from google.antigravity import Agent, LocalAgentConfig, types

# 1. Define leaf worker (Read-only, no subagent spawning privileges)
linter_worker = types.SubagentConfig(
    name="linter_worker",
    description="Runs static code linters and outputs structured JSON diagnostics.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[types.BuiltinTools.RUN_COMMAND, types.BuiltinTools.VIEW_FILE],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

# 2. Define coordinator worker (Can view files and delegate to linter_worker)
qa_lead = types.SubagentConfig(
    name="qa_lead",
    description="Coordinates QA pipelines and static analysis passes.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[
            types.BuiltinTools.VIEW_FILE,
            types.BuiltinTools.START_SUBAGENT,
        ],
        allowed_subagents=["linter_worker"],
    ),
)

# 3. Configure root agent with hierarchical constraints
root_config = LocalAgentConfig(
    model="gemini-3.8-flash",
    subagents=[qa_lead, linter_worker],
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,
        max_subagent_depth=2,
        allowed_subagents=["qa_lead"],  # Root can only invoke qa_lead
    ),
)
```

### 3.6 Workspace Isolation Modes
When calling `invoke_subagent`, the `Workspace` parameter controls file system boundaries:
*   **`inherit` (Default):** The subagent executes directly in the parent workspace directory. Ideal for fast in-place reading, code edits, and linting.
*   **`branch`:** Antigravity creates an isolated Git worktree or branch. File modifications do not touch the active workspace files until explicitly reviewed and merged. In Antigravity 2.18.1, worktree storage is strictly decoupled from conversation logs.
*   **`share`:** Shares the underlying repository directory storage (similar to Mercurial `hg share`), allowing independent branching without duplicating object storage.

### 3.7 Subagent Lifecycle States & Auto-Wake Mechanics
Every subagent operates through standard lifecycle states:
*   `running`: Actively reasoning, emitting tool calls, or executing shell processes.
*   `idle`: Task complete; result emitted to parent. The subagent pauses execution while retaining its full conversation history.
*   `waiting_for_input`: Subagent triggered an approval prompt or question that bubbled up to the user.
*   `killed`: Subagent permanently terminated. Associated temporary worktrees are pruned immediately.
*   **Auto-Wake:** Sending a message to an `idle` subagent via `send_message` instantly re-awakens it to `running` with full conversational memory intact.

### 3.8 Monitoring, Teleporting (`Alt+J`) & Fast-Path Approvals (`Ctrl+K`)
*   **Live Subagent Cards:** In the Antigravity 2.0 chat canvas, active subagents display as interactive cards showing real-time tool calls and execution duration.
*   **`/agents` Command:** In the Antigravity CLI, typing `/agents` launches the interactive Agent Manager Panel showing all active, completed, or failed subagents with full detail views.
*   **Teleport (`Alt+J`):** Pressing `Alt+J` in the CLI instantly jumps your focus from the main thread into the subagent requiring tool authorization.
*   **Fast-Path (`Ctrl+K`):** Pressing `Ctrl+K` authorizes a pending subagent command directly from the main status bar without switching views.

---

## 4. Rules (`AGENTS.md`, `GEMINI.md` & Modular Rules)

### 4.1 Hierarchy & Scopes
Rules establish behavioral invariants, coding standards, and architectural constraints. They are cumulative and discovered by walking up the directory tree from the target file to the repository root:
1.  **Directory Rules:** `<subdir>/AGENTS.md` or `<subdir>/GEMINI.md` (Highest specificity).
2.  **Workspace Root Rules:** `<workspace>/AGENTS.md` or `<workspace>/GEMINI.md`.
3.  **Modular Workspace Rules:** `<workspace>/.agents/rules/*.md`.
4.  **Plugin Rules:** `plugins/<name>/rules/AGENTS.md`.
5.  **Global Rules:** `~/.gemini/AGENTS.md`, `~/.gemini/GEMINI.md`, or `~/.gemini/config/rules/*.md`.

### 4.2 Root Files vs. Modular Rule Files
*   **Standalone Root Files (`AGENTS.md`, `GEMINI.md`):** Do **NOT** use YAML frontmatter. The entire file content is loaded as Markdown and is continuously active (`always_on`) for its directory scope.
*   **Modular Rule Files (`.agents/rules/*.md`):** **MUST** begin with a valid YAML frontmatter block declaring a `trigger:`. Files omitting frontmatter or using invalid trigger casings (e.g. camelCase `alwaysOn`) are discarded.
*   **Flat Directory Restriction:** Antigravity scans only immediate `.md` children of `rules/`. Subdirectories (e.g., `rules/backend/db.md`) are ignored unless explicitly registered in `.agents/rules.json`.

### 4.3 Trigger Modes
Modular rules support four declarative activation triggers:

```yaml
---
trigger: model_decision
description: "Enforces strict SQL transaction safety and schema migration protocols."
globs: "*.sql, src/db/**/*.ts"
---

# Database Reliability Rules
1. Never run raw DDL migrations without transactional rollback blocks.
2. Require index coverage on all foreign key references.
```

| Trigger Mode | Required Fields | Context Behavior |
| :--- | :--- | :--- |
| `always_on` | None | Content is permanently loaded into the active prompt context. |
| `model_decision` | `description` | Progressive disclosure: Only the rule's path and description are injected into the prompt index. The model reads the full rule on demand when relevant. |
| `glob` | `globs` (or `glob`) | Activates automatically whenever the agent views or modifies a file matching the glob pattern (e.g., `"*.py, src/**/*.py"`). |
| `manual` | None | Inactive by default; invoked explicitly in chat using an `@rule-name` mention. |

### 4.4 Budgets, 24 KB File Cap & Demotion Protocol
*   **Dedicated 20,000-Token Rules Budget (`defaultRulesBudget`):** Always-on rules occupy a dedicated token reserve, ensuring large guidelines never displace skills or subagents.
*   **24 KB (24,000 Bytes) Per-File Cap:** Individual rule files must strictly remain under 24,000 bytes (after expanding includes). Oversized files are truncated at line boundaries.
*   **Demotion Protocol:** If aggregate `always_on` rules exceed the 20,000-token budget, Antigravity demotes excess rules from full inline text to file path pointers with descriptions, allowing the agent to read them on demand.

---

## 5. Lifecycle Hooks (`hooks.json`)

### 5.1 Hook Execution Mechanics & Locations
Lifecycle hooks are deterministic shell commands or scripts executed by the harness at exact checkpoints in the agent execution loop. They enforce hard guardrails that the LLM cannot bypass or hallucinate around.
*   **Workspace:** `.agents/hooks.json`
*   **Global:** `~/.gemini/config/hooks.json`
*   **Plugins:** `plugins/<plugin_name>/hooks.json`

### 5.2 Lifecycle Events Matrix

```
   ┌───────────────────────────────────────────────────────────┐
   │                    Agent Turn Begins                      │
   └─────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
                     [Event: PreInvocation]
                     (Inject ephemeral hints)
                                 │
                                 ▼
                         Model Invocation
                                 │
                                 ▼
                    [Event: PostInvocation]
                    (Inspect response / force continuation)
                                 │
               Tool Call Emitted? ◄───────┐
                     │ Yes                │ Next Tool
                     ▼                    │
            [Event: PreToolUse]           │
       (Gating / Argument Overwrite)      │
                     │                    │
                     ▼                    │
             Tool Executes                │
                     │                    │
                     ▼                    │
            [Event: PostToolUse]          │
         (Lint / Auto-format / Log)       │
                     │                    │
                     └────────────────────┘
                                 │ No More Tools
                                 ▼
                           [Event: Stop]
               (Block finish if tests not passed)
                                 │
                                 ▼
                            Turn Ends
```

| Lifecycle Event | Execution Point | Matcher Target | Scope & Primary Use Cases |
| :--- | :--- | :--- | :--- |
| `PreToolUse` | Immediately before a tool executes. | Tool name (regex). | Security gating (`decision: "deny"`), argument rewriting (`overwrite`), human authorization prompts (`ask`). |
| `PostToolUse` | Immediately after a tool finishes execution. | Tool name (regex). | Auto-formatting code (`prettier`, `black`), static lint checks, audit logging. |
| `PreInvocation` | Immediately before the model is called. | N/A (ignored). | Dynamic system prompt injection (`ephemeralMessage`), state synchronization. |
| `PostInvocation`| Immediately after model output arrives. | N/A (ignored). | Guarding completion, enforcing turn continuation (`terminationBehavior: "force_continue"`). |
| `Stop` | When the agent execution loop terminates. | N/A (ignored). | Mechanical exit gate: Prevents agent completion if tests fail (`decision: "continue"`). |

### 5.3 Tool Matcher Syntax
For `PreToolUse` and `PostToolUse`, handlers are grouped under a `matcher` regular expression:
*   `"matcher": "*"` or `""`: Matches all tools.
*   `"matcher": "run_command"`: Matches only shell execution.
*   `"matcher": "write_to_file|replace_file_content"`: Matches file modification tools.
*   `"matcher": "browser_.*"`: Matches all browser automation tools.

### 5.4 Protocol Contract: Stdin & Stdout Payloads
Hooks communicate strictly via JSON over standard streams using **`camelCase`** (protojson) keys. The working directory is the directory containing `hooks.json`.

#### Common Input Payload (`stdin`)
```json
{
  "conversationId": "801bc7ea-5feb-44bd-ad55-00799869f233",
  "workspacePaths": ["${WORKSPACE_ROOT}"],
  "transcriptPath": "${APP_DATA_DIR}/antigravity/brain/801bc7ea/transcript.jsonl",
  "artifactDirectoryPath": "${APP_DATA_DIR}/antigravity/brain/801bc7ea",
  "modelName": "gemini-3.8-flash"
}
```

#### 1. `PreToolUse` Specification
*   **Input (`stdin`):**
    ```json
    {
      "toolCall": {
        "name": "run_command",
        "args": {
          "CommandLine": "rm -rf /tmp/data",
          "Cwd": "${WORKSPACE_ROOT}"
        }
      },
      "stepIdx": 14,
      "conversationId": "..."
    }
    ```
*   **Output (`stdout`):**
    ```json
    {
      "decision": "deny",
      "reason": "Destructive deletion command blocked by security hook policy."
    }
    ```
    *   `decision` (`string`, required): `"allow"`, `"deny"`, `"ask"` (prompts user), or `"force_ask"`.
    *   `reason` (`string`, optional): User-facing explanation.
    *   `overwrite` (`object`, optional): Top-level shallow merge into tool arguments.

#### 2. `Stop` Specification
*   **Input (`stdin`):**
    ```json
    {
      "executionNum": 1,
      "terminationReason": "model_stop",
      "error": "",
      "fullyIdle": true,
      "conversationId": "..."
    }
    ```
*   **Output (`stdout`):**
    ```json
    {
      "decision": "continue",
      "reason": "Deliverable validation failed: validation_report.json reports overall_verdict == FAIL. Re-enter loop and resolve defects."
    }
    ```
    *   `decision`: `"continue"` forces the agent to re-enter the loop. Any other value allows the agent to terminate normally.

### 5.5 Tool Argument Rewriting (`overwrite`) & Gating
`PreToolUse` hooks can rewrite tool arguments before execution. If a hook specifies:
```json
{
  "decision": "allow",
  "overwrite": {
    "CommandLine": "pytest tests/ --maxfail=1"
  }
}
```
The original tool call is replaced with the modified arguments, and the tool output in the transcript is prefixed with a notice notifying the agent that a hook modified the parameters.

### 5.6 Agent-Scoped Hooks (`hooks:` in Frontmatter)
As of Antigravity 2.17.0, custom agents defined in Markdown can specify agent-scoped hooks directly in YAML frontmatter:
```yaml
---
name: backend-engineer
hooks:
  - ./hooks/enforce_branch_safety.py
  - /etc/antigravity/global_guard.py
---
```
These hooks execute exclusively when this specific agent is active, allowing custom verification routines per agent persona.

---

## 6. Cutting-Edge Multi-Agent Orchestration Patterns

### 6.1 Boost Deep Reasoning (`/boost`)
*Plan availability: Google One AI Premium (Pro/Ultra) & Enterprise.*  
Launching `/boost` activates a three-tier reasoning hierarchy:
1.  **Lead Orchestrator:** Decomposes difficult problems, synthesizes counter-hypotheses, and assigns exploration subtasks.
2.  **DeepCoder / DeepInvestigator Coordinators:** Parallel agents exploring solution spaces and evaluating edge cases.
3.  **Execution Workers:** Isolated background workers testing code against deterministic unit tests and benchmarks.

### 6.2 Teamwork Agent Teams (`/teamwork-preview`)
*Plan availability: All paid plans.*  
Designed for multi-day, multi-file software engineering, distributed systems simulations, and theoretical proofs.

```
                  ┌───────────────────────────────┐
                  │       User Prompt / Goal      │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                   Phase 1: Scoping Interview
                   (Specify WHAT, Not HOW)
                                  │
                                  ▼
                        [Prompt Artifact]
                                  │ User Approval
                                  ▼
                  ┌───────────────────────────────┐
                  │           Sentinel            │
                  │    (Top-Level Coordinator)    │
                  └───────────────┬───────────────┘
                                  │
                                  ▼
                  ┌───────────────────────────────┐
                  │      Project Orchestrator     │
                  │  (Successor per Milestone)    │
                  └───────┬───────────────┬───────┘
                          │               │
            ┌─────────────┴─────┐   ┌─────┴─────────────┐
            ▼                   ▼   ▼                   ▼
       [Explorers]          [Workers]                [Critic]
       (Read-only)      (File Owners)            (Code Quality)
                                │                       │
                                └───────────┬───────────┘
                                            │
                                            ▼
                                      [Challenger]
                                  (Adversarial Tests)
                                            │
                                            ▼
                                        [Auditor]
                                    (Integrity Mode)
                                            │
                                            ▼
                                    [Success Auditor]
                                (End-to-End Release Gate)
```

#### Team Roles & Responsibilities
*   **Sentinel:** Manages session continuity, posts periodic progress updates, handles crash recoveries, and invokes the final Success Auditor.
*   **Project Orchestrator:** Breaks briefs into milestones. **Successor Handoff:** Between milestones, the orchestrator terminates itself and hands off state to a fresh successor orchestrator to maintain zero context degradation.
*   **Explorers:** Read-only analysis agents tracing call chains and researching APIs without touching project files.
*   **Workers:** Implementation agents with **exclusive file ownership**. Two workers never modify the same file concurrently.
*   **Adversarial Verification Quadrant:**
    *   `Critic`: Evaluates code style, architectural conformance, and readability.
    *   `Challenger`: Constructs adversarial stress tests, edge cases, and memory-limit probes.
    *   `Auditor`: Verifies that test passes are genuine and checks command exits against real logs.
    *   `Success Auditor`: Independent end-to-end evaluation before final handoff.

#### Integrity Modes
*   `development`: Lenient mode. Permits open-source reuse, external libraries, and pre-built utilities.
*   `demo`: Moderate mode. Forbids copying core logic from external repositories; prevents reading test code to reverse-engineer expected answers.
*   `benchmark`: Maximum strictness. Standard library only; zero external scaffolding; ground-truth evaluation against real systems.

### 6.3 Sidecars (`sidecar.json`) & Background Daemons
Sidecars are managed background processes running alongside Antigravity:
*   **Locations:** `~/.gemini/config/sidecars/<sidecarId>/sidecar.json` or within plugin `sidecars/`.
*   **Schema:**
    ```json
    {
      "command": "python3",
      "args": ["health_monitor.py"],
      "restart_policy": "always",
      "description": "Continuous service health monitor and metric collector."
    }
    ```
*   `restart_policy`: `"always"`, `"on-failure"`, or `"never"`.

### 6.4 The Sunset of Legacy Workflows & Migration to Skills
Single-file legacy workflows (`.agents/workflows/*.md`) are formally **deprecated** and will be permanently decommissioned on **November 1, 2026**.
*   **Why Skills Replaced Workflows:** Skills conform to the Agent Skills Standard (`agentskills.io`), feature semantic discovery, support multi-file encapsulation (`scripts/`, `references/`, `resources/`), and integrate with context budgeting.
*   **Migration Tooling:** Running `/migrate-workflows` automatically parses legacy workflow files, converts them into valid `.agents/skills/<name>/SKILL.md` structures, and archives legacy files as `.md.bak`.

### 6.5 Remote Control & Cross-Surface Steering (`antigravity.google.com`)
Antigravity 2.18.1 provides native web-based **Remote Control** (`https://antigravity.google.com`):
*   **Decoupled Web Monitoring:** Developers can monitor, steer, and interact with long-running desktop and CLI agent sessions from any mobile or desktop web browser.
*   **Zero Environment Duplication:** The remote interface connects directly to your workstation's running agent instance, leveraging local toolchains, terminals, and Git worktrees without cloning code to remote servers.
*   **Remote Permission Approvals:** Interactive tool authorization requests and question prompts stream live to the remote interface, allowing approvals from outside your desk.

### 6.6 Headless Execution & CI/CD Pipelines (`agy --headless`)
For automated build pipelines, GitHub Actions, and headless remote server management:
*   **Headless Mode:** `agy --headless -p "Execute test suite and generate validation_report.json"` runs the agent autonomously to completion without opening interactive TUI prompts.
*   **Structured Stream Logs:** Emits JSONL step transcripts directly to standard output or specified log targets for CI pipeline ingestion.
*   **Fail-Closed Exit Codes:** Non-zero exit codes trigger automatically when `Stop` hooks reject completion or unhandled tool failures occur.

### 6.7 Plugin CLI Operations & Marketplace Sync
Plugins can be managed directly from the CLI or IDE settings:
*   `agy plugin list`: Enumerate all workspace, global, and built-in plugins with enabled/disabled status.
*   `agy plugin install <plugin-id>`: Install plugins directly from the marketplace into `~/.gemini/config/plugins/` or `.agents/plugins/`.
*   `agy plugin enable <name>` / `agy plugin disable <name>`: Toggle plugins across workspace and global configurations without modifying plugin source files.
*   **Cross-Surface Synchronization:** Plugins installed in the Antigravity 2.0 desktop app are automatically recognized and mounted in the Antigravity CLI and IDE surfaces.


---

## 7. Comprehensive Configuration Blueprint

Below is an enterprise-grade `.agents/hooks.json` incorporating tool gating, argument rewriting, automated linting, and a fail-closed mechanical verification completion gate:

```json
{
  "security-firewall": {
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/scripts/security_firewall.py",
            "timeout": 15
          }
        ]
      }
    ]
  },
  "code-formatter": {
    "PostToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/scripts/auto_format.py",
            "timeout": 20
          }
        ]
      }
    ]
  },
  "deliverable-validation-gate": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 .agents/scripts/mechanical_stop_gate.py",
        "timeout": 30
      }
    ]
  }
}
```

#### Companion Mechanical Stop Script (`mechanical_stop_gate.py`)
```python
#!/usr/bin/env python3
"""
Mechanical Stop Hook Gate (Fail-Closed)
Verifies physical deliverable existence and audit reports before agent exit.
"""
import sys, json, os

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Check for active verification reports
    report_path = os.path.join(payload.get("artifactDirectoryPath", ""), "validation_report.json")
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            if report.get("overall_verdict") != "PASS" or report.get("checks_failed", 0) > 0:
                print(json.dumps({
                    "decision": "continue",
                    "reason": f"Gate Refusal: validation_report.json reports {report.get('checks_failed')} failures. Correct issues before concluding."
                }))
                sys.exit(0)
        except Exception as e:
            print(json.dumps({"decision": "continue", "reason": f"Validation parse error: {e}"}))
            sys.exit(0)

    # Allow clean exit
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
```
