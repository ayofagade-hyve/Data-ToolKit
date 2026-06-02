"""
Matching & Fuzzy-Duplicate Utilities
====================================
Provides Levenshtein distance, similarity percentage, and a
configurable fuzzy-duplicate finder.  Ported from the multiple
``findDuplicatesInSheet8`` functions in the original Apps Scripts.
"""

from __future__ import annotations
from typing import List, Tuple
import pandas as pd


def levenshtein(a: str, b: str) -> int:
    """Memory-efficient Levenshtein distance (two-row algorithm)."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la

    prev = list(range(lb + 1))
    cur = [0] * (lb + 1)

    for i in range(1, la + 1):
        cur[0] = i
        ai = a[i - 1]
        for j in range(1, lb + 1):
            cost = 0 if ai == b[j - 1] else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost)
        prev, cur = cur, prev

    return prev[lb]


def similarity_pct(a: str, b: str) -> int:
    """Return similarity as an integer 0–100."""
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    if not a and not b:
        return 0
    if a == b:
        return 100
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 0
    return round((1 - levenshtein(a, b) / max_len) * 100)


def find_fuzzy_duplicates(
    values: List[str],
    threshold: int = 90,
) -> List[Tuple[int, str, str, int, int]]:
    """Find fuzzy duplicates in a list of strings.

    Returns a list of tuples:
        (row_index, status, match_name, match_pct, first_occurrence_index)

    ``status`` is ``'Unique'`` or ``'Duplicate'``.
    For unique rows, ``match_name``/``match_pct``/``first_occurrence_index``
    are ``''``, ``0``, ``-1`` respectively.
    """
    n = len(values)
    results: List[Tuple[int, str, str, int, int]] = []

    for i in range(n):
        current = (values[i] or "").strip()
        if not current:
            results.append((i, "", "", 0, -1))
            continue

        best_pct = 0
        best_idx = -1
        for j in range(i):
            other = (values[j] or "").strip()
            if not other:
                continue
            pct = similarity_pct(current, other)
            if pct > best_pct:
                best_pct = pct
                best_idx = j

        if best_idx != -1 and best_pct >= threshold:
            results.append((i, "Duplicate", values[best_idx], best_pct, best_idx))
        else:
            results.append((i, "Unique", "", 0, -1))

    return results
