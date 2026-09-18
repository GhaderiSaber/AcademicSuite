#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_task_router.py — Capability Resolver & Academic Task Router Engine ("The Hands")

Resolves user academic research tasks into authoritative capability requirements:
USER TASK
  → REQUIRED CAPABILITIES (from config/capabilities.yaml)
  → DURABLE AGENT
  → REQUIRED SUBAGENTS (Execution Worker, Reviewer, Challenger)
  → SKILLS
  → DETERMINISTIC EXECUTION
  → VALIDATION

Preserves backwards compatibility with existing pipeline interfaces.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, Any, List, Optional, Set, Tuple

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# =============================================================================
# 1. Authoritative Capability Registry Loader
# =============================================================================

DEFAULT_CAPABILITIES_PATH = os.path.join(ROOT_DIR, "config", "capabilities.yaml")


class CapabilityRegistry:
    """Loads, validates, and queries the authoritative capabilities registry."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CAPABILITIES_PATH
        self.capabilities: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.config_path):
            if HAS_YAML:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    self.capabilities = data.get("capabilities", {})
            else:
                # Fallback: simple text/json parsing or error logging
                sys.stderr.write(f"[CapabilityRegistry WARNING] PyYAML not found. Using fallback.\n")
                self.capabilities = {}
        else:
            sys.stderr.write(f"[CapabilityRegistry WARNING] Config file not found at {self.config_path}.\n")
            self.capabilities = {}

    def get(self, capability_id: str) -> Optional[Dict[str, Any]]:
        return self.capabilities.get(capability_id)

    def all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        return dict(self.capabilities)

    def all_ids(self) -> List[str]:
        return list(self.capabilities.keys())


# Singleton registry instance
_GLOBAL_REGISTRY = CapabilityRegistry()


# =============================================================================
# 2. Legacy Macro Categories & Metadata (Backwards Compatibility)
# =============================================================================

CAPABILITY_METADATA = {
    "RESEARCH": {
        "agent": "research-agent",
        "primary_skill": "literature-review",
        "skill_path": ".agents/skills/literature-review/SKILL.md",
        "input_artifact": "academic-state/requirements.json",
        "output_artifact": "academic-state/requirements.json",
        "description": "Scientific literature harvesting, theoretical foundations, and research question formulation"
    },
    "METHODOLOGY": {
        "agent": "research-agent",
        "primary_skill": "methodology-review",
        "skill_path": ".agents/skills/methodology-review/SKILL.md",
        "input_artifact": "academic-state/requirements.json",
        "output_artifact": "academic-state/analysis_plan.json",
        "description": "Research design formulation, G*Power sampling determination, and validity safeguards"
    },
    "DATA": {
        "agent": "data-agent",
        "primary_skill": "data-cleaning",
        "skill_path": ".agents/skills/data-cleaning/SKILL.md",
        "input_artifact": "projects/*/01_raw_inputs/*",
        "output_artifact": "academic-state/data/data_quality.json",
        "description": "Raw dataset ingestion, scale reverse-coding, missing value screening, and quality auditing"
    },
    "NETWORK-ANALYSIS": {
        "agent": "statistics-agent",
        "primary_skill": "network-analysis",
        "skill_path": ".agents/skills/network-analysis/SKILL.md",
        "input_artifact": "academic-state/data/data_dictionary.json",
        "output_artifact": "academic-state/analysis/network_results.json",
        "description": "Bibliometric network mapping, keyword co-occurrence, and citation centrality analysis"
    },
    "STATISTICS": {
        "agent": "statistics-agent",
        "primary_skill": "sem",
        "skill_path": ".agents/skills/sem/SKILL.md",
        "input_artifact": "academic-state/data/data_quality.json",
        "output_artifact": "academic-state/analysis/sem.json",
        "description": "Deterministic inferential modeling (SEM, CFA, ANCOVA, regression, mediation, reliability)"
    },
    "WRITING": {
        "agent": "writing-agent",
        "primary_skill": "chapter-4-writing",
        "skill_path": ".agents/skills/chapter-4-writing/SKILL.md",
        "input_artifact": "academic-state/analysis/sem.json",
        "output_artifact": "academic-state/outputs/Chapter_4_Results.docx",
        "description": "Scholarly narrative formulation, APA 7 3-line tables, and OpenXML institutional typography"
    },
    "VALIDATION": {
        "agent": "validation-agent",
        "primary_skill": "thesis-integrity-auditor",
        "skill_path": ".agents/skills/thesis-integrity-auditor/SKILL.md",
        "input_artifact": "academic-state/outputs/*",
        "output_artifact": "academic-state/validation/statistical_validation.json",
        "description": "Independent adversarial verification of df, numerical consistency, and APA reporting rules"
    }
}

EXECUTION_ORDER = [
    "RESEARCH",
    "METHODOLOGY",
    "DATA",
    "NETWORK-ANALYSIS",
    "STATISTICS",
    "WRITING",
    "VALIDATION"
]


# =============================================================================
# 3. Modern Capability Resolver
# =============================================================================

class CapabilityResolver:
    """
    Answers: 'What capabilities are required?'
    Resolves tasks into required capabilities, durable primary agents,
    required subagents (worker, reviewer, challenger), skills, and validation rules.
    """

    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or _GLOBAL_REGISTRY

    def resolve(self, prompt: str, requested_capabilities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main capability resolution method.
        Returns:
            status: "RESOLVED" | "AMBIGUOUS" | "BLOCKED"
        """
        p = prompt.strip()
        p_lower = p.lower()

        # 1. Unknown / Out-of-domain detection
        # Tasks that are clearly not academic capabilities supported by the system
        prohibited_or_unknown_patterns = [
            r"\bquantum\s+(?:neural\s+network|computing|deep\s+learning)\b",
            r"\bcryptocurrency\b|\bbitcoin\b|\bethereum\b|\bmine\s+crypto\b",
            r"\bgenome\s+sequencing\b|\bdna\s+alignment\b",
            r"\bweather\s+forecast(?:ing)?\b",
            r"\bweb\s+scraping\s+bot\b"
        ]
        for pat in prohibited_or_unknown_patterns:
            if re.search(pat, p_lower):
                return {
                    "status": "BLOCKED",
                    "task_prompt": prompt,
                    "reason": f"Unknown capability requested matching pattern '{pat}'. No matching capability registered in config/capabilities.yaml. Explicit human escalation required.",
                    "required_capabilities": [],
                    "escalation_required": True
                }

        # 2. Check if specific capability IDs were directly requested
        detected_caps: Set[str] = set()
        if requested_capabilities:
            for cap in requested_capabilities:
                if self.registry.get(cap):
                    detected_caps.add(cap)
                else:
                    return {
                        "status": "BLOCKED",
                        "task_prompt": prompt,
                        "reason": f"Unknown capability ID explicitly requested: '{cap}'. Not found in registry.",
                        "required_capabilities": [],
                        "escalation_required": True
                    }

        # 3. Intent Pattern Matching against Registry
        for cap_id, cap_meta in self.registry.all_capabilities().items():
            patterns = cap_meta.get("intent_patterns", [])
            for pat in patterns:
                if re.search(pat, p_lower):
                    detected_caps.add(cap_id)
                    break

        # 4. Check for Ambiguous Capability requests
        # e.g., "Run regression" could be multiple regression, or moderation, or meta-analysis regression
        # e.g., "Analyze this model" without indicating what model
        if re.search(r'^\s*(?:run|do|perform)\s+regression\s*$', p_lower):
            return {
                "status": "AMBIGUOUS",
                "task_prompt": prompt,
                "reason": "Ambiguous regression capability requested. Task does not specify whether Multiple Regression, Hierarchical Regression, or Moderation Interaction is required.",
                "candidate_capabilities": ["regression", "moderation"],
                "clarification_prompt": "Please specify the exact model type: Standard Multiple Regression, Hierarchical Blockwise Regression, or Moderation (PROCESS Model 1)."
            }

        if re.search(r'^\s*(?:do|perform|run)\s+(?:advanced\s+)?modeling\s*$', p_lower):
            return {
                "status": "AMBIGUOUS",
                "task_prompt": prompt,
                "reason": "Ambiguous modeling capability requested. Task does not specify whether SEM, CFA, ANCOVA, or LMM is required.",
                "candidate_capabilities": ["sem", "cfa", "ancova", "linear_mixed_model"],
                "clarification_prompt": "Please specify the statistical modeling family: Structural Equation Modeling (SEM), Confirmatory Factor Analysis (CFA), ANCOVA, or Linear Mixed Model (LMM)."
            }

        # 5. Fallback heuristics for macro queries if pattern matching yielded empty
        if not detected_caps:
            # Check if canonical macro prompts match
            if re.search(r'\banalyz(?:e|ing)\s+(?:this\s+|the\s+|these\s+)?(?:data|dataset)\b', p_lower):
                detected_caps.add("data_cleaning")
                detected_caps.add("descriptive_statistics")
            elif re.search(r'\b(?:write|draft)\s+chapter\s*4\b', p_lower) or re.search(r'\bresults\s+chapter\b', p_lower):
                detected_caps.add("thesis_chapter4")
            elif re.search(r'\b(?:find|identify)\s+research\s+gaps?\b', p_lower):
                detected_caps.add("literature_review")
                detected_caps.add("research_methodology")
            elif re.search(r'\b(?:perform|run)\s+cfa\s+and\s+sem\b', p_lower):
                detected_caps.add("cfa")
                detected_caps.add("sem")
            elif re.search(r'\bnetwork\s+data\b', p_lower):
                detected_caps.add("network_analysis")

        # If still empty, check for general domain keywords
        if not detected_caps:
            if any(w in p_lower for w in ["clean", "reverse code", "scoring", "dataset"]):
                detected_caps.add("data_cleaning")
            if any(w in p_lower for w in ["descriptive", "mean", "std", "demographics"]):
                detected_caps.add("descriptive_statistics")
            if any(w in p_lower for w in ["literature", "pubmed", "crossref", "review"]):
                detected_caps.add("literature_review")
            if any(w in p_lower for w in ["sem", "path model"]):
                detected_caps.add("sem")
            if any(w in p_lower for w in ["cfa", "factor loading"]):
                detected_caps.add("cfa")
            if any(w in p_lower for w in ["mediation", "indirect effect"]):
                detected_caps.add("mediation")
            if any(w in p_lower for w in ["moderation", "interaction effect"]):
                detected_caps.add("moderation")
            if any(w in p_lower for w in ["ancova"]):
                detected_caps.add("ancova")
            if any(w in p_lower for w in ["chapter 4", "findings"]):
                detected_caps.add("thesis_chapter4")
            if any(w in p_lower for w in ["chapter 5", "discussion"]):
                detected_caps.add("thesis_chapter5")

        # If still empty after checking keywords, it is unknown
        if not detected_caps:
            return {
                "status": "BLOCKED",
                "task_prompt": prompt,
                "reason": f"Unknown capability requested. The prompt does not match any registered academic capability in config/capabilities.yaml. Explicit human review required.",
                "required_capabilities": [],
                "escalation_required": True
            }

        # 6. Topological Dependency Resolution
        # Expand dependencies recursively and order topologically
        resolved_order = self._resolve_dependencies(list(detected_caps))

        # 7. Synthesize Subagent, Skill, Artifact, and Validation Requirements
        primary_agents: Set[str] = set()
        execution_workers: List[str] = []
        reviewers: List[str] = []
        challengers: List[str] = []
        required_skills: List[str] = []
        required_artifacts: List[str] = []
        output_artifacts: List[str] = []
        validation_requirements: List[str] = []

        ordered_execution_chain = []

        for idx, cap_id in enumerate(resolved_order, 1):
            meta = self.registry.get(cap_id)
            if not meta:
                continue

            p_agent = meta.get("primary_agent", "academic-orchestrator")
            primary_agents.add(p_agent)

            worker = meta.get("execution_worker")
            if worker and worker not in execution_workers:
                execution_workers.append(worker)

            rev = meta.get("reviewer")
            if rev and rev not in reviewers:
                reviewers.append(rev)

            chal = meta.get("challenger")
            if chal and chal not in challengers:
                challengers.append(chal)

            for s in meta.get("required_skills", []):
                if s not in required_skills:
                    required_skills.append(s)

            for ra in meta.get("required_artifacts", []):
                if ra not in required_artifacts:
                    required_artifacts.append(ra)

            for oa in meta.get("output_artifacts", []):
                if oa not in output_artifacts:
                    output_artifacts.append(oa)

            for vr in meta.get("validation_requirements", []):
                if vr not in validation_requirements:
                    validation_requirements.append(vr)

            ordered_execution_chain.append({
                "step": idx,
                "capability_id": cap_id,
                "domain": meta.get("domain", "general"),
                "primary_agent": p_agent,
                "execution_worker": worker,
                "reviewer": rev,
                "challenger": chal,
                "required_skills": meta.get("required_skills", []),
                "description": meta.get("description", "")
            })

        # Determine durable primary agent:
        # Prioritize primary agent of the requested target capability(ies)
        target_primary_agents = set()
        for cap in detected_caps:
            meta = self.registry.get(cap)
            if meta and meta.get("primary_agent"):
                target_primary_agents.add(meta.get("primary_agent"))

        if len(target_primary_agents) == 1:
            durable_primary_agent = list(target_primary_agents)[0]
        elif len(primary_agents) == 1:
            durable_primary_agent = list(primary_agents)[0]
        else:
            durable_primary_agent = "academic-orchestrator"

        # Determine complexity level and compile teamwork boundary package
        try:
            from teamwork_boundary_adapter import classify_complexity, build_teamwork_boundary_package
            c_meta = classify_complexity(prompt, resolved_capabilities=list(detected_caps))
            complexity_level = c_meta["complexity_level"]
            teamwork_boundary = build_teamwork_boundary_package(
                task_description=prompt,
                resolved_capabilities=ordered_execution_chain
            )
        except Exception:
            complexity_level = "L1"
            teamwork_boundary = {}

        return {
            "status": "RESOLVED",
            "task_prompt": prompt,
            "complexity_level": complexity_level,
            "required_capabilities": list(detected_caps),
            "topological_capability_order": resolved_order,
            "durable_agent": durable_primary_agent,
            "required_subagents": {
                "primary_agents": list(primary_agents),
                "execution_workers": execution_workers,
                "reviewers": reviewers,
                "challengers": challengers
            },
            "required_skills": required_skills,
            "required_artifacts": required_artifacts,
            "output_artifacts": output_artifacts,
            "validation_requirements": validation_requirements,
            "ordered_execution_chain": ordered_execution_chain,
            "teamwork_boundary": teamwork_boundary,
            "orchestration_directive": (
                f"Resolved {len(resolved_order)} capability stages ({complexity_level}): {' ──► '.join(resolved_order)}. "
                f"Primary agent: {durable_primary_agent}. Required workers: {', '.join(execution_workers)}. "
                f"Auditors: {', '.join(reviewers)}. Challengers: {', '.join(challengers)}."
            )
        }

    def _resolve_dependencies(self, target_caps: List[str]) -> List[str]:
        """Resolves capability dependencies and returns a topologically sorted list."""
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(cap_id: str):
            if cap_id in visited:
                return
            meta = self.registry.get(cap_id)
            if meta:
                for dep in meta.get("dependencies", []):
                    if dep in self.registry.all_capabilities():
                        dfs(dep)
            visited.add(cap_id)
            order.append(cap_id)

        for cap in target_caps:
            dfs(cap)

        return order


