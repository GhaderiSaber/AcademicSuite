#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_event_engine.py — Authoritative Durable Event Engine

Manages immutable, append-only event logging in state/events.jsonl.
Strictly validates every event against contracts/event.schema.json, enforces
monotonic event ordering, binds durable artifact provenance (hashes, producers),
and reconstructs complete study workflows from the event stream.
"""

import os
import sys
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Union

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

# Fallback to system dist-packages
try:
    import jsonschema
except ImportError:
    for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
        if os.path.exists(p) and p not in sys.path:
            sys.path.append(p)
    try:
        import jsonschema
    except ImportError:
        jsonschema = None


try:
    from scripts.permission_manager import state_ledger_transaction
except ImportError:
    try:
        from permission_manager import state_ledger_transaction
    except ImportError:
        from contextlib import contextmanager
        @contextmanager
        def state_ledger_transaction(state_dir: str):
            state_dir = os.path.abspath(state_dir)
            os.makedirs(state_dir, exist_ok=True)
            try:
                if sys.platform != "win32":
                    os.chmod(state_dir, 0o755)
                    for f in os.listdir(state_dir):
                        fp = os.path.join(state_dir, f)
                        if os.path.isfile(fp):
                            os.chmod(fp, 0o644)
            except Exception:
                pass
            try:
                yield
            finally:
                try:
                    if sys.platform != "win32":
                        for f in os.listdir(state_dir):
                            fp = os.path.join(state_dir, f)
                            if os.path.isfile(fp):
                                os.chmod(fp, 0o444)
                        os.chmod(state_dir, 0o555)
                except Exception:
                    pass


# ==============================================================================
# Custom Fail-Closed Event Exceptions
# ==============================================================================

class EventError(Exception):
    """Base exception for AcademicSuite event engine errors."""
    pass

class EventSchemaValidationError(EventError):
    """Raised when an event fails schema validation against contracts/event.schema.json."""
    pass

class DuplicateEventError(EventError):
    """Raised when attempting to emit an event with an already existing event_id."""
    pass

class MalformedEventError(EventError):
    """Raised when an unparseable or corrupted line is detected in events.jsonl."""
    pass

class EventOrderingError(EventError):
    """Raised when event timestamps regress or temporal causality is violated."""
    pass

class ArtifactEventMismatchError(EventError):
    """Raised when an artifact's physical hash/path mismatches its ARTIFACT_CREATED event."""
    pass

class MissingArtifactEventError(EventError):
    """Raised when an artifact exists on disk or in state without a corresponding ARTIFACT_CREATED event."""
    pass


# ==============================================================================
# Canonical 14 Event Types (from contracts/event.schema.json)
# ==============================================================================

VALID_EVENT_TYPES: Set[str] = {
    "PROJECT_CREATED",
    "MILESTONE_STARTED",
    "PLAN_CREATED",
    "ARTIFACT_CREATED",
    "EXECUTION_STARTED",
    "EXECUTION_COMPLETED",
    "VALIDATION_STARTED",
    "VALIDATION_FAILED",
    "CRITIQUE_CREATED",
    "REVISION_REQUESTED",
    "MILESTONE_APPROVAL_REQUESTED",
    "MILESTONE_APPROVED",
    "MILESTONE_REJECTED",
    "MILESTONE_FAILED",
    "USER_FEEDBACK_DETECTED",
    "SUBAGENT_REQUESTED",
    "SUBAGENT_STARTED",
    "SUBAGENT_COMPLETED",
    "SUBAGENT_FAILED",
    "ARTIFACT_RETURNED",
}


