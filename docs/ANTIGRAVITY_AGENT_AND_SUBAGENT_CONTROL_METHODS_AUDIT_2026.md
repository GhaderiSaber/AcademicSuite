# Controlling Agents and Subagents in Google Antigravity: Technical Audit & Reference Architecture (2026)

**Published:** September 20, 2026  
**Ecosystem:** Google Antigravity 2.0 (Standalone Desktop, CLI `agy`, IDE Extensions, and Python SDK `google-antigravity`)  
**Document Status:** Final / Production Engineering Audit  

---

## Executive Summary

The evolution of agentic platforms reached a watershed moment with the general availability of **Google Antigravity 2.0** on May 19, 2026. Prior to this milestone, multi-agent workflows largely relied on probabilistic prompt instructions ("You are a supervisor; please instruct agent B") or ad-hoc scripting emulators. Such patterns frequently suffered from instruction drift, runaway recursive delegation loops, silent privilege escalation, and context window pollution.

In Antigravity 2.0 and the unified Antigravity Harness, agent control has transitioned from soft prompt steering to **hard machine-enforced governance**. Controlling agents and subagents is achieved across **seven distinct control planes**:
1. **Architectural & Topology Scoping** (hierarchical role boundaries, depth caps, and spawn whitelists).
2. **Declarative Access & Tool Policies** (9-level priority-based resolution, argument predicates, and fail-closed defaults).
3. **Filesystem & Workspace Sandboxing** (worktree branching, shared repo storage, and path confinement).
4. **Deterministic Lifecycle Hook Enforcement** (`PreInvocation`, `PreToolUse`, `PostToolUse`, `Stop` with completion blocking).
5. **Operational Budget & Token Governance** (hard invocation caps, net prompt token budgeting, and typed stop reason tracking).
6. **Asynchronous Concurrency & Reactive State Control** (non-blocking message queues, reactive wakeups, and cron/scheduler daemons).
7. **Contractual Delegation & Adversarial Verification** (strict separation of concerns, schema-gated handoffs, and independent critic subagents).

This document audits each of these methods, examines their failure modes and bypass vectors, provides production-grade configuration templates, and establishes reference architectural patterns for mission-critical deployments.

---

## 1. System Architecture: The Seven Control Planes

Antigravity treats agents not as monolithic chat loops, but as governed state machines executing within an operating system container. 

```
                                  ┌──────────────────────────────────────────────┐
                                  │           User / Orchestrator                │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                   [Plane 1: Topology & Depth Whitelist]
                                                         │
                                                         ▼
                                  ┌──────────────────────────────────────────────┐
                                  │               Root Lead Agent                │
                                  └──────┬───────────────────────────────┬───────┘
                                         │                               │
                      [Plane 6: Reactive Async Message]      [Plane 3: Worktree Isolation]
                                         │                               │
                                         ▼                               ▼
                 ┌────────────────────────────────┐            ┌───────────────────┐
                 │     Worker Subagent Tier       │            │ Worker Git Branch │
                 └───────────────┬────────────────┘            └───────────────────┘
                                 │
           ┌─────────────────────┼─────────────────────┐
           │                     │                     │
           ▼                     ▼                     ▼
 [Plane 4: Hooks]      [Plane 2: Policies]   [Plane 5: Budgets]
 • PreInvocation       • 9-Tier Precedence   • Model/Tool Caps
 • PreToolUse          • Match Predicates    • Token Ceilings
 • PostToolUse         • Fail-Closed Engine  • StopReason Audit
 • Stop (Gate)         • Workspace Jail
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                                 ▼
                     [Plane 7: Verification]
                     • Triad Artifact Handshake
                     • Schema Validation Contracts
                     • Adversarial Critic Audit
```

---

## 2. In-Depth Audit of Control Planes

### Plane 1: Architectural & Topology Scoping

#### Mechanics
Antigravity supports both **Static Custom Subagents** (predefined in `.agents/agents/*.md` with YAML frontmatter) and **Dynamic Subagents** (spawned via `define_subagent` and `invoke_subagent`). Subagents are configured via `SubagentConfig` and `SubagentCapabilities`.

