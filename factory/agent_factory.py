#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/agent_factory.py — Modernized Autonomous Agent & Subagent Specification Factory

Generates canonical, constitutional Antigravity agent specifications in directory form:
.agents/agents/<agent-name>/agent.md
with persistent cognitive roles, canonical frontmatter metadata, comprehensive validation checks,
and formal contracts adhering to the authoritative target architecture.
"""

import os
import sys
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
SKILLS_DIR = os.path.join(ROOT_DIR, ".agents", "skills")

# Authoritative Model Tiers in Google Antigravity
VALID_MODELS: Set[str] = {
    "flash",
    "flash_lite",
    "pro",
    "inherit",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.7-pro",
}

# Canonical Antigravity Command Execution Policies (camelCase field name)
VALID_COMMAND_EXECUTION_POLICIES: Set[str] = {
    "always-proceed",
    "request-review",
    "strict",
    "proceed-in-sandbox",
    "deny",
}

# Canonical Antigravity Tool Whitelist
VALID_TOOLS: Set[str] = {
    # File tools
    "view_file",
    "write_to_file",
    "replace_file_content",
    "list_dir",
    "grep_search",
    "find_by_name",
    # Terminal & process management tools
    "run_command",
    "manage_task",
    "schedule",
    # Subagent & communication tools
    "invoke_subagent",
    "manage_subagents",
    "send_message",
    "define_subagent",
    # Interactive & search tools
    "ask_question",
    "read_url_content",
    "search_web",
    "generate_image",
}

# Subagent delegation tools strictly forbidden for Tier 3/4 specialist subagents
DISALLOWED_WORKER_TOOLS: Set[str] = {
    "invoke_subagent",
    "manage_subagents",
    "define_subagent",
}

# Target Durable Agents (Tier 1 Orchestrators & Tier 2 Domain Authorities)
TARGET_DURABLE_AGENTS: List[str] = [
    "digital-saber",
    "academic-orchestrator",
    "methodology-expert",
    "statistical-expert",
    "academic-writer",
    "evidence-auditor",
    "final-judge",
]

# Target Bounded Specialist Subagents (Tier 3 Execution & Tier 4 Adversarial Critics)
TARGET_SUBAGENTS: List[str] = [
    "research-agent",
    "literature-expert",
    "journal-strategist",
    "meta-analyst",
    "data-agent",
    "data-curator",
    "statistics-agent",
    "psychometric-expert",
    "longitudinal-modmed-expert",
    "intervention-designer",
    "qualitative-analyst",
    "validation-agent",
    "results-auditor",
    "statistical-auditor",
    "academic-challenger",
]

ALL_TARGET_ROLES: Set[str] = set(TARGET_DURABLE_AGENTS) | set(TARGET_SUBAGENTS)

CONSTITUTIONAL_DIRECTIVES = """## 🛑 Mandatory Constitutional Directives (AGENTS.md Compliance)
All subagents in this workspace operate under strict adherence to `AGENTS.md`:
1. **Directive 0 (Binary Honesty & Anti-Deception)**: Zero defensive rationalization. Never fabricate numbers, citations, or compliance claims. If asked a compliance question, start with an unambiguous "Yes" or "No".
2. **Directive 2 (Deterministic Calculations)**: Never calculate statistics, p-values, or effect sizes mentally. Execute deterministic Python scripts in `.agents/skills/<skill>/scripts/` on the actual dataset.
3. **Directive 4 (APA 7 & Persian Leading Zero Standard)**: Italicize Latin statistical symbols (*M, SD, t, F, p, r, R², β, z*). NEVER omit leading zeros in Persian (`۰.۰۵`, `۰.۰۰۱`). Report p < .001 or ۰.۰۰۱ > p (never .000). Zero emojis in academic text or slides.
4. **Directive 5 (BiDi OpenXML & Persian Font Binding)**: Enforce RTL paragraph `<w:bidi/>`. Bind Persian fonts to `B Nazanin` (body) and `B Titr` (headings), with Latin in `Times New Roman`. Preserve Word OMML math equations (`<m:oMath>`).
5. **Directive 6 (English-Only Filenames)**: Every file and directory on disk MUST use English ASCII characters only (`[a-zA-Z0-9_.-]`).
6. **Directive 14 (Anti-Hallucination & Zero Ghost Citations)**: Never invent bibliographic references. All citations must be verified against real academic databases.
7. **Directive 15 (Temporal Anchor: 2026)**: Current operative year is 2026 (1405 SH).
"""


class AgentValidationError(ValueError):
    """Raised when an AgentSpec violates Antigravity or AcademicSuite architectural constraints."""
    pass


@dataclass
class AgentSpec:
    """Canonical representation of an Antigravity agent or subagent specification."""
    name: str
    description: str
    role: str
    tools: List[str] = field(default_factory=list)
    mainAgent: bool = False
    subagent: bool = True
    model: str = "inherit"
    commandExecutionPolicy: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)
    mcpServers: List[str] = field(default_factory=list)
    inheritCustomizations: Optional[bool] = None

    # Narrative & behavioral specifications
    mission: Optional[str] = None
    decision_rules: List[str] = field(default_factory=list)
    anti_patterns: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    non_responsibilities: Optional[List[str]] = None
    forbidden_actions: Optional[List[str]] = None

    def to_frontmatter_dict(self) -> Dict[str, Any]:
        """Returns the dictionary representation formatted strictly for Antigravity YAML frontmatter."""
        fm: Dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "role": self.role,
            "model": self.model,
            "mainAgent": self.mainAgent,
            "subagent": self.subagent,
        }
        if self.commandExecutionPolicy is not None:
            fm["commandExecutionPolicy"] = self.commandExecutionPolicy
        if self.tools:
            fm["tools"] = list(self.tools)
        if self.skills:
            fm["skills"] = list(self.skills)
        if self.agents:
            fm["agents"] = list(self.agents)
        if self.mcpServers:
            fm["mcpServers"] = list(self.mcpServers)
        if self.inheritCustomizations is not None:
            fm["inheritCustomizations"] = self.inheritCustomizations
        return fm

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSpec":
        if "command_execution_policy" in data:
            raise AgentValidationError(
                "Deprecated field 'command_execution_policy' detected. Use canonical camelCase 'commandExecutionPolicy'."
            )
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


def get_available_skills(skills_dir: Optional[str] = None) -> Set[str]:
    """Discovers available skills on disk and known built-in Antigravity skills."""
    skills_path = skills_dir or SKILLS_DIR
    available = {
        "agy-customizations",
        "antigravity_guide",
        "generative_ui",
        "migrate-workflows",
    }
    if os.path.isdir(skills_path):
        for entry in os.listdir(skills_path):
            full_path = os.path.join(skills_path, entry)
            if os.path.isdir(full_path) and os.path.exists(os.path.join(full_path, "SKILL.md")):
                available.add(entry)
    return available


def check_circular_dependencies(graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """
    Detects circular dependencies in a directed agent graph using DFS.
    Returns the cycle path as a list of agent names if found, else None.
    """
    visited: Set[str] = set()
    rec_stack: List[str] = []

    def dfs(node: str) -> Optional[List[str]]:
        visited.add(node)
        rec_stack.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in rec_stack:
                cycle_start = rec_stack.index(neighbor)
                return rec_stack[cycle_start:] + [neighbor]
        rec_stack.pop()
        return None

    for node in list(graph.keys()):
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                return cycle
    return None


def calculate_max_depth(graph: Dict[str, List[str]], root: str) -> Tuple[int, List[str]]:
    """
    Calculates the maximum delegation depth and path originating from root.
    A root with no dependencies has depth 1.
    Root -> Child has depth 2.
    Root -> Child -> Grandchild has depth 3.
    """
    def dfs_depth(node: str, current_path: List[str]) -> Tuple[int, List[str]]:
        if node in current_path:
            return len(current_path), current_path
        children = graph.get(node, [])
        if not children:
            return len(current_path) + 1, current_path + [node]
        best_depth = 0
        best_path: List[str] = []
        for child in children:
            d, p = dfs_depth(child, current_path + [node])
            if d > best_depth:
                best_depth = d
                best_path = p
        return best_depth, best_path

    return dfs_depth(root, [])


def validate_agent_spec(
    spec: AgentSpec,
    existing_agents: Optional[Dict[str, AgentSpec]] = None,
    available_skills: Optional[Set[str]] = None,
    allow_name_collision: bool = False,
    max_dependency_depth: int = 3,
) -> None:
    """
    Validates an AgentSpec against all constitutional and architectural constraints:
    1. Unique name
    2. Valid role
    3. mainAgent/subagent consistency
    4. Valid model
    5. Valid commandExecutionPolicy (rejects deprecated command_execution_policy)
    6. Valid tools & least-privilege tool isolation
    7. Valid skills
    8. Valid agent dependencies
    9. Valid MCP references
    10. No self-dependency
    11. No unauthorized worker-to-worker dependency
    12. No circular dependencies
    13. No excessive dependency depth
    """
    # 1. Unique Name
    if not spec.name or not isinstance(spec.name, str):
        raise AgentValidationError("Agent name must be a non-empty string.")
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", spec.name):
        raise AgentValidationError(
            f"Invalid agent name '{spec.name}'. Must be lowercase ASCII alphanumeric with single hyphens."
        )
    if existing_agents and spec.name in existing_agents and not allow_name_collision:
        raise AgentValidationError(f"Duplicate agent name: '{spec.name}' already exists in registry.")

    # 2. Valid Role
    if not spec.role or not isinstance(spec.role, str) or not spec.role.strip():
        raise AgentValidationError("Agent role must be a non-empty descriptive string.")
    if len(spec.role.strip()) < 3 or len(spec.role.strip()) > 120:
        raise AgentValidationError(f"Agent role length ({len(spec.role.strip())}) must be between 3 and 120 characters.")

    # 3. mainAgent / subagent Consistency
    if not isinstance(spec.mainAgent, bool) or not isinstance(spec.subagent, bool):
        raise AgentValidationError("mainAgent and subagent must both be boolean values.")
    if not spec.mainAgent and not spec.subagent:
        raise AgentValidationError(
            "mainAgent/subagent consistency failure: An agent cannot have both mainAgent=False and subagent=False."
        )

    # 4. Valid Model
    if spec.model not in VALID_MODELS:
        raise AgentValidationError(
            f"Invalid model '{spec.model}' for agent '{spec.name}'. Allowed models: {sorted(VALID_MODELS)}"
        )

    # 5. Valid commandExecutionPolicy
    if spec.commandExecutionPolicy is not None:
        if spec.commandExecutionPolicy not in VALID_COMMAND_EXECUTION_POLICIES:
            raise AgentValidationError(
                f"Invalid commandExecutionPolicy '{spec.commandExecutionPolicy}' for agent '{spec.name}'. "
                f"Allowed policies: {sorted(VALID_COMMAND_EXECUTION_POLICIES)}"
            )

    # 6. Valid Tools & Principle of Least Privilege
    for tool in spec.tools:
        if tool not in VALID_TOOLS:
            raise AgentValidationError(
                f"Invalid tool '{tool}' for agent '{spec.name}'. Allowed tools: {sorted(VALID_TOOLS)}"
            )

    # Tool permissions: Worker subagents must not have subagent orchestration tools
    is_worker = spec.subagent and not spec.mainAgent and spec.name not in TARGET_DURABLE_AGENTS
    if is_worker:
        for tool in spec.tools:
            if tool in DISALLOWED_WORKER_TOOLS:
                raise AgentValidationError(
                    f"Unauthorized delegation tool '{tool}' for specialist subagent '{spec.name}'. "
                    "Specialist subagents cannot invoke or manage other subagents."
                )

    # Tool permissions: Pure critics must not have mutating or command execution tools
    if spec.name in {"academic-challenger", "results-auditor"}:
        disallowed_critic_tools = {"run_command", "replace_file_content"}
        for tool in spec.tools:
            if tool in disallowed_critic_tools:
                raise AgentValidationError(
                    f"Unauthorized tool '{tool}' for critic role '{spec.name}'. Critic roles must remain read-only."
                )

    # 7. Valid Skills
    skills_pool = available_skills if available_skills is not None else get_available_skills()
    for skill in spec.skills:
        if skill not in skills_pool:
            raise AgentValidationError(
                f"Unknown skill '{skill}' declared by agent '{spec.name}'. Skill does not exist in workspace or built-ins."
            )

    # 8. Valid Agent Dependencies
    known_agents = ALL_TARGET_ROLES.copy()
    if existing_agents:
        known_agents.update(existing_agents.keys())
    for dep in spec.agents:
        if dep not in known_agents:
            raise AgentValidationError(
                f"Unknown agent dependency '{dep}' declared by agent '{spec.name}'."
            )

    # 9. Valid MCP References
    for mcp in spec.mcpServers:
        if not isinstance(mcp, str) or not re.match(r"^[a-zA-Z0-9_-]+$", mcp):
            raise AgentValidationError(
                f"Invalid MCP server reference '{mcp}' declared by agent '{spec.name}'."
            )

    # 10. No Self-Dependency
    if spec.name in spec.agents:
        raise AgentValidationError(
            f"Self-dependency detected: Agent '{spec.name}' cannot declare a dependency on itself."
        )

    # 11. No Unauthorized Worker-to-Worker Dependency
    if is_worker and len(spec.agents) > 0:
        raise AgentValidationError(
            f"Unauthorized worker-to-worker dependency: Specialist subagent '{spec.name}' cannot depend on other agents {spec.agents}."
        )

    # 12. No Circular Dependencies & 13. No Excessive Dependency Depth
    # Build comprehensive dependency graph
    graph: Dict[str, List[str]] = {}
    if existing_agents:
        for a_name, a_spec in existing_agents.items():
            graph[a_name] = list(a_spec.agents)
    graph[spec.name] = list(spec.agents)

    # Ensure all mentioned children are nodes in graph
    for children in graph.values():
        for c in children:
            if c not in graph:
                graph[c] = []

    cycle = check_circular_dependencies(graph)
    if cycle:
        raise AgentValidationError(
            f"Circular dependency detected: {' -> '.join(cycle)}"
        )

    # Check max depth from all potential roots
    roots = [n for n, deps in graph.items() if n == spec.name or (existing_agents and n in existing_agents and existing_agents[n].mainAgent)]
    if not roots:
        roots = [spec.name]
    for root in roots:
        depth, path = calculate_max_depth(graph, root)
        if depth > max_dependency_depth:
            raise AgentValidationError(
                f"Excessive dependency depth ({depth} > {max_dependency_depth}): Path {' -> '.join(path)} exceeds ceiling."
            )


def render_frontmatter(metadata: Dict[str, Any]) -> str:
    """Renders canonical, deterministic Antigravity YAML frontmatter."""
    lines = ["---"]
    key_order = [
        "name",
        "description",
        "role",
        "model",
        "mainAgent",
        "subagent",
        "commandExecutionPolicy",
        "tools",
        "skills",
        "agents",
        "mcpServers",
        "inheritCustomizations",
    ]
    for k in key_order:
        if k not in metadata:
            continue
        v = metadata[k]
        if v is None:
            continue
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, str):
            if "\n" in v or len(v) > 80:
                lines.append(f"{k}: >-")
                for subline in v.strip().splitlines():
                    lines.append(f"  {subline}")
            else:
                lines.append(f"{k}: {v}")
        elif isinstance(v, (list, tuple, set)):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
        elif isinstance(v, dict):
            if not v:
                lines.append(f"{k}: {{}}")
            else:
                lines.append(f"{k}:")
                for dk, dv in v.items():
                    lines.append(f"  {dk}: {dv}")
        else:
            lines.append(f"{k}: {v}")

    lines.append("---")
    return "\n".join(lines)


def generate_agent_markdown(
    name: str,
    role: str,
    description: str,
    skills: List[str],
    mission: str,
    decision_rules: List[str],
    anti_patterns: Optional[List[str]] = None,
    spec: Optional[AgentSpec] = None,
) -> str:
    """
    Generates standardized Antigravity agent Markdown with canonical YAML frontmatter.
    """
    anti_patterns = anti_patterns or [
        "Never calculate statistics in your head (violates Directive 2).",
        "Never omit the Persian leading zero before decimals (violates Directive 4).",
        "Never skip the Pre-Flight Pipeline Declaration (violates Directive 1).",
    ]

    rules_md = "\n".join([f"{i+1}. {r}" for i, r in enumerate(decision_rules)])
    anti_md = "\n".join([f"- ❌ {ap}" for ap in anti_patterns])

    if spec:
        fm_dict = spec.to_frontmatter_dict()
    else:
        fm_dict = {
            "name": name,
            "description": description,
            "role": role,
            "model": "inherit",
            "mainAgent": False,
            "subagent": True,
            "commandExecutionPolicy": "request-review",
            "skills": skills,
        }

    frontmatter = render_frontmatter(fm_dict)

    content = f"""{frontmatter}

