#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/digital_saber_guard.py
Dedicated Lifecycle Hook Guard for digital-saber.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Advisor Read-Only: Blocks write_to_file, replace_file_content, edit_file.
3. Advisor Execution Revocation: Blocks run_command.
4. Directive 13: Anti-Sycophancy (blocks sycophantic flattery).
5. Human Gate: Pricing estimations in Tomans strictly require Saber Admin Desk clearance (124911145).
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): digital-saber is an advisory consultant and cannot spawn subagents directly.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Advisor Read-Only): digital-saber is an advisory consultant and cannot mutate workspace files directly.'}
    if name == 'run_command':
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Execution Revocation): digital-saber cannot run terminal commands directly.'}
    return {'decision': 'allow'}

def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    tpath = payload.get('transcriptPath')
    if not tpath or not os.path.exists(tpath): return {'decision': 'allow'}
    try:
        with open(tpath, 'r', encoding='utf-8') as f: recs = [json.loads(l) for l in f if l.strip()]
        last_resp = ''
        for r in reversed(recs):
            if r.get('type') == 'PLANNER_RESPONSE' and r.get('content'):
                last_resp = r.get('content', '')
                break
        sycophantic_patterns = [
            r'great question', r'brilliant (?:idea|approach|question)',
            r'excellent observation', r'سؤال بسیار عالی و هوشمندانه‌ای', r'ایده بسیار فوق‌العاده'
        ]
        for pat in sycophantic_patterns:
            if re.search(pat, last_resp, re.IGNORECASE):
                return {'decision': 'continue', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 13 — Anti-Sycophancy): Flattery and sycophantic praise are strictly prohibited.'}
        pricing_terms = ['میلیون تومان', 'تومان', 'قیمت', 'هزینه پروژه', 'برآورد مالی', 'pricing', 'quotation']
        has_pricing = any(term in last_resp for term in pricing_terms)
        has_gate_approval = '124911145' in last_resp or 'saber admin desk' in last_resp.lower()
        if has_pricing and not has_gate_approval:
            return {'decision': 'continue', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 7 & 11 — Human Gate Required): Financial quotations in Tomans require approval from Saber Admin Desk (124911145).'}
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