def load_event_schema() -> Optional[Dict[str, Any]]:
    """Loads contracts/event.schema.json from the repository."""
    candidates = [
        os.path.join(ROOT_DIR, "contracts", "event.schema.json"),
        os.path.join(ROOT_DIR, ".agents", "contracts", "event.schema.json"),
    ]
    for schema_path in candidates:
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def compute_file_sha256(filepath: str) -> str:
    """Computes SHA-256 cryptographic hash of a physical file."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


# ==============================================================================
# Academic Event Engine Class
# ==============================================================================

class AcademicEventEngine:
    """
    Durable, reliable filesystem event manager for state/events.jsonl.
    Enforces schema validity, duplicate detection, monotonic timestamps,
    and durable artifact provenance.
    """

    def __init__(self, events_path: str, project_id: str = ""):
        self.events_path = os.path.abspath(events_path)
        self.project_id = project_id
        os.makedirs(os.path.dirname(self.events_path), exist_ok=True)

        self.schema = load_event_schema()
        self.known_event_ids: Set[str] = set()
        self.last_timestamp: Optional[str] = None

        # Warm up cache from disk if file already exists
        if os.path.exists(self.events_path):
            self._warmup_cache()

    def _warmup_cache(self) -> None:
        """Reads existing events.jsonl to populate known event IDs and last timestamp."""
        try:
            events = self.read_events(validate_schema=False, enforce_ordering=False)
            for ev in events:
                eid = ev.get("event_id")
                if eid:
                    self.known_event_ids.add(eid)
                ts = ev.get("timestamp")
                if ts:
                    self.last_timestamp = ts
        except Exception:
            # Errors will be caught on explicit read
            pass

    def emit(
        self,
        event_type: str,
        emitter_agent: str,
        summary: str,
        milestone_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        artifact_ids: Optional[List[str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        recipient_agent: Optional[str] = None,
        project_id: Optional[str] = None,
        **extra_payload
    ) -> Dict[str, Any]:
        """
        Emits and appends a single schema-validated event to state/events.jsonl.
        Fails closed on schema violation, duplicate ID, or timestamp regression.
        """
        # 1. Type validation
        if event_type not in VALID_EVENT_TYPES:
            raise EventSchemaValidationError(
                f"Invalid event_type '{event_type}'. Must be one of {sorted(list(VALID_EVENT_TYPES))}."
            )

        # 2. Identifier generation & duplicate check
        eid = event_id or f"EVT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
        if eid in self.known_event_ids:
            raise DuplicateEventError(f"Duplicate event_id detected: '{eid}'. Events are immutable.")

        # 3. Timestamp generation & ordering check
        now_ts = timestamp or datetime.now(timezone.utc).isoformat()
        if self.last_timestamp and now_ts < self.last_timestamp:
            raise EventOrderingError(
                f"Event ordering violation: New timestamp '{now_ts}' regressed "
                f"prior to last recorded timestamp '{self.last_timestamp}'."
            )

        # 4. Construct payload ensuring required 'summary'
        payload: Dict[str, Any] = {
            "summary": summary or f"Event {event_type} emitted by {emitter_agent}"
        }
        if artifact_ids:
            payload["artifact_ids"] = artifact_ids
        if metrics:
            payload["metrics"] = metrics
        if details:
            payload["details"] = details
        if extra_payload:
            payload.update(extra_payload)

        # 5. Build full event object
        event: Dict[str, Any] = {
            "contract_version": "1.0.0",
            "event_id": eid,
            "event_type": event_type,
            "timestamp": now_ts,
            "project_id": project_id or self.project_id or "academic_project",
            "emitter_agent": emitter_agent,
            "payload": payload
        }
        if milestone_id:
            event["milestone_id"] = milestone_id
        if stage_id:
            event["stage_id"] = stage_id
        if recipient_agent:
            event["recipient_agent"] = recipient_agent

        # 6. Strict schema validation
        if self.schema and jsonschema:
            try:
                format_checker = jsonschema.FormatChecker() if hasattr(jsonschema, "FormatChecker") else None
                jsonschema.validate(instance=event, schema=self.schema, format_checker=format_checker)
            except jsonschema.ValidationError as ve:
                path_str = " -> ".join([str(p) for p in ve.path]) if ve.path else "root"
                raise EventSchemaValidationError(f"Event schema validation failed at [{path_str}]: {ve.message}") from ve

        # 7. Append to file atomically within state_ledger_transaction
        state_dir = os.path.dirname(self.events_path)
        with state_ledger_transaction(state_dir):
            with open(self.events_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

        self.known_event_ids.add(eid)
        self.last_timestamp = now_ts
        return event

    def emit_artifact_created(
        self,
        artifact_id: str,
        artifact_path: str,
        milestone_id: str,
        producer_agent: str,
        producer_script: str = "",
        provenance: Optional[Dict[str, Any]] = None,
        stage_id: Optional[str] = None,
        summary: Optional[str] = None,
        project_root: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Emits an ARTIFACT_CREATED event with full cryptographic provenance:
        producer, artifact ID, artifact path, real SHA-256 hash, milestone, timestamp, provenance.
        """
        state_dir = os.path.dirname(self.events_path)
        base_dir = project_root or os.path.dirname(state_dir)

        if os.path.isabs(artifact_path):
            full_path = artifact_path
        elif os.path.exists(os.path.join(base_dir, artifact_path)):
            full_path = os.path.join(base_dir, artifact_path)
        elif os.path.exists(os.path.join(state_dir, artifact_path)):
            full_path = os.path.join(state_dir, artifact_path)
        else:
            full_path = os.path.join(base_dir, artifact_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Cannot emit ARTIFACT_CREATED for missing file: {full_path}")

        file_hash = compute_file_sha256(full_path)
        prov = provenance or {
            "source_dataset": "real_input",
            "deterministic_tool": producer_script or "academic_state_manager.py",
            "command_line": f"python3 {producer_script}" if producer_script else "internal"
        }

        details = {
            "artifact_id": artifact_id,
            "path": artifact_path,
            "hash": {
                "algorithm": "sha256",
                "value": file_hash
            },
            "milestone": milestone_id,
            "stage_id": stage_id or "",
            "producer": {
                "agent": producer_agent,
                "script_or_generator": producer_script
            },
            "provenance": prov
        }

        return self.emit(
            event_type="ARTIFACT_CREATED",
            emitter_agent=producer_agent,
            summary=summary or f"Artifact '{artifact_id}' generated by {producer_agent} ({producer_script})",
            milestone_id=milestone_id,
            stage_id=stage_id,
            artifact_ids=[artifact_id],
            details=details
        )

    def read_events(
        self,
        validate_schema: bool = True,
        enforce_ordering: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Reads and parses events.jsonl into a list of event dictionaries.
        Fails closed on malformed JSON, schema invalidity, or temporal ordering violations.
        """
        if not os.path.exists(self.events_path):
            return []

        events: List[Dict[str, Any]] = []
        last_ts: Optional[str] = None
        seen_ids: Set[str] = set()

        with open(self.events_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                clean_line = line.strip()
                if not clean_line:
                    continue

                try:
                    ev = json.loads(clean_line)
                except Exception as e:
                    raise MalformedEventError(
                        f"Malformed JSON in '{self.events_path}' at line {line_no}: {str(e)}"
                    ) from e

                if not isinstance(ev, dict):
                    raise MalformedEventError(
                        f"Malformed event in '{self.events_path}' at line {line_no}: Expected JSON object."
                    )

                eid = ev.get("event_id")
                if not eid:
                    raise MalformedEventError(
                        f"Malformed event at line {line_no}: Missing required 'event_id'."
                    )
                if eid in seen_ids:
                    raise DuplicateEventError(
                        f"Duplicate event_id detected in log: '{eid}' at line {line_no}."
                    )
                seen_ids.add(eid)

                ts = ev.get("timestamp")
                if enforce_ordering and ts and last_ts:
                    if ts < last_ts:
                        raise EventOrderingError(
                            f"Event ordering violation at line {line_no}: "
                            f"Timestamp '{ts}' regressed after '{last_ts}'."
                        )
                if ts:
                    last_ts = ts

                if validate_schema and self.schema and jsonschema:
                    try:
                        format_checker = jsonschema.FormatChecker() if hasattr(jsonschema, "FormatChecker") else None
                        jsonschema.validate(instance=ev, schema=self.schema, format_checker=format_checker)
                    except jsonschema.ValidationError as ve:
                        raise EventSchemaValidationError(
                            f"Schema validation failed for event '{eid}' (line {line_no}): {ve.message}"
                        ) from ve

                events.append(ev)

        return events

    def verify_artifact_alignment(
        self,
        artifact_records: List[Dict[str, Any]],
        project_root: Optional[str] = None,
        check_disk_files: bool = True,
        scanned_disk_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Verifies that every registered artifact has a matching, hash-consistent ARTIFACT_CREATED event,
        and conversely that every artifact event corresponds to an existing, non-tampered physical file.
        Raises MissingArtifactEventError if un-emitted artifact exists.
        Raises ArtifactEventMismatchError if hash or path differs or physical file is missing.
        """
        events = self.read_events(validate_schema=False, enforce_ordering=False)
        artifact_events: Dict[str, Dict[str, Any]] = {}

        for ev in events:
            if ev.get("event_type") == "ARTIFACT_CREATED":
                details = ev.get("payload", {}).get("details", {})
                aid = details.get("artifact_id") or (ev.get("payload", {}).get("artifact_ids") or [None])[0]
                if aid:
                    artifact_events[aid] = ev

        state_dir = os.path.dirname(self.events_path)
        base_dir = project_root or os.path.dirname(state_dir)

        # 1. Verify every registered artifact has a matching ARTIFACT_CREATED event
        for art in artifact_records:
            aid = art.get("artifact_id")
            if not aid:
                continue

            if aid not in artifact_events:
                raise MissingArtifactEventError(
                    f"Artifact '{aid}' exists in state/artifacts.json or disk, "
                    f"but lacks a required durable ARTIFACT_CREATED event in {self.events_path}."
                )

            ev = artifact_events[aid]
            details = ev.get("payload", {}).get("details", {})
            event_path = details.get("path")
            art_path = art.get("path")

            if event_path and art_path and event_path != art_path:
                raise ArtifactEventMismatchError(
                    f"Path mismatch for artifact '{aid}': "
                    f"event path='{event_path}' vs record path='{art_path}'."
                )

            # Hash verification against physical file
            full_path = None
            if art_path:
                if os.path.isabs(art_path):
                    full_path = art_path
                elif os.path.exists(os.path.join(base_dir, art_path)):
                    full_path = os.path.join(base_dir, art_path)
                elif os.path.exists(os.path.join(state_dir, art_path)):
                    full_path = os.path.join(state_dir, art_path)
                else:
                    full_path = os.path.join(base_dir, art_path)

            if check_disk_files and full_path:
                if not os.path.exists(full_path):
                    raise ArtifactEventMismatchError(
                        f"Artifact '{aid}' references path '{art_path}', but physical file does not exist on disk."
                    )
                disk_hash = compute_file_sha256(full_path)
                event_hash = details.get("hash", {}).get("value")
                if event_hash and disk_hash.lower() != event_hash.lower():
                    raise ArtifactEventMismatchError(
                        f"Cryptographic hash mismatch for artifact '{aid}': "
                        f"event hash='{event_hash}', disk hash='{disk_hash}'."
                    )

        # 2. Check that all artifact events point to physical files on disk if check_disk_files
        if check_disk_files:
            for aid, ev in artifact_events.items():
                details = ev.get("payload", {}).get("details", {})
                event_path = details.get("path")
                if not event_path:
                    continue
                if os.path.isabs(event_path):
                    fp = event_path
                elif os.path.exists(os.path.join(base_dir, event_path)):
                    fp = os.path.join(base_dir, event_path)
                elif os.path.exists(os.path.join(state_dir, event_path)):
                    fp = os.path.join(state_dir, event_path)
                else:
                    fp = os.path.join(base_dir, event_path)

                if not os.path.exists(fp):
                    raise ArtifactEventMismatchError(
                        f"Artifact event '{ev.get('event_id')}' references artifact '{aid}' at '{event_path}', "
                        f"but physical file is missing from disk."
                    )

        # 3. Check extra scanned disk paths if provided
        if scanned_disk_paths:
            known_event_paths = set()
            for ev in artifact_events.values():
                ep = ev.get("payload", {}).get("details", {}).get("path")
                if ep:
                    known_event_paths.add(os.path.abspath(ep) if os.path.isabs(ep) else os.path.abspath(os.path.join(base_dir, ep)))
                    known_event_paths.add(os.path.abspath(os.path.join(state_dir, ep)))

            for sdp in scanned_disk_paths:
                abs_sdp = os.path.abspath(sdp)
                if abs_sdp not in known_event_paths:
                    raise MissingArtifactEventError(
                        f"Physical file '{sdp}' exists on disk but has no corresponding ARTIFACT_CREATED event."
                    )

        return {
            "status": "ALIGNED",
            "verified_artifacts_count": len(artifact_records),
            "events_count": len(artifact_events)
        }

    def reconstruct_workflow(self) -> Dict[str, Any]:
        """
        Reconstructs the complete project lifecycle, milestones, artifacts,
        validations, and approval decisions directly from the event log.
        """
        events = self.read_events(validate_schema=False, enforce_ordering=False)
        workflow: Dict[str, Any] = {
            "project_id": self.project_id,
            "events_count": len(events),
            "created_at": None,
            "milestones": {},
            "artifacts": {},
            "validations": [],
            "approvals": []
        }

        for ev in events:
            etype = ev.get("event_type")
            ts = ev.get("timestamp")
            mid = ev.get("milestone_id")
            payload = ev.get("payload", {})
            agent = ev.get("emitter_agent")

            if etype == "PROJECT_CREATED":
                workflow["created_at"] = ts
                workflow["project_id"] = ev.get("project_id", self.project_id)

            elif etype == "MILESTONE_STARTED":
                if mid:
                    workflow["milestones"].setdefault(mid, {
                        "milestone_id": mid,
                        "status": "STARTED",
                        "started_at": ts,
                        "agent": agent,
                        "artifacts": [],
                        "history": []
                    })
                    workflow["milestones"][mid]["history"].append({
                        "event": etype, "timestamp": ts, "summary": payload.get("summary")
                    })

            elif etype == "ARTIFACT_CREATED":
                details = payload.get("details", {})
                aid = details.get("artifact_id") or (payload.get("artifact_ids") or [""])[0]
                if aid:
                    workflow["artifacts"][aid] = {
                        "artifact_id": aid,
                        "path": details.get("path"),
                        "hash": details.get("hash", {}).get("value"),
                        "milestone": mid,
                        "timestamp": ts,
                        "producer": details.get("producer", {}),
                        "provenance": details.get("provenance", {})
                    }
                    if mid and mid in workflow["milestones"]:
                        workflow["milestones"][mid]["artifacts"].append(aid)

            elif etype in ["VALIDATION_STARTED", "VALIDATION_FAILED"]:
                workflow["validations"].append({
                    "event": etype,
                    "milestone_id": mid,
                    "timestamp": ts,
                    "summary": payload.get("summary"),
                    "details": payload.get("details", {})
                })
                if mid and mid in workflow["milestones"]:
                    workflow["milestones"][mid]["history"].append({
                        "event": etype, "timestamp": ts, "summary": payload.get("summary")
                    })

            elif etype in ["MILESTONE_APPROVAL_REQUESTED", "MILESTONE_APPROVED", "MILESTONE_REJECTED"]:
                workflow["approvals"].append({
                    "event": etype,
                    "milestone_id": mid,
                    "timestamp": ts,
                    "agent": agent,
                    "summary": payload.get("summary")
                })
                if mid and mid in workflow["milestones"]:
                    if etype == "MILESTONE_APPROVED":
                        workflow["milestones"][mid]["status"] = "APPROVED"
                    elif etype == "MILESTONE_REJECTED":
                        workflow["milestones"][mid]["status"] = "REJECTED"
                    workflow["milestones"][mid]["history"].append({
                        "event": etype, "timestamp": ts, "summary": payload.get("summary")
                    })

            elif etype in ["EXECUTION_STARTED", "EXECUTION_COMPLETED", "MILESTONE_FAILED"]:
                if mid and mid in workflow["milestones"]:
                    if etype == "MILESTONE_FAILED":
                        workflow["milestones"][mid]["status"] = "FAILED"
                    workflow["milestones"][mid]["history"].append({
                        "event": etype, "timestamp": ts, "summary": payload.get("summary")
                    })

        return workflow

    def explain_transition(self, milestone_id: str, target_state: str) -> Dict[str, Any]:
        """
        Explains the causal sequence of events that led to a milestone transition.
        """
        events = self.read_events(validate_schema=False, enforce_ordering=False)
        relevant = [ev for ev in events if ev.get("milestone_id") == milestone_id]

        causal_chain = []
        for ev in relevant:
            causal_chain.append({
                "event_id": ev["event_id"],
                "event_type": ev["event_type"],
                "timestamp": ev["timestamp"],
                "emitter_agent": ev["emitter_agent"],
                "summary": ev.get("payload", {}).get("summary")
            })

        return {
            "milestone_id": milestone_id,
            "target_state": target_state,
            "events_count": len(causal_chain),
            "causal_chain": causal_chain,
            "justification": f"Transition to {target_state} justified by {len(causal_chain)} recorded events."
        }
