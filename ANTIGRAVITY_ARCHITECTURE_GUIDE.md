# Google Antigravity Architecture & Customization Guide
**Agents, Subagents, Skills, and Workflows**  
*Document Version: 2026.09.16 | Operative Date: September 16, 2026*

---

## Executive Summary & System Overview

**Google Antigravity (AGY)** is an agent-first software development and research platform designed to orchestrate autonomous AI agents across codebases, developer tools, terminals, and web environments. Operating on a **Plan → Execute → Verify** cognitive loop, Antigravity enables complex multi-step workflows to run either interactively with human developers or fully autonomously.

As of late 2026, Antigravity provides four primary development surfaces:
1. **Antigravity 2.0 Desktop Application**: An Electron-based command center for multi-agent orchestration, workspace management, scheduled tasks (cron/timers), and real-time artifact inspection.
2. **Antigravity IDE**: Standalone or extension-based environment (e.g., VS Code integration) featuring inline code lenses, diff reviews, and context-aware chat sidebars.
3. **Antigravity CLI (`agy`)**: A lightweight, terminal-native text user interface (TUI) optimized for local development and headless remote SSH sessions.
4. **Google Antigravity Python SDK (`google-antigravity`)**: A programmatic framework allowing developers to instantiate, configure, and orchestrate agents and multi-tier subagent hierarchies in code.

A major architectural evolution in 2026 is the consolidation of the customization system: **Agent Skills** have formally replaced legacy **Workflows** (which are scheduled for complete sunset on November 1, 2026). This guide provides the complete, authoritative reference for creating and managing **Agents**, **Subagents**, **Skills**, and **Workflows** within the Antigravity ecosystem.

---

## 1. Primary Agents

### 1.1 Core Architecture & Pillars

Every Antigravity session is anchored by a **Primary Agent** (also referred to as the Lead Agent or Orchestrator). In the underlying architecture (such as the Python SDK), three foundational pillars govern execution:

*   **Agent**: The configuration and policy interface. It manages models, tools, capabilities, system instructions (personas), security sandbox policies, and lifecycle hooks.
*   **Conversation**: The stateful session engine. It maintains turn history, aggregates multi-step tool calls, controls context window compaction, and handles streaming interactions.
*   **Connection**: The transport layer to the model backend. Antigravity supports multiple connection strategies:
    *   `LocalConnectionStrategy`: Connects to Google AI Studio / Gemini Developer API or Gemini Enterprise Agent Platform (formerly Vertex AI).
    *   `LiteRTConnectionStrategy`: Runs models locally on-device using LiteRT-LM (e.g., Gemma 2/3 variants) with zero external network calls.
    *   `LocalOpenAIConnectionStrategy`: Connects to any local OpenAI-compatible inference server (such as Ollama, LM Studio, or vLLM).

### 1.2 Agent Configuration & Behavioral Modes

In both configuration files and the SDK, agents support two primary execution modes:
*   **Autonomous Mode (`AgentBehavior.AUTONOMOUS`)** *(Default)*: The agent acts autonomously from start to finish. It plans, invokes tools, resolves errors, and verifies its own outputs without prompting the user for approval at every minor step.
*   **Interactive Mode (`AgentBehavior.INTERACTIVE`)**: Collaborative mode. The agent utilizes interactive tools (e.g., `ask_question`) to prompt the user for requirements clarification, solicit design decisions, and pause before executing high-impact actions.

#### Python SDK Agent Configuration Example
```python
from google.antigravity import Agent, LocalAgentConfig, types

# Configure a primary agent with custom persona, budget controls, and interactive mode
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
    app_data_dir="/absolute/path/to/custom/storage",  # Absolute path override for artifacts/brain
)

async def main():
    async with Agent(config=config) as agent:
        response = await agent.chat("Analyze the system architecture and propose an implementation plan.")
        print(await response.text())
```

### 1.3 Permissions, Security & Sandboxing

