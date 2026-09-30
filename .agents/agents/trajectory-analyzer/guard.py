#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/trajectory-analyzer/guard.py
Dedicated Lifecycle Hook Guard for trajectory-analyzer.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Forensic Read-Only: Blocks run_command and file mutation tools.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): trajectory-analyzer cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        target = args.get('TargetFile') or args.get('file_path') or args.get('target') or ''
        if any(prod in target for prod in ('03_deliverables', '02_analysis_code', '01_raw_inputs', '04_references_and_lit')):
            return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Forensic Read-Only): trajectory-analyzer cannot mutate production files '{target}'."}
        if not ('.agents/learning/' in target or '/brain/' in target or 'artifact' in target.lower() or 'scratch' in target or target.endswith(('.json', '.jsonl', '.md'))):
            return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Forensic Read-Only): trajectory-analyzer writes strictly to .agents/learning/ or brain artifacts."}
        if target and not re.match(r'^[a-zA-Z0-9_.\-/\\]+$', target):
            return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Directive 6): File '{target}' must use strictly English ASCII characters."}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Execution Revocation): trajectory-analyzer cannot run shell commands.'}
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
