#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_critique_detection_precision.py — High-Precision Critique Detection & False-Positive Immunity Test Suite

Verifies:
1. Immunity for IDE metadata changes (<USER_SETTINGS_CHANGE>, <ADDITIONAL_METADATA>).
2. Immunity for machine/subagent context markers (DETERMINISTIC ADAPTIVE CONTEXT, CDE envelopes).
3. Immunity for academic/statistical domain queries containing keywords like 'error', 'missing', 'reject', 'problem'.
4. Immunity for Persian statistical queries ('خطای استاندارد', 'داده‌های گمشده', 'رد فرض صفر', 'بیان مسئله').
5. Immunity for conversational questions and progress inquiries ('What have we done?', 'What should we do?').
6. High precision for genuine human critiques and defect reports (must still trigger).
7. End-to-end integration with LearningHooks, IntegrityHooks, and academic-orchestrator guard.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "contracts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from contracts.critique_detection_contract import (
    is_meaningful_user_critique,
    extract_clean_user_message
)
from learning_hooks import LearningHooks
from integrity_hooks import IntegrityHooks
import importlib.util
_guard_spec = importlib.util.spec_from_file_location(
    "orch_guard",
    os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "guard.py")
)
orch_guard = importlib.util.module_from_spec(_guard_spec)
_guard_spec.loader.exec_module(orch_guard)


