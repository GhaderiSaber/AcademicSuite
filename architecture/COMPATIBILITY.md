# AcademicSuite — Antigravity Compatibility Specification

**Document Version:** 1.0.0 (Compatibility Standard)  
**Operative Date:** September 2026 (1405 SH)  
**Compatibility Target:** Google Antigravity 2.0+ (2026.x Releases)  

---

## 🏛️ Foundational Architectural Rule
> **From this point forward: No new agent, Skill, framework, or orchestration abstraction is added unless it fills a documented architectural gap.**  
> **This prevents AcademicSuite from continuing to grow horizontally.**

---

## 1. Antigravity Compatibility Boundary

AcademicSuite maintains a minimal, zero-friction compatibility layer with Google Antigravity:
```text
AcademicSuite Agent Specification
               │
               ▼
   Antigravity-Compatible Markdown
               │
               ▼
Antigravity Native Discovery & Execution
```
AcademicSuite does **not** attempt to wrap or replace Antigravity's agent runtime. It provides structured Markdown instructions, skills, contracts, and deterministic scripts executed directly by Antigravity tools.

---

## 2. Agent Discovery Specification

Antigravity automatically discovers workspace agents by traversing the `.agents/agents/` directory at the project root.

### 2.1 Supported File Layouts
An agent is discoverable if placed in either of two locations:
1. **Directory-Based Packaging (Recommended)**:
   ```text
   .agents/agents/<agent-name>/agent.md
   ```
2. **Flat File Packaging**:
   ```text
   .agents/agents/<agent-name>.md
   ```

*Note: In AcademicSuite, all canonical agents reside in directory form (`<agent-name>/agent.md`), with symlinks (`<agent-name>.md`) maintained strictly for backward compatibility.*

### 2.2 Frontmatter Schema

#### Minimal Agent Contract
The minimal valid agent requires only `name` and `description`:
```yaml
---
name: statistical-auditor
description: Adversarial auditor for statistical assumptions, degrees of freedom, and MSAI scoring.
---
```

#### Complete Supported Frontmatter Schema
```yaml
---
name: string                   # Required. Lowercase ASCII kebab-case ([a-z0-9_-]+). Must match folder name.
description: string            # Required. Actionable description of agent role and delegation triggers.
role: string                   # Optional. Human-readable display role or title.
model: string                  # Optional. Model tier: 'inherit', 'pro', 'flash', 'flash_lite'.
mainAgent: boolean             # Optional. Defaults to false. If true, appears in primary chat agent selector.
subagent: boolean              # Optional. Defaults to true. If true, callable via invoke_subagent.
tools: list[string]            # Optional. List of enabled Antigravity tools.
skills: list[string]           # Optional. List of skills mounted into this agent's context.
agents: list[string]           # Optional. List of subagents this agent is permitted to delegate to.
mcpServers: list[string]       # Optional. List of mounted MCP servers.
inheritCustomizations: boolean # Optional. If true, inherits workspace plugins and global customizations.
---
```

#### Strictly Prohibited Frontmatter Fields
- ❌ `commandExecutionPolicy` / `command_execution_policy`: **Causes Antigravity agent loader to drop the agent silently.**
- ❌ `runtime`: Unsupported.
- ❌ Custom Python class paths: Unsupported.

---

## 3. Tool Whitelist & Compatibility

Antigravity agent definitions must reference only valid built-in tools. Referencing invalid or misspelled tool names causes subagent execution errors during task dispatch.

### 3.1 Supported Antigravity Tools
| Tool Name | Purpose | Execution Type |
|---|---|---|
| `view_file` | Read files and inspection | Read-only |
| `write_to_file` | Create or overwrite files | Write |
| `replace_file_content` | Precision in-place code editing | Write |
| `list_dir` | List directory contents | Read-only |
| `grep_search` | ripgrep regex searching | Read-only |
| `find_by_name` | fd file finding | Read-only |
| `run_command` | Execute shell commands & Python scripts | Execution |
| `manage_task` | List, kill, or status background tasks | Execution |
| `schedule` | One-shot timers or recurring cron jobs | Execution |
| `invoke_subagent` | Concurrently spawn registered subagents | Orchestration |
| `manage_subagents` | Inspect or kill active subagents | Orchestration |
| `send_message` | Communicate with active subagents | Orchestration |
| `define_subagent` | Dynamically register ephemeral subagents | Orchestration |
| `ask_question` | Interactive user prompt modal | Interactive |
| `read_url_content` | Fetch static web content via HTTP | Web |
| `search_web` | Web search queries | Web |
| `generate_image` | Image generation / UI mocking | Media |
| `call_mcp_tool` | Lazy-loaded MCP tool execution | MCP |
| `list_resources` | MCP resource discovery | MCP |
| `read_resource` | MCP resource retrieval | MCP |

---

## 4. Skill Discovery & Mounting Specification

Skills reside in `.agents/skills/<skill-name>/` and must contain a `SKILL.md` file.

### 4.1 Skill Frontmatter
```yaml
---
name: apa-reporting
description: Generate strictly formatted APA 7th Edition 3-line tables and statistical reports.
---
```

### 4.2 Progressive Disclosure
Antigravity injects only skill names and descriptions into the model context by default. The complete body of `SKILL.md` is loaded only when the model calls `view_file` on the skill path or when triggered by task context.

### 4.3 Available Built-in Skills
Antigravity automatically provides built-in skills located at `~/.gemini/antigravity/builtin/skills/`:
- `agy-customizations`
- `antigravity_guide`
- `generative_ui`
- `migrate-workflows`
- `google-antigravity-sdk`

Any workspace agent referencing these built-in skills resolves successfully.

---

## 5. Security & Permission Enforcement Mapping

Execution restrictions are mapped to Antigravity's multi-layered security model:

```text
+------------------------------+--------------------------------------------------------------+
| Security Objective           | Enforcement Mechanism                                        |
+------------------------------+--------------------------------------------------------------+
| Command Review & Approval    | Antigravity IDE workspace permissions & user confirmation     |
| Raw Data Immutability        | POSIX mode 0444 + PreToolUse hook path matcher               |
| Safe Shell Commands          | PreToolUse regex blocking destructive commands (rm -rf, etc.)|
| Binary Honesty Verification  | Stop lifecycle hook inspecting transcript.jsonl              |
| Multi-Agent Truthfulness     | Stop lifecycle hook verifying actual invoke_subagent calls   |
| Stage Artifact Completeness  | PostInvocation hook + fail-closed validation manifests        |
+------------------------------+--------------------------------------------------------------+
```
