#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/hook_identity_contract.py — Multi-Signal Hook Identity Contract & Resolution Engine

Authoritative SSOT for resolving caller identity, execution track, and security boundaries
from Antigravity lifecycle hook payloads.

Architectural Context:
- Antigravity lifecycle hooks receive payloads defined by docs/hooks.md.
- Official core fields: conversationId, workspacePaths, transcriptPath, artifactDirectoryPath, modelName, toolCall.
- Identity extension fields: agentName, agentRole, track, mode, isSubagent, parentConversationId.
- Dual-Track Architecture:
  * Track 1 (Built-In Main Developer Agent): Software engineering, testing, refactoring. Exempt from academic stop-gates.
  * Track 2 (Academic Orchestrator & Specialist Subagents): Academic thesis, data, stats pipelines. Bound to capability contracts.
- SECURITY INVARIANT (Fail-Closed Authorization):
  Unvetted, missing, or unprovable identity signals MUST strictly resolve to is_main_developer = False.
"""

import os
import sys
import json
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, Set

CONTRACTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CONTRACTS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(CONTRACTS_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
if CONTRACTS_DIR not in sys.path:
    sys.path.insert(0, CONTRACTS_DIR)

try:
    from contracts.contract_validator import validate_payload_against_schema
except ImportError:
    try:
        from .contract_validator import validate_payload_against_schema
    except ImportError:
        validate_payload_against_schema = None


@dataclass(frozen=True)
class HookIdentity:
    """Resolved identity profile for an Antigravity hook invocation."""
    agent_name: str
    agent_role: str
    track: str                     # "track_1_developer", "track_2_academic", "unknown"
    is_main_developer: bool        # True only if affirmatively proven to be Track 1 Main Developer
    is_subagent: bool
    parent_conversation_id: Optional[str]
    interface: str                 # "cli", "ide", "desktop_or_web", "unknown"
    confidence: str                # "high", "moderate", "low", "fail_closed_default"
    resolution_source: str         # "explicit_payload", "environment_variable", "transcript_analysis", "path_signature", "fail_closed_default"
    details: Dict[str, Any] = field(default_factory=dict)


def get_canonical_academic_agents() -> Set[str]:
    """Dynamically loads all canonical agent names from the capability policy SSOT."""
    try:
        from contracts.agents.capability_policy import get_all_policy_agents
        return set(get_all_policy_agents())
    except Exception:
        try:
            from .agents.capability_policy import get_all_policy_agents
            return set(get_all_policy_agents())
        except Exception:
            return {
                "academic-orchestrator", "research-agent", "data-agent",
                "statistics-agent", "academic-writer", "validation-agent",
                "digital-saber", "methodology-expert", "statistical-expert",
                "statistical-auditor", "results-auditor", "academic-challenger",
                "literature-expert", "evidence-auditor", "final-judge",
                "psychometric-expert", "qualitative-analyst", "meta-analyst",
                "journal-strategist", "intervention-designer", "data-curator",
                "project-organizer", "longitudinal-modmed-expert", "behavior-analyst", "curriculum-builder",
                "evaluation-agent", "knowledge-curator", "skill-evolver",
                "trajectory-analyzer", "test-orchestrator", "test-worker"
            }


SURFACE_APP_DATA_DIRS = {
    "desktop_or_web": os.path.expanduser("~/.gemini/antigravity"),
    "cli": os.path.expanduser("~/.gemini/antigravity-cli"),
    "ide": os.path.expanduser("~/.gemini/antigravity-ide"),
}


def detect_interface(payload: Dict[str, Any], env: Optional[Dict[str, str]] = None) -> str:
    """
    Detects the Antigravity product/runtime interface based on path signatures
    and environment variables (antigravity-cli, antigravity-ide, antigravity).
    """
    active_env = os.environ if env is None else env
    env_surface = (
        active_env.get("ANTIGRAVITY_SURFACE")
        or active_env.get("ANTIGRAVITY_CLIENT")
        or active_env.get("ANTIGRAVITY_INTERFACE")
        or ""
    ).lower().strip()
    if env_surface in ("cli", "antigravity-cli"):
        return "cli"
    if env_surface in ("ide", "antigravity-ide"):
        return "ide"
    if env_surface in ("desktop", "web", "antigravity", "desktop_or_web"):
        return "desktop_or_web"

    candidate_paths = []
    for key in ("transcriptPath", "artifactDirectoryPath"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            candidate_paths.append(val.lower())
    for ws in payload.get("workspacePaths", []):
        if isinstance(ws, str) and ws.strip():
            candidate_paths.append(ws.lower())

    for path in candidate_paths:
        if "antigravity-cli" in path:
            return "cli"
        if "antigravity-ide" in path:
            return "ide"
        if "antigravity" in path:
            return "desktop_or_web"

    return "unknown"


def resolve_transcript_path(payload: Dict[str, Any], env: Optional[Dict[str, str]] = None) -> Optional[str]:
    """
    Authoritatively resolves the transcript path for an Antigravity hook event.

    ROBUST ARCHITECTURAL INVARIANT:
    1. If `transcriptPath` is provided directly by runtime payload, USE IT DIRECTLY.
       Never alter, redirect, or override it.
    2. If and ONLY IF `transcriptPath` is genuinely absent, empty, or None:
       Fall back to an explicitly surface-aware resolution mechanism:
       a. Derive from `artifactDirectoryPath` if present:
          {artifactDirectoryPath}/.system_generated/logs/transcript.jsonl
       b. Check explicit environment variable app data directory overrides:
          ANTIGRAVITY_APP_DATA_DIR / ANTIGRAVITY_DATA_DIR / ANTIGRAVITY_APP_DIR
       c. Check surface-specific app data directory corresponding to detected interface:
          - CLI: ~/.gemini/antigravity-cli/brain/{cid}/.system_generated/logs/transcript.jsonl
          - IDE: ~/.gemini/antigravity-ide/brain/{cid}/.system_generated/logs/transcript.jsonl
          - Desktop/Web: ~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl
       d. Search across all known surface directories for an existing transcript file.
       e. Return surface-derived candidate path if conversationId is known.
    """
    if not isinstance(payload, dict):
        return None

    # Step 1: Use runtime transcriptPath directly if provided
    raw_path = payload.get("transcriptPath")
    if raw_path and isinstance(raw_path, str) and raw_path.strip():
        return os.path.expanduser(raw_path.strip())

    active_env = os.environ if env is None else env
    cid = payload.get("conversationId")
    if isinstance(cid, str):
        cid = cid.strip()
    else:
        cid = None

    # Step 2a: Derive from artifactDirectoryPath if present
    artifact_cand = None
    artifact_dir = payload.get("artifactDirectoryPath")
    if artifact_dir and isinstance(artifact_dir, str) and artifact_dir.strip():
        clean_artifact_dir = os.path.expanduser(artifact_dir.strip())
        artifact_cand = os.path.join(clean_artifact_dir, ".system_generated", "logs", "transcript.jsonl")
        if os.path.isfile(artifact_cand) or not cid:
            return artifact_cand

    # Step 2b: Check environment variable overrides
    env_app_dir = (
        active_env.get("ANTIGRAVITY_APP_DATA_DIR")
        or active_env.get("ANTIGRAVITY_DATA_DIR")
        or active_env.get("ANTIGRAVITY_APP_DIR")
    )
    if env_app_dir and cid:
        clean_env_dir = os.path.expanduser(env_app_dir.strip())
        cand = os.path.join(clean_env_dir, "brain", cid, ".system_generated", "logs", "transcript.jsonl")
        if os.path.isfile(cand):
            return cand

    if not cid:
        return artifact_cand

    # Step 2c: Surface-aware candidate resolution
    interface = detect_interface(payload, env=active_env)

    # Priority order based on detected interface
    surface_order = []
    if interface in SURFACE_APP_DATA_DIRS:
        surface_order.append(interface)
    for s in ("desktop_or_web", "cli", "ide"):
        if s not in surface_order:
            surface_order.append(s)

    # First pass: check if transcript file physically exists on disk in any surface
    for surf in surface_order:
        base_dir = SURFACE_APP_DATA_DIRS[surf]
        cand = os.path.join(base_dir, "brain", cid, ".system_generated", "logs", "transcript.jsonl")
        if os.path.isfile(cand):
            return cand

    # Second pass: if none exist on disk, return artifact candidate if available, else primary surface
    if artifact_cand:
        return artifact_cand
    primary_surf = surface_order[0]
    return os.path.join(SURFACE_APP_DATA_DIRS[primary_surf], "brain", cid, ".system_generated", "logs", "transcript.jsonl")


def extract_subagent_info(payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Determines whether the payload is executing within a subagent thread."""
    if not isinstance(payload, dict):
        return False, None

    parent_id = payload.get("parentConversationId")
    if parent_id and isinstance(parent_id, str) and parent_id.strip():
        return True, parent_id.strip()

    parent_ids = payload.get("parentConversationIds")
    if isinstance(parent_ids, list) and len(parent_ids) > 0:
        return True, str(parent_ids[0])

    if payload.get("isSubagent") is True or payload.get("subagent") is True:
        return True, parent_id

    subagent_depth = payload.get("subagentDepth") or payload.get("depth")
    if isinstance(subagent_depth, int) and subagent_depth > 0:
        return True, parent_id

    return False, None


