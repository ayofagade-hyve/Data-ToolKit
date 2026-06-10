"""Deduplicate against a master list using 4-key matching."""
import pandas as pd
from utils.column_mapping import find_column, get_series
from utils.io_helpers import generate_summary
from utils.name_tools import split_full_name

def _normalize_url(url):
    url = str(url or "").strip().lower()
    url = url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
    return url

def _normalize(value):
    return str(value or "").strip().lower()

def dedupe_against_master(master_df, check_df):
    m_emails = get_series(master_df, "email")
    m_linkedin = get_series(master_df, "linkedin")
    m_first = get_series(master_df, "first_name")
    m_last = get_series(master_df, "last_name")
    m_company = get_series(master_df, "company")
    m_website = get_series(master_df, "website")
    fnc = find_column(master_df, "full_name")
    if fnc and not find_column(master_df, "first_name"):
        names = master_df[fnc].fillna("").astype(str).apply(split_full_name)
        m_first = names.apply(lambda x: x[0]).str.lower().str.strip()
        m_last = names.apply(lambda x: x[1]).str.lower().str.strip()
    email_set = set(m_emails.str.lower().str.strip()) - {""}
    linkedin_set = set(m_linkedin.apply(_normalize_url)) - {""}
    nc_set = set()
    nw_set = set()
    for fn, ln, c, w in zip(m_first, m_last, m_company, m_website):
        fn, ln, c = _normalize(fn), _normalize(ln), _normalize(c)
        wn = _normalize_url(w)
        if fn and ln and c: nc_set.add((fn, ln, c))
        if fn and ln and wn: nw_set.add((fn, ln, wn))
    c_emails = get_series(check_df, "email")
    c_linkedin = get_series(check_df, "linkedin")
    c_first = get_series(check_df, "first_name")
    c_last = get_series(check_df, "last_name")
    c_company = get_series(check_df, "company")
    c_website = get_series(check_df, "website")
    fnc2 = find_column(check_df, "full_name")
    if fnc2 and not find_column(check_df, "first_name"):
        names2 = check_df[fnc2].fillna("").astype(str).apply(split_full_name)
        c_first = names2.apply(lambda x: x[0]).str.lower().str.strip()
        c_last = names2.apply(lambda x: x[1]).str.lower().str.strip()
    is_dupe, reasons = [], []
    for i in range(len(check_df)):
        email = _normalize(c_emails.iloc[i])
        linkedin = _normalize_url(c_linkedin.iloc[i])
        first = _normalize(c_first.iloc[i])
        last = _normalize(c_last.iloc[i])
        company = _normalize(c_company.iloc[i])
        website = _normalize_url(c_website.iloc[i])
        if email and email in email_set:
            is_dupe.append(True); reasons.append("Email match"); continue
        if linkedin and linkedin in linkedin_set:
            is_dupe.append(True); reasons.append("LinkedIn match"); continue
        if first and last and company and (first, last, company) in nc_set:
            is_dupe.append(True); reasons.append("Name + Company match"); continue
        if first and last and website and (first, last, website) in nw_set:
            is_dupe.append(True); reasons.append("Name + Website match"); continue
        is_dupe.append(False); reasons.append("")
    cr = check_df.copy()
    cr["_is_dupe"] = is_dupe; cr["Match Reason"] = reasons
    cleaned = cr[~cr["_is_dupe"]].drop(columns=["_is_dupe", "Match Reason"]).copy()
    removed = cr[cr["_is_dupe"]].drop(columns=["_is_dupe"]).copy()
    summary = generate_summary("Deduplicate vs Master List", len(check_df), len(cleaned), removed_count=len(removed),
        extra_info={"Master list size": f"{len(master_df):,}",
                    "Email matches": str(reasons.count("Email match")),
                    "LinkedIn matches": str(reasons.count("LinkedIn match")),
                    "Name+Company matches": str(reasons.count("Name + Company match")),
                    "Name+Website matches": str(reasons.count("Name + Website match"))})
    return cleaned, removed, summary
