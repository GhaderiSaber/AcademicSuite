import os
import json
import numpy as np
import pandas as pd

def cronbach_alpha(df_items):
    item_vars = df_items.var(axis=0, ddof=1)
    t_var = df_items.sum(axis=1).var(ddof=1)
    n = df_items.shape[1]
    if n <= 1 or t_var == 0:
        return 0.0
    return float((n / (n - 1)) * (1 - item_vars.sum() / t_var))

def main():
    raw_path = "01_raw_inputs/روانپزشکی.xlsx"
    out_dir = "02_processed_data"
    os.makedirs(out_dir, exist_ok=True)
    
    df = pd.read_excel(raw_path)
    N = len(df)
    print(f"Loaded raw dataset with N = {N} rows and {len(df.columns)} columns.")
    
    scored_df = pd.DataFrame()
    
    # 1. Demographics
    scored_df['id'] = range(1, N + 1)
    
    def clean_age(val):
        v = str(val).strip()
        trans = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
        v = v.translate(trans)
        try:
            val_int = int(float(v))
            if 14 <= val_int <= 20:
                return val_int
            elif val_int > 20:
                return val_int
            return val_int
        except:
            return 16
            
    scored_df['Age'] = df.iloc[:, 1].apply(clean_age)
    scored_df['Gender'] = df.iloc[:, 2].astype(str).str.strip()
    scored_df['Ethnicity'] = df.iloc[:, 3].astype(str).str.strip()
    scored_df['School_Type'] = df.iloc[:, 4].astype(str).str.strip()
    scored_df['Marital_Status'] = df.iloc[:, 5].astype(str).str.strip()
    scored_df['Grade'] = df.iloc[:, 8].astype(str).str.strip()
    scored_df['School_District'] = df.iloc[:, 9].astype(str).str.strip()
    scored_df['Living_Arrangement'] = df.iloc[:, 11].astype(str).str.strip()
    scored_df['Father_Education'] = df.iloc[:, 12].astype(str).str.strip()
    scored_df['Mother_Education'] = df.iloc[:, 13].astype(str).str.strip()
    scored_df['Family_SES'] = df.iloc[:, 14].astype(str).str.strip()
    
    scored_df['Gender_Female'] = scored_df['Gender'].apply(lambda x: 1 if ('زن' in str(x) or 'دختر' in str(x)) else 0)
    
    # 2. Sansone Self-Harm Inventory (SHI) - 21 items (cols 15-35)
    shi_cols = df.columns[15:36]
    shi_items = pd.DataFrame()
    for i, col in enumerate(shi_cols):
        def score_shi_item(val):
            v = str(val).strip()
            if v in ['خیر', 'nan', '']:
                return 0
            return 1
        shi_items[f'SHI_{i+1}'] = df[col].apply(score_shi_item)
        
    scored_df['SHI_Total'] = shi_items.sum(axis=1)
    scored_df['SelfHarm_Presence'] = (scored_df['SHI_Total'] > 0).astype(int)
    scored_df['SelfHarm_ClinicalRisk'] = (scored_df['SHI_Total'] >= 5).astype(int)
    
    direct_idx = [1, 3, 4, 5, 8, 9, 16]
    indirect_idx = [i for i in range(1, 22) if i not in direct_idx]
    scored_df['SHI_Direct'] = shi_items[[f'SHI_{i}' for i in direct_idx]].sum(axis=1)
    scored_df['SHI_Indirect'] = shi_items[[f'SHI_{i}' for i in indirect_idx]].sum(axis=1)
    
    # 3. Spence Children's Anxiety Scale (SCAS) - 38 items (cols 36-79, excluding 6 positive fillers)
    filler_indices = [46, 52, 61, 66, 72, 77]
    anxiety_col_indices = [i for i in range(36, 80) if i not in filler_indices]
    
    scas_map = {'هیچ وقت': 0, 'گاهی اوقات': 1, 'اغلب': 2, 'همیشه': 3}
    scas_items = pd.DataFrame()
    for idx, col_idx in enumerate(anxiety_col_indices):
        scas_items[f'SCAS_{idx+1}'] = df.iloc[:, col_idx].astype(str).str.strip().map(scas_map).fillna(0).astype(int)
        
    scored_df['Anxiety_Total'] = scas_items.sum(axis=1)
    
    # 4. Children's Depression Inventory (CDI) - 27 items (cols 80-106)
    rev_items_cdi = [2, 5, 7, 8, 9, 10, 11, 13, 15, 16, 18, 21, 25]
    cdi_items = pd.DataFrame()
    for i in range(27):
        item_num = i + 1
        col_idx = 80 + i
        s = df.iloc[:, col_idx].astype(str).str.strip()
        if item_num in rev_items_cdi:
            mapping = {'الف': 2, 'ب': 1, 'ج': 0}
        else:
            mapping = {'الف': 0, 'ب': 1, 'ج': 2}
        cdi_items[f'CDI_{item_num}'] = s.map(mapping).fillna(0).astype(int)
        
    scored_df['Depression_Total'] = cdi_items.sum(axis=1)
    scored_df['Depression_Clinical'] = (scored_df['Depression_Total'] >= 13).astype(int)
    
    # 5. Suicide Behaviors Questionnaire-Revised (SBQ-R) - 4 items (cols 107-110)
    c1, c2, c3, c4 = df.columns[107:111]
    def map_sbq1(v):
        v = str(v).strip()
        if 'هرگز' in v: return 1
        if 'گذرا' in v: return 2
        if 'برنامه' in v: return 3
        if 'تلاش' in v: return 4
        return 1

    def map_sbq2(v):
        v = str(v).strip()
        if 'هرگز' in v: return 1
        if 'ندر' in v or '١ بار' in v: return 2
        if 'گاهی' in v or '٢ بار' in v: return 3
        if 'اغلب' in v or '٣ تا ٤' in v: return 4
        if 'زیاد' in v or '٥ بار' in v: return 5
        return 1

    def map_sbq3(v):
        v = str(v).strip()
        if 'خیر' in v: return 1
        if 'نمی‌خواستم' in v or 'نداشتم' in v: return 2
        if 'واقعا' in v and ('می‌خواستم' in v or 'انجام دهم' in v): return 3
        return 1

    def map_sbq4(v):
        v = str(v).strip()
        if 'هرگز' in v: return 0
        if 'خیلی بعید' in v: return 1
        if 'بعید است' in v: return 2
        if 'کمی بعید' in v: return 2
        if 'کمی احتمال' in v: return 3
        if 'احتمال دارد' in v: return 4
        if 'خیلی احتمال' in v: return 5
        return 0

    scored_df['SBQ_1_Lifetime'] = df[c1].apply(map_sbq1)
    scored_df['SBQ_2_PastYear'] = df[c2].apply(map_sbq2)
    scored_df['SBQ_3_Threat'] = df[c3].apply(map_sbq3)
    scored_df['SBQ_4_Future'] = df[c4].apply(map_sbq4)
    scored_df['Suicide_Total'] = (
        scored_df['SBQ_1_Lifetime'] + 
        scored_df['SBQ_2_PastYear'] + 
        scored_df['SBQ_3_Threat'] + 
        scored_df['SBQ_4_Future']
    )
    scored_df['Suicide_Risk'] = (scored_df['Suicide_Total'] >= 7).astype(int)
    scored_df['Suicide_Ideation_Lifetime'] = (scored_df['SBQ_1_Lifetime'] >= 2).astype(int)
    scored_df['Suicide_Attempt_Lifetime'] = (scored_df['SBQ_1_Lifetime'] == 4).astype(int)
    
    # 6. Body Image Concern Inventory (BICI) - 7 items (cols 111-117)
    bici_map = {'هرگز (0)': 0, 'به اندازه دیگران (1)': 1, 'بیشتر از دیگران(2)': 2, 'خیلی بیشتر از دیگران(3)': 3}
    bici_items = pd.DataFrame()
    for i in range(7):
        col_idx = 111 + i
        bici_items[f'BICI_{i+1}'] = df.iloc[:, col_idx].astype(str).str.strip().map(bici_map).fillna(0).astype(int)
        
    scored_df['BodyDysmorphia_Total'] = bici_items.sum(axis=1)
    
    # Save scored dataset
    scored_out_path = os.path.join(out_dir, "data_scored.xlsx")
    scored_df.to_excel(scored_out_path, index=False)
    print(f"Saved scored dataset to {scored_out_path}")
    
    # Calculate Cronbach Alphas
    alpha_shi = cronbach_alpha(shi_items)
    alpha_scas = cronbach_alpha(scas_items)
    alpha_cdi = cronbach_alpha(cdi_items)
    alpha_sbqr = cronbach_alpha(scored_df[['SBQ_1_Lifetime', 'SBQ_2_PastYear', 'SBQ_3_Threat', 'SBQ_4_Future']])
    alpha_bici = cronbach_alpha(bici_items)
    
    scoring_log = {
        "dataset_name": "Qom High School Self-Harm and Suicide Study",
        "sample_size": N,
        "scales": {
            "SHI_Self_Harm": {
                "items_count": 21,
                "scoring": "Binary 0/1",
                "cronbach_alpha": round(alpha_shi, 3),
                "mean": round(float(scored_df['SHI_Total'].mean()), 2),
                "sd": round(float(scored_df['SHI_Total'].std()), 2),
                "min": int(scored_df['SHI_Total'].min()),
                "max": int(scored_df['SHI_Total'].max()),
                "prevalence_any_self_harm_pct": round(float(scored_df['SelfHarm_Presence'].mean() * 100), 2),
                "clinical_risk_cutoff_5_pct": round(float(scored_df['SelfHarm_ClinicalRisk'].mean() * 100), 2)
            },
            "SCAS_Anxiety": {
                "items_count": 38,
                "scoring": "Likert 0 to 3",
                "cronbach_alpha": round(alpha_scas, 3),
                "mean": round(float(scored_df['Anxiety_Total'].mean()), 2),
                "sd": round(float(scored_df['Anxiety_Total'].std()), 2),
                "min": int(scored_df['Anxiety_Total'].min()),
                "max": int(scored_df['Anxiety_Total'].max())
            },
            "CDI_Depression": {
                "items_count": 27,
                "scoring": "3-point (0 to 2)",
                "cronbach_alpha": round(alpha_cdi, 3),
                "mean": round(float(scored_df['Depression_Total'].mean()), 2),
                "sd": round(float(scored_df['Depression_Total'].std()), 2),
                "min": int(scored_df['Depression_Total'].min()),
                "max": int(scored_df['Depression_Total'].max()),
                "clinical_depression_pct": round(float(scored_df['Depression_Clinical'].mean() * 100), 2)
            },
            "SBQ_R_Suicide": {
                "items_count": 4,
                "scoring": "Multi-category sum (range 3-18)",
                "cronbach_alpha": round(alpha_sbqr, 3),
                "mean": round(float(scored_df['Suicide_Total'].mean()), 2),
                "sd": round(float(scored_df['Suicide_Total'].std()), 2),
                "min": int(scored_df['Suicide_Total'].min()),
                "max": int(scored_df['Suicide_Total'].max()),
                "suicide_risk_cutoff_7_pct": round(float(scored_df['Suicide_Risk'].mean() * 100), 2),
                "lifetime_ideation_pct": round(float(scored_df['Suicide_Ideation_Lifetime'].mean() * 100), 2),
                "lifetime_attempt_pct": round(float(scored_df['Suicide_Attempt_Lifetime'].mean() * 100), 2)
            },
            "BICI_Body_Dysmorphia": {
                "items_count": 7,
                "scoring": "Likert 0 to 3 (range 0-21)",
                "cronbach_alpha": round(alpha_bici, 3),
                "mean": round(float(scored_df['BodyDysmorphia_Total'].mean()), 2),
                "sd": round(float(scored_df['BodyDysmorphia_Total'].std()), 2),
                "min": int(scored_df['BodyDysmorphia_Total'].min()),
                "max": int(scored_df['BodyDysmorphia_Total'].max())
            }
        },
        "demographics_summary": {
            "gender_counts": scored_df['Gender'].value_counts().to_dict(),
            "grade_counts": scored_df['Grade'].value_counts().to_dict(),
            "mean_age": round(float(scored_df['Age'].mean()), 2),
            "sd_age": round(float(scored_df['Age'].std()), 2)
        }
    }
    
    log_out_path = os.path.join(out_dir, "scoring_log.json")
    with open(log_out_path, "w", encoding="utf-8") as f:
        json.dump(scoring_log, f, ensure_ascii=False, indent=2)
    print(f"Saved scoring log to {log_out_path}")

if __name__ == "__main__":
    main()
