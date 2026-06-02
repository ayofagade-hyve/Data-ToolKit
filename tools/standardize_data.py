"""
Standardise Names, Phones, Websites, LinkedIn URLs
=====================================================
"""

from __future__ import annotations
import re
import pandas as pd
from utils.name_tools import split_name
from utils.domain_tools import normalize_domain
from utils.linkedin_tools import normalize_linkedin_url


def standardize_names(df: pd.DataFrame, full_name_col: str) -> pd.DataFrame:
    """Split a full-name column into First Name and Last Name."""
    result = df.copy()
    splits = result[full_name_col].apply(
        lambda v: split_name(v) if isinstance(v, str) else ("", "")
    )
    result["First Name"] = splits.apply(lambda x: x[0])
    result["Last Name"] = splits.apply(lambda x: x[1])
    return result


def standardize_phones(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Strip non-digit characters from phone numbers (keep leading +)."""
    result = df.copy()
    result[col] = result[col].fillna("").astype(str).apply(
        lambda v: re.sub(r"[^+\d]", "", v.strip())
    )
    return result


def standardize_websites(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Normalise website/domain values."""
    result = df.copy()
    result[col] = result[col].fillna("").astype(str).apply(normalize_domain)
    return result


def standardize_linkedin(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Normalise LinkedIn URLs."""
    result = df.copy()
    result[col] = result[col].fillna("").astype(str).apply(normalize_linkedin_url)
    return result
