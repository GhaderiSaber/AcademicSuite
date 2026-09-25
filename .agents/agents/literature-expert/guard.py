#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/literature_expert_guard.py
Dedicated Lifecycle Hook Guard for literature-expert.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Directive 6: English-only filenames.
3. Read-Only / Source Extraction Boundary: Cannot mutate 03_deliverables/ directly.
4. Directive 15: Temporal Reality Anchor (2026 / 1405 SH).
5. Directive 14: Anti-Hallucination & Zero Ghost Citations.
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): literature-expert cannot spawn subagents.'}
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        target = args.get('TargetFile') or args.get('file_path') or ''
        if '03_deliverables' in target or target.endswith(('.docx', '.pptx')):
            return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Literature Source Boundary): literature-expert extracts and synthesizes evidence; chapter drafting belongs to academic-writer.'}
    target = args.get('TargetFile') or args.get('file_path') or args.get('path') or ''
    if target and not re.match(r'^[a-zA-Z0-9_.\-/\\]+$', target):
        return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Directive 6): File '{target}' must use strictly English ASCII characters."}
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
        if re.search(r'\b(?:currently in|the year is|as of)\s+(?:202[0-5]|139\d|140[0-4])\b', last_resp, re.I):
            return {'decision': 'continue', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 15): The operative calendar year is strictly 2026 (1405 SH).'}
        if re.search(r'doi:\s*10\.1234/ghost', last_resp, re.I) or re.search(r'ghost\s*citation', last_resp, re.I):
            return {'decision': 'continue', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 14): Detected unverified or ghost DOI citation.'}
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
