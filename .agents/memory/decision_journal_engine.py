#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Decision Journal Engine
(موتور ثبت و تحلیل تصمیمات روش‌شناختی و آماری دیجیتال صابر)

Maintains an auditable, structured record of WHY Saber makes specific
methodological and statistical choices, which alternatives were rejected,
and human gate approvals.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime

MEMORY_DIR = os.path.dirname(os.path.abspath(__file__))
DECISIONS_DIR = os.path.join(MEMORY_DIR, "decisions")


class DecisionJournalEngine:
    """Records, inspects, and audits critical academic decisions made by Digital Saber."""

    def __init__(self, decisions_dir: Optional[str] = None):
        self.decisions_dir = decisions_dir or DECISIONS_DIR
        os.makedirs(self.decisions_dir, exist_ok=True)
        self.decisions: List[Dict[str, Any]] = []
        self._load_decisions()

    def _load_decisions(self):
        self.decisions = []
        if not os.path.exists(self.decisions_dir):
            return

        for fname in sorted(os.listdir(self.decisions_dir)):
            if fname.endswith(".json"):
                fpath = os.path.join(self.decisions_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            data["_file"] = fname
                            self.decisions.append(data)
                except Exception as e:
                    print(f"Warning: Could not load decision {fname}: {e}", file=sys.stderr)

    def count(self) -> int:
        return len(self.decisions)

    def log_decision(self,
                     decision_type: str,
                     context: str,
                     selected_option: str,
                     rationale: str,
                     alternatives_considered: List[Dict[str, Any]],
                     project_title: str = "",
                     evidence_citations: Optional[List[str]] = None,
                     confidence: float = 0.95,
                     human_gate_required: bool = False,
                     human_gate_approved: bool = False,
                     approved_by: Optional[str] = None) -> str:
        """Records a new critical decision in the journal."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        did = f"dec_{timestamp}_{decision_type[:4]}"

        record = {
            "decision_id": did,
            "timestamp": datetime.now().isoformat(),
            "project_title": project_title,
            "decision_type": decision_type,
            "context": context,
            "selected_option": selected_option,
            "rationale": rationale,
            "alternatives_considered": alternatives_considered,
            "evidence_citations": evidence_citations or [],
            "confidence": confidence,
            "human_gate_required": human_gate_required,
            "human_gate_approved": human_gate_approved,
            "approved_by": approved_by or ("GhaderiSaber (124911145)" if human_gate_approved else None)
        }

        fpath = os.path.join(self.decisions_dir, f"{did}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        self._load_decisions()
        return did

    def query_decisions(self, keyword: Optional[str] = None, decision_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries historical decisions by keyword or category."""
        res = []
        kw = keyword.lower() if keyword else None
        dt = decision_type.lower() if decision_type else None

        for d in self.decisions:
            if dt and d.get("decision_type", "").lower() != dt:
                continue
            if kw:
                haystack = f"{d.get('project_title', '')} {d.get('context', '')} {d.get('selected_option', '')} {d.get('rationale', '')}".lower()
                if kw not in haystack:
                    continue
            res.append(d)
        return res


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Decision Journal Engine")
    parser.add_argument("--list", action="store_true", help="List all decisions in journal")
    parser.add_argument("--query", "-q", type=str, help="Search decisions by keyword")
    parser.add_argument("--type", "-t", type=str, help="Filter by decision type")
    parser.add_argument("--test-log", action="store_true", help="Log a sample test decision")

    args = parser.parse_args()
    engine = DecisionJournalEngine()

    if args.test_log:
        did = engine.log_decision(
            decision_type="statistical_method",
            project_title="Mindfulness & Burnout in Healthcare Workers",
            context="Student requested Baron & Kenny causal steps mediation, but sample size is N=142 and residuals are skewed.",
            selected_option="5,000-sample Percentile Bootstrap Mediation (Hayes PROCESS Model 4)",
            rationale="Baron & Kenny suffers from low statistical power and assumes normal sampling distribution of indirect effect, which is skewed. Bootstrap provides robust 95% asymmetric CI.",
            alternatives_considered=[
                {"option": "Baron & Kenny Causal Steps", "verdict": "REJECTED", "reason": "Inferior power; does not formally quantify indirect effect"},
                {"option": "Sobel Test", "verdict": "REJECTED", "reason": "Requires normality assumption of ab product; severely deflates power in N=142"}
            ],
            evidence_citations=["Hayes, A. F. (2018). Introduction to Mediation, Moderation, and Conditional Process Analysis. Guilford Press."],
            confidence=0.98,
            human_gate_required=False,
            human_gate_approved=True
        )
        print(f"Test decision successfully logged with ID: {did}")
        return

    if args.list or args.query or args.type:
        matches = engine.query_decisions(keyword=args.query, decision_type=args.type)
        print(f"\nDecision Journal ({len(matches)} matches):")
        print("=" * 75)
        for m in matches:
            print(f"• [{m.get('decision_id')}] Type: {m.get('decision_type')} | Date: {m.get('timestamp')[:10]}")
            print(f"  Project: {m.get('project_title')}")
            print(f"  Selected: {m.get('selected_option')}")
            print(f"  Rationale: {m.get('rationale')[:100]}...")
            print(f"  Human Gate: {'Approved by ' + str(m.get('approved_by')) if m.get('human_gate_approved') else 'Not required/Pending'}")
            print("-" * 75)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
