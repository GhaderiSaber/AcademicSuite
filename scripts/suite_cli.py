#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcademicSuite Unified CLI & Skill Linter Tooling (scripts/suite_cli.py)
=====================================================================
Centralized CLI for managing, validating, scaffolding, and auditing
the 27+ academic skills in GhaderiSaber/AcademicSuite.

Inspired by dzarezenko/ai-academic-skills init_skill.py and Agent Skills open standard.

Usage:
  python3 scripts/suite_cli.py list-skills
  python3 scripts/suite_cli.py validate-skills
  python3 scripts/suite_cli.py validate-schemas
  python3 scripts/suite_cli.py init-skill <name> --category <category>
"""

import os
import sys
import re
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Root paths
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = WORKSPACE_ROOT / ".agents" / "skills"
SCHEMAS_DIR = WORKSPACE_ROOT / ".agents" / "shared" / "schemas"

VALID_CATEGORIES = [
    "methodology-and-proposal",
    "translation-and-literature",
    "psychometrics-and-measurement",
    "statistical-analysis",
    "thesis-and-article-writing",
    "academic-integrity-and-audit",
    "defense-and-presentation",
    "consulting-and-orchestration",
    "systematic-review-meta-analysis"
]

SKILL_NAME_REGEX = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")

def parse_yaml_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Parse basic YAML frontmatter from markdown without external pyyaml dependency."""
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    
    fm_text = parts[1]
    body = parts[2]
    
    metadata = {}
    current_key = None
    multiline_val = []
    
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        
        # Check key: value
        match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if match:
            if current_key and multiline_val:
                metadata[current_key] = "\n".join(multiline_val).strip()
                multiline_val = []
            
            key, val = match.groups()
            current_key = key.strip()
            val = val.strip()
            if val in (">", ">-", "|", "|-"):
                multiline_val = []
            else:
                metadata[current_key] = val.strip("\"'")
                current_key = None
        elif current_key is not None:
            multiline_val.append(line.strip())
            
    if current_key and multiline_val:
        metadata[current_key] = " ".join(multiline_val).strip()
        
    return metadata, body


def validate_skill_name(name: str) -> List[str]:
    """Validate skill name per Agent Skills open specification."""
    errors = []
    if not name:
        errors.append("Skill name cannot be empty.")
        return errors
    if len(name) > 64:
        errors.append(f"Skill name exceeds 64 characters (length: {len(name)}).")
    if not SKILL_NAME_REGEX.match(name):
        errors.append("Skill name must be lowercase alphanumeric with single hyphens.")
    if "--" in name:
        errors.append("Skill name must not contain consecutive hyphens.")
    return errors


def audit_skills() -> int:
    """Audit all skills in .agents/skills for specification compliance and script syntax."""
    print("=" * 80)
    print("  ACADEMIC SUITE — SKILL SPECIFICATION & QUALITY AUDITOR")
    print("=" * 80)
    
    if not SKILLS_DIR.exists():
        print(f"[ERROR] Skills directory not found: {SKILLS_DIR}")
        return 1
        
    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    total_skills = len(skill_dirs)
    passed_skills = 0
    total_errors = 0
    
    for skill_dir in skill_dirs:
        skill_name = skill_dir.name
        skill_file = skill_dir / "SKILL.md"
        issues = []
        
        # 1. Name check
        name_errs = validate_skill_name(skill_name)
        issues.extend(name_errs)
        
        # 2. SKILL.md existence
        if not skill_file.exists():
            issues.append("Missing SKILL.md")
        else:
            try:
                content = skill_file.read_text(encoding="utf-8")
                fm, body = parse_yaml_frontmatter(content)
                if not fm:
                    issues.append("Missing or malformed YAML frontmatter")
                else:
                    if "name" not in fm:
                        issues.append("YAML missing 'name' field")
                    elif fm["name"] != skill_name:
                        issues.append(f"YAML name '{fm['name']}' != folder name '{skill_name}'")
                    
                    if "description" not in fm or len(fm["description"]) < 20:
                        issues.append("YAML description missing or too short (<20 chars)")
            except Exception as e:
                issues.append(f"Failed reading SKILL.md: {e}")
                
        # 3. Python scripts check
        scripts_dir = skill_dir / "scripts"
        py_scripts_count = 0
        if scripts_dir.exists():
            for py_file in scripts_dir.glob("*.py"):
                py_scripts_count += 1
                try:
                    code = py_file.read_text(encoding="utf-8")
                    ast.parse(code, filename=str(py_file))
                except SyntaxError as se:
                    issues.append(f"SyntaxError in {py_file.name}: {se.msg} (line {se.lineno})")
                except Exception as e:
                    issues.append(f"Error parsing {py_file.name}: {e}")
                    
        # Report
        status_icon = "✓ PASS" if not issues else "✗ FAIL"
        if not issues:
            passed_skills += 1
            print(f"[{status_icon}] {skill_name:<40} ({py_scripts_count} scripts)")
        else:
            total_errors += len(issues)
            print(f"[{status_icon}] {skill_name:<40} ({len(issues)} issues)")
            for issue in issues:
                print(f"       ↳ {issue}")
                
    print("-" * 80)
    print(f"Summary: {passed_skills}/{total_skills} skills fully compliant. Total issues: {total_errors}")
    print("=" * 80)
    return 0 if total_errors == 0 else 1