# {role}

{CONSTITUTIONAL_DIRECTIVES}

---

## 🏛️ Identity & Domain Mission

You are the **{role}** in Digital Saber's cognitive architecture.
{mission}

---

## ⚙️ Foundational Decision Sequences & Methodological Philosophy

Always execute the following domain procedures:

{rules_md}

---

## 🚫 Prohibited Anti-Patterns

{anti_md}

---

## 📦 Deliverables & Artifact Hand-off

1. Output must be saved as structured, machine-readable JSON checkpoints and OpenXML Word artifacts on disk.
2. Every output must be certified by independent validators prior to handoff.
3. Handoff to the next pipeline stage must reference the exact physical disk path.
"""
    return content


def generate_contract_markdown(
    name: str,
    role: str,
    mission: str,
    skills: List[str],
    responsibilities: Optional[List[str]] = None,
    non_responsibilities: Optional[List[str]] = None,
    forbidden_actions: Optional[List[str]] = None,
) -> str:
    """
    Generates the formal 12-section contract Markdown adhering to Phase 4 standards.
    """
    can_items = responsibilities or [
        f"Execute domain analytical workflows for {role}.",
        "Generate structured analysis results and machine-readable JSON checkpoints.",
        "Produce verified tables and narrative drafts adhering to APA 7 standards.",
    ]
    cannot_items = non_responsibilities or [
        "Calculate, estimate, or hallucinate statistical numbers mentally (Directive 2).",
        "Modify raw empirical datasets or overwrite files in place.",
        "Self-validate deliverables without independent review by validation-agent.",
    ]
    forbidden = forbidden_actions or [
        "Zero Mental Math: Never guess or estimate parameters mentally (Directive 2).",
        "Zero Non-ASCII Filenames: Strictly use English ASCII characters for all disk files (Directive 6).",
        "Zero Unverified Citations: Never invent bibliographic data (Directive 14).",
    ]

    can_md = "\n".join([f"- {item}" for item in can_items])
    cannot_md = "\n".join([f"- {item}" for item in cannot_items])
    skills_md = "\n".join([f"- `{s}`" for s in skills])
    forbidden_md = "\n".join([
        f"- **{f.split(':')[0]}:**{':'.join(f.split(':')[1:])}" if ':' in f else f"- {f}"
        for f in forbidden
    ])

    return f"""# Agent Contract: {role}

