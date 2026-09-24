#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/results_auditor_guard.py
Dedicated Lifecycle Hook Guard for results-auditor.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Read-Only Invariant: Quality auditor cannot mutate files or run shell commands.
3. Directive 4: Enforces APA 7 precision, Persian leading zero standard, and p = .000 ban.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): results-auditor cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Auditor Read-Only): results-auditor cannot mutate files directly.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Auditor Execution Revocation): results-auditor cannot execute shell commands directly.'}
    return {'decision': 'allow'}

def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    tpath = payload.get('transcriptPath')
    if not tpath or not os.path.exists(tpath):
        return {'decision': 'allow'}
    try:
        with open(tpath, 'r', encoding='utf-8') as f:
            recs = [json.loads(l) for l in f if l.strip()]
        last_resp = ''
        for r in reversed(recs):
            if r.get('type') == 'PLANNER_RESPONSE' and r.get('content'):
                last_resp = r.get('content', '')
                break
        if re.search(r'[pP]\s*=\s*\.?000', last_resp) or re.search(r'[pP]\s*=\s*۰\.۰۰۰', last_resp):
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Directive 4): results-auditor must enforce reporting p < .001 (or ۰.۰۰۱ > p). Reporting p = .000 is strictly forbidden.'
            }
        if re.search(r'(?<![۰-۹0-9])\.[۰-۹]+', last_resp):
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Directive 4): Detected naked decimal in Persian text (e.g. ".۰۵"). You must strictly preserve the leading zero ("۰.۰۵").'
            }
    except Exception:
        pass
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
