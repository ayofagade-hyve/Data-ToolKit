"""
Column Mapping & Auto-Detection
================================
Automatically detect columns by matching against a list of known
aliases.  Ported from the Python ``CSV Deduplicater`` and extended
with aliases from the Apps Script ``consolidate.gs``.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import pandas as pd

# Canonical field name → list of known aliases (case-insensitive)
COLUMN_ALIASES: Dict[str, List[str]] = {
    "email": [
        "email", "e-mail", "work email", "business email",
        "personal email", "cognism email", "email input",
    ],
    "first_name": [
        "first name", "firstname", "first_name", "first name input",
    ],
    "last_name": [
        "last name", "lastname", "last_name", "last name input",
    ],
    "full_name": [
        "name", "full name", "full_name", "contact name",
    ],
    "company": [
        "company", "company name", "organization", "organisation",
        "account", "matched company", "company name input", "brand",
    ],
    "website": [
        "website", "domain", "company domain", "company website",
        "matched website", "website input", "company url",
    ],
    "linkedin": [
        "linkedin", "linkedin url", "personal linkedin url",
        "profileurl", "profile url", "linkedin input",
    ],
    "job_title": [
        "job title", "title", "matched job title",
        "job title input", "position",
    ],
    "phone": [
        "phone", "mobile", "mobile phone number", "direct",
        "office", "phone 1", "phone number",
    ],
    "country": [
        "country", "country/region", "person country",
        "company country", "country input", "location",
    ],
    "seniority": [
        "seniority", "seniority (ftmu)", "job title level",
        "ftmu_job title level",
    ],
    "job_function": [
        "job function", "department", "ftmu_job function",
    ],
    "org_type": [
        "organization type", "organisation type",
        "ftmu_organization type",
    ],
    "industries": [
        "industries", "industry",
    ],
    "company_type": [
        "company type",
    ],
    "company_tech": [
        "company tech",
    ],
}


def find_column(df: pd.DataFrame, field: str) -> Optional[str]:
    """Return the actual column name in *df* that matches *field*
    aliases, or ``None`` if not found.
    """
    aliases = COLUMN_ALIASES.get(field, [field])
    col_map = {c.strip().lower(): c for c in df.columns}
    for alias in aliases:
        actual = col_map.get(alias.strip().lower())
        if actual is not None:
            return actual
    return None


def get_series(df: pd.DataFrame, field: str) -> pd.Series:
    """Return the column matching *field* as a Series.
    Falls back to an empty-string Series if the column is missing.
    """
    col = find_column(df, field)
    if col is not None:
        return df[col].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index, dtype=str)


def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """Return a mapping of canonical field → actual column name (or None)."""
    return {field: find_column(df, field) for field in COLUMN_ALIASES}