Antigravity implements granular security and tool execution policies at both global (`~/.gemini/antigravity/`) and project levels (`.agents/`):
*   **Tool Execution Policy**:
    *   `always-proceed`: Executes terminal commands automatically.
    *   `request-review`: Requires explicit human approval before running commands.
    *   `strict`: Denies destructive or untrusted commands.
    *   `proceed-in-sandbox`: Runs all shell commands in a restricted terminal sandbox.
*   **File Access Policy**: `allow`, `ask`, or `deny` access to files outside the workspace root.
*   **Internet Access Policy**: Controls whether web search, URL fetching, or external HTTP requests are permitted.
*   **Allowlist / Denylist**: Regex patterns for permissible commands, domains, and filesystem paths.

---

## 2. Subagents

### 2.1 Concept & Purpose of Subagents

Subagents are specialized, semi-isolated AI worker agents spawned by the primary agent to handle specific subtasks. Spawning subagents offers three critical architectural advantages:
1. **Context Window Hygiene**: Complex research, test runs, or repetitive file scans run in isolated contexts, preventing token bloat in the primary conversation.
2. **Role Specialization**: Subagents can be provisioned with specialized system prompts, tailored tool permissions (e.g., read-only vs. full write access), and specific model tiers.
3. **Parallelism & Delegation**: Multiple subagents can run concurrently to inspect different services or implement parallel features.

Subagents operate under a maximum recursion depth (up to 10 layers, configurable via `max_subagent_depth`) and inherit security boundaries from the parent agent.

### 2.2 Methods for Creating Subagents

Antigravity supports three distinct paradigms for defining and invoking subagents:

#### Paradigm A: Declarative Workspace Subagents (`.agents/agents/<name>.md`)
In an Antigravity project workspace, subagents can be defined declaratively as Markdown files with YAML frontmatter inside `.agents/agents/` (or `.agent/agents/`, `_agents/agents/`).

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

**Frontmatter Specification:**
*   `name` (string, required): Lowercase identifier used when invoking the subagent.
*   `description` (string, required): Explains what the subagent does and when the lead agent should delegate to it.
*   `role` (string, optional): Display title (e.g., "Codebase Researcher", "Database Debugger").
*   `skills` (list of strings, optional): Pre-assigned skills automatically mounted into this subagent's context.

#### Paradigm B: Dynamic Runtime Subagents (Antigravity Tools)
During an ongoing session, the lead agent can define and invoke subagents on the fly using built-in agent management tools:

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `define_subagent` | `name`, `description`, `system_prompt`, `enable_write_tools`, `enable_subagent_tools`, `enable_mcp_tools` | Dynamically registers a new subagent type for the remainder of the session. |
| `invoke_subagent` | `Subagents` array: `TypeName`, `Role`, `Prompt`, `Model`, `Workspace` | Spawns one or more subagents concurrently in the background. |
| `manage_subagents` | `Action` (`list`, `kill`, `kill_all`), `ConversationIds` | Inspects live states (`running`, `idle`, `errored`) or terminates subagent executions. |
| `send_message` | `Recipient` (conversation ID), `Message` | Sends follow-up instructions or queries to an active or idle subagent. |

**Runtime Invocation Parameters (`invoke_subagent`):**
*   `TypeName`: The registered name of the subagent (e.g., `research`, `code-reviewer`, or a custom name).
*   `Role`: Brief 2–5 word description of the assignment.
*   `Prompt`: Actionable instructions for the subagent.
*   `Model`:
    *   `inherit` *(Default)*: Inherits the parent's model.
    *   `flash_lite`: Lightweight model for high-speed, cost-efficient filtering or lookups.
    *   `flash`: Balanced model for standard research, file reading, or script running.
    *   `pro`: High-reasoning model for complex refactoring, mathematical proofs, or architecture design.
*   `Workspace`:
    *   `inherit` *(Default)*: Operates in the same directory as the parent.
    *   `branch`: Creates an isolated workspace branched/cloned from the parent.
    *   `share`: Shares the underlying repository via worktree/share mechanics.

#### Paradigm C: Programmatic Subagents in the Python SDK
When building custom agentic systems with `google-antigravity`, subagents and delegation graphs are declared using `SubagentConfig` and `SubagentCapabilities`:

