#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_mechanical_contradictions_regression.py

Automated Architectural Regression Suite verifying that all 7 identified
mechanical rule contradictions and registry defects remain resolved.
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "hooks"), os.path.join(AGENTS_DIR, "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from dynamic_invariant_guard import DynamicInvariantGuard


def test_01_zero_stale_validation_contradictions():
    """Assert no active invariant directs creating .stale copies while CAND-2026-DIAGRAM-CEX-AND-UNLINK-001 bans them."""
    invariants = DynamicInvariantGuard.load_invariants()

    # Rule banning .stale must remain active
    unlink_rule = invariants.get("CAND-2026-DIAGRAM-CEX-AND-UNLINK-001")
    assert unlink_rule is not None, "CAND-2026-DIAGRAM-CEX-AND-UNLINK-001 must exist"
    assert unlink_rule.get("enabled") is True, "CAND-2026-DIAGRAM-CEX-AND-UNLINK-001 must be enabled"

    # Rule directing .stale must be updated to mandate physical unlinking
    legacy_deact = invariants.get("LSN-2026-LEGACY-VALIDATION-REPORT-DEACTIVATION")
    assert legacy_deact is not None, "LSN-2026-LEGACY-VALIDATION-REPORT-DEACTIVATION must exist"
    assert legacy_deact.get("enabled") is True, "LSN-2026-LEGACY-VALIDATION-REPORT-DEACTIVATION must be enabled"
    assert "os.remove" in legacy_deact.get("remedy") or "physically delete" in legacy_deact.get("remedy").lower()
    assert "validation_report.stale" not in legacy_deact.get("remedy")

    # All active remedies must mandate physical deletion, never creating .stale copies
    checked_rules = [
        "CAND-2026-LEGACY-VAL-ISOLATION-001",
        "CAND-2026-LEGACY-VAL-PHYSICAL-CLEAN-001",
        "CAND-2026-PHYSICAL-DECONTAMINATION-001",
        "AP-2026-COPY-WITHOUT-UNLINK-CONTAMINATION",
        "AP-2026-SUBDIRECTORY-VALIDATION-QUARANTINE-FAILURE"
    ]
    for r_id in checked_rules:
        rule = invariants.get(r_id)
        if rule and rule.get("enabled"):
            remedy = rule.get("remedy", "")
            statement = rule.get("statement", "")
            assert "rename the file to validation_report.stale" not in remedy.lower(), (
                f"Rule {r_id} still prescribes renaming to .stale in remedy: {remedy}"
            )
            assert "os.remove" in remedy or "rm" in remedy or "physically delete" in remedy.lower() or "physically remove" in remedy.lower(), (
                f"Rule {r_id} remedy does not mandate physical deletion: {remedy}"
            )


def test_02_sem_single_indicator_and_no_parcel_ban_in_r():
    """Assert statistics-agent is not blocked by corrupted parcel bans in R and SEM adheres to single-indicator modeling."""
    invariants = DynamicInvariantGuard.load_invariants()

    # Corrupted parcel ban on R files must not exist and mandate must be on markdown/narrative
    writer_mandate = invariants.get("LSN-2026-WRITER-READ-ONLY-JSON-MANDATE")
    assert writer_mandate is not None
    assert writer_mandate.get("enabled") is True
    assert writer_mandate.get("file_pattern") != ".*\\.R", (
        "LSN-2026-WRITER-READ-ONLY-JSON-MANDATE must not ban parcels in .R files"
    )

    # AP-2026-MANIFEST-PATH-LABELED-AS-SEM must reflect genuine subscales vs single-indicator latent modeling
    sem_rule = invariants.get("AP-2026-MANIFEST-PATH-LABELED-AS-SEM")
    assert sem_rule is not None
    sem_stmt = sem_rule.get("statement", "")
    assert "single observed indicator" in sem_stmt.lower() or "single-indicator" in sem_stmt.lower() or "subscales" in sem_stmt.lower(), (
        f"SEM invariant statement must reflect single observed indicator / subscale rules: {sem_stmt}"
    )

    # Test that statistics-agent writing an R model with single indicator or subscales is allowed
    payload = {
        "agentName": "statistics-agent",
        "caller": "statistics-agent",
        "tool_name": "write_to_file",
        "toolCall": {
            "name": "write_to_file",
            "args": {
                "TargetFile": "/path/to/02_analysis_code/sem_model.R",
                "CodeContent": "model <- 'Depression =~ 1*dep_total\ndep_total ~~ 0.2*dep_total'"
            }
        },
        "track": 2
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use("statistics-agent", payload)
    assert decision.get("decision") == "allow", f"Expected allow, got {decision}"


def test_03_regression_3_table_spec_synchronization():
    """Assert 06_chapter4_and_statistical_modeling.md matches AGENTS.md and mechanical validator."""
    spec_path = os.path.join(AGENTS_DIR, "rules", "06_chapter4_and_statistical_modeling.md")
    assert os.path.isfile(spec_path)
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Table 1 must be Correlation Matrix
    assert "Table 1: Correlation Matrix" in content or "Table 1 (Correlations)" in content
    # Table 2 must be Model Summary & Combined ANOVA with 11 columns
    assert "Table 2: Model Summary & Combined ANOVA" in content
    assert "11 columns" in content
    # Table 3 must be Coefficients & Collinearity Diagnostics with 8 columns
    assert "Table 3: Coefficients & Collinearity" in content
    assert "8 columns" in content


def test_04_data_audit_json_scoping():
    """Assert CAND-2026-DATA-AUDIT-SINGLE-SAMPLE-INVARIANT is scoped to findings deliverables and allows audit ledgers."""
    invariants = DynamicInvariantGuard.load_invariants()
    rule = invariants.get("CAND-2026-DATA-AUDIT-SINGLE-SAMPLE-INVARIANT")
    assert rule is not None
    fp = rule.get("file_pattern", "")
    assert fp != ".*\\.json", "CAND-2026-DATA-AUDIT-SINGLE-SAMPLE-INVARIANT must not use blanket .*\\.json pattern"

    # Verify that data-agent writing a data audit report with initial_sample is ALLOWED
    payload = {
        "agentName": "data-agent",
        "caller": "data-agent",
        "tool_name": "write_to_file",
        "toolCall": {
            "name": "write_to_file",
            "args": {
                "TargetFile": "/workspace/02_analysis_code/data_audit_report.json",
                "CodeContent": '{"initial_sample": 500, "final_sample": 483, "attrition": 17}'
            }
        },
        "track": 2
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use("data-agent", payload)
    assert decision.get("decision") == "allow", f"Data audit report should be allowed, got: {decision}"


def test_05_english_docx_western_decimal_exemption():
    """Assert English deliverables are exempt from CAND-2026-TABLE-BORDER-PERSIAN-ZERO."""
    invariants = DynamicInvariantGuard.load_invariants()
    rule = invariants.get("CAND-2026-TABLE-BORDER-PERSIAN-ZERO")
    assert rule is not None
    fp = rule.get("file_pattern", "")
    assert "_English" in fp or "(?!.*_English)" in fp, (
        f"CAND-2026-TABLE-BORDER-PERSIAN-ZERO file_pattern must exempt English tracks: {fp}"
    )

    # Test that writing an English document with 0.45 decimal is allowed
    payload = {
        "agentName": "academic-writer",
        "caller": "academic-writer",
        "tool_name": "write_to_file",
        "toolCall": {
            "name": "write_to_file",
            "args": {
                "TargetFile": "/workspace/03_deliverables/manuscript_English.docx",
                "CodeContent": "Results indicated a significant effect (M = 0.45, SD = 0.12)."
            }
        },
        "track": 2
    }
    decision = DynamicInvariantGuard.evaluate_pre_tool_use("academic-writer", payload)
    assert decision.get("decision") == "allow", f"English docx should be allowed, got: {decision}"


def test_06_openxml_alignment_advice_concordance():
    """Assert AGENTS.md AP-2026-OUT-OF-ORDER-OXML-JC does not advise setting p.alignment = RIGHT."""
    agents_file = os.path.join(AGENTS_DIR, "plugins", "academic-suite", "rules", "AGENTS.md")
    assert os.path.isfile(agents_file)
    with open(agents_file, "r", encoding="utf-8") as f:
        content = f.read()

    for line in content.splitlines():
        if "AP-2026-OUT-OF-ORDER-OXML-JC" in line:
            assert "WD_ALIGN_PARAGRAPH.RIGHT" not in line or "omit <w:jc>" in line, (
                f"AP-2026-OUT-OF-ORDER-OXML-JC must not prescribe WD_ALIGN_PARAGRAPH.RIGHT: {line}"
            )
            assert "omit <w:jc>" in line or "omit <w:jc" in line, (
                f"AP-2026-OUT-OF-ORDER-OXML-JC must advise omitting w:jc for RTL headings: {line}"
            )


def test_07_two_tier_dyad_remedy_alignment():
    """Assert CAND-2026-DISAGGREGATED-HYPOTHESIS-JSON-001 remedy adheres to Two-Tier Dyad."""
    invariants = DynamicInvariantGuard.load_invariants()
    rule = invariants.get("CAND-2026-DISAGGREGATED-HYPOTHESIS-JSON-001")
    assert rule is not None
    remedy = rule.get("remedy", "")
    assert "Two-Tier Dyad" in remedy or "optional until Tier 2" in remedy or ".json and .md" in remedy, (
        f"CAND-2026-DISAGGREGATED-HYPOTHESIS-JSON-001 remedy must reflect Two-Tier Dyad: {remedy}"
    )
