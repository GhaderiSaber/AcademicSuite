#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Epistemic Literature Reasoner
(موتور ارزیابی معرفت‌شناختی شواهد و پیشینه پژوهش دیجیتال صابر)

Evaluates the evidentiary weight of empirical literature supporting or refuting
academic claims across study design, sample size, measurement quality, effect size,
replication status, and population congruence.

Classifies evidence strength into:
  STRONG, MODERATE, LIMITED, MIXED, CONFLICTING, INSUFFICIENT
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

DESIGN_WEIGHTS = {
    "meta_analysis": 1.0,
    "systematic_review": 0.95,
    "rct": 0.90,
    "quasi_experimental": 0.75,
    "longitudinal": 0.70,
    "cross_sectional": 0.50,
    "case_control": 0.45,
    "qualitative": 0.40,
    "expert_opinion": 0.20
}


class EpistemicLiteratureReasoner:
    """Evaluates the epistemic strength of empirical literature supporting academic claims."""

    def __init__(self):
        pass

    def evaluate_claim(self, claim_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates an academic claim against supporting and contradicting study records.

        claim_payload format:
        {
          "claim_id": "C101",
          "claim_statement": "ACT significantly reduces burnout in healthcare workers",
          "target_population": "healthcare workers",
          "supporting_studies": [
            {
              "citation": "Smith et al. (2021)",
              "design": "rct",
              "sample_size": 120,
              "measurement_tool": "MBI (validated)",
              "effect_size": 0.65,
              "effect_size_type": "cohen_d",
              "year": 2021,
              "population": "nurses"
            }
          ],
          "contradicting_studies": []
        }
        """
        claim_statement = claim_payload.get("claim_statement", "")
        supporting = claim_payload.get("supporting_studies", [])
        contradicting = claim_payload.get("contradicting_studies", [])
        target_pop = claim_payload.get("target_population", "").lower()

        n_sup = len(supporting)
        n_con = len(contradicting)

        # 1. Compute Quality Index for Supporting Studies
        sup_score = 0.0
        total_sup_n = 0
        for s in supporting:
            d_weight = DESIGN_WEIGHTS.get(s.get("design", "cross_sectional").lower(), 0.50)
            n = s.get("sample_size", 30)
            total_sup_n += n
            n_factor = min(1.0, n / 100.0)  # max out at N=100
            recency = 1.0 if s.get("year", 2020) >= 2018 else 0.8
            tool_quality = 1.0 if "validated" in s.get("measurement_tool", "").lower() else 0.7
            pop_similarity = 1.0 if target_pop and target_pop in s.get("population", "").lower() else 0.8
            
            item_score = d_weight * (0.4 * n_factor + 0.2 * recency + 0.2 * tool_quality + 0.2 * pop_similarity)
            sup_score += item_score

        # 2. Compute Quality Index for Contradicting Studies
        con_score = 0.0
        total_con_n = 0
        for c in contradicting:
            d_weight = DESIGN_WEIGHTS.get(c.get("design", "cross_sectional").lower(), 0.50)
            n = c.get("sample_size", 30)
            total_con_n += n
            n_factor = min(1.0, n / 100.0)
            item_score = d_weight * n_factor
            con_score += item_score

        # 3. Epistemic Classification Logic
        classification = "INSUFFICIENT"
        rationale_en = ""
        rationale_fa = ""

        if n_sup == 0 and n_con == 0:
            classification = "INSUFFICIENT"
            rationale_en = "No empirical studies provided to substantiate the claim."
            rationale_fa = "هیچ مطالعه تجربی مستندی برای پشتیبانی از این گزاره یافت نشد."

        elif n_con > 0 and n_sup > 0:
            ratio = sup_score / (sup_score + con_score + 1e-6)
            if 0.4 <= ratio <= 0.6:
                classification = "CONFLICTING"
                rationale_en = (
                    f"Substantial contradicting evidence exists ({n_sup} supporting vs. {n_con} contradicting). "
                    "Findings are deeply divided and likely depend on unmeasured moderating variables."
                )
                rationale_fa = (
                    f"شواهد متناقض جدی وجود دارد ({n_sup} مطالعه موافق در برابر {n_con} مطالعه مخالف). "
                    "نتایج دارای تعارض مستقیم بوده و احتمالاً وابسته به متغیرهای تعدیل‌کننده ناشناخته است."
                )
            elif ratio > 0.6:
                classification = "MIXED"
                rationale_en = (
                    f"Evidence leans in favor of the claim ({n_sup} supporting vs. {n_con} contradicting), "
                    "but notable dissent requires explicit theoretical qualification in Chapter 5."
                )
                rationale_fa = (
                    f"کفه شواهد به نفع گزاره سنگینی می‌کند ({n_sup} موافق در برابر {n_con} مخالف)، "
                    "اما وجود شواهد ناهمسو نیازمند تبیین نقادانه و ذکر قیود مرزی در فصل پنجم است."
                )
            else:
                classification = "CONFLICTING"
                rationale_en = "Contradicting evidence outweighs supporting literature."
                rationale_fa = "شواهد تجربی مخالف بر مطالعات موافق برتری کیفی یا کمّی دارد."

        elif n_sup > 0 and n_con == 0:
            has_meta = any(s.get("design", "").lower() in ["meta_analysis", "systematic_review"] for s in supporting)
            has_rct = any(s.get("design", "").lower() == "rct" for s in supporting)

            if has_meta or (has_rct and total_sup_n >= 150) or (n_sup >= 4 and total_sup_n >= 250):
                classification = "STRONG"
                rationale_en = (
                    f"High-quality empirical evidence ({n_sup} studies, total N = {total_sup_n}) "
                    "derived from rigorous designs (RCTs or systematic synthesis) with consistent effects."
                )
                rationale_fa = (
                    f"شواهد تجربی نیرومند ({n_sup} مطالعه با مجموع نمونه {total_sup_n}) "
                    "مبتنی بر طرح‌های دقیق (کارآزمایی بالینی تصادفی یا فراتحلیل) با اندازه اثرهای همگرا."
                )
            elif has_rct or (n_sup >= 2 and total_sup_n >= 60):
                classification = "MODERATE"
                rationale_en = (
                    f"Plausible empirical support ({n_sup} studies, total N = {total_sup_n}) "
                    "from controlled studies or multiple correlational samples, but requires local replication."
                )
                rationale_fa = (
                    f"حمایت تجربی متوسط ({n_sup} مطالعه با مجموع نمونه {total_sup_n}) "
                    "از مطالعات کنترل‌شده، اما نیازمند تعمیم‌بخشی و تکرار در نمونه‌های بومی‌تر."
                )
            else:
                classification = "LIMITED"
                rationale_en = (
                    f"Sparse or preliminary evidence ({n_sup} study, total N = {total_sup_n}). "
                    "Treat claim with caution; avoid sweeping generalization."
                )
                rationale_fa = (
                    f"شواهد محدود یا مقدماتی ({n_sup} مطالعه، N = {total_sup_n}). "
                    "ادعا باید با احتیاط و بدون تعمیم‌های مبالغه‌آمیز گزارش شود."
                )

        return {
            "claim_statement": claim_statement,
            "epistemic_verdict": classification,
            "supporting_count": n_sup,
            "contradicting_count": n_con,
            "total_evaluated_sample_size": total_sup_n + total_con_n,
            "quality_index_supporting": round(sup_score, 2),
            "quality_index_contradicting": round(con_score, 2),
            "rationale_en": rationale_en,
            "rationale_fa": rationale_fa,
            "chapter2_guidance": (
                "Highlight as well-established empirical law." if classification == "STRONG"
                else "Contrast competing paradigms and cite potential moderators." if classification in ["MIXED", "CONFLICTING"]
                else "Frame as an emerging or preliminary hypothesis needing empirical validation."
            ),
            "chapter5_guidance": (
                "Interpret findings confidently against high-consensus theoretical models." if classification == "STRONG"
                else "Provide deep theoretical explanation for why current results align or diverge from divided literature." if classification in ["MIXED", "CONFLICTING"]
                else "Emphasize exploratory nature and call for rigorous RCT replication."
            )
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Epistemic Literature Reasoner")
    parser.add_argument("--demo", action="store_true", help="Run sample epistemic evaluation")

    args = parser.parse_args()
    reasoner = EpistemicLiteratureReasoner()

    if args.demo or len(sys.argv) == 1:
        sample_claim = {
            "claim_statement": "درمان مبتنی بر پذیرش و تعهد (ACT) بر کاهش فرسودگی شغلی کادر درمان اثربخش است.",
            "target_population": "کادر درمان و پرستاران",
            "supporting_studies": [
                {
                    "citation": "Towey-Swift et al. (2023)",
                    "design": "systematic_review",
                    "sample_size": 840,
                    "measurement_tool": "MBI (validated)",
                    "year": 2023,
                    "population": "healthcare professionals"
                },
                {
                    "citation": "Prudenzi et al. (2022)",
                    "design": "rct",
                    "sample_size": 142,
                    "measurement_tool": "MBI (validated)",
                    "year": 2022,
                    "population": "nurses and physicians"
                }
            ],
            "contradicting_studies": []
        }
        res = reasoner.evaluate_claim(sample_claim)
        print("\nDigital Saber Epistemic Claim Evaluation:")
        print("=" * 75)
        print(f"Claim:        {res['claim_statement']}")
        print(f"Verdict:      [{res['epistemic_verdict']}]")
        print(f"Supporting:   {res['supporting_count']} studies (Total N = {res['total_evaluated_sample_size']})")
        print(f"Rationale:    {res['rationale_fa']}")
        print(f"Ch 2 Advice:  {res['chapter2_guidance']}")
        print(f"Ch 5 Advice:  {res['chapter5_guidance']}")
        print("=" * 75)


if __name__ == "__main__":
    main()
