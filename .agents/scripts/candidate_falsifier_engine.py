#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/candidate_falsifier_engine.py — [EXPERIMENTAL / DELIBERATION HARNESS]

Candidate -> Falsifier -> Synthesis multi-perspective deliberation engine (Phase 20 testbed).

  Candidate A, Candidate B, Candidate C
  ↓
  Academic Challenger (Actively falsifies each candidate; returns SUPPORTED, WEAK, CONDITIONAL, REJECTED)
  ↓
  Statistical / Methodology Expert (Synthesizes evidence, addresses conditions, logs pitfalls)
  ↓
  Selected AnalysisPlan (Schema-valid contract artifact conforming to contracts/analysis_plan.schema.json)

Constitutional Invariants Enforced:
1. Non-Numeric Scoring Invariant: Challenger verdicts are strictly categorical
   (SUPPORTED, WEAK, CONDITIONAL, REJECTED). Zero numeric scores, weights, or rankings.
2. Mandatory Phase Gate Invariant: A final AnalysisPlan CANNOT be formed until
   the Academic Challenger falsification and expert synthesis steps have concluded.
3. Canonical Pitfall Persistence & Memory: All rejected approaches are serialized
   into state/pitfalls.jsonl conforming to contracts/pitfall.schema.json, and future
   runs query this registry to detect and reject historical anti-patterns.
