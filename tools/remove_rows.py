"""
Row Removal Tools
==================
Remove blank rows, rows matching keywords, or rows with specific flags.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any, List
import pandas as pd
from utils.io_helpers import generate_summary


def remove_blank_rows(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Remove rows where all cells are empty."""
    before = len(df)
    cleaned = df.dropna(how="all")
    # Also remove rows where every cell is just whitespace
    mask = cleaned.apply(
        lambda row: all(
            str(v).strip() == "" or pd.isna(v) for v in row
        ),
        axis=1,
    )
    cleaned = cleaned[~mask].reset_index(drop=True)
    removed = before - len(cleaned)
    summary = generate_summary(
        tool_name="Remove Blank Rows",
        before_count=before,
        after_count=len(cleaned),
        removed_count=removed,
    )
    return cleaned, summary


def remove_by_keywords(
    df: pd.DataFrame,
    column: str,
    keywords: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Remove rows where *column* contains any of the *keywords*.

    Returns ``(cleaned_df, removed_df, summary)``.
    """
    mask = df[column].fillna("").astype(str).apply(
        lambda v: any(kw.lower() in v.lower() for kw in keywords)
    )
    removed = df[mask].copy()
    cleaned = df[~mask].reset_index(drop=True)

    summary = generate_summary(
        tool_name="Remove by Keywords",
        before_count=len(df),
        after_count=len(cleaned),
        removed_count=len(removed),
        extra_info={"Keywords": ", ".join(keywords), "Column": column},
    )
    return cleaned, removed, summary


def remove_by_flag(
    df: pd.DataFrame,
    column: str,
    flag_value: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Remove rows where *column* equals *flag_value* (case-insensitive).

    Returns ``(cleaned_df, removed_df, summary)``.
    """
    mask = (
        df[column].fillna("").astype(str).str.strip().str.lower()
        == flag_value.strip().lower()
    )
    removed = df[mask].copy()
    cleaned = df[~mask].reset_index(drop=True)

    summary = generate_summary(
        tool_name="Remove by Flag",
        before_count=len(df),
        after_count=len(cleaned),
        removed_count=len(removed),
        extra_info={"Column": column, "Flag value": flag_value},
    )
    return cleaned, removed, summary
