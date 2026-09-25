#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/final-judge/guard.py
Dedicated Lifecycle Hook Guard for final-judge.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Read-Only Invariant: Release gatekeeper cannot mutate files or run shell commands.
3. Zero Grade Inflation: Blocks naive 20/20 defense grades without published papers.
4. Human Gate Card: Enforces routing defense clearance to Saber Admin Desk (124911145).
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): final-judge cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Gatekeeper Read-Only): final-judge cannot mutate files directly.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Gatekeeper Execution Revocation): final-judge cannot run shell commands directly.'}
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
        naive_20_patterns = [r'نمره\s*۲۰\s*(?:از\s*۲۰)?(?:\s*عالی)?', r'grade:\s*20', r'score:\s*20(?:/20)?', r'20/20']
        has_naive_20 = any(re.search(pat, last_resp, re.IGNORECASE) for pat in naive_20_patterns)
        has_publication_proof = any(w in last_resp.lower() for w in ('indexed journal', 'acceptance letter', 'مقاله isi', 'پذیرش مقاله', 'scopus'))
        if has_naive_20 and not has_publication_proof:
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Zero Grade Inflation): Awarding a naive 20/20 defense grade is strictly forbidden without verified acceptance of an indexed journal publication.'
            }
        if any(w in last_resp.lower() for w in ('clearance_granted', 'defense_approved', 'verdict:')):
            if '124911145' not in last_resp and 'saber' not in last_resp.lower():
                return {
                    'decision': 'continue',
                    'reason': 'CONSTITUTIONAL VIOLATION (Directive 11): Final defense clearance requires formatting a structured Human Gate Card for Saber Ghaderi Admin Desk (124911145).'
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
