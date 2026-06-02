"""
I/O Helpers
============
CSV loading with encoding detection, export helpers, and
summary-report generation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import io
import pandas as pd


def load_csv(uploaded_file, **kwargs) -> pd.DataFrame:
    """Load a CSV with automatic encoding fallback.

    Tries UTF-8 first, then ``latin-1`` as a safe fallback.
    """
    try:
        return pd.read_csv(uploaded_file, dtype=str, **kwargs)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, dtype=str, encoding="latin-1", **kwargs)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Export a DataFrame as UTF-8 BOM CSV bytes (safe for Excel)."""
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()


def generate_summary(
    tool_name: str,
    before_count: int,
    after_count: int,
    removed_count: int = 0,
    extra_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a summary dict displayed after every tool run."""
    summary = {
        "Tool": tool_name,
        "Rows before": f"{before_count:,}",
        "Rows after": f"{after_count:,}",
        "Rows removed / changed": f"{removed_count:,}",
    }
    if extra_info:
        summary.update(extra_info)
    return summary
