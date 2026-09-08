#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcademicSuite Master Research Lifecycle CLI Pipeline & Orchestration Engine
(موتور جامع فرماندهی و اجرای خودکار پایپ‌لاین‌های پژوهشی AcademicSuite)

Coordinates and chains the 18 specialized skills of AcademicSuite into
reproducible, automated, and resilient end-to-end research pipelines.
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
REPO_ROOT = os.path.abspath(os.path.join(SKILLS_DIR, "../.."))
PYTHON_BIN = sys.executable or "/opt/miniconda3/bin/python3"


# ==============================================================================
# Skill Registry & Script Directory Map
# ==============================================================================

SKILL_REGISTRY = {
    "proposal": {
        "skill": "persian-proposal-builder",
        "script": os.path.join(SKILLS_DIR, "persian-proposal-builder", "scripts", "generate_proposal_docx.py"),
        "default_sample": os.path.join(SKILLS_DIR, "persian-proposal-builder", "examples", "sample_proposal.json"),
        "desc": "Research proposal & methodology (.docx)"
    },
    "literature_review": {
        "skill": "persian-literature-review-builder",
        "script": os.path.join(SKILLS_DIR, "persian-literature-review-builder", "scripts", "literature_review_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "persian-literature-review-builder", "examples", "sample_ch2_payload.json"),
        "desc": "Chapter 2 theoretical foundations & empirical literature (.docx & .xlsx)"
    },
    "simulation": {
        "skill": "psychometric-data-simulator",
        "script": os.path.join(SKILLS_DIR, "psychometric-data-simulator", "scripts", "simdat_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "psychometric-data-simulator", "examples", "sample_regression_payload.json"),
        "desc": "Monte Carlo synthetic survey & trial dataset generation (.xlsx & .csv)"
    },
    "statistics": {
        "skill": "statistical-data-analyst",
        "script_calc": os.path.join(SKILLS_DIR, "statistical-data-analyst", "scripts", "psychology_stats.py"),
        "script_doc": os.path.join(SKILLS_DIR, "statistical-data-analyst", "scripts", "generate_apa_docx.py"),
        "default_sample": os.path.join(SKILLS_DIR, "statistical-data-analyst", "examples", "sample_stats_results.json"),
        "desc": "SPSS hypothesis testing & Chapter 4 APA 7 reporting (.docx & .json)"
    },
    "scale_resolver": {
        "skill": "psychometric-scale-resolver",
        "script": os.path.join(SKILLS_DIR, "psychometric-scale-resolver", "scripts", "questionnaire_resolver.py"),
        "desc": "Questionnaire registry lookup, factor keys, and subscales"
    },
    "scale_validator": {
        "skill": "psychometric-scale-validator",
        "script": os.path.join(SKILLS_DIR, "psychometric-scale-validator", "scripts", "psychometric_validator_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "psychometric-scale-validator", "examples", "sample_validation_payload.json"),
        "desc": "Scale standardization, CTT (Lawshe CVR, EFA/CFA, Omega) & IRT (GRM, TIF, DIF) (.docx, .xlsx, .png)"
    },
    "qualitative": {
        "skill": "qualitative-data-analyst",
        "script": os.path.join(SKILLS_DIR, "qualitative-data-analyst", "scripts", "qualitative_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "qualitative-data-analyst", "examples", "sample_thematic_payload.json"),
        "desc": "Thematic analysis & Grounded Theory Paradigmatic Model (.docx, .xlsx, .png)"
    },
    "discussion": {
        "skill": "persian-discussion-builder",
        "script": os.path.join(SKILLS_DIR, "persian-discussion-builder", "scripts", "generate_chapter5_docx.py"),
        "default_sample": os.path.join(SKILLS_DIR, "persian-discussion-builder", "examples", "sample_ch5_payload.json"),
        "desc": "Chapter 5 theoretical mechanisms, limitations & recommendations (.docx)"
    },
    "thesis": {
        "skill": "persian-thesis-builder",
        "script": os.path.join(SKILLS_DIR, "persian-thesis-builder", "scripts", "compile_full_thesis.py"),
        "desc": "Master full thesis compilation (.docx with institutional template)"
    },
    "defense": {
        "skill": "persian-defense-presentation-builder",
        "script": os.path.join(SKILLS_DIR, "persian-defense-presentation-builder", "scripts", "compile_defense_presentation.py"),
        "default_sample": os.path.join(SKILLS_DIR, "persian-defense-presentation-builder", "examples", "sample_defense_payload.json"),
        "desc": "Defense slide deck with RTL OpenXML & candidate oral notes (.pptx)"
    },
    "plagiarism": {
        "skill": "irandoc-plagiarism-reducer",
        "script": os.path.join(SKILLS_DIR, "irandoc-plagiarism-reducer", "scripts", "paraphrase_engine.py"),
        "desc": "Irandoc similarity reduction & academic paraphrasing (< 20%)"
    },
    "article": {
        "skill": "academic-article-writer",
        "script": os.path.join(SKILLS_DIR, "academic-article-writer", "scripts", "compile_academic_article.py"),
        "default_sample": os.path.join(SKILLS_DIR, "academic-article-writer", "examples", "sample_article_fa.json"),
        "desc": "Academic journal article manuscript (ISI/Scopus or ISC) (.docx)"
    },
    "submission": {
        "skill": "journal-submission-assistant",
        "script": os.path.join(SKILLS_DIR, "journal-submission-assistant", "scripts", "compile_submission_package.py"),
        "default_sample": os.path.join(SKILLS_DIR, "journal-submission-assistant", "examples", "sample_submission_payload_fa.json"),
        "desc": "Submission collateral: Cover Letter, Title Page (CRediT), Highlights, Rebuttal (.docx)"
    },
    "meta_analysis": {
        "skill": "systematic-review-meta-analyst",
        "script": os.path.join(SKILLS_DIR, "systematic-review-meta-analyst", "scripts", "meta_analysis_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "systematic-review-meta-analyst", "examples", "sample_meta_payload_fa.json"),
        "desc": "PRISMA 2020 & Cochrane RoB 2 meta-analysis with Forest/Funnel plots (.docx, .png, .json)"
    },
    "protocol": {
        "skill": "psychological-intervention-protocol-builder",
        "script": os.path.join(SKILLS_DIR, "psychological-intervention-protocol-builder", "scripts", "compile_intervention_protocol.py"),
        "default_sample": os.path.join(SKILLS_DIR, "psychological-intervention-protocol-builder", "examples", "sample_protocol_payload.json"),
        "desc": "Intervention protocol clinical manuals & Ch 3 summary tables (.docx & .json)"
    },
    "revision": {
        "skill": "persian-thesis-revision-assistant",
        "script": os.path.join(SKILLS_DIR, "persian-thesis-revision-assistant", "scripts", "generate_revision_response_docx.py"),
        "default_sample": os.path.join(SKILLS_DIR, "persian-thesis-revision-assistant", "examples", "sample_feedback_payload.json"),
        "desc": "Triage of supervisor/examiner comments & Point-by-Point response table (.docx)"
    },
    "reference": {
        "skill": "academic-reference-extractor",
        "script": os.path.join(SKILLS_DIR, "academic-reference-extractor", "scripts", "extract_section_references.py"),
        "desc": "In-text citation matching & export to EndNote (.enw), RIS (.ris), and APA (.txt)"
    },
    "audit": {
        "skill": "thesis-integrity-auditor",
        "script": os.path.join(SKILLS_DIR, "thesis-integrity-auditor", "scripts", "audit_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "thesis-integrity-auditor", "examples", "sample_audit_payload.json"),
        "desc": "Cross-chapter thesis integrity audit, hypothesis alignment, degrees of freedom & citation reconciliation"
    },
    "sample_size": {
        "skill": "gpower-sample-size-calculator",
        "script": os.path.join(SKILLS_DIR, "gpower-sample-size-calculator", "scripts", "gpower_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "gpower-sample-size-calculator", "examples", "sample_gpower_payload.json"),
        "desc": "G*Power academic sample size determination, statistical power curves & Chapter 3 justifications"
    },
    "tone_polish": {
        "skill": "ai-academic-tone-polisher",
        "script": os.path.join(SKILLS_DIR, "ai-academic-tone-polisher", "scripts", "tone_polisher_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "ai-academic-tone-polisher", "examples", "sample_ai_text_payload.json"),
        "desc": "Academic tone polisher, syntactic burstiness optimizer & anti-AI refiner (.docx, .xlsx, .png)"
    },
    "harvest": {
        "skill": "literature-harvester",
        "script": os.path.join(SKILLS_DIR, "literature-harvester", "scripts", "harvester_engine.py"),
        "default_sample": os.path.join(SKILLS_DIR, "literature-harvester", "examples", "sample_harvest_query.json"),
        "desc": "Multi-database literature search & Chapter 2 empirical background extractor (.docx, .xlsx, .ris)"
    }
}


# ==============================================================================
# Standard Predefined Pipelines
# ==============================================================================

PIPELINE_PRESETS = {
    "thesis_empirical": [
        "proposal",
        "simulation",
        "statistics",
        "discussion",
        "thesis",
        "defense"
    ],
    "scale_validation": [
        "scale_validator",
        "article",
        "submission"
    ],
    "qualitative_study": [
        "proposal",
        "qualitative",
        "discussion",
        "thesis",
        "defense"
    ],
    "meta_analysis": [
        "meta_analysis",
        "article",
        "submission"
    ],
    "thesis_to_publication": [
        "plagiarism",
        "article",
        "submission"
    ]
}


# ==============================================================================
# Master Pipeline Orchestrator Class
# ==============================================================================

class MasterAcademicOrchestrator:
    """Controls the execution, data routing, artifact logging, and dashboard compilation."""

    def __init__(self, config_path: str, out_dir: str, pipeline_name: Optional[str] = None,
                 custom_steps: Optional[List[str]] = None, dry_run: bool = False,
                 resume_from: Optional[str] = None, single_step: Optional[str] = None,
                 lang: str = "fa"):
        self.config_path = os.path.abspath(config_path) if config_path else None
        self.out_dir = os.path.abspath(out_dir)
        self.pipeline_name = pipeline_name or "thesis_empirical"
        self.custom_steps = custom_steps
        self.dry_run = dry_run
        self.resume_from = resume_from
        self.single_step = single_step
        self.lang = lang

        self.config: Dict[str, Any] = {}
        self.manifest: Dict[str, Any] = {
            "orchestrator_version": "1.0.0",
            "start_time": datetime.now().isoformat(),
            "pipeline": self.pipeline_name,
            "status": "INITIALIZING",
            "out_dir": self.out_dir,
            "steps_executed": [],
            "artifacts": {}
        }
        self.context: Dict[str, Any] = {}

    def load_configuration(self):
        """Loads and validates the project configuration JSON."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            print(f"[CONFIG] Loaded project configuration: {self.config_path}")
        else:
            print("[CONFIG] No config file supplied. Initializing with default project metadata.")
            self.config = {
                "project_name": "Academic_Thesis_Project",
                "project_title": "پژوهش علمی و دانشگاهی",
                "project_title_en": "Academic Research Project",
                "author": "دانشجو / پژوهشگر",
                "supervisor": "استاد راهنما",
                "pipeline": self.pipeline_name,
                "target_language": self.lang,
                "steps_configuration": {}
            }

        os.makedirs(self.out_dir, exist_ok=True)

    def resolve_pipeline_steps(self) -> List[str]:
        """Resolves the ordered sequence of steps to execute."""
        if self.custom_steps:
            steps = self.custom_steps
        elif self.single_step:
            steps = [self.single_step]
        else:
            preset = self.config.get("pipeline", self.pipeline_name)
            steps = PIPELINE_PRESETS.get(preset, PIPELINE_PRESETS["thesis_empirical"])

        # Filter if resume_from is specified
        if self.resume_from:
            if self.resume_from in steps:
                start_idx = steps.index(self.resume_from)
                steps = steps[start_idx:]
                print(f"[RESUME] Resuming pipeline from step '{self.resume_from}' ({len(steps)} steps remaining)")
            else:
                print(f"[WARNING] Step '{self.resume_from}' not found in pipeline steps. Running full pipeline.")

        return steps

    def print_pipeline_dag(self, steps: List[str]):
        """Visualizes the pipeline DAG and execution schedule."""
        print("\n" + "=" * 76)
        print(" ACADEMIC SUITE MASTER ORCHESTRATOR - PIPELINE EXECUTION PLAN")
        print("=" * 76)
        print(f" Project: {self.config.get('project_title', '')}")
        print(f" Author: {self.config.get('author', '')} | Supervisor: {self.config.get('supervisor', '')}")
        print(f" Pipeline Mode: {self.pipeline_name.upper()} ({len(steps)} steps)")
        print(f" Output Directory: {self.out_dir}")
        print(f" Dry-Run Mode: {'ENABLED (Simulation Only)' if self.dry_run else 'DISABLED (Live Execution)'}")
        print("-" * 76)
        print(" STEPS TO EXECUTE:")
        for idx, s in enumerate(steps, start=1):
            info = SKILL_REGISTRY.get(s, {})
            skill_name = info.get("skill", "unknown")
            desc = info.get("desc", "")
            print(f"  {idx}. [{s.upper()}] ──► {skill_name}")
            print(f"     Description: {desc}")
        print("=" * 76 + "\n")

    def execute(self):
        """Main execution engine."""
        self.load_configuration()
        steps = self.resolve_pipeline_steps()
        self.print_pipeline_dag(steps)

        start_total = time.time()
        success_count = 0

        for idx, step_name in enumerate(steps, start=1):
            print(f"\n>>> [{idx}/{len(steps)}] EXECUTING STEP: {step_name.upper()} <<<")
            step_start = time.time()

            try:
                cmd, expected_outputs = self._build_step_command(step_name)
                print(f"    Command: {' '.join(cmd)}")

                if not self.dry_run:
                    step_dir = os.path.join(self.out_dir, f"{idx:02d}_{step_name}")
                    os.makedirs(step_dir, exist_ok=True)
                    
                    # Execute sub-process
                    proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    print(f"    [SUCCESS] Step '{step_name}' completed with exit code {proc.returncode}")
                else:
                    print(f"    [DRY-RUN] Simulated execution for '{step_name}' successfully planned.")

                duration = round(time.time() - step_start, 2)
                self.manifest["steps_executed"].append({
                    "step": step_name,
                    "skill": SKILL_REGISTRY.get(step_name, {}).get("skill", ""),
                    "status": "COMPLETED",
                    "duration_seconds": duration,
                    "expected_artifacts": expected_outputs
                })
                success_count += 1

            except subprocess.CalledProcessError as cpe:
                print(f"    [ERROR] Step '{step_name}' failed with code {cpe.returncode}!", file=sys.stderr)
                print(f"    [STDERR]: {cpe.stderr[:500]}", file=sys.stderr)
                self.manifest["steps_executed"].append({
                    "step": step_name,
                    "skill": SKILL_REGISTRY.get(step_name, {}).get("skill", ""),
                    "status": "FAILED",
                    "error": cpe.stderr[:500]
                })
                self.manifest["status"] = "FAILED"
                break
            except Exception as e:
                print(f"    [ERROR] Step '{step_name}' execution error: {str(e)}", file=sys.stderr)
                self.manifest["steps_executed"].append({
                    "step": step_name,
                    "skill": SKILL_REGISTRY.get(step_name, {}).get("skill", ""),
                    "status": "FAILED",
                    "error": str(e)
                })
                self.manifest["status"] = "FAILED"
                break

        total_duration = round(time.time() - start_total, 2)
        if self.manifest["status"] != "FAILED":
            self.manifest["status"] = "COMPLETED"

        self.manifest["end_time"] = datetime.now().isoformat()
        self.manifest["total_duration_seconds"] = total_duration

        # Generate Manifest and Executive Dashboard
        if not self.dry_run:
            self._write_manifest()
            self._write_dashboard()

        print("\n" + "=" * 76)
        print(f" ORCHESTRATOR RUN {self.manifest['status']}")
        print(f" Completed {success_count}/{len(steps)} steps in {total_duration}s")
        print(f" Artifacts & Manifest saved in: {self.out_dir}")
        print("=" * 76 + "\n")

    def _build_step_command(self, step: str) -> (List[str], Dict[str, str]):
        """Constructs the exact Python command and expected outputs for each step."""
        step_dir = os.path.join(self.out_dir, step)
        os.makedirs(step_dir, exist_ok=True)
        info = SKILL_REGISTRY.get(step, {})
        step_conf = self.config.get("steps_configuration", {}).get(step, {})

        if step == "proposal":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            out_docx = os.path.join(step_dir, "پروپوزال_پژوهش.docx")
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out", out_docx]
            self.context["proposal_docx"] = out_docx
            self.manifest["artifacts"]["proposal_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "literature_review":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx")
            self.context["ch2_docx"] = out_docx
            self.manifest["artifacts"]["ch2_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "simulation":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir]
            sim_xlsx = os.path.join(step_dir, "simulated_regression_dataset.xlsx")
            self.context["simulated_data"] = sim_xlsx
            self.manifest["artifacts"]["simulated_dataset"] = sim_xlsx
            return cmd, {"xlsx": sim_xlsx}

        elif step == "statistics":
            # Uses generate_apa_docx with standard verified sample or results
            script = info["script_doc"]
            json_payload = info["default_sample"]
            out_docx = os.path.join(step_dir, "فصل_چهارم_یافته‌های_پژوهش.docx")
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out", out_docx, "--mode", "chapter4"]
            self.context["ch4_docx"] = out_docx
            self.context["stats_json"] = json_payload
            self.manifest["artifacts"]["ch4_docx"] = out_docx
            self.manifest["artifacts"]["stats_json"] = json_payload
            return cmd, {"docx": out_docx, "json": json_payload}

        elif step == "scale_validator":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "فصل_چهارم_ویژگی‌های_روان‌سنجی_و_هنجاریابی.docx")
            out_xlsx = os.path.join(step_dir, "psychometric_validation_matrix.xlsx")
            self.context["ch4_docx"] = out_docx
            self.context["validation_xlsx"] = out_xlsx
            self.manifest["artifacts"]["validation_docx"] = out_docx
            self.manifest["artifacts"]["validation_matrix"] = out_xlsx
            return cmd, {"docx": out_docx, "xlsx": out_xlsx}

        elif step == "qualitative":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "فصل_چهارم_یافته‌های_کیفی.docx")
            self.context["ch4_docx"] = out_docx
            self.manifest["artifacts"]["ch4_qual_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "discussion":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            out_docx = os.path.join(step_dir, "فصل_پنجم_بحث_و_نتیجه‌گیری.docx")
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out", out_docx]
            self.context["ch5_docx"] = out_docx
            self.manifest["artifacts"]["ch5_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "thesis":
            script = info["script"]
            out_docx = os.path.join(step_dir, "رساله_کامل_دانشگاهی.docx")
            ch4_file = self.context.get("ch4_docx")
            ch5_file = self.context.get("ch5_docx")
            cmd = [PYTHON_BIN, script, "--output", out_docx]
            if ch4_file and os.path.exists(ch4_file):
                cmd.extend(["--ch4", ch4_file])
            if ch5_file and os.path.exists(ch5_file):
                cmd.extend(["--ch5", ch5_file])
            self.context["full_thesis_docx"] = out_docx
            self.manifest["artifacts"]["full_thesis_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "defense":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            out_pptx = os.path.join(step_dir, "اسلایدهای_جلسه_دفاع.pptx")
            cmd = [
                PYTHON_BIN, script,
                "--json", json_payload,
                "--output", out_pptx,
                "--title", self.config.get("project_title", "پژوهش رساله"),
                "--author", self.config.get("author", "دانشجو"),
                "--supervisor", self.config.get("supervisor", "استاد راهنما")
            ]
            self.context["defense_pptx"] = out_pptx
            self.manifest["artifacts"]["defense_presentation_pptx"] = out_pptx
            return cmd, {"pptx": out_pptx}

        elif step == "plagiarism":
            script = info["script"]
            input_file = self.context.get("full_thesis_docx") or os.path.join(REPO_ROOT, "AGENTS.md")
            out_docx = os.path.join(step_dir, "متن_بازنویسی_کاهش_همانندجویی.docx")
            out_rep = os.path.join(step_dir, "گزارش_کاهش_همانندجویی.docx")
            cmd = [PYTHON_BIN, script, "--input", input_file, "--output-docx", out_docx, "--output-report", out_rep]
            self.manifest["artifacts"]["rewritten_docx"] = out_docx
            return cmd, {"docx": out_docx, "report": out_rep}

        elif step == "article":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            out_docx = os.path.join(step_dir, "مقاله_علمی_پژوهشی.docx")
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out", out_docx, "--lang", self.lang]
            self.context["article_docx"] = out_docx
            self.manifest["artifacts"]["article_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "submission":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            self.manifest["artifacts"]["submission_dir"] = step_dir
            return cmd, {"dir": step_dir}

        elif step == "meta_analysis":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "گزارش_جامع_مرور_سیستماتیک_و_فراتحلیل.docx")
            self.manifest["artifacts"]["meta_docx"] = out_docx
            return cmd, {"docx": out_docx}

        elif step == "audit":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx" if self.lang == "fa" else "Thesis_Integrity_Audit_Report.docx")
            self.manifest["artifacts"]["audit_docx"] = out_docx
            self.manifest["artifacts"]["audit_json"] = os.path.join(step_dir, "thesis_audit_summary.json")
            self.manifest["artifacts"]["audit_excel"] = os.path.join(step_dir, "annotated_citations.xlsx")
            return cmd, {"docx": out_docx, "dir": step_dir}

        elif step == "sample_size":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "گزارش_محاسبه_حجم_نمونه_جی‌پاور.docx" if self.lang == "fa" else "GPower_Sample_Size_Report.docx")
            plot_path = os.path.join(step_dir, "power_curve_plot.png")
            self.manifest["artifacts"]["gpower_docx"] = out_docx
            self.manifest["artifacts"]["gpower_plot"] = plot_path
            self.manifest["artifacts"]["gpower_excel"] = os.path.join(step_dir, "sample_size_calculator_matrix.xlsx")
            self.manifest["artifacts"]["gpower_json"] = os.path.join(step_dir, "gpower_results.json")
            return cmd, {"docx": out_docx, "plot": plot_path, "dir": step_dir}

        elif step == "tone_polish":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            sample_name = "persian_draft" if self.lang == "fa" else "english_draft"
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--sample", sample_name, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "متن_ویراسته_و_دانشگاهی.docx" if self.lang == "fa" else "Polished_Academic_Manuscript.docx")
            plot_path = os.path.join(step_dir, "tone_burstiness_plot.png")
            self.manifest["artifacts"]["tone_polish_docx"] = out_docx
            self.manifest["artifacts"]["tone_polish_plot"] = plot_path
            self.manifest["artifacts"]["tone_polish_excel"] = os.path.join(step_dir, "academic_tone_audit_matrix.xlsx")
            self.manifest["artifacts"]["tone_polish_json"] = os.path.join(step_dir, "tone_polish_results.json")
            return cmd, {"docx": out_docx, "plot": plot_path, "dir": step_dir}

        elif step == "harvest":
            script = info["script"]
            json_payload = step_conf.get("payload_path") or info["default_sample"]
            if not os.path.isabs(json_payload):
                json_payload = os.path.join(REPO_ROOT, json_payload)
            sample_name = "act_psychological_flexibility_fa" if self.lang == "fa" else "cognitive_reappraisal_mindfulness_en"
            cmd = [PYTHON_BIN, script, "--json", json_payload, "--sample", sample_name, "--out-dir", step_dir, "--lang", self.lang]
            out_docx = os.path.join(step_dir, "گزارش_جامع_پیشینه_پژوهش_استخراج‌شده.docx" if self.lang == "fa" else "Harvested_Literature_Review.docx")
            self.manifest["artifacts"]["harvest_docx"] = out_docx
            self.manifest["artifacts"]["harvest_excel"] = os.path.join(step_dir, "harvested_empirical_studies.xlsx")
            self.manifest["artifacts"]["harvest_ris"] = os.path.join(step_dir, "harvested_citations.ris")
            self.manifest["artifacts"]["harvest_json"] = os.path.join(step_dir, "harvested_studies.json")
            return cmd, {"docx": out_docx, "dir": step_dir}

        else:
            raise ValueError(f"Unknown step '{step}'. Valid steps are: {list(SKILL_REGISTRY.keys())}")

    def _write_manifest(self):
        """Saves execution manifest audit log."""
        manifest_path = os.path.join(self.out_dir, "orchestrator_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)
        print(f"[AUDIT] Saved orchestrator manifest: {manifest_path}")

    def _write_dashboard(self):
        """Generates the executive summary dashboard markdown file."""
        dashboard_path = os.path.join(self.out_dir, "PROJECT_DASHBOARD.md")
        lines = [
            f"# Executive Project Dashboard: {self.config.get('project_title', 'Academic Project')}",
            f"**Pipeline**: `{self.pipeline_name}` | **Status**: `{self.manifest['status']}` | **Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 1. Project Metadata",
            f"- **Author / Candidate**: {self.config.get('author', 'N/A')}",
            f"- **Supervisor**: {self.config.get('supervisor', 'N/A')}",
            f"- **University & Faculty**: {self.config.get('university', 'N/A')} - {self.config.get('faculty', 'N/A')}",
            f"- **Field & Degree**: {self.config.get('field', 'N/A')} ({self.config.get('degree', 'N/A')})",
            f"- **Total Duration**: {self.manifest.get('total_duration_seconds', 0)} seconds",
            "",
            "---",
            "",
            "## 2. Pipeline Execution Stages",
            "| Step | Skill Engine | Status | Duration | Deliverable Artifacts |",
            "| :--- | :--- | :---: | :---: | :--- |"
        ]

        for s in self.manifest.get("steps_executed", []):
            step_name = s.get("step", "")
            skill = s.get("skill", "")
            status = "✅ " + s.get("status", "") if s.get("status") == "COMPLETED" else "❌ " + s.get("status", "")
            dur = f"{s.get('duration_seconds', 0)}s"
            artifacts = s.get("expected_artifacts", {})
            links = []
            for k, p in artifacts.items():
                links.append(f"[{os.path.basename(p)}](file://{p})")
            art_str = ", ".join(links) if links else "-"
            lines.append(f"| **{step_name}** | `{skill}` | {status} | {dur} | {art_str} |")

        lines.extend([
            "",
            "---",
            "",
            "## 3. Master Deliverables Directory",
            f"All compiled artifacts are located in: [{self.out_dir}](file://{self.out_dir})"
        ])

        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"[DASHBOARD] Compiled executive project dashboard: {dashboard_path}")


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Master Research Lifecycle CLI Pipeline & Orchestration Engine")
    parser.add_argument("--pipeline", default="thesis_empirical", choices=list(PIPELINE_PRESETS.keys()),
                        help="Predefined pipeline preset to execute (default: thesis_empirical)")
    parser.add_argument("--config", help="Path to project configuration JSON file")
    parser.add_argument("--out-dir", required=True, help="Directory to save pipeline outputs and manifest")
    parser.add_argument("--steps", help="Comma-separated custom step sequence (overrides preset)")
    parser.add_argument("--resume-from", help="Resume pipeline from a specific step (skips earlier steps)")
    parser.add_argument("--step", help="Execute only a single isolated step")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pipeline DAG and validate inputs without running heavy tasks")
    parser.add_argument("--lang", default="fa", choices=["fa", "en"], help="Target language (default: fa)")

    args = parser.parse_args()

    custom_steps = [s.strip() for s in args.steps.split(",")] if args.steps else None

    orchestrator = MasterAcademicOrchestrator(
        config_path=args.config,
        out_dir=args.out_dir,
        pipeline_name=args.pipeline,
        custom_steps=custom_steps,
        dry_run=args.dry_run,
        resume_from=args.resume_from,
        single_step=args.step,
        lang=args.lang
    )
    orchestrator.execute()


if __name__ == "__main__":
    main()
