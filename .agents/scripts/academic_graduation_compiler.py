#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_graduation_compiler.py — AcademicSuite Immediate Graduation Compiler ("The Hands")

Constitutional Invariant (Directives 12.1, 18, 19, 21):
- Directive 12.1: Python scripts are strictly deterministic tools ("The Hands").
- Directive 18: Strict single-view ceilings (max 500 lines, 40,000 bytes per SKILL.md).
- Directive 19: Agent decides, Script computes & mutates.
- Directive 21: Dual-Track Immediate Ingestion Protocol — Track 1 immediate graduation.

Executes deterministic markdown synthesis, context budget enforcement (Directive 18),
and Git lifecycle synchronization across canonical skills and rules.
"""

import os
import sys
import re
import json
import shutil
import argparse
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts")]:
    if p not in sys.path:
        sys.path.insert(0, p)

MAX_SKILL_LINES = 500
MAX_SKILL_BYTES = 40000
WARNING_SKILL_LINES = 470

CAPABILITY_TO_SKILLS = {
    "chapter5": ["persian-discussion-builder", "chapter-5-writing"],
    "chapter4": ["chapter-4-writing", "apa-reporting"],
    "discussion": ["persian-discussion-builder", "chapter-5-writing"],
    "writing": ["chapter-4-writing", "persian-discussion-builder", "apa-reporting"],
    "academic-writer": ["chapter-4-writing", "persian-discussion-builder", "apa-reporting"],
    "footnote": ["persian-discussion-builder", "apa-reporting"],
    "openxml": ["apa-reporting", "persian-discussion-builder", "persian-thesis-builder"],
    "typography": ["apa-reporting", "persian-discussion-builder", "ai-academic-tone-polisher"],
    "mediation": ["mediation"],
    "moderation": ["moderation"],
    "sem": ["sem"],
    "psychometrics": ["psychometric-scale-validator", "cfa", "reliability-analysis"],
    "ancova": ["assumption-testing", "statistical-data-analyst"],
    "regression": ["regression", "assumption-testing"],
    "evidence": ["persian-literature-review-builder", "literature-review"],
    "apa7": ["apa-reporting"],
}


class AcademicGraduationCompiler:
    """Deterministic compilation engine ('The Hands') for Track 1 invariant graduation."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or os.environ.get("ACADEMIC_SUITE_BASE_DIR") or ROOT_DIR)
        cand_agents = os.path.join(self.base_dir, ".agents")
        self.agents_dir = cand_agents if os.path.isdir(cand_agents) else self.base_dir
        self.skills_dir = os.path.join(self.agents_dir, "skills")
        self.rules_file = os.path.join(self.agents_dir, "plugins", "academic-suite", "rules", "AGENTS.md")
        self.snapshots_dir = os.path.join(self.agents_dir, "learning", "snapshots", "skills")
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def resolve_targets(
        self,
        capability: Optional[str] = None,
        skills: Optional[List[str]] = None,
        is_global: bool = False
    ) -> List[str]:
        """Resolve canonical absolute file paths targeted for graduation."""
        targets = []
        if is_global or not capability or capability.lower() in ("general", "universal"):
            if os.path.isfile(self.rules_file):
                targets.append(self.rules_file)

        target_skills = list(skills or [])
        if capability:
            norm_cap = capability.lower().replace("-", "").replace("_", "")
            for k, s_list in CAPABILITY_TO_SKILLS.items():
                if k.lower() in norm_cap or norm_cap in k.lower():
                    for s in s_list:
                        if s not in target_skills:
                            target_skills.append(s)

        for s in target_skills:
            cand = os.path.join(self.skills_dir, s, "SKILL.md")
            if os.path.isfile(cand) and cand not in targets:
                targets.append(cand)

        if not targets and os.path.isfile(self.rules_file):
            targets.append(self.rules_file)

        return targets

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract substantive keywords for semantic synthesis and deduplication."""
        stop_words = {
            "always", "never", "must", "should", "rule", "invariant", "directive", "using",
            "with", "from", "that", "this", "these", "those", "when", "where", "into",
            "برای", "همیشه", "نباید", "باید", "است", "دارد", "شود", "کنید", "این", "استفاده"
        }
        words = re.findall(r'[a-zA-Z\u0600-\u06FF]{4,}', text.lower())
        return [w for w in words if w not in stop_words]

    def synthesize_markdown_rule(
        self,
        file_path: str,
        item_id: str,
        statement: str,
        category: str = "Principle",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Safely synthesize an invariant into target markdown with snapshot and budget checks."""
        if not os.path.isfile(file_path):
            return {"file": file_path, "status": "SKIPPED_NOT_FOUND", "success": False}

        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        orig_lines = original_content.splitlines()
        orig_line_count = len(orig_lines)
        orig_byte_count = len(original_content.encode("utf-8"))

        # 1. Create Pre-Mutation Snapshot
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(os.path.dirname(file_path)) or os.path.basename(file_path)
        snap_file = f"pre_grad_{base_name}_{now_str}.md"
        snap_path = os.path.join(self.snapshots_dir, snap_file)
        if not dry_run:
            with open(snap_path, "w", encoding="utf-8") as sf:
                sf.write(original_content)

        # 2. Safety Rule 1: Synthesis, Not Stacking
        clean_statement = statement.strip().rstrip(".")
        clean_cat = category.strip().capitalize()
        new_bullet = f"- **{clean_cat} ({item_id})**: {clean_statement}."

        is_skill = file_path.endswith("SKILL.md")
        target_section_header = "## 🧠 Active Learned Behavioral Invariants" if is_skill else "## 1. Radical Honesty & Pipeline Enforcement"

        updated_content = original_content
        kw_new = set(self._extract_keywords(clean_statement))

        if target_section_header in updated_content:
            # Check for existing related bullet to merge/strengthen
            sec_pattern = rf"({re.escape(target_section_header)}[\s\S]*?)(?=\n## |\Z)"
            sec_match = re.search(sec_pattern, updated_content)
            if sec_match:
                full_section = sec_match.group(1)
                sec_lines = full_section.splitlines()
                merged = False
                for idx, line in enumerate(sec_lines):
                    if line.strip().startswith("- "):
                        kw_existing = set(self._extract_keywords(line))
                        overlap = kw_new.intersection(kw_existing)
                        if len(overlap) >= 2:
                            # Merge and strengthen existing bullet
                            sec_lines[idx] = f"- **{clean_cat} ({item_id})**: {clean_statement}."
                            merged = True
                            break
                if not merged:
                    sec_lines.append(new_bullet)

                new_section_str = "\n".join(sec_lines)
                updated_content = updated_content[:sec_match.start(1)] + new_section_str + updated_content[sec_match.end(1):]
        else:
            # Create section cleanly before final reference links or at end
            new_section_block = f"\n\n{target_section_header}\n{new_bullet}\n"
            updated_content = updated_content.rstrip() + new_section_block

        # 3. Safety Rule 2: Strict Single-View Ceiling (Directive 18)
        new_lines = updated_content.splitlines()
        new_line_count = len(new_lines)
        new_byte_count = len(updated_content.encode("utf-8"))
        offloaded = False

        if is_skill and (new_line_count > WARNING_SKILL_LINES or new_byte_count > 38000):
            skill_dir = os.path.dirname(file_path)
            refs_dir = os.path.join(skill_dir, "references")
            os.makedirs(refs_dir, exist_ok=True)
            refs_file = os.path.join(refs_dir, "learned_invariants.md")

            ref_entry = f"\n### Invariant {item_id} ({now_str})\n- **Category**: {clean_cat}\n- **Rule**: {clean_statement}.\n"
            if not dry_run:
                with open(refs_file, "a", encoding="utf-8") as rf:
                    rf.write(ref_entry)

            compact_bullet = f"- **{clean_cat} ({item_id})**: {clean_statement[:70]}... See [learned_invariants.md](references/learned_invariants.md)."
            updated_content = original_content.rstrip() + f"\n\n{target_section_header}\n{compact_bullet}\n"
            new_lines = updated_content.splitlines()
            new_line_count = len(new_lines)
            new_byte_count = len(updated_content.encode("utf-8"))
            offloaded = True

        # Ceiling violation check
        max_lines = MAX_SKILL_LINES if is_skill else 250
        max_bytes = MAX_SKILL_BYTES if is_skill else 25000
        if new_line_count > max_lines or new_byte_count > max_bytes:
            # Atomic rollback
            if not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
            return {
                "file": file_path,
                "status": "OVERFLOW_ROLLED_BACK",
                "success": False,
                "line_count": new_line_count,
                "max_lines": max_lines,
                "snapshot": snap_path
            }

        if not dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

        return {
            "file": file_path,
            "status": "GRADUATED_SUCCESS",
            "success": True,
            "orig_lines": orig_line_count,
            "new_lines": new_line_count,
            "orig_bytes": orig_byte_count,
            "new_bytes": new_byte_count,
            "offloaded": offloaded,
            "snapshot": snap_path
        }

    def git_sync(self, target_files: List[str], item_id: str, statement: str) -> Dict[str, Any]:
        """Execute atomic Git staging, semantic commit, and remote push (Safety Rule 3)."""
        summary = re.sub(r'[\r\n\t"\']+', ' ', statement).strip()[:50]
        commit_msg = f"feat(mentorship): graduate [{item_id}] {summary} [skip ci]"

        try:
            # 1. Stage files
            rel_files = [os.path.relpath(p, self.base_dir) for p in target_files if os.path.exists(p)]
            if not rel_files:
                return {"success": False, "reason": "No files to stage"}

            subprocess.run(["git", "add"] + rel_files, cwd=self.base_dir, check=True, capture_output=True, text=True)

            # 2. Check if git diff has staged changes
            diff_res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=self.base_dir)
            if diff_res.returncode == 0:
                # No changes staged
                return {"success": True, "committed": False, "pushed": False, "commit_hash": "HEAD"}

            # 3. Commit
            c_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.base_dir, check=True, capture_output=True, text=True)
            m_hash = re.search(r'\[(?:[a-zA-Z0-9_\-]+ )?([a-f0-9]{7,})\]', c_res.stdout)
            commit_hash = m_hash.group(1) if m_hash else "committed"

            # 4. Push to origin main
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=self.base_dir, capture_output=True, text=True, timeout=10)
            pushed = (push_res.returncode == 0)

            return {
                "success": True,
                "committed": True,
                "pushed": pushed,
                "commit_hash": commit_hash,
                "push_msg": push_res.stdout if pushed else push_res.stderr
            }
        except subprocess.TimeoutExpired:
            return {"success": True, "committed": True, "pushed": False, "reason": "Git push timed out (offline)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def graduate_item(
        self,
        item_id: str,
        statement: str,
        category: str = "Principle",
        capability: Optional[str] = None,
        skills: Optional[List[str]] = None,
        json_artifact_path: Optional[str] = None,
        is_global: bool = False,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """End-to-end Track 1 execution: target resolution -> synthesis -> guard -> git lifecycle."""
        targets = self.resolve_targets(capability=capability, skills=skills, is_global=is_global)
        grad_results = []
        all_passed = True

        for target in targets:
            res = self.synthesize_markdown_rule(
                file_path=target,
                item_id=item_id,
                statement=statement,
                category=category,
                dry_run=dry_run
            )
            grad_results.append(res)
            if not res.get("success"):
                all_passed = False

        git_res = {}
        if all_passed and auto_commit and not dry_run:
            files_to_commit = list(targets)
            if json_artifact_path and os.path.isfile(json_artifact_path):
                files_to_commit.append(json_artifact_path)
            git_res = self.git_sync(files_to_commit, item_id, statement)

        return {
            "item_id": item_id,
            "statement": statement,
            "category": category,
            "capability": capability,
            "targets": targets,
            "grad_results": grad_results,
            "all_passed": all_passed,
            "git": git_res
        }

    def graduate_from_json_file(
        self,
        json_path: str,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Graduates a lesson or anti-pattern JSON file directly into its matching SKILL.md or rules/AGENTS.md."""
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON artifact not found: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        item_id = data.get("lesson_id") or data.get("anti_pattern_id") or data.get("id") or os.path.splitext(os.path.basename(json_path))[0]
        if "lesson_id" in data or "lesson_type" in data or "LSN-" in item_id:
            category = "Lesson"
        elif "anti_pattern_id" in data or "AP-" in item_id:
            category = "Anti-Pattern"
        else:
            category = "Principle"

        statement = data.get("desired_behavior") or data.get("corrective_remedy") or data.get("generalization") or data.get("statement") or ""
        if not statement:
            statement = data.get("description", "")
        if not statement and category == "Anti-Pattern":
            defective = data.get("defective_pattern", "")
            remedy = data.get("corrective_remedy", "")
            statement = f"Prohibited: {defective}. Remedy: {remedy}" if defective and remedy else (defective or remedy)

        skills = data.get("related_skills") or []
        capability = data.get("capability") or data.get("target_agent")

        # Fallback keyword matching
        if not skills and not capability:
            for k in CAPABILITY_TO_SKILLS:
                if k in statement.lower() or k in item_id.lower():
                    capability = k
                    break

        is_global = (data.get("scope") == "cross-project" and not skills and not capability)

        res = self.graduate_item(
            item_id=item_id,
            statement=statement,
            category=category,
            capability=capability,
            skills=skills,
            json_artifact_path=json_path,
            is_global=is_global,
            auto_commit=auto_commit,
            dry_run=dry_run
        )

        if res.get("all_passed") and not dry_run:
            data["graduation_status"] = "GRADUATED"
            data["graduated_at"] = datetime.now(timezone.utc).isoformat()
            data["graduated_targets"] = res.get("targets", [])
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return res

    def compile_all_pending(
        self,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Scans all lessons and anti-patterns in .agents/learning/knowledge/ and graduates pending items."""
        knowledge_dir = os.path.join(self.agents_dir, "learning", "knowledge")
        results = []
        for subdir in ["lessons", "anti-patterns", "principles"]:
            s_path = os.path.join(knowledge_dir, subdir)
            if not os.path.isdir(s_path):
                continue
            for fname in sorted(os.listdir(s_path)):
                if fname.endswith(".json") and not fname.startswith("."):
                    f_full = os.path.join(s_path, fname)
                    try:
                        with open(f_full, "r", encoding="utf-8") as f:
                            d = json.load(f)
                        status = d.get("graduation_status")
                        track = d.get("graduation_track")
                        if status == "PENDING_GRADUATION" or track == "TRACK_1_IMMEDIATE_GRADUATION":
                            r = self.graduate_from_json_file(f_full, auto_commit=auto_commit, dry_run=dry_run)
                            results.append(r)
                    except Exception as e:
                        print(f"Error compiling {fname}: {e}", file=sys.stderr)
        return results


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Graduation Compiler ('The Hands')")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compile-lesson
    p_comp = subparsers.add_parser("compile-lesson", help="Compile a lesson or anti-pattern JSON file into SKILL.md/AGENTS.md")
    p_comp.add_argument("file", help="Path to lesson or anti-pattern JSON file")
    p_comp.add_argument("--no-git", action="store_true", help="Do not commit or push to Git")
    p_comp.add_argument("--dry-run", action="store_true", help="Simulate compilation without writing files")

    # compile-all-pending
    p_all = subparsers.add_parser("compile-all-pending", help="Scan and compile all pending lessons in .agents/learning/knowledge/")
    p_all.add_argument("--no-git", action="store_true", help="Do not commit or push to Git")
    p_all.add_argument("--dry-run", action="store_true", help="Simulate compilation without writing files")

    # compile-item
    p_item = subparsers.add_parser("compile-item", help="Compile an ad-hoc invariant directly")
    p_item.add_argument("--id", required=True, help="Item ID (e.g. LSN-2026-001)")
    p_item.add_argument("--statement", required=True, help="Invariant statement")
    p_item.add_argument("--category", default="Principle", choices=["Principle", "Pattern", "Anti-Pattern", "Lesson"])
    p_item.add_argument("--capability", default=None, help="Target capability (e.g. chapter5, sem, regression)")
    p_item.add_argument("--skills", nargs="*", default=None, help="Explicit target skill names")
    p_item.add_argument("--global", dest="is_global", action="store_true", help="Target global rules/AGENTS.md")
    p_item.add_argument("--no-git", action="store_true", help="Do not commit or push to Git")
    p_item.add_argument("--dry-run", action="store_true", help="Simulate compilation without writing files")

    args = parser.parse_args()
    compiler = AcademicGraduationCompiler()

    if args.command == "compile-lesson":
        res = compiler.graduate_from_json_file(args.file, auto_commit=not args.no_git, dry_run=args.dry_run)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if not res.get("all_passed"):
            sys.exit(1)

    elif args.command == "compile-all-pending":
        res_list = compiler.compile_all_pending(auto_commit=not args.no_git, dry_run=args.dry_run)
        print(f"Graduated {len(res_list)} pending knowledge items.")
        print(json.dumps(res_list, indent=2, ensure_ascii=False))

    elif args.command == "compile-item":
        res = compiler.graduate_item(
            item_id=args.id,
            statement=args.statement,
            category=args.category,
            capability=args.capability,
            skills=args.skills,
            is_global=args.is_global,
            auto_commit=not args.no_git,
            dry_run=args.dry_run
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if not res.get("all_passed"):
            sys.exit(1)


if __name__ == "__main__":
    main()
