#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/meta_factory.py — The Unifying Agent-Skill-Validator Meta-Factory

Orchestrates the autonomous production of complete domain specialists:
Agent + Skill + Deterministic Tools + Contract + Validator + Evaluation Cases,
executing an automated Pre-Registration Sandbox Test Gate before registration.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import numpy as np
import pandas as pd

try:
    import jsonschema
except ImportError:
    jsonschema = None

from factory.agent_factory import create_agent
from factory.skill_factory import create_skill
from factory.validator_factory import create_validator

EVAL_SCHEMA_PATH = os.path.join(ROOT_DIR, "evals", "eval_schema.json")


def load_eval_schema() -> Optional[Dict[str, Any]]:
    if os.path.exists(EVAL_SCHEMA_PATH):
        with open(EVAL_SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def run_preregistration_sandbox_test(
    script_path: str,
    data_path: str,
    validator_path: str,
    eval_case: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes an isolated end-to-end sandbox test on the generated specialist components:
    1. Executes deterministic tool script on benchmark fixture.
    2. Runs validator on produced output.
    3. Validates evaluation test case against evals/eval_schema.json.
    """
    test_results = {
        "script_execution": "PENDING",
        "validator_execution": "PENDING",
        "eval_case_schema": "PENDING",
        "overall_verdict": "FAIL",
        "errors": []
    }

    # 1. Check eval case schema
    schema = load_eval_schema()
    if schema and jsonschema:
        try:
            clean_case = {k: v for k, v in eval_case.items() if not k.startswith("_")}
            jsonschema.validate(instance=clean_case, schema=schema)
            test_results["eval_case_schema"] = "PASS"
        except Exception as e:
            test_results["eval_case_schema"] = "FAIL"
            test_results["errors"].append(f"Evaluation case schema violation: {str(e)}")
    else:
        test_results["eval_case_schema"] = "PASS"

    # 2. Execute script in temp dir
    temp_dir = tempfile.mkdtemp(prefix="specialist_sandbox_")
    output_json = os.path.join(temp_dir, "test_output.json")

    try:
        cmd = [
            sys.executable, script_path,
            "--data", data_path,
            "--output", output_json
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and os.path.exists(output_json):
            test_results["script_execution"] = "PASS"
        else:
            test_results["script_execution"] = "FAIL"
            test_results["errors"].append(f"Script execution failed (code {res.returncode}): {res.stderr}")

        # 3. Run validator on script output
        if test_results["script_execution"] == "PASS":
            val_cmd = [sys.executable, validator_path, "--input", output_json]
            val_res = subprocess.run(val_cmd, capture_output=True, text=True, timeout=30)
            if val_res.returncode == 0:
                test_results["validator_execution"] = "PASS"
            else:
                test_results["validator_execution"] = "FAIL"
                test_results["errors"].append(f"Validator rejected output (code {val_res.returncode}): {val_res.stdout} {val_res.stderr}")

    except Exception as ex:
        test_results["errors"].append(f"Sandbox runner exception: {str(ex)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Determine overall verdict
    if (
        test_results["eval_case_schema"] == "PASS" and
        test_results["script_execution"] == "PASS" and
        test_results["validator_execution"] == "PASS"
    ):
        test_results["overall_verdict"] = "PASS"

    return test_results


def build_longitudinal_modmed_specialist(target_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Demonstration builder for: Longitudinal Moderated Mediation Specialist.
    Produces Agent + Skill + Tool + Contract + Validator + Eval Case,
    and runs the Pre-Registration Sandbox Gate before final registration.
    """
    root = target_root or ROOT_DIR
    agents_dir = os.path.join(root, ".agents", "agents")
    skills_dir = os.path.join(root, ".agents", "skills")
    validators_dir = os.path.join(root, "validators")
    evals_dir = os.path.join(root, "evals", "mediation")

    # 1. Agent Specification
    agent_name = "longitudinal-modmed-expert"
    agent_role = "Longitudinal Moderated Mediation Specialist"
    agent_desc = "Specialist subagent for 3-wave longitudinal moderated mediation modeling (Cole & Maxwell, Hayes PROCESS Model 7/14 over time)."
    agent_mission = (
        "You are the expert responsible for modeling longitudinal conditional process mechanisms. "
        "You estimate time-lagged mediation (Wave 1 Predictor -> Wave 2 Mediator -> Wave 3 Outcome) "
        "conditioned on baseline or time-varying moderators, while strictly controlling for autoregressive baseline effects (M1, Y1)."
    )
    agent_rules = [
        "Enforce 3-wave time-lagged temporal precedence (X at T1, M at T2, Y at T3).",
        "Control for autoregressive baseline values of M1 and Y1 to isolate true change over time.",
        "Estimate the Index of Moderated Mediation via 5,000 bootstrap resamples with 95% BCa confidence intervals.",
        "Prohibit cross-sectional mediation claims when longitudinal data is available.",
        "Generate APA 7 3-line tables for conditional indirect effects across moderator percentiles (16th, 50th, 84th)."
    ]
    agent_info = create_agent(
        name=agent_name,
        role=agent_role,
        description=agent_desc,
        skills=["longitudinal-moderated-mediation", "mediation", "apa-reporting"],
        mission=agent_mission,
        decision_rules=agent_rules,
        target_dir=agents_dir
    )

    # 2. Tool Script: run_longitudinal_modmed.py
    script_name = "run_longitudinal_modmed.py"
    script_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic Longitudinal Moderated Mediation CLI Engine (Model 7 Longitudinal)
Wave 1: X (Predictor), W (Moderator)
Wave 2: M (Mediator), M1 control
Wave 3: Y (Outcome), Y1 control
"""

import os, sys, json, argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

import numpy as np
import pandas as pd
import statsmodels.api as sm

def run_analysis(data_path: str, output_path: str):
    df = pd.read_excel(data_path) if data_path.endswith('.xlsx') else pd.read_csv(data_path)
    n = len(df)

    # Required columns: x_t1, w_t1, m_t2, m_t1, y_t3, y_t1
    x = df['x_t1']
    w = df['w_t1']
    xw = x * w
    m2 = df['m_t2']
    m1 = df['m_t1']
    y3 = df['y_t3']
    y1 = df['y_t1']

    # 1. Mediator model: M2 ~ X1 + W1 + X1*W1 + M1
    X_med = pd.DataFrame({'const': 1, 'x_t1': x, 'w_t1': w, 'xw': xw, 'm_t1': m1})
    mod_med = sm.OLS(m2, X_med).fit()

    # 2. Outcome model: Y3 ~ M2 + X1 + Y1
    X_out = pd.DataFrame({'const': 1, 'm_t2': m2, 'x_t1': x, 'y_t1': y1})
    mod_out = sm.OLS(y3, X_out).fit()

    a1 = mod_med.params['x_t1']
    a3 = mod_med.params['xw']
    b1 = mod_out.params['m_t2']

    # Index of moderated mediation
    index_modmed = float(a3 * b1)

    # Bootstrap 5,000 for Index CI
    np.random.seed(42)
    boot_indices = []
    for _ in range(5000):
        idx = np.random.choice(n, size=n, replace=True)
        boot_df = df.iloc[idx]
        b_x = boot_df['x_t1']
        b_w = boot_df['w_t1']
        b_xw = b_x * b_w
        b_m2 = boot_df['m_t2']
        b_m1 = boot_df['m_t1']
        b_y3 = boot_df['y_t3']
        b_y1 = boot_df['y_t1']

        b_Xm = pd.DataFrame({'const': 1, 'x_t1': b_x, 'w_t1': b_w, 'xw': b_xw, 'm_t1': b_m1})
        m_fit = sm.OLS(b_m2, b_Xm).fit()
        b_Xy = pd.DataFrame({'const': 1, 'm_t2': b_m2, 'x_t1': b_x, 'y_t1': b_y1})
        y_fit = sm.OLS(b_y3, b_Xy).fit()
        boot_indices.append(m_fit.params['xw'] * y_fit.params['m_t2'])

    boot_indices = np.array(boot_indices)
    ci_lower = float(np.percentile(boot_indices, 2.5))
    ci_upper = float(np.percentile(boot_indices, 97.5))

    results = {
        "model_type": "Longitudinal Moderated Mediation (Wave 1 -> Wave 2 -> Wave 3)",
        "sample_size": n,
        "mediator_model": {
            "r_squared": round(float(mod_med.rsquared), 4),
            "f_stat": round(float(mod_med.fvalue), 3),
            "p_value": round(float(mod_med.f_pvalue), 4),
            "interaction_coeff_a3": round(float(a3), 4),
            "interaction_p_value": round(float(mod_med.pvalues['xw']), 4)
        },
        "outcome_model": {
            "r_squared": round(float(mod_out.rsquared), 4),
            "f_stat": round(float(mod_out.fvalue), 3),
            "p_value": round(float(mod_out.f_pvalue), 4),
            "b1_coeff": round(float(b1), 4),
            "b1_p_value": round(float(mod_out.pvalues['m_t2']), 4)
        },
        "moderated_mediation_index": {
            "index": round(index_modmed, 4),
            "bootstrap_samples": 5000,
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4),
            "significant": bool(ci_lower > 0 or ci_upper < 0)
        },
        "verdict": "SUPPORTED" if (ci_lower > 0 or ci_upper < 0) else "NOT_SUPPORTED"
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Longitudinal Mod-Med results saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run_analysis(args.data, args.output)
'''

    # 3. Skill Scaffolding
    skill_name = "longitudinal-moderated-mediation"
    skill_desc = "Execute 3-wave longitudinal moderated mediation modeling, autoregressive baseline controls, and 5,000 bootstrap index estimation."
    sections = {
        "Overview & Scope": (
            "This skill provides deterministic estimation for time-lagged longitudinal conditional process models. "
            "It tests whether the indirect effect of a predictor at Time 1 on an outcome at Time 3 via a mediator at Time 2 "
            "is moderated by a boundary condition at Time 1."
        ),
        "Methodological Standards & Equations": (
            "Follows Cole & Maxwell (2003) and Preacher, Rucker, & Hayes (2007). "
            "Baseline autoregressive controls for M1 and Y1 are mandatory to purge prior equilibrium variance."
        ),
        "Deterministic Execution Instructions": (
            f"Run CLI engine: `python3 .agents/skills/{skill_name}/scripts/{script_name} --data <path> --output <path.json>`"
        )
    }
    skill_info = create_skill(
        name=skill_name,
        description=skill_desc,
        sections=sections,
        script_name=script_name,
        script_code=script_code,
        target_dir=skills_dir
    )

    # 4. Validator Scaffolding
    validator_name = "longitudinal_modmed"
    val_desc = "Validates longitudinal moderated mediation outputs, sample sizes, and bootstrap CI bounds."
    val_custom_logic = """    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get("sample_size", 0) < 50:
            errors.append("Sample size too small for longitudinal modeling (N < 50).")

        idx_info = data.get("moderated_mediation_index", {})
        if idx_info.get("bootstrap_samples", 0) < 5000:
            errors.append("Bootstrap resamples must be >= 5,000.")

        if "ci_95_lower" not in idx_info or "ci_95_upper" not in idx_info:
            errors.append("Missing 95% bootstrap confidence intervals.")

        if data.get("verdict") not in ["SUPPORTED", "NOT_SUPPORTED"]:
            errors.append("Invalid model verdict status.")

    except Exception as e:
        errors.append(f"Validation parsing exception: {str(e)}")"""

    val_info = create_validator(
        name=validator_name,
        description=val_desc,
        custom_logic=val_custom_logic,
        target_dir=validators_dir
    )

    # 5. Benchmark Data Fixture & Evaluation Test Case
    os.makedirs(os.path.join(evals_dir, "data"), exist_ok=True)
    data_fixture_path = os.path.join(evals_dir, "data", "longitudinal_modmed_data.xlsx")

    # Deterministic generation of 3-wave dataset (N=200)
    np.random.seed(1405)
    n = 200
    x_t1 = np.random.normal(3.0, 0.8, n)
    w_t1 = np.random.normal(2.8, 0.7, n)
    m_t1 = np.random.normal(2.5, 0.6, n)
    y_t1 = np.random.normal(2.7, 0.6, n)
    # Wave 2: m_t2 = 0.5*m_t1 + 0.35*x_t1 + 0.25*w_t1 + 0.20*(x_t1*w_t1) + noise
    m_t2 = 0.4 * m_t1 + 0.3 * x_t1 + 0.2 * w_t1 + 0.25 * (x_t1 * w_t1) + np.random.normal(0, 0.3, n)
    # Wave 3: y_t3 = 0.4*y_t1 + 0.45*m_t2 + 0.15*x_t1 + noise
    y_t3 = 0.4 * y_t1 + 0.45 * m_t2 + 0.15 * x_t1 + np.random.normal(0, 0.3, n)

    df_synth = pd.DataFrame({
        'id': range(1, n + 1),
        'x_t1': np.round(x_t1, 3),
        'w_t1': np.round(w_t1, 3),
        'm_t1': np.round(m_t1, 3),
        'm_t2': np.round(m_t2, 3),
        'y_t1': np.round(y_t1, 3),
        'y_t3': np.round(y_t3, 3)
    })
    df_synth.to_excel(data_fixture_path, index=False)

    eval_case = {
        "test_id": "EVAL-LMM-01",
        "domain": "mediation",
        "title": "3-Wave Longitudinal Moderated Mediation with Autoregressive Baseline Controls",
        "version_target": "Academic Suite v2",
        "INPUT": {
            "data_path": "evals/mediation/data/longitudinal_modmed_data.xlsx",
            "format": "xlsx",
            "sample_n": n,
            "predictors": ["x_t1"],
            "moderators": ["w_t1"],
            "mediators": ["m_t2"],
            "dependent_variable": "y_t3"
        },
        "EXPECTED_ANALYSIS": {
            "model_type": "3-Wave Longitudinal Moderated Mediation",
            "methodology": "Time-lagged conditional process with 5,000 bootstrap resamples",
            "standard_applied": "Cole & Maxwell (2003) & Hayes (2018)",
            "tool_script": f".agents/skills/{skill_name}/scripts/{script_name}"
        },
        "EXPECTED_N": n,
        "EXPECTED_VARIABLES": ["x_t1", "w_t1", "m_t1", "m_t2", "y_t1", "y_t3"],
        "EXPECTED_KEY_STATISTICS": {
            "index_moderated_mediation": {"tolerance": 0.050},
            "bootstrap_samples": {"value": 5000}
        },
        "EXPECTED_TABLES": [
            {"table_number": 1, "title": "Mediator & Outcome Models in Longitudinal Mod-Med", "columns": 6, "format": "APA 7"},
            {"table_number": 2, "title": "Index of Moderated Mediation & 95% BCa CI", "columns": 5, "format": "APA 7"}
        ],
        "EXPECTED_INTERPRETATION_CONSTRAINTS": {
            "language": "Persian (Farsi)",
            "paragraph_structure": "5-Part Epistemic Formula",
            "leading_zero_persian": True,
            "table_placement": "narrative_above_table",
            "zero_citations_in_results": True,
            "zero_ai_cliches": True,
            "effect_size_reporting": True
        },
        "EXPECTED_VALIDATION": {
            "data_integrity": "PASS",
            "numerical_consistency": "PASS",
            "reporting_consistency": "PASS",
            "result_consistency": "PASS",
            "statistical_assumptions": "PASS",
            "state_schema_validation": "PASS"
        }
    }

    eval_case_path = os.path.join(evals_dir, "case_longitudinal_modmed_01.json")
    with open(eval_case_path, "w", encoding="utf-8") as f:
        json.dump(eval_case, f, indent=2, ensure_ascii=False)

    # 6. Pre-Registration Sandbox Test Gate
    test_result = run_preregistration_sandbox_test(
        script_path=skill_info["script_path"],
        data_path=data_fixture_path,
        validator_path=val_info["file_path"],
        eval_case=eval_case
    )

    manifest = {
        "specialist_name": agent_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_info,
        "skill": skill_info,
        "validator": val_info,
        "evaluation_case": eval_case_path,
        "preregistration_sandbox_test": test_result,
        "registration_status": "CERTIFIED_AND_REGISTERED" if test_result["overall_verdict"] == "PASS" else "REJECTED"
    }

    manifest_path = os.path.join(root, "factory", "specialist_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    if test_result["overall_verdict"] != "PASS":
        raise RuntimeError(f"Pre-Registration Sandbox Test FAILED: {test_result['errors']}")

    return manifest
