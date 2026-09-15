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
    if skills_dir is None:
        base_repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        skills_dir = os.path.join(base_repo, ".agents", "skills")

    skill_files = glob.glob(os.path.join(skills_dir, "*", "SKILL.md"))
    if not skill_files:
        return {"passed": True, "total_checked": 0, "violations": [], "message": f"No SKILL.md found in {skills_dir}"}

    violations = []
    inspected = []

    for sf in sorted(skill_files):
        skill_name = os.path.basename(os.path.dirname(sf))
        try:
            with open(sf, "r", encoding="utf-8") as f:
                lines = f.readlines()
            line_count = len(lines)
            byte_size = os.path.getsize(sf)
        except Exception as e:
            violations.append({
                "skill": skill_name,
                "file": sf,
                "error": str(e)
            })
            continue

        inspected.append((skill_name, line_count, byte_size))

        if line_count > MAX_LINES_LIMIT or byte_size > MAX_BYTES_LIMIT:
            violations.append({
                "skill": skill_name,
                "file": sf,
                "line_count": line_count,
                "byte_size": byte_size,
                "max_lines": MAX_LINES_LIMIT,
                "max_bytes": MAX_BYTES_LIMIT,
                "line_overflow": max(0, line_count - MAX_LINES_LIMIT),
                "byte_overflow": max(0, byte_size - MAX_BYTES_LIMIT)
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

    print(f"Audited {result['total_checked']} skills in .agents/skills/:")
    if result["passed"]:
        print(f"✅ All {result['total_checked']} skills are within single-view limits (<= {MAX_LINES_LIMIT} lines, <= {MAX_BYTES_LIMIT} bytes).")
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
