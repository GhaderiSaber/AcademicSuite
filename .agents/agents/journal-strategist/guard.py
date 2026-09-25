#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/journal-strategist/guard.py
Dedicated Lifecycle Hook Guard for journal-strategist.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Capability Boundary: Blocks run_command.
3. Directive 6: English-only filenames.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): journal-strategist cannot spawn subagents.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Capability Boundary): journal-strategist packages journal submissions; shell execution is revoked.'}
    target = args.get('TargetFile') or args.get('file_path') or ''
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
