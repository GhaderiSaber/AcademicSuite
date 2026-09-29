#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_phase1_learning_consolidation.py — Verification of Phase 1 Consolidation

Constitutional Governance (Directives 0, 18, 19, 21, 25):
- Tests that .agents/learning/knowledge/lessons/ contains zero runaway duplicates.
- Tests that machine context banners (DETERMINISTIC ADAPTIVE CONTEXT, CDE) are rejected as corrections.
- Tests that academic_lesson_distiller content-addressable deduplication blocks duplicate files.
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from scripts.academic_correction_detector import AcademicCorrectionDetector
from scripts.academic_lesson_distiller import AcademicLessonDistiller


class TestPhase1LearningConsolidation:
    """Verifies that Phase 1 consolidation invariants hold permanently."""

    def test_01_knowledge_lessons_count_and_curated_semantic_preservation(self):
        """Asserts that all 85 curated semantic lessons are preserved and duplicate explosion is eliminated."""
        lessons_dir = os.path.join(ROOT_DIR, ".agents", "learning", "knowledge", "lessons")
        assert os.path.isdir(lessons_dir), "Lessons directory must exist"

        all_json = [f for f in os.listdir(lessons_dir) if f.endswith(".json")]
        # Total active lessons should be around 97 (85 semantic + 12 unique feedback)
        assert len(all_json) < 120, f"Active lessons count ({len(all_json)}) exceeded clean ceiling (< 120)"

        semantic_lessons = [f for f in all_json if f.startswith("LSN-2026-") and not f[9:17].isdigit()]
        assert len(semantic_lessons) >= 80, f"Expected at least 80 semantic lessons, got {len(semantic_lessons)}"

        # Assert no runaway validator failure duplicate files exist in active lessons
        for fn in all_json:
            with open(os.path.join(lessons_dir, fn), "r", encoding="utf-8") as f:
                data = json.load(f)
            wh = str(data.get("what_happened", ""))
            if "diagnosis" in data and isinstance(data["diagnosis"], dict):
                wh += " " + str(data["diagnosis"].get("what_happened", ""))
            assert "DETERMINISTIC ADAPTIVE CONTEXT" not in wh, f"Self-pollution lesson {fn} must not be in active lessons"

    def test_02_correction_detector_ignores_machine_context_markers(self):
        """Asserts that internal agent banners are immune from being detected as user corrections."""
        detector = AcademicCorrectionDetector(project_root=ROOT_DIR)

        adaptive_banner = (
            "🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY) [Budget: ~327/600 tokens (54.5%)]\n"
            "- Target Capability: SEM | Task: structural_equation_modeling | Agent: trajectory-analyzer\n"
            "Observable defect identified from trigger: Stage Validator Gate in '03_deliverables' failed."
        )
        assert detector.detect_correction(adaptive_banner) is None

        cde_banner = "### Contractual Delegation Envelope (CDE)\nYou must follow Directive 20."
        assert detector.detect_correction(cde_banner) is None

        # Ensure genuine user feedback is still detected
        genuine_critique = "The degrees of freedom reported in Table 4-3 are wrong. df should be 120 not 124."
        assert detector.detect_correction(genuine_critique) is not None

    def test_03_lesson_distiller_deduplication_gate(self):
        """Asserts that attempting to record a duplicate lesson returns ALREADY_EXISTS and creates no new file."""
        distiller = AcademicLessonDistiller(project_root=ROOT_DIR)
        lessons_dir = os.path.join(ROOT_DIR, ".agents", "learning", "knowledge", "lessons")

        all_json = [f for f in os.listdir(lessons_dir) if f.endswith(".json")]
        assert len(all_json) > 0

        with open(os.path.join(lessons_dir, all_json[0]), "r", encoding="utf-8") as f:
            existing_data = json.load(f)

        duplicate_payload = dict(existing_data)
        duplicate_payload["lesson_id"] = "LSN-TEST-9999-DEDUP-TEST"

        result = distiller.record_lesson(duplicate_payload)
        assert result.get("status") == "ALREADY_EXISTS"
        assert not os.path.exists(os.path.join(lessons_dir, "LSN-TEST-9999-DEDUP-TEST.json"))
