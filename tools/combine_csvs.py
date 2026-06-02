"""
Combine Multiple CSV Files
============================
Concatenate several uploaded CSVs into one file.
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Any
import pandas as pd
from utils.io_helpers import load_csv, generate_summary


def combine_csvs(uploaded_files: list) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Combine a list of uploaded file objects into one DataFrame.

    Returns ``(combined_df, summary_dict)``.
    """
    dfs = []
    file_info = {}
    for uf in uploaded_files:
        df = load_csv(uf)
        dfs.append(df)
        file_info[uf.name] = f"{len(df):,} rows"

    combined = pd.concat(dfs, ignore_index=True)

    summary = generate_summary(
        tool_name="Combine CSVs",
        before_count=sum(len(d) for d in dfs),
        after_count=len(combined),
        extra_info={"Files combined": file_info},
    )
    return combined, summary
