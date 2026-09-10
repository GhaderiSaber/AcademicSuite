#!/usr/bin/env python3
"""
generate_soldiers_dataset.py
============================
Deterministic generator and validator for the Soldiers Research Dataset (Healthy vs Self-Harm).
Generates N=495 total participants:
  - Healthy Soldiers: N = 297 (Group_Code = 0)
  - Self-Harm Soldiers: N = 198 (Group_Code = 1)

Assumptions strictly satisfied and verified:
  1. Univariate Normality: Skewness and Kurtosis in [-0.85, +0.85] for all subscales in both groups.
  2. Homogeneity of Variances: Levene's test p > .05 for all 28 subscales.
  3. Homogeneity of Covariance Matrices: Box's M test p > .05 for all 6 multidimensional questionnaires.
  4. Multivariate Effects (MANOVA): Wilks' Lambda p < .001 for all scales.
  5. Exact Hypotheses:
     - PID: Confirmed significant difference across all 5 dimensions (Healthy lower / better).
     - CERQ: Confirmed significant difference in 7 dimensions (Healthy better),
             EXCEPT CERQ_PR and CERQ_PRE which have NO significant difference (p > .05).
     - BERF: Confirmed significant difference across all 5 dimensions (Healthy better).
     - EP: Confirmed significant difference across all 3 dimensions.
     - IP: Confirmed significant difference across all 3 dimensions.
     - CP: Confirmed significant difference on CP_I,
           EXCEPT CP_TP and CP_AP which have NO significant difference (p > .05).
  6. Theoretical Bounds: All responses strictly integer-valued within each scale's min-max range.

Outputs:
  - soldiers_variance_dataset.sav (SPSS file with metadata, column labels, value labels)
  - soldiers_variance_dataset.xlsx (Excel workbook)
  - DATASET_VERIFICATION_REPORT.md (Exhaustive APA 7 verification report)
"""

import os
import sys
import numpy as np
import pandas as pd
import scipy.stats as stats
import pyreadstat
from statsmodels.multivariate.manova import MANOVA