**Role Identifier:** `{name}`  
**Operational Tier:** Tier 2 — Domain Specialist  
**Contract Version:** 1.0.0  
**Effective Date:** September 2026 (1405 SH)  

---

## MISSION
{mission}

---

## RESPONSIBILITIES

### CAN:
{can_md}

---

## NON-RESPONSIBILITIES

### CANNOT:
{cannot_md}

---

## INPUTS
- Target dataset or input payload checkpoint (`.xlsx`, `.json`, `.docx`).
- Research questions, variable definitions, and model specifications.

---

## OUTPUTS
- Structured JSON checkpoints: `stats_results.json`, `findings.json`.
- APA 7 tables and narrative report files.
- Synchronized micro-stage triads (`.docx`, `.md`, `.json`).

---

## ALLOWED TOOLS
- `view_file` (Inspect input payloads and skill specifications)
- `write_to_file` & `replace_file_content` (Export outputs and draft narrative)
- `run_command` (Execute deterministic scripts in `.agents/skills/`)
- `list_dir`, `grep_search`, `find_by_name` (Search and inspect workspace assets)

---

## REQUIRED SKILLS
{skills_md}

---

## FORBIDDEN ACTIONS
{forbidden_md}

---

## HANDOFF FORMAT
The {role} hands off structured artifacts:
```markdown
### 📦 {role} Handoff
- **Domain:** {name}
- **Artifacts Generated on Disk (Triad):**
  - `<output_dir>/output.docx`
  - `<output_dir>/output.md`
  - `<output_dir>/output.json`
- **Validation Status:** PASS
```

