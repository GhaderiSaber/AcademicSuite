import os
import json
import numpy as np

def main():
    stats_path = "02_processed_data/stats_results.json"
    out_dir = "02_processed_data"
    
    with open(stats_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    N = data["study_metadata"]["sample_size"]
    
    audit_report = {
        "audit_name": "Multi-Signal Anomaly Index (MSAI) Statistical Audit",
        "sample_size": N,
        "checks": []
    }
    
    # 1. Degrees of Freedom Concordance
    # Model 1
    m1 = data["regression_self_harm"]["model_summary"]
    df1_expected = 3
    df2_expected = N - 3 - 1 # 508
    df_match = (m1["df1"] == df1_expected and m1["df2"] == df2_expected)
    audit_report["checks"].append({
        "check_name": "Degrees of Freedom Concordance (Self-Harm Model)",
        "observed": f"df1={m1['df1']}, df2={m1['df2']}",
        "expected": f"df1={df1_expected}, df2={df2_expected}",
        "status": "PASSED" if df_match else "FAILED",
        "msai_penalty": 0 if df_match else 25
    })
    
    # Model 2
    m2 = data["regression_suicide"]["model_summary"]
    df_match2 = (m2["df1"] == df1_expected and m2["df2"] == df2_expected)
    audit_report["checks"].append({
        "check_name": "Degrees of Freedom Concordance (Suicide Model)",
        "observed": f"df1={m2['df1']}, df2={m2['df2']}",
        "expected": f"df1={df1_expected}, df2={df2_expected}",
        "status": "PASSED" if df_match2 else "FAILED",
        "msai_penalty": 0 if df_match2 else 25
    })
    
    # 2. Variance Deflation Check (SD < 0.10 * Range)
    desc = data["descriptive_statistics"]
    var_deflation_flag = False
    for v_key, v_info in desc.items():
        v_range = v_info["max"] - v_info["min"]
        sd = v_info["sd"]
        is_deflated = (sd < 0.10 * v_range) if v_range > 0 else False
        if is_deflated:
            var_deflation_flag = True
        audit_report["checks"].append({
            "check_name": f"Variance Deflation Check ({v_info['name_fa']})",
            "sd": sd,
            "range": v_range,
            "ratio": round(sd / v_range, 3) if v_range > 0 else 0,
            "status": "PASSED" if not is_deflated else "FLAG_FOR_REVIEW",
            "msai_penalty": 0 if not is_deflated else 15
        })
        
    # 3. Multicollinearity Check (VIF < 5.0, Tol > 0.20)
    collin = data["collinearity_diagnostics"]
    collin_flag = False
    for c_key, c_info in collin.items():
        if c_info["vif"] > 5.0 or c_info["tolerance"] < 0.20:
            collin_flag = True
            
    audit_report["checks"].append({
        "check_name": "Multicollinearity Safeguard (VIF < 5.0, Tolerance > 0.20)",
        "max_vif": max(c["vif"] for c in collin.values()),
        "min_tolerance": min(c["tolerance"] for c in collin.values()),
        "status": "PASSED" if not collin_flag else "FLAG_FOR_REVIEW",
        "msai_penalty": 0 if not collin_flag else 20
    })
    
    # 4. Effect Size Plausibility (R2 plausible between 0.05 and 0.60 for behavioral surveys)
    r2_1 = m1["R2"]
    r2_2 = m2["R2"]
    plausible_r2 = (0.05 <= r2_1 <= 0.60) and (0.05 <= r2_2 <= 0.60)
    audit_report["checks"].append({
        "check_name": "Effect Size Plausibility (R² bounds in adolescent surveys)",
        "r2_self_harm": r2_1,
        "r2_suicide": r2_2,
        "status": "PASSED" if plausible_r2 else "FLAG_FOR_REVIEW",
        "msai_penalty": 0 if plausible_r2 else 15
    })
    
    # 5. Residual Independence (Durbin-Watson 1.5 to 2.5)
    dw1 = m1["durbin_watson"]
    dw2 = m2["durbin_watson"]
    dw_pass = (1.5 <= dw1 <= 2.5) and (1.5 <= dw2 <= 2.5)
    audit_report["checks"].append({
        "check_name": "Residual Independence (Durbin-Watson in [1.5, 2.5])",
        "dw_self_harm": dw1,
        "dw_suicide": dw2,
        "status": "PASSED" if dw_pass else "FLAG_FOR_REVIEW",
        "msai_penalty": 0 if dw_pass else 15
    })
    
    # Calculate Total MSAI Score
    total_penalty = sum(c["msai_penalty"] for c in audit_report["checks"])
    msai_score = max(0, 100 - total_penalty)
    audit_report["msai_score"] = msai_score
    audit_report["audit_verdict"] = "AUDIT_PASSED" if msai_score >= 85 else "FLAG_FOR_REVIEW"
    
    out_audit_path = os.path.join(out_dir, "statistical_audit_report.json")
    with open(out_audit_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, ensure_ascii=False, indent=2)
    print(f"Saved MSAI audit report to {out_audit_path} with score {msai_score}/100.")

if __name__ == "__main__":
    main()
