#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/modernize_stage_invariants.py

Modernizes stage artifact invariants in .agents/hooks/rules/enforced_invariants.json
to align with the Two-Tier Drafting Architecture:
- Disables outdated 3-artifact triad rules that demand (.docx, .md, .json) across all stages.
- Updates statements and remedies to reflect:
  * Pure data stages: .json only
  * Pure narrative stages: .md only
  * Micro-stage empirical findings: .json + .md (dyad; .docx optional)
  * Chapter consolidation milestones: .docx + .md (monograph)
  * Continuous learning pipelines: .json / .md only (zero .docx)
"""

import os
import json
from datetime import datetime, timezone

INVARIANTS_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "hooks", "rules", "enforced_invariants.json")
)


def modernize_invariants() -> int:
    if not os.path.isfile(INVARIANTS_FILE):
        print(f"Error: Invariants file not found: {INVARIANTS_FILE}")
        return 1

    with open(INVARIANTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    invariants = data.get("invariants", {})
    updated = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    # 1. CAND-2026-ATOMIC-TRIAD-CH4-001
    if "CAND-2026-ATOMIC-TRIAD-CH4-001" in invariants:
        inv = invariants["CAND-2026-ATOMIC-TRIAD-CH4-001"]
        inv["enabled"] = True
        inv["statement"] = (
            "Atomic Micro-Stage Findings Invariant: In Tier 1 micro-stages, enforce the analytical dyad "
            "(.json + .md; .docx optional). In Tier 2 chapter milestones, enforce the monograph (.docx + .md)."
        )
        inv["violation_message"] = "Fragmented pipeline state: stage deliverables do not match required artifacts."
        inv["remedy"] = (
            "Generate required deliverables based on stage type (data stages: .json; narrative stages: .md; "
            "empirical micro-stages: .json + .md; chapter consolidation: .docx + .md)."
        )
        inv["updated_at"] = now_iso
        updated += 1

    # 2. CAND-2026-ATOMIC-TRIAD-ORCH-001
    if "CAND-2026-ATOMIC-TRIAD-ORCH-001" in invariants:
        inv = invariants["CAND-2026-ATOMIC-TRIAD-ORCH-001"]
        inv["enabled"] = True
        inv["statement"] = (
            "Two-Tier Drafting Validation Invariant: Enforce the Two-Tier Drafting Architecture. Pure computational "
            "payloads are validated as JSON, while chapter consolidation enforces the complete monograph (.docx + .md)."
        )
        inv["pattern"] = r"--bypass-stage-gates|--skip-monograph-assembly"
        inv["violation_message"] = "Bypassing stage validation or skipping chapter monograph assembly is prohibited."
        inv["remedy"] = "Ensure stage deliverables conform to the Two-Tier Drafting Architecture before validation."
        inv["updated_at"] = now_iso
        updated += 1

    # 3. AP-2026-DECOUPLED-PAYLOAD-TRIAD-FRAGMENTATION
    if "AP-2026-DECOUPLED-PAYLOAD-TRIAD-FRAGMENTATION" in invariants:
        inv = invariants["AP-2026-DECOUPLED-PAYLOAD-TRIAD-FRAGMENTATION"]
        inv["enabled"] = True
        inv["statement"] = (
            "Two-Tier Drafting Invariant: Stage execution must synthesize required deliverables according to stage type "
            "(data stages: .json; narrative stages: .md; empirical micro-stages: .json + .md; chapter consolidation: .docx + .md)."
        )
        inv["pattern"] = r"(?s)bypass_monograph_assembly.*\.docx"
        inv["violation_message"] = "Stage execution missing required deliverables on disk."
        inv["remedy"] = "Synthesize the declared stage deliverables before triggering validation or declaring completion."
        inv["updated_at"] = now_iso
        updated += 1

    # 4. AP-2026-MISSING-TRIAD-JSON-001
    if "AP-2026-MISSING-TRIAD-JSON-001" in invariants:
        inv = invariants["AP-2026-MISSING-TRIAD-JSON-001"]
        inv["enabled"] = True
        inv["statement"] = (
            "Canonical Stage Payload Naming Invariant: Generate required deliverables with correct canonical file names "
            "for every stage. Ensure parameter files are fully populated."
        )
        inv["violation_message"] = "Stage deliverables missing required data payloads or improperly named."
        inv["remedy"] = "Generate required deliverables with correct canonical names for every micro-stage."
        inv["updated_at"] = now_iso
        updated += 1

    # 5. CAND-20260927-THESIS-INTEGRITY-001
    if "CAND-20260927-THESIS-INTEGRITY-001" in invariants:
        inv = invariants["CAND-20260927-THESIS-INTEGRITY-001"]
        inv["statement"] = (
            "BAN-20260927-002: Premature global validation on 03_deliverables is blocked. "
            "Ensure all micro-stage deliverables are complete on disk before running global suite."
        )
        inv["violation_message"] = (
            "BAN-20260927-002: Premature global validation on 03_deliverables is blocked. "
            "Ensure all micro-stage deliverables are complete on disk before running global suite."
        )
        inv["remedy"] = (
            "Wait until stage deliverables are synthesized before running global validation, "
            "or target a specific micro-stage directory with --stage-dir."
        )
        inv["updated_at"] = now_iso
        updated += 1

    # 6. CAND-20260927-CHAPTER4-WRITING-001
    if "CAND-20260927-CHAPTER4-WRITING-001" in invariants:
        inv = invariants["CAND-20260927-CHAPTER4-WRITING-001"]
        inv["remedy"] = (
            "Target specific micro-stage directories for validation, or ensure all stage deliverables "
            "are generated before running global validation."
        )
        inv["updated_at"] = now_iso
        updated += 1

    data["invariants"] = invariants
    data["updated_at"] = now_iso

    with open(INVARIANTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully modernized {updated} invariants in {INVARIANTS_FILE}")

    # Supersede legacy triad knowledge items so adaptive context boundary no longer injects them
    knowledge_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "learning", "knowledge")
    )
    legacy_items = [
        os.path.join(knowledge_dir, "lessons", "LSN-2026-ATOMIC-MICRO-STAGE-TRIAD-SYNTHESIS.json"),
        os.path.join(knowledge_dir, "lessons", "LSN-2026-MICRO-STAGE-TRIAD-SYNCHRONIZATION.json"),
        os.path.join(knowledge_dir, "lessons", "LSN-2026-MISSING-TRIAD-JSON-001.json"),
        os.path.join(knowledge_dir, "anti-patterns", "AP-2026-DECOUPLED-PAYLOAD-TRIAD-FRAGMENTATION.json"),
        os.path.join(knowledge_dir, "anti-patterns", "AP-2026-MISSING-TRIAD-JSON-001.json"),
        os.path.join(knowledge_dir, "anti-patterns", "AP-2026-PREMATURE-GLOBAL-VALIDATION-DECOUPLED-TRIAD.json"),
    ]
    for k_path in legacy_items:
        if os.path.isfile(k_path):
            try:
                with open(k_path, "r", encoding="utf-8") as kf:
                    k_data = json.load(kf)
                k_data["status"] = "SUPERSEDED"
                k_data["is_active_behavior"] = False
                k_data["reusable"] = False
                k_data["updated_at"] = now_iso
                with open(k_path, "w", encoding="utf-8") as kf:
                    json.dump(k_data, kf, indent=2, ensure_ascii=False)
                print(f"Marked SUPERSEDED: {os.path.basename(k_path)}")
            except Exception as e:
                print(f"Failed to supersede {k_path}: {e}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(modernize_invariants())
