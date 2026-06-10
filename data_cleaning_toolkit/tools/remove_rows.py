"""Row removal tools: blank rows, keywords, and flags."""
import pandas as pd
from utils.io_helpers import generate_summary

def remove_blank_rows(df):
    mask = df.apply(lambda row: all(str(v).strip() == "" for v in row), axis=1)
    result = df[~mask].copy()
    summary = generate_summary("Remove Blank Rows", len(df), len(result), removed_count=int(mask.sum()))
    return result, summary

def remove_by_keywords(df, column, keywords):
    series = df[column].fillna("").astype(str).str.lower()
    keywords_lower = [str(k).lower().strip() for k in keywords if str(k).strip()]
    mask = pd.Series([False] * len(df), index=df.index)
    for kw in keywords_lower:
        mask = mask | series.str.contains(kw, regex=False, na=False)
    removed = df[mask].copy(); cleaned = df[~mask].copy()
    summary = generate_summary("Remove by Keywords", len(df), len(cleaned), removed_count=len(removed),
        extra_info={"Keywords": ", ".join(keywords_lower), "Column": column})
    return cleaned, removed, summary

def remove_by_flag(df, column, flag_value):
    series = df[column].fillna("").astype(str).str.lower().str.strip()
    mask = series == str(flag_value).lower().strip()
    removed = df[mask].copy(); cleaned = df[~mask].copy()
    summary = generate_summary("Remove by Flag", len(df), len(cleaned), removed_count=len(removed),
        extra_info={"Flag value": flag_value, "Column": column})
    return cleaned, removed, summary
