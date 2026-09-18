#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_adaptive_context.py — Verification Suite for academic-adaptive-context Skill

Verifies:
1. SKILL.md exists, parses, and strictly adheres to Directive 18 ceilings (<= 500 lines, <= 40,000 bytes).
2. Deterministic retrieval CLI (retrieve_adaptive_context.py) produces targeted briefings (markdown and JSON).
3. Acceptance Criterion 1: A lesson promoted in Project A automatically influences subsequent tasks in Project A.
4. Acceptance Criterion 2: Project A lesson is strictly quarantined and excluded from Project B or un-scoped queries.
5. Acceptance Criterion 3: Promoted cross-project lessons are retrieved automatically without explicit /learn invocation.
6. Anti-patterns, remedies, calibrated defaults, and known failure modes are surfaced.
7. Agent frontmatter integration: Confirms academic-adaptive-context is registered in durable and specialist agents.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager


class TestAcademicAdaptiveContext(unittest.TestCase):
    """Authoritative test suite for the academic-adaptive-context skill and integration."""

    def setUp(self):
        """Create isolated test workspace."""
        self.test_dir = tempfile.mkdtemp(prefix="test_adaptive_ctx_")
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.cli_script = os.path.join(
            ROOT_DIR,
            ".agents",
            "skills",
            "academic-adaptive-context",
            "scripts",
            "retrieve_adaptive_context.py"
        )

    def tearDown(self):
        """Clean up isolated test workspace."""
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_skill_definition_and_directive_18_compliance(self):
        """SKILL.md must exist, declare name, and strictly observe Directive 18 line and byte limits."""
        skill_path = os.path.join(
            ROOT_DIR,
            ".agents",
            "skills",
            "academic-adaptive-context",
            "SKILL.md"
        )
        self.assertTrue(os.path.isfile(skill_path), "SKILL.md must exist on disk.")

        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.splitlines()

        # Directive 18 ceilings
        self.assertLessEqual(len(lines), 500, f"SKILL.md exceeds 500 lines limit ({len(lines)} lines)")
        self.assertLessEqual(len(content.encode("utf-8")), 40000, "SKILL.md exceeds 40,000 bytes limit")

        # Frontmatter validation
        self.assertTrue(content.startswith("---"), "SKILL.md must start with YAML frontmatter")
        self.assertIn("name: academic-adaptive-context", content)
        self.assertIn("description:", content)

    def test_02_cli_retrieval_returns_targeted_briefing(self):
        """CLI tool must execute cleanly and output targeted markdown and json briefings."""
        cmd_json = [
            sys.executable,
            self.cli_script,
            "--capability", "mediation",
            "--task", "bootstrap_mediation",
            "--agent", "statistics-agent",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc_json = subprocess.run(cmd_json, capture_output=True, text=True)
        self.assertEqual(proc_json.returncode, 0, f"CLI json failed: {proc_json.stderr}")
        data = json.loads(proc_json.stdout)
        self.assertIn("query_context", data)
        self.assertEqual(data["query_context"]["capability"], "mediation")
        self.assertEqual(data["query_context"]["agent"], "statistics-agent")

        cmd_md = [
            sys.executable,
            self.cli_script,
            "--capability", "mediation",
            "--task", "bootstrap_mediation",
            "--agent", "statistics-agent",
            "--format", "markdown",
            "--base-dir", self.test_dir
        ]
        proc_md = subprocess.run(cmd_md, capture_output=True, text=True)
        self.assertEqual(proc_md.returncode, 0, f"CLI markdown failed: {proc_md.stderr}")
        self.assertIn("Active Learned Behavioral Context (MEDIATION)", proc_md.stdout)
        self.assertIn("Critical Anti-Patterns to Avoid", proc_md.stdout)

    def test_03_project_specific_lesson_influence_in_same_project(self):
        """Acceptance Criterion: A lesson promoted in Project A influences a later task in Project A."""
        # Add project-specific lesson in Project A
        lesson_id = "LSN-PROJ-A-SLOPE-001"
        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "source_experience_id": "EXP-PROJ-A-001",
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "VALIDATOR_FAILURE",
            "observed_failure": {
                "defect_type": "STATISTICAL_ASSUMPTION_VIOLATION",
                "description": "Covariate slope was non-homogeneous across groups in Project_A.",
                "failing_artifact_path": "projects/Project_A/ancova.json"
            },
            "desired_behavior": "In Project_A, switch to Johnson-Neyman floodlight probing when slope homogeneity fails.",
            "generalization": "Floodlight probing resolves non-parallel regression slopes.",
            "scope": "PROJECT_SPECIFIC",
            "confidence": 0.95,
            "evidence": {
                "metric_or_check": "CHK-SLOPE-HOMOGENEITY",
                "observed_value": 0.034,
                "threshold_value": 0.05
            },
            "related_skills": ["assumption-testing", "statistical-data-analyst"],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": "2026-09-18T12:00:00Z",
            "derived_by": "statistical-auditor"
        }
        # Save lesson in test_dir
        lesson_file = os.path.join(self.km.lessons_dir, f"{lesson_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            # Add project context
            lesson_data["context"] = {"project_id": "Project_A"}
            lesson_data["project_id"] = "Project_A"
            json.dump(lesson_data, f, indent=2)

        # Retrieve briefing for a LATER task in Project A
        cmd = [
            sys.executable,
            self.cli_script,
            "--capability", "chapter4",
            "--task", "ancova_hypothesis_testing",
            "--skill", "assumption-testing",
            "--project-id", "Project_A",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        res = json.loads(proc.stdout)

        # Confirm the lesson learned in Project A is retrieved
        retrieved_ids = [lsn.get("lesson_id") for lsn in res.get("lessons", [])]
        self.assertIn(lesson_id, retrieved_ids, "Project A lesson must be automatically available for Project A tasks")

    def test_04_project_specific_lesson_quarantined_from_other_projects(self):
        """Acceptance Criterion: Project A lesson is quarantined from Project B and un-scoped queries."""
        lesson_id = "LSN-PROJ-A-QUIRK-002"
        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "source_experience_id": "EXP-PROJ-A-002",
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "USER_FEEDBACK",
            "observed_failure": {
                "defect_type": "REPORTING_OR_TYPOGRAPHY_DEFECT",
                "description": "Supervisor in Project_A specifically prefers reverse coded label 'R_burnout'.",
                "failing_artifact_path": "projects/Project_A/report.docx"
            },
            "desired_behavior": "Label reversed burnout as 'R_burnout' exclusively in Project_A.",
            "generalization": "Adhere to supervisor nomenclature preference for Project_A.",
            "scope": "PROJECT_SPECIFIC",
            "confidence": 0.90,
            "evidence": {
                "metric_or_check": "CHK-USER-FEEDBACK",
                "observed_value": "burnout_rev",
                "threshold_value": "R_burnout"
            },
            "related_skills": ["chapter-4-writing", "data-cleaning"],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": "2026-09-18T12:30:00Z"
        }
        lesson_file = os.path.join(self.km.lessons_dir, f"{lesson_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            lesson_data["context"] = {"project_id": "Project_A"}
            lesson_data["project_id"] = "Project_A"
            json.dump(lesson_data, f, indent=2)

        # 1. Query for Project B -> MUST BE QUARANTINED
        cmd_b = [
            sys.executable,
            self.cli_script,
            "--capability", "chapter4",
            "--task", "chapter_4_table",
            "--skill", "chapter-4-writing",
            "--project-id", "Project_B",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc_b = subprocess.run(cmd_b, capture_output=True, text=True)
        res_b = json.loads(proc_b.stdout)
        ids_b = [lsn.get("lesson_id") for lsn in res_b.get("lessons", [])]
        self.assertNotIn(lesson_id, ids_b, "Project A lesson must NEVER leak into Project B!")

        # 2. Query without project ID -> MUST BE QUARANTINED
        cmd_none = [
            sys.executable,
            self.cli_script,
            "--capability", "chapter4",
            "--task", "chapter_4_table",
            "--skill", "chapter-4-writing",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc_none = subprocess.run(cmd_none, capture_output=True, text=True)
        res_none = json.loads(proc_none.stdout)
        ids_none = [lsn.get("lesson_id") for lsn in res_none.get("lessons", [])]
        self.assertNotIn(lesson_id, ids_none, "Project A lesson must NEVER leak into un-scoped query!")

    def test_05_cross_project_lesson_automatically_available(self):
        """Acceptance Criterion: Promoted cross-project lesson is retrieved automatically without /learn."""
        lesson_id = "LSN-CROSS-LEADING-ZERO-003"
        lesson_data = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "source_experience_id": "EXP-UNIVERSAL-001",
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "AUDITOR_FAILURE",
            "observed_failure": {
                "defect_type": "REPORTING_OR_TYPOGRAPHY_DEFECT",
                "description": "Leading zero omitted in Persian narrative: .041 was written instead of ۰.۰۴۱.",
                "failing_artifact_path": "ch4.docx"
            },
            "desired_behavior": "Always preserve leading zero in Persian text (۰.۰۴۱) per Directive 4.",
            "generalization": "In all Persian academic documents, numbers between 0 and 1 must maintain leading zero.",
            "scope": "CROSS_PROJECT_UNIVERSAL",
            "confidence": 0.99,
            "evidence": {
                "metric_or_check": "CHK-APA-LEADING-ZERO",
                "observed_value": ".041",
                "threshold_value": "۰.۰۴۱"
            },
            "related_skills": ["apa-reporting", "chapter-4-writing"],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": "2026-09-18T13:00:00Z"
        }
        lesson_file = os.path.join(self.km.lessons_dir, f"{lesson_id}.json")
        with open(lesson_file, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, indent=2)

        # Retrieve for ANY project
        cmd = [
            sys.executable,
            self.cli_script,
            "--capability", "chapter4",
            "--task", "chapter_4_table",
            "--skill", "apa-reporting",
            "--project-id", "Any_Arbitrary_Project",
            "--format", "json",
            "--base-dir", self.test_dir
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        res = json.loads(proc.stdout)
        ids = [lsn.get("lesson_id") for lsn in res.get("lessons", [])]
        self.assertIn(lesson_id, ids, "Cross-project lesson must automatically be available across all projects")

    def test_06_anti_pattern_and_failure_mode_surfacing(self):
        """Verifies that active anti-patterns and capability failure modes are surfaced with remedy guidance."""
        # 1. Add anti-pattern
        ap_id = self.km.add_anti_pattern({
            "category": "statistical",
            "defective_pattern": "Dichotomizing continuous moderator variables via median split.",
            "why_defective": "Reduces power by up to 50% and inflates Type I errors.",
            "observed_symptoms": ["Median split performed on Likert scale"],
            "corrective_remedy": "Continuous moderation using Hayes PROCESS Model 1 with mean-centering.",
            "detection_heuristic": {"trigger_rule": "Median split in moderation syntax"}
        })

        # 2. Record failure mode and calibrated defaults in capability memory
        self.km.record_capability_event(
            capability="moderation",
            event_type="failures",
            record_data={"experience_id": "EXP-MOD-001", "defect_type": "NON_CENTERED_INTERACTION"},
            metadata={"typical_remedy": "Mean-center continuous focal predictor and moderator before product calculation."}
        )
        self.km.record_capability_event(
            capability="moderation",
            event_type="successful_examples",
            record_data={"exemplar_id": "EXM-MOD-GOLD-001"},
            metadata={"calibrated_parameters": {"mean_center": True, "bootstrap": 5000}}
        )

        # Retrieve markdown briefing
        cmd = [
            sys.executable,
            self.cli_script,
            "--capability", "moderation",
            "--task", "process_model_1_moderation",
            "--format", "markdown",
            "--base-dir", self.test_dir
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        out = proc.stdout

        self.assertIn(ap_id, out)
        self.assertIn("Dichotomizing continuous moderator", out)
        self.assertIn("Approved Remedy", out)
        self.assertIn("Hayes PROCESS Model 1", out)
        self.assertIn("Calibrated Parameter Defaults", out)
        self.assertIn("mean_center", out)

    def test_07_agent_frontmatter_integration(self):
        """All 11 target durable and specialist agents must have academic-adaptive-context in their skills list."""
        target_agents = [
            "academic-orchestrator",
            "digital-saber",
            "validation-agent",
            "statistics-agent",
            "data-agent",
            "academic-writer",
            "statistical-auditor",
            "results-auditor",
            "academic-challenger",
            "psychometric-expert",
            "methodology-expert"
        ]

        for agent in target_agents:
            agent_file = os.path.join(ROOT_DIR, ".agents", "agents", agent, "agent.md")
            self.assertTrue(os.path.isfile(agent_file), f"Agent definition {agent} must exist")
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "academic-adaptive-context",
                content,
                f"Agent '{agent}' must include 'academic-adaptive-context' in frontmatter skills"
            )


if __name__ == "__main__":
    unittest.main()
