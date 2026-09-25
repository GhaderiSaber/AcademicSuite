#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/data_curator_guard.py
Dedicated Lifecycle Hook Guard for data-curator.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Raw Data Protection: Blocks mutating 01_raw_inputs/ and raw_*.xlsx.
3. Directive 23: Clean Workspace Root Standard (blocks root scripts).
4. Directive 6: English-only filenames.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): data-curator cannot spawn subagents.'}
    target = args.get('TargetFile') or args.get('file_path') or ''
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        if '01_raw_inputs' in target or re.search(r'raw_.*\.(xlsx|csv|sav)', target, re.I):
            return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Raw Data Protection): data-curator cannot mutate raw data artifact '{target}'."}
        workspaces = payload.get('workspacePaths', [])
        for ws in workspaces:
            parent_dir = os.path.dirname(os.path.abspath(target))
            if os.path.abspath(parent_dir) == os.path.abspath(ws):
                if target.endswith(('.py', '.sh', '.bash', '.r', '.sps')):
                    return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Directive 23 — Clean Workspace Root): Cannot create executable script '{target}' in root."}
    if target and not re.match(r'^[a-zA-Z0-9_.\-/\\]+$', target):
        return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Directive 6): File '{target}' must use strictly English ASCII characters."}
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
