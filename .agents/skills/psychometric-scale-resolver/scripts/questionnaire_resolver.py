#!/usr/bin/env python3
"""
Questionnaire Resolver & Factor Scoring Engine (questionnaire_resolver.py)
-------------------------------------------------------------------------
Automates psychometric scale lookup, subscale/factor extraction, reverse-item scoring,
and dataset factor aggregation for psychological, counseling, and behavioral research.

Sources:
1. Tier 1 (Project Folder): Local questionnaire files or proposal/methodology data.
2. Tier 2 (Excel Registry): /Users/saber/Desktop/academic_suite/Questionnaires.xlsx (4,880 rows)
   - Scale names (English & Persian), Subscales, Item mappings, Likert scoring ranges,
     Min/Max/Theoretical means, and Reverse scoring items.
3. Tier 3 (Google Drive Master Library):
   - /Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/Pending Works/Questionnaire(s)
   - 2,206 original psychometric instruments (.pdf, .docx, .doc).
"""

import os
import re
import sys
import json
import argparse
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

# Default paths
DEFAULT_EXCEL_REGISTRY = "/Users/saber/Desktop/academic_suite/Questionnaires.xlsx"
DEFAULT_GDRIVE_DIRS = [
    "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/Pending Works/Questionnaires",
    "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/Pending Works/Questionnaire"
]

def find_excel_registry(custom_path: Optional[str] = None) -> Optional[str]:
    """Resolve path to Questionnaires.xlsx."""
    candidates = []
    if custom_path:
        candidates.append(custom_path)
    candidates.extend([
        os.path.abspath("Questionnaires.xlsx"),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "Questionnaires.xlsx"),
        DEFAULT_EXCEL_REGISTRY
    ])
    for c in candidates:
        if os.path.isfile(c):
            return os.path.abspath(c)
    return None

def find_gdrive_library(custom_path: Optional[str] = None) -> Optional[str]:
    """Resolve path to Google Drive questionnaire library folder."""
    if custom_path and os.path.isdir(custom_path):
        return os.path.abspath(custom_path)
    for p in DEFAULT_GDRIVE_DIRS:
        if os.path.isdir(p):
            return os.path.abspath(p)
    return None

def parse_item_indices(item_str: Any) -> List[int]:
    """
    Parse item lists into sorted unique integer lists.
    Handles: '1-7', '1–28', '1, 3, 8, 10, 11', '1-5, 8, 11-15', '12, 14 (See manual)', '10 items'.
    """
    if item_str is None or pd.isna(item_str):
        return []
    s = str(item_str).strip()
    # Strip parenthetical comments
    s = re.sub(r"\(.*?\)", "", s).strip()
    # Check for pattern like 'N items'
    m_items = re.match(r"^(\d+)\s+items?$", s, re.IGNORECASE)
    if m_items:
        return list(range(1, int(m_items.group(1)) + 1))
        
    s = s.replace("،", ",").replace("؛", ",").replace(";", ",")
    s = s.replace("–", "-").replace("—", "-")
    
    items = []
    parts = s.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m_range = re.match(r"^(\d+)\s*-\s*(\d+)$", part)
        if m_range:
            start, end = int(m_range.group(1)), int(m_range.group(2))
            if start <= end:
                items.extend(range(start, end + 1))
        else:
            m_num = re.search(r"\b(\d+)\b", part)
            if m_num:
                items.append(int(m_num.group(1)))
    return sorted(list(set(items)))

def parse_scoring_range(scoring_str: Any) -> Tuple[Optional[int], Optional[int]]:
    """Extract (min_item_score, max_item_score) from scoring description."""
    if scoring_str is None or pd.isna(scoring_str):
        return None, None
    s = str(scoring_str).strip()
    m = re.search(r"(\d+)\s+to\s+(\d+)", s, re.IGNORECASE)
    if m:
        return int(m.group(1)), int(m.group(2))
    m2 = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if m2:
        return int(m2.group(1)), int(m2.group(2))
    if "dichotomous" in s.lower():
        if "0-1" in s or "0 to 1" in s:
            return 0, 1
        elif "1-2" in s or "1 to 2" in s:
            return 1, 2
        return 0, 1
    return None, None

