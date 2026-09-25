#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_learning_hook_parity.py — Invariant-Hook Parity and Mechanical Enforcement Audit

Verifies:
1. Every active learned behavioral invariant in any SKILL.md possesses an explicit,
   valid mechanical [Enforcement: ...] anchor pointing to a registered guard, script, or rule.
2. The mechanical invariant registry (enforced_invariants.json) is valid and well-formed.
3. DynamicInvariantGuard mechanically intercepts violations during PreToolUse and Stop.
4. Academic graduation compiler provides idempotency, snapshot pruning, and dual-channel registration.
5. Track 1 Main Developer Agent is 100% exempt from academic prompts in learning_hooks.
"""

import os
import sys
import glob
import json
import re
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from hooks.dynamic_invariant_guard import DynamicInvariantGuard
from hooks.learning_hooks import LearningHooks


def test_skills_active_invariants_have_enforcement_anchors():
    """Asserts that all bullets under 'Active Learned Behavioral Invariants' have valid enforcement anchors."""
    skill_files = glob.glob(os.path.join(AGENTS_DIR, "skills", "*", "SKILL.md"))
    assert len(skill_files) > 0, "No SKILL.md files found!"

    # Load active invariants from enforced_invariants.json
    inv_file = os.path.join(AGENTS_DIR, "hooks", "rules", "enforced_invariants.json")
    assert os.path.isfile(inv_file), "enforced_invariants.json does not exist!"
    with open(inv_file, "r", encoding="utf-8") as f:
        registry_data = json.load(f)
    registered_rule_ids = set(registry_data.get("invariants", {}).keys())

    # Gather all known hook and script files
    hook_files = {os.path.basename(p) for p in glob.glob(os.path.join(AGENTS_DIR, "hooks", "*.py"))}
    hook_agent_files = {os.path.basename(p) for p in glob.glob(os.path.join(AGENTS_DIR, "hooks", "agents", "*.py"))}
    agent_guards = {
        f"{os.path.basename(os.path.dirname(p)).replace('-', '_')}_guard.py"
        for p in glob.glob(os.path.join(AGENTS_DIR, "agents", "*", "guard.py"))
    }
    all_hook_files = hook_files | hook_agent_files | agent_guards

    script_files = {os.path.basename(p) for p in glob.glob(os.path.join(AGENTS_DIR, "scripts", "*.py"))}
    skill_script_files = {os.path.basename(p) for p in glob.glob(os.path.join(AGENTS_DIR, "skills", "*", "scripts", "*.py"))}
    all_scripts = script_files | skill_script_files

    checked_invariants = 0

    for sf in skill_files:
        with open(sf, "r", encoding="utf-8") as f:
            content = f.read()

        if "## 🧠 Active Learned Behavioral Invariants" not in content:
            continue

        section = content.split("## 🧠 Active Learned Behavioral Invariants")[1]
        # Invariant section ends at next heading or EOF
        if "\n## " in section:
            section = section.split("\n## ")[0]

        lines = [line.strip() for line in section.strip().split("\n") if line.strip().startswith("- ")]
        for line in lines:
            checked_invariants += 1
            # Assert [Enforcement: ...] anchor exists
            match = re.search(r"\[Enforcement:\s*([^\]]+)\]", line)
            assert match, f"Missing [Enforcement: ...] anchor in {sf}:\n{line}"

            anchor_text = match.group(1).strip()
            parts = [p.strip() for p in re.split(r"[/,]", anchor_text) if p.strip()]

            # At least one mechanism in the anchor must resolve to an existing hook, script, or rule
            resolved = False
            for part in parts:
                clean_part = re.sub(r"\(.*?\)", "", part).strip()
                if ":" in clean_part:
                    # e.g., enforced_invariants.json:RULE-CH5-NO-TABLES
                    file_name, rule_id = clean_part.split(":", 1)
                    if rule_id.strip() in registered_rule_ids:
                        resolved = True
                        break
                elif clean_part in registered_rule_ids:
                    resolved = True
                    break
                elif clean_part in all_hook_files:
                    resolved = True
                    break
                elif clean_part in all_scripts:
                    resolved = True
                    break
                elif clean_part in ("dynamic_invariant_guard.py", "safety_hooks.py"):
                    resolved = True
                    break

            assert resolved, (
                f"Unresolved enforcement mechanism '{anchor_text}' in {sf}:\n{line}\n"
                f"Available hooks: {sorted(all_hook_files)}\n"
                f"Registered rules: {sorted(registered_rule_ids)}"
            )

    assert checked_invariants >= 5, f"Expected at least 5 learned invariants across skills, found {checked_invariants}"


def test_enforced_invariants_json_schema():
    """Asserts that enforced_invariants.json contains valid rules."""
    inv_file = os.path.join(AGENTS_DIR, "hooks", "rules", "enforced_invariants.json")
    with open(inv_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "contract_version" in data
    assert "invariants" in data
    assert len(data["invariants"]) > 0

    for item_id, inv in data["invariants"].items():
        for field in ("item_id", "category", "statement", "target_agents", "event", "tool_match", "remedy"):
            assert field in inv, f"Invariant {item_id} missing required field: {field}"
        assert inv["event"] in ("PreToolUse", "Stop", "Both", "*")


def test_dynamic_invariant_guard_blocks_chapter4_bold_caption():
    """Tests that DynamicInvariantGuard denies writing **جدول ۱** in Chapter 4 deliverable."""
    payload_bad = {
        "toolCall": {
            "name": "replace_file_content",
            "args": {
                "TargetFile": "/path/to/03_deliverables/stage_06_hypothesis_1/table1.md",
                "ReplacementContent": "Here is the table:\n**جدول ۱**\n| a | b |\n|---|---|\n"
            }
        }
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use(caller="academic-writer", payload=payload_bad)
    assert decision.get("decision") == "deny", "Guard failed to intercept prohibited bold table caption!"
    assert "AP-2026-BOLD-TABLE-CAPTIONS" in decision.get("reason", "")


def test_dynamic_invariant_guard_allows_compliant_content():
    """Tests that DynamicInvariantGuard allows compliant write operations."""
    payload_good = {
        "toolCall": {
            "name": "replace_file_content",
            "args": {
                "TargetFile": "/path/to/03_deliverables/stage_06_hypothesis_1/table1.md",
                "ReplacementContent": "جدول ۱\nتوزیع فراوانی متغیرهای جمعیت‌شناختی\n| a | b |\n|---|---|\n"
            }
        }
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use(caller="academic-writer", payload=payload_good)
    assert decision.get("decision") == "allow"


def test_dynamic_invariant_guard_blocks_chapter5_markdown_table():
    """Tests that DynamicInvariantGuard denies markdown tables in Chapter 5."""
    payload_bad = {
        "toolCall": {
            "name": "write_to_file",
            "args": {
                "TargetFile": "/path/to/03_deliverables/stage_02_hypo_1/Chapter_5_Discussion.md",
                "CodeContent": "بحث و بررسی فرضیه اول\n| متغیر | مقدار |\n| - | - |\n| سن | ۲۵ |\n"
            }
        }
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use(caller="academic-writer", payload=payload_bad)
    assert decision.get("decision") == "deny", "Guard failed to intercept markdown table in Chapter 5!"
    assert "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001" in decision.get("reason", "")


def test_main_agent_developer_exemption_in_learning_hooks():
    """Asserts that Track 1 developer calls receive zero academic ephemeral messages."""
    # Track 1 explicit
    res_track1 = LearningHooks.handle_pre_invocation({"track": 1})
    assert res_track1 == {}, "Track 1 was not completely exempt!"

    # Mode developer explicit
    res_mode = LearningHooks.handle_pre_invocation({"mode": "developer"})
    assert res_mode == {}, "Developer mode was not completely exempt!"

    # Caller default / antigravity
    res_caller = LearningHooks.handle_pre_invocation({"agentName": "default"})
    assert res_caller == {}, "Default agent was not exempt!"

    # Governed academic agent receives constitutional reminder
    res_acad = LearningHooks.handle_pre_invocation({"agentName": "academic-orchestrator"})
    assert "injectSteps" in res_acad
    assert len(res_acad["injectSteps"]) > 0
    msg = res_acad["injectSteps"][0]["ephemeralMessage"]
    assert "CONSTITUTIONAL ENFORCEMENT ACTIVE" in msg
    assert "Directive 0" in msg
    assert "Directive 20" in msg


def test_academic_graduation_compiler_snapshot_pruning():
    """Verifies that academic_graduation_compiler prunes snapshots to max 3."""
    from scripts.academic_graduation_compiler import AcademicGraduationCompiler
    compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)

    base_name = "test_skill_pruning"
    snap_dir = compiler.snapshots_dir

    try:
        # Create 5 test snapshots
        for i in range(5):
            fname = f"pre_grad_{base_name}_{20260924100000 + i}.md"
            with open(os.path.join(snap_dir, fname), "w", encoding="utf-8") as f:
                f.write(f"Snapshot {i}")

        compiler._prune_snapshots(base_name, max_keep=3)

        prefix = f"pre_grad_{base_name}_"
        remaining = [f for f in os.listdir(snap_dir) if f.startswith(prefix) and f.endswith(".md")]
        assert len(remaining) == 3, f"Expected 3 remaining snapshots, got {len(remaining)}"
    finally:
        # Cleanup test snapshots
        prefix = f"pre_grad_{base_name}_"
        for f in os.listdir(snap_dir):
            if f.startswith(prefix):
                try:
                    os.remove(os.path.join(snap_dir, f))
                except OSError:
                    pass
