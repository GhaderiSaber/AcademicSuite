#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_agent_roster.py — Cognitive Subagent Roster & Architecture Verification
----------------------------------------------------------------------------
Validates:
  1. Existence and valid YAML frontmatter for all 14 subagents in .agents/agents/
  2. Task packet generation across all 14 roles in MultiAgentOrchestrator
  3. Strict schema validation (valid & invalid payloads) across all 14 roles
  4. Questionnaire registry path resolution (data/questionnaires/ & root symlink)
  5. Constitutional alignment in AGENTS.md and HYBRID_MULTI_AGENT_SPEC.md
"""

import os
import sys
import unittest
import json
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

# Dynamically import multi_agent_orchestrator and questionnaire_resolver
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "psychometric-scale-resolver", "scripts"))

from multi_agent_orchestrator import MultiAgentOrchestrator
from questionnaire_resolver import find_excel_registry, search_registry, get_scale_profile

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
AGENTS_DEF_DIR = os.path.join(AGENTS_DIR, "agents")


class TestAgentRoster(unittest.TestCase):
    """Verifies the complete 14-agent cognitive architecture and directory restructuring."""

    EXPECTED_ROLES = [
        "digital-saber",
        "methodology-expert",
        "statistical-expert",
        "statistical-auditor",
        "results-auditor",
        "academic-writer",
        "literature-expert",
        "evidence-auditor",
        "final-judge",
        "psychometric-expert",
        "qualitative-analyst",
        "meta-analyst",
        "journal-strategist",
        "intervention-designer"
    ]

    def setUp(self):
        self.orchestrator = MultiAgentOrchestrator(workspace_root=ROOT_DIR)

    def test_all_14_subagent_files_exist(self):
        """Verify that all 14 subagent markdown definitions exist in .agents/agents/."""
        self.assertTrue(os.path.isdir(AGENTS_DEF_DIR), f"Directory not found: {AGENTS_DEF_DIR}")
        for role in self.EXPECTED_ROLES:
            filepath = os.path.join(AGENTS_DEF_DIR, f"{role}.md")
            self.assertTrue(
                os.path.isfile(filepath),
                f"Missing agent definition file for '{role}': {filepath}"
            )

    def test_agent_frontmatter_and_content_structure(self):
        """Verify YAML frontmatter (name, description, role, skills) and non-empty body for each agent."""
        for role in self.EXPECTED_ROLES:
            filepath = os.path.join(AGENTS_DEF_DIR, f"{role}.md")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("---"), f"{role}.md must start with YAML frontmatter delimiter '---'")
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{role}.md missing closing frontmatter delimiter '---'")

            frontmatter = parts[1]
            body = parts[2].strip()

            # Verify required frontmatter keys
            self.assertIn("name:", frontmatter, f"{role}.md frontmatter missing 'name'")
            self.assertIn("description:", frontmatter, f"{role}.md frontmatter missing 'description'")
            self.assertIn("role:", frontmatter, f"{role}.md frontmatter missing 'role'")
            self.assertIn("skills:", frontmatter, f"{role}.md frontmatter missing 'skills'")

            # Verify substantial markdown content
            self.assertGreater(len(body), 150, f"{role}.md body content is too short or empty")

    def test_orchestrator_roles_count_and_parity(self):
        """Verify MultiAgentOrchestrator.ROLES has exact 14 roles matching expected roster."""
        self.assertEqual(len(self.orchestrator.ROLES), 14)
        self.assertEqual(set(self.orchestrator.ROLES), set(self.EXPECTED_ROLES))

    def test_task_packet_generation_for_all_14_roles(self):
        """Verify generate_task_packet produces a valid, actionable packet for all 14 roles."""
        for role in self.EXPECTED_ROLES:
            packet = self.orchestrator.generate_task_packet(
                workflow="chapter4",
                role=role,
                context_dir="output"
            )
            self.assertIsInstance(packet, dict, f"Task packet for {role} must be a dict")
            self.assertIn("task_id", packet, f"Task packet for {role} missing 'task_id'")
            self.assertEqual(packet.get("role"), role, f"Task packet role mismatch for {role}")
            self.assertIn("stage", packet, f"Task packet for {role} missing 'stage'")
            self.assertIn("instructions", packet, f"Task packet for {role} missing 'instructions'")
            self.assertTrue(
                "expected_return_schema" in packet or "expected_output_schema" in packet,
                f"Task packet for {role} missing expected schema"
            )
            self.assertGreater(len(packet["instructions"]), 0, f"Instructions for {role} are empty")

    def test_schema_validation_valid_payloads(self):
        """Verify schema validation accepts valid payloads across all 14 roles."""
        valid_mock_payloads = {
            "methodology-expert": {
                "methodology_approved": True,
                "power_adequate": True,
                "sampling_power": {"target_power": 0.80, "calculated_n": 60},
                "design_safeguards": ["Random allocation", "Active control"]
            },
            "statistical-expert": {
                "primary_analysis_type": "ANCOVA",
                "assumptions_met": True,
                "hypotheses_evaluated": True
            },
            "statistical-auditor": {
                "audit_verdict": "NORMAL_EMPIRICAL",
                "degrees_of_freedom_verified": True,
                "slope_homogeneity_verified": True,
                "msai_score": 0.12
            },
            "results-auditor": {
                "qc_passed": True,
                "leading_zero_concordance": True,
                "p_value_formatting_valid": True,
                "omml_math_preserved": True
            },
            "academic-writer": {
                "draft_complete": True,
                "section_word_counts": {"findings": 1250},
                "cadence_burstiness_cv": 0.58,
                "persian_half_space_count": 85
            },
            "literature-expert": {
                "epistemic_evidence_weight": "STRONG",
                "harvested_studies_count": 18,
                "theoretical_mechanisms_identified": ["Beck Cognitive Triad"]
            },
            "evidence-auditor": {
                "citation_concordance_rate": 1.0,
                "orphaned_citations": [],
                "ghost_references": [],
                "irandoc_similarity_risk": "LOW"
            },
            "final-judge": {
                "verdict": "APPROVED_FOR_DEFENSE",
                "defense_readiness_score": 92.5,
                "viva_voce_challenges": [{"challenge": "C1", "model_answer": "A1"}]
            },
            "digital-saber": {
                "orchestration_status": "COMPLETED",
                "workflow_verdict": "APPROVED",
                "stages_verified": [0, 3, 4, 5, 6, 7, 8]
            },
            "psychometric-expert": {
                "psychometrics_valid": True,
                "reliability_verified": True,
                "instruments_validated": ["BDI-II", "STAI"]
            },
            "qualitative-analyst": {
                "thematic_structure_valid": True,
                "trustworthiness_audit_passed": True,
                "paradigm": "THEMATIC_ANALYSIS"
            },
            "meta-analyst": {
                "prisma_flow_compliant": True,
                "pooled_effect_significant": True,
                "heterogeneity": {"I2": 42.5, "Q_p": 0.08}
            },
            "journal-strategist": {
                "imrad_structure_compliant": True,
                "highlights_within_limit": True,
                "target_tier": "ISI_Q1"
            },
            "intervention-designer": {
                "protocol_sessions_count": 8,
                "session_anatomy_complete": True,
                "approach": "ACT"
            }
        }

        for role in self.EXPECTED_ROLES:
            payload = valid_mock_payloads[role]
            is_valid, errors = self.orchestrator.validate_critique_payload(role, payload)
            self.assertTrue(is_valid, f"Role {role} failed validation on valid payload: {errors}")
            self.assertEqual(len(errors), 0)

    def test_schema_validation_catches_missing_fields(self):
        """Verify schema validation rejects payloads missing required fields."""
        for role in self.EXPECTED_ROLES:
            empty_payload = {}
            is_valid, errors = self.orchestrator.validate_critique_payload(role, empty_payload)
            self.assertFalse(is_valid, f"Role {role} should have failed on empty payload")
            self.assertGreater(len(errors), 0, f"Role {role} should report missing fields")

    def test_questionnaire_registry_resolution(self):
        """Verify questionnaire resolver finds Questionnaires.xlsx in data/questionnaires/."""
        resolved_path = find_excel_registry()
        self.assertIsNotNone(resolved_path, "Could not resolve Questionnaires.xlsx")
        self.assertTrue(os.path.isfile(resolved_path), f"Resolved path does not exist: {resolved_path}")

        # Query standard instruments (e.g. Beck Depression Inventory / افسردگی بک and BDI)
        results_persian = search_registry("افسردگی", excel_path=resolved_path)
        self.assertGreater(len(results_persian), 0, "Failed to search standard Persian scale 'افسردگی'")

        results_en = search_registry("Depression", excel_path=resolved_path)
        self.assertGreater(len(results_en), 0, "Failed to search standard English scale 'Depression'")

        profile = get_scale_profile("Beck Depression", excel_path=resolved_path)
        self.assertIsNotNone(profile, "Failed to get scale profile for 'Beck Depression'")

    def test_constitutional_documentation_references_all_14_agents(self):
        """Verify AGENTS.md and HYBRID_MULTI_AGENT_SPEC.md explicitly document all 14 roles."""
        agents_md_path = os.path.join(ROOT_DIR, "AGENTS.md")
        with open(agents_md_path, "r", encoding="utf-8") as f:
            agents_md = f.read()

        spec_path = os.path.join(AGENTS_DIR, "architecture", "HYBRID_MULTI_AGENT_SPEC.md")
        with open(spec_path, "r", encoding="utf-8") as f:
            spec_md = f.read()

        for role in self.EXPECTED_ROLES:
            self.assertIn(
                role,
                agents_md,
                f"AGENTS.md does not document role '{role}'"
            )
            self.assertIn(
                role,
                spec_md,
                f"HYBRID_MULTI_AGENT_SPEC.md does not document role '{role}'"
            )


if __name__ == "__main__":
    unittest.main()
