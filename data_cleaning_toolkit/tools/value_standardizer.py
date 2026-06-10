"""Rule-based value standardisation with 4 matching strategies."""
import pandas as pd
from utils.matching import similarity_pct
from utils.io_helpers import generate_summary

def build_lookup(standards_df, standard_col, aliases_col=None):
    lookup = {}
    for _, row in standards_df.iterrows():
        standard = str(row[standard_col]).strip()
        if not standard: continue
        lookup[standard.lower()] = standard
        if aliases_col and aliases_col in standards_df.columns:
            aliases_str = str(row.get(aliases_col, "")).strip()
            if aliases_str and aliases_str.lower() != "nan":
                for alias in aliases_str.split(";"):
                    alias = alias.strip()
                    if alias:
                        lookup[alias.lower()] = standard
    return lookup

def standardize_values(df, col, standards_df, standard_col, aliases_col=None, threshold=80):
    lookup = build_lookup(standards_df, standard_col, aliases_col)
    all_standards = list(set(lookup.values()))
    result = df.copy()
    standardised_col = f"{col} (standardised)"
    result[standardised_col] = ""
    report_rows = []
    for i, row in result.iterrows():
        raw = str(row[col]).strip()
        if not raw:
            result.at[i, standardised_col] = ""; continue
        raw_lower = raw.lower()
        matched, confidence, method = None, 0, ""
        # Strategy 1: Exact
        if raw_lower in lookup:
            matched = lookup[raw_lower]; confidence = 100; method = "Exact"
        # Strategy 2: Keyword (alias inside raw)
        if not matched:
            for alias, standard in lookup.items():
                if alias in raw_lower and len(alias) >= 3:
                    matched = standard; confidence = 90; method = "Keyword"; break
        # Strategy 3: Substring (raw inside alias, min 3 chars)
        if not matched and len(raw_lower) >= 3:
            for alias, standard in lookup.items():
                if raw_lower in alias:
                    matched = standard; confidence = 85; method = "Substring"; break
        # Strategy 4: Fuzzy
        if not matched:
            best_pct, best_std = 0, None
            for alias, standard in lookup.items():
                pct = similarity_pct(raw_lower, alias)
                if pct > best_pct:
                    best_pct = pct; best_std = standard
            if best_pct >= threshold:
                matched = best_std; confidence = best_pct; method = "Fuzzy"
        result.at[i, standardised_col] = matched if matched else raw
        report_rows.append({"Original Value": raw, "Standardised Value": matched or raw,
            "Confidence %": confidence, "Method": method or "No match",
            "Changed": "Yes" if matched and matched != raw else "No"})
    report_df = pd.DataFrame(report_rows)
    changed = sum(1 for r in report_rows if r["Changed"] == "Yes")
    summary = generate_summary("Value Standardiser", len(df), len(result),
        extra_info={"Column": col, "Values standardised": f"{changed:,}",
                    "Standards count": str(len(all_standards)), "Threshold": f"{threshold}%"})
    return result, report_df, summary