```python
from google.antigravity import Agent, LocalAgentConfig, types

# 1. Define a leaf-tier fact-checker (Read-only, cannot spawn subagents)
fact_checker = types.SubagentConfig(
    name="fact_checker",
    description="Verifies claims against internal data.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[types.BuiltinTools.VIEW_FILE],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

# 2. Define an intermediary lead-researcher (Can view files and delegate to fact_checker)
lead_researcher = types.SubagentConfig(
    name="lead_researcher",
    description="Conducts deep domain research and delegates verification.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[
            types.BuiltinTools.VIEW_FILE,
            types.BuiltinTools.START_SUBAGENT,
        ],
        allowed_subagents=["fact_checker"],
    ),
)

# 3. Configure root agent with hierarchical depth ceiling
root_config = LocalAgentConfig(
    subagents=[lead_researcher, fact_checker],
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,
        max_subagent_depth=3,             # Session-wide recursion depth ceiling
        allowed_subagents=["lead_researcher"],  # Root can only call lead_researcher
    ),
)
```

---

## 3. Skills (Agent Skills Specification)

### 3.1 What are Skills?

**Skills** are modular packages of procedural knowledge, runbooks, executable scripts, and reference documents that extend an agent's capabilities. Formally conforming to the [Agent Skills Standard](https://agentskills.io), skills provide:
*   **Context Cheat Sheets**: Direct, unambiguous domain instructions that prevent model hallucinations.
*   **Progressive Disclosure**: Only skill names and descriptions are loaded into the initial context window. The complete instructions (`SKILL.md`) are fetched on-demand only when triggered by user prompt or explicit slash command.
*   **First-Class Slash Commands**: Any skill named `my-skill` automatically registers a slash command `/<my-skill>` in the Antigravity UI.
*   **Multi-File Encapsulation**: Skills can include helper scripts ("The Hands"), reference documentation, and static templates.

### 3.2 Directory Structure & File Hierarchy

A valid Antigravity skill must be placed in a `skills/` directory and structured as follows:

```text
skills/<skill-name>/
├── SKILL.md            # [REQUIRED] Main instruction file with YAML frontmatter
├── scripts/            # [OPTIONAL] Deterministic Python, Bash, or Node helper scripts
├── references/         # [OPTIONAL] Deep documentation, API manuals, and extended specs
├── examples/           # [OPTIONAL] Reference implementations and exemplar outputs
└── resources/          # [OPTIONAL] Static assets, templates, or seed files
```

### 3.3 Skill Instruction File Anatomy (`SKILL.md`)

The entrypoint file `SKILL.md` consists of a mandatory YAML frontmatter header followed by standard Markdown body instructions:

```markdown
---
name: data-pipeline-runner
description: Validates, cleans, and runs ETL data pipelines on incoming CSV and Parquet files. Use when the user requests data ingestion or pipeline verification.
---

# Data Pipeline Runner

This skill guides the agent through validating raw datasets and executing the deterministic ETL pipeline.

## Execution Sequence

1. **Schema Pre-Check**:
   Run the schema validator script:
   `python3 .agents/skills/data-pipeline-runner/scripts/validate_schema.py --input <path/to/data>`

2. **Pipeline Execution**:
   If validation passes, execute the transformation:
   `python3 .agents/skills/data-pipeline-runner/scripts/run_etl.py --config config.json`

3. **Verification**:
   Inspect the generated `output/summary.json` and report record counts and anomalous rows.

## References
For full database schema specifications, consult [references/schema_guide.md](references/schema_guide.md).
```

#### Critical Rules for `SKILL.md`:
1. **`name`**: Must be lowercase, hyphenated, and match the directory name.
2. **`description`**: The single most critical piece of text. The primary agent scans this description during routing to decide whether to activate the skill. It should clearly declare **what** the skill does and **under what conditions** to use it.
3. **Single-View Context Ceiling**: To prevent context window saturation, `SKILL.md` should remain concise (recommended: $\le 500$ lines, $\le 40$ KB). Bulky reference tables, schemas, or lengthy exemplars must be placed in `references/` and linked via relative markdown links.
4. **Executable Separation ("Hands vs. Brains")**: Complex calculations, statistical tests, or OpenXML generation should not be performed mentally by the LLM. Instead, package them as deterministic scripts in `scripts/` that the agent executes via `run_command`.

