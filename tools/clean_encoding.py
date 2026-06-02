"""
Clean Encoding / Fix Mojibake
==============================
Apply text-encoding fixes across an entire CSV.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
from utils.text_cleaning import fix_mojibake_dataframe
from utils.io_helpers import generate_summary


def clean_encoding(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Fix mojibake in every string column.

    Returns ``(cleaned_df, summary)``.
    """
    before = df.copy()
    cleaned = fix_mojibake_dataframe(df)

    # Count how many cells actually changed
    changed_cells = 0
    for col in before.select_dtypes(include=["object"]).columns:
        changed_cells += (before[col].fillna("") != cleaned[col].fillna("")).sum()

    summary = generate_summary(
        tool_name="Clean Encoding (Mojibake Fix)",
        before_count=len(df),
        after_count=len(cleaned),
        extra_info={"Cells fixed": f"{changed_cells:,}"},
    )
    return cleaned, summary