---

## VALIDATION REQUIREMENTS
- Deterministic script execution logs present in workspace.
- Passage through independent validators before handoff.
- Verification of synchronized triad on disk.

---

## COMPLETION CRITERIA
- Domain outputs completely generated and saved on disk.
- Zero validator errors across numerical and reporting consistency.

---

## FAILURE CONDITIONS
- Discrepancy between calculated data and narrative text.
- Missing required outputs or non-ASCII filenames on disk.
- Unhandled model errors or failed validator checks.
"""


def create_agent(
    name: Optional[str] = None,
    role: Optional[str] = None,
    description: Optional[str] = None,
    skills: Optional[List[str]] = None,
    mission: Optional[str] = None,
    decision_rules: Optional[List[str]] = None,
    anti_patterns: Optional[List[str]] = None,
    target_dir: Optional[str] = None,
    # Canonical modern options
    spec: Optional[AgentSpec] = None,
    tools: Optional[List[str]] = None,
    mainAgent: Optional[bool] = None,
    subagent: Optional[bool] = None,
    model: Optional[str] = None,
    commandExecutionPolicy: Optional[str] = None,
    agents: Optional[List[str]] = None,
    mcpServers: Optional[List[str]] = None,
    inheritCustomizations: Optional[bool] = None,
    create_symlink: bool = False,
    validate: bool = True,
    allow_name_collision: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Creates and writes a verified agent specification package to disk in canonical directory-form:
    1. Dedicated directory: target_dir/<name>/
    2. Co-located runtime prompt: target_dir/<name>/agent.md
    3. Co-located 12-section contract: target_dir/<name>/contract.md
    """
    if "command_execution_policy" in kwargs:
        raise AgentValidationError(
            "Deprecated field 'command_execution_policy' detected. Use canonical camelCase 'commandExecutionPolicy'."
        )

    if spec is None:
        agent_name = name or ""
        agent_role = role or ""
        agent_desc = description or ""
        agent_skills = skills or []
        agent_mission = mission or f"Execute domain analytical workflows for {agent_role}."
        agent_rules = decision_rules or ["Always execute deterministic scripts on real data."]
        agent_anti = anti_patterns

        is_main = mainAgent if mainAgent is not None else False
        is_sub = subagent if subagent is not None else True
        selected_model = model or ("pro" if is_main else "inherit")
        policy = commandExecutionPolicy or "request-review"

        default_tools = (
            [
                "invoke_subagent",
                "manage_subagents",
                "send_message",
                "view_file",
                "list_dir",
                "grep_search",
                "find_by_name",
                "write_to_file",
                "run_command",
                "ask_question",
            ]
            if is_main
            else [
                "view_file",
                "list_dir",
                "grep_search",
                "find_by_name",
                "write_to_file",
                "run_command",
            ]
        )
        selected_tools = tools if tools is not None else default_tools

        spec = AgentSpec(
            name=agent_name,
            description=agent_desc,
            role=agent_role,
            tools=selected_tools,
            mainAgent=is_main,
            subagent=is_sub,
            model=selected_model,
            commandExecutionPolicy=policy,
            skills=agent_skills,
            agents=agents or [],
            mcpServers=mcpServers or [],
            inheritCustomizations=inheritCustomizations,
            mission=agent_mission,
            decision_rules=agent_rules,
            anti_patterns=agent_anti,
        )

    if validate:
        validate_agent_spec(spec, allow_name_collision=allow_name_collision)

    out_dir = target_dir or AGENTS_DIR
    agent_dir = os.path.join(out_dir, spec.name)
    os.makedirs(agent_dir, exist_ok=True)

    agent_file = os.path.join(agent_dir, "agent.md")
    contract_file = os.path.join(agent_dir, "contract.md")

    md_content = generate_agent_markdown(
        name=spec.name,
        role=spec.role,
        description=spec.description,
        skills=spec.skills,
        mission=spec.mission or f"Execute domain workflows for {spec.role}.",
        decision_rules=spec.decision_rules or ["Execute domain tasks."],
        anti_patterns=spec.anti_patterns,
        spec=spec,
    )

    contract_content = generate_contract_markdown(
        name=spec.name,
        role=spec.role,
        mission=spec.mission or f"Execute domain workflows for {spec.role}.",
        skills=spec.skills,
        responsibilities=spec.responsibilities,
        non_responsibilities=spec.non_responsibilities,
        forbidden_actions=spec.forbidden_actions,
    )

    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(contract_file, "w", encoding="utf-8") as f:
        f.write(contract_content)

    # Optional flat symlink only if explicitly requested
    symlink_path = os.path.join(out_dir, f"{spec.name}.md")
    if create_symlink:
        if os.path.islink(symlink_path) or os.path.exists(symlink_path):
            os.remove(symlink_path)
        os.symlink(f"{spec.name}/agent.md", symlink_path)

    return {
        "status": "SUCCESS",
        "agent_name": spec.name,
        "agent_dir": agent_dir,
        "agent_file": agent_file,
        "contract_file": contract_file,
        "file_path": agent_file,
        "size_bytes": len(md_content.encode("utf-8")),
        "spec": spec.to_dict(),
    }


