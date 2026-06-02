"""
Text Cleaning Utilities
=======================
Fixes mojibake (garbled character encoding), standardises whitespace,
and applies a comprehensive character-replacement map ported from the
original Google Apps Script `text clean.gs` and `consolidate.gs`.

The optional `ftfy` library is used when available for an extra pass;
the built-in character map handles the most common cases on its own.
"""

import re
import unicodedata
import pandas as pd

try:
    import ftfy
    HAS_FTFY = True
except ImportError:
    HAS_FTFY = False

# ── Mojibake replacement map ───────────────────────────────────
# Each tuple is (broken_sequence, correct_character).
# Ported from the Apps Script `applyCharacterMap` functions.
CHARACTER_MAP = [
    # Western European uppercase
    ("\u00c3\u20ac", "\u00c0"),   # À
    ("\u00c3\ufeff", "\u00c1"),   # Á  (BOM variant)
    ("\u00c3\u201a", "\u00c2"),   # Â
    ("\u00c3\u0192", "\u00c3"),   # Ã
    ("\u00c3\u201e", "\u00c4"),   # Ä
    ("\u00c3\u2026", "\u00c5"),   # Å
    ("\u00c3\u2020", "\u00c6"),   # Æ
    ("\u00c3\u2021", "\u00c7"),   # Ç
    ("\u00c3\u02c6", "\u00c8"),   # È
    ("\u00c3\u2030", "\u00c9"),   # É
    ("\u00c3\u0160", "\u00ca"),   # Ê
    ("\u00c3\u2039", "\u00cb"),   # Ë
    ("\u00c3\u0152", "\u00cc"),   # Ì
    ("\u00c3\ufeff", "\u00cd"),   # Í
    ("\u00c3\u017d", "\u00ce"),   # Î
    ("\u00c3\ufeff", "\u00cf"),   # Ï
    ("\u00c3\u2019", "\u00d1"),   # Ñ
    ("\u00c3\u2018", "\u00d2"),   # Ò
    ("\u00c3\u201c", "\u00d3"),   # Ó
    ("\u00c3\u201d", "\u00d4"),   # Ô
    ("\u00c3\u2022", "\u00d5"),   # Õ
    ("\u00c3\u2013", "\u00d6"),   # Ö
    ("\u00c3\u02dc", "\u00d8"),   # Ø
    ("\u00c3\u2122", "\u00d9"),   # Ù
    ("\u00c3\u0161", "\u00da"),   # Ú
    ("\u00c3\u203a", "\u00db"),   # Û
    ("\u00c3\u0153", "\u00dc"),   # Ü
    ("\u00c3\ufeff", "\u00dd"),   # Ý
    ("\u00c3\u017e", "\u00de"),   # Þ
    # Western European lowercase
    ("\u00c3\u0178", "\u00df"),   # ß
    ("\u00c3\u00a0", "\u00e0"),   # à
    ("\u00c3\u00a1", "\u00e1"),   # á
    ("\u00c3\u00a2", "\u00e2"),   # â
    ("\u00c3\u00a3", "\u00e3"),   # ã
    ("\u00c3\u00a4", "\u00e4"),   # ä
    ("\u00c3\u00a5", "\u00e5"),   # å
    ("\u00c3\u00a6", "\u00e6"),   # æ
    ("\u00c3\u00a7", "\u00e7"),   # ç
    ("\u00c3\u00a8", "\u00e8"),   # è
    ("\u00c3\u00a9", "\u00e9"),   # é
    ("\u00c3\u00aa", "\u00ea"),   # ê
    ("\u00c3\u00ab", "\u00eb"),   # ë
    ("\u00c3\u00ac", "\u00ec"),   # ì
    ("\u00c3\u00ad", "\u00ed"),   # í
    ("\u00c3\u00ae", "\u00ee"),   # î
    ("\u00c3\u00af", "\u00ef"),   # ï
    ("\u00c3\u00b0", "\u00f0"),   # ð
    ("\u00c3\u00b1", "\u00f1"),   # ñ
    ("\u00c3\u00b2", "\u00f2"),   # ò
    ("\u00c3\u00b3", "\u00f3"),   # ó
    ("\u00c3\u00b4", "\u00f4"),   # ô
    ("\u00c3\u00b5", "\u00f5"),   # õ
    ("\u00c3\u00b6", "\u00f6"),   # ö
    ("\u00c3\u00b8", "\u00f8"),   # ø
    ("\u00c3\u00b9", "\u00f9"),   # ù
    ("\u00c3\u00ba", "\u00fa"),   # ú
    ("\u00c3\u00bb", "\u00fb"),   # û
    ("\u00c3\u00bc", "\u00fc"),   # ü
    ("\u00c3\u00bd", "\u00fd"),   # ý
    ("\u00c3\u00be", "\u00fe"),   # þ
    ("\u00c3\u00bf", "\u00ff"),   # ÿ
    # Punctuation / symbols
    ("\u00e2\u20ac\u201c", "\u2013"),  # –
    ("\u00e2\u20ac\u201d", "\u2014"),  # —
    ("\u00e2\u20ac\u02dc", "\u2018"),  # '
    ("\u00e2\u20ac\u2122", "\u2019"),  # '
    ("\u00e2\u20ac\u0153", "\u201c"),  # "
    ("\u00e2\u20ac\ufeff", "\u201d"),  # "
    ("\u00e2\u20ac\u00a6", "\u2026"),  # …
    ("\u00e2\u20ac\u00a2", "\u2022"),  # •
    ("\u00c2\u00a3", "\u00a3"),        # £
    ("\u00e2\u201a\u00ac", "\u20ac"),  # €
    ("\u00c2\u00a9", "\u00a9"),        # ©
    ("\u00c2\u00ae", "\u00ae"),        # ®
    ("\u00c2\u00b0", "\u00b0"),        # °
    ("\u00c2\u00b7", "\u00b7"),        # ·
    ("\u00c2\u00bd", "\u00bd"),        # ½
    ("\u00c2\u00bc", "\u00bc"),        # ¼
    ("\u00c2\u00be", "\u00be"),        # ¾
]


