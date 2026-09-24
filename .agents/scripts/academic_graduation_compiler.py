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
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts"), os.path.join(AGENTS_DIR, "hooks")]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from dynamic_invariant_guard import DynamicInvariantGuard
except ImportError:
    try:
        from hooks.dynamic_invariant_guard import DynamicInvariantGuard
    except ImportError:
        DynamicInvariantGuard = None

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
        self.invariants_file = os.path.join(self.agents_dir, "hooks", "rules", "enforced_invariants.json")
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.invariants_file), exist_ok=True)

    def _prune_snapshots(self, base_name: str, max_keep: int = 3) -> None:
        """Prunes historical snapshots in self.snapshots_dir to prevent disk clutter."""
        try:
            prefix = f"pre_grad_{base_name}_"
            snaps = []
            for fname in os.listdir(self.snapshots_dir):
                if fname.startswith(prefix) and fname.endswith(".md"):
                    full_p = os.path.join(self.snapshots_dir, fname)
                    snaps.append((os.path.getmtime(full_p), full_p))
            snaps.sort(key=lambda x: x[0], reverse=True)
            for _, old_snap in snaps[max_keep:]:
                try:
                    os.remove(old_snap)
                except OSError:
                    pass
        except Exception:
            pass

    def _deduce_enforcement(self, file_path: str, item_id: str, category: str = "Principle") -> str:
        """Deduces appropriate mechanical enforcement anchor for Option A formatting."""
        fname = os.path.basename(os.path.dirname(file_path)) or os.path.basename(file_path)
        if "chapter-5" in fname or "discussion" in fname:
            return "academic_writer_guard.py"
        elif "chapter-4" in fname or "apa" in fname:
            return "results_auditor_guard.py"
        elif "statistics" in fname or "assumption" in fname or "regression" in fname:
            return "statistics_agent_guard.py"
        elif "data" in fname or "cleaning" in fname or "audit" in fname:
            return "data_agent_guard.py"
        return f"dynamic_invariant_guard.py ({item_id})"

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
        enforcement: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Safely synthesize an Option A invariant into target markdown with snapshot, budget, and deduplication checks."""
        if not os.path.isfile(file_path):
            return {"file": file_path, "status": "SKIPPED_NOT_FOUND", "success": False}

        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        orig_lines = original_content.splitlines()
        orig_line_count = len(orig_lines)
        orig_byte_count = len(original_content.encode("utf-8"))

        # 1. Create Pre-Mutation Snapshot & Prune Older
        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(os.path.dirname(file_path)) or os.path.basename(file_path)
        snap_file = f"pre_grad_{base_name}_{now_str}.md"
        snap_path = os.path.join(self.snapshots_dir, snap_file)
        if not dry_run:
            with open(snap_path, "w", encoding="utf-8") as sf:
                sf.write(original_content)
            self._prune_snapshots(base_name, max_keep=3)

        # 2. Safety Rule 1: Synthesis, Not Stacking (Option A: - **<Category> (<ID>)**: <Statement>. [Enforcement: <Mechanism>])
        clean_statement = statement.strip().rstrip(".")
        clean_cat = category.strip().capitalize()
        eff_enforcement = enforcement or self._deduce_enforcement(file_path, item_id, clean_cat)
        new_bullet = f"- **{clean_cat} ({item_id})**: {clean_statement}. [Enforcement: {eff_enforcement}]"

        is_skill = file_path.endswith("SKILL.md")
        target_section_header = "## 🧠 Active Learned Behavioral Invariants" if is_skill else "## 1. Radical Honesty & Pipeline Enforcement"

        updated_content = original_content
        kw_new = set(self._extract_keywords(clean_statement))

        if target_section_header in updated_content:
            sec_pattern = rf"({re.escape(target_section_header)}[\s\S]*?)(?=\n## |\Z)"
            sec_match = re.search(sec_pattern, updated_content)
            if sec_match:
                full_section = sec_match.group(1)
                sec_lines = full_section.splitlines()
                merged = False

                # Step 2a: Deduplicate by exact Item ID
                id_pat = rf"- \*\*[^(]+\({re.escape(item_id)}\)\*\*:"
                for idx, line in enumerate(sec_lines):
                    if re.search(id_pat, line):
                        sec_lines[idx] = new_bullet
                        merged = True
                        break

                # Step 2b: Deduplicate / merge by keyword overlap (Safety Rule 1)
                if not merged:
                    for idx, line in enumerate(sec_lines):
                        if line.strip().startswith("- "):
                            kw_existing = set(self._extract_keywords(line))
                            overlap = kw_new.intersection(kw_existing)
                            if len(overlap) >= 2:
                                sec_lines[idx] = new_bullet
                                merged = True
                                break

                # Step 2c: Append if new
                if not merged:
                    sec_lines.append(new_bullet)

                new_section_str = "\n".join(sec_lines)
                updated_content = updated_content[:sec_match.start(1)] + new_section_str + updated_content[sec_match.end(1):]
        else:
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

            ref_entry = f"\n### Invariant {item_id} ({now_str})\n- **Category**: {clean_cat}\n- **Rule**: {clean_statement}.\n- **Enforcement**: {eff_enforcement}\n"
            if not dry_run:
                with open(refs_file, "a", encoding="utf-8") as rf:
                    rf.write(ref_entry)

            compact_bullet = f"- **{clean_cat} ({item_id})**: {clean_statement[:70]}... See [learned_invariants.md](references/learned_invariants.md). [Enforcement: {eff_enforcement}]"
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
            # 1. Stage files (only paths within base_dir)
            rel_files = [
                os.path.relpath(p, self.base_dir) for p in target_files
                if os.path.exists(p) and not os.path.relpath(p, self.base_dir).startswith("..")
            ]
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
        enforcement: Optional[str] = None,
        target_agents: Optional[List[str]] = None,
        check_type: Optional[str] = None,
        pattern: Optional[str] = None,
        file_pattern: Optional[str] = None,
        remedy: Optional[str] = None,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Dual-Channel Track 1 execution: Channel 1 (SKILL.md) + Channel 2 (Mechanical Hook)."""
        targets = self.resolve_targets(capability=capability, skills=skills, is_global=is_global)
        grad_results = []
        all_passed = True

        for target in targets:
            res = self.synthesize_markdown_rule(
                file_path=target,
                item_id=item_id,
                statement=statement,
                category=category,
                enforcement=enforcement,
                dry_run=dry_run
            )
            grad_results.append(res)
            if not res.get("success"):
                all_passed = False

        # Channel 2: Register Mechanical Hook Rule in enforced_invariants.json
        hook_registered = False
        if all_passed and not dry_run:
            try:
                if DynamicInvariantGuard is not None:
                    eff_pattern = pattern or ""
                    eff_check = check_type or ("regex_ban" if eff_pattern else "")
                    if eff_pattern or eff_check:
                        hook_registered = DynamicInvariantGuard.register_invariant(
                            item_id=item_id,
                            category=category,
                            statement=statement,
                            target_agents=target_agents or ["*"],
                            target_skills=skills or [],
                            event="PreToolUse",
                            file_pattern=file_pattern or ".*\\.(?:md|docx|txt)",
                            check_type=eff_check or "regex_ban",
                            pattern=eff_pattern,
                            violation_message=statement,
                            remedy=remedy or "",
                            base_dir=self.base_dir
                        )
            except Exception as e_hook:
                sys.stderr.write(f"[academic_graduation_compiler] Hook registration note: {e_hook}\n")

        git_res = {}
        if all_passed and auto_commit and not dry_run:
            files_to_commit = list(targets)
            if json_artifact_path and os.path.isfile(json_artifact_path):
                files_to_commit.append(json_artifact_path)
            if hook_registered and os.path.isfile(self.invariants_file):
                files_to_commit.append(self.invariants_file)
            git_res = self.git_sync(files_to_commit, item_id, statement)

        return {
            "item_id": item_id,
            "statement": statement,
            "category": category,
            "capability": capability,
            "targets": targets,
            "grad_results": grad_results,
            "all_passed": all_passed,
            "hook_registered": hook_registered,
            "git": git_res
        }

    def graduate_from_json_file(
        self,
        json_path: str,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Graduates a lesson or anti-pattern JSON file into matching SKILL.md and mechanical hooks."""
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

        # Extract mechanical heuristic parameters for Channel 2 hook registration
        dh = data.get("detection_heuristic", {})
        pattern = dh.get("regex") or dh.get("pattern") or ""
        check_type = dh.get("check_type")
        if not pattern and category == "Anti-Pattern":
            trig = dh.get("trigger_rule", "")
            if re.search(r"[\^\\\[\].*+?|]", trig):
                pattern = trig

        target_agents = data.get("target_agents") or ([data.get("target_agent")] if data.get("target_agent") else None)
        remedy = data.get("corrective_remedy") or statement
        enforcement = data.get("enforcement")

        # Cross-workspace synchronization: sync to central AcademicSuite store if json_path is external
        subdir_name = "lessons" if category == "Lesson" else ("anti-patterns" if category == "Anti-Pattern" else "principles")
        fname = os.path.basename(json_path)
        central_json = os.path.join(self.agents_dir, "learning", "knowledge", subdir_name, fname)
        is_external = not os.path.abspath(json_path).startswith(self.base_dir)
        effective_json = central_json if is_external else json_path

        res = self.graduate_item(
            item_id=item_id,
            statement=statement,
            category=category,
            capability=capability,
            skills=skills,
            json_artifact_path=effective_json if not is_external else None,
            is_global=is_global,
            enforcement=enforcement,
            target_agents=target_agents,
            check_type=check_type,
            pattern=pattern,
            remedy=remedy,
            auto_commit=auto_commit,
            dry_run=dry_run
        )

        if res.get("all_passed") and not dry_run:
            data["graduation_status"] = "GRADUATED"
            data["graduated_at"] = datetime.now(timezone.utc).isoformat()
            data["graduated_targets"] = res.get("targets", [])
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            if is_external:
                os.makedirs(os.path.dirname(central_json), exist_ok=True)
                with open(central_json, "w", encoding="utf-8") as cf:
                    json.dump(data, cf, indent=2, ensure_ascii=False)
                if auto_commit:
                    self.git_sync([central_json], item_id, f"sync knowledge {fname}")

        return res

    def graduate_candidate_from_json_file(
        self,
        candidate_json_path: str,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Compiles/promotes an improvement candidate JSON into its target component."""
        if not os.path.isfile(candidate_json_path):
            return {"candidate_id": "", "status": "FILE_NOT_FOUND", "success": False, "all_passed": False}

        with open(candidate_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        candidate_id = data.get("candidate_id") or os.path.basename(candidate_json_path).replace(".json", "")
        target_component = data.get("target_component", "")
        mutation = data.get("mutation", {})
        rationale = data.get("rationale", "")

        norm_target = target_component.replace("\\", "/").lstrip("/")
        target_path = os.path.join(self.base_dir, norm_target)
        if not os.path.isfile(target_path):
            cand_alt = os.path.join(ROOT_DIR, norm_target)
            if os.path.isfile(cand_alt):
                target_path = cand_alt

        if not os.path.isfile(target_path):
            return {
                "candidate_id": candidate_id,
                "status": "TARGET_NOT_FOUND",
                "target": target_component,
                "success": False,
                "all_passed": False
            }

        diff_content = mutation.get("content", "")
        applied = False
        if mutation.get("diff_type") == "UNIFIED_DIFF" and diff_content:
            try:
                added_lines = []
                for d_line in diff_content.splitlines():
                    if d_line.startswith("+") and not d_line.startswith("+++"):
                        clean_added = d_line[1:].strip()
                        if clean_added:
                            added_lines.append(clean_added)
                if added_lines:
                    statement = " ".join(added_lines)
                    res_synth = self.synthesize_markdown_rule(
                        file_path=target_path,
                        item_id=candidate_id,
                        statement=statement,
                        category="Learned Candidate",
                        dry_run=dry_run
                    )
                    applied = res_synth.get("success", False)
            except Exception:
                applied = False

        if not applied and rationale:
            res_synth = self.synthesize_markdown_rule(
                file_path=target_path,
                item_id=candidate_id,
                statement=rationale,
                category="Learned Candidate",
                dry_run=dry_run
            )
            applied = res_synth.get("success", False)

        if applied and not dry_run:
            data["status"] = "PROMOTED"
            data["promoted_at"] = datetime.now(timezone.utc).isoformat()
            data["promoted_targets"] = [target_path]
            with open(candidate_json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            if auto_commit:
                self.git_sync([target_path, candidate_json_path], candidate_id, f"promote candidate {candidate_id}")

        return {
            "candidate_id": candidate_id,
            "status": "PROMOTED" if applied else "FAILED",
            "target": target_path,
            "targets": [target_path],
            "all_passed": applied,
            "success": applied
        }

    def compile_all_pending(
        self,
        workspaces: Optional[List[str]] = None,
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Scans all lessons and anti-patterns in central and workspace knowledge directories and graduates pending items."""
        search_dirs = [os.path.join(self.agents_dir, "learning", "knowledge")]
        if workspaces:
            for ws in workspaces:
                if not ws or not os.path.isdir(ws):
                    continue
                ws_abs = os.path.abspath(ws)
                for cand in [os.path.join(ws_abs, ".agents", "learning", "knowledge"), os.path.join(ws_abs, "learning", "knowledge")]:
                    if os.path.isdir(cand) and cand not in search_dirs:
                        search_dirs.append(cand)

        results = []
        for k_dir in search_dirs:
            for subdir in ["lessons", "anti-patterns", "principles"]:
                s_path = os.path.join(k_dir, subdir)
                if not os.path.isdir(s_path):
                    continue
                for fname in sorted(os.listdir(s_path)):
                    if not fname.endswith(".json") or fname.startswith("."):
                        continue
                    f_full = os.path.join(s_path, fname)
                    try:
                        with open(f_full, "r", encoding="utf-8") as f:
                            d = json.load(f)
                        is_pending = (
                            d.get("graduation_status") != "GRADUATED" and (
                                d.get("graduation_status") == "PENDING_GRADUATION" or
                                d.get("graduation_track") == "TRACK_1_IMMEDIATE_GRADUATION"
                            )
                        )
                        if is_pending:
                            results.append(self.graduate_from_json_file(f_full, auto_commit=auto_commit, dry_run=dry_run))
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

    # compile-candidate
    p_cand = subparsers.add_parser("compile-candidate", help="Compile and promote an improvement candidate JSON into target component")
    p_cand.add_argument("file", help="Path to improvement candidate JSON file")
    p_cand.add_argument("--no-git", action="store_true", help="Do not commit or push to Git")
    p_cand.add_argument("--dry-run", action="store_true", help="Simulate compilation without writing files")

    # compile-all-pending
    p_all = subparsers.add_parser("compile-all-pending", help="Scan and compile all pending lessons in .agents/learning/knowledge/")
    p_all.add_argument("--workspaces", nargs="*", default=None, help="Additional workspace roots to scan for lessons")
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

    elif args.command == "compile-candidate":
        res = compiler.graduate_candidate_from_json_file(args.file, auto_commit=not args.no_git, dry_run=args.dry_run)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        if not res.get("all_passed"):
            sys.exit(1)

    elif args.command == "compile-all-pending":
        res_list = compiler.compile_all_pending(workspaces=args.workspaces, auto_commit=not args.no_git, dry_run=args.dry_run)
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