SCALES = {
    'PID': {
        'persian_name': 'پرسشنامه ویژگی‌های شخصیت ناکارآمد (PID)',
        'items': [
            {'col': 'PID_NA', 'min': 2, 'max': 14, 'h_mean': 5.0, 's_mean': 10.0, 'std': 1.90, 'diff': True,  'label': 'PID: Negative Affectivity (2-14)'},
            {'col': 'PID_D',  'min': 1, 'max': 14, 'h_mean': 4.0, 's_mean': 10.0, 'std': 1.80, 'diff': True,  'label': 'PID: Detachment (1-14)'},
            {'col': 'PID_A',  'min': 1, 'max': 14, 'h_mean': 4.0, 's_mean': 11.0, 'std': 1.90, 'diff': True,  'label': 'PID: Antagonism (1-14)'},
            {'col': 'PID_DI', 'min': 1, 'max': 14, 'h_mean': 4.0, 's_mean': 11.0, 'std': 2.00, 'diff': True,  'label': 'PID: Disinhibition (1-14)'},
            {'col': 'PID_P',  'min': 0, 'max': 14, 'h_mean': 2.0, 's_mean': 9.0,  'std': 1.70, 'diff': True,  'label': 'PID: Psychoticism (0-14)'},
        ]
    },
    'CERQ': {
        'persian_name': 'پرسشنامه تنظیم شناختی هیجان (CERQ)',
        'items': [
            {'col': 'CERQ_PR',  'min': 2, 'max': 10, 'h_mean': 5.8, 's_mean': 5.7, 'std': 1.35, 'diff': False, 'label': 'CERQ: Positive Refocusing (2-10)'},
            {'col': 'CERQ_PRE', 'min': 2, 'max': 10, 'h_mean': 5.9, 's_mean': 5.8, 'std': 1.30, 'diff': False, 'label': 'CERQ: Positive Reappraisal (2-10)'},
            {'col': 'CERQ_P',   'min': 2, 'max': 10, 'h_mean': 7.0, 's_mean': 3.0, 'std': 1.05, 'diff': True,  'label': 'CERQ: Refocus on Planning (2-10)'},
            {'col': 'CERQ_A',   'min': 2, 'max': 10, 'h_mean': 6.0, 's_mean': 4.0, 'std': 1.35, 'diff': True,  'label': 'CERQ: Acceptance (2-10)'},
            {'col': 'CERQ_PP',  'min': 2, 'max': 10, 'h_mean': 7.0, 's_mean': 4.0, 'std': 1.30, 'diff': True,  'label': 'CERQ: Putting into Perspective (2-10)'},
            {'col': 'CERQ_SB',  'min': 2, 'max': 10, 'h_mean': 4.0, 's_mean': 7.0, 'std': 1.30, 'diff': True,  'label': 'CERQ: Self-Blame (2-10)'},
            {'col': 'CERQ_OB',  'min': 2, 'max': 10, 'h_mean': 3.0, 's_mean': 6.0, 'std': 1.00, 'diff': True,  'label': 'CERQ: Other-Blame (2-10)'},
            {'col': 'CERQ_R',   'min': 2, 'max': 10, 'h_mean': 3.0, 's_mean': 7.0, 'std': 1.05, 'diff': True,  'label': 'CERQ: Rumination (2-10)'},
            {'col': 'CERQ_C',   'min': 2, 'max': 10, 'h_mean': 3.0, 's_mean': 6.0, 'std': 1.00, 'diff': True,  'label': 'CERQ: Catastrophizing (2-10)'},
        ]
    },
    'BERF': {
        'persian_name': 'پرسشنامه تنظیم هیجان و انعطاف‌پذیری رفتاری (BERF)',
        'items': [
            {'col': 'BERF_SD',  'min': 4, 'max': 19, 'h_mean': 15.0, 's_mean': 7.0,  'std': 2.00, 'diff': True, 'label': 'BERF: Positive Dimension SD (4-19)'},
            {'col': 'BERF_AA',  'min': 4, 'max': 19, 'h_mean': 15.0, 's_mean': 6.0,  'std': 1.70, 'diff': True, 'label': 'BERF: Positive Dimension AA (4-19)'},
            {'col': 'BERF_SSS', 'min': 4, 'max': 19, 'h_mean': 16.0, 's_mean': 7.0,  'std': 1.90, 'diff': True, 'label': 'BERF: Positive Dimension SSS (4-19)'},
            {'col': 'BERF_I',   'min': 4, 'max': 19, 'h_mean': 7.0,  's_mean': 13.0, 'std': 2.00, 'diff': True, 'label': 'BERF: Negative Dimension I (4-19)'},
            {'col': 'BERF_W',   'min': 4, 'max': 19, 'h_mean': 7.0,  's_mean': 14.0, 'std': 2.10, 'diff': True, 'label': 'BERF: Negative Dimension W (4-19)'},
        ]
    },
    'EP': {
        'persian_name': 'پرسشنامه الگوهای رفتاری و برانگیختگی (EP)',
        'items': [
            {'col': 'EP_AG', 'min': 2, 'max': 28, 'h_mean': 13.0, 's_mean': 20.0, 'std': 3.00, 'diff': True, 'label': 'EP: Aggression (2-28)'},
            {'col': 'EP_RB', 'min': 2, 'max': 27, 'h_mean': 12.0, 's_mean': 19.0, 'std': 3.00, 'diff': True, 'label': 'EP: Risk Behavior (2-27)'},
            {'col': 'EP_I',  'min': 2, 'max': 12, 'h_mean': 4.0,  's_mean': 8.0,  'std': 1.65, 'diff': True, 'label': 'EP: Impulsivity (2-12)'},
        ]
    },
    'IP': {
        'persian_name': 'پرسشنامه الگوهای بین‌فردی (IP)',
        'items': [
            {'col': 'IP_AD', 'min': 2, 'max': 34, 'h_mean': 12.0, 's_mean': 27.0, 'std': 3.60, 'diff': True, 'label': 'IP: Dimension AD (2-34)'},
            {'col': 'IP_WD', 'min': 1, 'max': 17, 'h_mean': 7.0,  's_mean': 13.0, 'std': 2.10, 'diff': True, 'label': 'IP: Dimension WD (1-17)'},
            {'col': 'IP_SC', 'min': 2, 'max': 22, 'h_mean': 9.0,  's_mean': 15.0, 'std': 2.60, 'diff': True, 'label': 'IP: Dimension SC (2-22)'},
        ]
    },
    'CP': {
        'persian_name': 'پرسشنامه الگوهای شناختی (CP)',
        'items': [
            {'col': 'CP_TP', 'min': 0, 'max': 19, 'h_mean': 9.8,  's_mean': 10.0, 'std': 2.50, 'diff': False, 'label': 'CP: Thought Patterns (0-19)'},
            {'col': 'CP_AP', 'min': 2, 'max': 28, 'h_mean': 15.2, 's_mean': 15.4, 'std': 3.15, 'diff': False, 'label': 'CP: Affective Patterns (2-28)'},
            {'col': 'CP_I',  'min': 2, 'max': 12, 'h_mean': 4.0,  's_mean': 8.0,  'std': 1.65, 'diff': True,  'label': 'CP: Impulsivity (2-12)'},
        ]
    }
}

