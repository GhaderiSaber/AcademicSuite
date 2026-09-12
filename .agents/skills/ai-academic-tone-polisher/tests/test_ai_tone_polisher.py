#!/usr/bin/env python3
"""
Unit Tests for Skill #22: AI Academic Tone Polisher
Verifies invariant masking fidelity, AI detection heuristics linter, and cadence metrics.
"""

import sys
import unittest
from pathlib import Path

# Add scripts directory to path
SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from mask_invariants import InvariantMasker
from lint_ai_risk import AIRiskLinter
from cadence_inverter import CadenceInverter


class TestInvariantMasker(unittest.TestCase):
    """Verifies that mathematical and bibliographic entities are masked and restored with 100% fidelity."""

    def setUp(self):
        self.masker = InvariantMasker()

    def test_apa_english_citations_preservation(self):
        text = (
            "According to Beck et al. (2020), cognitive appraisal shapes pain perception. "
            "Prior investigations (Costa & McCrae, 1992; Kline, 2015) confirm this model."
        )
        masked_text, state = self.masker.mask(text)
        self.assertIn("__CIT_", masked_text)
        self.assertNotIn("Beck et al. (2020)", masked_text)
        self.assertNotIn("(Costa & McCrae, 1992; Kline, 2015)", masked_text)

        unmasked_text = self.masker.unmask(masked_text, state)
        self.assertEqual(text, unmasked_text)

    def test_persian_citations_preservation(self):
        text = (
            "بر اساس یافته‌های پیشین (بک و همکاران، ۱۳۹۹)، شفقت خود نقش تعدیل‌کننده دارد. "
            "این الگو در پژوهش‌های دیگر (روشن و همکاران، ۱۳۸۵) نیز تایید شده است."
        )
        masked_text, state = self.masker.mask(text)
        self.assertIn("__CIT_", masked_text)
        
        unmasked_text = self.masker.unmask(masked_text, state)
        self.assertEqual(text, unmasked_text)

    def test_statistical_math_formulas_preservation(self):
        text = (
            "The ANCOVA revealed a significant group effect: F(1, 58) = 14.25, p < .001, η_p² = .197. "
            "Independent t-tests confirmed baseline equivalence: t(58) = 0.42, p = .676."
        )
        masked_text, state = self.masker.mask(text)
        self.assertIn("__STAT_", masked_text)
        self.assertNotIn("F(1, 58) = 14.25, p < .001", masked_text)

        unmasked_text = self.masker.unmask(masked_text, state)
        self.assertEqual(text, unmasked_text)

    def test_complex_sem_fit_indices_preservation(self):
        text = "Model fit was acceptable: χ²(52) = 57.762, p = .271; CFI = .995; RMSEA = .019."
        masked_text, state = self.masker.mask(text)
        unmasked_text = self.masker.unmask(masked_text, state)
        self.assertEqual(text, unmasked_text)


class TestAIRiskLinter(unittest.TestCase):
    """Verifies that the diagnostic linter catches synthetic footprints and approves human-cadence text."""

    def setUp(self):
        self.linter_en = AIRiskLinter(lang="en")
        self.linter_fa = AIRiskLinter(lang="fa")

    def test_flags_monotone_sentence_lengths(self):
        # 5 sentences with identical length (12 words each) -> CV should be 0.0
        monotone_text = (
            "The university campus provides various psychological services for enrolled undergraduate students every semester. "
            "Students experiencing persistent distress can contact counselors through the online administrative portal directly. "
            "Appointments are scheduled during standard business hours throughout the entire regular academic year. "
            "Confidentiality is strictly maintained according to ethical guidelines established by medical university boards. "
            "Follow-up evaluations are conducted periodically to evaluate the overall effectiveness of interventions provided."
        )
        result = self.linter_en.evaluate(monotone_text)
        cadence = result["cadence"]
        self.assertLess(cadence["cv"], 0.20)
        self.assertGreater(result["composite_risk_score"], 20.0)

    def test_detects_rhetorical_question_opener(self):
        text = (
            "Pain affects students profoundly. "
            "Why do two students with similar complaints experience different suffering? "
            "Biopsychosocial models explain that cognitive appraisals shape pain."
        )
        result = self.linter_en.evaluate(text)
        rq_triggers = [t for t in result["structural_triggers"] if t["type"] == "RHETORICAL_QUESTION"]
        self.assertTrue(len(rq_triggers) > 0)

    def test_detects_ordinal_enumeration(self):
        text = (
            "We formulated four hypotheses: First, neuroticism will predict pain. "
            "Second, extraversion will buffer stress. "
            "Third, self-compassion will reduce symptoms. "
            "Finally, mediation will occur."
        )
        result = self.linter_en.evaluate(text)
        ord_triggers = [t for t in result["structural_triggers"] if t["type"] == "ORDINAL_ENUMERATION"]
        self.assertTrue(len(ord_triggers) > 0)

    def test_detects_english_cliches(self):
        text = "Self-compassion plays a crucial role in emotion regulation and sheds light on pain mechanisms."
        cliches = self.linter_en.scan_cliches(text)
        matched = [c["matched_text"].lower() for c in cliches]
        self.assertTrue(any("crucial role" in m for m in matched))
        self.assertTrue(any("sheds light" in m for m in matched))

    def test_detects_persian_cliches(self):
        text = "شایان ذکر است که شفقت خود در این راستا نقش بسیار مهمی ایفا می‌کند و در جهان پرشتاب امروز حیاتی است."
        cliches = self.linter_fa.scan_cliches(text)
        self.assertGreaterEqual(len(cliches), 3)

    def test_approves_high_burstiness_human_text(self):
        text = (
            "Pain is rarely physical alone. "
            "For university students, persistent bodily discomfort represents a recurrent, disabling burden—disrupting sleep, forcing missed classes, and derailing concentration during exams (Treede et al., 2015). "
            "Campus surveys tell a stark story. "
            "Between 15% and 40% of college students live with recurrent musculoskeletal discomfort lingering well beyond the standard three-month mark (Gloria-Kang et al., 2020). "
            "This is not fleeting tension. "
            "Rather, it is enduring somatic distress that directly undermines developmental priorities during emerging adulthood, initiating a troubling trajectory toward academic attrition and depressive symptoms when left unaddressed."
        )
        result = self.linter_en.evaluate(text)
        cadence = result["cadence"]
        self.assertGreaterEqual(cadence["cv"], 0.60)
        self.assertEqual(len(result["structural_triggers"]), 0)
        self.assertEqual(len(result["cliches"]), 0)
        self.assertEqual(result["verdict"], "PASSED")


class TestCadenceInverter(unittest.TestCase):
    """Verifies the cadence inverter metrics and advice generator."""

    def setUp(self):
        self.inverter = CadenceInverter()

    def test_cadence_calculation(self):
        text = "Short sentence. Another short sentence here. Now a much longer sentence containing explanatory clauses and analytical details that expand the empirical context significantly."
        res = self.inverter.analyze_paragraph(text)
        self.assertEqual(res["sentence_count"], 3)
        self.assertGreater(res["cv"], 0.50)


if __name__ == "__main__":
    unittest.main()
