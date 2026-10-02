#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/evaluation-agent/guard.py
Dedicated Lifecycle Hook Guard for evaluation-agent.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent, define_subagent).
2. Evaluator Boundary: Cannot mutate production deliverables directly or execute deliverable mutations via shell.
3. Directive 6: English-only filenames.
4. Zero Unverified Success: Rejects declaring improvements without benchmark evidence.
"""
import sys, os, re, json, argparse
from typing import Dict, Any, List

DOCUMENT_COMPILATION_PATTERNS = [
    r"\bcompile_.*chapter.*\.py\b",
    r"\bbuild_thesis\.py\b",
    r"\bbuild_discussion\.py\b",
    r"\bbuild_hypothesis_triad.*\.py\b",
    r"\bscaffold_chapter4.*\.py\b",
    r"\bacademic_docgen\.py\b",
    r"\bformat_apa.*\.py\b",
    r"\bopenxml_docx_engine\.py\b",
    r"\bpersian_docx_engine\.py\b",
]

def extract_target_paths(args: Dict[str, Any]) -> List[str]:
    paths = []
    for k in ("TargetFile", "file_path", "filePath", "target_file", "path", "target"):
        val = args.get(k)
        if isinstance(val, str) and val.strip():
            paths.append(val.strip())
    for lk in ("files", "paths", "targets", "file_paths"):
        val = args.get(lk)
        if isinstance(val, list):
            for it in val:
                if isinstance(it, str) and it.strip():
                    paths.append(it.strip())
    return paths

def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get('toolCall', {})
    name = (tool_call.get('name') or '').strip().lower()
    args = tool_call.get('args', {})

    # 1. Delegation Guard
    if name in ('invoke_subagent', 'define_subagent'):
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): evaluation-agent cannot spawn subagents.'}

    # 2. Mutation Tool Guard
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        targets = extract_target_paths(args)
        for target in targets:
            norm_target = target.replace('\\', '/').lower()
            if '03_deliverables' in norm_target:
                return {
                    'decision': 'deny',
                    'reason': 'CONSTITUTIONAL VIOLATION (Evaluator Boundary): evaluation-agent evaluates candidate performance and cannot edit deliverables in 03_deliverables/ directly.'
                }
            if norm_target.endswith('.docx') or norm_target.endswith('.doc'):
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Evaluator Boundary): evaluation-agent cannot create or edit Word documents ('{target}')."
                }
            if not re.match(r'^[a-zA-Z0-9_.\-/\\ ]+$', target):
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Directive 6): File '{target}' must use strictly English ASCII characters."
                }

    # 3. Shell Command Guard (run_command)
    if name == 'run_command':
        cmd = args.get('CommandLine', '')
        cmd_clean = cmd.strip()

        # 3a. Deliverable Shell Mutations (sed -i, awk, redirects targeting 03_deliverables)
        # Note: LSN-2026-LEGACY-VAL-ISOLATION permits os.remove / rm on failing validation_report.json
        if '03_deliverables' in cmd_clean:
            is_val_report_rm = bool(re.search(r'\brm\s+(?:-f\s+)?[\'"]?[^\s;&|]*03_deliverables[^\s;&|]*validation_report\.json[\'"]?', cmd_clean))
            if not is_val_report_rm:
                shell_deliv_match = re.search(
                    r'(?:>|>>|\btee\b|\bsed\s+-i|\bawk\b|\bperl\s+-i|\bcp\b|\bmv\b|\bcat\s+.*>|\btruncate\b|\btouch\b).*03_deliverables',
                    cmd_clean,
                    re.IGNORECASE
                )
                if shell_deliv_match or any(op in cmd_clean for op in ('>', '>>', 'sed -i')):
                    return {
                        'decision': 'deny',
                        'reason': (
                            f"CONSTITUTIONAL VIOLATION (Evaluator Boundary — Shell Deliverable Mutation Prohibited): "
                            f"evaluation-agent cannot execute shell commands mutating production deliverables in '03_deliverables/' ('{cmd_clean}'). "
                            f"Deliverable remediation belongs exclusively to academic-writer after candidate graduation."
                        )
                    }

        # 3b. Document Generation / Compilation Invocations
        for doc_pat in DOCUMENT_COMPILATION_PATTERNS:
            if re.search(doc_pat, cmd_clean, re.IGNORECASE):
                return {
                    'decision': 'deny',
                    'reason': (
                        f"CONSTITUTIONAL VIOLATION (Evaluator Boundary — Document Compilation Prohibited): "
                        f"evaluation-agent is strictly an evaluator of continuous learning candidates and cannot run "
                        f"production document compilation scripts ('{cmd_clean}'). Document generation belongs exclusively to academic-writer."
                    )
                }

        # 3c. Ad-hoc patch script creation & execution
        if re.search(r'\b(?:cat\s+<<.*patch_script|python3?\s+.*patch_script|python3?\s+.*gen_cand)\b', cmd_clean, re.IGNORECASE):
            return {
                'decision': 'deny',
                'reason': (
                    f"CONSTITUTIONAL VIOLATION (Evaluator Boundary — Ad-Hoc Patch Script Prohibited): "
                    f"evaluation-agent cannot author or execute ad-hoc patch scripts ('{cmd_clean}'). "
                    f"Evaluation must be performed against deterministic evaluation harnesses and test suites."
                )
            }

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
        if 'improvement verified' in last_resp.lower() or 'benchmarks passed' in last_resp.lower():
            if not any(k in last_resp.lower() for k in ('test', 'metric', 'score', 'benchmark', 'baseline', 'run')):
                return {'decision': 'continue', 'reason': 'CONSTITUTIONAL VIOLATION (Evaluator Integrity): evaluation-agent cannot declare success without explicit quantitative benchmark metrics.'}
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
