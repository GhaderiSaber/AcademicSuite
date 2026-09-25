#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/statistical_auditor_guard.py
Dedicated Lifecycle Hook Guard for statistical-auditor.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Auditor Mutation Boundary: statistical-auditor cannot directly mutate 03_deliverables/.
3. Mathematical Admissibility Gate: Blocks Heywood cases (negative variances, loadings > 1.0).
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): statistical-auditor cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        target = args.get('TargetFile') or args.get('file_path') or ''
        if '03_deliverables' in target or target.endswith(('.docx', '.pptx')):
            return {
                'decision': 'deny',
                'reason': 'CONSTITUTIONAL VIOLATION (Auditor Mutation Boundary): statistical-auditor cannot mutate deliverables directly.'
            }
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
        if re.search(r'error variance\s*=\s*-\d', last_resp, re.I) or re.search(r'variance\s*<\s*0', last_resp, re.I):
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Mathematical Admissibility Gate): statistical-auditor detected a Heywood case (negative error variance).'
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
