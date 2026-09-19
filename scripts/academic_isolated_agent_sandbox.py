#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_isolated_agent_sandbox.py — AcademicSuite Isolated Agent Sandbox

Instantiates isolated agent and skill versions in an isolated sandbox directory:
    learning/candidates/<candidate_id>/isolated_agent/

Invariants:
1. Production Isolation:
   - Canonical production files in .agents/agents/ and .agents/skills/ are NEVER modified.
   - The candidate mutation is applied strictly to an isolated copy inside the candidate's sandbox.
2. Cryptographic Manifest:
   - Every sandbox generates an `isolated_manifest.json` tracking original file hashes,
     patched file hashes, mutation metadata, and isolation paths.
3. Execution Harness:
   - Provides methods to inspect, load, and execute test cases against the isolated agent
     without polluting production context.
"""

import os
import sys
import json
import shutil
import hashlib
import uuid
import difflib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


class SandboxError(Exception):
    """Base exception for sandbox operations."""
    pass


class ProductionIntegrityViolationError(SandboxError):
    """Raised if an operation attempts to mutate production files instead of the sandbox."""
    pass


def compute_sha256(content_or_path: Any) -> str:
    """Computes SHA-256 hash of a file or string."""
    hasher = hashlib.sha256()
    if isinstance(content_or_path, str) and os.path.isfile(content_or_path):
        with open(content_or_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
    elif isinstance(content_or_path, (str, bytes)):
        data = content_or_path.encode("utf-8") if isinstance(content_or_path, str) else content_or_path
        hasher.update(data)
    return hasher.hexdigest()


class AcademicIsolatedAgentSandbox:
    """
    Manages isolated staging sandboxes for candidate agents and skills.
    Ensures safe, non-destructive experimentation and testing.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.candidates_root = os.path.join(self.base_dir, "learning", "candidates")
        self.production_skills_dir = os.path.join(self.base_dir, ".agents", "skills")
        self.production_agents_dir = os.path.join(self.base_dir, ".agents", "agents")

        os.makedirs(self.candidates_root, exist_ok=True)

    def get_sandbox_dir(self, candidate_id: str) -> str:
        """Returns the isolated agent sandbox directory for a given candidate."""
        return os.path.join(self.candidates_root, candidate_id, "isolated_agent")

    def create_sandbox(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates an isolated agent sandbox, copies target components, applies
        the candidate mutation patch, and writes `isolated_manifest.json`.

        Args:
            candidate_data: Candidate improvement dictionary (conforming to improvement_candidate schema).

        Returns:
            Dictionary containing sandbox metadata and manifest.
        """
        cid = candidate_data.get("candidate_id") or f"CAND-{uuid.uuid4().hex[:6].upper()}"
        target_comp = candidate_data.get("target_component", "")
        target_type = candidate_data.get("target_type", "SKILL_PROCEDURAL_SPECIFICATION")
        mutation = candidate_data.get("mutation", {})
        diff_type = mutation.get("diff_type", "UNIFIED_DIFF")
        content = mutation.get("content", "")

        sandbox_dir = self.get_sandbox_dir(cid)
        os.makedirs(sandbox_dir, exist_ok=True)

        manifest_path = os.path.join(sandbox_dir, "isolated_manifest.json")

        base_files = {}
        modified_files = {}

        # Resolve target component path
        src_path = os.path.join(self.base_dir, target_comp) if not os.path.isabs(target_comp) else target_comp
        if not os.path.isfile(src_path):
            # If target_component is a skill name, look up .agents/skills/<name>/SKILL.md
            candidate_skill_path = os.path.join(self.production_skills_dir, target_comp, "SKILL.md")
            if os.path.isfile(candidate_skill_path):
                src_path = candidate_skill_path
            else:
                # If target_component is an agent name, look up .agents/agents/<name>.json or .agents/agents/<name>/agent.md
                agent_json = os.path.join(self.production_agents_dir, f"{target_comp}.json")
                if os.path.isfile(agent_json):
                    src_path = agent_json

        original_content = ""
        orig_sha = ""
        if os.path.isfile(src_path):
            with open(src_path, "r", encoding="utf-8") as f:
                original_content = f.read()
            orig_sha = compute_sha256(original_content)
            base_rel = os.path.relpath(src_path, self.base_dir)
            base_files[base_rel] = {
                "source_path": src_path,
                "sha256": orig_sha
            }

        # Apply mutation in sandbox
        dest_filename = os.path.basename(src_path) if os.path.isfile(src_path) else "SKILL.md"
        dest_path = os.path.join(sandbox_dir, dest_filename)

        patched_content = self._apply_mutation_to_content(
            original_content=original_content,
            diff_type=diff_type,
            mutation_content=content
        )

        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(patched_content)

        patched_sha = compute_sha256(patched_content)
        modified_files[dest_filename] = {
            "sandbox_path": dest_path,
            "sha256": patched_sha
        }

        # Manifest
        manifest = {
            "contract_version": "1.0.0",
            "sandbox_id": f"SBX-{cid}",
            "candidate_id": cid,
            "target_component": target_comp,
            "target_type": target_type,
            "sandbox_directory": sandbox_dir,
            "base_files": base_files,
            "modified_files": modified_files,
            "mutation_applied": {
                "diff_type": diff_type,
                "content_preview": content[:120] + ("..." if len(content) > 120 else ""),
                "applied_at": datetime.now(timezone.utc).isoformat()
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest

    def _apply_mutation_to_content(
        self,
        original_content: str,
        diff_type: str,
        mutation_content: str
    ) -> str:
        """Applies mutation to content based on diff_type."""
        if not original_content:
            return mutation_content

        if diff_type == "FULL_CONTENT_REPLACEMENT":
            return mutation_content

        elif diff_type == "UNIFIED_DIFF":
            # Attempt unified diff patch
            try:
                patch_lines = mutation_content.splitlines(keepends=True)
                # If patch does not look like unified diff, append/replace
                if any(l.startswith("@@") for l in patch_lines):
                    # Apply diff
                    patched = self._patch_unified_diff(original_content, mutation_content)
                    if patched is not None:
                        return patched
            except Exception:
                pass
            # Fallback: append mutation content with clear header
            return original_content + "\n\n# --- Candidate Refinement ---\n" + mutation_content

        elif diff_type == "PARAMETER_PATCH":
            # JSON parameter patch
            try:
                orig_json = json.loads(original_content)
                patch_json = json.loads(mutation_content)
                orig_json.update(patch_json)
                return json.dumps(orig_json, indent=2, ensure_ascii=False)
            except Exception:
                return original_content + "\n\n# --- Parameter Patch ---\n" + mutation_content

        # Default fallback: append
        return original_content + "\n\n# --- Candidate Mutation ---\n" + mutation_content

    def _patch_unified_diff(self, original_text: str, diff_text: str) -> Optional[str]:
        """Simple deterministic unified diff patcher."""
        try:
            orig_lines = original_text.splitlines(keepends=True)
            diff_lines = diff_text.splitlines(keepends=True)
            result = []
            orig_idx = 0

            i = 0
            while i < len(diff_lines):
                line = diff_lines[i]
                if line.startswith("@@"):
                    # Parse hunk header: @@ -start,len +start,len @@
                    m = re.search(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
                    if m:
                        orig_start = int(m.group(1)) - 1
                        while orig_idx < orig_start and orig_idx < len(orig_lines):
                            result.append(orig_lines[orig_idx])
                            orig_idx += 1
                    i += 1
                    continue
                elif line.startswith("---") or line.startswith("+++"):
                    i += 1
                    continue
                elif line.startswith("-"):
                    # Line removed from original
                    orig_idx += 1
                    i += 1
                    continue
                elif line.startswith("+"):
                    # Line added in candidate
                    result.append(line[1:])
                    i += 1
                    continue
                elif line.startswith(" "):
                    # Context line
                    result.append(line[1:])
                    orig_idx += 1
                    i += 1
                    continue
                else:
                    i += 1

            while orig_idx < len(orig_lines):
                result.append(orig_lines[orig_idx])
                orig_idx += 1

            return "".join(result)
        except Exception:
            return None

    def get_isolated_content(self, candidate_id: str, filename: str = "SKILL.md") -> Optional[str]:
        """Reads the content of a file in the candidate's isolated sandbox."""
        fp = os.path.join(self.get_sandbox_dir(candidate_id), filename)
        if os.path.isfile(fp):
            with open(fp, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def verify_production_untouched(self, candidate_data: Dict[str, Any]) -> bool:
        """
        Verifies that canonical production files have NOT been modified by the sandbox.
        """
        target_comp = candidate_data.get("target_component", "")
        src_path = os.path.join(self.base_dir, target_comp) if not os.path.isabs(target_comp) else target_comp
        if not os.path.isfile(src_path):
            return True

        # Check if parent version sha matches current sha
        parent_sha = candidate_data.get("parent_version")
        if parent_sha and len(parent_sha) == 64:
            curr_sha = compute_sha256(src_path)
            if curr_sha != parent_sha:
                raise ProductionIntegrityViolationError(
                    f"Production file '{src_path}' SHA-256 changed from parent {parent_sha[:12]} to {curr_sha[:12]}! "
                    f"Candidate sandbox operations must not touch production."
                )
        return True

    def cleanup_sandbox(self, candidate_id: str) -> bool:
        """Removes an isolated sandbox directory if no longer needed."""
        sbx_dir = self.get_sandbox_dir(candidate_id)
        if os.path.isdir(sbx_dir):
            shutil.rmtree(sbx_dir, ignore_errors=True)
            return True
        return False
