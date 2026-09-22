#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_knowledge_store_hook.py — Test Suite for Knowledge Store PreToolUse Safety Hook

Verifies:
1. Mechanical fail-closed interception of invalid lessons (missing target_agent/target_agents).
2. Mechanical fail-closed interception of invalid anti-patterns.
3. Syntax error interception on malformed JSON.
4. Boundary guard preventing direct promotion (is_active_behavior: true).
5. Successful allowance of 100% schema-compliant lessons and anti-patterns.
6. 100% schema compliance across all existing files in .agents/learning/knowledge/.
"""

import os
import sys
import json
import glob
import unittest
try:
    import pytest
except ImportError:
    pytest = None

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from hooks.safety_hooks import SafetyHooks
from contracts.contract_validator import validate_lesson, validate_anti_pattern


class TestKnowledgeStoreSafetyHook(unittest.TestCase):
    """Validates the PreToolUse mechanical enforcement on knowledge store mutations."""

    def test_lesson_missing_target_agent_is_denied(self):
        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-001.json",
                    "CodeContent": json.dumps({
                        "contract_version": "1.0.0",
                        "lesson_id": "LSN-TEST-001",
                        "desired_behavior": "Always decouple numbers",
                        "generalization": "Decouple all numbers",
                        "scope": "CROSS_PROJECT_UNIVERSAL",
                        "confidence": 0.95,
                        "evidence": {
                            "metric_or_check": "CHECK",
                            "observed_value": "val",
                            "threshold_value": "thresh"
                        },
                        "related_skills": ["apa-reporting"],
                        "is_active_behavior": False,
                        "status": "VALIDATED",
                        "created_at": "2026-09-22T09:00:00Z"
                        # target_agent and target_agents intentionally omitted
                    })
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "target_agent" in res.get("reason", "")

    def test_lesson_missing_target_agents_list_is_denied(self):
        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-002.json",
                    "CodeContent": json.dumps({
                        "contract_version": "1.0.0",
                        "lesson_id": "LSN-TEST-002",
                        "desired_behavior": "Always decouple numbers",
                        "generalization": "Decouple all numbers",
                        "scope": "CROSS_PROJECT_UNIVERSAL",
                        "confidence": 0.95,
                        "evidence": {
                            "metric_or_check": "CHECK",
                            "observed_value": "val",
                            "threshold_value": "thresh"
                        },
                        "related_skills": ["apa-reporting"],
                        "is_active_behavior": False,
                        "status": "VALIDATED",
                        "created_at": "2026-09-22T09:00:00Z",
                        "target_agent": "academic-writer"
                        # target_agents omitted
                    })
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "target_agents" in res.get("reason", "")

    def test_anti_pattern_missing_target_agent_is_denied(self):
        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/anti-patterns/AP-TEST-001.json",
                    "CodeContent": json.dumps({
                        "contract_version": "1.0.0",
                        "anti_pattern_id": "AP-TEST-001",
                        "category": "typography",
                        "defective_pattern": "Writing redundant symbols",
                        "why_defective": "Violates APA guidelines",
                        "observed_symptoms": ["Symptom 1"],
                        "corrective_remedy": "Strip symbols",
                        "detection_heuristic": {"trigger_rule": "rule"},
                        "reusable": True,
                        "updated_at": "2026-09-22T09:00:00Z"
                        # target_agent and target_agents omitted
                    })
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "target_agent" in res.get("reason", "")

    def test_malformed_json_is_denied(self):
        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-003.json",
                    "CodeContent": "{not valid json"
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Syntax Error" in res.get("reason", "") or "invalid JSON" in res.get("reason", "")

    def test_direct_promotion_is_denied(self):
        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-TEST-004.json",
                    "CodeContent": json.dumps({
                        "contract_version": "1.0.0",
                        "lesson_id": "LSN-TEST-004",
                        "target_agent": "academic-writer",
                        "target_agents": ["academic-writer"],
                        "is_active_behavior": True  # FORBIDDEN: Direct promotion
                    })
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Promotion Boundary" in res.get("reason", "")

    def test_valid_lesson_is_allowed(self):
        lesson_file = os.path.join(AGENTS_DIR, "learning", "knowledge", "lessons", "LSN-2026-PURE-NUMERIC-P-VALUES-IN-TABLES-001.json")
        with open(lesson_file, "r", encoding="utf-8") as f:
            valid_json = f.read()

        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/lessons/LSN-2026-PURE-NUMERIC-P-VALUES-IN-TABLES-001.json",
                    "CodeContent": valid_json
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "allow"

    def test_valid_anti_pattern_is_allowed(self):
        ap_file = os.path.join(AGENTS_DIR, "learning", "knowledge", "anti-patterns", "AP-2026-REDUNDANT-P-SYMBOL-IN-TABLE-CELLS.json")
        with open(ap_file, "r", encoding="utf-8") as f:
            valid_json = f.read()

        payload = {
            "agentName": "knowledge-curator",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": ".agents/learning/knowledge/anti-patterns/AP-2026-REDUNDANT-P-SYMBOL-IN-TABLE-CELLS.json",
                    "CodeContent": valid_json
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "allow"

    def test_all_existing_knowledge_files_are_strictly_valid(self):
        lessons = glob.glob(os.path.join(AGENTS_DIR, "learning", "knowledge", "lessons", "*.json"))
        anti_patterns = glob.glob(os.path.join(AGENTS_DIR, "learning", "knowledge", "anti-patterns", "*.json"))

        assert len(lessons) > 0, "Expected existing lesson files"
        assert len(anti_patterns) > 0, "Expected existing anti-pattern files"

        for l_path in lessons:
            with open(l_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "target_agent" in data, f"Missing target_agent in {l_path}"
            assert "target_agents" in data, f"Missing target_agents in {l_path}"
            report = validate_lesson(data)
            assert report["valid"] is True, f"Lesson schema validation failed for {l_path}: {report['errors']}"

        for ap_path in anti_patterns:
            with open(ap_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "target_agent" in data, f"Missing target_agent in {ap_path}"
            assert "target_agents" in data, f"Missing target_agents in {ap_path}"
            report = validate_anti_pattern(data)
            assert report["valid"] is True, f"Anti-pattern schema validation failed for {ap_path}: {report['errors']}"
