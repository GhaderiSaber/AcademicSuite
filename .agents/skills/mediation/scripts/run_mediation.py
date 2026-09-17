#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute bootstrap mediation (PROCESS Model 4) with 5,000 resamples.
"""
import argparse
import json
import os
import sys
import pandas as pd
import numpy as np

def run_mediation(data_path, iv, mediator, dv, n_boot, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    sub_df = df[[iv, mediator, dv]].dropna()
    n = len(sub_df)
    
    # Path a: IV -> Med
    cov_xm = np.cov(sub_df[iv], sub_df[mediator])[0, 1]
    var_x = np.var(sub_df[iv], ddof=1)
    a = cov_xm / var_x
    
    # Path b: Med -> DV (controlling for IV)
    import statsmodels.api as sm
    X_b = sm.add_constant(sub_df[[mediator, iv]])
    model_b = sm.OLS(sub_df[dv], X_b).fit()
    b = float(model_b.params[mediator])
    c_prime = float(model_b.params[iv])
    
    # Path c: Total effect IV -> DV
    model_c = sm.OLS(sub_df[dv], sm.add_constant(sub_df[iv])).fit()
    c = float(model_c.params[iv])
    
    # Bootstrap 5,000 for indirect effect (a * b)
    np.random.seed(42)
    indirect_effects = []
    for _ in range(n_boot):
        sample = sub_df.sample(n=n, replace=True)
        a_b = np.cov(sample[iv], sample[mediator])[0, 1] / np.var(sample[iv], ddof=1)
        m_b = sm.OLS(sample[dv], sm.add_constant(sample[[mediator, iv]])).fit()
        b_b = float(m_b.params[mediator])
        indirect_effects.append(a_b * b_b)
        
    ci_lower = float(np.percentile(indirect_effects, 2.5))
    ci_upper = float(np.percentile(indirect_effects, 97.5))
    sig = bool(ci_lower * ci_upper > 0)  # CI does not contain zero

    report = {
        "iv": iv,
        "mediator": mediator,
        "dv": dv,
        "sample_size": n,
        "bootstrap_samples": n_boot,
        "path_a": round(float(a), 3),
        "path_b": round(float(b), 3),
        "total_effect_c": round(float(c), 3),
        "direct_effect_c_prime": round(float(c_prime), 3),
        "indirect_effect": round(float(a * b), 3),
        "bootstrap_95_ci": [round(ci_lower, 3), round(ci_upper, 3)],
        "significant": sig,
        "status": "MEDIATION_SIGNIFICANT" if sig else "MEDIATION_NON_SIGNIFICANT"
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Mediation analysis results saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Bootstrap mediation analysis")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--iv', required=True, help="Independent variable")
    parser.add_argument('--mediator', required=True, help="Mediator variable")
    parser.add_argument('--dv', required=True, help="Dependent variable")
    parser.add_argument('--bootstrap', type=int, default=5000, help="Number of resamples")
    parser.add_argument('--output', default="mediation_results.json", help="Output JSON path")
    args = parser.parse_args()
    run_mediation(args.data, args.iv, args.mediator, args.dv, args.bootstrap, args.output)
