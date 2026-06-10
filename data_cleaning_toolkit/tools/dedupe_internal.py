"""Internal fuzzy deduplication within a single file."""
import pandas as pd
from utils.matching import find_fuzzy_duplicates
from utils.io_helpers import generate_summary

def dedupe_within_file(df, column, threshold=90):
    values = df[column].fillna("").astype(str).str.strip().tolist()
    matches = find_fuzzy_duplicates(values, threshold)
    statuses = [""] * len(df)
    matched_vals = [""] * len(df)
    match_pcts = [""] * len(df)
    first_indices = [""] * len(df)
    for idx, status, matched_val, pct, first_idx in matches:
        if idx < len(df):
            statuses[idx] = status
            matched_vals[idx] = matched_val
            match_pcts[idx] = str(pct) if pct > 0 else ""
            first_indices[idx] = str(first_idx) if status == "Duplicate" else ""
    result = df.copy()
    result["Dedup Status"] = statuses
    result["Matched With"] = matched_vals
    result["Match %"] = match_pcts
    result["First Occurrence Row"] = first_indices
    dup_count = sum(1 for s in statuses if s == "Duplicate")
    unique_count = sum(1 for s in statuses if s == "Unique")
    summary = generate_summary("Fuzzy Duplicate Finder", len(df), len(df),
        extra_info={"Duplicates found": f"{dup_count:,}", "Unique values": f"{unique_count:,}",
                    "Threshold": f"{threshold}%", "Column checked": column})
    return result, summary