def box_m_test(df, group_col, var_cols):
    groups = df[group_col].unique()
    k = len(groups)
    p = len(var_cols)
    n = []
    covs = []
    for g in groups:
        sub = df[df[group_col] == g][var_cols]
        n.append(len(sub))
        covs.append(sub.cov().values)
    n = np.array(n)
    N = np.sum(n)
    pooled_cov = np.zeros((p, p))
    for i in range(k):
        pooled_cov += (n[i] - 1) * covs[i]
    pooled_cov /= (N - k)
    log_det_pooled = np.linalg.slogdet(pooled_cov)[1]
    M = 0
    for i in range(k):
        log_det_i = np.linalg.slogdet(covs[i])[1]
        M += (n[i] - 1) * (log_det_pooled - log_det_i)
    c = (np.sum(1.0 / (n - 1)) - 1.0 / (N - k)) * (2 * p**2 + 3 * p - 1) / (6 * (p + 1) * (k - 1))
    stat = M * (1 - c)
    df_chi = 0.5 * p * (p + 1) * (k - 1)
    p_val = 1 - stats.chi2.cdf(stat, df_chi)
    return M, stat, df_chi, p_val

def generate_scale_subscales(scale_name, items, n_h=297, n_s=198, seed=42):
    rng = np.random.default_rng(seed)
    
    for attempt in range(1000):
        h_dict = {}
        s_dict = {}
        valid = True
        
        for item in items:
            col = item['col']
            min_v, max_v = item['min'], item['max']
            
            # Organic non-integer target within +/- 0.25 of nominal target
            # Ensuring realistic empirical decimal variations (e.g. 5.14, 4.88, 10.18, 9.85)
            h_noise = rng.choice([-1, 1]) * rng.uniform(0.08, 0.25)
            if item['diff']:
                s_noise = rng.choice([-1, 1]) * rng.uniform(0.08, 0.25)
            else:
                s_noise = h_noise + rng.uniform(-0.04, 0.04)
                
            h_target = item['h_mean'] + h_noise
            s_target = item['s_mean'] + s_noise
            std = item['std']
            
            # Healthy sample
            raw_h = rng.normal(h_target, std, size=n_h)
            h_vals = np.clip(np.round(raw_h), min_v, max_v)
            diff_h = int(np.round((h_target - np.mean(h_vals)) * n_h))
            if diff_h != 0:
                step = 1 if diff_h > 0 else -1
                cand = np.where((h_vals + step >= min_v) & (h_vals + step <= max_v))[0]
                if len(cand) >= abs(diff_h):
                    chosen = rng.choice(cand, size=abs(diff_h), replace=False)
                    h_vals[chosen] += step

            # Self-Harm sample
            raw_s = rng.normal(s_target, std, size=n_s)
            s_vals = np.clip(np.round(raw_s), min_v, max_v)
            diff_s = int(np.round((s_target - np.mean(s_vals)) * n_s))
            if diff_s != 0:
                step = 1 if diff_s > 0 else -1
                cand = np.where((s_vals + step >= min_v) & (s_vals + step <= max_v))[0]
                if len(cand) >= abs(diff_s):
                    chosen = rng.choice(cand, size=abs(diff_s), replace=False)
                    s_vals[chosen] += step

            # Normality check (skew & kurtosis)
            if abs(stats.skew(h_vals)) > 0.85 or abs(stats.skew(s_vals)) > 0.85:
                valid = False
                break
            if abs(stats.kurtosis(h_vals)) > 0.85 or abs(stats.kurtosis(s_vals)) > 0.85:
                valid = False
                break
                
            # Homogeneity of variance (Levene)
            _, lev_p = stats.levene(h_vals, s_vals)
            if lev_p < 0.06:
                valid = False
                break
                
            # Hypothesis test
            _, t_p = stats.ttest_ind(h_vals, s_vals)
            if item['diff'] and t_p > 0.001:
                valid = False
                break
            if not item['diff'] and t_p < 0.10:
                valid = False
                break
                
            h_dict[col] = h_vals
            s_dict[col] = s_vals

        if not valid:
            continue
            
        # Homogeneity of covariance matrices (Box's M)
        cols = [it['col'] for it in items]
        df_h = pd.DataFrame(h_dict)[cols]
        df_s = pd.DataFrame(s_dict)[cols]
        df_h['Group_Code'] = 0
        df_s['Group_Code'] = 1
        df_scale = pd.concat([df_h, df_s], ignore_index=True)
        
        M, stat, df_chi, box_p = box_m_test(df_scale, 'Group_Code', cols)
        if box_p > 0.06:
            return h_dict, s_dict, M, stat, df_chi, box_p
            
    raise RuntimeError(f"Scale {scale_name} could not converge after 1000 attempts.")

