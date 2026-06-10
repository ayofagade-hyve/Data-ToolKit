"""Data standardisation tools: names, phones, URLs."""
import re
import pandas as pd
from utils.name_tools import split_full_name
from utils.io_helpers import generate_summary

def standardize_names(df, name_col):
    result = df.copy()
    names = result[name_col].fillna("").astype(str).apply(split_full_name)
    result["First Name"] = names.apply(lambda x: x[0])
    result["Last Name"] = names.apply(lambda x: x[1])
    return result

def standardize_phones(df, phone_col):
    result = df.copy()
    original = result[phone_col].fillna("").astype(str)
    def clean_phone(phone):
        phone = str(phone).strip()
        if not phone: return ""
        cleaned = re.sub(r"[^\d+\s]", "", phone)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    result[phone_col] = original.apply(clean_phone)
    changes = (original != result[phone_col]).sum()
    summary = generate_summary("Standardise Phone Numbers", len(df), len(result),
        extra_info={"Cells changed": f"{changes:,}", "Column": phone_col})
    return result, summary

def standardize_urls(df, url_col):
    result = df.copy()
    original = result[url_col].fillna("").astype(str)
    def clean_url(url):
        url = str(url).strip().lower()
        if not url: return ""
        url = url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")
        if not url: return ""
        return f"https://{url}"
    result[url_col] = original.apply(clean_url)
    changes = (original != result[url_col]).sum()
    summary = generate_summary("Standardise URLs", len(df), len(result),
        extra_info={"Cells changed": f"{changes:,}", "Column": url_col})
    return result, summary
