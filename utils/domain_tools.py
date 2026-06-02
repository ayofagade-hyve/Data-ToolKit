"""
Domain Extraction & Normalisation
==================================
Merged from ``Extract Domain.gs`` and the Python ``Domain Extractor``
Colab script.
"""

from __future__ import annotations
import re
from typing import Optional
import pandas as pd

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "protonmail.com", "live.com",
    "mail.com", "yandex.com", "zoho.com", "gmx.com",
    "me.com", "msn.com", "yahoo.co.uk", "yahoo.fr",
    "hotmail.co.uk", "hotmail.fr", "googlemail.com",
}


def normalize_domain(domain: str) -> str:
    """Strip protocol, www prefix, and trailing slash."""
    d = str(domain or "").strip().lower()
    d = re.sub(r"^https?://", "", d)
    d = re.sub(r"^www\.", "", d)
    return d.rstrip("/")


def is_personal_domain(domain: str) -> bool:
    """Return True if the domain is a well-known personal email provider."""
    return normalize_domain(domain) in PERSONAL_DOMAINS


def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract the domain part from an email address."""
    email = str(email or "").strip().lower()
    if "@" not in email:
        return None
    domain = email.split("@")[-1].strip()
    if not domain or is_personal_domain(domain):
        return None
    return normalize_domain(domain)


def extract_domains_for_companies(
    df: pd.DataFrame,
    email_col: str,
    company_col: str,
) -> tuple:
    """Extract the most common domain per company.

    Returns ``(result_df, missing_companies_df)``.
    """
    work = df.copy()
    work["_email_clean"] = work[email_col].fillna("").str.lower().str.strip()
    work["_company_clean"] = work[company_col].fillna("").str.strip()
    work["_domain"] = work["_email_clean"].apply(
        lambda e: extract_domain_from_email(e) or ""
    )

    # Count domains per company, pick the most common
    domain_counts = (
        work[work["_domain"] != ""]
        .groupby("_company_clean")["_domain"]
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
        .rename(columns={"_domain": "Domain"})
    )

    # Merge back
    result = (
        work.drop(columns=["_email_clean", "_domain"])
        .merge(domain_counts, on="_company_clean", how="left")
        .drop(columns=["_company_clean"])
    )

    # Companies with no domain found
    missing = result[result["Domain"].isna() | (result["Domain"] == "")]
    missing_companies = (
        missing[[company_col]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return result, missing_companies
