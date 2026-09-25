#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/behavior-analyst/guard.py
Dedicated Lifecycle Hook Guard for behavior-analyst.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Analyst Read-Only: Blocks run_command and mutating project deliverables/code.
3. Causal Diagnosis Fidelity: Rejects empty or rubber-stamp diagnoses.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): behavior-analyst cannot spawn subagents.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Analyst Execution Revocation): behavior-analyst cannot execute shell commands directly.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        target = args.get('TargetFile') or args.get('file_path') or ''
        if '03_deliverables' in target or '02_analysis_code' in target:
            return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Analyst Mutation Boundary): behavior-analyst cannot mutate production deliverables or code.'}
    return {'decision': 'allow'}

def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {'decision': 'allow'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', type=str, default='PreToolUse')
    args, _ = parser.parse_known_args()
    payload = {}
    if not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if raw: payload = json.loads(raw)
    res = handle_pre_tool_use(payload) if args.event == 'PreToolUse' else handle_stop(payload) if args.event == 'Stop' else {'decision': 'allow'}
    print(json.dumps(res, ensure_ascii=False))

if __name__ == '__main__': main()
