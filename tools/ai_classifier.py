"""AI Column Classifier — zero-shot classification via Hugging Face Inference API."""

import time
import requests
import pandas as pd

API_URL = "https://api-inference.huggingface.co/models/{model_id}"


def classify_text(text, labels, api_token,
                  model_id="facebook/bart-large-mnli",
                  multi_label=False):
    """
    Classify a single text string against candidate labels using the
    Hugging Face Inference API (free tier).

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
                # Model is loading — wait and retry
                wait = 10 if attempt == 0 else 20
                time.sleep(wait)
                continue

            if resp.status_code == 429:
                # Rate-limited — back off
                time.sleep(5)
                continue

            resp.raise_for_status()
            data = resp.json()

            # The API returns {"sequence": ..., "labels": [...], "scores": [...]}
            top_label = data["labels"][0]
            top_score = round(data["scores"][0], 3)
            return {"label": top_label, "confidence": top_score}

        except Exception:
            time.sleep(3)
            continue

    return {"label": "Error", "confidence": 0.0}


def classify_column(df, text_col, labels, api_token,
                    model_id="facebook/bart-large-mnli",
                    multi_label=False,
                    confidence_threshold=0.3):
    """
    Classify every value in *text_col* using the HF Inference API.

    Parameters
    ----------
    df : pd.DataFrame
    text_col : str
    labels : list[str]
    api_token : str           – Hugging Face API token (free).
    model_id : str            – HF model repo id.
    multi_label : bool
    confidence_threshold : float

    Returns
    -------
    result_df : pd.DataFrame  – original df + AI_Classification, AI_Confidence
    summary : dict
    """
    rows_before = len(df)
    classifications = []
    confidences = []

    empty_count = 0
    uncertain_count = 0
    classified_count = 0
    error_count = 0

    texts = df[text_col].fillna("").astype(str).tolist()

    for text in texts:
        if text.strip() == "":
            classifications.append("Empty")
            confidences.append(0.0)
            empty_count += 1
            continue

        result = classify_text(
            text, labels, api_token,
            model_id=model_id,
            multi_label=multi_label,
        )

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
    }
    return result_df, summary


def classification_summary(df):
    """Return a value-counts DataFrame of the AI_Classification column."""
    if "AI_Classification" not in df.columns:
        return pd.DataFrame()
    counts = df["AI_Classification"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    return counts
