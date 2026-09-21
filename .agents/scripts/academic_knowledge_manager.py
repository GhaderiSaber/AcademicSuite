#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_knowledge_manager.py — AcademicSuite Persistent Knowledge & Capability Memory System

Implements the second layer of the continuous self-improvement architecture:
    RAW EXPERIENCE → PERSISTENT KNOWLEDGE → EXECUTABLE SKILLS

Separates persistent knowledge into dedicated epistemological categories:
- learning/knowledge/lessons/        (Diagnosed failure prevention and positive lessons)
- learning/knowledge/patterns/       (Approved workflows and procedural patterns)
- learning/knowledge/anti-patterns/  (Defective, prohibited approaches with symptoms and remedies)
- learning/knowledge/principles/     (Foundational theoretical, statistical, and typographic rules)
- learning/knowledge/exemplars/      (Gold-standard verified research artifacts)

Supports capability-partitioned skill memory:
- learning/skill-memory/<capability>/ (Independent memory for 8 major research capabilities:
  longitudinal-analysis, mediation, moderation, SEM, psychometrics, chapter4, chapter5, evidence)
  Tracking: successful examples, failures, lessons, anti-patterns, related knowledge, evaluation cases, history.

Features:
1. 7 Explicit Relationship Types: related_to, caused_by, tested_by, implemented_by, contradicts, supersedes, derived_from.
2. Semantic Versioning & Superseding: Old knowledge marked SUPERSEDED; graph lineage preserved.
3. Strict Scope Containment: project, domain, cross-project, global-in-project. Project-specific rules never leak.
4. Pre-Task Retrieval Engine: Briefs agents with relevant lessons, anti-patterns, and exemplars before task execution.
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

# Virtualenv auto-discovery shim
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

from contracts.contract_validator import (
    validate_knowledge_item,
    validate_anti_pattern,
    validate_exemplar,
    validate_lesson,
    validate_skill_memory_record,
    validate_contradiction_record
)


class ContractValidationError(Exception):
    """Raised when a knowledge or memory contract fails validation."""
    pass