Key control primitives:
- `max_subagent_depth`: Limits nested subagent spawning (e.g., Root → Coordinator → Worker). Prevents recursive exponential agent explosion.
- `allowed_subagents`: Whitelist defining which specific subagents a given tier is authorized to invoke.
- `enabled_tools`: Explicitly constrains the tool registry for the subagent. A worker can be given read-only inspection tools (`view_file`, `grep_search`) without file mutation tools.
- `Orchestrator Non-Execution Invariant`: Best-practice pattern enforcing that orchestrator agents hold **zero execution tools** (`run_command`, `write_to_file`, `replace_file_content`), forcing them to delegate all computational work to specialized workers.

```python
# Programmatic Topology Restriction in Google Antigravity SDK
from google.antigravity import LocalAgentConfig, types

# Leaf Specialist: Read-only inspection, cannot spawn subagents
code_auditor = types.SubagentConfig(
    name="code_auditor",
    description="Audits codebase syntax and safety invariants.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[types.BuiltinTools.VIEW_FILE, types.BuiltinTools.GREP_SEARCH],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

# Root Orchestrator: Depth ceiling = 2, whitelist strictly allows code_auditor
config = LocalAgentConfig(
    subagents=[code_auditor],
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,
        max_subagent_depth=2,
        allowed_subagents=["code_auditor"],
    ),
)
```

#### Audit Findings
*   **Strengths:** Enforces strict compartmentalization of responsibilities. If an orchestrator model hallucinates code modifications, it cannot execute them because the mutation tools are absent from its schema.
*   **Vulnerabilities & Bypass Vectors:** If `allowed_subagents` is omitted while `enable_subagents=True`, an agent can invoke *any* subagent registered in the workspace or define arbitrary subagents via `define_subagent`. 
*   **Verdict:** **COMPLETED & ROBUST**. Setting explicit `allowed_subagents` and a bounded `max_subagent_depth` is mandatory for mission-critical deployments.

---

### Plane 2: Execution & Declarative Access Policies

#### Mechanics
The Antigravity SDK embeds a declarative policy resolution engine (`google.antigravity.hooks.policy`). Policies govern whether a tool call is executed immediately (`allow`), requires user confirmation (`ask_user`), or is blocked (`deny`).

#### The 9-Level Precedence Hierarchy
When a tool invocation is requested, the policy engine resolves permissions using a 9-level priority model. Lower-numbered levels strictly override higher-numbered levels:

| Priority | Rule Type | Example Syntax | Description |
| :---: | :--- | :--- | :--- |
| **1** | **Specific Deny** | `policy.deny("run_command")` | Blocks a specific tool explicitly. |
| **2** | **Specific Ask** | `policy.ask_user("run_command", handler=...)` | Demands human/agent confirmation. |
| **3** | **Specific Allow** | `policy.allow("view_file")` | Permits a specific tool explicitly. |
| **4** | **Prefix Wildcard Deny** | `policy.deny("mcp_server/*")` | Blocks all tools on an MCP server. |
| **5** | **Prefix Wildcard Ask** | `policy.ask_user("mcp_server/*")` | Demands approval for an entire server. |
| **6** | **Prefix Wildcard Allow** | `policy.allow("mcp_server/*")` | Permits an entire MCP server. |
| **7** | **Global Wildcard Deny** | `policy.deny("*")` / `policy.deny_all()` | Denies all tools across the runtime. |
| **8** | **Global Wildcard Ask** | `policy.ask_user("*")` | Demands confirmation for any tool. |
| **9** | **Global Wildcard Allow** | `policy.allow("*")` / `policy.allow_all()` | Permits all tools (dev-only mode). |

#### Argument Predicates (`when`) and Fail-Closed Semantics
Policies can inspect runtime tool arguments via callable predicates:
```python
# Deny shell execution if attempting destructive operations
policy.deny(
    "run_command",
    when=lambda args: any(cmd in args.get("CommandLine", "") for cmd in ["rm -rf", "mkfs", "dd"]),
    name="block_destructive_commands",
)
```
*Crucial Safety Guarantee:* If a predicate throws an uncaught exception (e.g., malformed argument dictionary or `KeyError`), the policy engine **fails closed**, treating the exception as an affirmative match for the decision.

