"""
Extract Domains from Emails
=============================
Determine the most common company domain from email addresses.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
from utils.domain_tools import extract_domains_for_companies
from utils.io_helpers import generate_summary


def extract_domains(
    df: pd.DataFrame,
    email_col: str,
    company_col: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Extract domains and return (result_df, missing_companies_df, summary)."""
    result, missing = extract_domains_for_companies(df, email_col, company_col)

    domain_found = result["Domain"].notna() & (result["Domain"] != "")
    summary = generate_summary(
        tool_name="Extract Domains",
        before_count=len(df),
        after_count=len(result),
        extra_info={
            "Rows with domain": f"{domain_found.sum():,}",
            "Companies missing domain": f"{len(missing):,}",
        },
    )
    return result, missing, summary
