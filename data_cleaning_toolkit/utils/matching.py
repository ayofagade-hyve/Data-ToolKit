"""Fuzzy string matching with blocking strategy for performance."""
from collections import defaultdict


def levenshtein(a, b):
    """Levenshtein distance using two-row algorithm."""
    a = str(a).lower().strip()
    b = str(b).lower().strip()
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b) + 1))
    curr = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        curr[0] = i
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            curr[j] = min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev
    return prev[len(b)]


def similarity_pct(a, b):
    """Similarity percentage (0-100)."""
    a, b = str(a).strip(), str(b).strip()
    if not a and not b: return 100
    if not a or not b: return 0
    max_len = max(len(a), len(b))
    if max_len == 0: return 100
    return int(round((1 - levenshtein(a, b) / max_len) * 100))


def _block_key(value, length=3):
    cleaned = value.lower().strip()
    return cleaned[:length] if len(cleaned) >= length else cleaned


def find_fuzzy_duplicates(values, threshold=90):
    """Find near-duplicates using blocking + Levenshtein similarity."""
    results = []
    value_list = [(i, str(v).strip()) for i, v in enumerate(values) if str(v).strip()]

    # Phase 1: exact dedup
    exact_map = {}
    for i, val in value_list:
        key = val.lower()
        if key in exact_map:
            results.append((i, "Duplicate", val, 100, exact_map[key]))
        else:
            exact_map[key] = i

    exact_dupes = {r[0] for r in results}
    unique_entries = [(i, val) for i, val in value_list if i not in exact_dupes]

    # Phase 2: blocking with first 3 chars
    blocks = defaultdict(list)
    for i, val in unique_entries:
        blocks[_block_key(val, 3)].append((i, val))

    blocks_2 = defaultdict(set)
    for key_3 in blocks:
        blocks_2[key_3[:2]].add(key_3)

    matched = set()
    for key_2, block_keys in blocks_2.items():
        combined = []
        for bk in block_keys:
            combined.extend(blocks[bk])
        for a in range(len(combined)):
            idx_a, val_a = combined[a]
            if idx_a in matched:
                continue
            for b in range(a + 1, len(combined)):
                idx_b, val_b = combined[b]
                if idx_b in matched:
                    continue
                pct = similarity_pct(val_a, val_b)
                if pct >= threshold:
                    matched.add(idx_b)
                    results.append((idx_b, "Duplicate", val_a, pct, idx_a))

    all_matched = {r[0] for r in results}
    for i, val in value_list:
        if i not in all_matched:
            results.append((i, "Unique", "", 0, i))

    results.sort(key=lambda x: x[0])
    return results
