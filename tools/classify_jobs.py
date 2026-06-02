"""
Classify Job Seniority, Function & Organisation Type
=======================================================
"""

from __future__ import annotations
from typing import Tuple, Dict, Any
import pandas as pd
from utils.classifiers import (
    classify_seniority,
    classify_job_function,
    classify_org_type,
)
from utils.column_mapping import find_column, get_series
from utils.io_helpers import generate_summary


def classify_jobs(
    df: pd.DataFrame,
    title_col: str,
    seniority_col: str | None = None,
    dept_col: str | None = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Add seniority and job-function columns based on job titles.

    Returns ``(result_df, summary)``.
    """
    result = df.copy()
    titles = result[title_col].fillna("").astype(str)
    orig_sen = (
        result[seniority_col].fillna("").astype(str) if seniority_col else pd.Series([""] * len(df))
    )
    depts = (
        result[dept_col].fillna("").astype(str) if dept_col else pd.Series([""] * len(df))
    )

    result["Seniority (classified)"] = [
        classify_seniority(t, s)
        for t, s in zip(titles, orig_sen)
    ]
    result["Job Function (classified)"] = [
        classify_job_function(t, d)
        for t, d in zip(titles, depts)
    ]

    summary = generate_summary(
        tool_name="Classify Jobs",
        before_count=len(df),
        after_count=len(result),
        extra_info={
            "Seniority column": "Seniority (classified)",
            "Function column": "Job Function (classified)",
        },
    )
    return result, summary


def classify_org_types(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Add organisation type based on available columns.

    Returns ``(result_df, summary)``.
    """
    result = df.copy()
    industries = get_series(df, "industries")
    company = get_series(df, "company")
    title = get_series(df, "job_title")
    website = get_series(df, "website")
    ctype = get_series(df, "company_type")
    ctech = get_series(df, "company_tech")

    result["Organization Type (classified)"] = [
        classify_org_type(ind, comp, tit, web, ct, cte)
        for ind, comp, tit, web, ct, cte
        in zip(industries, company, title, website, ctype, ctech)
    ]

    summary = generate_summary(
        tool_name="Classify Organisation Type",
        before_count=len(df),
        after_count=len(result),
        extra_info={"Column added": "Organization Type (classified)"},
    )
    return result, summary
