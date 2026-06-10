"""Domain extraction utilities."""
import pandas as pd
from typing import Optional

PERSONAL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "protonmail.com", "live.com",
    "msn.com", "ymail.com", "mail.com", "zoho.com",
    "gmx.com", "fastmail.com", "hushmail.com", "tutanota.com",
    "yahoo.co.uk", "hotmail.co.uk", "googlemail.com",
    "me.com", "mac.com", "inbox.com",
}


def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract the corporate domain from an email address. Returns None if personal."""
    email = str(email).strip().lower()
    if "@" not in email:
        return None
    try:
        domain = email.rsplit("@", 1)[1].strip()
    except IndexError:
        return None
    if not domain or "." not in domain:
        return None
    if domain in PERSONAL_DOMAINS:
        return None
    return domain


def extract_domains_for_companies(df, email_col, company_col):
    """Extract corporate domains for each company from email addresses."""
    result = df.copy()
    result["Domain"] = ""
    company_domains = {}
    for _, row in df.iterrows():
        company = str(row.get(company_col, "")).strip()
        email = str(row.get(email_col, "")).strip()
        if not company or not email:
            continue
        domain = extract_domain_from_email(email)
        if domain:
            ck = company.lower()
            if ck not in company_domains:
                company_domains[ck] = {}
            company_domains[ck][domain] = company_domains[ck].get(domain, 0) + 1
    best_domains = {ck: max(d, key=d.get) for ck, d in company_domains.items()}
    missing_companies = set()
    for i, row in result.iterrows():
        company = str(row.get(company_col, "")).strip()
        if not company:
            continue
        ck = company.lower()
        if ck in best_domains:
            result.at[i, "Domain"] = best_domains[ck]
        else:
            missing_companies.add(company)
    missing_df = pd.DataFrame({"Company": sorted(missing_companies)})
    return result, missing_df
