#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_chapter4_split_pipeline.py — Comprehensive Test Suite for Decoupled Chapter 4 Pipeline

Validates:
1. Authoritative 4-Phase Decoupled Pipeline specification in MICRO_STAGE_SEQUENCES.md:
   - Phase 4A: Data Engineering & Curation (Stages 4A.0 – 4A.2)
   - Phase 4B: Exploratory Analysis & Assumptions (Stages 4B.1 – 4B.4)
   - Phase 4C: Core Inferential Modeling & Anomaly Audit (Stages 4C.1 – 4C.5)
   - Phase 4D: Scholarly Persian Drafting, QC & Monograph Assembly (Stages 4D.0 – 4D.11)
2. Three-Gate Checkpoint Architecture:
   - Gate 1: Data Curation & Reliability Passport
   - Gate 2: Assumption Compliance & Inferential Method Authorization
   - Gate 3: Mathematical Admissibility & MSAI Sign-Off Gate
3. Strict Cognitive Role Boundaries:
   - Computational immunity: Phases 4A–4C are strictly "The Hands" (zero Persian narrative prose).
   - Hallucination prevention: Phase 4D is strictly "The Voice" (bound to audited empirical JSON payload).
4. Academic Orchestrator Task Routing & Sequence synchronization in agent.md.
"""

import os
import re
import sys
import json
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(REPO_ROOT, ".agents")
for p in [REPO_ROOT, AGENTS_DIR, os.path.join(AGENTS_DIR, "validators")]:
    if p not in sys.path:
        sys.path.insert(0, p)

MICRO_STAGES_PATH = os.path.join(REPO_ROOT, ".agents", "references", "MICRO_STAGE_SEQUENCES.md")
ORCHESTRATOR_AGENT_PATH = os.path.join(REPO_ROOT, ".agents", "agents", "academic-orchestrator", "agent.md")


class TestChapter4SplitPipeline(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.isfile(MICRO_STAGES_PATH), f"Missing {MICRO_STAGES_PATH}")
        with open(MICRO_STAGES_PATH, "r", encoding="utf-8") as f:
            self.micro_stages_content = f.read()

        self.assertTrue(os.path.isfile(ORCHESTRATOR_AGENT_PATH), f"Missing {ORCHESTRATOR_AGENT_PATH}")
        with open(ORCHESTRATOR_AGENT_PATH, "r", encoding="utf-8") as f:
            self.orchestrator_content = f.read()

    def test_01_chapter4_four_phases_documented(self):
        """Verifies Section 1 in MICRO_STAGE_SEQUENCES.md documents all 4 decoupled phases."""
        self.assertIn("## 1. Chapter 4: Decoupled Empirical Findings Pipeline (Phases 4A – 4D)", self.micro_stages_content)
        self.assertIn("Phase 4A: Data Engineering & Curation Gate", self.micro_stages_content)
        self.assertIn("Phase 4B: Exploratory Analysis & Assumptions Gate", self.micro_stages_content)
        self.assertIn("Phase 4C: Core Inferential Modeling & Anomaly Audit", self.micro_stages_content)
        self.assertIn("Phase 4D: Scholarly Persian Drafting, QC & Monograph Assembly", self.micro_stages_content)

    def test_02_three_gate_checkpoints_documented(self):
        """Verifies all 3 intermediate mathematical and methodological gates are documented."""
        self.assertIn("Gate 1: Data Curation Passport", self.micro_stages_content)
        self.assertIn("Gate 2: Assumption Compliance & Method Authorization", self.micro_stages_content)
        self.assertIn("Gate 3: Mathematical Admissibility & MSAI Sign-Off", self.micro_stages_content)

    def test_03_phase_4a_stages_and_roles(self):
        """Verifies Phase 4A stages (4A.0, 4A.1, 4A.2) and assigned subagents."""
        self.assertIn("Stage 4A.0", self.micro_stages_content)
        self.assertIn("Stage 4A.1", self.micro_stages_content)
        self.assertIn("Stage 4A.2", self.micro_stages_content)
        self.assertIn("data-curator", self.micro_stages_content)
        self.assertIn("psychometric-expert", self.micro_stages_content)
        self.assertIn("data_cleaned.xlsx", self.micro_stages_content)

    def test_04_phase_4b_stages_and_roles(self):
        """Verifies Phase 4B stages (4B.1 to 4B.4) and assumption certificate gate."""
        self.assertIn("Stage 4B.1", self.micro_stages_content)
        self.assertIn("Stage 4B.2", self.micro_stages_content)
        self.assertIn("Stage 4B.3", self.micro_stages_content)
        self.assertIn("Stage 4B.4", self.micro_stages_content)
        self.assertIn("01_demographics_payload.json", self.micro_stages_content)
        self.assertIn("03_assumptions_report.json", self.micro_stages_content)
        self.assertIn("04_correlations_payload.json", self.micro_stages_content)
        self.assertIn("Assumption Compliance Certificate", self.micro_stages_content)

    def test_05_phase_4c_stages_and_admissibility_gate(self):
        """Verifies Phase 4C stages (4C.1 to 4C.5), MSAI audit, and Gate 3 clearance."""
        self.assertIn("Stage 4C.1", self.micro_stages_content)
        self.assertIn("Stage 4C.2.1", self.micro_stages_content)
        self.assertIn("Stage 4C.3.1", self.micro_stages_content)
        self.assertIn("Stage 4C.4", self.micro_stages_content)
        self.assertIn("Stage 4C.5", self.micro_stages_content)
        self.assertIn("empirical_findings_payload.json", self.micro_stages_content)
        self.assertIn("statistical_audit_report.json", self.micro_stages_content)
        self.assertIn("structural_model_diagram.png", self.micro_stages_content)

    def test_06_phase_4d_stages_triads_and_voice_role(self):
        """Verifies Phase 4D drafting stages, triad outputs, and 3-table regression standard."""
        self.assertIn("Stage 4D.0", self.micro_stages_content)
        self.assertIn("Stage 4D.1", self.micro_stages_content)
        self.assertIn("Stage 4D.6.1", self.micro_stages_content)
        self.assertIn("Stage 4D.10", self.micro_stages_content)
        self.assertIn("Stage 4D.11", self.micro_stages_content)
        self.assertIn("academic-writer", self.micro_stages_content)
        self.assertIn("results-auditor", self.micro_stages_content)
        self.assertIn("final-judge", self.micro_stages_content)
        self.assertIn("Chapter_4_Results.docx", self.micro_stages_content)

    def test_07_decoupled_contract_invariants(self):
        """Verifies the core architectural invariants of the decoupled pipeline."""
        self.assertIn("Computational Immunity", self.micro_stages_content)
        self.assertIn("Hallucination Prevention", self.micro_stages_content)
        self.assertIn("One-Hypothesis-One-Stage Triad Invariant", self.micro_stages_content)
        self.assertIn("ZERO narrative text is drafted", self.micro_stages_content)
        self.assertIn("Emitting Persian narrative draft text in Phases 4A–4C is strictly prohibited", self.micro_stages_content)

    def test_08_academic_orchestrator_agent_synchronization(self):
        """Verifies academic-orchestrator/agent.md reflects the 4-phase decoupled pipeline."""
        self.assertIn("Phase 4A: DATA (data-curator)", self.orchestrator_content)
        self.assertIn("Phase 4B: ASSUMPTIONS (statistics-agent + statistical-expert)", self.orchestrator_content)
        self.assertIn("Phase 4D: DRAFTING (Tables First -> Dynamic Non-Template Narration -> Triad Assembly via academic-writer + results-auditor + final-judge)", self.orchestrator_content)
        self.assertIn("Chapter 4 Findings (Phases 4A–4D Decoupled)", self.orchestrator_content)
        self.assertIn("Phase 4D: Scholarly Drafting (Tables First -> Dynamic Non-Template Narration -> 4D.0–4D.11)", self.orchestrator_content)


    def test_09_writing_phase_internal_separation(self):
        """Verifies Phase 4D internally separates into Tables First and Dynamic Narration."""
        self.assertIn("The Internal Writing Phase Decoupling (Tables First", self.micro_stages_content)
        self.assertIn("Step 4D-1: Deterministic Table Scaffolding (Tables First)", self.micro_stages_content)
        self.assertIn("Step 4D-2: Dynamic Epistemic Narration Formulation", self.micro_stages_content)
        self.assertIn("Step 4D-3: Synchronized Triad Compilation & Monograph Assembly", self.micro_stages_content)
        self.assertIn("Zero narrative prose is written in this step", self.micro_stages_content)

    def test_10_zero_template_dynamic_narration_invariant(self):
        """Verifies that prewritten templates, canned boilerplate, and placeholders are strictly prohibited."""
        self.assertIn("Zero-Template Dynamic Narration Invariant", self.micro_stages_content)
        self.assertIn("Strict Zero-Template & Anti-Boilerplate Invariant", self.micro_stages_content)
        self.assertIn("Prewritten boilerplate, static placeholders", self.micro_stages_content)
        self.assertIn("mechanical fill-in-the-blank text are **strictly prohibited**", self.micro_stages_content)
        self.assertIn("refuse and fail any deliverable containing empty, canned, or template placeholder text", self.micro_stages_content)

    def test_11_mechanical_invariant_registered_in_hook_rules(self):
        """Verifies AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION is registered and active in enforced_invariants.json."""
        import json
        invariants_path = os.path.join(REPO_ROOT, ".agents", "hooks", "rules", "enforced_invariants.json")
        self.assertTrue(os.path.isfile(invariants_path), f"Missing {invariants_path}")
        with open(invariants_path, "r", encoding="utf-8") as f:
            invariants_data = json.load(f)

        invariants = invariants_data.get("invariants", {})
        self.assertIn("AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION", invariants)
        rule = invariants["AP-2026-ZERO-TEMPLATE-DYNAMIC-NARRATION"]
        self.assertTrue(rule.get("enabled"))
        self.assertEqual(rule.get("check_type"), "regex_ban")
        self.assertIn("در این بخش", rule.get("pattern", ""))

    def test_12_wrapped_result_json_numerical_validation(self):
        """Verifies validate_numbers properly extracts parameters from wrapped result_json payloads."""
        import tempfile
        from validators.numerical_consistency.validator import validate_numbers

        # Construct a synthetic SEM payload conforming to statistical_execution_result.schema.json
        payload = {
            "contract_version": "1.0.0",
            "execution_id": "test_exec_01",
            "stage": "05_macro_model",
            "sample_size": 300,
            "result_json": {
                "sample_size": 300,
                "test_statistics": {
                    "chi2": 12.5,
                    "df": 8,
                    "cfi": 0.985,
                    "tli": 0.978,
                    "rmsea": 0.042,
                    "srmr": 0.035
                },
                "structural_paths": [
                    {
                        "parameter_label": "X -> Y",
                        "unstandardized_b": 0.35,
                        "standardized_beta": 0.28,
                        "se": 0.07,
                        "critical_ratio_z": 5.0,
                        "p_value": 0.00001
                    }
                ]
            }
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tmp:
            json.dump(payload, tmp)
            tmp_path = tmp.name

        try:
            res = validate_numbers(tmp_path)
            self.assertEqual(res["verdict"], "PASS")
            self.assertGreater(res["evidence_items_audited"], 0)
            self.assertEqual(res["errors"], [])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_13_stage_scoped_validation_suite_data_analysis(self):
        """Verifies run_all_validators passes for data analysis stages with only .json payload."""
        import tempfile
        import shutil
        from validators.run_all_validators import run_suite

        temp_dir = tempfile.mkdtemp(prefix="test_stage_val_")
        try:
            # Create a data analysis payload file
            payload_file = os.path.join(temp_dir, "05_macro_model_payload.json")
            with open(payload_file, "w", encoding="utf-8") as f:
                json.dump({
                    "contract_version": "1.0.0",
                    "execution_id": "exec_05",
                    "sample_size": 250,
                    "result_json": {
                        "sample_size": 250,
                        "test_statistics": {"chi2": 15.2, "df": 10, "cfi": 0.98, "rmsea": 0.04},
                        "structural_paths": [
                            {"parameter_label": "path_1", "critical_ratio_z": 4.2, "p_value": 0.0001}
                        ]
                    }
                }, f)

            rep = run_suite(stage_dir=temp_dir, stage_id="05_macro_model_payload")
            self.assertEqual(rep["overall_verdict"], "PASS")
            self.assertEqual(rep["evidence_summary"]["checks_failed"], 0)
            self.assertEqual(rep["evidence_summary"]["checks_blocked"], 0)
            self.assertGreater(rep["evidence_summary"]["checks_passed"], 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_14_tier_summaries_evaluated_before_defense_certification(self):
        """Verifies Tier 1 and Tier 2 summaries are evaluated and passed into defense certification."""
        from validators.defense_readiness_compiler import run_defense_certification
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp(prefix="test_tier_eval_")
        try:
            with open(os.path.join(temp_dir, "05_macro_model_payload.json"), "w", encoding="utf-8") as f:
                json.dump({"sample_size": 200}, f)

            cert = run_defense_certification(
                temp_dir,
                tier1_result={"verdict": "PASS"},
                tier2_result={"verdict": "PASS"},
                tier3_result={"verdict": "PASS"}
            )
            self.assertTrue(cert["defense_verdict"].startswith("PASS"))
            self.assertGreaterEqual(cert["overall_score_out_of_20"], 14.0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_15_verify_chapter4_gate3_clearance_detects_missing_payloads(self):
        """Verifies verify_chapter4_gate3_clearance detects missing inferential payloads."""
        import tempfile
        import shutil
        from contracts.canonical_pipelines import verify_chapter4_gate3_clearance

        temp_dir = tempfile.mkdtemp(prefix="test_gate3_clearance_")
        try:
            # 1. Empty directory -> Fails with all items missing
            ok, err_msg, missing = verify_chapter4_gate3_clearance([temp_dir])
            self.assertFalse(ok)
            self.assertEqual(len(missing), 4)
            self.assertIn("Gate 3 Clearance Invariant", err_msg)

            # 2. Add macro SEM and H1 -> Still missing bootstrap mediation and decision matrix
            with open(os.path.join(temp_dir, "05_macro_model_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "06_hypothesis_1_payload.json"), "w") as f:
                f.write("{}")
            ok, err_msg, missing = verify_chapter4_gate3_clearance([temp_dir])
            self.assertFalse(ok)
            self.assertEqual(len(missing), 2)
            self.assertTrue(any("mediation" in m.lower() for m in missing))
            self.assertTrue(any("decision matrix" in m.lower() for m in missing))

            # 3. Add mediation payload and decision matrix -> PASS
            with open(os.path.join(temp_dir, "08_mediation_analysis_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "master_decision_matrix.json"), "w") as f:
                f.write("{}")
            ok, err_msg, missing = verify_chapter4_gate3_clearance([temp_dir])
            self.assertTrue(ok)
            self.assertEqual(len(missing), 0)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_16_verify_capability_routing_blocks_academic_writer_without_gate3(self):
        """Verifies verify_capability_routing mechanically blocks academic-writer if Gate 3 is incomplete."""
        import tempfile
        import shutil
        from contracts.canonical_pipelines import verify_capability_routing

        temp_dir = tempfile.mkdtemp(prefix="test_cap_routing_gate3_")
        try:
            # Workspace has macro model and H1, but MISSING bootstrap mediation
            with open(os.path.join(temp_dir, "05_macro_model_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "06_hypothesis_1_payload.json"), "w") as f:
                f.write("{}")

            envelope = {
                "task_id": "TSK-2026-CH4-STAGE-45-DRAFTING",
                "stage": "Stage 4.5: Macro Path Model Findings (Drafting & Triad Completion)",
                "worker_agent": "academic-writer",
                "objective": "Synthesize authentic Persian scholarly findings narrative into 03_deliverables/05_macro_model.docx"
            }
            prompt = "Draft Stage 4.5 Macro Model findings in Word (.docx) and Markdown (.md)"

            ok, reason = verify_capability_routing(
                worker_agent="academic-writer",
                prompt=prompt,
                envelope=envelope,
                workspaces=[temp_dir]
            )
            self.assertFalse(ok)
            self.assertIn("Gate 3 Clearance Invariant", reason)
            self.assertIn("Bootstrap Mediation Analysis Payload", reason)

            # Now add bootstrap mediation and decision matrix
            with open(os.path.join(temp_dir, "08_mediation_analysis_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "master_decision_matrix.json"), "w") as f:
                f.write("{}")

            ok_pass, reason_pass = verify_capability_routing(
                worker_agent="academic-writer",
                prompt=prompt,
                envelope=envelope,
                workspaces=[temp_dir]
            )
            self.assertTrue(ok_pass)
            self.assertIn("verified", reason_pass.lower())
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_17_verify_pipeline_stage_prerequisites_phase4c_and_phase4d(self):
        """Verifies verify_pipeline_stage_prerequisites validates Phase 4C and 4D dependencies."""
        import tempfile
        import shutil
        from contracts.canonical_pipelines import verify_pipeline_stage_prerequisites

        temp_dir = tempfile.mkdtemp(prefix="test_prereq_stages_")
        try:
            # Stage 4C.1 without assumptions -> FAIL
            ok, reason = verify_pipeline_stage_prerequisites("Stage 4C.1: Macro SEM", [temp_dir])
            self.assertFalse(ok)
            self.assertIn("MISSING on disk", reason)

            # Add Gate 2 assumptions and correlation matrix
            with open(os.path.join(temp_dir, "03_assumptions_report.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "04_correlations_payload.json"), "w") as f:
                f.write("{}")
            ok, reason = verify_pipeline_stage_prerequisites("Stage 4C.1: Macro SEM", [temp_dir])
            self.assertTrue(ok)

            # Stage 4C.3 without macro model or H1 -> FAIL
            ok, reason = verify_pipeline_stage_prerequisites("Stage 4C.3: Indirect Mediation", [temp_dir])
            self.assertFalse(ok)

            with open(os.path.join(temp_dir, "05_macro_model_payload.json"), "w") as f:
                f.write("{}")
            ok, reason = verify_pipeline_stage_prerequisites("Stage 4C.3: Indirect Mediation", [temp_dir])
            self.assertTrue(ok)

            # Stage 4D.5 drafting without Gate 3 (missing mediation & decision matrix) -> FAIL
            ok, reason = verify_pipeline_stage_prerequisites("Stage 4D.5: Macro Path Findings Drafting", [temp_dir])
            self.assertFalse(ok)

            with open(os.path.join(temp_dir, "06_hypothesis_1_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "08_mediation_analysis_payload.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "master_decision_matrix.json"), "w") as f:
                f.write("{}")

            ok, reason = verify_pipeline_stage_prerequisites("Stage 4D.5: Macro Path Findings Drafting", [temp_dir])
            self.assertTrue(ok)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_18_academic_orchestrator_guard_blocks_premature_academic_writer(self):
        """Verifies academic-orchestrator/guard.py handle_pre_tool_use denies premature writer dispatch."""
        import tempfile
        import shutil
        import importlib.util

        guard_path = os.path.join(REPO_ROOT, ".agents", "agents", "academic-orchestrator", "guard.py")
        spec = importlib.util.spec_from_file_location("test_orch_guard", guard_path)
        guard_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(guard_mod)

        temp_dir = tempfile.mkdtemp(prefix="test_guard_writer_")
        try:
            # Workspace has only Gate 2 assumptions, but NO mediation payload
            with open(os.path.join(temp_dir, "03_assumptions_report.json"), "w") as f:
                f.write("{}")
            with open(os.path.join(temp_dir, "05_macro_model_payload.json"), "w") as f:
                f.write("{}")

            payload = {
                "caller": "academic-orchestrator",
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": json.dumps([{
                            "TypeName": "academic-writer",
                            "Prompt": (
                                "### Contractual Delegation Envelope (CDE)\n"
                                "```json\n"
                                "{\n"
                                '  "task_id": "TSK-2026-CH4-STAGE-45-DRAFTING",\n'
                                '  "stage": "Stage 4.5: Macro Path Model Findings (Drafting & Triad Completion)",\n'
                                '  "worker_agent": "academic-writer",\n'
                                '  "objective": "Synthesize authentic Persian scholarly findings narrative into 03_deliverables/05_macro_model.docx",\n'
                                '  "inputs": ["03_deliverables/05_macro_model_payload.json"],\n'
                                '  "required_artifacts": ["03_deliverables/05_macro_model.docx"]\n'
                                "}\n"
                                "```\n"
                            )
                        }])
                    }
                },
                "workspacePaths": [temp_dir]
            }

            res = guard_mod.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Gate 3 Clearance Invariant", res.get("reason", ""))
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