### 3.4 Discovery Locations & Precedence

Antigravity discovers skills across three hierarchical levels:

1. **Workspace Project**:
   *   Path: `.agents/skills/` (or `.agent/skills/`, `_agents/skills/`, `_agent/skills/`)
   *   Highest precedence. Overrides global or built-in skills with the same name. Can be checked into git to share with team members.
2. **Explicit Manifest (`skills.json`)**:
   *   Allows referencing skills stored outside default paths or inheriting from shared directories.
3. **Global Machine Configuration**:
   *   Path: `~/.gemini/config/skills/`
   *   Available to all workspaces and sessions on the local machine.
4. **Built-in System Skills**:
   *   Default skills bundled with Antigravity (e.g., `antigravity-guide`, `migrate-workflows`, `generative_ui`).

---

## 4. Workflows (Legacy System & Migration)

### 4.1 Historical Role of Workflows

In earlier releases of Antigravity, **Workflows** were standalone Markdown files stored in:
*   Workspace: `.agents/workflows/<workflow-name>.md`
*   Global: `~/.gemini/config/workflows/<workflow-name>.md`
*   Manifest: `workflows.json`

Workflows functioned as predefined prompt templates or procedural recipes for repeatable tasks (such as PR review checklists, release runbooks, or deployment instructions).

### 4.2 Deprecation & Sunset Timeline (2026)

In mid-2026, the Antigravity architecture transitioned to the unified **Agent Skills Standard**:
*   **Status**: Legacy Workflows are formally **deprecated**.
*   **Sunset Date**: Complete retirement takes effect on **November 1, 2026**.
*   **Why Skills Replaced Workflows**:
    *   *Semantic Discovery*: Workflows required the user to know and manually trigger the workflow via slash commands. Skills are semantically discovered by the LLM based on user intent.
    *   *Multi-File Capabilities*: Workflows were restricted to single `.md` files, whereas skills encapsulate scripts (`scripts/`), reference manuals (`references/`), and templates (`resources/`).
    *   *Context Management*: Skills natively integrate with progressive disclosure and context budgeting.

### 4.3 Automated Migration via `/migrate-workflows`

Antigravity provides an automated migration skill (`migrate-workflows`) that safely transitions legacy workflows to modern skills:

1. **Invocation**: Type `/migrate-workflows` in the chat canvas or CLI.
2. **Discovery**: Scans workspace and global directories for `.agents/workflows/*.md` and `workflows.json`.
3. **Conversion**:
   *   Extracts existing frontmatter or title.
   *   Creates `.agents/skills/<name>/SKILL.md` with standardized YAML frontmatter (`name` and `description`).
   *   Preserves all operational instructions and guidelines.
   *   Applies overwrite protection (does not overwrite existing skills).
4. **Safe Archiving**: Renames the legacy `.md` workflow file to `<name>.md.bak` rather than deleting it.

```text
Migration Mapping:
.agents/workflows/deploy.md  ──►  .agents/skills/deploy/SKILL.md
                                  .agents/workflows/deploy.md.bak (Archived)
```

### 4.4 Conceptual Workflows in Modern Multi-Agent Architecture

While single-file *legacy workflow files* are deprecated, **conceptual multi-agent workflows** remain fundamental to Antigravity. In modern systems, multi-stage pipelines are structured through **Artifact-Gated Stages**:
*   **Stage Checkpoints**: Each pipeline stage produces a deterministic artifact on disk (e.g., `data_scored.xlsx`, `stats_results.json`, `audit_report.json`).
*   **Strict Hand-Offs**: Subsequent stages cannot proceed until upstream checkpoint artifacts exist and are validated.
*   **Adversarial Critic Gates**: Generation and auditing are separated. A generator subagent (e.g., `academic-writer`) drafts content, which must be approved by an independent auditor subagent (e.g., `results-auditor`) before final release.

---