def inspect_transcript_for_identity(transcript_path: str) -> Optional[Tuple[str, str, str]]:
    """
    Safely inspects a transcript file on disk to determine caller identity.
    Returns (agent_name, track, confidence) if conclusive, else None.
    """
    if not transcript_path:
        return None

    target_path = transcript_path
    if os.path.basename(transcript_path) == "transcript.jsonl":
        full_cand = os.path.join(os.path.dirname(transcript_path), "transcript_full.jsonl")
        if os.path.isfile(full_cand) and os.path.getsize(full_cand) > 0:
            target_path = full_cand

    if not os.path.isfile(target_path):
        return None

    try:
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            return None

        # Pass 1: Check identity block in early steps (first 30 lines)
        for line_str in lines[:30]:
            try:
                step = json.loads(line_str)
                content = step.get("content") or ""
                if "<identity>" in content:
                    id_match = re.search(r"<identity>([\s\S]*?)</identity>", content)
                    if id_match:
                        id_text = id_match.group(1)
                        if "You are Antigravity, a powerful agentic AI coding assistant" in id_text:
                            return "default", "track_1_developer", "high"
                        if "academic-orchestrator" in id_text or "Master Academic Orchestrator" in id_text:
                            return "academic-orchestrator", "track_2_academic", "high"
                        if "digital-saber" in id_text:
                            return "digital-saber", "track_2_academic", "high"
            except Exception:
                continue

        # Pass 2: Behavioral pattern scan across transcript
        # If the agent has recently called developer execution tools (run_command, replace_file_content, write_to_file),
        # it is affirmatively the Track 1 Main Developer Agent (Directive 20 forbids orchestrator from these tools).
        has_developer_tool_call = False
        has_orchestrator_signature = False

        academic_orchestrator_signatures = (
            "### 🛫 Pre-Flight Pipeline Declaration",
            "Contractual Delegation Envelope (CDE)",
            "academic-state/routing_plan.json"
        )

        for line_str in reversed(lines[-50:]):
            try:
                step = json.loads(line_str)
                # Inspect tool calls
                for tc in step.get("tool_calls", []):
                    tc_name = (tc.get("name") or "").lower()
                    if tc_name in ("run_command", "replace_file_content", "write_to_file", "edit_file", "apply_diff"):
                        has_developer_tool_call = True
                    elif tc_name == "invoke_subagent":
                        tc_args = tc.get("args", {})
                        subs = tc_args.get("Subagents", [])
                        if isinstance(subs, str):
                            try:
                                subs = json.loads(subs, strict=False)
                            except Exception:
                                subs = []
                        if isinstance(subs, list):
                            for s in subs:
                                if isinstance(s, dict):
                                    t_name = (s.get("TypeName") or "").lower()
                                    if t_name in (
                                        "academic-writer", "statistics-agent", "data-agent",
                                        "psychometric-expert", "results-auditor", "validation-agent"
                                    ):
                                        return "academic-orchestrator", "track_2_academic", "high"

                # Only inspect model output content (NEVER thinking or user inputs)
                if step.get("source") == "MODEL" and step.get("type") == "PLANNER_RESPONSE":
                    content = str(step.get("content") or "")
                    if any(pat in content for pat in academic_orchestrator_signatures):
                        has_orchestrator_signature = True
            except Exception:
                continue

        if has_developer_tool_call:
            return "default", "track_1_developer", "high"
        if has_orchestrator_signature:
            return "academic-orchestrator", "track_2_academic", "high"
    except Exception:
        return None

    return None


