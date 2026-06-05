"""AI Column Classifier — zero-shot classification via Hugging Face Transformers."""

import pandas as pd


def classify_column(df, text_col, labels, classifier,
                    multi_label=False,
                    hypothesis_template="This text is about {}.",
                    confidence_threshold=0.3):
    """
    Classify every value in *text_col* into one of *labels* using a
    Hugging Face zero-shot-classification pipeline.

    Parameters
    ----------
    df : pd.DataFrame
        The source data.
    text_col : str
        Name of the column whose values will be classified.
    labels : list[str]
        Candidate class labels (e.g. ["Tech", "Finance", "Healthcare"]).
    classifier : transformers.Pipeline
        A preloaded ``pipeline("zero-shot-classification", …)`` object.
    multi_label : bool
        If True each label is scored independently (scores won't sum to 1).
    hypothesis_template : str
        Template used internally by the model.  Must contain ``{}``.
    confidence_threshold : float
        Rows whose top score falls below this value are prefixed "Uncertain".

    Returns
    -------
    result_df : pd.DataFrame
        Original dataframe with two new columns:
        ``AI_Classification`` and ``AI_Confidence``.
    summary : dict
        Metrics dict compatible with the toolkit's ``show_summary()`` helper.
    """
    rows_before = len(df)
    classifications = []
    confidences = []

    empty_count = 0
    uncertain_count = 0
    classified_count = 0

    texts = df[text_col].fillna("").astype(str).tolist()

    for text in texts:
        if text.strip() == "":
            classifications.append("Empty")
            confidences.append(0.0)
            empty_count += 1
            continue

        result = classifier(
            text,
            candidate_labels=labels,
            multi_label=multi_label,
            hypothesis_template=hypothesis_template,
        )
        top_label = result["labels"][0]
        top_score = round(result["scores"][0], 3)

        if top_score < confidence_threshold:
            classifications.append(f"Uncertain ({top_label})")
            confidences.append(top_score)
            uncertain_count += 1
        else:
            classifications.append(top_label)
            confidences.append(top_score)
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
    }
    return result_df, summary


def classification_summary(df):
    """Return a value-counts DataFrame of the AI_Classification column."""
    if "AI_Classification" not in df.columns:
        return pd.DataFrame()
    counts = df["AI_Classification"].value_counts().reset_index()
    counts.columns = ["Category", "Count"]
    return counts
