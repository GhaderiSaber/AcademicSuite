#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/skill-evolver/guard.py
Dedicated Lifecycle Hook Guard for skill-evolver.
Enforces:
1. Directive 12: Worker delegation guard (blocks invoke_subagent, define_subagent).
2. Candidate Safety Invariant: Cannot directly overwrite canonical skills in .agents/skills/ without staging candidate diffs.
3. Direct Candidate Assembly Mandate: Writes candidate JSON directly to .agents/learning/candidates/; forbidden from authoring python scratch scripts.
4. Evolver Boundary: Cannot mutate production deliverables directly or execute deliverable mutations via shell.
5. Directive 6: English-only filenames.
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
        return {'decision': 'deny', 'reason': 'CONSTITUTIONAL VIOLATION (Directive 12): skill-evolver cannot spawn subagents.'}

    # 2. Mutation Tool Guard
    if name in ('write_to_file', 'replace_file_content', 'multi_replace_file_content', 'apply_diff', 'edit_file'):
        targets = extract_target_paths(args)
        for target in targets:
            norm_target = target.replace('\\', '/').lower()
            norm_base = os.path.basename(norm_target)

            # 2a. Deliverable isolation
            if '03_deliverables' in norm_target:
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Evolver Boundary): skill-evolver evolves skills and cannot edit deliverables in '03_deliverables/' ('{target}')."
                }
            if norm_target.endswith('.docx') or norm_target.endswith('.doc'):
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Evolver Boundary): skill-evolver cannot create or edit Word documents ('{target}')."
                }

            # 2b. Direct candidate assembly mandate (forbid python scratch scripts)
            if norm_base in ('gen_cand.py', 'patch_script.py') or (norm_target.endswith('.py') and ('scratch/' in norm_target or not norm_target.startswith(('tests/', '.agents/')))):
                return {
                    'decision': 'deny',
                    'reason': (
                        f"CONSTITUTIONAL VIOLATION (Direct Candidate Assembly Mandate): "
                        f"skill-evolver must write candidate JSON files directly to .agents/learning/candidates/<candidate_id>.json. "
                        f"It is forbidden from authoring Python scratch generation scripts ('{target}')."
                    )
                }

            # 2c. Direct skill mutation protection
            if norm_target.startswith(('.agents/skills/', 'skills/')) or '/.agents/skills/' in norm_target or '/skills/' in norm_target:
                return {
                    'decision': 'deny',
                    'reason': f"CONSTITUTIONAL VIOLATION (Candidate Safety Invariant): skill-evolver cannot directly mutate canonical skills '{target}'. It must formulate and stage candidate diffs in .agents/learning/candidates/."
                }

            # 2d. Directive 6 English ASCII
            if not re.match(r'^[a-zA-Z0-9_.\-/\\ ]+$', target):
                return {'decision': 'deny', 'reason': f"CONSTITUTIONAL VIOLATION (Directive 6): File '{target}' must use strictly English ASCII characters."}

    # 3. Shell Command Guard (run_command)
    if name == 'run_command':
        cmd = args.get('CommandLine', '')
        cmd_clean = cmd.strip()

        # 3a. Deliverable Shell Mutations
        if '03_deliverables' in cmd_clean:
            return {
                'decision': 'deny',
                'reason': (
                    f"CONSTITUTIONAL VIOLATION (Evolver Boundary — Shell Deliverable Mutation Prohibited): "
                    f"skill-evolver cannot execute shell commands targeting production deliverables ('{cmd_clean}')."
                )
            }

        # 3b. Document Compilation Scripts
        for doc_pat in DOCUMENT_COMPILATION_PATTERNS:
            if re.search(doc_pat, cmd_clean, re.IGNORECASE):
                return {
                    'decision': 'deny',
                    'reason': (
                        f"CONSTITUTIONAL VIOLATION (Evolver Boundary — Document Compilation Prohibited): "
                        f"skill-evolver cannot run production document compilation scripts ('{cmd_clean}')."
                    )
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
