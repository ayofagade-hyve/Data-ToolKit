"""Generate LinkedIn search links for contacts."""
import pandas as pd
from utils.linkedin_tools import generate_linkedin_search_url
from utils.io_helpers import generate_summary

def generate_links(df, first_col, last_col, company_col=None):
    result = df.copy()
    urls = []
    for _, row in result.iterrows():
        first = str(row.get(first_col, "")).strip()
        last = str(row.get(last_col, "")).strip()
        company = str(row.get(company_col, "")).strip() if company_col else ""
        urls.append(generate_linkedin_search_url(first, last, company))
    result["LinkedIn Search URL"] = urls
    generated = sum(1 for u in urls if u)
    summary = generate_summary("LinkedIn Search Links", len(df), len(result),
        extra_info={"Links generated": f"{generated:,}", "Empty (no name data)": f"{len(df) - generated:,}"})
    return result, summary
