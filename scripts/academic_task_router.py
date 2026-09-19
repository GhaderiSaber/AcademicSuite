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
        "agent": "academic-writer",
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
# 3. Empirical Design Derivation & Dynamic Antigravity Team Assembly
# =============================================================================

def derive_research_design(prompt: str) -> Dict[str, Any]:
    """
    Extracts the empirical research design topology from a user task or research question.
    Derives:
      - study_type: RCT, quasi_experimental, cross_sectional, longitudinal, scale_validation, qualitative, meta_analysis
      - group_structure: multi-group, single-group, factorial
      - temporal_dynamics: repeated measures, cross-sectional, single-point
      - waves: follow-up, pre-post, cross-sectional
      - factors: list of canonical design descriptors e.g. ["RCT", "multi-group", "repeated measures", "follow-up"]
      - interventions: list of detected interventions e.g. ["ACT", "CBT"]
      - outcomes: list of detected outcome variables
    """
    p = prompt.lower()

    # 1. Detect Interventions
    interventions = []
    if re.search(r'\bact\b|acceptance and commitment', p):
        interventions.append("ACT")
    if re.search(r'\bcbt\b|cognitive behavioral', p):
        interventions.append("CBT")
    if re.search(r'\bschema\b', p):
        interventions.append("Schema Therapy")
    if re.search(r'\bmbsr\b|mindfulness', p):
        interventions.append("Mindfulness/MBSR")
    if re.search(r'\bcft\b|compassion focused', p):
        interventions.append("CFT")
    if re.search(r'\bintervention\b|\btreatment\b|\btraining\b|\btherapy\b', p) and not interventions:
        interventions.append("Experimental Intervention")

    # 2. Detect Outcomes / DVs
    outcomes = []
    for term in [
        "anxiety", "depression", "psychological distress", "stress", "resilience",
        "well-being", "quality of life", "cognitive flexibility", "burnout"
    ]:
        if term in p:
            outcomes.append(term)

    # 3. Detect Temporal Waves & Follow-up
    has_followup = bool(re.search(r'\bfollow[- ]up\b|\b\d+[- ]month\b|\blongitudinal\b', p))
    has_posttest = bool(re.search(r'\bpost[- ]test\b|\bpre[- ]test\b|\bbefore and after\b', p))

    # 4. Determine Design Factors
    factors = []

    # Study Type
    if interventions and (has_posttest or has_followup or "rct" in p or "trial" in p or "experimental" in p):
        study_type = "RCT"
        factors.append("RCT")
    elif "meta-analysis" in p or "systematic review" in p or "prisma" in p:
        study_type = "meta_analysis"
        factors.append("meta-analysis")
    elif "thematic" in p or "grounded theory" in p or "qualitative" in p or "interview" in p:
        study_type = "qualitative"
        factors.append("qualitative")
    elif "scale validation" in p or "psychometric" in p or "cvr" in p or "cvi" in p or ("efa" in p and "cfa" in p):
        study_type = "scale_validation"
        factors.append("scale validation")
    elif "sem" in p or "mediation" in p or "moderation" in p or "path analysis" in p or "path model" in p:
        study_type = "correlational_structural"
        factors.append("correlational structural")
    elif has_followup or "longitudinal" in p:
        study_type = "longitudinal"
        factors.append("longitudinal")
    else:
        study_type = "observational_survey"
        factors.append("observational")

    # Group Structure
    if interventions or "group" in p or "control" in p or "waitlist" in p or "compare" in p or study_type == "RCT":
        group_structure = "multi-group"
        factors.append("multi-group")
    elif "factorial" in p or "2x2" in p:
        group_structure = "factorial"
        factors.append("factorial")
    else:
        group_structure = "single-group"

    # Temporal Dynamics
    if has_posttest or has_followup or "repeated measures" in p:
        temporal_dynamics = "repeated measures"
        factors.append("repeated measures")
    elif "cross-sectional" in p:
        temporal_dynamics = "cross-sectional"
    else:
        temporal_dynamics = "single-point"

    # Waves
    if has_followup:
        waves = "follow-up"
        factors.append("follow-up")
    elif has_posttest:
        waves = "pre-post"
    else:
        waves = "cross-sectional"

    return {
        "study_type": study_type,
        "group_structure": group_structure,
        "temporal_dynamics": temporal_dynamics,
        "waves": waves,
        "factors": factors,
        "interventions": interventions,
        "outcomes": outcomes,
    }