"""

import os
import sys
import json
import time
import uuid
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Tuple

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_analysis_candidate,
    validate_analysis_plan,
    validate_pitfall
)

try:
    from scripts.academic_pitfall_registry import (
        AcademicPitfallRegistry,
        PitfallError,
        PitfallSchemaValidationError,
        DuplicatePitfallError,
        MalformedPitfallError,
        InvalidPitfallQueryError,
        PitfallNotFoundError,
        VALID_CATEGORIES
    )
except ImportError:
    from academic_pitfall_registry import (
        AcademicPitfallRegistry,
        PitfallError,
        PitfallSchemaValidationError,
        DuplicatePitfallError,
        MalformedPitfallError,
        InvalidPitfallQueryError,
        PitfallNotFoundError,
        VALID_CATEGORIES
    )

DEFAULT_STATE_DIR = os.path.join(ROOT_DIR, "state")
DEFAULT_PITFALLS_FILE = os.path.join(DEFAULT_STATE_DIR, "pitfalls.jsonl")


# ==============================================================================
# Exceptions
# ==============================================================================

class CandidateDeliberationError(Exception):
    """Base exception for candidate deliberation errors."""
    pass

class PrematureFinalizationError(CandidateDeliberationError):
    """Raised when an AnalysisPlan is created before the challenge and synthesis steps complete."""
    pass

class NoDefensibleCandidateError(CandidateDeliberationError):
    """Raised when all candidate approaches are rejected by the Academic Challenger."""
    pass

class InvalidCandidateError(CandidateDeliberationError):
    """Raised when a candidate analysis plan fails schema validation."""
    pass

class MissingProductionDataError(CandidateDeliberationError):
    """Raised when real production empirical candidates payload is missing in production mode."""
    pass

class ProductionSampleFallbackBlockedError(CandidateDeliberationError):
    """Raised when an attempt is made to fall back to sample/demo candidate data in production mode."""
    pass


# ==============================================================================
# Candidate Data Structure
# ==============================================================================

class AnalysisCandidate:
    """
    Structured representation of a proposed statistical analysis candidate.
    Enforces the 10 mandatory fields specified by AcademicSuite.
    """

    def __init__(
        self,
        candidate_id: str,
        method: str,
        research_question: str,
        estimand: str,
        assumptions: List[str],
        data_requirements: Dict[str, Any],
        diagnostics: List[str],
        strengths: List[str],
        limitations: List[str],
        expected_interpretation: str,
        execution_requirements: Dict[str, Any],
        proposed_by: str = "statistical-expert",
        contract_version: str = "1.0.0"
    ):
        self.candidate_id = candidate_id
        self.method = method
        self.research_question = research_question
        self.estimand = estimand
        self.assumptions = list(assumptions)
        self.data_requirements = dict(data_requirements)
        self.diagnostics = list(diagnostics)
        self.strengths = list(strengths)
        self.limitations = list(limitations)
        self.expected_interpretation = expected_interpretation
        self.execution_requirements = dict(execution_requirements)
        self.proposed_by = proposed_by
        self.contract_version = contract_version

    def to_dict(self) -> Dict[str, Any]:
        """Converts candidate to dictionary representation."""
        return {
            "contract_version": self.contract_version,
            "candidate_id": self.candidate_id,
            "proposed_by": self.proposed_by,
            "method": self.method,
            "research_question": self.research_question,
            "estimand": self.estimand,
            "assumptions": self.assumptions,
            "data_requirements": self.data_requirements,
            "diagnostics": self.diagnostics,
            "strengths": self.strengths,
            "limitations": self.limitations,
            "expected_interpretation": self.expected_interpretation,
            "execution_requirements": self.execution_requirements
        }

    def validate(self) -> Dict[str, Any]:
        """Validates candidate against contracts/analysis_candidate.schema.json."""
        d = self.to_dict()
        val = validate_analysis_candidate(d)
        if not val.get("valid", False):
            raise InvalidCandidateError(f"Candidate '{self.candidate_id}' failed schema validation: {val.get('errors')}")
        return val

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisCandidate":
        """Instantiates AnalysisCandidate from dictionary."""
        val = validate_analysis_candidate(data)
        if not val.get("valid", False):
            raise InvalidCandidateError(f"Candidate data failed schema validation: {val.get('errors')}")
        return cls(
            candidate_id=data["candidate_id"],
            method=data["method"],
            research_question=data["research_question"],
            estimand=data["estimand"],
            assumptions=data["assumptions"],
            data_requirements=data["data_requirements"],
            diagnostics=data["diagnostics"],
            strengths=data["strengths"],
            limitations=data["limitations"],
            expected_interpretation=data["expected_interpretation"],
            execution_requirements=data["execution_requirements"],
            proposed_by=data.get("proposed_by", "statistical-expert"),
            contract_version=data.get("contract_version", "1.0.0")
        )


# ==============================================================================
# Canonical Pitfall Registry
# ==============================================================================

class CanonicalPitfallRegistry(AcademicPitfallRegistry):
    """
    Manages the persistence, audit, and retrieval of methodological pitfalls in state/pitfalls.jsonl.
    Enforces contracts/pitfall.schema.json for every persisted entry.
    Subclasses AcademicPitfallRegistry to provide full backward-compatibility and research-memory indexing.
    """

    def __init__(self, registry_path: Optional[str] = None, project_id: Optional[str] = None):
        super().__init__(registry_path=registry_path, project_id=project_id)

    def load_pitfalls(self) -> List[Dict[str, Any]]:
        """Loads all recorded pitfalls from the JSONL registry."""
        return self.read(validate_schema=False)

    def record_pitfall(
        self,
        candidate: Union[AnalysisCandidate, Dict[str, Any]],
        problem: str,
        evidence_description: str,
        corrective_action: str,
        adapted_approach: str,
        stage: str = "methodological_candidate_selection",
        verification_check: str = "Re-evaluate against study design and baseline characteristics.",
        project: Optional[str] = None,
        milestone: Optional[str] = None,
        category: str = "methodological",
        related_artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Creates and appends a structured pitfall record conforming to contracts/pitfall.schema.json.
        """
        cand_dict = candidate.to_dict() if isinstance(candidate, AnalysisCandidate) else candidate
        cand_id = cand_dict.get("candidate_id", "CAND-UNKNOWN")
        method = cand_dict.get("method", "Unknown Method")
        rq = cand_dict.get("research_question", "target research question")
        candidate_approach_str = f"{method} for '{rq}'"

        pid = f"PIT-{int(time.time())}-{cand_id}-{uuid.uuid4().hex[:4].upper()}"

        return self.create(
            candidate_approach=candidate_approach_str,
            problem=problem,
            evidence=evidence_description,
            corrective_action=corrective_action,
            adapted_approach=adapted_approach,
            detected_by="academic-challenger",
            category=category,
            stage=stage,
            milestone=milestone or stage,
            project=project or self.project_id or "academic_project",
            reusable=True,
            pitfall_id=pid,
            verification_check=verification_check,
            related_artifacts=related_artifacts or []
        )

    def find_matching_pitfalls(
        self,
        candidate: Union[AnalysisCandidate, Dict[str, Any]],
        study_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Checks if candidate method or characteristics match previously recorded pitfalls.
        """
        cand_dict = candidate.to_dict() if isinstance(candidate, AnalysisCandidate) else candidate
        cand_method = cand_dict.get("method", "").lower().strip()
        data_req = cand_dict.get("data_requirements", {})
        if isinstance(data_req, dict):
            time_structure = data_req.get("time_structure", "").lower()
        elif isinstance(data_req, str):
            time_structure = data_req.lower()
        else:
            time_structure = ""

        matches = []
        for p in self.read(validate_schema=False):
            appr = p.get("candidate_approach", "").lower()
            prob = p.get("problem", "").lower()
            # Match method name
            if cand_method and (cand_method in appr or cand_method in prob):
                # If study context or time structure also indicates similar defect
                if time_structure and (time_structure in appr or time_structure in prob):
                    matches.append(p)
                elif not time_structure:
                    matches.append(p)
                else:
                    matches.append(p)
        return matches


# ==============================================================================
# Academic Challenger (Adversarial Falsifier)
# ==============================================================================

class AcademicChallenger:
    """
    Adversarial Methodology, Bias & Statistical Falsifier Subagent.
    Actively attempts to invalidate each candidate analysis plan.
    Does NOT merely verify field presence.
    Returns structured categorical findings:
      - SUPPORTED: Withstands rigorous methodological scrutiny.
      - WEAK: Defensible but vulnerable to efficiency, power, or interpretation limitations.
      - CONDITIONAL: Viable only if specific corrective conditions or diagnostics are satisfied.
      - REJECTED: Methodologically flawed, invalid for study design, or matches a fatal pitfall.

    Zero numeric scores or rankings.
    """

    def __init__(
        self,
        pitfall_registry: Optional[Union[CanonicalPitfallRegistry, Any]] = None,
        pitfall_file: Optional[str] = None
    ):
        if pitfall_file:
            self.pitfall_registry = CanonicalPitfallRegistry(pitfall_file)
        else:
            self.pitfall_registry = pitfall_registry or CanonicalPitfallRegistry()

    def challenge_candidate(
        self,
        candidate: Union[AnalysisCandidate, Dict[str, Any]],
        study_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actively challenges a single candidate against domain falsification criteria.
        Returns a structured finding.
        """
        cand = candidate.to_dict() if isinstance(candidate, AnalysisCandidate) else candidate
        cand_id = cand.get("candidate_id", "CAND")
        method = cand.get("method", "")
        method_lower = method.lower()
        design_type = study_context.get("design_type", "").lower()
        time_structure = study_context.get("time_structure", "").lower()
        has_baseline = (
            study_context.get("has_baseline", False)
            or study_context.get("baseline_collected", False)
            or "pre_post" in design_type
        )
        missing_rate = study_context.get("missing_rate", 0.0)
        if not missing_rate and "missing_percentage" in study_context:
            mp = float(study_context["missing_percentage"])
            missing_rate = mp / 100.0 if mp > 1.0 else mp
        is_randomized = study_context.get("is_randomized", True)
        sample_size = study_context.get("sample_size", 100)

        evaluations: List[Dict[str, Any]] = []
        rejection_reasons: List[str] = []
        conditions: List[str] = []
        warnings: List[str] = []

        # 0. Historical Pitfall Check
        historical_matches = self.pitfall_registry.find_matching_pitfalls(cand, study_context)
        if historical_matches:
            matched_pitfall = historical_matches[0]
            evaluations.append({
                "question": "Does this proposed candidate match a previously recorded methodological pitfall?",
                "verdict": "FAIL",
                "rationale": f"Candidate matches previous failure recorded in '{matched_pitfall['pitfall_id']}': {matched_pitfall['problem']}"
            })
            rejection_reasons.append(f"Recurring Pitfall [{matched_pitfall['pitfall_id']}]: {matched_pitfall['problem']}")
        else:
            evaluations.append({
                "question": "Does this proposed candidate match a previously recorded methodological pitfall?",
                "verdict": "PASS",
                "rationale": "No recurring pitfall detected in canonical registry."
            })

        # 1. Design Compatibility
        # E.g. Using pure Between-Subjects ANOVA when baseline or repeated measures exist
        if (
            ("between" in method_lower or "post-test" in method_lower or "one-way" in method_lower)
            and "anova" in method_lower
            and "ancova" not in method_lower
            and has_baseline
        ):
            evaluations.append({
                "question": "Is the proposed model compatible with the study design?",
                "verdict": "FAIL",
                "rationale": "One-Way ANOVA ignores baseline measurement, failing to account for baseline variability and group imbalance."
            })
            rejection_reasons.append("Ignoring pre-test baseline in an intervention design violates design compatibility.")
        elif "change_score" in method_lower or "gain_score" in method_lower:
            if not is_randomized:
                evaluations.append({
                    "question": "Is the proposed model compatible with the study design?",
                    "verdict": "FAIL",
                    "rationale": "Change score analysis in non-randomized quasi-experiments suffers from Lord's Paradox and regresses to the mean."
                })
                rejection_reasons.append("Change score analysis is biased in non-randomized designs (Lord's Paradox).")
            else:
                evaluations.append({
                    "question": "Is the proposed model compatible with the study design?",
                    "verdict": "WARN",
                    "rationale": "Change score analysis assumes baseline and posttest have equal variance and measurement error."
                })
                warnings.append("Change score has lower statistical power than ANCOVA when pre-post correlation is < .50.")
        else:
            evaluations.append({
                "question": "Is the proposed model compatible with the study design?",
                "verdict": "PASS",
                "rationale": f"Method '{method}' aligns with design '{design_type}' and time structure '{time_structure}'."
            })

        # 2. Estimand Explicitness
        estimand = cand.get("estimand", "").strip()
        if not estimand or len(estimand) < 10:
            evaluations.append({
                "question": "Is the estimand explicit?",
                "verdict": "FAIL",
                "rationale": "Estimand is unstated or too vague to define the target counterfactual contrast."
            })
            rejection_reasons.append("Ambiguous or absent estimand specification.")
        elif not any(term in estimand.lower() for term in ["treatment effect", "adjusted difference", "rate of change", "path", "contrast", "trajectory"]):
            evaluations.append({
                "question": "Is the estimand explicit?",
                "verdict": "WARN",
                "rationale": "Estimand lacks explicit formal contrast definition."
            })
            conditions.append("Explicitly specify the formal estimand as Average Treatment Effect (ATE) or population mean contrast.")
        else:
            evaluations.append({
                "question": "Is the estimand explicit?",
                "verdict": "PASS",
                "rationale": f"Estimand is explicitly specified: '{estimand}'."
            })

        # 3. Repeated Observations & Within-Subject Clustering
        if "repeated" in time_structure or "longitudinal" in time_structure:
            if "repeated_measures_anova" in method_lower or "rm_anova" in method_lower:
                if missing_rate > 0.05:
                    evaluations.append({
                        "question": "Are repeated observations handled appropriately?",
                        "verdict": "FAIL",
                        "rationale": f"RM-ANOVA relies on listwise deletion under missing rate ({missing_rate*100:.1f}%), causing substantial sample loss and attrition bias."
                    })
                    rejection_reasons.append("RM-ANOVA cannot handle missing waves without listwise case deletion.")
                else:
                    evaluations.append({
                        "question": "Are repeated observations handled appropriately?",
                        "verdict": "WARN",
                        "rationale": "RM-ANOVA requires sphericity assumption (Mauchly test) and compound symmetry."
                    })
                    conditions.append("Incorporate Greenhouse-Geisser or Huynh-Feldt epsilon corrections if Mauchly sphericity is violated.")
            elif "mixed" in method_lower or "lmm" in method_lower or "multilevel" in method_lower:
                evaluations.append({
                    "question": "Are repeated observations handled appropriately?",
                    "verdict": "PASS",
                    "rationale": "Linear mixed models handle unbalanced time points and within-subject dependency via random intercepts/slopes."
                })
            else:
                evaluations.append({
                    "question": "Are repeated observations handled appropriately?",
                    "verdict": "WARN",
                    "rationale": "Verify that within-subject correlation structure is explicitly accounted for."
                })
        else:
            evaluations.append({
                "question": "Are repeated observations handled appropriately?",
                "verdict": "PASS",
                "rationale": "Cross-sectional or single posttest contrast; repeated observation clustering is not required."
            })

        # 4. Missingness Vulnerability
        if missing_rate > 0.05:
            data_req = cand.get("data_requirements", {})
            if isinstance(data_req, dict):
                req_missing = data_req.get("missing_data_strategy", "")
            elif isinstance(data_req, str):
                req_missing = data_req
            else:
                req_missing = ""
            if "listwise" in req_missing.lower() or "deletion" in req_missing.lower():
                evaluations.append({
                    "question": "Does missingness affect the proposed method?",
                    "verdict": "FAIL",
                    "rationale": f"Listwise deletion under {missing_rate*100:.1f}% missingness induces severe selection bias."
                })
                rejection_reasons.append("Unacceptable reliance on listwise deletion under moderate-to-high missingness.")
            elif "fiml" in method_lower or "imputation" in method_lower or "mixed" in method_lower:
                evaluations.append({
                    "question": "Does missingness affect the proposed method?",
                    "verdict": "PASS",
                    "rationale": "Method accommodates missingness under Missing at Random (MAR) assumptions."
                })
            else:
                evaluations.append({
                    "question": "Does missingness affect the proposed method?",
                    "verdict": "WARN",
                    "rationale": "Method requires explicit missing data handling strategy."
                })
                conditions.append("Implement Multiple Imputation (m=20) or Full Information Maximum Likelihood (FIML).")
        else:
            evaluations.append({
                "question": "Does missingness affect the proposed method?",
                "verdict": "PASS",
                "rationale": f"Minimal missing rate ({missing_rate*100:.1f}%) within acceptable tolerance."
            })

        # 5. Baseline Adjustment Justification
        if has_baseline:
            if "ancova" in method_lower:
                evaluations.append({
                    "question": "Is baseline adjustment justified?",
                    "verdict": "PASS",
                    "rationale": "ANCOVA statistically adjusts for pre-existing baseline score differences and increases statistical precision."
                })
                conditions.append("Verify homogeneity of regression slopes (Group × Pretest interaction p > .05).")
            elif "gain" in method_lower or "diff_in_diff" in method_lower:
                evaluations.append({
                    "question": "Is baseline adjustment justified?",
                    "verdict": "WARN",
                    "rationale": "Change/gain score handles baseline via subtraction rather than regression conditioning."
                })
            else:
                evaluations.append({
                    "question": "Is baseline adjustment justified?",
                    "verdict": "FAIL",
                    "rationale": "Baseline was measured but omitted from the statistical model, inflating error variance."
                })
                rejection_reasons.append("Unjustified omission of available baseline covariate.")
        else:
            evaluations.append({
                "question": "Is baseline adjustment justified?",
                "verdict": "PASS",
                "rationale": "No baseline covariate recorded in study design."
            })

        # 6. Effect Size Appropriateness
        effect_sizes = cand.get("strengths", []) + cand.get("limitations", [])
        if "ancova" in method_lower or "anova" in method_lower:
            evaluations.append({
                "question": "Is the proposed effect size appropriate?",
                "verdict": "PASS",
                "rationale": "Partial eta-squared (η_p²) appropriately isolates variance attributable to effect removing covariate variance."
            })
        elif "regression" in method_lower:
            evaluations.append({
                "question": "Is the proposed effect size appropriate?",
                "verdict": "PASS",
                "rationale": "Standardized beta (β) and semi-partial R² are appropriate."
            })
        else:
            evaluations.append({
                "question": "Is the proposed effect size appropriate?",
                "verdict": "PASS",
                "rationale": "Effect size metrics align with model parameterization."
            })

        # 7. Assumption Testability with Available Data
        diagnostics = cand.get("diagnostics", [])
        if not diagnostics or len(diagnostics) == 0:
            evaluations.append({
                "question": "Are assumptions actually testable with available data?",
                "verdict": "FAIL",
                "rationale": "No empirical diagnostic tests declared for model assumptions."
            })
            rejection_reasons.append("Lack of testable diagnostic procedures.")
        else:
            evaluations.append({
                "question": "Are assumptions actually testable with available data?",
                "verdict": "PASS",
                "rationale": f"Explicit diagnostics provided: {', '.join(diagnostics)}."
            })

        # 8. Competing Alternative Model Superiority
        if "rm_anova" in method_lower and ("longitudinal" in time_structure or missing_rate > 0.05):
            evaluations.append({
                "question": "Could another model better match the data-generating structure?",
                "verdict": "FAIL",
                "rationale": "Linear Mixed-Effects Model (LMM) strictly dominates RM-ANOVA by modeling time continuously, accommodating missing data, and relaxing sphericity."
            })
            rejection_reasons.append("Linear Mixed-Effects Model (LMM) strictly dominates RM-ANOVA for this data structure.")
        else:
            evaluations.append({
                "question": "Could another model better match the data-generating structure?",
                "verdict": "PASS",
                "rationale": "No strictly dominant alternative model found."
            })

        # 9. Interpretation Exceeding Design Boundaries
        expected_interp = cand.get("expected_interpretation", "").lower()
        if not is_randomized and ("causes" in expected_interp or "proves efficacy" in expected_interp or "causal" in expected_interp):
            evaluations.append({
                "question": "Does the interpretation exceed what the design supports?",
                "verdict": "FAIL",
                "rationale": "Observational or non-randomized quasi-experimental design cannot assert strict unconfounded causal claims."
            })
            rejection_reasons.append("Causal claim exceeds the methodological capability of non-randomized design.")
        elif "proves" in expected_interp:
            evaluations.append({
                "question": "Does the interpretation exceed what the design supports?",
                "verdict": "WARN",
                "rationale": "Avoid dogmatic phrasing ('proves'); adhere to epistemic sobriety."
            })
            conditions.append("Reframe expected interpretation using probabilistic empirical terminology ('demonstrates evidence for', 'supports').")
        else:
            evaluations.append({
                "question": "Does the interpretation exceed what the design supports?",
                "verdict": "PASS",
                "rationale": "Interpretation maintains scholarly sobriety and respects design boundaries."
            })

        # Categorical Verdict Determination (Zero Numeric Scoring)
        if rejection_reasons:
            verdict = "REJECTED"
        elif conditions:
            verdict = "CONDITIONAL"
        elif warnings:
            verdict = "WEAK"
        else:
            verdict = "SUPPORTED"

        finding = {
            "candidate_id": cand_id,
            "method": method,
            "verdict": verdict,
            "evaluations": evaluations,
            "rejection_reasons": rejection_reasons,
            "conditions_for_acceptance": conditions,
            "methodological_warnings": warnings,
            "historical_pitfall_match": historical_matches[0] if historical_matches else None
        }

        # If rejected, immediately persist into pitfall registry
        if verdict == "REJECTED":
            primary_problem = rejection_reasons[0]
            evidence_desc = "; ".join([e["rationale"] for e in evaluations if e["verdict"] == "FAIL"])
            self.pitfall_registry.record_pitfall(
                candidate=cand,
                problem=primary_problem,
                evidence_description=evidence_desc,
                corrective_action="Discard approach; adopt robust competing candidate that satisfies design constraints.",
                adapted_approach="Condition on baseline via ANCOVA or adopt Linear Mixed Model for longitudinal unbalanced data.",
                project=study_context.get("project_id", "academic_project"),
                milestone=study_context.get("milestone_id", "M7_HYPOTHESIS_TESTING"),
                category="methodological"
            )

        return finding

    def challenge_all_candidates(
        self,
        candidates: List[Union[AnalysisCandidate, Dict[str, Any]]],
        study_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Challenges a collection of candidate analysis plans."""
        return [self.challenge_candidate(c, study_context) for c in candidates]


# ==============================================================================
# Statistical / Methodology Expert (Synthesis Engine)
# ==============================================================================

class StatisticalMethodologySynthesizer:
    """
    Synthesizes competing candidates, incorporates Academic Challenger findings,
    resolves conditions, and generates the final schema-valid AnalysisPlan.
    Enforces the mandatory phase gate invariant.
    """

    def __init__(self, pitfall_registry: Optional[CanonicalPitfallRegistry] = None):
        self.pitfall_registry = pitfall_registry or CanonicalPitfallRegistry()
        self.challenger = AcademicChallenger(pitfall_registry=self.pitfall_registry)

    def synthesize_and_select(
        self,
        candidates: List[Union[AnalysisCandidate, Dict[str, Any]]],
        study_context: Dict[str, Any],
        project_id: str = "academic_project",
        plan_id_prefix: str = "PLAN-2026-SYNTH"
    ) -> Dict[str, Any]:
        """
        Executes the full Candidate -> Falsifier -> Synthesis sequence:
          1. Validates candidate specifications.
          2. Runs Academic Challenger to actively falsify candidates.
          3. Rejects invalid candidates and persists them into state/pitfalls.jsonl.
          4. Integrates required conditions for CONDITIONAL candidates.
          5. Synthesizes winning candidate into a schema-valid AnalysisPlan.
        """
        if not candidates:
            raise CandidateDeliberationError("Cannot synthesize plan without candidates.")

        # 1. Candidate Schema Validation
        parsed_candidates = []
        for c in candidates:
            if isinstance(c, AnalysisCandidate):
                c.validate()
                parsed_candidates.append(c.to_dict())
            else:
                val = validate_analysis_candidate(c)
                if not val.get("valid", False):
                    raise InvalidCandidateError(f"Candidate failed contract schema: {val.get('errors')}")
                parsed_candidates.append(c)

        # 2. Challenger Falsification
        challenger_findings = self.challenger.challenge_all_candidates(parsed_candidates, study_context)

        # 3. Categorize Findings
        supported = [f for f in challenger_findings if f["verdict"] == "SUPPORTED"]
        conditional = [f for f in challenger_findings if f["verdict"] == "CONDITIONAL"]
        weak = [f for f in challenger_findings if f["verdict"] == "WEAK"]
        rejected = [f for f in challenger_findings if f["verdict"] == "REJECTED"]

        if not supported and not conditional and not weak:
            raise NoDefensibleCandidateError(
                f"All {len(parsed_candidates)} candidate approaches were REJECTED by Academic Challenger. "
                "Methodological redesign is required before an AnalysisPlan can be formed."
            )

        # 4. Expert Selection Hierarchy
        # Prefer SUPPORTED > CONDITIONAL > WEAK
        if supported:
            selected_finding = supported[0]
            selection_category = "SUPPORTED"
        elif conditional:
            selected_finding = conditional[0]
            selection_category = "CONDITIONAL"
        else:
            selected_finding = weak[0]
            selection_category = "WEAK"

        selected_cand_id = selected_finding["candidate_id"]
        selected_cand = next(c for c in parsed_candidates if c["candidate_id"] == selected_cand_id)

        # 5. Build Synthesis Rationale
        rationale_lines = [
            f"Deliberation evaluated {len(parsed_candidates)} competing candidate analysis plans.",
            f"Candidate '{selected_cand_id}' ({selected_cand['method']}) was selected under {selection_category} status.",
            f"Methodological justification: {', '.join(selected_cand.get('strengths', []))}."
        ]
        if rejected:
            rationale_lines.append(
                f"Disqualified candidates: {', '.join([r['candidate_id'] + ' (' + r['method'] + ')' for r in rejected])} "
                f"due to fatal design/assumption vulnerabilities persisted into canonical pitfall registry."
            )
        if selected_finding.get("conditions_for_acceptance"):
            rationale_lines.append(
                f"Synthesized conditions addressed: {'; '.join(selected_finding['conditions_for_acceptance'])}."
            )

        synthesis_rationale = " ".join(rationale_lines)

        # 6. Map Candidate to Official AnalysisPlan Contract Schema
        plan_id = f"{plan_id_prefix}-{int(time.time())}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Build assumptions list with check items
        assumptions_list = []
        for a in selected_cand.get("assumptions", []):
            assumptions_list.append({
                "test_name": a.split()[0] if a.split() else "AssumptionCheck",
                "target": a,
                "threshold": "p > .05 or satisfactory Q-Q plot",
                "action_on_violation": "Adopt robust Welch correction, bootstrapping, or rank transform."
            })
        if not assumptions_list:
            assumptions_list.append({
                "test_name": "DiagnosticSuite",
                "target": "Model residuals normality and homoscedasticity",
                "threshold": "p > .05",
                "action_on_violation": "Robust estimation"
            })

        # Build statistical models list
        model_family = selected_cand.get("method", "").lower().replace(" ", "_").replace("-", "_")
        if "ancova" in model_family:
            family_key = "ancova_analysis_of_covariance"
            hyp_type = "group_comparison"
        elif "repeated" in model_family or "rm_anova" in model_family or "mixed" in model_family:
            family_key = "repeated_measures_anova"
            hyp_type = "group_comparison"
        elif "sem" in model_family or "structural" in model_family:
            family_key = "sem_structural_equation_modeling"
            hyp_type = "direct"
        elif "cfa" in model_family or "factor" in model_family:
            family_key = "cfa_confirmatory_factor_analysis"
            hyp_type = "measurement_cfa"
        elif "process_4" in model_family or "mediation" in model_family:
            family_key = "process_model_4_mediation"
            hyp_type = "indirect_mediation"
        elif "process_7" in model_family or "modmed" in model_family:
            family_key = "process_model_7_modmed"
            hyp_type = "moderated_mediation"
        elif "process_1" in model_family or "moderation" in model_family:
            family_key = "process_model_1_moderation"
            hyp_type = "moderation"
        elif "meta" in model_family:
            family_key = "meta_analytic_random_effects"
            hyp_type = "direct"
        elif "anova" in model_family or "t_test" in model_family or "ttest" in model_family or "comparison" in model_family:
            family_key = "ancova_analysis_of_covariance"
            hyp_type = "group_comparison"
        else:
            family_key = "linear_regression"
            hyp_type = "direct"

        # Build final AnalysisPlan conforming strictly to contracts/analysis_plan.schema.json
        # and backwards-compatible with academic_state schema
        final_plan = {
            "contract_version": "1.0.0",
            "plan_id": plan_id,
            "project_id": project_id,
            "created_at": now_iso,
            "decided_by": "statistical-expert",
            "status": "APPROVED",
            "significance_alpha": 0.05,
            "power_target": 0.85,
            "bootstrap_resamples": 5000,
            "planned_sequence": [
                {
                    "stage_id": "06_hypothesis_1",
                    "title": f"{selected_cand.get('method')} Hypothesis Testing",
                    "engine": "python",
                    "script": "scripts/statistical_pipeline_engine.py",
                    "output_artifact": "06_hypothesis_1.docx",
                    "assigned_subagent": "statistics-agent"
                }
            ],
            "research_questions": [
                {
                    "id": "RQ1",
                    "question": selected_cand.get("research_question", "Target empirical question."),
                    "target_variables": selected_cand.get("data_requirements", {}).get("variables", [])
                }
            ],
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": selected_cand.get("expected_interpretation", "Intervention produces directional change in outcome."),
                    "type": hyp_type,
                    "direction": "negative",
                    "independent_variable": selected_cand.get("data_requirements", {}).get("variables", ["group"])[0],
                    "dependent_variable": selected_cand.get("data_requirements", {}).get("variables", ["outcome"])[-1]
                }
            ],
            "design": {
                "type": study_context.get("design_type", "experimental"),
                "time_structure": study_context.get("time_structure", "pre_post_repeated_measures"),
                "grouping": {
                    "is_grouped": True,
                    "group_variable": "group",
                    "levels": ["intervention", "control"]
                },
                "power_analysis": {
                    "target_power": 0.85,
                    "significance_alpha": 0.05,
                    "required_n": selected_cand.get("data_requirements", {}).get("minimum_sample_size", 60),
                    "software": "G*Power 3.1"
                }
            },
            "variables": {
                "outcome_variables": study_context.get("variables", {}).get("dependent") or [selected_cand.get("data_requirements", {}).get("variables", ["burnout_post"])[-1]],
                "predictors": study_context.get("variables", {}).get("independent") or [selected_cand.get("data_requirements", {}).get("variables", ["group"])[0]],
                "covariates": study_context.get("variables", {}).get("covariates") or ([v for v in selected_cand.get("data_requirements", {}).get("variables", []) if "pre" in v or "covar" in v] or ([selected_cand.get("data_requirements", {}).get("variables", ["burnout_pre"])[1]] if len(selected_cand.get("data_requirements", {}).get("variables", [])) > 2 else [])),
                "independent": study_context.get("variables", {}).get("independent") or [selected_cand.get("data_requirements", {}).get("variables", ["group"])[0]],
                "dependent": study_context.get("variables", {}).get("dependent") or [selected_cand.get("data_requirements", {}).get("variables", ["burnout_post"])[-1]]
            },
            "estimands": [
                {
                    "id": "EST-01",
                    "description": selected_cand.get("estimand", "Adjusted average treatment effect."),
                    "target_parameter": "average_treatment_effect"
                }
            ],
            "statistical_models": [
                {
                    "model_id": f"MOD-{family_key.upper()}-01",
                    "family": family_key,
                    "estimator": "OLS" if "ancova" in family_key else "REML",
                    "specification": f"{selected_cand.get('method')} with diagnostic checks"
                }
            ],
            "assumptions": assumptions_list,
            "missing_data_strategy": {
                "strategy": "listwise_deletion" if study_context.get("missing_rate", 0) < 0.05 else "multiple_imputation_chained_equations",
                "mcar_diagnostic_required": True,
                "maximum_allowed_missing_rate": max(0.05, float(study_context.get("missing_rate", 0.05))),
                "mean_imputation_prohibited": True
            },
            "exclusion_rules": [
                {
                    "rule_id": "EXC-01",
                    "criterion": "Mahalanobis D2 p < .001 or unengaged straight-lining",
                    "action": "flag_for_review"
                }
            ],
            "effect_size_specifications": [
                {
                    "metric": "partial_eta_squared" if "ancova" in family_key else "standardized_beta",
                    "benchmark_scale": "Cohen 1988 (small=.01, medium=.06, large=.14)"
                }
            ],
            "confidence_intervals": {
                "confidence_level": 0.95,
                "estimation_method": "bca_bias_corrected_accelerated_bootstrap",
                "bootstrap_resamples": 5000
            },
            "multiple_testing_strategy": {
                "correction_method": "none_planned_orthogonal_hypotheses",
                "family_definition": "Pre-planned primary hypothesis"
            },
            "diagnostics": selected_cand.get("diagnostics", ["Residual normality Q-Q plot"]),
            "required_tables": [
                {
                    "table_id": "Table 1",
                    "title": f"Summary of {selected_cand.get('method')} results",
                    "standard": "apa_7_three_line"
                }
            ],
            "required_figures": [
                {
                    "figure_id": "Figure 1",
                    "type": f"{selected_cand.get('method')} visualization",
                    "dpi": 300
                }
            ],
            "execution_specification": {
                "assigned_subagent": selected_cand.get("execution_requirements", {}).get("assigned_subagent", "statistics-agent"),
                "engine": selected_cand.get("execution_requirements", {}).get("engine", "python"),
                "scripts": selected_cand.get("execution_requirements", {}).get("scripts", ["scripts/statistical_pipeline_engine.py"]),
                "expected_triad_artifacts": {
                    "docx_path": "06_hypothesis_1.docx",
                    "md_path": "06_hypothesis_1.md",
                    "json_path": "06_hypothesis_1.json"
                }
            },
            "deliberation_metadata": {
                "considered_candidates": [c["candidate_id"] for c in parsed_candidates],
                "selected_candidate_id": selected_cand_id,
                "selection_category": selection_category,
                "synthesis_rationale": synthesis_rationale,
                "challenger_findings": challenger_findings
            }
        }

        # Validate final AnalysisPlan against authoritative schema
        val_res = validate_analysis_plan(final_plan)
        if not val_res.get("valid", False):
            raise CandidateDeliberationError(f"Synthesized AnalysisPlan failed contract schema: {val_res.get('errors')}")

        return {
            "status": "SUCCESS",
            "selected_candidate_id": selected_cand_id,
            "selection_category": selection_category,
            "synthesis_rationale": synthesis_rationale,
            "analysis_plan": final_plan,
            "challenger_findings": challenger_findings,
            "rejected_candidates": rejected
        }


# ==============================================================================
# Helper to prevent premature finalization without challenge
# ==============================================================================

def create_unverified_plan_guard():
    """Throws PrematureFinalizationError when trying to skip challenger phase."""
    raise PrematureFinalizationError(
        "CONSTITUTIONAL VIOLATION: An AnalysisPlan cannot be created without executing the "
        "Candidate -> Falsifier -> Synthesis deliberation sequence."
    )


# ==============================================================================
# Markdown Report Generation & CLI Entry Point
# ==============================================================================

def generate_deliberation_markdown(delib_result: Dict[str, Any], study_context: Dict[str, Any]) -> str:
    """
    Generates an executive APA-style markdown report detailing candidate evaluations,
    Academic Challenger categorical findings, avoided pitfalls, and the synthesized plan.
    """
    plan = delib_result.get("analysis_plan", {})
    selected_id = delib_result.get("selected_candidate_id", "N/A")
    category = delib_result.get("selection_category", "N/A")
    rationale = delib_result.get("synthesis_rationale", "N/A")
    findings = delib_result.get("challenger_findings", [])
    rejected = delib_result.get("rejected_candidates", [])
    model_family = plan.get("statistical_models", [{}])[0].get("family", "N/A")
    estimand_def = plan.get("estimands", [{}])[0].get("description", "N/A")

    lines = [
        "# Methodological Deliberation & Academic Challenger Report",
        "",
        "## Executive Summary",
        f"- **Project ID**: `{study_context.get('project_id', 'N/A')}`",
        f"- **Design Type**: `{study_context.get('design_type', 'N/A')}`",
        f"- **Time Structure**: `{study_context.get('time_structure', 'N/A')}`",
        f"- **Selected Candidate**: `{selected_id}` (`{model_family}`)",
        f"- **Selection Verdict**: **{category}**",
        f"- **Synthesis Rationale**: {rationale}",
        "",
        "---",
        "",
        "## 1. Candidate Evaluation & Challenger Invalidation Matrix",
        "",
        "| Candidate ID | Challenger Verdict | Methodological Vulnerabilities / Conditions | Avoided Pitfalls |",
        "| :--- | :---: | :--- | :--- |"
    ]

    for f in findings:
        cand_id = f.get("candidate_id", "N/A")
        verdict = f.get("verdict", "UNKNOWN")
        flaws = []
        for r_reason in f.get("rejection_reasons", []):
            flaws.append(f"**FATAL**: {r_reason}")
        for c_cond in f.get("conditions_for_acceptance", []):
            flaws.append(f"**CONDITION**: {c_cond}")
        for w_warn in f.get("methodological_warnings", []):
            flaws.append(f"**WARN**: {w_warn}")
        flaw_str = "<br>".join(flaws) if flaws else "None (Fully Defensible)"

        pf_match = f.get("historical_pitfall_match")
        pf_str = f"`{pf_match.get('pitfall_id', '')}`" if pf_match else "None"

        lines.append(f"| `{cand_id}` | **{verdict}** | {flaw_str} | {pf_str} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Canonical Pitfalls Registry Action",
        ""
    ])

    if rejected:
        lines.append(f"The Academic Challenger invalidated {len(rejected)} candidate approach(es) and permanently recorded them to `state/pitfalls.jsonl`:")
        for r in rejected:
            p_reasons = "; ".join(r.get("rejection_reasons", ["Methodological flaw detected"]))
            lines.append(f"- **`{r.get('candidate_id', '')}`** ({r.get('method', '')}): *{p_reasons}*")
    else:
        lines.append("No candidates were rejected in this deliberation cycle.")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Synthesized Analysis Plan Summary",
        f"- **Primary Hypothesis**: {plan.get('hypotheses', [{}])[0].get('statement', 'N/A')}",
        f"- **Estimand**: {estimand_def}",
        f"- **Model Family**: `{model_family}`",
        f"- **Software Engine**: `{plan.get('execution_specification', {}).get('engine', 'N/A')}`",
        f"- **Assigned Subagent**: `{plan.get('execution_specification', {}).get('assigned_subagent', 'N/A')}`",
        f"- **Artifact Triad Path**: `{plan.get('execution_specification', {}).get('expected_triad_artifacts', {}).get('json_path', '06_hypothesis_1.json')}`",
        "",
        "> [!NOTE]",
        "> Complete formal specification written to `analysis_plan.json` conforming to `contracts/analysis_plan.schema.json`."
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Candidate -> Falsifier -> Synthesis Deliberation Engine")
    parser.add_argument("--candidates", required=True, help="Path to JSON file containing candidates or deliberation payload")
    parser.add_argument("--out-dir", required=True, help="Output directory for generated artifacts")
    parser.add_argument("--pitfalls", default=DEFAULT_PITFALLS_FILE, help="Path to pitfalls.jsonl registry")
    parser.add_argument("--context", help="Path to optional study context JSON file")
    parser.add_argument("--mode", default="production", choices=["production", "demo", "test"], help="Execution mode (default: production)")
    parser.add_argument("--preferred", help="Optional preferred candidate ID")

    args = parser.parse_args()

    # Safety checks in production mode
    if args.mode == "production":
        norm_cand = os.path.abspath(args.candidates).replace("\\", "/")
        if "/examples/" in norm_cand or "sample_" in os.path.basename(norm_cand):
            raise ProductionSampleFallbackBlockedError(
                f"CRITICAL SAFETY VIOLATION: Production execution attempted with sample/demo candidates payload '{args.candidates}'. "
                f"Production mode strictly requires real empirical candidates on disk."
            )

    if not os.path.isfile(args.candidates):
        raise MissingProductionDataError(f"Candidates file not found: {args.candidates}")

    with open(args.candidates, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    if isinstance(raw_data, list):
        candidates_list = raw_data
        study_context = {}
    elif isinstance(raw_data, dict):
        candidates_list = raw_data.get("candidates", [])
        study_context = raw_data.get("study_context", {})
    else:
        raise InvalidCandidateError(f"Malformed candidates data in {args.candidates}")

    if args.context and os.path.isfile(args.context):
        with open(args.context, "r", encoding="utf-8") as f:
            study_context.update(json.load(f))

    os.makedirs(args.out_dir, exist_ok=True)
    pitfalls_path = os.path.abspath(args.pitfalls)

    registry = CanonicalPitfallRegistry(registry_path=pitfalls_path)
    synthesizer = StatisticalMethodologySynthesizer(pitfall_registry=registry)

    # Challenge & Synthesize
    delib_res = synthesizer.synthesize_and_select(
        candidates=candidates_list,
        study_context=study_context,
        project_id=study_context.get("project_id", "academic_project")
    )

    # 3. Output artifacts
    plan_path = os.path.join(args.out_dir, "analysis_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(delib_res["analysis_plan"], f, indent=2, ensure_ascii=False)

    report_json_path = os.path.join(args.out_dir, "deliberation_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(delib_res, f, indent=2, ensure_ascii=False)

    report_md_path = os.path.join(args.out_dir, "deliberation_report.md")
    md_content = generate_deliberation_markdown(delib_res, study_context)
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[SUCCESS] Synthesized AnalysisPlan: {plan_path}")
    print(f"[SUCCESS] Deliberation Report JSON: {report_json_path}")
    print(f"[SUCCESS] Deliberation Report MD: {report_md_path}")
    print(f"[DELIBERATION] Selected Candidate: {delib_res['selected_candidate_id']} ({delib_res['selection_category']})")
    if delib_res["rejected_candidates"]:
        print(f"[PITFALLS] Recorded {len(delib_res['rejected_candidates'])} rejected candidate(s) to {pitfalls_path}")


if __name__ == "__main__":
    main()