# =============================================================================
# 4. Backwards-Compatible Pipeline Builder & Helper Functions
# =============================================================================

_RESOLVER = CapabilityResolver(_GLOBAL_REGISTRY)


def detect_capabilities(prompt: str) -> List[str]:
    """
    Legacy helper: Returns list of legacy macro category names for prompt.
    Preserves backwards compatibility with tests and callers expecting
    ['DATA', 'STATISTICS'], ['STATISTICS', 'WRITING', 'VALIDATION'], etc.
    """
    p = prompt.lower()
    capabilities: Set[str] = set()

    # Explicit Pattern Rules (Legacy Macro Rules)
    if re.search(r'\banalyz(?:e|ing)\s+(?:this\s+|the\s+|these\s+)?(?:data|dataset)\b', p) or \
       re.search(r'\bexplore\s+(?:this\s+|the\s+|these\s+)?(?:data|dataset)\b', p):
        capabilities.add("DATA")
        capabilities.add("STATISTICS")

    if re.search(r'\b(?:write|draft|generate)\s+chapter\s*4\b', p) or \
       re.search(r'\bchapter\s*4\s+findings\b', p) or \
       re.search(r'\bresults\s+chapter\b', p):
        capabilities.add("STATISTICS")
        capabilities.add("WRITING")
        capabilities.add("VALIDATION")

    if re.search(r'\b(?:find|identify|explore)\s+(?:research\s+)?gaps\b', p) or \
       re.search(r'\bresearch\s+gap\b', p) or \
       re.search(r'\bformulate\s+research\s+questions\b', p):
        capabilities.add("RESEARCH")
        capabilities.add("METHODOLOGY")

    if re.search(r'\b(?:perform|run|execute)\s+cfa\s+(?:and\s+)?sem\b', p) or \
       re.search(r'\bcfa\s+and\s+sem\b', p) or \
       re.search(r'\bsem\s+and\s+cfa\b', p):
        capabilities.add("DATA")
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    if re.search(r'\banalyz(?:e|ing)\s+(?:these\s+|the\s+|this\s+)?network\s+data\b', p) or \
       re.search(r'\bnetwork\s+analysis\b', p) or \
       re.search(r'\bbibliometric\s+network\b', p) or \
       re.search(r'\bco-occurrence\s+network\b', p):
        capabilities.add("DATA")
        capabilities.add("NETWORK-ANALYSIS")
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    # Domain Specific Keyword Heuristics if no macro pattern triggered
    if not capabilities:
        if any(w in p for w in ["data", "dataset", "clean", "reverse code", "missingness", "mcar", "score", "curation"]):
            capabilities.add("DATA")

        if any(w in p for w in ["network", "bibliometric", "vosviewer", "callon", "co-occurrence"]):
            capabilities.add("NETWORK-ANALYSIS")

        if any(w in p for w in ["stat", "sem", "cfa", "regression", "ancova", "anova", "t-test", "descriptive", "reliability", "correlation", "mediation", "moderation"]):
            capabilities.add("STATISTICS")

        if any(w in p for w in ["literature", "pubmed", "crossref", "gap", "background", "theoretical framework", "citation"]):
            capabilities.add("RESEARCH")

        if any(w in p for w in ["methodology", "g*power", "sample size", "experimental design", "validity"]):
            capabilities.add("METHODOLOGY")

        if any(w in p for w in ["write", "writing", "draft", "chapter", "apa", "narrative", "discussion", "prose"]):
            capabilities.add("WRITING")

        if any(w in p for w in ["validate", "validation", "audit", "verify", "check", "qc", "df"]):
            capabilities.add("VALIDATION")

    # Contextual Invariant Complements
    if "WRITING" in capabilities and any(w in p for w in ["chapter 4", "results", "findings"]):
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    if "STATISTICS" in capabilities and any(w in p for w in ["cfa", "sem", "model", "from scratch"]):
        capabilities.add("DATA")
        capabilities.add("VALIDATION")

    ordered_caps = [c for c in EXECUTION_ORDER if c in capabilities]
    if not ordered_caps:
        ordered_caps = ["DATA", "STATISTICS"]

    return ordered_caps


