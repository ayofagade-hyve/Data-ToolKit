"""Mojibake (encoding corruption) fixer.

Strategy (4 passes):
1. ftfy library (if available) - handles double-encoding
2. Manual re-encoding: cp1252 -> utf-8 (up to 3 passes)
3. Explicit character map (40+ common broken sequences)
4. Stray character removal + whitespace normalization
"""
import re
import pandas as pd

try:
    import ftfy
    HAS_FTFY = True
except ImportError:
    HAS_FTFY = False

CHARACTER_MAP = [
    ("\u00c3\u0080", "\u00c0"),  # À
    ("\u00c3\u0081", "\u00c1"),  # Á
    ("\u00c3\u0082", "\u00c2"),  # Â
    ("\u00c3\u0083", "\u00c3"),  # Ã
    ("\u00c3\u0084", "\u00c4"),  # Ä
    ("\u00c3\u0085", "\u00c5"),  # Å
    ("\u00c3\u0086", "\u00c6"),  # Æ
    ("\u00c3\u0087", "\u00c7"),  # Ç
    ("\u00c3\u0088", "\u00c8"),  # È
    ("\u00c3\u0089", "\u00c9"),  # É
    ("\u00c3\u008a", "\u00ca"),  # Ê
    ("\u00c3\u008b", "\u00cb"),  # Ë
    ("\u00c3\u008c", "\u00cc"),  # Ì
    ("\u00c3\u008d", "\u00cd"),  # Í
    ("\u00c3\u008e", "\u00ce"),  # Î
    ("\u00c3\u008f", "\u00cf"),  # Ï
    ("\u00c3\u0090", "\u00d0"),  # Ð
    ("\u00c3\u0091", "\u00d1"),  # Ñ
    ("\u00c3\u0092", "\u00d2"),  # Ò
    ("\u00c3\u0093", "\u00d3"),  # Ó
    ("\u00c3\u0094", "\u00d4"),  # Ô
    ("\u00c3\u0095", "\u00d5"),  # Õ
    ("\u00c3\u0096", "\u00d6"),  # Ö
    ("\u00c3\u0097", "\u00d7"),  # ×
    ("\u00c3\u0098", "\u00d8"),  # Ø
    ("\u00c3\u0099", "\u00d9"),  # Ù
    ("\u00c3\u009a", "\u00da"),  # Ú
    ("\u00c3\u009b", "\u00db"),  # Û
    ("\u00c3\u009c", "\u00dc"),  # Ü
    ("\u00c3\u009d", "\u00dd"),  # Ý
    ("\u00c3\u009e", "\u00de"),  # Þ
    ("\u00c3\u009f", "\u00df"),  # ß
    ("\u00c3\u00a0", "\u00e0"),  # à
    ("\u00c3\u00a1", "\u00e1"),  # á
    ("\u00c3\u00a2", "\u00e2"),  # â
    ("\u00c3\u00a3", "\u00e3"),  # ã
    ("\u00c3\u00a4", "\u00e4"),  # ä
    ("\u00c3\u00a5", "\u00e5"),  # å
    ("\u00c3\u00a6", "\u00e6"),  # æ
    ("\u00c3\u00a7", "\u00e7"),  # ç
    ("\u00c3\u00a8", "\u00e8"),  # è
    ("\u00c3\u00a9", "\u00e9"),  # é
    ("\u00c3\u00aa", "\u00ea"),  # ê
    ("\u00c3\u00ab", "\u00eb"),  # ë
    ("\u00c3\u00ac", "\u00ec"),  # ì
    ("\u00c3\u00ad", "\u00ed"),  # í
    ("\u00c3\u00ae", "\u00ee"),  # î
    ("\u00c3\u00af", "\u00ef"),  # ï
    # Special characters
    ("\u00c3\u20ac", "\u00c0"),
    ("\u00c3\u201a", "\u00c2"),
    ("\u00e2\u20ac\u201d", "\u2014"),   # em dash
    ("\u00e2\u20ac\u201c", "\u2013"),   # en dash
    ("\u00e2\u20ac\u2122", "\u2019"),   # right single quote
    ("\u00e2\u20ac\u0153", "\u201c"),   # left double quote
    ("\u00e2\u20ac\u009d", "\u201d"),   # right double quote
    ("\u00e2\u201a\u00ac", "\u20ac"),   # euro sign
    ("\u00c2\u00a0", " "),               # non-breaking space
    ("\u00c2\u00ab", "\u00ab"),          # «
    ("\u00c2\u00bb", "\u00bb"),          # »
    ("\u00c2\u00b0", "\u00b0"),          # °
]


def _pass1_ftfy(text):
    if HAS_FTFY:
        return ftfy.fix_text(text)
    return text


def _pass2_reencode(text):
    for _ in range(3):
        try:
            decoded = text.encode("cp1252").decode("utf-8")
            if decoded == text:
                break
            text = decoded
        except (UnicodeDecodeError, UnicodeEncodeError):
            break
    return text


def _pass3_charmap(text):
    for broken, fixed in CHARACTER_MAP:
        if broken in text:
            text = text.replace(broken, fixed)
    return text


def _pass4_cleanup(text):
    text = re.sub(r"\u00c2(?![\u00a0-\u00bf])", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fix_mojibake(text):
    """Fix mojibake (encoding corruption) in a text string."""
    if not text or not isinstance(text, str):
        return text or ""
    text = _pass1_ftfy(text)
    text = _pass2_reencode(text)
    text = _pass3_charmap(text)
    text = _pass4_cleanup(text)
    return text


def fix_mojibake_column(series):
    """Apply mojibake fix to an entire pandas Series."""
    return series.fillna("").astype(str).apply(fix_mojibake)