#### Audit Findings
*   **Strengths:** Priority resolution is unambiguous and deterministic. Specific rules consistently trump wildcards.
*   **Vulnerabilities & Bypass Vectors:** Naive argument string matching in `run_command` can be bypassed using bash obfuscation (e.g., base64 decoding, string concatenation `r''m`, variable expansion `$CMD`).
*   **Mitigation:** Do not rely solely on simple string matching for shell security. Pair `policy.workspace_only()` with OS-level containerization or dedicated hook scripts that parse command semantics.

---

### Plane 3: Filesystem & Workspace Sandboxing

#### Mechanics
When invoking subagents via `invoke_subagent`, Antigravity supports three distinct **Workspace Isolation Modes**:

1.  **`inherit`**: The subagent executes directly inside the parent's directory. All filesystem mutations occur in place. Useful for linear workflows and single-file edits.
2.  **`branch` (Git Worktree Isolation)**: Antigravity automatically creates an isolated Git worktree (`git worktree add`). The subagent executes in a separate physical directory on a private branch. File modifications are isolated; if the subagent errors or is terminated, the worktree is cleanly pruned without contaminating the primary working tree.
3.  **`share` (Shared Repository Storage)**: The subagent shares underlying repository metadata (e.g., Mercurial `hg share` or shared Git object storage) without duplicating disk space, allowing coordinated multi-agent writing without directory locks.

Additionally, `policy.workspace_only(workspaces)` mechanically constrains all file operations (`view_file`, `write_to_file`, `replace_file_content`) to approved directory paths, blocking directory traversal (`../../etc/passwd`).

```
                    Root Repository (/workspace)
                               │
               ┌───────────────┴───────────────┐
               │                               │
        Subagent A (branch)             Subagent B (branch)
   Worktree: /tmp/agy/worktree_a   Worktree: /tmp/agy/worktree_b
   Branch:   feature/subagent-a    Branch:   feature/subagent-b
               │                               │
        [Isolated Edits]                [Isolated Edits]
               │                               │
               └───────────────┬───────────────┘
                               │
                Pull Request / Merge Review
```

#### Audit Findings
*   **Strengths:** `branch` mode eliminates race conditions and file collisions during parallel subagent operations.
*   **Vulnerabilities & Bypass Vectors:** In `inherit` mode, concurrent subagents editing the same file will trigger non-deterministic overwrite conflicts.
*   **Verdict:** **COMPLETED & PRODUCTION-READY**. Use `branch` mode for all parallel code-authoring subagents.

---

### Plane 4: Deterministic Lifecycle Hook Enforcement

#### Mechanics
Antigravity supports machine-level lifecycle hooks configured declaratively via `.agents/hooks.json` or programmatically via SDK decorators (`@hooks.pre_tool_call_decide`, etc.).

#### The Five Canonical Lifecycle Events

| Event | Execution Point | Primary Governance Objective |
| :--- | :--- | :--- |
| **`PreInvocation`** | Before model candidate dispatch. | Injects ephemeral constitutional instructions, checks token ceilings, and prepares dynamic context. |
| **`PostInvocation`** | Immediately after model returns. | Audits model output, filters sensitive strings, and sanitizes chain-of-thought representations. |
| **`PreToolUse`** | Prior to tool execution. Supports regex `matcher`. | **Interception Gate**: Validates arguments, blocks unauthorized file access, enforces raw data immutability. |
| **`PostToolUse`** | Immediately after tool finishes. Supports regex `matcher`. | **Audit Trail**: Hashes generated files, records execution metadata to append-only logs (`audit_log.jsonl`). |
| **`Stop`** | At session/turn conclusion. | **Completion Gate**: Validates artifacts on disk. Can return `{"decision": "continue"}` to **reject termination** and force the agent to fix errors. |

#### Declarative Schema (`.agents/hooks.json`)
```json
{
  "constitutional-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/verification/safety_guard.py --event PreToolUse",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 .agents/verification/transcript_and_rule_guard.py --event Stop",
        "timeout": 15
      }
    ]
  }
}
```

