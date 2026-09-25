#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/evidence-auditor/guard.py
Dedicated Lifecycle Hook Guard for evidence-auditor.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Read-Only Invariant: Evaluative auditor cannot mutate files or run shell commands.
3. Directive 14: Zero Ghost Citations and verified citation concordance.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): evidence-auditor cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Auditor Read-Only): evidence-auditor cannot mutate files directly.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Auditor Execution Revocation): evidence-auditor cannot execute shell commands directly.'}
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
        claims_pass = any(w in last_resp.lower() for w in ('concordance verified', 'citations approved', 'references verified', 'verdict: pass'))
        if claims_pass and ('ghost citation' in last_resp.lower() or 'unverified reference' in last_resp.lower()):
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Directive 14): evidence-auditor cannot approve deliverables containing ghost or unverified citations.'
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