def list_skills():
    """List all registered skills with their summary and script counts."""
    print("=" * 80)
    print("  ACADEMIC SUITE — SKILL REGISTRY INVENTORY")
    print("=" * 80)
    skill_dirs = sorted([d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")])
    print(f"{'#':<3} {'Skill Name':<45} {'Scripts':<8} {'Frontmatter'}")
    print("-" * 80)
    for idx, sdir in enumerate(skill_dirs, 1):
        skill_file = sdir / "SKILL.md"
        has_fm = "No"
        if skill_file.exists():
            content = skill_file.read_text(encoding="utf-8")
            fm, _ = parse_yaml_frontmatter(content)
            if fm and "name" in fm:
                has_fm = "Yes"
        scripts_count = len(list((sdir / "scripts").glob("*.py"))) if (sdir / "scripts").exists() else 0
        print(f"{idx:<3} {sdir.name:<45} {scripts_count:<8} {has_fm}")
    print("=" * 80)


def validate_schemas():
    """Verify that schemas in shared/schemas are syntactically valid JSON."""
    print("=" * 80)
    print("  ACADEMIC SUITE — SHARED CONTRACT SCHEMAS VALIDATION")
    print("=" * 80)
    if not SCHEMAS_DIR.exists():
        print(f"Schema dir {SCHEMAS_DIR} does not exist.")
        return 1
    schemas = list(SCHEMAS_DIR.glob("*.json"))
    valid = 0
    for s in schemas:
        try:
            with open(s, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            print(f"[✓ VALID] {s.name:<35} Title: {data.get('title', 'N/A')}")
            valid += 1
        except Exception as e:
            print(f"[✗ ERROR] {s.name:<35} Error: {e}")
    print(f"\nTotal: {valid}/{len(schemas)} schemas valid.")
    return 0 if valid == len(schemas) else 1


def init_skill(skill_name: str, category: str):
    """Scaffold a new skill following the AcademicSuite standard layout."""
    errs = validate_skill_name(skill_name)
    if errs:
        for err in errs:
            print(f"[ERROR] {err}")
        return 1
        
    target_dir = SKILLS_DIR / skill_name
    if target_dir.exists():
        print(f"[ERROR] Skill '{skill_name}' already exists at {target_dir}")
        return 1
        
    for sub in ["scripts", "references", "examples", "tests"]:
        (target_dir / sub).mkdir(parents=True, exist_ok=True)
        
    title = " ".join(w.capitalize() for w in skill_name.split("-"))
    skill_md = f"""---
name: {skill_name}
description: >-
  [TODO: Comprehensive description of the skill, including trigger keywords,
  domain purpose, and primary deliverables. Must be >= 20 characters.]
---

# `{skill_name}` — {title}

## 1. When to Activate This Skill
[TODO: List activation scenarios and triggers]

## 2. Core Methodological Standards & Theoretical Benchmarks
[TODO: Define APA 7th, empirical formulas, and domain rules]

## 3. CLI Command Reference
```bash
python3 .agents/skills/{skill_name}/scripts/{skill_name.replace('-', '_')}_engine.py --help
```

## 4. Multi-Modal Deliverables
1. Professional `.docx` reports formatted with native BiDi OpenXML.
2. 300-DPI visual figures (`.png`).
3. Comprehensive Excel audit matrix (`.xlsx`).
4. Machine-readable JSON summary (`.json`).
"""
    (target_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    
    script_slug = skill_name.replace("-", "_")
    script_py = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
{title} Engine ({script_slug}_engine.py)
AcademicSuite: Automated Research & Consultancy Engine
Author: Saber Ghaderi
\"\"\"

import os
import sys
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="{title} Engine")
    parser.add_argument("--json", type=str, help="Input payload JSON")
    parser.add_argument("--out-dir", type=str, default="./output", help="Output directory")
    args = parser.parse_args()
    print("AcademicSuite: Running {title} Engine...")

if __name__ == "__main__":
    main()
"""
    (target_dir / "scripts" / f"{script_slug}_engine.py").write_text(script_py, encoding="utf-8")
    print(f"[✓ SUCCESS] Created new skill scaffold at: {target_dir}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Unified CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("list-skills", help="List all skills in suite")
    subparsers.add_parser("validate-skills", help="Audit all skills for spec compliance")
    subparsers.add_parser("validate-schemas", help="Verify shared JSON schemas")
    
    init_parser = subparsers.add_parser("init-skill", help="Scaffold a new skill")
    init_parser.add_argument("name", type=str, help="Kebab-case skill name")
    init_parser.add_argument("--category", type=str, default="methodology-and-proposal", choices=VALID_CATEGORIES)
    
    args = parser.parse_args()
    if args.command == "list-skills":
        list_skills()
    elif args.command == "validate-skills":
        sys.exit(audit_skills())
    elif args.command == "validate-schemas":
        sys.exit(validate_schemas())
    elif args.command == "init-skill":
        sys.exit(init_skill(args.name, args.category))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