def build_pipeline(prompt: str) -> Dict[str, Any]:
    """
    Backwards-compatible entry point: Generates pipeline specification for prompt,
    enriched with modern CapabilityResolver results.
    """
    legacy_caps = detect_capabilities(prompt)
    steps = []

    for idx, cap_name in enumerate(legacy_caps, 1):
        meta = CAPABILITY_METADATA.get(cap_name, {})
        steps.append({
            "step": idx,
            "capability": cap_name,
            "agent": meta.get("agent", "academic-orchestrator"),
            "skill": meta.get("primary_skill", "academic-suite-orchestrator"),
            "skill_path": meta.get("skill_path", ""),
            "description": meta.get("description", ""),
            "input_artifact": meta.get("input_artifact", ""),
            "output_artifact": meta.get("output_artifact", "")
        })

    capabilities_formula = " + ".join(legacy_caps)
    resolution = _RESOLVER.resolve(prompt)

    return {
        "task_prompt": prompt,
        "capabilities_formula": capabilities_formula,
        "capabilities": legacy_caps,
        "total_steps": len(steps),
        "pipeline": steps,
        "capability_resolution": resolution,
        "orchestration_directive": (
            f"The Academic Orchestrator will execute {len(steps)} sequential stages: "
            f"{' ──► '.join([s['agent'] for s in steps])}. "
            "Unneeded agents are pruned to preserve context bandwidth."
        )
    }


