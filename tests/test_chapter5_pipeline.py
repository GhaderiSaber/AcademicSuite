#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_chapter5_pipeline.py — Comprehensive Test Suite for Chapter 5 Pipeline

Validates:
1. Article Enrichment Engine (parsing articles, empirical extraction, mechanisms, keyword queries)
2. Strict Zero-Template Triad Scaffold (rejects missing narrative, creates .docx, .md, .json)
3. Micro-Stage Triad Assembly (merging verified stages into Chapter_5_Discussion.docx/md + manifest)
4. State Machine Chapter 5 Governance (initialization, milestones, stage DAG, sequential progression)
5. Orchestrator Dependency Resolution & Capabilities (prerequisite DAG, keyword routing)
6. Orchestrator CLI Presets & Registry integration
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "persian-discussion-builder", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts"))

import academic_state_manager as sm
from academic_state_manager import StrictStateMachine, StageState, ProjectState, CHAPTER_5_STAGE_GRAPH
import article_enrichment_engine as aee
import scaffold_chapter5_triad as sct
import assemble_chapter5 as ac5
import orchestrator_dependency_resolver as odr
import orchestrator_cli as ocli


class TestChapter5Pipeline(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ch5_test_")
        self.state_dir = os.path.join(self.temp_dir, "academic-state")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # 1. Article Enrichment Engine Tests
    # --------------------------------------------------------------------------
    def test_01_article_enrichment_engine(self):
        """Test parsing local research articles into structured evidence cards."""
        papers_dir = os.path.join(self.temp_dir, "papers")
        os.makedirs(papers_dir, exist_ok=True)

        sample_article_text = (
            "Title: Emotional Schema Therapy and Psychological Well-being in Healthcare Workers\n"
            "Author: Leahy et al., 2022\n"
            "Journal: Journal of Cognitive Psychotherapy, 36(2), 115-130.\n"
            "Abstract: This study examined the efficacy of Emotional Schema Therapy (EST) on 350 nurses (N = 350). "
            "Using a structural equation model with standard regression, results indicated that cognitive reappraisal "
            "significantly mediated the relationship between schema endorsement and emotional exhaustion (beta = 0.42, p < .001). "
            "Scale reliability showed Cronbach alpha = 0.89 for the emotional schema scale.\n"
            "Discussion: Findings align with Bandura's self-efficacy theory and Gross's process model of emotion regulation. "
            "Individuals with maladaptive beliefs about emotion experience higher burnout due to cognitive inflexibility."
        )
        sample_file = os.path.join(papers_dir, "leahy_2022.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(sample_article_text)

        corpus_out = os.path.join(self.temp_dir, "article_cards.json")
        corpus = aee.build_article_corpus(papers_dir, output_json=corpus_out)

        self.assertEqual(corpus["status"], "SUCCESS")
        self.assertEqual(corpus["total_articles"], 1)
        self.assertTrue(os.path.isfile(corpus_out))

        card = corpus["articles"][0]
        self.assertIn("Leahy", card["author"])
        self.assertEqual(card["sample_size"], 350)
        self.assertTrue(any(b["value"] == 0.89 for b in card["reliability_benchmarks"]))
        self.assertTrue(len(card["theoretical_mechanisms"]) > 0)

        # Test query
        matches = aee.query_corpus_by_keyword(corpus, "Gross")
        self.assertEqual(len(matches), 1)

    # --------------------------------------------------------------------------
    # 2. Strict Zero-Template Triad Compiler Tests
    # --------------------------------------------------------------------------
    def test_02_scaffold_triad_zero_template_rejection(self):
        """Zero Template Invariant: Triad compiler must refuse execution if agent narrative is empty."""
        with self.assertRaises(ValueError):
            sct.compile_chapter5_triad(
                stage_id="01_findings_recap",
                base_name="01_findings_recap",
                output_dir=self.temp_dir,
                stage_title="مرور اجمالی یافته‌ها",
                agent_narrative=None,
                narrative_file=None
            )

    def test_03_scaffold_triad_successful_compilation(self):
        """Triad compiler generates valid .docx, .md, and .json from agent-authored text."""
        agent_narrative = (
            "یافته‌های پژوهش حاضر نشان داد که الگوی ساختاری روابط بین متغیرهای پژوهش از برازش مطلوبی با داده‌های تجربی برخوردار است. "
            "بر اساس شاخص‌های برازش استاندارد، مسیرهای مستقیم و غیرمستقیم فرضیه اول با ضریب مسیر ۰.۴۵ در سطح معناداری ۰.۰۰۱ > p مورد تأیید قرار گرفتند. "
            "این یافته با مبانی نظری مدل پردازش هیجانی و نتایج تجربی پیشین همخوانی کامل دارد."
        )
        stage_dir = os.path.join(self.temp_dir, "stage_01")
        manifest = sct.compile_chapter5_triad(
            stage_id="01_findings_recap",
            base_name="01_findings_recap",
            output_dir=stage_dir,
            stage_title="مرور اجمالی هدف و یافته‌های پژوهش",
            agent_narrative=agent_narrative
        )

        self.assertEqual(manifest["stage_id"], "01_findings_recap")
        self.assertEqual(manifest["status"], "STAGE_DRAFTED")

        docx_path = os.path.join(stage_dir, "01_findings_recap.docx")
        md_path = os.path.join(stage_dir, "01_findings_recap.md")
        json_path = os.path.join(stage_dir, "01_findings_recap.json")

        self.assertTrue(os.path.isfile(docx_path), "Missing .docx deliverable")
        self.assertTrue(os.path.isfile(md_path), "Missing .md deliverable")
        self.assertTrue(os.path.isfile(json_path), "Missing .json deliverable")

        with open(json_path, "r", encoding="utf-8") as f:
            jdata = json.load(f)
        self.assertIn("sha256", jdata["deliverables"])
        self.assertTrue(jdata["metrics"]["word_count"] > 20)

    # --------------------------------------------------------------------------
    # 3. Chapter 5 Micro-Stage Assembly Tests
    # --------------------------------------------------------------------------
    def test_04_assemble_chapter5_stages(self):
        """Assembles verified micro-stages into unified Chapter_5_Discussion (.docx, .md, manifest)."""
        stages_dir = os.path.join(self.temp_dir, "stages")
        os.makedirs(stages_dir, exist_ok=True)

        stages_to_create = [
            ("01_findings_recap", "مرور اجمالی یافته‌ها", "پژوهش حاضر با هدف بررسی مدل ساختاری روابط انجام شد."),
            ("02_hypothesis_discussion", "تبیین فرضیه‌های پژوهش", "فرضیه اول حاکی از رابطه مستقیم معنادار بود."),
            ("04_implications", "کاربردهای کاربردی و بالینی", "یافته‌های حاضر دلالت‌های کاربردی مهمی برای روان‌درمانگران دارد.")
        ]

        for s_id, title, text in stages_to_create:
            sct.compile_chapter5_triad(
                stage_id=s_id,
                base_name=s_id,
                output_dir=stages_dir,
                stage_title=title,
                agent_narrative=text
            )

        out_dir = os.path.join(self.temp_dir, "assembly_out")
        assembly_res = ac5.assemble_chapter5(stages_dir, out_dir)

        self.assertEqual(assembly_res["chapter"], 5)
        self.assertEqual(assembly_res["total_stages_merged"], 3)
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "Chapter_5_Discussion.docx")))
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "Chapter_5_Discussion.md")))
        self.assertTrue(os.path.isfile(os.path.join(out_dir, "chapter5_assembly_manifest.json")))

    # --------------------------------------------------------------------------
    # 4. State Machine Governance Tests
    # --------------------------------------------------------------------------
    def test_05_state_manager_chapter5_init(self):
        """Initializes academic-state with chapter5 pipeline and registers all 10 stages."""
        res = sm.init_state(self.temp_dir, title="Chapter 5 Study", methodology="sem", n=320, pipeline="chapter5")
        self.assertEqual(res["status"], "SUCCESS")

        with open(os.path.join(self.state_dir, "project.json"), "r", encoding="utf-8") as f:
            proj = json.load(f)

        self.assertEqual(proj["current_stage"], "01_findings_recap")
        self.assertEqual(proj["active_milestone"], "M8_DISCUSSION")
        self.assertEqual(proj["metadata"]["pipeline"], "chapter5")

        with open(os.path.join(self.state_dir, "requirements.json"), "r", encoding="utf-8") as f:
            req = json.load(f)
        self.assertIn("Chapter_5_Discussion.docx", req["deliverables"])
        self.assertIn("Chapter_5_Discussion.md", req["deliverables"])

        # Check strict state machine
        sm_inst = StrictStateMachine(state_dir=self.state_dir)
        self.assertEqual(len(sm_inst.stages), len(CHAPTER_5_STAGE_GRAPH))
        self.assertIn("01_findings_recap", sm_inst.stages)
        self.assertIn("10_defense_brief", sm_inst.stages)
        self.assertEqual(sm_inst.stages["01_findings_recap"]["status"], StageState.STAGE_READY.value)
        self.assertEqual(sm_inst.stages["02_hypothesis_discussion"]["status"], StageState.STAGE_LOCKED.value)

    def test_06_state_machine_chapter5_advancement(self):
        """Tests sequential advancement along Chapter 5 stage graph."""
        sm.init_state(self.temp_dir, title="Chapter 5 Advancement", methodology="sem", n=300, pipeline="chapter5")
        sm_inst = StrictStateMachine(state_dir=self.state_dir)

        # Mock required input artifact for 01_findings_recap (analysis/sem.json)
        os.makedirs(os.path.join(self.state_dir, "analysis"), exist_ok=True)
        with open(os.path.join(self.state_dir, "analysis", "sem.json"), "w", encoding="utf-8") as f:
            json.dump({"mock": "sem_results", "fit": {"cfi": 0.96}}, f)

        # Transition 01_findings_recap: READY -> RUNNING
        sm_inst.request_transition("01_findings_recap", StageState.STAGE_RUNNING)

        # Mock required output artifact before transition to STAGE_VALIDATING and STAGE_APPROVED
        with open(os.path.join(self.state_dir, "01_findings_recap.json"), "w", encoding="utf-8") as f:
            json.dump({"status": "STAGE_COMPLETED"}, f)

        # Transition RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED
        sm_inst.request_transition("01_findings_recap", StageState.STAGE_VALIDATING, mode="test")
        sm_inst.request_transition("01_findings_recap", StageState.STAGE_AWAITING_APPROVAL, mode="test")

        # Grant human approval (Directive 11 / Saber Admin Desk)
        appr = sm_inst.request_approval(
            milestone_id="01_findings_recap",
            category="reporting",
            requester_agent="academic-writer",
            rationale="Recap findings verified"
        )
        sm_inst.grant_approval(
            approval_id=appr["approval_id"],
            approver_identity="Saber Admin Desk 124911145",
            digital_signature="SIG-VERIFIED-124911145",
            comments="Approved"
        )

        # Create passing validation report (Directive 19 / Phase 13)
        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "checks_failed": 0, "stage_id": "01_findings_recap"}, f)

        sm_inst.request_transition("01_findings_recap", StageState.STAGE_APPROVED, mode="test")

        self.assertEqual(sm_inst.stages["01_findings_recap"]["status"], StageState.STAGE_APPROVED.value)

        # Now advance to next stage
        res = sm_inst.request_transition("01_findings_recap", StageState.NEXT_STAGE, mode="test")
        self.assertEqual(res["status"], "TRANSITIONED")
        self.assertEqual(res["next_stage_id"], "02_hypothesis_discussion")
        self.assertEqual(sm_inst.stages["02_hypothesis_discussion"]["status"], StageState.STAGE_READY.value)

    # --------------------------------------------------------------------------
    # 5. Orchestrator Dependency Resolver Tests
    # --------------------------------------------------------------------------
    def test_07_dependency_resolver_chapter5(self):
        """Verifies capability resolution and stage dependency validation for Chapter 5."""
        res = odr.resolve_capability("Write Chapter 5 discussion and conclusion")
        self.assertEqual(res["capability"], "chapter_5_writing")
        self.assertEqual(res["agent"], "academic-writer")
        self.assertEqual(res["skill"], "chapter-5-writing")

        # Verify STAGE_DEPENDENCIES contains all Chapter 5 stages
        for stage_info in CHAPTER_5_STAGE_GRAPH:
            stage_id = stage_info["stage_id"]
            self.assertIn(stage_id, odr.STAGE_DEPENDENCIES)
            self.assertIn(stage_id, odr.STAGE_ORDER)

        # Check prerequisite failure when required stage is unmet
        sm.init_state(self.temp_dir, pipeline="chapter5")
        check_res = odr.check_prerequisites("02_hypothesis_discussion", self.state_dir)
        self.assertEqual(check_res["status"], "BLOCKED")
        self.assertTrue(len(check_res["unmet_stages"]) > 0)

    # --------------------------------------------------------------------------
    # 6. Orchestrator CLI Presets & Registry Tests
    # --------------------------------------------------------------------------
    def test_08_orchestrator_cli_chapter5_presets(self):
        """Verifies Chapter 5 skills and preset registered in orchestrator_cli."""
        self.assertIn("article_enrichment", ocli.SKILL_REGISTRY)
        self.assertIn("chapter5_triad", ocli.SKILL_REGISTRY)
        self.assertIn("chapter5_assembly", ocli.SKILL_REGISTRY)

        self.assertIn("chapter5_micro", ocli.PIPELINE_PRESETS)
        preset_steps = ocli.PIPELINE_PRESETS["chapter5_micro"]
        self.assertIn("article_enrichment", preset_steps)
        self.assertIn("discussion", preset_steps)
        self.assertIn("chapter5_assembly", preset_steps)


if __name__ == "__main__":
    unittest.main()
