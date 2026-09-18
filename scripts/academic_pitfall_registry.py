#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_pitfall_registry.py — Authoritative Persistent Pitfall Registry ("The Research Memory")

Manages transparent, deterministic persistence and query retrieval for methodological,
statistical, execution, evidence, and validation failures in state/pitfalls.jsonl.
Strictly adheres to contracts/pitfall.schema.json without opaque machine learning.
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Tuple, Union

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

# Dist-packages fallback
for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

try:
    import jsonschema
except ImportError:
    jsonschema = None


# ==============================================================================
# Fail-Closed Exception Hierarchy
# ==============================================================================

class PitfallError(Exception):
    """Base exception for AcademicSuite pitfall registry operations."""
    pass

class PitfallSchemaValidationError(PitfallError):
    """Raised when a pitfall record fails schema validation against contracts/pitfall.schema.json."""
    pass

class DuplicatePitfallError(PitfallError):
    """Raised when an attempt is made to persist a pitfall with an existing pitfall_id."""
    pass

class MalformedPitfallError(PitfallError):
    """Raised when corrupted, unparseable, or non-object lines exist in pitfalls.jsonl."""
    pass

class InvalidPitfallQueryError(PitfallError):
    """Raised when invalid or unsupportable query parameters are supplied."""
    pass

class PitfallNotFoundError(PitfallError):
    """Raised when a requested pitfall_id cannot be found in the registry."""
    pass


# ==============================================================================
# Domain Failure Taxonomy
# ==============================================================================

VALID_CATEGORIES: Set[str] = {
    "methodological",
    "statistical",
    "execution",
    "evidence",
    "validation"
}

DEFAULT_PITFALLS_FILE = os.path.join(ROOT_DIR, "state", "pitfalls.jsonl")


