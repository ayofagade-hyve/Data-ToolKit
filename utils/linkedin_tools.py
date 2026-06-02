"""
LinkedIn URL Utilities
=======================
Ported from ``Linin.gs``.
"""

from __future__ import annotations
import re
from urllib.parse import quote_plus


def normalize_linkedin_url(url: str) -> str:
    """Normalise a LinkedIn profile URL for comparison."""
    u = str(url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    return u.rstrip("/")


def generate_linkedin_search_url(
    name: str,
    title: str = "",
    company: str = "",
) -> str:
    """Generate a LinkedIn People-search URL."""
    parts = [str(name or "").strip()]
    if title:
        parts.append(str(title).strip())
    if company:
        parts.append(str(company).strip())
    query = " ".join(p for p in parts if p)
    if not query:
        return ""
    return (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={quote_plus(query)}"
    )