class TestCritiqueDetectionPrecision(unittest.TestCase):

    def test_01_ide_settings_change_metadata_immunity(self):
        """Settings changes containing words like 'changed' or 'setting' must not be classified as critiques."""
        ide_payload = (
            "<USER_SETTINGS_CHANGE>The user changed setting 'Model Selection' "
            "to 'Gemini 2.5 Pro'.</USER_SETTINGS_CHANGE>"
        )
        clean = extract_clean_user_message(ide_payload)
        self.assertEqual(clean, "", "IDE settings change must be stripped completely")
        is_crit, term = is_meaningful_user_critique(ide_payload)
        self.assertFalse(is_crit, f"Settings change falsely classified as critique on term: {term}")

    def test_02_additional_metadata_block_immunity(self):
        """<ADDITIONAL_METADATA> blocks with workspace details must not trigger critique detection."""
        meta_payload = (
            "<ADDITIONAL_METADATA>\n"
            "Active file: error_log.txt\n"
            "Problem detected in previous session.\n"
            "</ADDITIONAL_METADATA>\n"
            "<USER_REQUEST>Please summarize the literature review.</USER_REQUEST>"
        )
        clean = extract_clean_user_message(meta_payload)
        self.assertEqual(clean, "Please summarize the literature review.")
        is_crit, term = is_meaningful_user_critique(clean)
        self.assertFalse(is_crit, f"Metadata leaked into critique: {term}")

    def test_03_machine_adaptive_context_envelope_immunity(self):
        """Internal subagent prompts beginning with machine context markers must be immune."""
        machine_prompt = (
            "🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY):\n"
            "- Defect avoidance: Do not report standard error without calculation.\n"
            "- Avoid flawed formatting."
        )
        is_crit, term = is_meaningful_user_critique(machine_prompt, is_subagent=True)
        self.assertFalse(is_crit, "Subagent machine envelope must never trigger critique")

        is_crit_caller, _ = is_meaningful_user_critique(machine_prompt, caller="academic-writer")
        self.assertFalse(is_crit_caller, "Worker subagent caller must never trigger critique")

    def test_04_statistical_and_methodology_domain_queries_immunity(self):
        """Domain queries with legitimate statistical words must NOT trigger critique detection."""
        domain_queries = [
            "Can you compute the standard error of measurement for the scales?",
            "What should we do about the missing data in Table 1?",
            "Was the null hypothesis rejected for Hypothesis 2?",
            "Please check the R-squared change in the hierarchical regression model.",
            "Can you write the problem statement for Chapter 1?",
            "Does the CFA model have any modification indices above 10?",
            "Should we use repeated measures ANOVA or mixed ANCOVA here?",
            "What have we done so far? What should we do next?",
            "Can you explain how Little's MCAR test evaluates missing values?"
        ]
        for query in domain_queries:
            is_crit, term = is_meaningful_user_critique(query, caller="academic-orchestrator")
            self.assertFalse(
                is_crit,
                f"Statistical query '{query}' was falsely classified as critique on term '{term}'"
            )

    def test_05_persian_domain_queries_immunity(self):
        """Persian academic queries with statistical collocations must NOT trigger critique detection."""
        persian_queries = [
            "خطای استاندارد متغیرها چقدر است؟",
            "داده‌های گمشده را با آزمون ام‌کار چگونه بررسی کردی؟",
            "آیا فرض صفر در فرضیه اول رد شد؟",
            "بیان مسئله پژوهش را برای من خلاصه کن.",
            "آیا تفاوت معناداری وجود ندارد؟",
            "تغییر ضریب تعیین در گام دوم چقدر بود؟"
        ]
        for query in persian_queries:
            is_crit, term = is_meaningful_user_critique(query, caller="academic-orchestrator")
            self.assertFalse(
                is_crit,
                f"Persian domain query '{query}' was falsely classified as critique on term '{term}'"
            )

    def test_06_genuine_critiques_accurately_detected(self):
        """Genuine critiques and defect assertions MUST reliably trigger critique detection."""
        genuine_critiques = [
            "So we have a problem. The table formatting is wrong.",
            "There is a defect in the references list.",
            "You forgot to include the regression ANOVA table.",
            "The calculation in Table 2 is incorrect.",
            "The numbers in Table 3 don't match the output.",
            "You made an error in the degrees of freedom.",
            "این جدول اشتباه است و ارقام با خروجی همخوانی ندارند.",
            "بخش محدودیت‌ها ناقص است و جا انداختی."
        ]
        for crit in genuine_critiques:
            is_crit, term = is_meaningful_user_critique(crit, caller="academic-orchestrator")
            self.assertTrue(
                is_crit,
                f"Genuine critique '{crit}' was NOT detected!"
            )
            self.assertIsNotNone(term)

    def test_07_learning_hooks_pre_invocation_no_spurious_cascade(self):
        """PreInvocation must not inject learning cascade prompts on routine queries."""
        normal_payload = {
            "userMessage": "What are the standard errors and R-squared change in Table 2?",
            "caller": "academic-orchestrator",
            "conversationId": "test-clean-turn"
        }
        res = LearningHooks.handle_pre_invocation(normal_payload)
        inject_steps = res.get("injectSteps", [])
        if inject_steps:
            msg = inject_steps[0].get("ephemeralMessage", "")
            self.assertNotIn(
                "CONTINUOUS LEARNING TRIGGER ACTIVE",
                msg,
                "PreInvocation falsely injected learning trigger on standard error query"
            )

    def test_08_integrity_hooks_stop_gate_allows_clean_turn(self):
        """IntegrityHooks.verify_learning_pipeline_completion must allow Stop on non-critique queries."""
        records = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "What is the problem statement and missing data status?"},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Here is the summary of the problem statement and missing data analysis."}
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records)
        self.assertTrue(
            ok,
            f"IntegrityHooks falsely blocked stop on non-critique query: {reason}"
        )

    def test_09_orchestrator_guard_is_user_critique_active_clean(self):
        """academic-orchestrator/guard.py is_user_critique_active must return False on non-critiques."""
        records = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "Can you check the standard error of measurement?"},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Checking standard error..."}
        ]
        is_crit, clean_txt, _ = orch_guard.is_user_critique_active(records)
        self.assertFalse(
            is_crit,
            f"orch_guard falsely detected critique on '{clean_txt}'"
        )


if __name__ == "__main__":
    unittest.main()
