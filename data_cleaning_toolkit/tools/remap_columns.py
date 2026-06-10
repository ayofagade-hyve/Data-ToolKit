"""Column remapping, merging, and splitting tools."""
import pandas as pd
from utils.io_helpers import generate_summary

def remap_columns(source_df, target_columns, mapping, defaults=None):
    defaults = defaults or {}
    result = pd.DataFrame()
    for col in target_columns:
        if col in mapping and mapping[col] in source_df.columns:
            result[col] = source_df[mapping[col]].values
        elif col in defaults:
            result[col] = defaults[col]
        else:
            result[col] = ""
    mapped_count = sum(1 for c in target_columns if c in mapping)
    default_count = sum(1 for c in target_columns if c in defaults and c not in mapping)
    summary = generate_summary("Column Remapper", len(source_df), len(result),
        extra_info={"Target columns": str(len(target_columns)), "Mapped columns": str(mapped_count),
                    "Default columns": str(default_count), "Empty columns": str(len(target_columns) - mapped_count - default_count)})
    return result, summary

def merge_columns(df, cols, separator=" ", new_col_name="Merged"):
    result = df.copy()
    result[new_col_name] = result[cols].fillna("").astype(str).apply(
        lambda row: separator.join(v for v in row if v.strip()), axis=1)
    return result

def split_column(df, col, separator, new_col_names):
    result = df.copy()
    split_data = result[col].fillna("").astype(str).str.split(separator, expand=True)
    for i, name in enumerate(new_col_names):
        if i < split_data.shape[1]:
            result[name] = split_data[i].str.strip()
        else:
            result[name] = ""
    return result
