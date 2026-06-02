"""
Deduplicate Against a Master List
===================================
Remove rows from a check-file that already appear in a master file.
Matches on email, LinkedIn URL, name+company, and name+website/domain.
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import re
import pandas as pd
from utils.column_mapping import get_series
from utils.io_helpers import generate_summary


def _clean(val):
    return str(val).strip().lower() if pd.notna(val) else ""


def _norm_domain(val):
    v = _clean(val)
    v = re.sub(r"^https?://", "", v)
    v = re.sub(r"^www\.", "", v)
    return v.rstrip("/")


def _norm_linkedin(val):
    v = _clean(val)
    v = v.replace("https://", "").replace("http://", "").replace("www.", "")
    return v.rstrip("/")


def _prepare(df):
    """Add hidden match-key columns."""
    out = df.copy()
    out["_email"] = get_series(df, "email").apply(_clean)
    out["_first"] = get_series(df, "first_name").apply(_clean)
    out["_last"] = get_series(df, "last_name").apply(_clean)

    full = get_series(df, "full_name").apply(_clean)
    needs_split = (out["_last"] == "") & full.str.contains(" ", na=False)
    split = full[needs_split].str.split(" ", n=1, expand=True)
    if not split.empty:
        out.loc[needs_split, "_first"] = split[0]
        if split.shape[1] > 1:
            out.loc[needs_split, "_last"] = split[1]

    out["_company"] = get_series(df, "company").apply(_clean)
    out["_website"] = get_series(df, "website").apply(_norm_domain)
    out["_linkedin"] = get_series(df, "linkedin").apply(_norm_linkedin)
    out["_name_company"] = out["_first"] + "|" + out["_last"] + "|" + out["_company"]
    out["_name_website"] = out["_first"] + "|" + out["_last"] + "|" + out["_website"]
    return out


def dedupe_against_master(
    master_df: pd.DataFrame,
    check_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """Remove duplicates from *check_df* that exist in *master_df*.

    Returns ``(cleaned_df, removed_df, summary)``.
    """
    master = _prepare(master_df)
    check = _prepare(check_df)

    # Build lookup sets from master
    email_set = set(master.loc[master["_email"] != "", "_email"])
    linkedin_set = set(master.loc[master["_linkedin"] != "", "_linkedin"])
    nc_set = set(master.loc[master["_name_company"] != "||", "_name_company"])
    nw_set = set(master.loc[master["_name_website"] != "||", "_name_website"])

    # Determine match reasons
    check["_match_reason"] = ""

    m1 = check["_email"].isin(email_set)
    check.loc[m1, "_match_reason"] = "email"

    m2 = (check["_match_reason"] == "") & check["_linkedin"].isin(linkedin_set)
    check.loc[m2, "_match_reason"] = "linkedin"

    m3 = (check["_match_reason"] == "") & check["_name_company"].isin(nc_set)
    check.loc[m3, "_match_reason"] = "name+company"

    m4 = (check["_match_reason"] == "") & check["_name_website"].isin(nw_set)
    check.loc[m4, "_match_reason"] = "name+website"

    is_dup = check["_match_reason"] != ""

    removed = check[is_dup].copy()
    cleaned = check[~is_dup].copy()

    # Drop helper columns
    helper = [c for c in cleaned.columns if c.startswith("_")]
    cleaned.drop(columns=helper, inplace=True)
    # Keep _match_reason in removed for export
    removed_export = removed.drop(
        columns=[c for c in removed.columns if c.startswith("_") and c != "_match_reason"]
    ).rename(columns={"_match_reason": "Match Reason"})

    summary = generate_summary(
        tool_name="Deduplicate Against Master",
        before_count=len(check_df),
        after_count=len(cleaned),
        removed_count=len(removed),
        extra_info={
            "By email": int(m1.sum()),
            "By LinkedIn": int(m2.sum()),
            "By name+company": int(m3.sum()),
            "By name+website": int(m4.sum()),
        },
    )
    return cleaned, removed_export, summary