def resolve_capability_matrix(prompt: str, design: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Derives canonical capability requirements based on research task and empirical design.
    Deconstructs requirements across the 6 research phases.
    """
    if design is None:
        design = derive_research_design(prompt)

    caps = []

    # 1. Design & Methodology
    caps.append("design-methodology")

    # 2. Longitudinal / Structural / Qualitative Analysis
    if design["temporal_dynamics"] == "repeated measures" or design["waves"] == "follow-up":
        caps.append("longitudinal-analysis")
    elif design["study_type"] == "correlational_structural":
        caps.append("structural-equation-modeling")
    elif design["study_type"] == "scale_validation":
        caps.append("psychometric-validation")
    elif design["study_type"] == "qualitative":
        caps.append("qualitative-thematic-analysis")
    elif design["study_type"] == "meta_analysis":
        caps.append("meta-analytic-pooling")

    # 3. Assumption Checking (for parametric quantitative designs)
    if design["study_type"] in ("RCT", "correlational_structural", "longitudinal"):
        caps.append("assumption-checking")

    # 4. Effect Size Calculation
    if design["study_type"] in ("RCT", "correlational_structural", "longitudinal", "meta_analysis"):
        caps.append("effect-size")

    # 5. Post-Hoc / Comparison / Path Tracing
    if design["group_structure"] == "multi-group" or design["temporal_dynamics"] == "repeated measures":
        caps.append("post-hoc/comparison")
    elif "mediation" in prompt.lower():
        caps.append("bootstrap-indirect-effects")

    # 6. Statistical Execution / Computation
    if design["study_type"] != "qualitative":
        caps.append("statistical-execution")

    # 7. Results Writing
    caps.append("results-writing")

    # 8. Audit & Independent Verification
    caps.append("audit")

    return caps


def assemble_antigravity_team(design: Dict[str, Any], capabilities: List[str]) -> Dict[str, Any]:
    """
    Dynamically assembles the minimal set of native Antigravity subagents required
    for the task, strictly pruning unneeded agents from the 28 workspace agents.
    """
    orchestrator = "academic-orchestrator"
    assigned_roles: Dict[str, Any] = {
        "lead_orchestrator": orchestrator,
        "methodologist": None,
        "data_specialist": None,
        "statisticians": [],
        "writer": None,
        "auditors": [],
    }

    subagents: List[str] = []
    pruned: Dict[str, str] = {}

    # 1. Methodology Assignment
    if "design-methodology" in capabilities:
        assigned_roles["methodologist"] = "methodology-expert"
        subagents.append("methodology-expert")
    else:
        pruned["methodology-expert"] = "Task does not involve experimental or sampling design specification."

    # 2. Data Specialist Assignment
    if any(c in capabilities for c in ["data-preparation", "assumption-checking", "statistical-execution"]):
        assigned_roles["data_specialist"] = "data-curator"
        subagents.append("data-curator")
    else:
        pruned["data-curator"] = "No quantitative tabular dataset curation or screening required."

    # 3. Statistician Assignment
    if "statistical-execution" in capabilities or "longitudinal-analysis" in capabilities or "assumption-checking" in capabilities:
        assigned_roles["statisticians"] = ["statistical-expert", "statistics-agent"]
        subagents.extend(["statistical-expert", "statistics-agent"])
    else:
        pruned["statistical-expert"] = "Non-statistical task; quantitative test selection not required."
        pruned["statistics-agent"] = "Non-statistical task; numerical computation script execution not required."

    # 4. Psychometrician Assignment
    if "psychometric-validation" in capabilities:
        subagents.append("psychometric-expert")
    else:
        pruned["psychometric-expert"] = "Standard validated psychometric scales utilized; no scale construction or IRT needed."

    # 5. Qualitative Assignment
    if "qualitative-thematic-analysis" in capabilities:
        subagents.append("qualitative-analyst")
    else:
        pruned["qualitative-analyst"] = "Quantitative empirical design; no qualitative transcript coding needed."

    # 6. Meta-Analyst Assignment
    if "meta-analytic-pooling" in capabilities:
        subagents.append("meta-analyst")
    else:
        pruned["meta-analyst"] = "Primary empirical research trial; not a systematic literature review."

    # 7. Longitudinal ModMed Assignment
    if "longitudinal-analysis" in capabilities and design.get("study_type") == "RCT":
        pruned["longitudinal-modmed-expert"] = "Design requires mixed repeated-measures ANOVA / follow-up comparison rather than continuous longitudinal moderated mediation."
    elif "longitudinal-moderated-mediation" in capabilities:
        subagents.append("longitudinal-modmed-expert")
    else:
        pruned["longitudinal-modmed-expert"] = "Task does not involve 3-wave autoregressive moderated mediation modeling."

    # 8. Writer Assignment
    if "results-writing" in capabilities:
        assigned_roles["writer"] = "academic-writer"
        subagents.append("academic-writer")
    else:
        pruned["academic-writer"] = "Execution only; formal academic manuscript drafting not requested."

    # 9. Auditors Assignment
    if "audit" in capabilities:
        auditors = []
        if "statistical-execution" in capabilities or "assumption-checking" in capabilities:
            auditors.append("statistical-auditor")
            auditors.append("academic-challenger")
        auditors.append("validation-agent")
        assigned_roles["auditors"] = auditors
        subagents.extend(auditors)
    else:
        pruned["validation-agent"] = "Pre-flight exploratory query; formal release audit not triggered."
        pruned["statistical-auditor"] = "Pre-flight exploratory query; formal statistical audit not triggered."
        pruned["academic-challenger"] = "Pre-flight exploratory query; adversarial defense cross-examination not triggered."

    # 10. Explicitly Prune Remaining Workspace Agents with Rationale
    pruned["digital-saber"] = "Lead supervisory persona reserved for administrative human consultation; runtime task conducted by academic-orchestrator."
    pruned["research-agent"] = "Design and statistical execution delegated directly to specialist subagents."
    pruned["literature-expert"] = "Empirical data trial analysis; literature database harvesting not requested."
    pruned["data-agent"] = "Execution worker data-curator assigned directly for dataset curation and screening."
    pruned["journal-strategist"] = "Pipeline focus is statistical execution and findings drafting, not submission packaging."
    pruned["results-auditor"] = "Statistical auditor and validation agent conduct primary numerical and procedural audit."
    pruned["evidence-auditor"] = "Bibliographic citation concordance audit not required for primary empirical dataset analysis."
    pruned["final-judge"] = "Reserved for institutional defense committee simulation and final release gating."

    # 11. Intervention Designer
    if design.get("study_type") == "RCT" and ("post-test" in design.get("waves", "") or "follow-up" in design.get("waves", "")):
        pruned["intervention-designer"] = "Intervention protocol already administered; data collected across post-test and follow-up."
    elif "intervention-protocol" not in capabilities:
        pruned["intervention-designer"] = "Task does not require designing a clinical or psychoeducational intervention manual."

    # 12. Learning Subagents (Autonomous loop)
    for l_agent in ["behavior-analyst", "curriculum-builder", "evaluation-agent", "knowledge-curator", "skill-evolver", "trajectory-analyzer"]:
        pruned[l_agent] = "Active empirical research task; autonomous self-improvement loop runs in background evaluation sandbox."

    # Ensure uniqueness while preserving order
    deduped_subagents = []
    for a in subagents:
        if a not in deduped_subagents:
            deduped_subagents.append(a)

    return {
        "lead_orchestrator": orchestrator,
        "assigned_roles": assigned_roles,
        "assembled_subagents": deduped_subagents,
        "pruned_agents": pruned,
        "orchestration_mode": "DYNAMIC_NATIVE_SUBAGENTS"
    }



# =============================================================================
# 4. Modern Capability Resolver
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

        # Check derived design for experimental or specialized research designs
        derived_design = derive_research_design(p)
        if derived_design["study_type"] == "RCT" or derived_design["temporal_dynamics"] == "repeated measures":
            if derived_design.get("interventions") or derived_design.get("waves") in ("follow-up", "pre-post") or "rct" in p_lower or "repeated measures" in p_lower:
                detected_caps.add("repeated_measures")
        elif derived_design["study_type"] == "correlational_structural":
            detected_caps.add("sem")
        elif derived_design["study_type"] == "scale_validation":
            detected_caps.add("cfa")
        elif derived_design["study_type"] == "qualitative":
            detected_caps.add("qualitative_analysis")
        elif derived_design["study_type"] == "meta_analysis":
            detected_caps.add("meta_analysis")

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

        # Derive research design, capability matrix, and dynamic team
        design = derive_research_design(prompt)
        cap_matrix = resolve_capability_matrix(prompt, design)
        assembled_team = assemble_antigravity_team(design, cap_matrix)

        return {
            "status": "RESOLVED",
            "task_prompt": prompt,
            "complexity_level": complexity_level,
            "design": design,
            "capability_matrix": cap_matrix,
            "assembled_team": assembled_team,
            "required_capabilities": list(detected_caps),
            "topological_capability_order": resolved_order,
            "durable_agent": durable_primary_agent,
            "required_subagents": {
                "primary_agents": list(primary_agents),
                "execution_workers": execution_workers,
                "reviewers": reviewers,
                "challengers": challengers,
                "assembled_subagents": assembled_team["assembled_subagents"],
                "pruned_agents": assembled_team["pruned_agents"]
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