def resolve_hook_identity(payload: Dict[str, Any], env: Optional[Dict[str, str]] = None) -> HookIdentity:
    """
    Authoritatively resolves caller identity, track, and developer status
    using a multi-signal hierarchy with fail-closed defaults.

    Precedence Hierarchy:
    1. Explicit Payload Identity Fields (track, mode, agentName, isSubagent)
    2. Environment Variables (ANTIGRAVITY_AGENT_NAME, ANTIGRAVITY_TRACK, ANTIGRAVITY_MODE)
    3. Transcript Analysis (Physical transcript inspection on disk)
    4. Product / Interface Signature
    5. Fail-Closed Default (Non-developer, governed track)
    """
    if not isinstance(payload, dict):
        return HookIdentity(
            agent_name="unknown",
            agent_role="unknown",
            track="unknown",
            is_main_developer=False,
            is_subagent=False,
            parent_conversation_id=None,
            interface="unknown",
            confidence="fail_closed_default",
            resolution_source="fail_closed_default",
            details={"error": "Payload is not a dictionary"}
        )

    interface = detect_interface(payload)
    is_subagent, parent_id = extract_subagent_info(payload)
    canonical_agents = get_canonical_academic_agents()

    # -------------------------------------------------------------
    # Signal 1: Explicit Payload Identity Fields
    # -------------------------------------------------------------
    explicit_track = payload.get("track")
    explicit_mode = str(payload.get("mode") or "").lower().strip()
    agent_name_raw = (
        payload.get("agentName") or
        payload.get("agentRole") or
        payload.get("agent") or
        payload.get("caller") or
        ""
    ).strip()
    agent_name_lower = agent_name_raw.lower()

    # Check for canonical academic agents first (never developer)
    if agent_name_lower:
        for ac in canonical_agents:
            if ac == agent_name_lower or ac in agent_name_lower:
                role = "orchestrator" if ac == "academic-orchestrator" else "specialist_worker"
                return HookIdentity(
                    agent_name=ac,
                    agent_role=str(payload.get("agentRole") or role),
                    track="track_2_academic",
                    is_main_developer=False,
                    is_subagent=is_subagent,
                    parent_conversation_id=parent_id,
                    interface=interface,
                    confidence="high",
                    resolution_source="explicit_payload",
                    details={"matched_canonical_agent": ac}
                )

        academic_keywords = ("orchestrator", "auditor", "expert", "challenger", "judge")
        if any(k in agent_name_lower for k in academic_keywords):
            return HookIdentity(
                agent_name=agent_name_raw,
                agent_role=str(payload.get("agentRole") or "academic_agent"),
                track="track_2_academic",
                is_main_developer=False,
                is_subagent=is_subagent,
                parent_conversation_id=parent_id,
                interface=interface,
                confidence="high",
                resolution_source="explicit_payload",
                details={"matched_academic_keyword": True}
            )

    # If payload explicitly states track 2 or academic mode
    if explicit_track in (2, "2", "track_2", "academic") or explicit_mode == "academic":
        return HookIdentity(
            agent_name=agent_name_raw or "academic-agent",
            agent_role=str(payload.get("agentRole") or "academic"),
            track="track_2_academic",
            is_main_developer=False,
            is_subagent=is_subagent,
            parent_conversation_id=parent_id,
            interface=interface,
            confidence="high",
            resolution_source="explicit_payload",
            details={"explicit_track": explicit_track, "explicit_mode": explicit_mode}
        )

    # If payload explicitly states track 1 or developer mode
    if (explicit_track in (1, "1", "track_1", "developer") or
            explicit_mode == "developer" or
            payload.get("agent_type") == "main"):
        # Subagents are never the root main agent developer
        if is_subagent:
            return HookIdentity(
                agent_name=agent_name_raw or "subagent-developer",
                agent_role=str(payload.get("agentRole") or "subagent"),
                track="track_1_developer",
                is_main_developer=False,
                is_subagent=True,
                parent_conversation_id=parent_id,
                interface=interface,
                confidence="high",
                resolution_source="explicit_payload",
                details={"subagent_blocked_from_main_exemption": True}
            )
        return HookIdentity(
            agent_name=agent_name_raw or "default",
            agent_role=str(payload.get("agentRole") or "developer"),
            track="track_1_developer",
            is_main_developer=True,
            is_subagent=False,
            parent_conversation_id=None,
            interface=interface,
            confidence="high",
            resolution_source="explicit_payload",
            details={"explicit_track": explicit_track, "explicit_mode": explicit_mode}
        )

    # Check for explicit main developer caller keywords
    main_developer_indicators = (
        "main", "main-agent", "mainagent", "default",
        "antigravity", "developer", "coding", "software-engineer",
        "code-agent", "cli-developer", "ide-developer"
    )
    if agent_name_lower and any(ind == agent_name_lower or ind in agent_name_lower for ind in main_developer_indicators):
        if not is_subagent:
            return HookIdentity(
                agent_name=agent_name_raw,
                agent_role=str(payload.get("agentRole") or "developer"),
                track="track_1_developer",
                is_main_developer=True,
                is_subagent=False,
                parent_conversation_id=None,
                interface=interface,
                confidence="high",
                resolution_source="explicit_payload",
                details={"matched_main_indicator": agent_name_lower}
            )

    # -------------------------------------------------------------
    # Signal 2: Environment Variables
    # -------------------------------------------------------------
    active_env = os.environ if env is None else env
    env_track = active_env.get("ANTIGRAVITY_TRACK") or active_env.get("TRACK")
    env_mode = (active_env.get("ANTIGRAVITY_MODE") or active_env.get("MODE") or "").lower().strip()
    env_agent = (active_env.get("ANTIGRAVITY_AGENT_NAME") or active_env.get("AGENT_NAME") or "").strip()

    if env_agent:
        env_agent_lower = env_agent.lower()
        if env_agent_lower in canonical_agents or any(k in env_agent_lower for k in ("orchestrator", "auditor", "expert")):
            return HookIdentity(
                agent_name=env_agent,
                agent_role="academic_agent",
                track="track_2_academic",
                is_main_developer=False,
                is_subagent=is_subagent,
                parent_conversation_id=parent_id,
                interface=interface,
                confidence="high",
                resolution_source="environment_variable",
                details={"env_agent": env_agent}
            )
        if any(ind in env_agent_lower for ind in main_developer_indicators) and not is_subagent:
            return HookIdentity(
                agent_name=env_agent,
                agent_role="developer",
                track="track_1_developer",
                is_main_developer=True,
                is_subagent=False,
                parent_conversation_id=None,
                interface=interface,
                confidence="high",
                resolution_source="environment_variable",
                details={"env_agent": env_agent}
            )

    if env_track in ("1", "developer") or env_mode == "developer":
        if not is_subagent:
            return HookIdentity(
                agent_name="default",
                agent_role="developer",
                track="track_1_developer",
                is_main_developer=True,
                is_subagent=False,
                parent_conversation_id=None,
                interface=interface,
                confidence="high",
                resolution_source="environment_variable",
                details={"env_track": env_track, "env_mode": env_mode}
            )

    if env_track in ("2", "academic") or env_mode == "academic":
        return HookIdentity(
            agent_name="academic-agent",
            agent_role="academic",
            track="track_2_academic",
            is_main_developer=False,
            is_subagent=is_subagent,
            parent_conversation_id=parent_id,
            interface=interface,
            confidence="high",
            resolution_source="environment_variable",
            details={"env_track": env_track, "env_mode": env_mode}
        )

    # -------------------------------------------------------------
    # Signal 3: Transcript Inspection
    # -------------------------------------------------------------
    transcript_path = resolve_transcript_path(payload, env=active_env)
    if transcript_path and isinstance(transcript_path, str):
        transcript_res = inspect_transcript_for_identity(transcript_path)
        if transcript_res:
            res_name, res_track, res_conf = transcript_res
            is_dev = (res_track == "track_1_developer" and not is_subagent)
            return HookIdentity(
                agent_name=res_name,
                agent_role="developer" if is_dev else "academic",
                track=res_track,
                is_main_developer=is_dev,
                is_subagent=is_subagent,
                parent_conversation_id=parent_id,
                interface=interface,
                confidence=res_conf,
                resolution_source="transcript_analysis",
                details={"inspected_transcript": transcript_path}
            )

    # -------------------------------------------------------------
    # Signal 3.5: Contextual Academic Workspace & Delegation Signature
    # -------------------------------------------------------------
    if not is_subagent:
        tool_call = payload.get("toolCall", {})
        tool_name = (tool_call.get("name") or "").strip().lower()
        if tool_name == "invoke_subagent":
            args = tool_call.get("args", {})
            subs = args.get("Subagents", [])
            if isinstance(subs, str):
                try:
                    subs = json.loads(subs, strict=False)
                except Exception:
                    subs = []
            if isinstance(subs, list):
                for s in subs:
                    if isinstance(s, dict):
                        t_name = (s.get("TypeName") or "").lower()
                        if t_name in canonical_agents or "academic" in t_name or "stat" in t_name:
                            return HookIdentity(
                                agent_name="academic-orchestrator",
                                agent_role="orchestrator",
                                track="track_2_academic",
                                is_main_developer=False,
                                is_subagent=False,
                                parent_conversation_id=None,
                                interface=interface,
                                confidence="high",
                                resolution_source="tool_call_signature",
                                details={"target_worker": t_name}
                            )


    # -------------------------------------------------------------
    # Signal 4: Fail-Closed Default
    # -------------------------------------------------------------
    return HookIdentity(
        agent_name="unknown",
        agent_role="unknown",
        track="unknown",
        is_main_developer=False,
        is_subagent=is_subagent,
        parent_conversation_id=parent_id,
        interface=interface,
        confidence="fail_closed_default",
        resolution_source="fail_closed_default",
        details={
            "reason": "No explicit, environment, or transcript identity signal established Track 1 status."
        }
    )


def validate_hook_payload_schema(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validates hook payload against the authoritative hook_payload contract schema."""
    if validate_payload_against_schema is None:
        # Fallback if validator unavailable
        required = ["conversationId", "workspacePaths"]
        missing = [r for r in required if r not in payload]
        if missing:
            return False, [f"Missing required fields: {missing}"]
        return True, []

    return validate_payload_against_schema(payload, "hook_payload")


def is_main_agent_developer(payload: Dict[str, Any]) -> bool:
    """Convenience helper delegating to the authoritative resolve_hook_identity engine."""
    return resolve_hook_identity(payload).is_main_developer