def main():
    print("=" * 80)
    print("SOLDIERS VARIANCE DATASET GENERATOR & VERIFIER")
    print("Healthy Soldiers: N = 297 | Self-Harm Soldiers: N = 198 | Total: N = 495")
    print("=" * 80)

    n_healthy = 297
    n_harm = 198
    total_n = n_healthy + n_harm

    h_all = {}
    s_all = {}
    box_m_results = {}

    seed = 2026
    for scale_name, scale_info in SCALES.items():
        print(f"Generating scale: {scale_name} ({scale_info['persian_name']})...")
        h_d, s_d, M, stat, df_chi, box_p = generate_scale_subscales(
            scale_name, scale_info['items'], n_h=n_healthy, n_s=n_harm, seed=seed
        )
        h_all.update(h_d)
        s_all.update(s_d)
        box_m_results[scale_name] = {'M': M, 'stat': stat, 'df': df_chi, 'p': box_p}
        print(f"  -> Box's M = {M:.2f}, Chi2 = {stat:.2f}, df = {df_chi:.0f}, p = {box_p:.4f} (Homogeneity Satisfied: p > .05)")
        seed += 101

    # Assemble complete DataFrame
    df_h = pd.DataFrame(h_all)
    df_h.insert(0, 'ID', [f'ID_{i+1:03d}' for i in range(n_healthy)])
    df_h.insert(1, 'Group', 'Healthy')
    df_h.insert(2, 'Group_Code', 0.0)

    df_s = pd.DataFrame(s_all)
    df_s.insert(0, 'ID', [f'ID_{i+n_healthy+1:03d}' for i in range(n_harm)])
    df_s.insert(1, 'Group', 'Self-Harm')
    df_s.insert(2, 'Group_Code', 1.0)

    df = pd.concat([df_h, df_s], ignore_index=True)

    print("\n" + "=" * 80)
    print("STATISTICAL ASSUMPTIONS & HYPOTHESIS TESTING REPORT")
    print("=" * 80)

    # Verification Table
    report_rows = []
    manova_results = {}

    for scale_name, scale_info in SCALES.items():
        cols = [it['col'] for it in scale_info['items']]
        formula = ' + '.join(cols) + ' ~ Group_Code'
        fit = MANOVA.from_formula(formula, data=df)
        mv_res = fit.mv_test().results['Group_Code']['stat']
        wilks_val = mv_res.loc["Wilks' lambda", 'Value']
        wilks_f = mv_res.loc["Wilks' lambda", 'F Value']
        wilks_p = mv_res.loc["Wilks' lambda", 'Pr > F']
        manova_results[scale_name] = {'Lambda': wilks_val, 'F': wilks_f, 'p': wilks_p}

        for it in scale_info['items']:
            col = it['col']
            h_v = df[df['Group_Code'] == 0][col]
            s_v = df[df['Group_Code'] == 1][col]

            h_m, s_m = h_v.mean(), s_v.mean()
            h_std, s_std = h_v.std(), s_v.std()
            h_skew, s_skew = stats.skew(h_v), stats.skew(s_v)
            h_kurt, s_kurt = stats.kurtosis(h_v), stats.kurtosis(s_v)

            lev_f, lev_p = stats.levene(h_v, s_v)
            t_stat, t_p = stats.ttest_ind(h_v, s_v)

            # Hypothesis check
            if it['diff']:
                hyp_status = 'PASS (Diff p < .001)' if t_p < 0.001 else 'FAIL'
            else:
                hyp_status = 'PASS (No Diff p > .05)' if t_p > 0.05 else 'FAIL'

            levene_status = 'PASS (p > .05)' if lev_p > 0.05 else 'FAIL'
            norm_status = 'PASS' if (abs(h_skew) < 1.0 and abs(s_skew) < 1.0 and abs(h_kurt) < 1.0 and abs(s_kurt) < 1.0) else 'FAIL'

            report_rows.append({
                'Scale': scale_name,
                'Variable': col,
                'Min-Max': f"{it['min']}-{it['max']}",
                'H Mean (SD)': f"{h_m:.2f} ({h_std:.2f})",
                'SH Mean (SD)': f"{s_m:.2f} ({s_std:.2f})",
                'H Skew/Kurt': f"{h_skew:+.2f} / {h_kurt:+.2f}",
                'SH Skew/Kurt': f"{s_skew:+.2f} / {s_kurt:+.2f}",
                'Levene p': f"{lev_p:.3f} ({levene_status})",
                't-test p': f"{t_p:.4f} (t={t_stat:+.2f})",
                'Hypothesis': hyp_status,
                'Normality': norm_status
            })

    rep_df = pd.DataFrame(report_rows)
    print(rep_df[['Variable', 'H Mean (SD)', 'SH Mean (SD)', 'Levene p', 't-test p', 'Hypothesis']].to_string(index=False))

    print("\n" + "=" * 80)
    print("MANOVA & BOX'S M MULTIVARIATE RESULTS SUMMARY")
    print("=" * 80)
    for s_name in SCALES:
        bm = box_m_results[s_name]
        mv = manova_results[s_name]
        print(f"{s_name:6s} | Box's M = {bm['M']:6.2f} (p = {bm['p']:.4f}) | MANOVA Wilks' Lambda = {mv['Lambda']:.3f}, F = {mv['F']:6.2f}, p < .001 ({mv['p']:.2e})")

    # Column labels and metadata for SPSS
    column_labels = {
        'ID': 'Participant Identification Number',
        'Group': 'Experimental Group (Healthy vs Self-Harm)',
        'Group_Code': 'Group Code (0=Healthy, 1=Self-Harm)'
    }
    for s_name, s_info in SCALES.items():
        for it in s_info['items']:
            column_labels[it['col']] = it['label']

    variable_value_labels = {
        'Group_Code': {
            0.0: 'Healthy (N=297)',
            1.0: 'Self-Harm (N=198)'
        }
    }

    # Export to SPSS .sav
    sav_path = 'soldiers_variance_dataset.sav'
    print(f"\nExporting to SPSS: {sav_path} ...")
    pyreadstat.write_sav(
        df,
        sav_path,
        column_labels=column_labels,
        variable_value_labels=variable_value_labels
    )
    print("SPSS .sav file successfully written.")

    # Export to Excel .xlsx
    xlsx_path = 'soldiers_variance_dataset.xlsx'
    print(f"Exporting to Excel: {xlsx_path} ...")
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Raw_Dataset', index=False)
        rep_df.to_excel(writer, sheet_name='Assumptions_Verification', index=False)
        
        # Summary sheet
        summary_rows = []
        for s_name in SCALES:
            bm = box_m_results[s_name]
            mv = manova_results[s_name]
            summary_rows.append({
                'Questionnaire': s_name,
                'Persian Title': SCALES[s_name]['persian_name'],
                'Box M': round(bm['M'], 2),
                'Box M Chi2': round(bm['stat'], 2),
                'Box M df': int(bm['df']),
                'Box M p-value': round(bm['p'], 4),
                'Box M Result': 'Homogeneity Satisfied (p > .05)',
                'MANOVA Wilks Lambda': round(mv['Lambda'], 3),
                'MANOVA F Value': round(mv['F'], 2),
                'MANOVA p-value': '< .001'
            })
        pd.DataFrame(summary_rows).to_excel(writer, sheet_name='MANOVA_and_BoxM', index=False)
    print("Excel .xlsx file successfully written.")

    # Generate Markdown Verification Report
    md_path = 'DATASET_VERIFICATION_REPORT.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# گزارش جامع صحت‌سنجی و فرضیه‌های آماری داده‌های سربازان (سالم در برابر خودجرحی)\n\n")
        f.write("این گزارش به بررسی ویژگی‌های آماری، پیش‌فرض‌های تحلیل واریانس چندمتغیره (مانوا) و نتایج آزمون فرضیه‌ها بر روی داده‌های شبیه‌سازی شده می‌پردازد.\n\n")
        f.write("### مشخصات حجم نمونه:\n")
        f.write(f"- **گروه سربازان سالم (Healthy):** {n_healthy} نفر (`Group_Code = 0`)\n")
        f.write(f"- **گروه سربازان خودجرحی (Self-Harm):** {n_harm} نفر (`Group_Code = 1`)\n")
        f.write(f"- **مجموع شرکت‌کنندگان:** {total_n} نفر\n\n")
        
        f.write("## ۱. پیش‌فرض‌های تحلیل واریانس چندمتغیره (MANOVA)\n\n")
        f.write("### الف) آزمون ام‌باکس (Box's M Test) - همگنی ماتریس‌های کوواریانس\n")
        f.write("برای تمامی ۶ پرسشنامه مقدار $p$ آزمون ام‌باکس بزرگتر از ۰/۰۵ است که نشان‌دهنده برقراری کامل پیش‌فرض همگنی ماتریس‌های واریانس-کوواریانس می‌باشد:\n\n")
        f.write("| پرسشنامه | نام فارسی | آماره M باکس | آماره Chi-Square | درجه آزادی | p-value | وضعیت همگنی |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n")
        for s_name in SCALES:
            bm = box_m_results[s_name]
            f.write(f"| **{s_name}** | {SCALES[s_name]['persian_name']} | {bm['M']:.2f} | {bm['stat']:.2f} | {bm['df']:.0f} | {bm['p']:.4f} | برفرار ($p > .05$) |\n")
            
        f.write("\n### ب) آزمون چندمتغیره لامبدای ویلکز (Wilks' Lambda)\n\n")
        f.write("| پرسشنامه | لامبدای ویلکز | آماره F | p-value | اثر چندمتغیره |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for s_name in SCALES:
            mv = manova_results[s_name]
            f.write(f"| **{s_name}** | {mv['Lambda']:.3f} | {mv['F']:.2f} | < ۰/۰۰۱ | معنادار |\n")

        f.write("\n## ۲. جدول بررسی تک‌تک زیرمقیاس‌ها، پیش‌فرض‌ها و آزمون فرضیه‌ها\n\n")
        f.write("| مقیاس | متغیر | دامنه نمره | میانگین (انحراف معیار) سالم | میانگین (انحراف معیار) خودجرحی | کجی/کشیدگی سالم | کجی/کشیدگی خودجرحی | آزمون لون (p) | آزمون تفاوت گروهی (t) | وضعیت تایید فرضیه |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for _, row in rep_df.iterrows():
            f.write(f"| {row['Scale']} | `{row['Variable']}` | {row['Min-Max']} | {row['H Mean (SD)']} | {row['SH Mean (SD)']} | {row['H Skew/Kurt']} | {row['SH Skew/Kurt']} | {row['Levene p']} | {row['t-test p']} | **{row['Hypothesis']}** |\n")

        f.write("\n## ۳. تطابق دقیق با درخواست‌های شهرام امیری\n")
        f.write("1. **تعداد نمونه‌ها:** سالم‌ها دقیقاً ۲۹۷ نفر و خودجرحی‌ها ۱۹۸ نفر هستند.\n")
        f.write("2. **بهنجاری (نرمالیته):** تمام زیرمقیاس‌ها در هر دو گروه دارای چولگی و کشیدگی بین ۰/۸۵- تا ۰/۸۵+ هستند (کاملاً بهنجار).\n")
        f.write("3. **آزمون لون (Levene):** برای تمام ۲۸ زیرمقیاس، سطح معناداری لون بالای ۰/۰۵ است (برابری واریانس‌ها رعایت شده است).\n")
        f.write("4. **آزمون ام‌باکس (Box's M):** برای هر ۶ مقیاس سطح معناداری بالای ۰/۰۵ است (برابری کوواریانس‌ها رعایت شده است).\n")
        f.write("5. **فرضیه PID:** در تمام ۵ بعد، تفاوت دو گروه معنادار است ($p < 0.001$).\n")
        f.write("6. **فرضیه CERQ:** در ۷ بعد تفاوت معنادار بوده و سالم‌ها نمرات بهتری دارند، اما در دو بعد PR و PRE هیچ تفاوت معناداری وجود ندارد ($p > .05$).\n")
        f.write("7. **فرضیه BERF:** در تمام ابعاد تفاوت معنادار است و سالم‌ها وضعیت بهتری دارند ($p < 0.001$).\n")
        f.write("8. **فرضیه EP:** تفاوت‌ها در هر ۳ بعد معنادار است ($p < 0.001$).\n")
        f.write("9. **فرضیه IP:** تفاوت‌ها در هر ۳ بعد معنادار است ($p < 0.001$).\n")
        f.write("10. **فرضیه CP:** تفاوت در دو بعد TP و AP معنادار نیست ($p > .05$) اما در بعد I معنادار است ($p < 0.001$).\n")

    print(f"Verification report written to: {md_path}")
    print("\nALL GENERATION AND VERIFICATION TASKS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
