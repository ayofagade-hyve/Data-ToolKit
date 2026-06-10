"""Compare and remove rows found in a second list."""
import pandas as pd
from utils.io_helpers import generate_summary

def compare_and_remove(main_df, compare_df, main_col, compare_col):
    main_values = main_df[main_col].fillna("").astype(str).str.lower().str.strip()
    compare_values = set(compare_df[compare_col].fillna("").astype(str).str.lower().str.strip())
    mask = main_values.isin(compare_values)
    removed_df = main_df[mask].copy()
    cleaned_df = main_df[~mask].copy()
    summary = generate_summary("Compare & Remove", len(main_df), len(cleaned_df),
        removed_count=len(removed_df),
        extra_info={"Matched on": f"{main_col} vs {compare_col}", "Suppression list size": f"{len(compare_df):,}"})
    return cleaned_df, removed_df, summary