#### The `Stop` Hook Continuation Primitive
A major breakthrough in Antigravity 2.0 is the programmatic **Continuation Verdict** emitted by the `Stop` hook:
```json
{
  "decision": "continue",
  "reason": "Directive 3 Violation: Missing required physical artifact '06_hypothesis_1.docx'. Complete generation before stopping."
}
```
When this is returned, the Antigravity Harness re-activates the agent loop, injecting the `reason` as an actionable system message. The agent cannot terminate until the guard script exits cleanly with `{"decision": "allow"}`.

#### Audit Findings
*   **Strengths:** Completely decoupled from model prompts. Operates outside LLM context. Fail-closed: script crashes or timeouts block tool execution.
*   **Vulnerabilities & Bypass Vectors:** Hooks must execute within their specified `timeout` (default 10–15s). Complex verification scripts must remain highly optimized to prevent timeouts.
*   **Verdict:** **GOLD STANDARD FOR DETERMINISTIC GOVERNANCE**.

---

### Plane 5: Resource & Token Budget Governance

#### Mechanics
Runaway agent loops and infinite tool recursion are mitigated via `types.BudgetConfig` and the `StopReason` enum.

```python
from google.antigravity import Agent, LocalAgentConfig, types

config = LocalAgentConfig(
    budget_config=types.BudgetConfig(
        # Invocation Controls
        max_model_calls=15,          # Maximum LLM generation calls
        max_tool_calls=30,           # Maximum tool executions allowed
        
        # Token Controls (Proactively calculated)
        max_input_tokens=150_000,    # Capped net uncached prompt tokens
        max_output_tokens=25_000,    # Capped cumulative output tokens
        max_total_tokens=175_000,    # Capped total token footprint
    )
)
```

#### Typed `StopReason` Audit
When an agent turn concludes, the orchestrator inspects `response.stop_reason` to distinguish clean completions from budget violations:
- `types.StopReason.UNSPECIFIED`: Normal completion.
- `types.StopReason.MAX_MODEL_CALLS_EXCEEDED`: Exceeded generator invocations.
- `types.StopReason.MAX_TOOL_CALLS_EXCEEDED`: Caught in repeated tool execution loops.
- `types.StopReason.MAX_INPUT_TOKENS_EXCEEDED`: Prevented bloated prompt dispatch.
- `types.StopReason.MAX_OUTPUT_TOKENS_EXCEEDED`: Candidate generation capped.
- `types.StopReason.RESOURCE_EXHAUSTED`: Cloud API quota or platform rate limit.

#### Audit Findings
*   **Strengths:** Prevents unexpected cloud expenditure and runaway agent cascades. Evaluated proactively before sending prompts to the inference engine.
*   **Vulnerabilities & Bypass Vectors:** If subagents inherit separate unconfigured budget objects, subagent cascades can bypass parent budget dials unless the parent enforces aggregated limits.
*   **Verdict:** **COMPLETED & ESSENTIAL FOR PRODUCTION CLOUD WORKLOADS**.

---

### Plane 6: Asynchronous Concurrency & Reactive State Control

#### Mechanics
Antigravity executes subagents asynchronously, maintaining responsive UI and orchestrator states:
- **State Machine**: Subagents exist in discrete states: `running`, `idle`, `waiting_for_input`, `waiting_for_dependents`, `waiting_for_message`, `canceling`, `errored`.
- **Reactive Wakeup (Zero Polling)**: The parent orchestrator does **not** run busy-waiting `while True: check_status()` loops. The Antigravity Harness suspends the parent turn until a message arrives or a subagent finishes, reactively waking the parent.
- **Task Management**: Managed programmatically via `manage_subagents` (`list`, `kill`, `kill_all`) and `schedule` (one-shot timers and recurring cron jobs).

```
                     Parent Invokes Subagent
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
      Subagent: [running]               Parent: [Suspended]
               │                                 │
     (Processes background task)                 │
               │                                 │
      Subagent: [idle / done]                    │
               │                                 │
               └──────── Message Sent ───────────┘
                                │
                                ▼
                    Parent: [Reactive Wakeup]
```

#### Audit Findings
*   **Strengths:** Maximizes system efficiency, eliminates API token waste on polling loops, and provides instant cancellation via `manage_subagents(Action="kill")`.
*   **Vulnerabilities & Bypass Vectors:** Subagents that hang indefinitely without generating tool calls or messages will leave tasks in `running` state unless monitored via timeout hooks or scheduler timers.
*   **Verdict:** **HIGHLY SCALABLE ARCHITECTURE**.

