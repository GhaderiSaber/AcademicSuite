#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute moderation analysis (PROCESS Model 1) with simple slopes.
"""
import argparse
import json
import os
import sys
import pandas as pd
import numpy as np
import statsmodels.api as sm

def run_moderation(data_path, iv, mod, dv, output_path):
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        sys.exit(1)
        
    df = pd.read_excel(data_path) if data_path.endswith(('.xlsx', '.xls')) else pd.read_csv(data_path)
    sub_df = df[[iv, mod, dv]].dropna().copy()
    
    # Mean-centering
    sub_df['x_c'] = sub_df[iv] - sub_df[iv].mean()
    sub_df['w_c'] = sub_df[mod] - sub_df[mod].mean()
    sub_df['interaction'] = sub_df['x_c'] * sub_df['w_c']
    
    X = sm.add_constant(sub_df[['x_c', 'w_c', 'interaction']])
    model = sm.OLS(sub_df[dv], X).fit()
    
    b_int = float(model.params['interaction'])
    se_int = float(model.bse['interaction'])
    t_int = float(model.tvalues['interaction'])
    p_int = float(model.pvalues['interaction'])
    
    # Simple slopes at -1 SD, Mean, +1 SD of Moderator
    w_sd = float(sub_df[mod].std())
    slopes = []
    for label, val in [("-1 SD (Low)", -w_sd), ("Mean (Average)", 0.0), ("+1 SD (High)", w_sd)]:
        b_simple = float(model.params['x_c'] + b_int * val)
        slopes.append({
            "level": label,
            "moderator_value": round(val, 3),
            "simple_slope": round(b_simple, 3)
        })

    report = {
        "iv": iv,
        "moderator": mod,
        "dv": dv,
        "interaction_b": round(b_int, 3),
        "interaction_se": round(se_int, 3),
        "interaction_t": round(t_int, 3),
        "interaction_p": "< .001" if p_int < 0.001 else str(round(p_int, 3)),
        "moderation_significant": bool(p_int < 0.05),
        "simple_slopes": slopes
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    print(f"Moderation analysis results saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Moderation analysis")
    parser.add_argument('--data', required=True, help="Path to dataset")
    parser.add_argument('--iv', required=True, help="Independent variable")
    parser.add_argument('--mod', required=True, help="Moderator variable")
    parser.add_argument('--dv', required=True, help="Dependent variable")
    parser.add_argument('--output', default="moderation_results.json", help="Output JSON path")
    args = parser.parse_args()
    run_moderation(args.data, args.iv, args.mod, args.dv, args.output)
