#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/test-orchestrator/guard.py
Dedicated Lifecycle Hook Guard for test-orchestrator.
Enforces:
1. Directive 20: Orchestrator Non-Execution Invariant (blocks run_command, write_to_file, replace_file_content, edit_file).
2. Allows invoke_subagent.
"""
import sys, os, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('run_command', 'write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        return {
            'decision': 'deny',
            'reason': f"CONSTITUTIONAL VIOLATION (Directive 20 — Orchestrator Non-Execution Invariant): test-orchestrator cannot execute tool '{name}'. Delegation must be used."
        }
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
