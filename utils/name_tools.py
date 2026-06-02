"""
Name Splitting & Text Normalisation
=====================================
Ported from ``strsep.gs`` and ``extract company.gs``.
"""

from __future__ import annotations
import re
import unicodedata


def normalize_text(value: str) -> str:
    """Lower-case, strip accents, remove punctuation, collapse whitespace."""
    text = str(value or "").lower()
    text = unicodedata.normalize("NFD", text)
    text = re.sub(r"[\u0300-\u036f]", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_any(text: str, phrases: list) -> bool:
    """Return True if *text* contains any of the *phrases*."""
    return any(p in text for p in phrases)


def split_name(full_name: str) -> tuple:
    """Split a full name into ``(first_name, last_name)``."""
    name = str(full_name or "").strip()
    if not name:
        return ("", "")
    parts = name.split(None, 1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""
    return (first, last)


def extract_company_from_title(title_string: str) -> str:
    """Extract a company name from strings like ``'John Doe at Acme Corp'``."""
    text = str(title_string or "").strip()
    if not text:
        return ""
    parts = text.split(" at ")
    if len(parts) > 1:
        return parts[-1].strip()
    return ""


def clean_company_name(name: str) -> str:
    """Remove common suffixes and noise from company names."""
    text = str(name or "").strip()
    text = re.sub(r"\s*-\s*fm\s*\d+\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bupsell\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bextra ticket\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[,.;]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
