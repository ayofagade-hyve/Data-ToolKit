"""
Internal (Within-File) Fuzzy Deduplication
============================================
Find and flag fuzzy duplicates within a single CSV column.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
from utils.matching import find_fuzzy_duplicates
from utils.io_helpers import generate_summary


def dedupe_within_file(
    df: pd.DataFrame,
    column: str,
    threshold: int = 90,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Flag fuzzy duplicates in *column*.

    Adds columns: ``Duplicate Status``, ``Matched With``,
    ``Match %``, ``First Occurrence Row``.

    Returns ``(result_df, summary)``.
    """
    values = df[column].fillna("").astype(str).tolist()
    results = find_fuzzy_duplicates(values, threshold=threshold)

    statuses, match_names, match_pcts, first_rows = [], [], [], []
    dup_count = 0
    for idx, status, match_name, pct, first_idx in results:
        statuses.append(status)
        match_names.append(match_name)
        match_pcts.append(pct if pct else "")
        first_rows.append(first_idx + 2 if first_idx >= 0 else "")  # 1-indexed + header
        if status == "Duplicate":
            dup_count += 1

    result = df.copy()
    result["Duplicate Status"] = statuses
    result["Matched With"] = match_names
    result["Match %"] = match_pcts
    result["First Occurrence Row"] = first_rows

    summary = generate_summary(
        tool_name="Internal Fuzzy Deduplicate",
        before_count=len(df),
        after_count=len(df),
        removed_count=dup_count,
        extra_info={
            "Column checked": column,
            "Threshold": f"{threshold}%",
            "Duplicates found": f"{dup_count:,}",
            "Unique rows": f"{len(df) - dup_count:,}",
        },
    )
    return result, summary
