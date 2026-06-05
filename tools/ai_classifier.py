ai_classifier_code = '''"""AI Column Classifier — zero-shot classification via Hugging Face Inference API.

Speed optimisations
-------------------
1. **Deduplication** – only unique values are sent to the API.
   If "Software Engineer" appears 500 times it is classified once.
2. **Parallel requests** – up to 10 concurrent API calls via ThreadPoolExecutor.
"""

import time
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "https://api-inference.huggingface.co/models/{model_id}"
MAX_WORKERS = 10  # parallel API calls


# ── single-text classification ──────────────────────────────────────
def classify_text(text, labels, api_token,
                  model_id="facebook/bart-large-mnli",
                  multi_label=False):
    """
    Classify a single text string against candidate labels using the
    Hugging Face Inference API.

    Returns
    -------
    dict  –  {"label": str, "confidence": float}
    """
    url = API_URL.format(model_id=model_id)
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": labels,
            "multi_label": multi_label,
        },
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)

            if resp.status_code == 503:
                # Model is waking up – wait and retry
                wait = 15 if attempt == 0 else 25
                time.sleep(wait)
                continue

            if resp.status_code == 429:
                # Rate-limited – back off
                time.sleep(5)
                continue

            resp.raise_for_status()
            data = resp.json()

            top_label = data["labels"][0]
            top_score = round(data["scores"][0], 3)
            return {"label": top_label, "confidence": top_score}

        except Exception:
            time.sleep(3)
            continue

    return {"label": "Error", "confidence": 0.0}


# ── classify an entire column (fast) ────────────────────────────────
def classify_column(df, text_col, labels, api_token,
                    model_id="facebook/bart-large-mnli",
                    multi_label=False,
                    confidence_threshold=0.3):
    """
    Classify every value in *text_col* using the HF Inference API.

    Speed tricks
    ------------
    * Unique values are extracted first so duplicates are classified once.
    * Unique values are sent in parallel (up to 10 concurrent requests).

    Returns
    -------
    result_df : pd.DataFrame  – original df + AI_Classification, AI_Confidence
    summary : dict
    """
    rows_before = len(df)
    texts = df[text_col].fillna("").astype(str).tolist()

    # ── Step 1: deduplicate ──────────────────────────────────────
    unique_texts = list({t.strip() for t in texts if t.strip() != ""})
    total_non_empty = sum(1 for t in texts if t.strip() != "")

    # ── Step 2: classify unique values in parallel ───────────────
    lookup = {}

    def _classify_one(text):
        return text, classify_text(
            text, labels, api_token,
            model_id=model_id,
            multi_label=multi_label,
        )

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_classify_one, t): t for t in unique_texts}
        for future in as_completed(futures):
            text, result = future.result()
            lookup[text] = result

    # ── Step 3: map results back to every row ────────────────────
    classifications = []
    confidences = []
    empty_count = 0
    uncertain_count = 0
    classified_count = 0
    error_count = 0

    for text in texts:
        stripped = text.strip()

        if stripped == "":
            classifications.append("Empty")
            confidences.append(0.0)
            empty_count += 1
            continue

        result = lookup.get(stripped, {"label": "Error", "confidence": 0.0})
        lbl = result["label"]
        score = result["confidence"]

        if lbl == "Error":
            classifications.append("Error")
            confidences.append(0.0)
            error_count += 1
        elif score < confidence_threshold:
            classifications.append(f"Uncertain ({lbl})")
            confidences.append(score)
            uncertain_count += 1
        else:
            classifications.append(lbl)
            confidences.append(score)
            classified_count += 1

    result_df = df.copy()
    result_df["AI_Classification"] = classifications
    result_df["AI_Confidence"] = confidences

    summary = {
        "Tool": "AI Column Classifier",
        "Rows before": rows_before,
        "Rows after": rows_before,
        "Rows removed / changed": f"{classified_count + uncertain_count} classified",
        "Classified (confident)": classified_count,
        "Uncertain (below threshold)": uncertain_count,
        "Empty / skipped": empty_count,
        "Errors": error_count,
        "Unique values classified": f"{len(unique_texts)} unique out of {total_non_empty:,} non-empty rows",
    }
    return result_df, summary


# ── helper ───────────────────────────────────────────────────────────
def classification_summary(df):
    """Return a value-counts DataFrame of the AI_Classification column."""
    if "AI_Classification" not in df.columns:
        return pd.DataFrame()
    counts = df["AI_Classification"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    return counts
'''

with open("ai_classifier.py", "w", encoding="utf-8") as f:
    f.write(ai_classifier_code)

print("✅ ai_classifier.py written successfully")
print(f"   Size: {len(ai_classifier_code):,} characters")
print()
print("=== SPEED COMPARISON ===")
print()
print("Example: 5,000 rows with 200 unique job titles")
print()
print("BEFORE (old version):")
print("  • 5,000 API calls (one per row)")
print("  • ~1 second each = ~83 minutes")
print()
print("AFTER (new version):")
print("  • 200 API calls (one per unique value)")
print("  • 10 in parallel = ~20 seconds")
print("  • That's ~250x faster")