# =============================================================================
# 5. CLI Interface
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Academic Task Router & Capability Resolver Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. route (compatibility)
    p_route = subparsers.add_parser("route", help="Determine minimum sufficient capability pipeline for a user task")
    p_route.add_argument("prompt", help="User task instruction prompt")

    # 2. resolve (modern capability resolver)
    p_resolve = subparsers.add_parser("resolve", help="Resolve task prompt to capabilities, workers, reviewers, and artifacts")
    p_resolve.add_argument("prompt", help="User task instruction prompt")
    p_resolve.add_argument("--teamwork-boundary", action="store_true", help="Output only the pure Antigravity Teamwork boundary manifest")

    # 3. explain (human-readable summary)
    p_exp = subparsers.add_parser("explain", help="Print human-readable routing summary")
    p_exp.add_argument("prompt", help="User task instruction prompt")

    # 4. list-capabilities
    subparsers.add_parser("list-capabilities", help="List all registered capabilities from config/capabilities.yaml")

    # 5. list-patterns (compatibility)
    subparsers.add_parser("list-patterns", help="List canonical recognized academic routing patterns")

    args = parser.parse_args()

    if args.command == "route":
        res = build_pipeline(args.prompt)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "resolve":
        res = _RESOLVER.resolve(args.prompt)
        if getattr(args, "teamwork_boundary", False) and "teamwork_boundary" in res:
            print(json.dumps(res["teamwork_boundary"], indent=2, ensure_ascii=False))
        else:
            print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "explain":
        res = build_pipeline(args.prompt)
        cap_res = res.get("capability_resolution", {})
        print(f"\nTask: \"{res['task_prompt']}\"")
        print(f"Status: {cap_res.get('status', 'RESOLVED')}")
        if cap_res.get("status") == "RESOLVED":
            print(f"Resolved Capabilities: {cap_res.get('topological_capability_order')}")
            print(f"Primary Agent: {cap_res.get('durable_agent')}")
            workers = cap_res.get("required_subagents", {}).get("execution_workers", [])
            reviewers = cap_res.get("required_subagents", {}).get("reviewers", [])
            challengers = cap_res.get("required_subagents", {}).get("challengers", [])
            print(f"Execution Workers: {workers}")
            print(f"Reviewers (Auditors): {reviewers}")
            print(f"Challengers (Critics): {challengers}\n")
        elif cap_res.get("status") == "AMBIGUOUS":
            print(f"Ambiguity: {cap_res.get('reason')}")
            print(f"Candidates: {cap_res.get('candidate_capabilities')}\n")
        elif cap_res.get("status") == "BLOCKED":
            print(f"BLOCKED: {cap_res.get('reason')}\n")

        print(f"Legacy Formula: {res['capabilities_formula']}")
        print(f"Total Steps: {res['total_steps']}\n")
        for s in res["pipeline"]:
            print(f"  Step {s['step']}: [{s['capability']}] -> {s['agent']} (Skill: {s['skill']})")
            print(f"          Input:  {s['input_artifact']}")
            print(f"          Output: {s['output_artifact']}\n")

    elif args.command == "list-capabilities":
        print(f"\nAcademicSuite Registered Capabilities (Total: {len(_GLOBAL_REGISTRY.all_ids())}):")
        for cap_id, meta in sorted(_GLOBAL_REGISTRY.all_capabilities().items()):
            domain = meta.get("domain", "")
            skills = ", ".join(meta.get("required_skills", []))
            worker = meta.get("execution_worker", "")
            rev = meta.get("reviewer", "")
            chal = meta.get("challenger", "")
            print(f" - [{domain}] {cap_id}:")
            print(f"     Worker: {worker} | Reviewer: {rev} | Challenger: {chal}")
            print(f"     Skills: {skills}")
        print()

    elif args.command == "list-patterns":
        print("Canonical Academic Routing Patterns:")
        print("  1. 'Analyze this dataset'         -> DATA + STATISTICS")
        print("  2. 'Write Chapter 4'              -> STATISTICS + WRITING + VALIDATION")
        print("  3. 'Find research gaps'           -> RESEARCH + METHODOLOGY")
        print("  4. 'Perform CFA and SEM'          -> DATA + STATISTICS + VALIDATION")
        print("  5. 'Analyze these network data'   -> DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION")


if __name__ == "__main__":
    main()