## 5. Ecosystem Customizations: Rules, Hooks, and Plugins

To complete the Antigravity customization landscape, three complementary mechanisms work alongside Agents, Subagents, and Skills:

### 5.1 Workspace & Project Rules (`AGENTS.md` / `GEMINI.md`)

Rules enforce behavioral invariants, coding standards, and project constraints:
*   **File Locations**: Placed at repository root or inside subdirectories as `AGENTS.md` or `GEMINI.md`.
*   **Hierarchical Scope**: When the agent operates on a file, it walks up the directory tree to the project root, loading all rules in scope.
*   **Deduplication**: Rules are deduplicated by canonical file path and injected once per turn.

### 5.2 Lifecycle Hooks (`hooks.json`)

Hooks allow executing shell scripts at deterministic points in the agent's execution loop:
*   **Location**: `.agents/hooks.json` (or `~/.gemini/config/hooks.json`).
*   **Execution**: Hooks communicate via JSON on `stdin` and `stdout` using protojson `camelCase` keys.

| Hook Event | Trigger Point | Use Cases |
| :--- | :--- | :--- |
| `PreToolUse` | Before a tool executes | Security gates, blocking unsafe commands (`decision: "deny"`), argument rewriting (`overwrite`). |
| `PostToolUse` | After a tool finishes | Auto-formatting code, running linters, logging. |
| `PreInvocation` | Before the LLM is called | Injecting ephemeral system instructions or dynamic reminders. |
| `PostInvocation` | After LLM tool calls finish | Forcing turn continuation (`terminationBehavior: "force_continue"`). |
| `Stop` | When the agent execution loop ends | Machine-guarding completion; preventing agent exit if tests fail (`decision: "continue"`). |

#### Example: `.agents/hooks.json`
```json
{
  "safety-guard": {
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "./scripts/verify_command_safety.sh",
            "timeout": 15
          }
        ]
      }
    ]
  },
  "completion-gate": {
    "Stop": [
      {
        "type": "command",
        "command": "python3 .agents/verification/completion_guard.py",
        "timeout": 30
      }
    ]
  }
}
```

### 5.3 Plugins (`plugin.json`)

Plugins are shareable, distributable bundles packaging skills, rules, hooks, and MCP servers into a single directory (`plugins/<plugin-name>/`):
*   `plugin.json`: Manifest file declaring the plugin name.
*   `skills/`: Packaged skills.
*   `rules/AGENTS.md`: Bundled rules.
*   `hooks.json`: Bundled lifecycle hooks.
*   `mcp_config.json`: Bundled Model Context Protocol server configurations.

---

## 6. Summary Comparison Matrix

| Component | Primary Location | Activation Mechanism | Key Purpose |
| :--- | :--- | :--- | :--- |
| **Primary Agent** | IDE / CLI / SDK Config | Started on session launch | High-level goal decomposition, orchestration, and user interaction. |
| **Subagent** | `.agents/agents/<name>.md` or runtime tools | Delegated by Primary Agent via `invoke_subagent` | Isolated, domain-specific execution (research, testing, auditing) with independent context. |
| **Skill** | `.agents/skills/<name>/SKILL.md` | Semantic intent discovery or slash command `/<name>` | Modular procedural runbook with progressive disclosure and helper scripts. |
| **Legacy Workflow** *(Deprecated)* | `.agents/workflows/<name>.md` | Manual slash command | Legacy prompt template; superseded by Skills (sunset Nov 1, 2026). |
| **Rule** | `AGENTS.md` / `GEMINI.md` | Contextual / Directory walk | Project-wide behavioral constraints, coding standards, and ethical directives. |
| **Hook** | `.agents/hooks.json` | Agent lifecycle events | Deterministic external shell scripts guarding tool calls and turn termination. |
| **Plugin** | `.agents/plugins/<name>/` | Config enablement | Distributable bundle combining skills, rules, hooks, and MCP servers. |

---

## 7. Hands-on Implementation Walkthrough

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
*   The primary agent will detect the subagent, invoke it with `TypeName: "qa-engineer"`, and mount the `test-runner` skill into the subagent's execution context.
