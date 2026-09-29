#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_and_rule_integrity.py — Master Architecture Verification Suite

Phase 5 Comprehensive Verification Gate:
- Mechanically proves that all 5 phases of the Mechanical Rules and Learning Consolidation
  are fully satisfied and guarded by permanent regression assertions.
- Covers:
  1. Zero hardcoded machine paths in active learning, hooks, and contracts.
  2. Zero duplicate or runaway learning lessons in knowledge/lessons/.
  3. Strict invariant pattern validity and zero slug collision corruption.
  4. Dual lifecycle coverage ('Both' / 'Stop') for all deliverable invariants.
  5. Multi-format Stop-hook enforcement (rejects defective .md and .docx, allows clean files).
  6. Prioritized role-specific context rehydration for worker subagents and orchestrator.
"""

import os
import sys
import json
import zipfile
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "hooks"), os.path.join(AGENTS_DIR, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from dynamic_invariant_guard import DynamicInvariantGuard
from learning_hooks import LearningHooks


def test_zero_machine_paths_in_core_assets():
    """Test 1: Zero hardcoded developer machine paths in active learning, hooks, and contracts."""
    banned_prefixes = ["/home/saber-ghaderi", "/home/ghaderi-saber"]
    target_dirs = [
        os.path.join(AGENTS_DIR, "learning", "knowledge"),
        os.path.join(AGENTS_DIR, "hooks"),
        os.path.join(AGENTS_DIR, "contracts"),
    ]

    violations = []
    for t_dir in target_dirs:
        if not os.path.isdir(t_dir):
            continue
        for root_p, _, files in os.walk(t_dir):
            for fname in files:
                if fname.endswith((".json", ".py", ".md", ".sh")):
                    full_p = os.path.join(root_p, fname)
                    with open(full_p, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for bp in banned_prefixes:
                        if bp in content:
                            violations.append(f"{os.path.relpath(full_p, ROOT_DIR)} contains '{bp}'")

    assert not violations, f"Found machine paths in core assets:\n" + "\n".join(violations[:10])


def test_zero_duplicate_lessons_in_knowledge_store():
    """Test 2: Zero duplicate or runaway lessons in knowledge/lessons/."""
    lessons_dir = os.path.join(AGENTS_DIR, "learning", "knowledge", "lessons")
    assert os.path.isdir(lessons_dir)

    lesson_files = [f for f in os.listdir(lessons_dir) if f.endswith(".json")]
    # Active lessons must be pruned and deduplicated (under 120 total, down from 490)
    assert len(lesson_files) < 120, f"Expected < 120 active lessons after consolidation, found {len(lesson_files)}"

    signatures = set()
    for lf in lesson_files:
        p = os.path.join(lessons_dir, lf)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        diag = data.get("diagnosis", {})
        sig = (
            data.get("target_agent", ""),
            diag.get("behavior_caused_outcome", "").strip()[:100],
            diag.get("what_happened", "").strip()[:100],
        )
        assert sig not in signatures or not any(sig), f"Duplicate lesson detected: {lf} (signature={sig})"
        if any(sig):
            signatures.add(sig)


def test_invariant_pattern_validity_and_slug_collisions():
    """Test 3: Every invariant compiles cleanly, with zero cross-domain slug collision corruption."""
    invariants = DynamicInvariantGuard.load_invariants()
    assert len(invariants) >= 50, f"Expected at least 50 invariants, got {len(invariants)}"

    for rule_id, rule in invariants.items():
        assert rule.get("item_id") == rule_id
        assert rule.get("enabled") is True
        pat = rule.get("pattern", "")
        if pat and rule.get("check_type") in ("regex_ban", "openxml_dom_ban", "tool_ban"):
            try:
                import re
                re.compile(pat)
            except re.error as e:
                pytest.fail(f"Invariant {rule_id} has invalid regex: {pat} ({e})")

    # Specifically assert the 3 previously corrupted rules
    dom_rule = invariants.get("LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001")
    assert dom_rule and "re.sub" in dom_rule["pattern"].replace("\\.", ".")
    assert "منابع" not in dom_rule["pattern"]

    align_rule = invariants.get("LSN-2026-EXPLICIT-RIGHT-ALIGNMENT-AND-INLINE-MARKDOWN-PARSING-001")
    assert align_rule and "<w:t>" in align_rule["pattern"]
    assert "منابع" not in align_rule["pattern"]

    val_rule = invariants.get("LSN-2026-VALIDATOR-THREE-TABLE-FAIL-CLOSED-001")
    assert val_rule and val_rule["pattern"] != "(?m)^[^\\n]\\n#+\\s"


def test_deliverable_rules_dual_lifecycle():
    """Test 4: Deliverable formatting, table, and typography rules have event 'Both' or 'Stop'."""
    invariants = DynamicInvariantGuard.load_invariants()
    key_deliverable_rules = [
        "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001",
        "CAND-2026-APA-SINGLE-SAMPLE-INVARIANT",
        "CAND-2026-CH4-SINGLE-SAMPLE-INVARIANT",
        "CAND-2026-DATA-AUDIT-SINGLE-SAMPLE-INVARIANT",
        "CAND-2026-LANGUAGE-TRACK-AWARE-TYPOGRAPHY",
        "CAND-2026-EXHAUSTIVE-SUPERVISOR-REVISION-AUDIT",
        "CAND-2026-EXHAUSTIVE-DEMOGRAPHICS-001",
        "AP-2026-WRITER-JSON-MUTATION",
        "CAND-2026-ATOMIC-TRIAD-CH4-001",
        "CAND-2026-DOCUMENT-CONSERVATION-IN-PLACE-REVISION",
    ]

    for r_id in key_deliverable_rules:
        r = invariants.get(r_id)
        assert r is not None, f"Rule {r_id} missing"
        assert r.get("event") in ("Both", "Stop"), f"Rule {r_id} has event '{r.get('event')}', expected Both or Stop"


def test_stop_guard_end_to_end_interception(tmp_path):
    """Test 5: DynamicInvariantGuard.evaluate_stop intercepts prohibited deliverables and allows clean ones."""
    d_dir = tmp_path / "03_deliverables"
    d_dir.mkdir(parents=True, exist_ok=True)

    # 1. Reject Chapter 5 with Markdown Table
    ch5_bad = d_dir / "chapter_5_discussion.md"
    ch5_bad.write_text("# فصل ۵: بحث\n\n| ستون ۱ | ستون ۲ |\n|---|---|\n| مقدار | داده |", encoding="utf-8")
    payload = {"deliverables_dir": str(d_dir), "agentName": "academic-writer", "track": 2}
    res1 = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res1.get("decision") == "continue"
    ch5_bad.unlink()

    # 2. Reject DOCX with Prohibited XML Vertical Borders
    docx_bad = d_dir / "test_findings.docx"
    doc_xml_bad = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:tbl><w:tblPr><w:tblBorders><w:insideV w:val="single"/></w:tblBorders></w:tblPr></w:tbl></w:body>'
        '</w:document>'
    )
    with zipfile.ZipFile(docx_bad, "w") as zf:
        zf.writestr("word/document.xml", doc_xml_bad)
    res2 = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res2.get("decision") == "continue"
    docx_bad.unlink()

    # 3. Allow Compliant Deliverable
    clean_md = d_dir / "stage4_findings.md"
    clean_md.write_text("# فصل ۴: یافته‌های پژوهش\n\nدر آزمون فرضیه اول، نتایج تایید شد.", encoding="utf-8")
    clean_docx = d_dir / "stage4_findings.docx"
    doc_xml_clean = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:pPr><w:jc w:val="both"/></w:pPr><w:r><w:t>یافته‌ها</w:t></w:r></w:p></w:body>'
        '</w:document>'
    )
    with zipfile.ZipFile(clean_docx, "w") as zf:
        zf.writestr("word/document.xml", doc_xml_clean)
    res3 = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res3.get("decision") == "allow"


def test_subagent_role_specific_steering():
    """Test 6: PreInvocation steering prioritizes role-specific active invariants."""
    # academic-writer payload
    writer_res = LearningHooks.handle_pre_invocation({
        "isSubagent": True,
        "agentName": "academic-writer",
        "track": 2
    })
    writer_msg = writer_res["injectSteps"][0]["ephemeralMessage"]
    assert "ACADEMIC WRITER DIRECTIVES" in writer_msg
    assert "ACTIVE ROLE INVARIANTS" in writer_msg
    # Specific writer rules must be included
    assert "CHAPTER-5-PROSE" in writer_msg or "DOM-PARSING" in writer_msg or "RIGHT-ALIGNMENT" in writer_msg

    # statistics-agent payload
    stat_res = LearningHooks.handle_pre_invocation({
        "isSubagent": True,
        "agentName": "statistics-agent",
        "track": 2
    })
    stat_msg = stat_res["injectSteps"][0]["ephemeralMessage"]
    assert "STATISTICAL & DATA INTEGRITY DIRECTIVES" in stat_msg

    # academic-orchestrator payload
    orch_res = LearningHooks.handle_pre_invocation({
        "isSubagent": False,
        "agentName": "academic-orchestrator",
        "track": 2
    })
    orch_msg = orch_res["injectSteps"][0]["ephemeralMessage"]
    assert "CONSTITUTIONAL ENFORCEMENT ACTIVE" in orch_msg
    assert "ACTIVE ORCHESTRATOR INVARIANTS" in orch_msg
