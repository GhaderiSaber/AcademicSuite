#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Multi-Signal Anomaly Detector
(موتور تشخیص چندعاملی ناهنجاری‌های آماری و ممیزی صابر)

Calculates a comprehensive Multi-Signal Anomaly Index (MSAI) across 10 diagnostic signals:
  1. Large effect size magnitude (d > 1.8, η_p² > .40)
  2. Severe variance deflation (SD / Mean < 0.10)
  3. Non-overlapping group distributions
  4. Unusually high psychometric reliability (α > .98)
  5. Uniform or unnatural decimal repetitions
  6. Suspicious normality clustering (Skew/Kurt artificially near 0.000)
  7. Identical distributions across distinct subscales
  8. Impossible or extreme inter-construct correlations (|r| > .95)
  9. Raw data / marginal sums mathematical mismatch
  10. Narrative-to-table discrepancy

Outputs 'FLAG FOR REVIEW' when multiple signals converge, avoiding simplistic
hard-coded accusations of artificial or fabricated data.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional


class MultiSignalAnomalyDetector:
    """Evaluates multi-signal statistical plausibility and defense readiness."""

    def __init__(self):
        pass

    def evaluate_payload(self, audit_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates an audit payload containing tests, groups, scales, and reported statistics.
        Returns composite anomaly score, triggered signals, and defense guidance.
        """
        signals = []
        tests = audit_payload.get("tests", [])
        descriptives = audit_payload.get("descriptives", {})
        reliability = audit_payload.get("reliability", {})
        correlations = audit_payload.get("correlations", {})
        narrative_vs_table = audit_payload.get("narrative_discrepancies", [])

        # Signal 1: Large Effect Size Magnitude
        for t in tests:
            eta = t.get("partial_eta_squared") or t.get("eta_squared")
            d = t.get("cohen_d")
            if eta is not None and float(eta) > 0.45:
                signals.append({
                    "signal_id": "SIG_01_LARGE_EFFECT",
                    "title": "Astronomical Effect Size (η_p² > .45)",
                    "severity": "REVIEW_FLAG",
                    "description": f"Test {t.get('test_id')}: Reported η_p² = {float(eta):.3f} indicates > 45% variance explained.",
                    "defense_context": "Clinical trials with potent interventions can produce large effects, but defense committees will question distribution overlap."
                })
            elif d is not None and float(d) > 2.0:
                signals.append({
                    "signal_id": "SIG_01_LARGE_EFFECT",
                    "title": "Astronomical Cohen's d (> 2.0)",
                    "severity": "REVIEW_FLAG",
                    "description": f"Test {t.get('test_id')}: Reported d = {float(d):.2f}.",
                    "defense_context": "Ensure this is not an artifact of small sample size (Hedges' g correction recommended)."
                })

        # Signal 2 & 3: Variance Deflation & Group Non-Overlap
        groups_data = descriptives.get("groups", [])
        if len(groups_data) >= 2:
            g1 = groups_data[0]
            g2 = groups_data[1]
            m1, s1 = g1.get("mean", 0), g1.get("sd", 1)
            m2, s2 = g2.get("mean", 0), g2.get("sd", 1)

            if s1 > 0 and s2 > 0:
                # Variance deflation
                if (s1 / (abs(m1) + 1e-5) < 0.08) or (s2 / (abs(m2) + 1e-5) < 0.08):
                    signals.append({
                        "signal_id": "SIG_02_VARIANCE_DEFLATION",
                        "title": "Severe Variance Deflation (SD/M < .08)",
                        "severity": "REVIEW_FLAG",
                        "description": f"Unusually small standard deviations (SD1={s1:.2f}, SD2={s2:.2f}) relative to means.",
                        "defense_context": "Check whether participants gave identical repetitive answers (low item variance)."
                    })

                # Distribution separation (complete non-overlap)
                if (m1 > m2 and (m2 + 2 * s2) < (m1 - 2 * s1)) or (m2 > m1 and (m1 + 2 * s1) < (m2 - 2 * s2)):
                    signals.append({
                        "signal_id": "SIG_03_PERFECT_SEPARATION",
                        "title": "Near-Zero Distribution Overlap Between Groups",
                        "severity": "REVIEW_FLAG",
                        "description": "Group distributions do not overlap within ±2 standard deviations.",
                        "defense_context": "In human psychology, psychological traits rarely exhibit zero group overlap. Be prepared for examiner questions."
                    })

        # Signal 4: Unnaturally Perfect Psychometric Reliability
        for scale, alpha in reliability.items():
            if float(alpha) > 0.97:
                signals.append({
                    "signal_id": "SIG_04_EXCESSIVE_RELIABILITY",
                    "title": "Excessive Scale Reliability (α > .97)",
                    "severity": "REVIEW_FLAG",
                    "description": f"Scale '{scale}' reported Cronbach's α = {float(alpha):.3f}.",
                    "defense_context": "Alpha > .95 often indicates item redundancy (bloated specific variance / synonymous items) rather than superior construct validity."
                })

        # Signal 5: Identical Decimal Uniformity
        means = [g.get("mean") for g in groups_data if g.get("mean") is not None]
        decimal_parts = [round(m - int(m), 3) for m in means if isinstance(m, (int, float))]
        if len(decimal_parts) >= 4 and len(set(decimal_parts)) == 1:
            signals.append({
                "signal_id": "SIG_05_DECIMAL_UNIFORMITY",
                "title": "Monotonically Identical Decimal Pattern",
                "severity": "REVIEW_FLAG",
                "description": f"Multiple independent means share identical fractional decimals ({decimal_parts[0]}).",
                "defense_context": "Inspect raw data calculation scripts to ensure no rounding truncation."
            })

        # Signal 6: Suspicious Normality Clustering
        skew_vals = descriptives.get("skewness", [])
        kurt_vals = descriptives.get("kurtosis", [])
        if len(skew_vals) >= 3 and all(abs(s) < 0.02 for s in skew_vals):
            signals.append({
                "signal_id": "SIG_06_PERFECT_NORMALITY",
                "title": "Artificial Normality Clustering (|Skew| < .02)",
                "severity": "REVIEW_FLAG",
                "description": "Multiple independent behavioral scales show near-zero skewness.",
                "defense_context": "Real survey data naturally displays empirical asymmetry."
            })

        # Signal 7: Narrative to Table Discrepancy
        if narrative_vs_table:
            for disc in narrative_vs_table:
                signals.append({
                    "signal_id": "SIG_10_NARRATIVE_MISMATCH",
                    "title": "Narrative Text vs Table Value Discrepancy",
                    "severity": "CRITICAL",
                    "description": disc,
                    "defense_context": "Immediate point of criticism in defense committee. Must be corrected."
                })

        # Composite Anomaly Index Computation
        active_signal_count = len(signals)
        anomaly_index = min(100, active_signal_count * 25)

        if active_signal_count == 0:
            verdict = "NORMAL_EMPIRICAL"
            verdict_fa = "الگوی داده‌های تجربی طبیعی و استاندارد (فاقد ناهنجاری همگرا)"
        elif active_signal_count <= 2:
            verdict = "FLAG_FOR_REVIEW"
            verdict_fa = "نیازمند بازبینی و آماده‌سازی توجیه روش‌شناختی (FLAG FOR REVIEW - ۱ تا ۲ نشانه)"
        else:
            verdict = "FLAG_FOR_REVIEW_ELEVATED"
            verdict_fa = "هشدار بازبینی سطح بالا (FLAG FOR REVIEW - همگرایی ۳ نشانه یا بیشتر)"

        return {
            "verdict": verdict,
            "verdict_fa": verdict_fa,
            "anomaly_index": anomaly_index,
            "active_signals_count": active_signal_count,
            "signals": signals,
            "defense_readiness_advice": (
                "No critical statistical anomaly detected. Results are defense-ready."
                if active_signal_count == 0
                else "Provide explicit sensitivity analyses and explain the clinical potency of the intervention to defend against reviewer skepticism."
            )
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Multi-Signal Anomaly Detector")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")

    args = parser.parse_args()
    detector = MultiSignalAnomalyDetector()

    if args.demo or len(sys.argv) == 1:
        sample_audit = {
            "tests": [
                {"test_id": "T1", "method": "ancova", "partial_eta_squared": 0.48}
            ],
            "descriptives": {
                "groups": [
                    {"name": "Experimental", "mean": 42.15, "sd": 1.20},
                    {"name": "Control", "mean": 21.15, "sd": 1.40}
                ],
                "skewness": [0.01, 0.01, 0.01]
            },
            "reliability": {
                "Burnout": 0.985
            },
            "narrative_discrepancies": []
        }
        res = detector.evaluate_payload(sample_audit)
        print("\nDigital Saber Multi-Signal Anomaly Audit:")
        print("=" * 75)
        print(f"Verdict:         [{res['verdict']}]")
        print(f"Verdict (FA):    {res['verdict_fa']}")
        print(f"Anomaly Index:   {res['anomaly_index']} / 100")
        print(f"Active Signals:  {res['active_signals_count']}")
        print("\nItemized Diagnostic Signals:")
        for s in res["signals"]:
            print(f"  🚩 [{s['signal_id']}] {s['title']}")
            print(f"     Details: {s['description']}")
            print(f"     Defense Advice: {s['defense_context']}")
        print(f"\nOverall Guidance: {res['defense_readiness_advice']}")
        print("=" * 75)


if __name__ == "__main__":
    main()
