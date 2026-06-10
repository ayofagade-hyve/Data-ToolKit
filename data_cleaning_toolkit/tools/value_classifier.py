"""Manual value classification tool."""
import pandas as pd
from utils.io_helpers import generate_summary

def classify_values(df, col, mapping):
    result = df.copy()
    new_col = f"{col} (classified)"
    lower_mapping = {str(k).lower().strip(): v for k, v in mapping.items()}
    classified = []
    mapped_count = 0
    for val in result[col].fillna("").astype(str):
        key = val.lower().strip()
        if key in lower_mapping:
            classified.append(lower_mapping[key]); mapped_count += 1
        else:
            classified.append(val)
    result[new_col] = classified
    summary = generate_summary("Value Classifier", len(df), len(result),
        extra_info={"Column": col, "Values mapped": f"{mapped_count:,}", "Unique mappings": str(len(mapping))})
    return result, summary