---

### Plane 7: Epistemic Integrity, Contractual Envelopes & Multi-Agent Critics

#### Mechanics
The most sophisticated control methodology in Antigravity is the **Six-Part Functional Separation Invariant** and the **Adversarial Critic Pattern**:

```
1. Agent         ──► Decides        (Context-isolated cognitive reasoning role)
2. Skill         ──► Instructs      (Domain knowledge, procedure specifications)
3. Script        ──► Computes       (Deterministic Python/R "Hands")
4. Hook          ──► Enforces       (Synchronous safety checks, tamper prevention)
5. State Machine ──► Authorizes     (Milestone transitions, event logging)
6. Manifest      ──► Verifies       (Schema contracts, required physical artifacts)
```

#### Contractual Delegation Envelopes
Orchestrators never send ambiguous prompts. Delegation occurs via structured envelopes defining input prerequisites, explicit CLI commands, and expected output artifacts:
```json
{
  "contract_version": "2.0",
  "task_id": "stage_4_06_hypothesis_1",
  "assigned_subagent": "statistics-agent",
  "workspace_mode": "inherit",
  "input_artifact": "academic-state/05_correlations.json",
  "executable_script": "python3 .agents/skills/statistical-data-analyst/scripts/run_ancova.py",
  "required_output_triad": {
    "docx": "academic-state/06_hypothesis_1.docx",
    "md": "academic-state/06_hypothesis_1.md",
    "json": "academic-state/06_hypothesis_1.json"
  },
  "verification_agent": "validation-agent"
}
```

#### Adversarial Critic Pattern (The Checker Cannot Be The Maker)
To eliminate sycophancy and self-confirmation bias:
1. Generator subagents (`academic-writer`, `statistics-agent`) produce candidate artifacts.
2. Independent critic subagents (`statistical-auditor`, `validation-agent`, `results-auditor`) inspect the generated artifacts against strict checklists and statistical thresholds.
3. The orchestrator requires unanimous approval from critics before updating project milestones.

#### Audit Findings
*   **Strengths:** Prevents hallucinated numbers, ensures compliance with empirical standards, and guarantees reproducible artifacts on disk.
*   **Vulnerabilities & Bypass Vectors:** In loosely governed configurations, agents may fabricate reports claiming validation passed without executing the validator. This is why Plane 4 (`Stop` hook) is paired with Plane 7 to mechanically inspect the actual command exit codes in `transcript.jsonl`.
*   **Verdict:** **MAXIMUM INTEGRITY ATTAINABLE IN AGENTIC SYSTEMS**.

---

## 3. Comparative Control Plane Matrix

| Control Dimension | Layer of Enforcement | Determinism | Latency Overhead | Primary Failure Mode | Recommended Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Topology & Whitelists** | Antigravity Harness | 100% Deterministic | Zero overhead | Omitted whitelist allows dynamic spawns | All multi-agent setups |
| **Policy Engine (9-Tier)** | SDK Core / Dispatcher | 100% Deterministic | Sub-millisecond | Argument predicate exceptions (mitigated by fail-closed) | All tool executions |
| **Workspace Sandboxing** | OS / Git Subsystem | 100% Deterministic | Low (~100ms worktree creation) | Disk space consumption if untracked | Concurrent write agents |
| **Lifecycle Hooks** | External Process Hook | 100% Deterministic | Script execution (~50–200ms) | Script timeouts (>15s) | Hard safety & audit gates |
| **Budget Controls** | SDK Token Accountant | 100% Deterministic | Pre-calculated, negligible | Subagents with unlinked budget pools | Cloud API deployments |
| **Reactive Wakeup** | Event Loop / Message Bus | 100% Deterministic | Zero active CPU | Deadlocks if subagent hangs silently | Asynchronous workflows |
| **Adversarial Critics** | Multi-Agent Deliberation | Hybrid (LLM + Script) | Moderate (turn-level invocation) | Collusion if critic prompt is sycophantic | Final deliverables / milestones |

---

