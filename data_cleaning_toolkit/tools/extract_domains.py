"""Extract company domains from email addresses."""
from utils.domain_tools import extract_domains_for_companies
from utils.io_helpers import generate_summary

def extract_domains(df, email_col, company_col):
    result, missing = extract_domains_for_companies(df, email_col, company_col)
    domains_found = (result["Domain"] != "").sum()
    summary = generate_summary("Extract Company Domains", len(df), len(result),
        extra_info={"Domains extracted": f"{domains_found:,}", "Companies without domain": f"{len(missing):,}"})
    return result, missing, summary
