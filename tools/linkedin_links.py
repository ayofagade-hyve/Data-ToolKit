"""
Generate LinkedIn Search Links
=================================
"""

from __future__ import annotations
import pandas as pd
from utils.linkedin_tools import generate_linkedin_search_url


def add_linkedin_links(
    df: pd.DataFrame,
    name_col: str,
    title_col: str | None = None,
    company_col: str | None = None,
) -> pd.DataFrame:
    """Add a ``LinkedIn Search URL`` column."""
    result = df.copy()
    names = result[name_col].fillna("").astype(str)
    titles = result[title_col].fillna("").astype(str) if title_col else [""] * len(df)
    companies = result[company_col].fillna("").astype(str) if company_col else [""] * len(df)

    result["LinkedIn Search URL"] = [
        generate_linkedin_search_url(n, t, c)
        for n, t, c in zip(names, titles, companies)
    ]
    return result
