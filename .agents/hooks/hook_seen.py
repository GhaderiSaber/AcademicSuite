#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/hook_seen.py — Structured Hook Telemetry Emitter

Emits structured HOOK_SEEN telemetry to stderr:
HOOK_SEEN
tool=<tool>
agent=<agent if available>
timestamp=<timestamp>
"""

import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

_last_emitted = None


def extract_tool_name(payload: Dict[str, Any]) -> str:
    """Extracts tool name from diverse payload structures."""
    if not isinstance(payload, dict):
        return ""
    tool_call = payload.get("toolCall")
    if isinstance(tool_call, dict):
        name = tool_call.get("name")
        if name:
            return str(name).strip()
    elif isinstance(tool_call, str) and tool_call.strip():
        return tool_call.strip()

    for k in ("tool", "tool_name", "toolName", "name"):
        val = payload.get(k)
        if val and isinstance(val, str) and val.strip():
            return val.strip()

    return ""


def extract_agent_name(payload: Dict[str, Any]) -> str:
    """Extracts agent name if available, otherwise returns empty string."""
    if not isinstance(payload, dict):
        return ""
    for k in ("agentName", "agentRole", "agent", "caller", "agent_type", "agentType"):
        val = payload.get(k)
        if val and isinstance(val, str) and val.strip():
            return val.strip()

    env_agent = os.environ.get("AGENT_NAME")
    if env_agent and env_agent.strip():
        return env_agent.strip()

    return ""


def extract_timestamp(payload: Dict[str, Any]) -> str:
    """Extracts timestamp from payload if present, otherwise generates ISO-8601 UTC."""
    if isinstance(payload, dict):
        for k in ("timestamp", "created_at", "createdAt", "time"):
            val = payload.get(k)
            if val and isinstance(val, str) and val.strip():
                return val.strip()

    return datetime.now(timezone.utc).isoformat()


def emit_hook_seen(payload: Dict[str, Any], event: str = "") -> str:
    """
    Emits HOOK_SEEN block to sys.stderr:
    HOOK_SEEN
    tool=<tool>
    agent=<agent if available>
    timestamp=<timestamp>
    """
    global _last_emitted
    if not isinstance(payload, dict):
        return ""

    if payload.get("_hook_seen_emitted"):
        return ""

    tool = extract_tool_name(payload)
    agent = extract_agent_name(payload)
    timestamp = extract_timestamp(payload)

    dedup_key = (tool, agent, timestamp)
    if _last_emitted == dedup_key:
        payload["_hook_seen_emitted"] = True
        return ""

    _last_emitted = dedup_key
    payload["_hook_seen_emitted"] = True

    msg = f"HOOK_SEEN\ntool={tool}\nagent={agent}\ntimestamp={timestamp}\n"
    sys.stderr.write(msg)
    sys.stderr.flush()
    return msg


if __name__ == "__main__":
    import json
    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception:
        pass
    emit_hook_seen(payload)