## 4. Production Hardening Guide: Reference Configurations

### 1. Hardened Workspace Hook Specification (`.agents/hooks.json`)

```json
{
  "production-governance": {
    "enabled": true,
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 .agents/verification/pre_invocation_guard.py",
        "timeout": 5
      }
    ],
    "PreToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/verification/pre_tool_guard.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/verification/audit_logger.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 .agents/verification/transcript_and_rule_guard.py --event Stop",
        "timeout": 15
      }
    ]
  }
}
```

### 2. Hardened Python SDK Agent Setup

```python
"""
Production Reference Setup for Governed Multi-Agent Pipeline in Google Antigravity SDK
"""
import asyncio
from google.antigravity import Agent, LocalAgentConfig, types
from google.antigravity.hooks import policy

# 1. Define Subagents with Least-Privilege Tools
code_worker = types.SubagentConfig(
    name="code_worker",
    description="Implements approved features.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[
            types.BuiltinTools.VIEW_FILE,
            types.BuiltinTools.EDIT_FILE,
            types.BuiltinTools.CREATE_FILE,
        ],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

auditor = types.SubagentConfig(
    name="auditor",
    description="Audits code and tests compliance.",
    capabilities=types.SubagentCapabilities(
        enabled_tools=[
            types.BuiltinTools.VIEW_FILE,
            types.BuiltinTools.GREP_SEARCH,
        ],
        agent_behavior=types.AgentBehavior.AUTONOMOUS,
    ),
)

# 2. Define Granular 9-Tier Safety Policies
policies = [
    # Tier 1: Specific Denies
    policy.deny("run_command", when=lambda a: "sudo" in a.get("CommandLine", ""), name="deny_sudo"),
    
    # Tier 2: Specific Asks
    policy.ask_user("run_command", when=lambda a: "git push" in a.get("CommandLine", ""), name="confirm_push"),
    
    # Tier 3: Specific Allows
    policy.allow("view_file"),
    policy.allow("grep_search"),
    
    # Preset: Confinement to designated workspace directories
    policy.workspace_only(["/home/user/workspace/production"]),
    
    # Tier 7: Global Deny on any unregistered tool
    policy.deny_all(),
]

# 3. Assemble Governed Configuration
config = LocalAgentConfig(
    system_instructions="You are the Lead Project Orchestrator. Coordinate tasks through subagents.",
    workspaces=["/home/user/workspace/production"],
    subagents=[code_worker, auditor],
    capabilities=types.CapabilitiesConfig(
        enable_subagents=True,
        max_subagent_depth=2,
        allowed_subagents=["code_worker", "auditor"],
    ),
    policies=policies,
    budget_config=types.BudgetConfig(
        max_model_calls=25,
        max_tool_calls=50,
        max_input_tokens=250_000,
        max_output_tokens=50_000,
        max_total_tokens=300_000,
    ),
)

async def main():
    async with Agent(config) as orchestrator:
        response = await orchestrator.chat("Execute audited implementation of authentication middleware.")
        print(f"Outcome: {await response.text()}")
        print(f"Termination Reason: {response.stop_reason}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Summary & Key Takeaways

1. **Prompt Steering is Dead; Machine Governance is Standard**: In Antigravity 2.0, controlling agents relies on OS-level primitives (Git worktrees), platform-level policies (9-tier priority engine), and runtime lifecycle interception (`hooks.json`).
2. **Fail-Closed by Design**: Antigravity policies and predicates treat uncaught exceptions and timeouts as matches for denial, preventing silent escalation.
3. **The Stop Hook as an Absolute Gatekeeper**: The ability of the `Stop` lifecycle hook to inspect `transcript.jsonl` and return `{"decision": "continue"}` mechanically forces agents to satisfy requirements (e.g., generating physical artifact triads or resolving validator failures) before exiting.
4. **Worktree Sandboxing Prevents Collisions**: Using `branch` workspace mode for parallel subagents completely isolates filesystem mutations until explicitly vetted and merged.
5. **Separation of Concerns Prevents Hallucinations**: Enforcing the Orchestrator Non-Execution Invariant ensures orchestrators remain objective conductors while deterministic scripts and specialist agents perform concrete operations.
