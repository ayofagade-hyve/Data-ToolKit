"""Job and organisation type classification tools."""
import pandas as pd
from utils.classifiers import classify_seniority, classify_job_function, classify_org_type
from utils.column_mapping import get_series, find_column
from utils.io_helpers import generate_summary


def classify_jobs(df, title_col, seniority_col=None, dept_col=None):
    result = df.copy()
    titles = result[title_col].fillna("").astype(str)
    seniorities = result[seniority_col].fillna("").astype(str) if seniority_col else pd.Series([""] * len(df))
    departments = result[dept_col].fillna("").astype(str) if dept_col else pd.Series([""] * len(df))
    result["Seniority (classified)"] = [classify_seniority(t, s) for t, s in zip(titles, seniorities)]
    result["Job Function (classified)"] = [classify_job_function(t, d) for t, d in zip(titles, departments)]
    summary = generate_summary("Classify Seniority & Job Function", len(df), len(result),
        extra_info={"Title column": title_col,
                    "Seniority values": ", ".join(result["Seniority (classified)"].value_counts().head(6).index.tolist()),
                    "Function values": ", ".join(result["Job Function (classified)"].value_counts().head(10).index.tolist())})
    return result, summary


def classify_org_types(df):
    result = df.copy()
    industries = get_series(df, "industry")
    companies = get_series(df, "company")
    job_titles = get_series(df, "job_title")
    websites = get_series(df, "website")
    company_types = pd.Series([""] * len(df))
    company_techs = pd.Series([""] * len(df))
    result["Organization Type (classified)"] = [
        classify_org_type(ind, comp, title, web, ct, ctech)
        for ind, comp, title, web, ct, ctech in zip(industries, companies, job_titles, websites, company_types, company_techs)]
    summary = generate_summary("Classify Organisation Type", len(df), len(result),
        extra_info={"Org types found": ", ".join(result["Organization Type (classified)"].value_counts().head(10).index.tolist())})
    return result, summary
