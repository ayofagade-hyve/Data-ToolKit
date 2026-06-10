"""Combine multiple CSV files into one."""
import pandas as pd
from utils.io_helpers import generate_summary

def combine_csvs(dfs):
    if not dfs:
        return pd.DataFrame(), generate_summary("Combine CSVs", 0, 0)
    combined = pd.concat(dfs, ignore_index=True, sort=False).fillna("")
    total_input = sum(len(d) for d in dfs)
    summary = generate_summary("Combine CSVs", total_input, len(combined),
        extra_info={"Files combined": str(len(dfs)), "Total columns": str(len(combined.columns))})
    return combined, summary
