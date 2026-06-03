import pandas as pd
from utils.matching import similarity_pct
from utils.io_helpers import generate_summary

def build_lookup(standards_df, standard_col, aliases_col=None):
    lookup = []
    for _, row in standards_df.iterrows():
        std = str(row[standard_col]).strip()
        if not std or std.lower()=="nan": continue
        aliases = []
        if aliases_col and aliases_col in standards_df.columns:
            raw = str(row.get(aliases_col, "")).strip()
            if raw and raw.lower() != "nan":
                aliases = [a.strip() for a in raw.split(",") if a.strip()]
        all_lower = [std.lower()] + [a.lower() for a in aliases]
        lookup.append({"standard": std, "all_lower": all_lower})
    return lookup

def _match_value(raw, lookup, threshold):
    if not raw or not raw.strip(): return ("", "empty", 0)
    val_lower = raw.strip().lower()
    # 1: Exact
    for entry in lookup:
        if val_lower in entry["all_lower"]:
            return (entry["standard"], "exact", 100)
    # 2: Keyword — standard/alias is substr of raw value
    for entry in lookup:
        for term in entry["all_lower"]:
            if len(term) >= 3 and term in val_lower:
                return (entry["standard"], "keyword", 90)
    # 3: Raw is substr of standard/alias
    if len(val_lower) >= 3:
        for entry in lookup:
            for term in entry["all_lower"]:
                if val_lower in term:
                    return (entry["standard"], "keyword", 85)
    # 4: Fuzzy
    best_std, best_pct = "", 0
    for entry in lookup:
        for term in entry["all_lower"]:
            pct = similarity_pct(val_lower, term)
            if pct > best_pct: best_pct = pct; best_std = entry["standard"]
    if best_pct >= threshold:
        return (best_std, "fuzzy", best_pct)
    return ("", "no match", best_pct)

def standardize_values(df, col, standards_df, standard_col, aliases_col=None, threshold=80):
    lookup = build_lookup(standards_df, standard_col, aliases_col)
    result = df.copy(); raw_values = result[col].fillna("").astype(str)
    cache = {}; stds, methods, confs = [], [], []
    for v in raw_values:
        vl = v.strip().lower()
        if vl not in cache: cache[vl] = _match_value(v, lookup, threshold)
        std, method, conf = cache[vl]
        stds.append(std if std else v); methods.append(method); confs.append(conf)
    result[f"{col} (standardised)"] = stds
    result["Match Method"] = methods; result["Match Confidence %"] = confs
    report_rows = []
    for vl, (std, method, conf) in sorted(cache.items()):
        if not vl: continue
        cnt = sum(1 for v in raw_values if v.strip().lower() == vl)
        report_rows.append({"Raw Value": vl, "Standardised To": std if std else "(kept)", "Method": method, "Confidence %": conf, "Occurrences": cnt})
    report_df = pd.DataFrame(report_rows)
    matched = sum(1 for m in methods if m not in ("no match","empty"))
    unmatched = sum(1 for m in methods if m == "no match")
    summary = generate_summary("Value Standardiser", len(df), len(result),
        extra_info={"Matched": f"{matched:,}", "Unmatched": f"{unmatched:,}",
                    "Unique values": f"{len(cache):,}", "Standards": f"{len(lookup):,}", "Threshold": f"{threshold}%"})
    return result, report_df, summary
