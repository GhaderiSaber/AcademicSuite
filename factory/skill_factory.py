#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/skill_factory.py — Autonomous Skill Scaffolding Factory

Generates modular Antigravity skills strictly adhering to Directive 18:
Single-View Invariant (<= 500 lines, <= 40,000 bytes per SKILL.md),
Progressive Disclosure to references/, and deterministic Python scripts in scripts/.
"""

import os
import sys
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(ROOT_DIR, ".agents", "skills")

MAX_LINES = 500
MAX_BYTES = 40000


def generate_skill_markdown(
    name: str,
    description: str,
    sections: Dict[str, str],
    reference_links: Optional[List[str]] = None
) -> str:
    """
    Constructs SKILL.md content adhering to Directive 18.
    """
    ref_md = ""
    if reference_links:
        ref_items = "\n".join([f"- [{os.path.basename(r)}]({r})" for r in reference_links])
        ref_md = f"\n\n## 📚 Modular References & Specifications\n{ref_items}\n"

    body_parts = []
    for heading, text in sections.items():
        body_parts.append(f"## {heading}\n\n{text.strip()}")

    body_combined = "\n\n".join(body_parts)

    content = f"""---
name: {name}
description: >-
  {description}
---

# `{name}` — Skill Specification

{body_combined}
{ref_md}
"""
    return content


def create_skill(
    name: str,
    description: str,
    sections: Dict[str, str],
    script_name: Optional[str] = None,
    script_code: Optional[str] = None,
    references: Optional[Dict[str, str]] = None,
    target_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scaffolds and validates a full modular skill directory with scripts/ and references/.
    """
    base_skills_dir = target_dir or SKILLS_DIR
    skill_dir = os.path.join(base_skills_dir, name)
    scripts_dir = os.path.join(skill_dir, "scripts")
    refs_dir = os.path.join(skill_dir, "references")

    os.makedirs(skill_dir, exist_ok=True)
    os.makedirs(scripts_dir, exist_ok=True)
    os.makedirs(refs_dir, exist_ok=True)

    # 1. Write reference files if provided
    ref_paths = []
    if references:
        for ref_file, ref_content in references.items():
            rpath = os.path.join(refs_dir, ref_file)
            with open(rpath, "w", encoding="utf-8") as f:
                f.write(ref_content)
            ref_paths.append(f"references/{ref_file}")

    # 2. Write deterministic script if provided
    script_path = None
    if script_name and script_code:
        script_path = os.path.join(scripts_dir, script_name)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_code)

    # 3. Generate and validate SKILL.md
    skill_md = generate_skill_markdown(
        name=name,
        description=description,
        sections=sections,
        reference_links=ref_paths
    )

    lines_count = len(skill_md.splitlines())
    bytes_count = len(skill_md.encode("utf-8"))

    if lines_count > MAX_LINES:
        raise ValueError(
            f"Directive 18 Violation: SKILL.md has {lines_count} lines (max {MAX_LINES}). "
            "Modularize extended content into references/."
        )
    if bytes_count > MAX_BYTES:
        raise ValueError(
            f"Directive 18 Violation: SKILL.md has {bytes_count} bytes (max {MAX_BYTES}). "
            "Modularize extended content into references/."
        )

    skill_file = os.path.join(skill_dir, "SKILL.md")
    with open(skill_file, "w", encoding="utf-8") as f:
        f.write(skill_md)

    return {
        "status": "SUCCESS",
        "skill_name": name,
        "skill_dir": skill_dir,
        "skill_file": skill_file,
        "script_path": script_path,
        "lines": lines_count,
        "bytes": bytes_count
    }
