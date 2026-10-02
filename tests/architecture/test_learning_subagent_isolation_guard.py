#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_subagent_isolation_guard.py

Regression test suite for learning subagent deliverable isolation and guard fortification.
Verifies:
1. Orchestrator delegation guard blocks delegating deliverable tasks to learning subagents.
2. Skill-evolver guard blocks mutating deliverables, creating python scratch scripts, and editing canonical skills.
3. Evaluation-agent guard blocks shell deliverable mutations (sed -i, awk, redirects) and document compilation scripts.
4. Evaluation-agent guard allows graduation compiler and test runners (pytest).
5. Global safety_hooks block learning subagents from writing to 03_deliverables/ or running document generators.
"""

import os
import sys
import json
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

# Import orchestrator guard
import importlib.util
def load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

orch_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "guard.py")
eval_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "evaluation-agent", "guard.py")
evolv_guard_path = os.path.join(ROOT_DIR, ".agents", "agents", "skill-evolver", "guard.py")

orch_guard = load_module_from_path("orch_guard", orch_guard_path)
eval_guard = load_module_from_path("eval_guard", eval_guard_path)
evolv_guard = load_module_from_path("evolv_guard", evolv_guard_path)

from safety_hooks import SafetyHooks


class TestLearningSubagentIsolationGuard(unittest.TestCase):
    """Verifies isolation between learning subagents and production deliverables."""

    def test_orchestrator_blocks_deliverables_in_envelope_to_skill_evolver(self):
        """Orchestrator must deny delegating tasks with 03_deliverables in required_artifacts to skill-evolver."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "skill-evolver",
                            "Role": "Skill Mutation Synthesizer",
                            "Prompt": json.dumps({
                                "task_id": "TSK-2026-LEARN-EVOLV-007",
                                "worker_agent": "skill-evolver",
                                "objective": "Fix table formatting defect",
                                "inputs": ["03_deliverables/validation_report.json"],
                                "required_artifacts": ["03_deliverables/findings.md"]
                            })
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = orch_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Learning Subagent", res.get("reason", ""))
        self.assertIn("03_deliverables", res.get("reason", ""))

    def test_orchestrator_blocks_deliverable_cleanup_prompt_to_evaluation_agent(self):
        """Orchestrator must deny delegating deliverable cleanup/patching instructions to evaluation-agent."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "evaluation-agent",
                            "Role": "Independent Candidate Evaluator",
                            "Prompt": "Please remove corrupt tokens from 03_deliverables/findings.md"
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = orch_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Learning Subagent", res.get("reason", ""))

    def test_orchestrator_allows_pure_learning_delegation(self):
        """Orchestrator allows delegating pure learning tasks without deliverable contamination."""
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "skill-evolver",
                            "Role": "Skill Mutation Synthesizer",
                            "Prompt": json.dumps({
                                "task_id": "TSK-2026-LEARN-EVOLV-008",
                                "worker_agent": "skill-evolver",
                                "objective": "Formulate candidate diff for regression APA table formatting",
                                "inputs": [".agents/learning/knowledge/LSN-2026-REG-TABLE.json"],
                                "required_artifacts": [".agents/learning/candidates/CAND-2026-REG-TABLE-001.json"]
                            })
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = orch_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_skill_evolver_guard_blocks_deliverables_write(self):
        """skill-evolver guard must deny write_to_file inside 03_deliverables/."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "03_deliverables", "findings.md"),
                    "CodeContent": "# Findings"
                }
            }
        }
        res = evolv_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Evolver Boundary", res.get("reason", ""))

    def test_skill_evolver_guard_blocks_gen_cand_py_scratch_script(self):
        """skill-evolver guard must deny creating python scratch scripts like gen_cand.py."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "scratch", "gen_cand.py"),
                    "CodeContent": "import json\nprint('candidate')"
                }
            }
        }
        res = evolv_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Direct Candidate Assembly Mandate", res.get("reason", ""))

    def test_skill_evolver_guard_blocks_canonical_skills_direct_mutation(self):
        """skill-evolver guard must deny writing directly to .agents/skills/."""
        payload = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, ".agents", "skills", "regression", "SKILL.md"),
                    "TargetContent": "old",
                    "ReplacementContent": "new"
                }
            }
        }
        res = evolv_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Candidate Safety Invariant", res.get("reason", ""))

    def test_skill_evolver_guard_allows_staged_candidate_json(self):
        """skill-evolver guard must allow writing candidate JSON to .agents/learning/candidates/."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, ".agents", "learning", "candidates", "CAND-2026-TEST-001.json"),
                    "CodeContent": json.dumps({"candidate_id": "CAND-2026-TEST-001"})
                }
            }
        }
        res = evolv_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_evaluation_agent_guard_blocks_sed_on_deliverables(self):
        """evaluation-agent guard must deny run_command using sed -i on 03_deliverables/."""
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "sed -i 's/corrupt/clean/g' 03_deliverables/findings.md"
                }
            }
        }
        res = eval_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Shell Deliverable Mutation Prohibited", res.get("reason", ""))

    def test_evaluation_agent_guard_blocks_document_compilation(self):
        """evaluation-agent guard must deny run_command running document compilation scripts."""
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 02_analysis_code/compile_gold_standard_chapter4.py"
                }
            }
        }
        res = eval_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Document Compilation Prohibited", res.get("reason", ""))

    def test_evaluation_agent_guard_blocks_ad_hoc_patch_script(self):
        """evaluation-agent guard must deny authoring or executing patch_script.py."""
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "cat << 'EOF' > patch_script.py && python3 patch_script.py"
                }
            }
        }
        res = eval_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Ad-Hoc Patch Script Prohibited", res.get("reason", ""))

    def test_evaluation_agent_guard_allows_compiler_and_pytest(self):
        """evaluation-agent guard must allow running the graduation compiler and test suites."""
        compiler_payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 .agents/scripts/academic_graduation_compiler.py compile-candidate .agents/learning/candidates/CAND-001.json"
                }
            }
        }
        res1 = eval_guard.handle_pre_tool_use(compiler_payload)
        self.assertEqual(res1.get("decision"), "allow")

        pytest_payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "pytest tests/evals/test_eval_regression.py -v"
                }
            }
        }
        res2 = eval_guard.handle_pre_tool_use(pytest_payload)
        self.assertEqual(res2.get("decision"), "allow")

    def test_safety_hooks_blocks_learning_subagents_from_deliverables_mutation(self):
        """safety_hooks.py must intercept and deny learning subagents writing to 03_deliverables/."""
        payload = {
            "caller": "evaluation-agent",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "03_deliverables", "summary.md"),
                    "CodeContent": "corrupt"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Deliverable Immutability Invariant", res.get("reason", ""))

    def test_safety_hooks_blocks_learning_subagents_from_shell_deliverables(self):
        """safety_hooks.py must deny learning subagents executing shell commands on 03_deliverables/."""
        payload = {
            "caller": "evaluation-agent",
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "sed -i 's/foo/bar/g' 03_deliverables/findings.md"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Learning Subagent Deliverable Immutability Invariant", res.get("reason", ""))

    def test_safety_hooks_blocks_learning_subagents_from_compiling_documents(self):
        """safety_hooks.py must deny learning subagents running document compilation scripts."""
        payload = {
            "caller": "evaluation-agent",
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 02_analysis_code/compile_gold_standard_chapter4.py"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Learning Subagent Execution Boundary Guard", res.get("reason", ""))


if __name__ == "__main__":
    unittest.main()
