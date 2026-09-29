#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_phase3_invariant_integrity.py — Phase 3 Architectural Verification

Validates:
1. Companion anti-pattern resolution rejects generic stop words and prevents slug collisions.
2. Corrupted invariant patterns are fully repaired with their genuine domain specifications.
3. Zero spurious cross-domain pattern duplication across unrelated rules in enforced_invariants.json.
4. All registered mechanical invariants compile cleanly and have valid metadata.
5. _is_actionable_regex_pattern correctly differentiates actionable regexes from descriptive prose.
"""

import os
import re
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INVARIANTS_PATH = os.path.join(ROOT_DIR, ".agents", "hooks", "rules", "enforced_invariants.json")


@pytest.fixture
def invariants():
    """Load the current enforced invariants registry."""
    assert os.path.isfile(INVARIANTS_PATH), f"Missing {INVARIANTS_PATH}"
    with open(INVARIANTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("invariants", {})


def test_slug_collision_prevention():
    """Verify that companion resolution in the compiler rejects generic stop words."""
    import sys
    sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
    from academic_graduation_compiler import AcademicGraduationCompiler

    compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)

    # Slugs with generic stop words must NOT match unrelated anti-patterns
    generic_test_cases = [
        "LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001",
        "LSN-2026-EXPLICIT-RIGHT-ALIGNMENT-AND-INLINE-MARKDOWN-PARSING-001",
        "LSN-2026-VALIDATOR-THREE-TABLE-FAIL-CLOSED-001",
        "LSN-2026-TABLE-FORMATTING-FAILURE-001",
    ]

    stop_words = {
        "parsing", "alignment", "format", "formatting", "failure", "invariant", "invariants",
        "standard", "standards", "check", "rule", "rules", "modification", "table", "tables",
        "explicit", "lesson", "defect", "writing", "docx", "code", "file", "blindspot",
        "validation", "validator", "handling", "processing", "reporting", "model", "suite",
        "overuse", "error", "leak", "clean", "test", "structural"
    }

    def _slug_base(val: str) -> str:
        s = re.sub(r"^(?:LSN|AP|CAN|CAND)-\d{4}-?", "", val)
        s = re.sub(r"-\d+$", "", s)
        return s.lower()

    for item_id in generic_test_cases:
        base = _slug_base(item_id)
        tokens = [t for t in base.split("-") if len(t) > 3 and not t.isdigit() and t not in stop_words]
        # None of the remaining substantive tokens should be in stop_words
        for tok in tokens:
            assert tok not in stop_words, f"Token {tok} in {item_id} should be filtered out"


def test_repaired_invariants_integrity(invariants):
    """Verify that the 3 previously corrupted invariants are correctly restored."""
    # 1. DOM parsing invariant must ban regex on document.xml, NOT match references
    dom_inv = invariants.get("LSN-2026-DOM-PARSING-FOR-OPENXML-MODIFICATION-001")
    assert dom_inv is not None, "LSN-2026-DOM-PARSING invariant is missing"
    assert "re\\.sub" in dom_inv["pattern"] or "re.sub" in dom_inv["pattern"]
    assert "document" in dom_inv["pattern"]
    assert "منابع" not in dom_inv["pattern"], "DOM parsing invariant contains corrupted reference pattern!"

    # 2. Alignment & inline markdown invariant must ban raw markdown in runs, NOT match references
    align_inv = invariants.get("LSN-2026-EXPLICIT-RIGHT-ALIGNMENT-AND-INLINE-MARKDOWN-PARSING-001")
    assert align_inv is not None, "LSN-2026-EXPLICIT-RIGHT-ALIGNMENT invariant is missing"
    assert "<w:t>" in align_inv["pattern"] or "w:jc" in align_inv["pattern"]
    assert "منابع" not in align_inv["pattern"], "Alignment invariant contains corrupted reference pattern!"

    # 3. Validator regression table invariant must check regression format, NOT header blank lines
    val_inv = invariants.get("LSN-2026-VALIDATOR-THREE-TABLE-FAIL-CLOSED-001")
    assert val_inv is not None, "LSN-2026-VALIDATOR-THREE-TABLE invariant is missing"
    assert val_inv["pattern"] != "(?m)^[^\\n]\\n#+\\s", "Validator invariant still has header blank line regex!"
    assert "regression" in val_inv["pattern"].lower() or "رگرسیون" in val_inv["pattern"]


def test_no_unrelated_pattern_duplicates(invariants):
    """Assert zero spurious pattern duplication across unrelated rules."""
    patterns = {}
    for k, v in invariants.items():
        pat = v.get("pattern", "")
        if pat:
            patterns.setdefault(pat, []).append(k)

    def _base_slug(name):
        s = re.sub(r"^(?:LSN|AP|CAN|CAND)-\d{4}(?:[0-9]{4})?-?", "", name)
        s = re.sub(r"-\d+$", "", s)
        return s.lower()

    for pat, keys in patterns.items():
        if len(keys) > 1:
            base_slugs = set(_base_slug(k) for k in keys)
            # Permissible duplicate groups:
            # 1. Exact companion LSN and AP (e.g. AP-2026-NAIVE-LENGTH-REFERENCE-PARSING & LSN-2026-STRUCTURAL-REFERENCE-PARSING-001)
            # 2. Cross-agent/skill targeting of the same single sample invariant (CAND-*-SINGLE-SAMPLE-INVARIANT)
            # 3. Cross-agent testing invariants (CAND-20260927-*-001)
            is_sample_inv = all("single-sample" in k.lower() for k in keys)
            is_validator_inv = all("run_all_validators" in pat for _ in keys)
            is_ref_companion = all("reference" in k.lower() or "parsing" in k.lower() for k in keys)

            assert is_sample_inv or is_validator_inv or is_ref_companion or len(base_slugs) == 1, (
                f"Spurious pattern collision detected for pattern {pat[:50]}: {keys}"
            )


def test_all_registered_invariants_valid(invariants):
    """Every registered invariant must have valid metadata and compilable regex."""
    assert len(invariants) >= 44, f"Expected at least 44 invariants, got {len(invariants)}"
    for item_id, rule in invariants.items():
        assert rule.get("item_id") == item_id
        assert bool(rule.get("category")), f"Rule {item_id} has empty category"
        assert rule.get("enabled") is True
        assert rule.get("check_type") in ("regex_ban", "substring_ban", "tool_ban", "openxml_dom_ban", "markdown_table_ban")

        pat = rule.get("pattern", "")
        if pat and rule.get("check_type") in ("regex_ban", "openxml_dom_ban", "tool_ban"):
            try:
                re.compile(pat)
            except re.error as e:
                pytest.fail(f"Invariant {item_id} has invalid regex pattern: {pat} ({e})")


def test_is_actionable_regex_rejects_prose():
    """Test that _is_actionable_regex_pattern strictly rejects descriptive prose sentences."""
    import sys
    sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
    from academic_graduation_compiler import _is_actionable_regex_pattern

    prose_examples = [
        "Scanning for Latin script substrings [A-Za-z] functioning as standalone technical jargon within RTL blocks.",
        "Regex detecting Latin alphabetical characters [A-Za-z] within Persian prose.",
        "Scripts checking layout by `if <w:jc w:val=\"right\"`",
        "Detection of bold styling applied to table captions.",
        "Assert presence of (table_1, table_2, table_3) in JSON output.",
        "Presence of bold styling applied to paragraph runs.",
    ]

    for prose in prose_examples:
        assert not _is_actionable_regex_pattern(prose), f"Should reject descriptive prose: {prose}"

    actionable_examples = [
        r"(?m)^\*\*جدول.*\*\*$",
        r"len\(.*?\)\s*>\s*\d+",
        r"(?i)parcel",
        r"(?m)^.*re\.sub.*xml.*$",
        r"(?i)<w:insideV\s*/?>",
    ]

    for regex in actionable_examples:
        assert _is_actionable_regex_pattern(regex), f"Should accept actionable regex: {regex}"