def search_registry(query: str, excel_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search Questionnaires.xlsx for scales matching query."""
    path = find_excel_registry(excel_path)
    if not path:
        return []
    
    df = pd.read_excel(path, sheet_name="Table 1")
    q_lower = query.lower().strip()
    
    mask = (
        df["Scale name"].astype(str).str.lower().str.contains(q_lower, na=False) |
        df["Scale Persian Name"].astype(str).str.contains(query.strip(), na=False) |
        df["Abbreviation"].astype(str).str.lower().str.contains(q_lower, na=False) |
        df["Subscale name"].astype(str).str.lower().str.contains(q_lower, na=False)
    )
    matches = df[mask]
    
    scales_grouped = {}
    for _, row in matches.iterrows():
        s_name = str(row["Scale name"])
        sub_name = str(row.get("Subscale name", "")).strip()
        if s_name not in scales_grouped:
            scales_grouped[s_name] = {
                "scale_name": s_name,
                "scale_persian_name": str(row.get("Scale Persian Name", "")),
                "abbreviation": str(row.get("Abbreviation", "")),
                "scoring_method": str(row.get("Scoring method", "")),
                "source": str(row.get("Source", "")),
                "subscales": [],
                "_seen_subscales": set()
            }
        
        # Deduplicate identical subscales
        if sub_name not in scales_grouped[s_name]["_seen_subscales"]:
            scales_grouped[s_name]["_seen_subscales"].add(sub_name)
            scales_grouped[s_name]["subscales"].append({
                "subscale_name": sub_name,
                "items_raw": str(row.get("Items of each subscale", "")),
                "items_parsed": parse_item_indices(row.get("Items of each subscale")),
                "min_score": str(row.get("Min score", "")),
                "max_score": str(row.get("Max score", "")),
                "theoretical_mean": str(row.get("Theoretical mean", "")),
                "reverse_items_raw": str(row.get("Reverse scoring item", "")),
                "reverse_items_parsed": parse_item_indices(row.get("Reverse scoring item"))
            })
            
    # Remove internal tracking set
    results = []
    for s_info in scales_grouped.values():
        s_info.pop("_seen_subscales", None)
        results.append(s_info)
        
    return results

def search_gdrive_library(query: str, gdrive_dir: Optional[str] = None) -> List[str]:
    """Search Google Drive questionnaire repository for matching files."""
    lib_path = find_gdrive_library(gdrive_dir)
    if not lib_path or not os.path.isdir(lib_path):
        return []
    
    files = os.listdir(lib_path)
    q_clean = query.strip().lower()
    if not q_clean:
        return []

    # Priority 1: Exact substring match
    exact_matches = [os.path.join(lib_path, f) for f in files if q_clean in f.lower()]
    if exact_matches:
        return sorted(exact_matches)

    # Priority 2: Distinctive terms (excluding generic stopwords like پرسشنامه, مقیاس, scale, etc.)
    stopwords = {"پرسشنامه", "مقياس", "مقیاس", "آزمون", "آزمون", "تست", "فرم", "کتاب", "scale", "questionnaire", "inventory", "test"}
    q_terms = [t for t in q_clean.split() if len(t) > 2 and t not in stopwords]
    if not q_terms:
        q_terms = [t for t in q_clean.split() if len(t) > 2]
        
    matches = []
    for f in files:
        f_lower = f.lower()
        # All distinctive terms or substantial match
        if all(term in f_lower for term in q_terms) if q_terms else False:
            matches.append(os.path.join(lib_path, f))
            
    if not matches and q_terms:
        # Fallback to any distinctive term match
        for f in files:
            f_lower = f.lower()
            if any(term in f_lower for term in q_terms):
                matches.append(os.path.join(lib_path, f))
                
    return sorted(matches)

def get_scale_profile(scale_name_or_query: str, excel_path: Optional[str] = None, gdrive_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve full psychometric profile, scoring method, subscale items, and reverse keys."""
    results = search_registry(scale_name_or_query, excel_path)
    if not results:
        # Try finding in gdrive files directly
        gdrive_matches = search_gdrive_library(scale_name_or_query, gdrive_dir)
        return {
            "scale_name": scale_name_or_query,
            "found_in_registry": False,
            "gdrive_files": gdrive_matches,
            "subscales": []
        }
        
    # Best match: prioritize exact or highest matching
    profile = results[0]
    profile["found_in_registry"] = True
    
    # Parse scoring range (min_item, max_item)
    min_item, max_item = parse_scoring_range(profile.get("scoring_method"))
    profile["item_min_score"] = min_item
    profile["item_max_score"] = max_item
    
    # Collect all reverse items across total scale & subscales
    all_reverse_items = set()
    total_scale_items = set()
    for sub in profile.get("subscales", []):
        all_reverse_items.update(sub["reverse_items_parsed"])
        if "total" in sub["subscale_name"].lower() or "overall" in sub["subscale_name"].lower():
            total_scale_items.update(sub["items_parsed"])
        else:
            total_scale_items.update(sub["items_parsed"])
            
    profile["all_reverse_items"] = sorted(list(all_reverse_items))
    profile["all_items"] = sorted(list(total_scale_items))
    profile["total_items_count"] = len(profile["all_items"])
    
    # Find matching files in GDrive
    profile["gdrive_files"] = search_gdrive_library(profile.get("scale_persian_name") or profile["scale_name"], gdrive_dir)
    
    return profile

def score_dataset(
    data_path: str,
    scale_name_or_query: str,
    item_col_prefix: Optional[str] = None,
    output_path: Optional[str] = None,
    excel_path: Optional[str] = None,
    gdrive_dir: Optional[str] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Score raw survey dataset according to questionnaire rules:
    1. Reverses specified reverse items: Item_rev = (min_item + max_item) - Item.
    2. Calculates subscale sum and mean scores.
    3. Calculates total composite score.
    4. Computes internal consistency (Cronbach's alpha) for each subscale and total scale.
    5. Saves enriched dataset to Excel/CSV.
    """
    profile = get_scale_profile(scale_name_or_query, excel_path, gdrive_dir)
    if not profile or not profile.get("found_in_registry"):
        raise ValueError(f"Could not find scoring specifications for scale '{scale_name_or_query}' in registry.")
        
    ext = os.path.splitext(data_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(data_path)
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(data_path)
    elif ext == '.sav':
        import pyreadstat
        df, _ = pyreadstat.read_sav(data_path)
    else:
        raise ValueError(f"Unsupported dataset format '{ext}'.")
        
    scored_df = df.copy()
    reverse_items = set(profile.get("all_reverse_items", []))
    min_item = profile.get("item_min_score", 1) or 1
    max_item = profile.get("item_max_score", 5) or 5
    
    # Map item number to actual DataFrame column
    def find_item_column(item_num: int) -> Optional[str]:
        if item_col_prefix:
            col_cand = f"{item_col_prefix}{item_num}"
            if col_cand in df.columns:
                return col_cand
            col_cand_under = f"{item_col_prefix}_{item_num}"
            if col_cand_under in df.columns:
                return col_cand_under
                
        patterns = [
            f"Q{item_num}", f"q{item_num}", f"Item{item_num}", f"item{item_num}",
            f"Q_{item_num}", f"q_{item_num}", f"Item_{item_num}", f"item_{item_num}",
            str(item_num)
        ]
        for p in patterns:
            if p in df.columns:
                return p
        return None

    # Step 1: Apply Reverse Scoring
    reversed_cols = []
    for item_num in profile.get("all_items", []):
        col = find_item_column(item_num)
        if not col:
            continue
        if item_num in reverse_items:
            rev_col = f"{col}_rev"
            scored_df[rev_col] = (min_item + max_item) - pd.to_numeric(scored_df[col], errors='coerce')
            reversed_cols.append({
                "item": item_num,
                "original_col": col,
                "reversed_col": rev_col,
                "formula": f"({min_item} + {max_item}) - {col}"
            })
            
    def get_effective_col(item_num: int) -> Optional[str]:
        col = find_item_column(item_num)
        if not col:
            return None
        if item_num in reverse_items:
            return f"{col}_rev"
        return col

    # Step 2: Compute Subscales
    subscale_summaries = []
    for sub in profile.get("subscales", []):
        sub_name = sub["subscale_name"]
        items = sub["items_parsed"]
        if not items:
            continue
            
        sub_cols = [get_effective_col(i) for i in items if get_effective_col(i) is not None]
        if not sub_cols:
            continue
            
        clean_sub_name = re.sub(r"[^\w\s-]", "", sub_name).strip().replace(" ", "_")
        sum_col = f"Sub_{clean_sub_name}_Sum"
        mean_col = f"Sub_{clean_sub_name}_Mean"
        
        sub_data = scored_df[sub_cols].apply(pd.to_numeric, errors='coerce')
        scored_df[sum_col] = sub_data.sum(axis=1)
        scored_df[mean_col] = sub_data.mean(axis=1)
        
        # Cronbach's Alpha
        k = len(sub_cols)
        if k >= 2 and len(sub_data.dropna()) >= 3:
            item_vars = sub_data.var(axis=0, ddof=1).sum()
            total_var = scored_df[sum_col].var(ddof=1)
            alpha = (k / (k - 1)) * (1 - (item_vars / total_var)) if total_var > 0 else 0.0
        else:
            alpha = None
            
        subscale_summaries.append({
            "subscale_name": sub_name,
            "items_count": len(items),
            "columns_used": sub_cols,
            "sum_column": sum_col,
            "mean_column": mean_col,
            "mean": round(float(scored_df[sum_col].mean()), 2),
            "sd": round(float(scored_df[sum_col].std(ddof=1)), 2),
            "cronbach_alpha": round(float(alpha), 3) if alpha is not None else None
        })

    # Step 3: Compute Total Composite Score
    all_scale_cols = [get_effective_col(i) for i in profile.get("all_items", []) if get_effective_col(i) is not None]
    clean_scale_name = re.sub(r"[^\w\s-]", "", profile["scale_name"]).strip().replace(" ", "_")
    total_sum_col = f"{clean_scale_name}_Total_Sum"
    total_mean_col = f"{clean_scale_name}_Total_Mean"
    
    if all_scale_cols:
        all_data = scored_df[all_scale_cols].apply(pd.to_numeric, errors='coerce')
        scored_df[total_sum_col] = all_data.sum(axis=1)
        scored_df[total_mean_col] = all_data.mean(axis=1)
        
        k_tot = len(all_scale_cols)
        if k_tot >= 2 and len(all_data.dropna()) >= 3:
            item_vars = all_data.var(axis=0, ddof=1).sum()
            total_var = scored_df[total_sum_col].var(ddof=1)
            total_alpha = (k_tot / (k_tot - 1)) * (1 - (item_vars / total_var)) if total_var > 0 else 0.0
        else:
            total_alpha = None
    else:
        total_alpha = None

    summary = {
        "scale_name": profile["scale_name"],
        "scale_persian_name": profile.get("scale_persian_name", ""),
        "total_items_indexed": len(profile.get("all_items", [])),
        "total_items_scored": len(all_scale_cols),
        "reverse_items_reversed": reversed_cols,
        "scoring_range": f"{min_item} to {max_item}",
        "subscales": subscale_summaries,
        "total_composite": {
            "sum_column": total_sum_col,
            "mean_column": total_mean_col,
            "mean": round(float(scored_df[total_sum_col].mean()), 2) if all_scale_cols else None,
            "sd": round(float(scored_df[total_sum_col].std(ddof=1)), 2) if all_scale_cols else None,
            "cronbach_alpha": round(float(total_alpha), 3) if total_alpha is not None else None
        }
    }

    if output_path:
        out_ext = os.path.splitext(output_path)[1].lower()
        if out_ext == '.csv':
            scored_df.to_csv(output_path, index=False)
        else:
            scored_df.to_excel(output_path, index=False)
        print(f"Scored dataset saved to: {output_path}")
        
    return scored_df, summary

def main():
    parser = argparse.ArgumentParser(description="Psychometric Questionnaire Resolver & Factor Scoring Engine")
    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")
    
    # 1. Search command
    p_search = subparsers.add_parser("search", help="Search questionnaires in registry and Google Drive library")
    p_search.add_argument("query", help="Scale name, Persian title, subscale, or abbreviation")
    p_search.add_argument("--excel", help="Path to Questionnaires.xlsx")
    p_search.add_argument("--gdrive", help="Path to Google Drive questionnaire directory")
    p_search.add_argument("--json", action="store_true", help="Output results as JSON")
    
    # 2. Profile command
    p_profile = subparsers.add_parser("profile", help="Show complete scoring profile, subscales, and reverse keys")
    p_profile.add_argument("scale", help="Scale name or abbreviation")
    p_profile.add_argument("--excel", help="Path to Questionnaires.xlsx")
    p_profile.add_argument("--gdrive", help="Path to Google Drive questionnaire directory")
    p_profile.add_argument("--json", action="store_true", help="Output profile as JSON")

    # 3. Score command
    p_score = subparsers.add_parser("score", help="Score raw dataset by reversing items and computing factors")
    p_score.add_argument("--data", required=True, help="Path to raw dataset (.xlsx, .csv, .sav)")
    p_score.add_argument("--scale", required=True, help="Scale name in registry (e.g. 'Connor-Davidson Resilience Scale')")
    p_score.add_argument("--prefix", default="Q", help="Item column prefix (e.g., 'Q' for Q1..Q25 or 'R' for R1..R25)")
    p_score.add_argument("--out", default="scored_dataset.xlsx", help="Output path for scored dataset")
    p_score.add_argument("--summary", default="scoring_summary.json", help="Path for JSON scoring report")
    p_score.add_argument("--excel", help="Path to Questionnaires.xlsx")
    p_score.add_argument("--gdrive", help="Path to Google Drive questionnaire directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        registry_matches = search_registry(args.query, args.excel)
        gdrive_matches = search_gdrive_library(args.query, args.gdrive)
        if args.json:
            print(json.dumps({
                "query": args.query,
                "registry_matches_count": len(registry_matches),
                "registry_matches": registry_matches,
                "gdrive_matches_count": len(gdrive_matches),
                "gdrive_matches": gdrive_matches
            }, ensure_ascii=False, indent=2))
        else:
            print(f"=== Questionnaire Search Results for: '{args.query}' ===")
            print(f"Found {len(registry_matches)} scale(s) in Questionnaires.xlsx:")
            for idx, m in enumerate(registry_matches, 1):
                print(f"{idx}. {m['scale_name']} ({m.get('scale_persian_name', '')})")
                print(f"   Abbreviation: {m.get('abbreviation', 'N/A')} | Scoring: {m.get('scoring_method', 'N/A')}")
                print(f"   Subscales ({len(m['subscales'])}): {', '.join([s['subscale_name'] for s in m['subscales']])}")
            
            print(f"\nFound {len(gdrive_matches)} file(s) in Google Drive Library:")
            for idx, gf in enumerate(gdrive_matches[:10], 1):
                print(f"{idx}. {os.path.basename(gf)}")
            if len(gdrive_matches) > 10:
                print(f"   ... and {len(gdrive_matches) - 10} more files.")

    elif args.command == "profile":
        profile = get_scale_profile(args.scale, args.excel, args.gdrive)
        if not profile:
            print(f"Scale '{args.scale}' not found.")
            sys.exit(1)
        if args.json:
            print(json.dumps(profile, ensure_ascii=False, indent=2))
        else:
            print(f"=== Psychometric Profile: {profile.get('scale_name')} ===")
            print(f"Persian Name: {profile.get('scale_persian_name', 'N/A')}")
            print(f"Abbreviation: {profile.get('abbreviation', 'N/A')}")
            print(f"Scoring Method: {profile.get('scoring_method', 'N/A')} (Item Range: {profile.get('item_min_score')} to {profile.get('item_max_score')})")
            print(f"Total Items: {profile.get('total_items_count')} (Items: {profile.get('all_items')})")
            print(f"Reverse Scored Items: {profile.get('all_reverse_items') or 'None'}")
            print(f"\nSubscales ({len(profile.get('subscales', []))}):")
            for idx, sub in enumerate(profile.get("subscales", []), 1):
                print(f"  {idx}. {sub['subscale_name']}")
                print(f"     Items: {sub['items_parsed']} (Raw: {sub['items_raw']})")
                print(f"     Min: {sub.get('min_score')} | Max: {sub.get('max_score')} | Theoretical Mean: {sub.get('theoretical_mean')}")
                if sub['reverse_items_parsed']:
                    print(f"     Reverse items in subscale: {sub['reverse_items_parsed']}")
            if profile.get("gdrive_files"):
                print(f"\nMatching Library Documents ({len(profile['gdrive_files'])}):")
                for gf in profile['gdrive_files'][:5]:
                    print(f"  - {os.path.basename(gf)}")

    elif args.command == "score":
        scored_df, summary = score_dataset(
            data_path=args.data,
            scale_name_or_query=args.scale,
            item_col_prefix=args.prefix,
            output_path=args.out,
            excel_path=args.excel,
            gdrive_dir=args.gdrive
        )
        if args.summary:
            with open(args.summary, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"Scoring summary written to: {args.summary}")
            
        print(f"\nSuccessfully scored '{args.scale}':")
        print(f"- Items processed: {summary['total_items_scored']}")
        print(f"- Reversed items: {len(summary['reverse_items_reversed'])}")
        print(f"- Subscales created: {len(summary['subscales'])}")
        for sub in summary['subscales']:
            print(f"  * {sub['subscale_name']}: Mean={sub['mean']}, SD={sub['sd']}, Alpha={sub['cronbach_alpha']}")
        tot = summary['total_composite']
        print(f"- Total Composite: Mean={tot['mean']}, SD={tot['sd']}, Alpha={tot['cronbach_alpha']}")

if __name__ == "__main__":
    main()