def apply_character_map(text: str) -> str:
    """Apply the mojibake character replacement map."""
    for broken, fixed in CHARACTER_MAP:
        text = text.replace(broken, fixed)
    return text


def _looks_broken(text: str) -> bool:
    """Quick heuristic: does *text* contain common mojibake sequences?"""
    return bool(re.search(r"[\u00c3\u00c4\u00c5\u00c6\u00c8\u00d0\u00d1\u00cb\u00e2\u00c2]", text))


def fix_mojibake(text: str) -> str:
    """Fix encoding problems in a single string.

    Strategy:
      1. Try ftfy (if installed) for a quick first pass.
      2. Try re-interpreting as cp1252 → utf-8 (common CSV export issue).
      3. Apply the explicit character replacement map.
      4. Strip stray ``\\u00c2`` characters left over.
      5. Normalise whitespace.
    """
    if not isinstance(text, str) or not text:
        return text

    # Pass 1 – ftfy (handles most double-encoding automatically)
    if HAS_FTFY:
        text = ftfy.fix_text(text)

    # Pass 2 – manual re-encoding attempt (up to 3 passes for triple-encoding)
    for _ in range(3):
        try:
            candidate = text.encode("cp1252").decode("utf-8")
            if candidate == text:
                break
            text = candidate
        except (UnicodeDecodeError, UnicodeEncodeError):
            break

    # Pass 3 – explicit character map
    if _looks_broken(text):
        text = apply_character_map(text)

    # Pass 4 – cleanup stray artefacts
    text = re.sub(r"\u00c2(?=[\x80-\xff])", "", text)
    text = text.replace("\u00c2 ", " ")

    # Normalise whitespace
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


def fix_mojibake_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply ``fix_mojibake`` to every string cell in *df*."""
    result = df.copy()
    for col in result.select_dtypes(include=["object"]).columns:
        result[col] = result[col].map(
            lambda v: fix_mojibake(v) if isinstance(v, str) else v
        )
    return result
