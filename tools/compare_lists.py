"""
Compare Two Lists and Remove Matches
=======================================
Ported from ``vlookup.gs`` and ``Compare.gs``.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
from utils.io_helpers import generate_summary


def compare_and_remove(
    source_df: pd.DataFrame,
    lookup_df: pd.DataFrame,
    source_col: str,
    lookup_col: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Remove rows from *source_df* whose *source_col* value appears
    in *lookup_df*[*lookup_col*].

    Returns ``(cleaned_df, removed_df, summary)``.
    """
    lookup_set = set(
        lookup_df[lookup_col]
        .fillna("").astype(str).str.strip().str.lower()
        .loc[lambda s: s != ""]
    )

    norm = source_df[source_col].fillna("").astype(str).str.strip().str.lower()
    mask = norm.isin(lookup_set)

    removed = source_df[mask].copy()
    cleaned = source_df[~mask].reset_index(drop=True)

    summary = generate_summary(
        tool_name="Compare & Remove",
        before_count=len(source_df),
        after_count=len(cleaned),
        removed_count=len(removed),
        extra_info={
            "Source column": source_col,
            "Lookup column": lookup_col,
            "Lookup values": f"{len(lookup_set):,}",
        },
    )
    return cleaned, removed, summary
