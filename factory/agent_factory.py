#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/agent_factory.py — Autonomous Subagent Specification Factory

Generates fully-specified, constitutional Antigravity subagents in .agents/agents/
with persistent cognitive roles, skill bindings, and decision-tree architectures.
"""

import os
import sys
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")


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


def generate_agent_markdown(
    name: str,
    role: str,
    description: str,
    skills: List[str],
    mission: str,
    decision_rules: List[str],
    anti_patterns: Optional[List[str]] = None
) -> str:
    """
    Generates the complete, standardized Markdown text for an Antigravity agent definition.
    """
    anti_patterns = anti_patterns or [
        "Never calculate statistics in your head (violates Directive 2).",
        "Never omit the Persian leading zero before decimals (violates Directive 4).",
        "Never skip the Pre-Flight Pipeline Declaration (violates Directive 1)."
    ]

    skills_yaml = "\n".join([f"- {s}" for s in skills])
    rules_md = "\n".join([f"{i+1}. {r}" for i, r in enumerate(decision_rules)])
    anti_md = "\n".join([f"- ❌ {ap}" for ap in anti_patterns])

    content = f"""---
name: {name}
description: >-
  {description}
role: {role}
skills:
{skills_yaml}
---

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


def create_agent(
    name: str,
    role: str,
    description: str,
    skills: List[str],
    mission: str,
    decision_rules: List[str],
    anti_patterns: Optional[List[str]] = None,
    target_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates and writes a verified agent specification to disk.
    """
    out_dir = target_dir or AGENTS_DIR
    os.makedirs(out_dir, exist_ok=True)
    file_path = os.path.join(out_dir, f"{name}.md")

    md_content = generate_agent_markdown(
        name=name,
        role=role,
        description=description,
        skills=skills,
        mission=mission,
        decision_rules=decision_rules,
        anti_patterns=anti_patterns
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {
        "status": "SUCCESS",
        "agent_name": name,
        "file_path": file_path,
        "size_bytes": len(md_content.encode("utf-8"))
    }
