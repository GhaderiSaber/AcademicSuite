#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/delegation_event_engine.py — Observable Subagent Delegation Engine

Authoritative telemetry engine for Phase 23, replacing speculative inference
("Probably statistics-agent was used") with strictly observable physical events:
- SUBAGENT_REQUESTED
- SUBAGENT_STARTED
- SUBAGENT_COMPLETED
- SUBAGENT_FAILED
- ARTIFACT_RETURNED

Records the 8 mandatory fields on every delegation event:
1. parent_agent
2. child_agent
3. task_id
4. timestamp
5. objective
6. input_artifacts
7. output_artifacts
8. status

Directly observes:
academic-orchestrator → invoke_subagent → statistics-agent
"""

import os
import sys
import json
import uuid
import argparse
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union

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

# Try jsonschema import
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


class DelegationEventType(str, Enum):
    """The 5 canonical delegation lifecycle event types."""
    SUBAGENT_REQUESTED = "SUBAGENT_REQUESTED"
    SUBAGENT_STARTED = "SUBAGENT_STARTED"
    SUBAGENT_COMPLETED = "SUBAGENT_COMPLETED"
    SUBAGENT_FAILED = "SUBAGENT_FAILED"
    ARTIFACT_RETURNED = "ARTIFACT_RETURNED"


class DelegationStatus(str, Enum):
    """Observable status of the child subagent at each lifecycle milestone."""
    REQUESTED = "REQUESTED"
    STARTED = "STARTED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETURNED = "RETURNED"
    BLOCKED = "BLOCKED"


class DelegationEventValidationError(Exception):
    """Raised when a delegation event fails schema validation."""
    pass


class UnobservedDelegationError(Exception):
    """Raised when delegation is claimed without physical observable telemetry."""
    pass


def load_delegation_event_schema() -> Optional[Dict[str, Any]]:
    """Loads contracts/delegation_event.schema.json."""
    schema_path = os.path.join(ROOT_DIR, "contracts", "delegation_event.schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


class DelegationEventEngine:
    """
    Core engine for observable subagent delegation event emission,
    validation, persistence, and chain reconstruction.
    """

    def __init__(self, state_dir: Optional[str] = None, project_root: Optional[str] = None):
        self.project_root = project_root or ROOT_DIR
        self.state_dir = state_dir or os.path.join(self.project_root, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.events_file = os.path.join(self.state_dir, "delegation_events.jsonl")
        self.schema = load_delegation_event_schema()

    def emit_delegation_event(
        self,
        event_type: Union[DelegationEventType, str],
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        status: Union[DelegationStatus, str],
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        output_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        sync_to_trajectory: bool = True
    ) -> Dict[str, Any]:
        """
        Emits and records a canonical delegation event enforcing the 8 mandatory fields:
        parent_agent, child_agent, task_id, timestamp, objective, input_artifacts,
        output_artifacts, status.
        """
        etype = event_type.value if isinstance(event_type, DelegationEventType) else str(event_type)
        stat = status.value if isinstance(status, DelegationStatus) else str(status)
        now_iso = timestamp or datetime.now(timezone.utc).isoformat()
        eid = event_id or f"EVT-DEL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        in_arts = input_artifacts or []
        out_arts = output_artifacts or []
        det = details or {}

        event_record = {
            "contract_version": "1.0.0",
            "event_id": eid,
            "event_type": etype,
            "parent_agent": str(parent_agent).strip(),
            "child_agent": str(child_agent).strip(),
            "task_id": str(task_id).strip(),
            "timestamp": now_iso,
            "objective": str(objective).strip(),
            "input_artifacts": in_arts,
            "output_artifacts": out_arts,
            "status": stat,
            "details": det
        }

        # Validate against schema if available
        if self.schema and jsonschema:
            try:
                jsonschema.validate(instance=event_record, schema=self.schema)
            except jsonschema.ValidationError as err:
                raise DelegationEventValidationError(
                    f"Delegation event validation failed against contracts/delegation_event.schema.json: {err.message}"
                )

        # Append to state/delegation_events.jsonl
        line = json.dumps(event_record, ensure_ascii=False) + "\n"
        with open(self.events_file, "a", encoding="utf-8") as f:
            f.write(line)

        # Sync to TrajectoryEngine if enabled
        if sync_to_trajectory:
            try:
                from scripts.trajectory_engine import TrajectoryEngine, TrajectoryEventType
                traj_engine = TrajectoryEngine(state_dir=self.state_dir, project_root=self.project_root)
                traj_payload = {
                    "conversationId": det.get("conversation_id", ""),
                    "workspacePaths": [self.project_root],
                    "stepIdx": det.get("step_index", 1),
                    "artifactDirectoryPath": det.get("artifact_directory_path", ""),
                    "modelName": det.get("model_name", ""),
                    "toolCall": {"name": "invoke_subagent", "args": {"child_agent": child_agent, "task_id": task_id}}
                }
                traj_details = {
                    "parent_agent": parent_agent,
                    "child_agent": child_agent,
                    "task_id": task_id,
                    "objective": objective,
                    "input_artifacts": in_arts,
                    "output_artifacts": out_arts,
                    "status": stat,
                    **det
                }
                # Map etype to TrajectoryEventType
                ttype = etype
                if etype in TrajectoryEventType.__members__:
                    ttype = TrajectoryEventType[etype]
                traj_engine.record_event(
                    event_type=ttype,
                    payload=traj_payload,
                    details=traj_details,
                    actor=parent_agent
                )
            except Exception as e_traj:
                sys.stderr.write(f"[delegation_event_engine] Note syncing to TrajectoryEngine: {e_traj}\n")

        # Sync to AcademicEventEngine if available
        try:
            from scripts.academic_event_engine import emit_academic_event
            emit_academic_event(
                event_type=etype,
                project_id=det.get("project_id", "PROJECT-ACADEMIC-SUITE"),
                emitter_agent=parent_agent,
                payload={
                    "child_agent": child_agent,
                    "task_id": task_id,
                    "objective": objective,
                    "input_artifacts": in_arts,
                    "output_artifacts": out_arts,
                    "status": stat,
                    **det
                },
                base_dir=self.project_root,
                stage_id=task_id
            )
        except Exception:
            pass

        return event_record

    def record_subagent_requested(
        self,
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        output_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Emits SUBAGENT_REQUESTED event with status REQUESTED."""
        return self.emit_delegation_event(
            event_type=DelegationEventType.SUBAGENT_REQUESTED,
            parent_agent=parent_agent,
            child_agent=child_agent,
            task_id=task_id,
            objective=objective,
            status=DelegationStatus.REQUESTED,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            details=details
        )

    def record_subagent_started(
        self,
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        output_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Emits SUBAGENT_STARTED event with status STARTED."""
        return self.emit_delegation_event(
            event_type=DelegationEventType.SUBAGENT_STARTED,
            parent_agent=parent_agent,
            child_agent=child_agent,
            task_id=task_id,
            objective=objective,
            status=DelegationStatus.STARTED,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            details=details
        )

    def record_subagent_completed(
        self,
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        output_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Emits SUBAGENT_COMPLETED event with status COMPLETED."""
        return self.emit_delegation_event(
            event_type=DelegationEventType.SUBAGENT_COMPLETED,
            parent_agent=parent_agent,
            child_agent=child_agent,
            task_id=task_id,
            objective=objective,
            status=DelegationStatus.COMPLETED,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            details=details
        )

    def record_subagent_failed(
        self,
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        error_message: Optional[str] = None,
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        output_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Emits SUBAGENT_FAILED event with status FAILED."""
        det = details or {}
        if error_message:
            det["error_message"] = error_message
        return self.emit_delegation_event(
            event_type=DelegationEventType.SUBAGENT_FAILED,
            parent_agent=parent_agent,
            child_agent=child_agent,
            task_id=task_id,
            objective=objective,
            status=DelegationStatus.FAILED,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            details=det
        )

    def record_artifact_returned(
        self,
        parent_agent: str,
        child_agent: str,
        task_id: str,
        objective: str,
        output_artifacts: List[Union[str, Dict[str, Any]]],
        input_artifacts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Emits ARTIFACT_RETURNED event with status RETURNED."""
        return self.emit_delegation_event(
            event_type=DelegationEventType.ARTIFACT_RETURNED,
            parent_agent=parent_agent,
            child_agent=child_agent,
            task_id=task_id,
            objective=objective,
            status=DelegationStatus.RETURNED,
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            details=details
        )

    def load_delegation_events(
        self,
        task_id: Optional[str] = None,
        child_agent: Optional[str] = None,
        parent_agent: Optional[str] = None,
        event_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Loads observable delegation events chronologically from delegation_events.jsonl."""
        if not os.path.exists(self.events_file):
            return []

        events = []
        with open(self.events_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if task_id and record.get("task_id") != task_id:
                        continue
                    if child_agent and record.get("child_agent") != child_agent:
                        continue
                    if parent_agent and record.get("parent_agent") != parent_agent:
                        continue
                    if event_types and record.get("event_type") not in event_types:
                        continue
                    events.append(record)
                except Exception:
                    continue
        return events

    def get_observable_delegation_chain(
        self,
        task_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Reconstructs the factually observed delegation chain:
        academic-orchestrator → invoke_subagent → statistics-agent
        Returns a list of structured observed delegations without guessing.
        """
        events = self.load_delegation_events(task_id=task_id)
        if not events:
            return []

        # Group events by (task_id, child_agent)
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for ev in events:
            key = f"{ev.get('task_id')}::{ev.get('child_agent')}"
            grouped.setdefault(key, []).append(ev)

        chains = []
        for key, ev_list in grouped.items():
            first_ev = ev_list[0]
            last_ev = ev_list[-1]
            parent = first_ev.get("parent_agent", "academic-orchestrator")
            child = first_ev.get("child_agent", "specialist")
            t_id = first_ev.get("task_id", "")
            obj = first_ev.get("objective", "")

            # Determine aggregate status
            has_failed = any(e.get("event_type") == DelegationEventType.SUBAGENT_FAILED.value for e in ev_list)
            has_completed = any(e.get("event_type") == DelegationEventType.SUBAGENT_COMPLETED.value for e in ev_list)
            has_returned = any(e.get("event_type") == DelegationEventType.ARTIFACT_RETURNED.value for e in ev_list)

            if has_failed:
                agg_status = "FAILED"
            elif has_completed or has_returned:
                agg_status = "COMPLETED"
            else:
                agg_status = last_ev.get("status", "STARTED")

            all_inputs = []
            all_outputs = []
            for e in ev_list:
                for inp in e.get("input_artifacts", []):
                    if inp not in all_inputs:
                        all_inputs.append(inp)
                for outp in e.get("output_artifacts", []):
                    if outp not in all_outputs:
                        all_outputs.append(outp)

            chains.append({
                "task_id": t_id,
                "parent_agent": parent,
                "child_agent": child,
                "objective": obj,
                "status": agg_status,
                "input_artifacts": all_inputs,
                "output_artifacts": all_outputs,
                "transition": f"{parent} → invoke_subagent → {child}",
                "event_count": len(ev_list),
                "lifecycle_events": [e.get("event_type") for e in ev_list]
            })

        return chains

    def verify_no_speculative_inference(
        self,
        task_id: str,
        claimed_child_agent: str
    ) -> bool:
        """
        Guarantees that a claimed delegation was physically observed in telemetry.
        Raises UnobservedDelegationError if claimed subagent was not logged in delegation_events.jsonl.
        """
        events = self.load_delegation_events(task_id=task_id, child_agent=claimed_child_agent)
        if not events:
            raise UnobservedDelegationError(
                f"Speculative delegation detected: Agent claimed '{claimed_child_agent}' was used for task '{task_id}', "
                f"but zero observable delegation events exist in state/delegation_events.jsonl. "
                f"All subagent invocations must be physically recorded via invoke_subagent telemetry."
            )
        return True


def main():
    parser = argparse.ArgumentParser(description="Observable Subagent Delegation Engine (Phase 23)")
    subparsers = parser.add_subparsers(dest="command")

    # Command: record
    rec_parser = subparsers.add_parser("record", help="Record a delegation event")
    rec_parser.add_argument("--event-type", required=True, choices=[
        "SUBAGENT_REQUESTED", "SUBAGENT_STARTED", "SUBAGENT_COMPLETED", "SUBAGENT_FAILED", "ARTIFACT_RETURNED"
    ])
    rec_parser.add_argument("--parent", default="academic-orchestrator", help="Parent agent")
    rec_parser.add_argument("--child", required=True, help="Child subagent")
    rec_parser.add_argument("--task-id", required=True, help="Task ID")
    rec_parser.add_argument("--objective", required=True, help="Task objective")
    rec_parser.add_argument("--status", default="STARTED", help="Status")
    rec_parser.add_argument("--input-artifact", action="append", default=[], help="Input artifact path")
    rec_parser.add_argument("--output-artifact", action="append", default=[], help="Output artifact path")
    rec_parser.add_argument("--state-dir", default=None, help="State directory")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List recorded delegation events")
    list_parser.add_argument("--task-id", default=None, help="Filter by task ID")
    list_parser.add_argument("--child", default=None, help="Filter by child agent")
    list_parser.add_argument("--state-dir", default=None, help="State directory")

    # Command: chain
    chain_parser = subparsers.add_parser("chain", help="Show observable delegation chain")
    chain_parser.add_argument("--task-id", default=None, help="Filter by task ID")
    chain_parser.add_argument("--state-dir", default=None, help="State directory")

    args = parser.parse_args()
    engine = DelegationEventEngine(state_dir=getattr(args, "state_dir", None))

    if args.command == "record":
        evt = engine.emit_delegation_event(
            event_type=args.event_type,
            parent_agent=args.parent,
            child_agent=args.child,
            task_id=args.task_id,
            objective=args.objective,
            status=args.status,
            input_artifacts=args.input_artifact,
            output_artifacts=args.output_artifact
        )
        print(json.dumps(evt, indent=2))

    elif args.command == "list":
        events = engine.load_delegation_events(task_id=args.task_id, child_agent=args.child)
        print(json.dumps(events, indent=2))

    elif args.command == "chain":
        chains = engine.get_observable_delegation_chain(task_id=args.task_id)
        if not chains:
            print("No observable delegation chains recorded.")
        else:
            for ch in chains:
                print(f"Task: {ch['task_id']}")
                print(f"  Transition: {ch['transition']}")
                print(f"  Status: {ch['status']}")
                print(f"  Events ({ch['event_count']}): {' -> '.join(ch['lifecycle_events'])}")
                if ch['output_artifacts']:
                    print(f"  Artifacts: {ch['output_artifacts']}")
                print("-" * 50)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
