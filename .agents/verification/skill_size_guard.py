#!/usr/bin/env python3
"""
skill_size_guard.py — Skill Modularity & Context Budget Guard

Enforces Directive 18: Ensures all SKILL.md files in .agents/skills/ remain
well within Antigravity's single-view tool thresholds (800 lines / 46,080 bytes)
by enforcing a safe ceiling:
- Max lines: 500 lines
- Max bytes: 40,000 bytes (~39 KB)

Any skill exceeding these bounds must be modularized using the references/
subdirectory to maintain 100% single-call readability for autonomous agents.
"""

import os
import sys
import glob
from typing import Dict, Any, List, Tuple

MAX_LINES_LIMIT = 500
MAX_BYTES_LIMIT = 40000

def audit_skill_sizes(skills_dir: str = None) -> Dict[str, Any]:
    base_repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if skills_dir is None:
        skills_dir = os.path.join(base_repo, ".agents", "skills")

    skill_files = glob.glob(os.path.join(skills_dir, "*", "SKILL.md"))
    violations = []
    inspected = []

    # 1. Audit Skills
    for sf in sorted(skill_files):
        skill_name = os.path.basename(os.path.dirname(sf))
        try:
            with open(sf, "r", encoding="utf-8") as f:
                lines = f.readlines()
            line_count = len(lines)
            byte_size = os.path.getsize(sf)
        except Exception as e:
            violations.append({"type": "skill", "name": skill_name, "file": sf, "error": str(e)})
            continue

        inspected.append(("skill:" + skill_name, line_count, byte_size))
        if line_count > MAX_LINES_LIMIT or byte_size > MAX_BYTES_LIMIT:
            violations.append({
                "type": "skill",
                "name": skill_name,
                "file": sf,
                "line_count": line_count,
                "byte_size": byte_size,
                "max_lines": MAX_LINES_LIMIT,
                "max_bytes": MAX_BYTES_LIMIT,
                "line_overflow": max(0, line_count - MAX_LINES_LIMIT),
                "byte_overflow": max(0, byte_size - MAX_BYTES_LIMIT)
            })

    # 2. Audit Subagents (.agents/agents/*.md)
    agents_dir = os.path.join(base_repo, ".agents", "agents")
    if os.path.exists(agents_dir):
        for af in sorted(glob.glob(os.path.join(agents_dir, "*.md"))):
            aname = os.path.basename(af)
            try:
                with open(af, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                lcnt = len(lines)
                bsz = os.path.getsize(af)
            except Exception as e:
                violations.append({"type": "agent", "name": aname, "file": af, "error": str(e)})
                continue
            inspected.append(("agent:" + aname, lcnt, bsz))
            if lcnt > 300 or bsz > 25000:
                violations.append({
                    "type": "agent",
                    "name": aname,
                    "file": af,
                    "line_count": lcnt,
                    "byte_size": bsz,
                    "max_lines": 300,
                    "max_bytes": 25000
                })

    # 3. Audit AGENTS.md at root
    agents_md = os.path.join(base_repo, "AGENTS.md")
    if os.path.exists(agents_md):
        with open(agents_md, "r", encoding="utf-8") as f:
            lines = f.readlines()
        lcnt = len(lines)
        bsz = os.path.getsize(agents_md)
        inspected.append(("AGENTS.md", lcnt, bsz))
        if lcnt > 200 or bsz > 20000:
            violations.append({
                "type": "constitution",
                "name": "AGENTS.md",
                "file": agents_md,
                "line_count": lcnt,
                "byte_size": bsz,
                "max_lines": 200,
                "max_bytes": 20000
            })

    passed = len(violations) == 0
    return {
        "passed": passed,
        "total_checked": len(inspected),
        "violations": violations,
        "inspected": inspected
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit SKILL.md sizes against single-view limits.")
    parser.add_argument("--dir", type=str, default=None, help="Path to .agents/skills directory")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    result = audit_skill_sizes(args.dir)

    if args.json:
        import json
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["passed"] else 1)

    print(f"Audited {result['total_checked']} items (skills, agents, constitution):")
    if result["passed"]:
        print(f"✅ All {result['total_checked']} items are within single-view context limits.")
        sys.exit(0)
    else:
        print(f"❌ {len(result['violations'])} skill(s) exceeded the single-view threshold:\n")
        for v in result["violations"]:
            print(f"  - {v['skill']}: {v['line_count']} lines (limit: {v['max_lines']}), {v['byte_size']} bytes (limit: {v['max_bytes']})")
            print(f"    Path: {v['file']}")
            print("    Remediation: Modularize extended rules, contracts, and examples into the 'references/' directory.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
