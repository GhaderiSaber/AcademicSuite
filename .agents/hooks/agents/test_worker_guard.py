#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/test_worker_guard.py
Dedicated Lifecycle Hook Guard for test-worker.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Allows execution tools.
"""
import sys, os, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('invoke_subagent', 'define_subagent'):
        return {
            'decision': 'deny',
            'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): test-worker is an execution worker and cannot spawn subagents.'
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