class AcademicKnowledgeManager:
    """Production Knowledge & Skill-Memory Manager for AcademicSuite Continuous Self-Improvement."""

    CANONICAL_CAPABILITIES = [
        "longitudinal-analysis",
        "mediation",
        "moderation",
        "SEM",
        "psychometrics",
        "chapter4",
        "chapter5",
        "evidence"
    ]

    CAPABILITY_ALIASES = {
        "longitudinal": "longitudinal-analysis",
        "longitudinal_analysis": "longitudinal-analysis",
        "longitudinal-modmed": "longitudinal-analysis",
        "mediation-analysis": "mediation",
        "process-mediation": "mediation",
        "moderation-analysis": "moderation",
        "sem": "SEM",
        "structural-equation-modeling": "SEM",
        "psychometric": "psychometrics",
        "scale-validation": "psychometrics",
        "chapter-4": "chapter4",
        "chapter_4": "chapter4",
        "chapter-5": "chapter5",
        "chapter_5": "chapter5",
        "literature": "evidence",
        "systematic-review": "evidence",
        "meta-analysis": "evidence"
    }

    VALID_RELATIONSHIPS = {
        "related_to",
        "caused_by",
        "tested_by",
        "implemented_by",
        "contradicts",
        "supersedes",
        "derived_from"
    }

    INVERSE_RELATIONSHIPS = {
        "supersedes": "superseded_by",
        "caused_by": "causes",
        "tested_by": "tests",
        "implemented_by": "implements",
        "derived_from": "source_of",
        "related_to": "related_to",
        "contradicts": "contradicts"
    }

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or os.environ.get("ACADEMIC_SUITE_BASE_DIR") or ROOT_DIR)
        cand_agents = os.path.join(self.base_dir, ".agents", "learning")
        self.learning_dir = cand_agents if os.path.isdir(cand_agents) else os.path.join(self.base_dir, "learning")
        self.knowledge_dir = os.path.join(self.learning_dir, "knowledge")
        self.skill_memory_dir = os.path.join(self.learning_dir, "skill-memory")

        # Epistemological category paths
        self.lessons_dir = os.path.join(self.knowledge_dir, "lessons")
        self.patterns_dir = os.path.join(self.knowledge_dir, "patterns")
        self.anti_patterns_dir = os.path.join(self.knowledge_dir, "anti-patterns")
        self.principles_dir = os.path.join(self.knowledge_dir, "principles")
        self.exemplars_dir = os.path.join(self.knowledge_dir, "exemplars")
        self.contradictions_dir = os.path.join(self.knowledge_dir, "contradictions")
        self.snapshots_dir = os.path.join(self.learning_dir, "snapshots")
        self.skill_snapshots_dir = os.path.join(self.snapshots_dir, "skills")

        self._ensure_directories()
        from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
        self.retriever = AcademicTwoStageRetriever(base_dir=self.base_dir)

    def _ensure_directories(self):
        """Ensure all mandated knowledge and capability directories exist on disk."""
        dirs = [
            self.learning_dir,
            self.knowledge_dir,
            self.lessons_dir,
            self.patterns_dir,
            self.anti_patterns_dir,
            self.principles_dir,
            self.exemplars_dir,
            self.contradictions_dir,
            self.snapshots_dir,
            self.skill_snapshots_dir,
            self.skill_memory_dir
        ]
        for cap in self.CANONICAL_CAPABILITIES:
            dirs.append(os.path.join(self.skill_memory_dir, cap))

        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def normalize_capability(self, capability: Optional[str]) -> Optional[str]:
        """Normalize capability name to canonical form."""
        if not capability:
            return None
        c_clean = capability.strip().lower()
        for canon in self.CANONICAL_CAPABILITIES:
            if canon.lower() == c_clean:
                return canon
        return self.CAPABILITY_ALIASES.get(c_clean, capability)

    # -------------------------------------------------------------------------
    # Knowledge Item Operations (Principles & Patterns)
    # -------------------------------------------------------------------------

    def add_principle(self, principle_dict: Dict[str, Any]) -> str:
        """
        Validate and store a foundational academic, statistical, or typographic principle.
        Validates against contracts/evolution/knowledge_item.schema.json.
        """
        item = dict(principle_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("item_type", "principle")
        item.setdefault("generalization_stage", "PROMOTED_PRINCIPLE")
        item.setdefault("status", "ACCEPTED_ACTIVE")
        item.setdefault("version", "1.0.0")
        item.setdefault("updated_at", datetime.now(timezone.utc).isoformat())

        if "knowledge_id" not in item:
            item["knowledge_id"] = f"PRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # Guarantee schema compliance defaults
        if "scope" not in item:
            item["scope"] = "domain"
        if "source_lessons" not in item:
            item["source_lessons"] = ["LSN-SYNTHESIZED-FOUNDATION"]
        if "supporting_evaluations" not in item:
            item["supporting_evaluations"] = []
        if "contradictions" not in item:
            item["contradictions"] = []
        if "relationships" not in item:
            item["relationships"] = []
        if "exclusions" not in item:
            item["exclusions"] = []
        if "applicability" not in item:
            item["applicability"] = {"criteria": ["general_academic_research"]}

        val_res = validate_knowledge_item(item)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid principle contract: {val_res.get('errors')}")

        file_path = os.path.join(self.principles_dir, f"{item['knowledge_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.principles_dir,
            {
                "knowledge_id": item["knowledge_id"],
                "item_type": "principle",
                "statement": item["statement"][:120],
                "scope": item["scope"],
                "project_id": item.get("project_id"),
                "version": item["version"],
                "status": item["status"],
                "confidence": item.get("confidence"),
                "tags": item.get("tags", []),
                "updated_at": item["updated_at"],
                "file_path": file_path
            }
        )
        return item["knowledge_id"]

    def add_pattern(self, pattern_dict: Dict[str, Any]) -> str:
        """
        Validate and store an approved reusable methodological or procedural pattern.
        Validates against contracts/evolution/knowledge_item.schema.json.
        """
        item = dict(pattern_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("item_type", "pattern")
        item.setdefault("status", "ACCEPTED_ACTIVE")
        item.setdefault("version", "1.0.0")
        item.setdefault("updated_at", datetime.now(timezone.utc).isoformat())

        if "knowledge_id" not in item:
            item["knowledge_id"] = f"PTR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        if "scope" not in item:
            item["scope"] = "cross-project"
        if "source_lessons" not in item:
            item["source_lessons"] = ["LSN-PATTERN-DERIVED"]
        if "supporting_evaluations" not in item:
            item["supporting_evaluations"] = []
        if "contradictions" not in item:
            item["contradictions"] = []
        if "relationships" not in item:
            item["relationships"] = []
        if "exclusions" not in item:
            item["exclusions"] = []
        if "applicability" not in item:
            item["applicability"] = {"criteria": ["standard_methodological_workflow"]}

        val_res = validate_knowledge_item(item)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid pattern contract: {val_res.get('errors')}")

        file_path = os.path.join(self.patterns_dir, f"{item['knowledge_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.patterns_dir,
            {
                "knowledge_id": item["knowledge_id"],
                "item_type": "pattern",
                "statement": item["statement"][:120],
                "scope": item["scope"],
                "project_id": item.get("project_id"),
                "version": item["version"],
                "status": item["status"],
                "confidence": item.get("confidence"),
                "tags": item.get("tags", []),
                "updated_at": item["updated_at"],
                "file_path": file_path
            }
        )
        return item["knowledge_id"]

    # -------------------------------------------------------------------------
    # Anti-Pattern Operations
    # -------------------------------------------------------------------------

    def add_anti_pattern(self, anti_pattern_dict: Dict[str, Any]) -> str:
        """
        Validate and store an anti-pattern (defective pattern, why defective, symptoms, and remedy).
        Validates against contracts/evolution/anti_pattern.schema.json.
        """
        item = dict(anti_pattern_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("reusable", True)
        item.setdefault("updated_at", datetime.now(timezone.utc).isoformat())

        if "anti_pattern_id" not in item:
            item["anti_pattern_id"] = f"AP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        val_res = validate_anti_pattern(item)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid anti-pattern contract: {val_res.get('errors')}")

        file_path = os.path.join(self.anti_patterns_dir, f"{item['anti_pattern_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.anti_patterns_dir,
            {
                "anti_pattern_id": item["anti_pattern_id"],
                "category": item["category"],
                "defective_pattern": item["defective_pattern"][:120],
                "corrective_remedy": item["corrective_remedy"][:120],
                "reusable": item["reusable"],
                "updated_at": item["updated_at"],
                "file_path": file_path
            }
        )
        return item["anti_pattern_id"]

    # -------------------------------------------------------------------------
    # Exemplar Operations
    # -------------------------------------------------------------------------

    def add_exemplar(self, exemplar_dict: Dict[str, Any]) -> str:
        """
        Validate and store a verified gold-standard research artifact or execution exemplar.
        Validates against contracts/evolution/exemplar.schema.json.
        """
        item = dict(exemplar_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        if "exemplar_id" not in item:
            item["exemplar_id"] = f"EXM-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        val_res = validate_exemplar(item)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid exemplar contract: {val_res.get('errors')}")

        file_path = os.path.join(self.exemplars_dir, f"{item['exemplar_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.exemplars_dir,
            {
                "exemplar_id": item["exemplar_id"],
                "domain": item["domain"],
                "task_type": item["task_type"],
                "why_exemplary": item["why_exemplary"][:120],
                "created_at": item["created_at"],
                "file_path": file_path
            }
        )
        return item["exemplar_id"]

    def add_lesson(self, lesson_dict: Dict[str, Any]) -> str:
        """
        Validate and store a learned lesson contract in learning/knowledge/lessons/.
        """
        item = dict(lesson_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("status", "VALIDATED")
        item.setdefault("is_active_behavior", True)
        item.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        lid = item.get("lesson_id") or item.get("item_id")
        if not lid:
            lid = f"LSN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        item["lesson_id"] = lid
        item["item_id"] = lid

        file_path = os.path.join(self.lessons_dir, f"{lid}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.lessons_dir,
            {
                "lesson_id": item["lesson_id"],
                "target_skill": item.get("target_skill") or (item.get("related_skills", ["unknown"])[0] if item.get("related_skills") else "unknown"),
                "status": item["status"],
                "confidence": item.get("confidence"),
                "created_at": item["created_at"]
            }
        )
        return item["lesson_id"]

    # -------------------------------------------------------------------------
    # General Item Retrieval & Updates
    # -------------------------------------------------------------------------

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve any persistent knowledge item, lesson, anti-pattern, or exemplar by ID."""
        dirs_to_check = [
            self.principles_dir,
            self.patterns_dir,
            self.anti_patterns_dir,
            self.exemplars_dir,
            self.lessons_dir
        ]
        target_name = f"{item_id}.json"
        for d in dirs_to_check:
            p = os.path.join(d, target_name)
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)

        # Also check without exact filename if id is inside JSON
        for d in dirs_to_check:
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                if fn.endswith(".json"):
                    fp = os.path.join(d, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if (
                                data.get("knowledge_id") == item_id or
                                data.get("anti_pattern_id") == item_id or
                                data.get("exemplar_id") == item_id or
                                data.get("lesson_id") == item_id
                            ):
                                return data
                    except Exception:
                        continue
        return None

    def update_item(self, item_id: str, updated_data: Dict[str, Any]) -> bool:
        """Save modifications to an existing knowledge item in place."""
        dirs_to_check = [
            self.principles_dir,
            self.patterns_dir,
            self.anti_patterns_dir,
            self.exemplars_dir,
            self.lessons_dir
        ]
        for d in dirs_to_check:
            fp = os.path.join(d, f"{item_id}.json")
            if os.path.isfile(fp):
                with open(fp, "w", encoding="utf-8") as f:
                    json.dump(updated_data, f, indent=2, ensure_ascii=False)
                return True

        # Scan fallback
        for d in dirs_to_check:
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                if fn.endswith(".json"):
                    fp = os.path.join(d, fn)
                    try:
                        with open(fp, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            if (
                                data.get("knowledge_id") == item_id or
                                data.get("anti_pattern_id") == item_id or
                                data.get("exemplar_id") == item_id or
                                data.get("lesson_id") == item_id
                            ):
                                with open(fp, "w", encoding="utf-8") as wf:
                                    json.dump(updated_data, wf, indent=2, ensure_ascii=False)
                                return True
                    except Exception:
                        continue
        return False

    # -------------------------------------------------------------------------
    # Relationship Graph Operations
    # -------------------------------------------------------------------------

    def link_items(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        description: str = ""
    ) -> bool:
        """
        Establish a typed relational link from source_id to target_id.
        Supported relation_types:
          related_to, caused_by, tested_by, implemented_by, contradicts, supersedes, derived_from.
        """
        if relation_type not in self.VALID_RELATIONSHIPS:
            raise ValueError(
                f"Unsupported relation_type '{relation_type}'. Must be one of {sorted(self.VALID_RELATIONSHIPS)}"
            )

        source_item = self.get_item(source_id)
        if not source_item:
            raise FileNotFoundError(f"Source knowledge item '{source_id}' not found.")

        # Add to source relationships
        relationships = source_item.setdefault("relationships", [])
        # Avoid duplicate links
        for r in relationships:
            if r.get("relation_type") == relation_type and r.get("target_id") == target_id:
                return True

        relationships.append({
            "relation_type": relation_type,
            "target_id": target_id,
            "description": description or f"Relation '{relation_type}' to {target_id}"
        })
        self.update_item(source_id, source_item)

        # If relation is contradicts, update reciprocal link
        if relation_type == "contradicts":
            target_item = self.get_item(target_id)
            if target_item:
                t_rels = target_item.setdefault("relationships", [])
                if not any(r.get("relation_type") == "contradicts" and r.get("target_id") == source_id for r in t_rels):
                    t_rels.append({
                        "relation_type": "contradicts",
                        "target_id": source_id,
                        "description": description or f"Reciprocal contradiction from {source_id}"
                    })
                    self.update_item(target_id, target_item)

        # Log edge in global graph
        graph_edge_file = os.path.join(self.knowledge_dir, "graph_edges.jsonl")
        edge_entry = {
            "source_id": source_id,
            "target_id": target_id,
            "relation_type": relation_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(graph_edge_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(edge_entry, ensure_ascii=False) + "\n")

        return True

    def get_relationships(self, item_id: str, relation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve all relationships (outgoing and incoming) associated with an item."""
        results = []
        item = self.get_item(item_id)
        if item and "relationships" in item:
            for r in item["relationships"]:
                if relation_type is None or r.get("relation_type") == relation_type:
                    results.append({
                        "direction": "outgoing",
                        "relation_type": r.get("relation_type"),
                        "related_id": r.get("target_id"),
                        "description": r.get("description", "")
                    })

        # Scan global graph edges for incoming links
        graph_edge_file = os.path.join(self.knowledge_dir, "graph_edges.jsonl")
        if os.path.isfile(graph_edge_file):
            with open(graph_edge_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        edge = json.loads(line)
                        if edge.get("target_id") == item_id:
                            r_type = edge.get("relation_type")
                            inv_type = self.INVERSE_RELATIONSHIPS.get(r_type, f"inverse_{r_type}")
                            if relation_type is None or r_type == relation_type or inv_type == relation_type:
                                results.append({
                                    "direction": "incoming",
                                    "relation_type": inv_type,
                                    "original_relation": r_type,
                                    "related_id": edge.get("source_id"),
                                    "description": edge.get("description", "")
                                })
                    except Exception:
                        continue
        return results

    def get_contradictions(self, item_id: str) -> List[Dict[str, Any]]:
        """Retrieve all explicit contradictory paradigms or competing approaches."""
        item = self.get_item(item_id)
        contradictions = []
        if item and "contradictions" in item:
            for c in item["contradictions"]:
                contradictions.append({
                    "type": "internal_paradigm_rejection",
                    "competing_approach": c.get("competing_approach"),
                    "rejection_rationale": c.get("rejection_rationale")
                })
        rel_contradictions = self.get_relationships(item_id, relation_type="contradicts")
        for rc in rel_contradictions:
            contradictions.append({
                "type": "relational_contradiction",
                "related_id": rc.get("related_id"),
                "description": rc.get("description")
            })
        return contradictions

    def add_contradiction_record(self, contradiction_dict: Dict[str, Any]) -> str:
        """
        Validate and store a detected contradiction record between learned directives.
        Enforces Phase 27: Initial status and stage default strictly to CONFLICT_DETECTED.
        """
        item = dict(contradiction_dict)
        item.setdefault("contract_version", "1.0.0")
        item.setdefault("status", "CONFLICT_DETECTED")
        item.setdefault("stage", item.get("status", "CONFLICT_DETECTED"))
        item.setdefault("detected_at", datetime.now(timezone.utc).isoformat())

        if "contradiction_id" not in item:
            item["contradiction_id"] = f"CTD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        val_res = validate_contradiction_record(item)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid contradiction contract: {val_res.get('errors')}")

        file_path = os.path.join(self.contradictions_dir, f"{item['contradiction_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)

        self._append_index(
            self.contradictions_dir,
            {
                "contradiction_id": item["contradiction_id"],
                "target_skill": item["target_skill"],
                "lesson_a_id": item["lesson_a_id"],
                "lesson_b_id": item["lesson_b_id"],
                "conflict_type": item["conflict_type"],
                "stage": item.get("stage", item["status"]),
                "status": item["status"],
                "detected_at": item["detected_at"],
                "file_path": file_path
            }
        )

        # Link in relationship graph if items exist in store
        try:
            self.link_items(
                source_id=item["lesson_a_id"],
                target_id=item["lesson_b_id"],
                relation_type="contradicts",
                description=f"Contradiction recorded ({item.get('stage', item['status'])}): {item['conflict_type']}"
            )
        except Exception:
            pass

        return item["contradiction_id"]

    def get_active_contradictions(
        self,
        target_skill: Optional[str] = None,
        capability: Optional[str] = None,
        include_resolved: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve active contradiction records to inform applicability conditions.
        By default, returns unresolved or in-progress contradictions (status != 'RESOLVED').
        """
        canon_cap = self.normalize_capability(capability)
        results = []
        if not os.path.isdir(self.contradictions_dir):
            return results

        for fn in os.listdir(self.contradictions_dir):
            if not fn.endswith(".json") or fn == "index.jsonl":
                continue
            fp = os.path.join(self.contradictions_dir, fn)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    rec = json.load(f)
                if not include_resolved and rec.get("status") in ["RESOLVED", "RESOLVED_WITH_CONDITIONS"]:
                    continue
                if target_skill and rec.get("target_skill") != target_skill:
                    continue
                if canon_cap and canon_cap.lower() not in json.dumps(rec).lower():
                    continue
                results.append(rec)
            except Exception:
                continue

        return results

    # -------------------------------------------------------------------------
    # Versioning & Superseding
    # -------------------------------------------------------------------------

    def supersede_item(
        self,
        old_id: str,
        new_item_data: Dict[str, Any],
        rationale: str = ""
    ) -> str:
        """
        Supersede an existing knowledge item with a new version.
        Marks old item SUPERSEDED, creates new item with incremented version and links them.
        """
        old_item = self.get_item(old_id)
        if not old_item:
            raise FileNotFoundError(f"Item '{old_id}' to supersede was not found.")

        # Update old item status
        old_item["status"] = "SUPERSEDED"
        old_item["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.update_item(old_id, old_item)

        # Prepare new item
        new_item = dict(new_item_data)
        new_item.pop("knowledge_id", None)
        new_item.pop("anti_pattern_id", None)
        new_item.pop("exemplar_id", None)
        new_item.pop("lesson_id", None)
        new_item.pop("item_id", None)
        new_item.setdefault("status", "ACCEPTED_ACTIVE")
        new_item.setdefault("updated_at", datetime.now(timezone.utc).isoformat())

        # Version bump logic
        old_ver = old_item.get("version", "1.0.0")
        try:
            parts = [int(p) for p in old_ver.split(".")]
            parts[1] += 1  # Increment minor version
            new_item["version"] = ".".join(str(p) for p in parts)
        except Exception:
            new_item["version"] = "2.0.0"

        # Determine item kind and add
        item_type = new_item.get("item_type", old_item.get("item_type", "principle"))
        if item_type == "pattern":
            new_id = self.add_pattern(new_item)
        elif item_type == "anti_pattern":
            new_id = self.add_anti_pattern(new_item)
        elif item_type == "exemplar":
            new_id = self.add_exemplar(new_item)
        else:
            new_id = self.add_principle(new_item)

        # Link relationships
        self.link_items(
            new_id,
            old_id,
            relation_type="supersedes",
            description=rationale or f"Supersedes {old_id} version {old_ver}"
        )
        self.link_items(
            old_id,
            new_id,
            relation_type="derived_from",
            description=f"Superseded by {new_id} version {new_item['version']}"
        )

        return new_id

    # -------------------------------------------------------------------------
    # Scope Containment & Filtering
    # -------------------------------------------------------------------------

    def is_in_scope(
        self,
        item: Dict[str, Any],
        query_project_id: Optional[str] = None,
        query_domain: Optional[str] = None,
        target_capability: Optional[str] = None
    ) -> bool:
        """
        Evaluate scope containment:
        - project / global-in-project: strictly quarantined to matching query_project_id.
          Never leaked if query_project_id is None or mismatched.
        - domain: matches if domain matches or broadly compatible.
        - cross-project: universally matches across projects.
        """
        if target_capability and not query_domain:
            t_cap = target_capability.lower()
            if "qualitative" in t_cap:
                query_domain = "qualitative"
            elif any(k in t_cap for k in ["stat", "regression", "mediation", "sem", "cfa"]):
                query_domain = "quantitative"
            else:
                query_domain = target_capability

        raw_scope = str(item.get("scope", "cross-project")).strip().lower()
        item_proj = item.get("project_id") or item.get("context", {}).get("project_id") or item.get("metadata", {}).get("project_id")

        if raw_scope in ["project", "global-in-project", "project_specific"]:
            if not query_project_id:
                return False
            return bool(item_proj and item_proj == query_project_id)

        # Hard domain boundary check (ATK-07 Hardening)
        if query_domain:
            q_dom = query_domain.lower()
            item_dom = str(item.get("domain", "")).strip().lower()
            item_tags = [str(t).lower() for t in item.get("tags", [])]
            item_text = (str(item.get("statement", "")) + " " + str(item.get("desired_behavior", "")) + " " + str(item.get("defective_pattern", ""))).lower()
            if q_dom == "qualitative":
                if item_dom in ["quantitative", "statistics", "regression", "mediation", "moderation", "sem", "cfa", "descriptive", "statistical-data-analyst"]:
                    return False
                if any(t in item_tags for t in ["quantitative", "sphericity", "mauchly"]):
                    return False
                if any(k in item_text for k in ["sphericity", "homoscedasticity", "levene", "shapiro-wilk", "mauchly", "f_value"]):
                    return False
            elif q_dom == "quantitative":
                if item_dom in ["qualitative", "thematic", "grounded_theory", "interviews", "qualitative-data-analyst"]:
                    return False
                if any(t in item_tags for t in ["qualitative", "thematic"]):
                    return False
                if any(k in item_text for k in ["sphericity", "homoscedasticity", "levene", "shapiro-wilk", "mauchly", "f_value"]):
                    return False
            elif q_dom == "quantitative":
                if item_dom in ["qualitative", "thematic", "grounded_theory", "interviews"]:
                    return False

        if raw_scope in ["domain", "domain_wide"]:
            if query_domain:
                item_domain = str(item.get("domain", "")).strip().lower()
                applicability = item.get("applicability", {})
                skills = applicability.get("target_skills", [])
                designs = applicability.get("target_designs", [])
                if item_domain and item_domain != query_domain.lower():
                    # Check if query_domain is in target_skills or designs
                    if query_domain.lower() not in [s.lower() for s in skills] and query_domain.lower() not in [d.lower() for d in designs]:
                        return False
            return True

        # cross-project or universal
        return True

    # -------------------------------------------------------------------------
    # Capability Skill-Memory Accumulation
    # -------------------------------------------------------------------------

    def record_capability_event(
        self,
        capability: str,
        event_type: str,
        record_data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Accumulate experience into the capability-isolated skill memory store.
        Supported event_types:
          successful_examples, failures, lessons, anti_patterns,
          related_knowledge, evaluation_cases, evaluation_history.
        """
        canon_cap = self.normalize_capability(capability)
        if not canon_cap:
            raise ValueError(f"Unknown capability '{capability}'.")

        cap_dir = os.path.join(self.skill_memory_dir, canon_cap)
        os.makedirs(cap_dir, exist_ok=True)
        record_file = os.path.join(cap_dir, "memory_record.json")

        # Load or initialize record
        if os.path.isfile(record_file):
            with open(record_file, "r", encoding="utf-8") as f:
                memory_rec = json.load(f)
        else:
            memory_rec = {
                "contract_version": "1.0.0",
                "record_id": f"SMR-{canon_cap.upper()}-001",
                "skill_name": canon_cap,
                "capability": canon_cap,
                "total_invocations": 0,
                "success_count": 0,
                "failure_count": 0,
                "average_duration_seconds": 0.0,
                "common_failure_modes": [],
                "calibrated_parameter_defaults": {},
                "last_evaluated_at": datetime.now(timezone.utc).isoformat(),
                "successful_examples": [],
                "failures": [],
                "lessons": [],
                "anti_patterns": [],
                "related_knowledge": [],
                "evaluation_cases": [],
                "evaluation_history": []
            }

        # Update telemetry
        memory_rec["total_invocations"] += 1
        memory_rec["last_evaluated_at"] = datetime.now(timezone.utc).isoformat()

        # Handle specific event types
        if event_type == "successful_examples":
            memory_rec["success_count"] += 1
            entry = record_data if isinstance(record_data, dict) else {"exemplar_id": str(record_data)}
            if not any(e.get("exemplar_id") == entry.get("exemplar_id") for e in memory_rec["successful_examples"]):
                memory_rec["successful_examples"].append(entry)

        elif event_type == "failures":
            memory_rec["failure_count"] += 1
            entry = record_data if isinstance(record_data, dict) else {"experience_id": str(record_data), "defect_type": "GENERAL_DEFECT"}
            if not any(e.get("experience_id") == entry.get("experience_id") for e in memory_rec["failures"]):
                memory_rec["failures"].append(entry)
            # Update common failure modes
            dtype = entry.get("defect_type", "UNKNOWN")
            modes = memory_rec["common_failure_modes"]
            found = False
            for m in modes:
                if m.get("failure_type") == dtype:
                    m["frequency"] += 1
                    found = True
                    break
            if not found:
                modes.append({
                    "failure_type": dtype,
                    "frequency": 1,
                    "typical_remedy": metadata.get("typical_remedy", "Investigate diagnostic checklists.") if metadata else "Investigate diagnostic checklists."
                })

        elif event_type == "lessons":
            l_id = str(record_data)
            if l_id not in memory_rec["lessons"]:
                memory_rec["lessons"].append(l_id)

        elif event_type == "anti_patterns":
            ap_id = str(record_data)
            if ap_id not in memory_rec["anti_patterns"]:
                memory_rec["anti_patterns"].append(ap_id)

        elif event_type == "related_knowledge":
            knw_id = str(record_data)
            if knw_id not in memory_rec["related_knowledge"]:
                memory_rec["related_knowledge"].append(knw_id)

        elif event_type == "evaluation_cases":
            ec_id = str(record_data)
            if ec_id not in memory_rec["evaluation_cases"]:
                memory_rec["evaluation_cases"].append(ec_id)

        elif event_type == "evaluation_history":
            entry = record_data if isinstance(record_data, dict) else {
                "evaluation_id": str(record_data),
                "verdict": "PASS",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            memory_rec["evaluation_history"].append(entry)

        if metadata and "calibrated_parameters" in metadata:
            memory_rec["calibrated_parameter_defaults"].update(metadata["calibrated_parameters"])

        # Validate against schema
        val_res = validate_skill_memory_record(memory_rec)
        if not val_res["valid"]:
            raise ContractValidationError(f"Invalid skill memory contract: {val_res.get('errors')}")

        # Persist
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(memory_rec, f, indent=2, ensure_ascii=False)

        # Append to capability index
        cap_index_file = os.path.join(cap_dir, "index.jsonl")
        with open(cap_index_file, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "record_data": record_data,
                "metadata": metadata or {}
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return memory_rec

    def get_capability_memory(self, capability: str) -> Optional[Dict[str, Any]]:
        """Load capability memory record for a canonical capability."""
        canon_cap = self.normalize_capability(capability)
        if not canon_cap:
            return None
        record_file = os.path.join(self.skill_memory_dir, canon_cap, "memory_record.json")
        if os.path.isfile(record_file):
            with open(record_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    # -------------------------------------------------------------------------
    # Phase 29: Two-Stage Knowledge Retrieval Engine
    # -------------------------------------------------------------------------

    def retrieve_two_stage(
        self,
        task: Optional[str] = None,
        agent: Optional[str] = None,
        skill: Optional[str] = None,
        capability: Optional[str] = None,
        domain: Optional[str] = None,
        failure_type: Optional[str] = None,
        scope: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        prompt_text: Optional[str] = None,
        item_types: Optional[List[str]] = None,
        include_superseded: bool = False,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Execute full Phase 29 Two-Stage Knowledge Retrieval.
        Stage 1: Hard Filtering (capability, domain, skill, task, failure_type, scope, status).
        Stage 2: Semantic Ranking (relevance, context_similarity, evidence_strength, recency, confidence, contradiction).
        Returns the auditable AcademicKnowledgeRetrievalRecord validated against knowledge_retrieval.schema.json.
        """
        canon_cap = self.normalize_capability(capability)
        scan_dirs = []
        if not item_types or "lesson" in item_types:
            scan_dirs.append((self.lessons_dir, "lesson"))
        if not item_types or "principle" in item_types:
            scan_dirs.append((self.principles_dir, "principle"))
        if not item_types or "pattern" in item_types:
            scan_dirs.append((self.patterns_dir, "pattern"))
        if not item_types or "anti_pattern" in item_types:
            scan_dirs.append((self.anti_patterns_dir, "anti_pattern"))
        if not item_types or "exemplar" in item_types:
            scan_dirs.append((self.exemplars_dir, "exemplar"))

        raw_items: List[Dict[str, Any]] = []
        for d, itype in scan_dirs:
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                if not fn.endswith(".json") or fn == "index.jsonl":
                    continue
                fp = os.path.join(d, fn)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        item = json.load(f)
                        raw_items.append(item)
                except Exception:
                    continue

        query_payload = {
            "task": task,
            "agent": agent,
            "skill": skill,
            "capability": canon_cap,
            "domain": domain,
            "failure_type": failure_type,
            "scope": scope,
            "tags": tags or [],
            "project_id": project_id,
            "prompt_text": prompt_text,
            "item_types": item_types,
            "include_superseded": include_superseded,
            "limit": limit
        }

        active_ctds = self.get_active_contradictions(target_skill=skill, capability=canon_cap)
        return self.retriever.retrieve(
            items=raw_items,
            query=query_payload,
            active_contradictions=active_ctds
        )

    def query(
        self,
        agent: Optional[str] = None,
        domain: Optional[str] = None,
        skill: Optional[str] = None,
        task: Optional[str] = None,
        capability: Optional[str] = None,
        failure_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        item_types: Optional[List[str]] = None,
        include_superseded: bool = False,
        limit: int = 20,
        prompt_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multi-criteria query across lessons, patterns, anti-patterns, principles, and exemplars.
        Utilizes Phase 29 Two-Stage Retrieval (Stage 1 Hard Filtering -> Stage 2 Semantic Ranking).
        Returns list of top-ranked items for backwards compatibility.
        """
        record = self.retrieve_two_stage(
            task=task,
            agent=agent,
            skill=skill,
            capability=capability,
            domain=domain,
            failure_type=failure_type,
            tags=tags,
            project_id=project_id,
            prompt_text=prompt_text,
            item_types=item_types,
            include_superseded=include_superseded,
            limit=limit
        )
        return record.get("results", [])

    # -------------------------------------------------------------------------
    # Pre-Task Retrieval Briefing
    # -------------------------------------------------------------------------

    def retrieve_pre_task_context(
        self,
        task: Optional[str] = None,
        agent: Optional[str] = None,
        skill: Optional[str] = None,
        capability: Optional[str] = None,
        domain: Optional[str] = None,
        failure_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        limit_per_category: int = 5,
        task_description: Optional[str] = None,
        max_token_budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Produce an actionable pre-flight briefing for an agent prior to beginning execution.
        Returns relevant lessons (what to do / what not to do), anti-patterns to avoid,
        gold-standard exemplars to emulate, and applicable principles.
        """
        effective_task = task or task_description or ""
        canon_cap = self.normalize_capability(capability)
        effective_domain = domain
        if not effective_domain and canon_cap:
            if "qualitative" in canon_cap.lower():
                effective_domain = "qualitative"
            elif any(k in canon_cap.lower() for k in ["statistical", "regression", "sem", "cfa", "mediation", "moderation", "reliability", "descriptive", "assumption"]):
                effective_domain = "quantitative"

        # Query lessons
        lessons = self.query(
            agent=agent,
            domain=effective_domain,
            skill=skill,
            task=effective_task,
            capability=canon_cap,
            tags=tags,
            project_id=project_id,
            item_types=["lesson"],
            limit=limit_per_category
        )

        # Contradiction Filtering (ATK-06 Hardening)
        active_contradictions = self.get_active_contradictions(target_skill=skill, capability=canon_cap)
        disputed_lesson_ids = set()
        for c in active_contradictions:
            disputed_lesson_ids.add(c.get("lesson_a_id"))
            disputed_lesson_ids.add(c.get("lesson_b_id"))

        if disputed_lesson_ids:
            lessons = [l for l in lessons if (l.get("lesson_id") or l.get("item_id")) not in disputed_lesson_ids]

        # Query anti-patterns
        f_type = failure_types[0] if failure_types else None
        anti_patterns = self.query(
            agent=agent,
            domain=domain,
            skill=skill,
            task=task,
            capability=canon_cap,
            failure_type=f_type,
            tags=tags,
            project_id=project_id,
            item_types=["anti_pattern"],
            limit=limit_per_category
        )

        # Query exemplars
        exemplars = self.query(
            agent=agent,
            domain=domain,
            skill=skill,
            task=task,
            capability=canon_cap,
            tags=tags,
            project_id=project_id,
            item_types=["exemplar"],
            limit=limit_per_category
        )

        # Query principles and patterns
        principles = self.query(
            agent=agent,
            domain=domain,
            skill=skill,
            task=task,
            capability=canon_cap,
            tags=tags,
            project_id=project_id,
            item_types=["principle"],
            limit=limit_per_category
        )

        patterns = self.query(
            agent=agent,
            domain=domain,
            skill=skill,
            task=task,
            capability=canon_cap,
            tags=tags,
            project_id=project_id,
            item_types=["pattern"],
            limit=limit_per_category
        )

        # Also retrieve capability memory summary if capability is specified
        cap_memory = self.get_capability_memory(canon_cap) if canon_cap else None

        briefing = {
            "query_context": {
                "task": task,
                "agent": agent,
                "skill": skill,
                "capability": canon_cap,
                "domain": domain,
                "project_id": project_id,
                "briefing_generated_at": datetime.now(timezone.utc).isoformat()
            },
            "lessons": lessons,
            "anti_patterns": anti_patterns,
            "exemplars": exemplars,
            "principles": principles,
            "patterns": patterns,
            "contradictions": self.get_active_contradictions(target_skill=skill, capability=canon_cap),
            "capability_summary": {
                "total_invocations": cap_memory.get("total_invocations", 0) if cap_memory else 0,
                "success_count": cap_memory.get("success_count", 0) if cap_memory else 0,
                "failure_count": cap_memory.get("failure_count", 0) if cap_memory else 0,
                "calibrated_parameter_defaults": cap_memory.get("calibrated_parameter_defaults", {}) if cap_memory else {}
            } if cap_memory else None
        }

        try:
            from scripts.academic_context_token_budgeter import AcademicContextTokenBudgeter
        except ImportError:
            from academic_context_token_budgeter import AcademicContextTokenBudgeter

        budgeter = AcademicContextTokenBudgeter(default_budget=max_token_budget or 800)
        budgeted = budgeter.budget_context(
            raw_context=briefing,
            max_token_budget=max_token_budget,
            target_capability=canon_cap or "General",
            task=effective_task or "general_task",
            agent=agent or "academic-orchestrator",
            project_id=project_id or "cross-project"
        )

        if max_token_budget is not None:
            briefing["lessons"] = budgeted["relevant_lessons"]
            briefing["anti_patterns"] = budgeted["known_pitfalls"]
            briefing["exemplars"] = budgeted["exemplars"]
            briefing["contradictions"] = budgeted["applicable_methodology_rules"]
            briefing["budget_telemetry"] = budgeted["budget_telemetry"]
            briefing["formatted_briefing"] = budgeted["formatted_briefing"]
        else:
            briefing["budget_telemetry"] = {
                "max_token_budget": None,
                "estimated_tokens_used": budgeted["budget_telemetry"]["estimated_tokens_used"],
                "budget_utilization_ratio": 1.0,
                "compression_mode": "STANDARD",
                "items_selected": budgeted["budget_telemetry"]["items_selected"],
                "items_pruned_by_budget": 0,
                "pruned_details": []
            }
            briefing["formatted_briefing"] = budgeted["formatted_briefing"]

        return briefing

    # -------------------------------------------------------------------------
    # Helper utilities
    # -------------------------------------------------------------------------

    def _append_index(self, directory: str, summary_entry: Dict[str, Any]):
        """Append summary record to local index.jsonl."""
        index_file = os.path.join(directory, "index.jsonl")
        with open(index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(summary_entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Persistent Knowledge Manager CLI")
    parser.add_argument(
        "--action",
        choices=["pre_task", "query", "show_memory", "link", "teach", "list", "search", "supersede"],
        default="pre_task"
    )
    parser.add_argument("--task", help="Target task type (e.g. bootstrap_mediation)")
    parser.add_argument("--capability", help="Capability (e.g. mediation, SEM, psychometrics)")
    parser.add_argument("--agent", help="Agent role name")
    parser.add_argument("--skill", help="Skill name")
    parser.add_argument("--domain", help="Domain filter")
    parser.add_argument("--tags", nargs="*", help="List of tags")
    parser.add_argument("--project-id", help="Project ID for scope containment")
    parser.add_argument("--category", help="Category for teach/list/search (principle, pattern, anti_pattern, lesson)")
    parser.add_argument("--statement", help="Instruction or rule statement for teach/supersede")
    parser.add_argument("--rationale", help="Empirical justification or reasoning")
    parser.add_argument("--old-id", help="ID of old knowledge item to supersede")
    parser.add_argument("--query", help="Search query string")
    parser.add_argument("--scope", default="cross-project", help="Scope containment (default: cross-project)")
    args = parser.parse_args()

    km = AcademicKnowledgeManager()

    if args.action == "pre_task":
        briefing = km.retrieve_pre_task_context(
            task=args.task or "general_task",
            agent=args.agent,
            skill=args.skill,
            capability=args.capability,
            domain=args.domain,
            tags=args.tags,
            project_id=args.project_id
        )
        print(json.dumps(briefing, indent=2, ensure_ascii=False))

    elif args.action == "show_memory":
        if not args.capability:
            print("Error: --capability required for show_memory", file=sys.stderr)
            sys.exit(1)
        mem = km.get_capability_memory(args.capability)
        print(json.dumps(mem, indent=2, ensure_ascii=False))

    elif args.action == "query":
        results = km.query(
            agent=args.agent,
            domain=args.domain,
            skill=args.skill,
            task=args.task,
            capability=args.capability,
            tags=args.tags,
            project_id=args.project_id
        )
        print(json.dumps(results, indent=2, ensure_ascii=False))

    elif args.action == "teach":
        if not args.statement:
            print("Error: --statement required for teach action", file=sys.stderr)
            sys.exit(1)
        from scripts.academic_human_mentor import AcademicHumanMentor
        mentor = AcademicHumanMentor()
        res = mentor.teach(
            category=args.category or "principle",
            statement=args.statement,
            rationale=args.rationale,
            capability=args.capability,
            tags=args.tags,
            scope=args.scope,
            agent=args.agent
        )
        print(res["badge"])

    elif args.action == "list":
        from scripts.academic_human_mentor import AcademicHumanMentor
        mentor = AcademicHumanMentor()
        items = mentor.list_knowledge(category=args.category, capability=args.capability)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.action == "search":
        if not args.query:
            print("Error: --query required for search action", file=sys.stderr)
            sys.exit(1)
        from scripts.academic_human_mentor import AcademicHumanMentor
        mentor = AcademicHumanMentor()
        items = mentor.search_knowledge(query=args.query, category=args.category, capability=args.capability)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.action == "supersede":
        if not args.old_id or not args.statement:
            print("Error: --old-id and --statement required for supersede action", file=sys.stderr)
            sys.exit(1)
        from scripts.academic_human_mentor import AcademicHumanMentor
        mentor = AcademicHumanMentor()
        res = mentor.supersede(old_id=args.old_id, new_statement=args.statement, rationale=args.rationale or "Updated")
        print(res["badge"])


if __name__ == "__main__":
    main()
