import pandas as pd
from utils.io_helpers import generate_summary

def remap_columns(source_df, target_columns, mapping, defaults=None):
    defaults = defaults or {}; result = pd.DataFrame(); mc = 0
    for tc in target_columns:
        sc = mapping.get(tc)
        if sc and sc in source_df.columns: result[tc] = source_df[sc].values; mc += 1
        else: result[tc] = defaults.get(tc, "")
    return result, generate_summary("Column Remapper",len(source_df),len(result),extra_info={"Target cols":len(target_columns),"Mapped":mc})

def merge_columns(df, cols, separator=" ", new_col_name="Merged"):
    r = df.copy()
    r[new_col_name] = df[cols].fillna("").astype(str).apply(lambda row: separator.join(v for v in row if v.strip()), axis=1)
    return r

def split_column(df, col, separator, new_col_names):
    r = df.copy(); splits = r[col].fillna("").astype(str).str.split(separator, n=len(new_col_names)-1, expand=True)
    for i, name in enumerate(new_col_names):
        r[name] = splits[i].str.strip() if i < splits.shape[1] else ""
    return r
