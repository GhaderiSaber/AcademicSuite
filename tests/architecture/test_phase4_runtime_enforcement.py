#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_phase4_runtime_enforcement.py — Phase 4 Architectural Verification

Validates:
1. Deliverable invariants are registered with event 'Both' or 'Stop' so CLI-generated outputs are inspected.
2. DynamicInvariantGuard.evaluate_stop intercepts prohibited markdown patterns (e.g. Chapter 5 tables).
3. DynamicInvariantGuard.evaluate_stop inspects .docx OpenXML markup (e.g. <w:insideV>, Word tables).
4. DynamicInvariantGuard.evaluate_stop allows clean, compliant deliverables.
5. LearningHooks.handle_pre_invocation prioritizes role-specific active invariants for subagents and orchestrator.
"""

import os
import sys
import json
import zipfile
import tempfile
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

from dynamic_invariant_guard import DynamicInvariantGuard
from learning_hooks import LearningHooks


def test_deliverable_invariants_are_both_or_stop():
    """Ensure key deliverable rules run on Stop as well as PreToolUse."""
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
    ]

    for rule_id in key_deliverable_rules:
        rule = invariants.get(rule_id)
        assert rule is not None, f"Rule {rule_id} is missing from enforced_invariants.json"
        assert rule.get("event") in ("Both", "Stop"), f"Rule {rule_id} must have event Both or Stop, got {rule.get('event')}"


def test_evaluate_stop_catches_markdown_violations(tmp_path):
    """Verify that evaluate_stop detects prohibited patterns in markdown deliverables."""
    d_dir = tmp_path / "03_deliverables"
    d_dir.mkdir(parents=True, exist_ok=True)

    # Violating Chapter 5 markdown file containing a table
    ch5_file = d_dir / "chapter_5_discussion.md"
    ch5_file.write_text(
        "# فصل ۵: بحث و نتیجه‌گیری\n\n| متغیر | مقدار |\n|---|---|\n| تاب‌آوری | ۴.۲ |",
        encoding="utf-8"
    )

    payload = {
        "deliverables_dir": str(d_dir),
        "agentName": "academic-writer",
        "track": 2
    }

    res = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res.get("decision") == "continue", f"Expected continue (rejection), got: {res}"
    assert "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001" in res.get("reason", "")


def test_evaluate_stop_catches_docx_openxml_violations(tmp_path):
    """Verify that evaluate_stop inspects .docx OpenXML markup and rejects prohibited XML tags."""
    d_dir = tmp_path / "03_deliverables"
    d_dir.mkdir(parents=True, exist_ok=True)

    # Create a mock .docx with prohibited <w:insideV> tag
    docx_file = d_dir / "stage4_analysis.docx"
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:tbl>'
        '<w:tblPr><w:tblBorders><w:insideV w:val="single"/></w:tblBorders></w:tblPr>'
        '<w:tr><w:tc><w:p><w:r><w:t>داده</w:t></w:r></w:p></w:tc></w:tr>'
        '</w:tbl>'
        '</w:body>'
        '</w:document>'
    )

    with zipfile.ZipFile(docx_file, "w") as zf:
        zf.writestr("word/document.xml", doc_xml)

    payload = {
        "deliverables_dir": str(d_dir),
        "agentName": "academic-writer",
        "track": 2
    }

    res = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res.get("decision") == "continue", f"Expected continue (rejection), got: {res}"
    assert "insideV" in res.get("reason", "") or "TABLE-BORDER" in res.get("reason", "") or "table" in res.get("reason", "").lower()


def test_evaluate_stop_allows_clean_deliverables(tmp_path):
    """Verify that compliant deliverables without violations pass cleanly."""
    d_dir = tmp_path / "03_deliverables"
    d_dir.mkdir(parents=True, exist_ok=True)

    # Clean Chapter 4 markdown deliverable adhering to all standards
    ch4_file = d_dir / "stage4_findings.md"
    ch4_file.write_text(
        "# فصل ۴: یافته‌های پژوهش\n\nدر ارزیابی فرضیه اول، یافته‌ها نشان داد که متغیر تاب‌آوری دارای میانگین ۱۲.۳۴ است.",
        encoding="utf-8"
    )

    # Clean DOCX without tables or prohibited tags
    clean_docx = d_dir / "stage4_findings.docx"
    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p><w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr><w:r><w:t>یافته‌های پژوهش به شرح زیر است.</w:t></w:r></w:p>'
        '</w:body>'
        '</w:document>'
    )
    with zipfile.ZipFile(clean_docx, "w") as zf:
        zf.writestr("word/document.xml", doc_xml)

    payload = {
        "deliverables_dir": str(d_dir),
        "agentName": "academic-writer",
        "track": 2
    }

    res = DynamicInvariantGuard.evaluate_stop("academic-writer", payload)
    assert res.get("decision") == "allow", f"Expected allow, got: {res}"


def test_pre_invocation_role_specific_context():
    """Verify that PreInvocation prioritizes role-specific invariants in ephemeral context."""
    # Test for academic-writer
    writer_payload = {
        "isSubagent": True,
        "agentName": "academic-writer",
        "track": 2
    }
    writer_res = LearningHooks.handle_pre_invocation(writer_payload)
    assert "injectSteps" in writer_res
    msg = writer_res["injectSteps"][0]["ephemeralMessage"]
    assert "ACADEMIC WRITER DIRECTIVES" in msg
    assert "ACTIVE ROLE INVARIANTS" in msg
    # Academic writer should see writer invariants (like Chapter 5 prose or OpenXML DOM)
    assert "LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001" in msg or "DOM-PARSING" in msg or "EXPLICIT-RIGHT-ALIGNMENT" in msg

    # Test for academic-orchestrator
    orch_payload = {
        "isSubagent": False,
        "agentName": "academic-orchestrator",
        "track": 2
    }
    orch_res = LearningHooks.handle_pre_invocation(orch_payload)
    assert "injectSteps" in orch_res
    orch_msg = orch_res["injectSteps"][0]["ephemeralMessage"]
    assert "CONSTITUTIONAL ENFORCEMENT ACTIVE" in orch_msg
    assert "ACTIVE ORCHESTRATOR INVARIANTS" in orch_msg
