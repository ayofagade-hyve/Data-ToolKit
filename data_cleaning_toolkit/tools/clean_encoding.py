"""Encoding fix (mojibake) tool."""
import pandas as pd
from utils.text_cleaning import fix_mojibake_column
from utils.io_helpers import generate_summary

def clean_encoding(df, columns):
    result = df.copy()
    changes = 0
    for col in columns:
        original = result[col].fillna("").astype(str)
        fixed = fix_mojibake_column(result[col])
        changes += (original != fixed).sum()
        result[col] = fixed
    summary = generate_summary("Fix Encoding (Mojibake)", len(df), len(result),
        extra_info={"Columns processed": str(len(columns)), "Cells changed": f"{changes:,}"})
    return result, summary
