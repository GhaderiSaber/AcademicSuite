#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/research-agent/guard.py
Dedicated Lifecycle Hook Guard for research-agent.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent).
2. Directive 1: Mandatory Pre-Flight Gate on CLI scripts.
3. Directive 6: English-only filenames.
4. Directive 15: Temporal Reality Anchor: 2026 (1405 SH).
"""
import sys, os, re, json, argparse
from typing import Dict, Any

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): research-agent is an execution worker and cannot spawn subagents.'}
    if name == 'run_command':
        cmd = args.get('CommandLine', '')
        m = re.search(r'\.agents/skills/([\w-]+)/scripts/([\w-]+\.py)', cmd)
        if m:
            skill_name = m.group(1)
            target_skill_md = f".agents/skills/{skill_name}/SKILL.md"
            transcript_path = payload.get('transcriptPath')
            saw_view = False
            if transcript_path and os.path.exists(transcript_path):
                try:
                    with open(transcript_path, 'r', encoding='utf-8') as tf:
                        for line in tf:
                            if not line.strip(): continue
                            rec = json.loads(line)
                            for tc in rec.get('tool_calls', []):
                                if tc.get('name') == 'view_file':
                                    p = tc.get('args', {}).get('AbsolutePath', '')
                                    if target_skill_md in p or f"skills/{skill_name}/SKILL.md" in p:
                                        saw_view = True
                                        break
                            if saw_view: break
                except Exception:
                    pass
            if not saw_view:
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Directive 1 — Mandatory Pre-Flight Gate): Attempted to execute CLI script '{m.group(2)}' without first inspecting the skill specification. You MUST explicitly call view_file on '{target_skill_md}' before running scripts."
                }
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
        if re.search(r'\b(?:currently in|the year is|as of)\s+(?:202[0-5]|139\d|140[0-4])\b', last_resp, re.IGNORECASE):
            return {
                'decision': 'continue',
                'reason': 'CONSTITUTIONAL VIOLATION (Directive 15 — Temporal Reality Anchor): The operative calendar year is strictly 2026 (1405 SH).'
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