def get_all_target_agent_specs() -> Dict[str, AgentSpec]:
    """
    Returns the authoritative dictionary of 22 target AgentSpecs:
    7 Durable Agents (Tier 1 & Tier 2) and 15 Specialist Subagents (Tier 3 & Tier 4).
    """
    specs: Dict[str, AgentSpec] = {
        # DURABLE AGENTS (7)
        "digital-saber": AgentSpec(
            name="digital-saber",
            role="Research Project Lead, Cognitive Architect & Digital Twin",
            description="Master Research Project Lead, Cognitive Architect, and Digital Twin of Saber Ghaderi. Orchestrates multi-agent academic research, statistical consulting, and dissertation defense preparation.",
            mainAgent=True,
            subagent=False,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command", "ask_question",
            ],
            skills=["digital-twin-academic-consultant", "academic-suite-orchestrator", "thesis-integrity-auditor"],
            agents=["methodology-expert", "statistical-expert", "academic-writer", "evidence-auditor", "final-judge"],
            inheritCustomizations=True,
        ),
        "academic-orchestrator": AgentSpec(
            name="academic-orchestrator",
            role="Master Academic Orchestrator & Research Project Lead",
            description="Primary academic master conductor and research project lead. Understands holistic research requirements, decomposes multi-chapter pipelines into bounded micro-stages, maps capabilities to skills and specialist subagents, delegates with strict context isolation, tracks artifact dependencies, coordinates adversarial validation, manages retry loops, and synthesizes final deliverables.",
            mainAgent=True,
            subagent=False,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command", "ask_question",
            ],
            skills=["academic-suite-orchestrator", "digital-twin-academic-consultant", "thesis-integrity-auditor"],
            agents=["methodology-expert", "statistical-expert", "academic-writer", "evidence-auditor", "final-judge", "data-agent", "statistics-agent", "research-agent", "validation-agent"],
            inheritCustomizations=True,
        ),
        "methodology-expert": AgentSpec(
            name="methodology-expert",
            role="Research Methodology, Experimental Design & Power Authority",
            description="Specialist subagent for research methodology, experimental design, sampling power determination (G*Power), and internal/external validity safeguards in psychology and behavioral sciences.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command",
            ],
            skills=["methodology-review", "gpower-sample-size-calculator", "persian-proposal-builder"],
            agents=["research-agent", "literature-expert", "intervention-designer", "qualitative-analyst"],
            inheritCustomizations=True,
        ),
        "statistical-expert": AgentSpec(
            name="statistical-expert",
            role="Statistical Modeling, Parametric Estimation & Inference Authority",
            description="Specialist subagent for statistical analysis planning, hypothesis testing determination, parametric assumption verification sequences, and execution script generation in psychology and behavioral sciences.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command",
            ],
            skills=["sem", "cfa", "mediation", "moderation", "regression", "statistical-data-analyst"],
            agents=["statistics-agent", "psychometric-expert", "longitudinal-modmed-expert", "data-agent"],
            inheritCustomizations=True,
        ),
        "academic-writer": AgentSpec(
            name="academic-writer",
            role="Persian Rhetoric, Inverted-Triangle Architecture & OpenXML Drafter",
            description="Master academic chapter drafter and Persian rhetoric specialist. Formulates defense-ready thesis chapters using Saber's 5-part epistemic paragraph structure, natural cadence variability (CV >= 0.50), and pristine OpenXML typography.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "replace_file_content", "run_command",
            ],
            skills=["chapter-4-writing", "persian-literature-review-builder", "persian-discussion-builder", "persian-thesis-builder", "ai-academic-tone-polisher", "apa-reporting"],
            agents=["research-agent", "literature-expert"],
            inheritCustomizations=True,
        ),
        "evidence-auditor": AgentSpec(
            name="evidence-auditor",
            role="Epistemic Evidence, Bibliographic Reconciliation & Anti-Plagiarism Authority",
            description="Epistemic integrity and citation verification subagent auditing bidirectional in-text to bibliography concordance, Irandoc similarity compliance (< 20%), and robotic AI cliche elimination.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command",
            ],
            skills=["thesis-integrity-auditor", "irandoc-plagiarism-reducer", "academic-reference-extractor"],
            agents=["results-auditor", "academic-challenger"],
            inheritCustomizations=True,
        ),
        "final-judge": AgentSpec(
            name="final-judge",
            role="Viva Voce Defense Simulator, Institutional Gatekeeper & Release Authority",
            description="Final dissertation defense committee simulator, viva voce cross-examiner, and administrative human-in-the-loop release gatekeeper.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=[
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command",
            ],
            skills=["thesis-integrity-auditor", "persian-defense-presentation-builder"],
            agents=["validation-agent", "statistical-auditor", "academic-challenger"],
            inheritCustomizations=True,
        ),

        # SUBAGENTS (15)
        "research-agent": AgentSpec(
            name="research-agent",
            role="Scientific Literature Harvester & Research Question Architect",
            description="Specialized domain subagent for scientific literature harvesting, research question formulation, experimental and quasi-experimental research design, methodology specification, statistical power determination (G*Power), epistemic evidence synthesis, and citation integrity.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["literature-review", "literature-harvester", "gpower-sample-size-calculator"],
            agents=[],
            inheritCustomizations=True,
        ),
        "literature-expert": AgentSpec(
            name="literature-expert",
            role="Literature Synthesis & Bibliometric Matrix Specialist",
            description="Specialist subagent for multi-database literature harvesting, empirical parameter extraction (N, design, scales), epistemic evidence weighting, and theoretical mechanism synthesis for Chapters 2 and 5.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["literature-harvester", "literature-review", "bibliometric-network-analyst"],
            agents=[],
            inheritCustomizations=True,
        ),
        "journal-strategist": AgentSpec(
            name="journal-strategist",
            role="Academic Journal Matching & Peer-Review Rebuttal Specialist",
            description="Specialist subagent for academic journal article packaging, target journal selection, and peer-review rebuttal management.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["journal-submission-assistant", "academic-article-writer"],
            agents=[],
            inheritCustomizations=True,
        ),
        "meta-analyst": AgentSpec(
            name="meta-analyst",
            role="PRISMA 2020 Systematic Review & Quantitative Meta-Analyst",
            description="Specialist subagent for PRISMA 2020 systematic literature reviews, Cochrane RoB 2 risk of bias evaluations, and quantitative meta-analysis.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["systematic-review-meta-analyst", "gpower-sample-size-calculator"],
            agents=[],
            inheritCustomizations=True,
        ),
        "data-agent": AgentSpec(
            name="data-agent",
            role="Raw Data Screening, Reverse-Coding & Psychometric Simulator",
            description="Specialized domain subagent for raw dataset ingestion, data discovery, schema mapping, data quality screening, missing value diagnostics (Little's MCAR), reverse-coding from 4,880 validated instruments, variable transformations, psychometric simulation, and data integrity verification.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["data-cleaning", "data-audit", "psychometric-scale-resolver", "psychometric-data-simulator"],
            agents=[],
            inheritCustomizations=True,
        ),
        "data-curator": AgentSpec(
            name="data-curator",
            role="Dataset Quality Diagnostics, Outlier & Missing Data Specialist",
            description="Specialist subagent for raw dataset ingestion, missing data pattern diagnosis (MCAR/MAR/MNAR), unengaged response filtering, multivariate outlier screening (Mahalanobis D2, Cook's distance), demographic standardization, and data dictionary compilation.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["data-audit", "data-cleaning", "descriptive-statistics"],
            agents=[],
            inheritCustomizations=True,
        ),
        "statistics-agent": AgentSpec(
            name="statistics-agent",
            role="Inferential Modeling, Parametric Hypothesis Testing & SEM Specialist",
            description="Specialized domain subagent for inferential statistical analysis planning, parametric assumption verification sequences, deterministic Python and R execution, advanced statistical modeling (ANCOVA, RM-ANOVA, PROCESS bootstrap mediation, SEM), results extraction, APA 7 tables, and 300-DPI figures.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["statistical-data-analyst", "regression", "mediation", "moderation", "descriptive-statistics", "reliability-analysis"],
            agents=[],
            inheritCustomizations=True,
        ),
        "psychometric-expert": AgentSpec(
            name="psychometric-expert",
            role="Psychometric Resolution, Classical Test Theory & IRT Specialist",
            description="Specialist subagent for psychometric instrument resolution, Classical Test Theory (CTT), Item Response Theory (IRT), Confirmatory Factor Analysis (CFA), and scale construct validation.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["psychometric-scale-validator", "cfa", "psychometric-scale-resolver", "reliability-analysis"],
            agents=[],
            inheritCustomizations=True,
        ),
        "longitudinal-modmed-expert": AgentSpec(
            name="longitudinal-modmed-expert",
            role="3-Wave Longitudinal Moderated Mediation Specialist",
            description="Specialist subagent for 3-wave longitudinal moderated mediation modeling (Cole & Maxwell, Hayes PROCESS Model 7/14 over time).",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["longitudinal-moderated-mediation", "mediation", "apa-reporting"],
            agents=[],
            inheritCustomizations=True,
        ),
        "intervention-designer": AgentSpec(
            name="intervention-designer",
            role="Clinical Protocol, Manualization & Fidelity Sheet Specialist",
            description="Specialist subagent for designing standardized evidence-based psychological and educational intervention protocols and clinical manuals.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
            skills=["psychological-intervention-protocol-builder", "persian-proposal-builder"],
            agents=[],
            inheritCustomizations=True,
        ),
        "qualitative-analyst": AgentSpec(
            name="qualitative-analyst",
            role="Reflexive Thematic Analysis & Grounded Theory Specialist",
            description="Specialist subagent for qualitative data analysis, Reflexive Thematic Analysis (Braun & Clarke), and Grounded Theory (Strauss & Corbin).",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["qualitative-data-analyst"],
            agents=[],
            inheritCustomizations=True,
        ),
        "validation-agent": AgentSpec(
            name="validation-agent",
            role="Independent Quality Assurance & Pre-Flight Release Gatekeeper",
            description="Independent adversarial quality auditor, Viva Voce defense simulator, and institutional release gatekeeper. Conducts independent checking of draft deliverables, verifies cross-chapter consistency, validates institutional and APA 7 requirements, audits methodological validity, verifies statistical integrity via Multi-Signal Anomaly Index (MSAI), and verifies physical artifact completeness.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["thesis-integrity-auditor", "apa-reporting"],
            agents=[],
            inheritCustomizations=True,
        ),
        "results-auditor": AgentSpec(
            name="results-auditor",
            role="APA 7 Formatting, Mathematical Precision & Typography Auditor",
            description="Quality control subagent enforcing APA 7th Edition numerical precision, the leading zero rule, p-value reporting standards, 3-line table borders, and OpenXML OMML math equation preservation.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
            skills=["apa-reporting", "thesis-integrity-auditor"],
            agents=[],
            inheritCustomizations=True,
        ),
        "statistical-auditor": AgentSpec(
            name="statistical-auditor",
            role="Parametric Assumptions, Degrees of Freedom & MSAI Anomaly Auditor",
            description="Adversarial quality auditor subagent for statistical assumptions, degrees of freedom concordance, variance deflation, and Multi-Signal Anomaly Index (MSAI) scoring.",
            mainAgent=False,
            subagent=True,
            model="flash",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file", "run_command"],
            skills=["thesis-integrity-auditor", "data-audit"],
            agents=[],
            inheritCustomizations=True,
        ),
        "academic-challenger": AgentSpec(
            name="academic-challenger",
            role="Adversarial Methodology, Bias & Statistical Challenger",
            description="Specialist adversarial reviewer identifying methodology flaws, p-hacking, publication bias, unmeasured confounding, and statistical fragility before committee submission.",
            mainAgent=False,
            subagent=True,
            model="pro",
            commandExecutionPolicy="request-review",
            tools=["view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"],
            skills=["thesis-integrity-auditor", "methodology-review"],
            agents=[],
            inheritCustomizations=True,
        ),
    }
    return specs
