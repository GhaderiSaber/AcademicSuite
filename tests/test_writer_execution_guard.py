#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_writer_execution_guard.py — Unit Tests for Phase 10 Academic Writer Execution Boundary Guard

Verifies:
1. Tool Manifest: academic-writer retains READ, WRITE, EDIT, and RUN_COMMAND tools.
2. Contract Integrity: academic-writer contract preserves all 12 constitutional sections and invariant phrase.
3. PreToolUse Hook Enforcement:
   - Permitted: Declared document-generation scripts (chapter-4-writing, persian-thesis-builder, apa-reporting, etc.).
   - Permitted: Allowed shared document utilities (structured_docx_generator.py, persian_docx_engine.py, etc.).
   - Permitted: Document conversion tools (pandoc, soffice) and file management (mkdir, cp).
   - Denied: Statistical skill scripts (regression, mediation, SEM, CFA, assumption-testing, data-cleaning, etc.).
   - Denied: Inline Python statistical calculations (pingouin, scipy.stats, statsmodels, sklearn, semopy).
   - Denied: R scripts and commands (Rscript, R).
   - Non-Writer Agents: statistics-agent is not blocked from executing statistical scripts.
"""

import os
import sys
import yaml
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
VERIF_DIR = os.path.join(ROOT_DIR, ".agents", "verification")
for p in (ROOT_DIR, HOOKS_DIR, VERIF_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from safety_hooks import SafetyHooks
from transcript_and_rule_guard import handle_pre_tool_use


class TestAcademicWriterExecutionGuard(unittest.TestCase):
    """Verifies least-privilege tool access and execution boundary for academic-writer."""

    def setUp(self):
        self.agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-writer", "agent.md")
        self.contract_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-writer", "contract.md")

    def test_01_writer_retains_required_worker_tools(self):
        """academic-writer must retain READ, WRITE, EDIT, and RUN_COMMAND."""
        with open(self.agent_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, "YAML frontmatter missing in academic-writer agent.md")
        frontmatter = yaml.safe_load(parts[1])
        tools = frontmatter.get("tools", [])

        # READ tools
        for read_tool in ("view_file", "list_dir", "grep_search", "find_by_name"):
            self.assertIn(read_tool, tools, f"academic-writer missing read tool: {read_tool}")

        # WRITE tool
        self.assertIn("write_to_file", tools, "academic-writer missing write_to_file")

        # EDIT tool
        self.assertIn("replace_file_content", tools, "academic-writer missing replace_file_content")

        # RUN_COMMAND tool
        self.assertIn("run_command", tools, "academic-writer missing run_command")

        # Worker isolation: Must NOT possess delegation tools
        self.assertNotIn("invoke_subagent", tools, "academic-writer must not possess invoke_subagent")
        self.assertNotIn("manage_subagents", tools, "academic-writer must not possess manage_subagents")

    def test_02_contract_preserves_constitutional_sections_and_boundary_phrase(self):
        """academic-writer contract must contain all 12 sections and boundary phrase."""
        with open(self.contract_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_sections = [
            "MISSION",
            "RESPONSIBILITIES",
            "NON-RESPONSIBILITIES",
            "INPUTS",
            "OUTPUTS",
            "ALLOWED TOOLS",
            "REQUIRED SKILLS",
            "FORBIDDEN ACTIONS",
            "HANDOFF FORMAT",
            "VALIDATION REQUIREMENTS",
            "COMPLETION CRITERIA",
            "FAILURE CONDITIONS",
        ]
        for sec in required_sections:
            self.assertIn(sec, content, f"Missing section: {sec}")

        # Required responsibility boundary phrase from test_durable_agents_migration.py
        self.assertIn("Never invent missing statistics", content)

    def test_03_permitted_document_generation_scripts_allowed(self):
        """SafetyHooks must allow academic-writer to execute declared document-generation scripts."""
        allowed_commands = [
            "python3 .agents/skills/chapter-4-writing/scripts/scaffold_chapter4_triad.py --stage 'آزمون فرضیه اول' --base '06_hypothesis_1' --outdir projects/active/ch4",
            "python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py --config config.json",
            "python3 .agents/skills/apa-reporting/scripts/scaffold_apa_tables.py --input table_spec.json",
            "python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py --in draft.md",
            "python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py",
            "python3 scripts/structured_docx_generator.py --input template.json",
            "python3 scripts/persian_docx_engine.py --md input.md --docx output.docx",
            "python3 scripts/build_hypothesis_triad_docx.py",
            "pandoc document.md -o document.docx",
            "mkdir -p projects/study_act/06_hypothesis_1",
            "cp template.docx projects/study_act/stage.docx",
        ]

        for cmd in allowed_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"Permitted command was denied for academic-writer: '{cmd}'. Reason: {res.get('reason')}"
            )

    def test_04_statistical_skill_scripts_denied(self):
        """SafetyHooks must deny academic-writer when calling scripts from statistical skills."""
        prohibited_skill_commands = [
            "python3 .agents/skills/regression/scripts/run_regression.py --data data.xlsx",
            "python3 .agents/skills/mediation/scripts/run_mediation.py --data data.xlsx",
            "python3 .agents/skills/sem/scripts/run_sem.py --model model.lav",
            "python3 .agents/skills/cfa/scripts/run_cfa.py --data data.xlsx",
            "python3 .agents/skills/assumption-testing/scripts/verify_assumptions.py --data data.xlsx",
            "python3 .agents/skills/statistical-data-analyst/scripts/run_ancova.py --data data.xlsx",
            "python3 .agents/skills/data-cleaning/scripts/clean_and_score.py --raw raw.xlsx",
            "python3 .agents/skills/data-audit/scripts/audit_dataset.py --data data.xlsx",
            "python3 .agents/skills/descriptive-statistics/scripts/compute_descriptives.py",
            "python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py",
            "python3 .agents/skills/longitudinal-moderated-mediation/scripts/run_longitudinal_modmed.py",
        ]

        for cmd in prohibited_skill_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Statistical skill script was not denied for academic-writer: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_05_inline_statistical_python_denied(self):
        """SafetyHooks must deny academic-writer executing inline statistical code via python -c."""
        inline_stat_commands = [
            "python3 -c 'import pingouin as pg; print(pg.ttest([1,2,3], [4,5,6]))'",
            "python3 -c 'import scipy.stats as stats; print(stats.f_oneway([1,2], [3,4]))'",
            "python3 -c 'import statsmodels.api as sm; model = sm.OLS()'",
            "python3 -c 'from sklearn.linear_model import LinearRegression; lr = LinearRegression()'",
            "python3 -c 'import semopy; desc = semopy.Model()'",
        ]

        for cmd in inline_stat_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Inline statistical computation was not denied for academic-writer: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_06_rscript_execution_denied(self):
        """SafetyHooks must deny academic-writer executing R commands or scripts."""
        r_commands = [
            "Rscript run_analysis.R",
            "R --slave -e 'summary(lm(y ~ x))'",
            "Rscript scripts/lavaan_sem.R",
        ]

        for cmd in r_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"R command was not denied for academic-writer: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_07_statistics_agent_not_blocked_by_writer_guard(self):
        """Execution worker statistics-agent must NOT be blocked by academic-writer boundary."""
        stat_cmd = "python3 .agents/skills/regression/scripts/run_regression.py --data data.xlsx"
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": stat_cmd}
            },
            "agentName": "statistics-agent",
            "workspacePaths": [ROOT_DIR]
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(
            res.get("decision"), "allow",
            f"statistics-agent was unexpectedly blocked on statistical script: {res.get('reason')}"
        )

    def test_08_subprocess_and_execution_wrappers_denied(self):
        """SafetyHooks must deny academic-writer when using Python subprocess wrappers or arbitrary -c."""
        wrapper_commands = [
            'python3 -c "import subprocess; subprocess.run([\'python3\',\'.agents/skills/regression/scripts/run_regression.py\'])"',
            'python3 -c "import os; os.system(\'python3 .agents/skills/regression/scripts/run_regression.py\')"',
            'python3 -c "import urllib.request; print(\'leak\')"',
            'python3 -c "print(\'hello world\')"',
            'python -c "exec(\'import os; os.system(\\\'id\\\')\')"',
            'python3 -c "open(\'test.py\', \'w\').write(\'evil\')"',
        ]
        for cmd in wrapper_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Execution wrapper was NOT denied for academic-writer: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_09_shell_chaining_and_redirection_denied(self):
        """SafetyHooks must deny academic-writer when using shell chaining operators or pipes."""
        chaining_commands = [
            "cp template.docx out.docx && python3 .agents/skills/regression/scripts/run_regression.py",
            "pandoc document.md -o document.docx; rm -rf /tmp/test",
            "mkdir -p out | sh",
            "python3 scripts/academic_docgen.py render-docx --md in.md --docx out.docx && ls",
            "python3 scripts/academic_docgen.py render-docx `id`",
            "python3 scripts/academic_docgen.py render-docx $(whoami)",
        ]
        for cmd in chaining_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Chaining command was NOT denied for academic-writer: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_10_dedicated_docgen_cli_allowed(self):
        """SafetyHooks must allow academic-writer to execute dedicated academic_docgen.py subcommands."""
        valid_docgen_commands = [
            "python3 scripts/academic_docgen.py render-docx --md input.md --docx output.docx",
            "python3 scripts/academic_docgen.py render-markdown --in input.md --out output.md",
            "python3 scripts/academic_docgen.py scaffold-triad --stage 'فرضیه اول' --base '06_hyp_1' --outdir out",
            "python3 scripts/academic_docgen.py compile-thesis --config config.json",
            "python3 scripts/academic_docgen.py compile-presentation --input slides.json",
            "python3 scripts/academic_docgen.py scaffold-apa-tables --input spec.json",
            "python3 scripts/academic_docgen.py polish-tone --in draft.md --out polished.md",
            "python3 .agents/scripts/academic_docgen.py render-docx --md input.md --docx output.docx",
        ]
        for cmd in valid_docgen_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"Valid academic_docgen command was denied: '{cmd}'. Reason: {res.get('reason')}"
            )

    def test_11_dedicated_docgen_cli_unauthorized_subcommand_denied(self):
        """SafetyHooks must deny academic-writer calling unauthorized subcommands on academic_docgen.py."""
        invalid_docgen_commands = [
            "python3 scripts/academic_docgen.py execute-arbitrary-code",
            "python3 scripts/academic_docgen.py run-regression",
            "python3 scripts/academic_docgen.py eval-payload",
            "python3 scripts/academic_docgen.py delete-files",
        ]
        for cmd in invalid_docgen_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Unauthorized docgen subcommand was NOT denied: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    def test_12_module_execution_and_interactive_mode_denied(self):
        """SafetyHooks must deny academic-writer using -m or -i flags with Python."""
        flag_commands = [
            "python3 -m unittest discover",
            "python3 -i scripts/academic_docgen.py",
        ]
        for cmd in flag_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"), "deny",
                f"Flag command was NOT denied: '{cmd}'"
            )
            self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))


    def test_13_writer_blocked_from_mutating_json_files(self):
        """SafetyHooks and academic-writer guard must deny writer from writing or modifying .json files."""
        writer_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-writer", "guard.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_writer_guard", writer_guard_path)
        writer_guard_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(writer_guard_mod)

        target_json_files = [
            "03_deliverables/01_demographics.json",
            "03_deliverables/02_descriptives_and_reliability.json",
            os.path.join(ROOT_DIR, "03_deliverables/06_hypothesis_1.json"),
        ]

        mutation_tools = ["write_to_file", "replace_file_content", "edit_file", "patch"]

        for tool in mutation_tools:
            for json_path in target_json_files:
                payload = {
                    "toolCall": {
                        "name": tool,
                        "args": {
                            "TargetFile": json_path,
                            "CodeContent": '{"status": "overwritten"}'
                        }
                    },
                    "agentName": "academic-writer",
                    "workspacePaths": [ROOT_DIR]
                }
                # 1. Test via SafetyHooks
                res_safety = SafetyHooks.handle_pre_tool_use(payload)
                self.assertEqual(
                    res_safety.get("decision"), "deny",
                    f"SafetyHooks failed to deny {tool} on {json_path} for academic-writer"
                )
                self.assertIn("Statistical Immobility Invariant", res_safety.get("reason", ""))

                # 2. Test directly via academic-writer guard
                res_guard = writer_guard_mod.handle_pre_tool_use(payload)
                self.assertEqual(
                    res_guard.get("decision"), "deny",
                    f"academic-writer guard failed to deny {tool} on {json_path}"
                )
                self.assertIn("Statistical Immobility Invariant", res_guard.get("reason", ""))

    def test_14_writer_blocked_from_shell_commands_targeting_json(self):
        """SafetyHooks and academic-writer guard must deny writer from shell redirection/copy targeting .json."""
        writer_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-writer", "guard.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_writer_guard_shell", writer_guard_path)
        writer_guard_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(writer_guard_mod)

        shell_json_commands = [
            "cat 02_analysis_code/demographics_calculated.json > 03_deliverables/01_demographics.json",
            "cp 02_analysis_code/data.json 03_deliverables/01_demographics.json",
            "echo '{}' >> 03_deliverables/02_descriptives.json",
            "tee 03_deliverables/01_demographics.json",
            "mv temp.json 03_deliverables/01_demographics.json",
        ]

        for cmd in shell_json_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "agentName": "academic-writer",
                "workspacePaths": [ROOT_DIR]
            }
            # 1. Test via SafetyHooks
            res_safety = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(
                res_safety.get("decision"), "deny",
                f"SafetyHooks failed to deny shell command targeting JSON: '{cmd}'"
            )
            self.assertIn("Statistical Immobility Invariant", res_safety.get("reason", ""))

            # 2. Test directly via academic-writer guard
            res_guard = writer_guard_mod.handle_pre_tool_use(payload)
            self.assertEqual(
                res_guard.get("decision"), "deny",
                f"academic-writer guard failed to deny shell command targeting JSON: '{cmd}'"
            )
            self.assertIn("Statistical Immobility Invariant", res_guard.get("reason", ""))

    def test_15_orchestrator_blocked_from_delegating_json_in_required_artifacts_to_writer(self):
        """Orchestrator must deny delegation to academic-writer if required_artifacts contains .json."""
        orch_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "guard.py")
        import importlib.util
        spec = importlib.util.spec_from_file_location("test_orch_guard", orch_guard_path)
        orch_guard_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orch_guard_mod)

        from contracts.canonical_pipelines import verify_capability_routing

        invalid_envelope_prompt = """
        Execute Stage 4D.1:
        ```json
        {
          "task_id": "TSK-2026-CH4-STAGE-4D1-DEMOGRAPHICS",
          "worker_agent": "academic-writer",
          "objective": "Draft Chapter 4 demographics",
          "inputs": [
            "02_analysis_code/demographics_calculated.json"
          ],
          "required_artifacts": [
            "03_deliverables/01_demographics.docx",
            "03_deliverables/01_demographics.md",
            "03_deliverables/01_demographics.json"
          ]
        }
        ```
        """

        # 1. Test verify_capability_routing directly
        import json
        from contracts.delegation_envelope_parser import validate_delegation_prompt
        _, _, env = validate_delegation_prompt(invalid_envelope_prompt, expected_worker="academic-writer")
        ok, reason = verify_capability_routing("academic-writer", invalid_envelope_prompt, env, [ROOT_DIR])
        self.assertFalse(ok, "verify_capability_routing should have rejected delegation with .json in required_artifacts")
        self.assertIn("Statistical Immobility Invariant", reason)

        # 2. Test orchestrator handle_pre_tool_use
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "academic-writer",
                            "Prompt": invalid_envelope_prompt
                        }
                    ]
                }
            },
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR]
        }
        res_orch = orch_guard_mod.handle_pre_tool_use(payload)
        self.assertEqual(
            res_orch.get("decision"), "deny",
            "academic-orchestrator guard should have denied delegation with .json in required_artifacts"
        )
        self.assertIn("Statistical Immobility Invariant", res_orch.get("reason", ""))

    def test_16_orchestrator_permits_json_in_inputs_for_writer(self):
        """Orchestrator must permit delegation to academic-writer when .json is in inputs and only docx/md in required_artifacts."""
        from contracts.canonical_pipelines import verify_capability_routing
        from contracts.delegation_envelope_parser import validate_delegation_prompt

        valid_envelope_prompt = """
        Execute Stage 2.1:
        ```json
        {
          "task_id": "TSK-2026-CH2-STAGE-21-THEORETICAL-FOUNDATIONS",
          "worker_agent": "academic-writer",
          "objective": "Draft Chapter 2 theoretical framework",
          "inputs": [
            "03_deliverables/00_literature_extracted.json"
          ],
          "required_artifacts": [
            "03_deliverables/01_theoretical_foundations.docx",
            "03_deliverables/01_theoretical_foundations.md"
          ]
        }
        ```
        """
        _, _, env = validate_delegation_prompt(valid_envelope_prompt, expected_worker="academic-writer")
        ok, reason = verify_capability_routing("academic-writer", valid_envelope_prompt, env, [ROOT_DIR])
        self.assertTrue(ok, f"verify_capability_routing unexpectedly rejected valid writer envelope: {reason}")

    def test_17_subagent_descriptor_hook_identity_resolution(self):
        """resolve_hook_identity must resolve academic-writer from subagent descriptor file."""
        import json
        import tempfile
        from contracts.hook_identity_contract import resolve_hook_identity, SURFACE_APP_DATA_DIRS

        test_cid = "test-writer-cid-9999"
        primary_surf = list(SURFACE_APP_DATA_DIRS.values())[0]
        subagent_dir = os.path.join(primary_surf, "brain", "test-parent", ".system_generated", "subagents")
        os.makedirs(subagent_dir, exist_ok=True)
        subagent_file = os.path.join(subagent_dir, f"{test_cid}.json")

        try:
            with open(subagent_file, "w", encoding="utf-8") as f:
                json.dump({
                    "conversationId": test_cid,
                    "subagentDescriptor": {
                        "typeName": "academic-writer",
                        "role": "Academic Drafting Specialist"
                    }
                }, f)

            payload = {
                "conversationId": test_cid,
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "ls -la"}
                },
                "workspacePaths": [ROOT_DIR]
            }

            ident = resolve_hook_identity(payload)
            self.assertEqual(ident.agent_name, "academic-writer")
            self.assertEqual(ident.track, "track_2_academic")
            self.assertTrue(ident.is_subagent)
            self.assertFalse(ident.is_main_developer)
            self.assertEqual(ident.resolution_source, "subagent_descriptor")
        finally:
            if os.path.exists(subagent_file):
                os.remove(subagent_file)


if __name__ == "__main__":
    unittest.main()