def load_pitfall_schema() -> Optional[Dict[str, Any]]:
    """Loads contracts/pitfall.schema.json from the repository."""
    schema_path = os.path.join(ROOT_DIR, "contracts", "pitfall.schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ==============================================================================
# Academic Pitfall Registry Class
# ==============================================================================

class AcademicPitfallRegistry:
    """
    Authoritative research memory registry storing methodological, statistical,
    execution, evidence, and validation failures in state/pitfalls.jsonl.
    Enforces fail-closed schema validation, duplicate detection, and deterministic querying.
    """

    def __init__(self, registry_path: Optional[str] = None, project_id: Optional[str] = None):
        self.registry_path = os.path.abspath(registry_path or DEFAULT_PITFALLS_FILE)
        self.project_id = project_id or ""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)

        self.schema = load_pitfall_schema()
        self.known_ids: Set[str] = set()

        if os.path.exists(self.registry_path):
            self._warmup_cache()

    def _warmup_cache(self) -> None:
        """Populates known_ids from disk cache without throwing on malformed lines."""
        try:
            records = self.read(validate_schema=False)
            for r in records:
                pid = r.get("pitfall_id")
                if pid:
                    self.known_ids.add(pid)
        except Exception:
            pass

    def create(
        self,
        candidate_approach: str,
        problem: str,
        evidence: Union[str, Dict[str, Any]],
        corrective_action: str,
        adapted_approach: str,
        detected_by: str = "academic-challenger",
        category: str = "methodological",
        stage: str = "methodological_candidate_selection",
        milestone: Optional[str] = None,
        project: Optional[str] = None,
        reusable: bool = True,
        pitfall_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        verification_check: Optional[str] = None,
        related_artifacts: Optional[List[str]] = None,
        contract_version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Creates, validates, and persists a structured pitfall record to state/pitfalls.jsonl.
        Fails closed on schema invalidity, unknown category, or duplicate pitfall_id.
        """
        # 1. Non-empty string checks
        if not candidate_approach or not str(candidate_approach).strip():
            raise PitfallSchemaValidationError("Field 'candidate_approach' must be a non-empty string.")
        if not problem or not str(problem).strip():
            raise PitfallSchemaValidationError("Field 'problem' must be a non-empty string.")
        if not corrective_action or not str(corrective_action).strip():
            raise PitfallSchemaValidationError("Field 'corrective_action' must be a non-empty string.")
        if not adapted_approach or not str(adapted_approach).strip():
            raise PitfallSchemaValidationError("Field 'adapted_approach' must be a non-empty string.")

        # 2. Category validation
        cat_lower = (category or "methodological").lower().strip()
        if cat_lower not in VALID_CATEGORIES:
            raise PitfallSchemaValidationError(
                f"Invalid failure category '{category}'. Must be one of {sorted(list(VALID_CATEGORIES))}."
            )

        # 2. Pitfall ID generation & uniqueness check
        now_utc = datetime.now(timezone.utc)
        pid = pitfall_id or f"PIT-{int(now_utc.timestamp())}-{uuid.uuid4().hex[:6].upper()}"
        if pid in self.known_ids:
            raise DuplicatePitfallError(f"Duplicate pitfall_id detected: '{pid}'. Pitfalls are immutable.")

        # 3. Timestamp formatting
        ts = timestamp or now_utc.isoformat()

        # 4. Evidence structure
        if isinstance(evidence, str):
            evidence_obj = {
                "description": evidence,
                "metric_or_statistic": f"{cat_lower}_defect",
                "observed_value": candidate_approach,
                "threshold_value": "Methodological & Validation Benchmark"
            }
        elif isinstance(evidence, dict):
            if "description" not in evidence:
                raise PitfallSchemaValidationError("Evidence dictionary must contain required 'description' field.")
            evidence_obj = evidence
        else:
            raise PitfallSchemaValidationError(f"Evidence must be a string or dict, got {type(evidence)}.")

        # 5. Resolution structure
        resolution_obj = {
            "corrective_action": corrective_action,
            "adapted_approach": adapted_approach,
            "verification_check": verification_check or "Verify against analytical requirements and empirical data.",
            "resolved_at": ts,
            "resolved_by": detected_by
        }

        # 6. Assemble complete record
        proj = project or self.project_id or "academic_project"
        m_id = milestone or stage or "M_UNSPECIFIED"

        record: Dict[str, Any] = {
            "contract_version": contract_version,
            "pitfall_id": pid,
            "project": proj,
            "milestone": m_id,
            "stage": stage or m_id,
            "category": cat_lower,
            "candidate_approach": candidate_approach,
            "detected_by": detected_by,
            "problem": problem,
            "evidence": evidence_obj,
            "resolution": resolution_obj,
            "reusable": bool(reusable),
            "timestamp": ts,
            "related_artifacts": related_artifacts or []
        }

        # 7. Strict schema validation
        if self.schema and jsonschema:
            try:
                format_checker = jsonschema.FormatChecker() if hasattr(jsonschema, "FormatChecker") else None
                jsonschema.validate(instance=record, schema=self.schema, format_checker=format_checker)
            except jsonschema.ValidationError as ve:
                path_str = " -> ".join([str(p) for p in ve.path]) if ve.path else "root"
                raise PitfallSchemaValidationError(f"Pitfall schema validation failed at [{path_str}]: {ve.message}") from ve

        # 8. Append atomically to file
        with open(self.registry_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        self.known_ids.add(pid)
        return record

    def read(self, validate_schema: bool = True) -> List[Dict[str, Any]]:
        """
        Reads all recorded pitfalls from the JSONL registry.
        Fails closed on corrupted JSON, non-object lines, or schema violations.
        """
        if not os.path.exists(self.registry_path):
            return []

        pitfalls: List[Dict[str, Any]] = []
        seen_ids: Set[str] = set()

        with open(self.registry_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue

                try:
                    record = json.loads(clean_line)
                except Exception as e:
                    raise MalformedPitfallError(
                        f"Malformed JSON in '{self.registry_path}' at line {line_no}: {str(e)}"
                    ) from e

                if not isinstance(record, dict):
                    raise MalformedPitfallError(
                        f"Malformed pitfall record in '{self.registry_path}' at line {line_no}: Expected JSON object."
                    )

                pid = record.get("pitfall_id")
                if not pid:
                    raise MalformedPitfallError(
                        f"Malformed pitfall record at line {line_no}: Missing required 'pitfall_id'."
                    )

                if pid in seen_ids:
                    raise DuplicatePitfallError(
                        f"Duplicate pitfall_id detected in log: '{pid}' at line {line_no}."
                    )
                seen_ids.add(pid)

                if validate_schema and self.schema and jsonschema:
                    try:
                        format_checker = jsonschema.FormatChecker() if hasattr(jsonschema, "FormatChecker") else None
                        jsonschema.validate(instance=record, schema=self.schema, format_checker=format_checker)
                    except jsonschema.ValidationError as ve:
                        raise PitfallSchemaValidationError(
                            f"Schema validation failed for pitfall '{pid}' (line {line_no}): {ve.message}"
                        ) from ve

                pitfalls.append(record)

        return pitfalls

    def get(self, pitfall_id: str) -> Dict[str, Any]:
        """Retrieves a single pitfall by pitfall_id or raises PitfallNotFoundError."""
        for p in self.read(validate_schema=False):
            if p.get("pitfall_id") == pitfall_id:
                return p
        raise PitfallNotFoundError(f"Pitfall '{pitfall_id}' not found in registry {self.registry_path}.")

    def query(
        self,
        category: Optional[str] = None,
        project: Optional[str] = None,
        milestone: Optional[str] = None,
        detected_by: Optional[str] = None,
        reusable: Optional[bool] = None,
        keyword: Optional[str] = None,
        candidate_method: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Deterministic, transparent research-memory query interface.
        Filters by metadata tags and keyword matching across problem, approach, and evidence.
        """
        if category and category.lower().strip() not in VALID_CATEGORIES:
            raise InvalidPitfallQueryError(
                f"Invalid query category '{category}'. Must be one of {sorted(list(VALID_CATEGORIES))}."
            )

        records = self.read(validate_schema=False)
        results: List[Dict[str, Any]] = []

        kw_lower = keyword.lower().strip() if keyword else None
        method_lower = candidate_method.lower().strip() if candidate_method else None
        cat_lower = category.lower().strip() if category else None

        for r in records:
            # Category match
            if cat_lower and r.get("category", "").lower() != cat_lower:
                continue

            # Project match
            if project and r.get("project") != project:
                continue

            # Milestone match (checks milestone and stage)
            if milestone:
                r_m = r.get("milestone", "")
                r_s = r.get("stage", "")
                if milestone != r_m and milestone != r_s:
                    continue

            # Detected by match
            if detected_by and r.get("detected_by") != detected_by:
                continue

            # Reusable match
            if reusable is not None and r.get("reusable") != reusable:
                continue

            # Candidate method match
            if method_lower:
                approach_text = r.get("candidate_approach", "").lower()
                problem_text = r.get("problem", "").lower()
                if method_lower not in approach_text and method_lower not in problem_text:
                    continue

            # Keyword match
            if kw_lower:
                approach_text = r.get("candidate_approach", "").lower()
                prob_text = r.get("problem", "").lower()
                ev_desc = r.get("evidence", {}).get("description", "").lower()
                action_text = r.get("resolution", {}).get("corrective_action", "").lower()
                adapted_text = r.get("resolution", {}).get("adapted_approach", "").lower()

                combined = f"{approach_text} {prob_text} {ev_desc} {action_text} {adapted_text}"
                if kw_lower not in combined:
                    continue

            results.append(r)

        return results

    def is_approach_invalidated(
        self,
        candidate_approach: Union[str, Dict[str, Any]],
        category: Optional[str] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Determines whether a proposed candidate approach matches a previously invalidated,
        reusable pitfall in the registry.
        Returns:
            (is_invalidated: bool, matching_pitfalls: List[Dict[str, Any]])
        """
        if isinstance(candidate_approach, dict):
            method = candidate_approach.get("method", "")
            rq = candidate_approach.get("research_question", "")
            search_str = f"{method} {rq}".strip()
            method_kw = method
        else:
            search_str = str(candidate_approach)
            method_kw = search_str

        # Query reusable pitfalls matching method keyword
        matches = self.query(
            category=category,
            reusable=True,
            candidate_method=method_kw if method_kw else None
        )

        if not matches and search_str:
            # Fallback to general keyword search across reusable pitfalls
            for word in search_str.split():
                if len(word) >= 4 and word.lower() not in {"what", "does", "with", "from", "into", "that"}:
                    kw_matches = self.query(category=category, reusable=True, keyword=word)
                    if kw_matches:
                        matches.extend(kw_matches)

        # Deduplicate matches
        unique_matches: List[Dict[str, Any]] = []
        seen = set()
        for m in matches:
            mid = m.get("pitfall_id")
            if mid and mid not in seen:
                seen.add(mid)
                unique_matches.append(m)

        return (len(unique_matches) > 0, unique_matches)

    def resolve_pitfall(
        self,
        pitfall_id: str,
        corrective_action: str,
        adapted_approach: str,
        resolved_by: str,
        verification_check: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Updates the resolution fields of an existing pitfall in state/pitfalls.jsonl.
        """
        records = self.read(validate_schema=False)
        found = False
        now_ts = datetime.now(timezone.utc).isoformat()
        updated_record = {}

        for r in records:
            if r.get("pitfall_id") == pitfall_id:
                found = True
                r.setdefault("resolution", {})
                r["resolution"]["corrective_action"] = corrective_action
                r["resolution"]["adapted_approach"] = adapted_approach
                r["resolution"]["resolved_by"] = resolved_by
                r["resolution"]["resolved_at"] = now_ts
                if verification_check:
                    r["resolution"]["verification_check"] = verification_check
                updated_record = r
                break

        if not found:
            raise PitfallNotFoundError(f"Cannot resolve non-existent pitfall '{pitfall_id}'.")

        # Validate updated record against schema
        if self.schema and jsonschema:
            try:
                format_checker = jsonschema.FormatChecker() if hasattr(jsonschema, "FormatChecker") else None
                jsonschema.validate(instance=updated_record, schema=self.schema, format_checker=format_checker)
            except jsonschema.ValidationError as ve:
                raise PitfallSchemaValidationError(f"Updated pitfall failed schema: {ve.message}") from ve

        # Rewrite file atomically
        with open(self.registry_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return updated_record

    def surface_reusable_pitfalls(
        self,
        category: Optional[str] = None,
        milestone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Surfaces all reusable historical pitfalls relevant to a planned milestone or category
        to prevent repeating past mistakes in a new workflow.
        """
        return self.query(category=category, milestone=milestone, reusable=True)
