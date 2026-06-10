"""Full Data Migration — 7-stage pipeline."""
import pandas as pd
from utils.io_helpers import generate_summary
from utils.classifiers import classify_seniority, classify_job_function, classify_org_type
from utils.column_mapping import get_series, find_column


def append_semicolon(existing, new_value):
    existing = str(existing or "").strip()
    new_value = str(new_value or "").strip()
    if not new_value:
        return existing
    existing_values = [v.strip().lower() for v in existing.split(";") if v.strip()]
    if new_value.lower() in existing_values:
        return existing
    if existing:
        return f"{existing};{new_value};"
    return f";{new_value};"


def _apply_conditional_rule(df, rule):
    col = rule.get("col", "")
    operator = rule.get("operator", "equals")
    value = rule.get("value", "")
    out_col = rule.get("out_col", "")
    out_val = rule.get("out_val", "")
    else_val = rule.get("else_val", "")
    mode = rule.get("mode", "overwrite")
    if not col or not out_col or col not in df.columns:
        return df
    if out_col not in df.columns:
        df[out_col] = ""
    series = df[col].fillna("").astype(str).str.strip()
    for i in range(len(df)):
        cell = series.iloc[i]
        if operator == "equals":
            match = cell.lower() == str(value).lower()
        elif operator == "contains":
            match = str(value).lower() in cell.lower()
        elif operator == "not_empty":
            match = cell != ""
        elif operator == "is_empty":
            match = cell == ""
        else:
            match = False
        write_val = out_val if match else else_val
        if mode == "overwrite":
            if write_val:
                df.at[df.index[i], out_col] = write_val
        elif mode == "fill_blank":
            current = str(df.at[df.index[i], out_col] or "").strip()
            if not current and write_val:
                df.at[df.index[i], out_col] = write_val
        elif mode == "append_semicolon":
            if write_val:
                current = str(df.at[df.index[i], out_col] or "")
                df.at[df.index[i], out_col] = append_semicolon(current, write_val)
    return df


def split_suppression(df, suppression_rules):
    if not suppression_rules:
        return df, pd.DataFrame(), {"suppressed": 0}
    mask = pd.Series([False] * len(df), index=df.index)
    for rule in suppression_rules:
        col = rule.get("col", "")
        operator = rule.get("operator", "equals")
        value = rule.get("value", "")
        if col not in df.columns:
            continue
        series = df[col].fillna("").astype(str).str.strip()
        if operator == "equals":
            mask = mask | (series.str.lower() == str(value).lower())
        elif operator == "contains":
            mask = mask | series.str.contains(str(value), case=False, na=False, regex=False)
        elif operator == "not_empty":
            mask = mask | (series != "")
    suppressed = df[mask].copy()
    normal = df[~mask].copy()
    return normal, suppressed, {"suppressed": len(suppressed), "kept": len(normal)}


def run_migration(df, config):
    result = df.copy()
    before_count = len(result)
    # Stage 1: Column Mapping
    column_mapping = config.get("column_mapping", {})
    if column_mapping:
        mapped = pd.DataFrame()
        for target_col, source_col in column_mapping.items():
            if source_col in result.columns:
                mapped[target_col] = result[source_col].values
            else:
                mapped[target_col] = ""
        for col in result.columns:
            if col not in mapped.columns and col not in column_mapping.values():
                mapped[col] = result[col].values
        result = mapped
    # Stage 2: Fixed Values
    for col, val in config.get("fixed_values", {}).items():
        result[col] = val
    # Stage 3: Conditional Rules
    for rule in config.get("conditional_rules", []):
        result = _apply_conditional_rule(result, rule)
    # Stage 4: Auto-Classification
    ac = config.get("auto_classify", {})
    if ac.get("seniority"):
        tc = find_column(result, "job_title")
        if tc:
            result["Seniority (classified)"] = result[tc].fillna("").astype(str).apply(classify_seniority)
    if ac.get("job_function"):
        tc = find_column(result, "job_title")
        dc = find_column(result, "department")
        if tc:
            titles = result[tc].fillna("").astype(str)
            depts = result[dc].fillna("").astype(str) if dc else pd.Series([""] * len(result))
            result["Job Function (classified)"] = [classify_job_function(t, d) for t, d in zip(titles, depts)]
    if ac.get("org_type"):
        ind = get_series(result, "industry"); comp = get_series(result, "company")
        tit = get_series(result, "job_title"); web = get_series(result, "website")
        result["Organization Type (classified)"] = [classify_org_type(i, c, t, w) for i, c, t, w in zip(ind, comp, tit, web)]
    # Stage 5: Value Mapping
    for col, mapping in config.get("value_mapping", {}).items():
        if col in result.columns:
            result[col] = result[col].fillna("").astype(str).map(lambda x, m=mapping: m.get(x, m.get(x.lower(), x)))
    # Stage 6: Suppression Split
    result, suppressed, supp_info = split_suppression(result, config.get("suppression_rules", []))
    # Stage 7: Column Cleanup
    cc = config.get("column_cleanup", {})
    if cc.get("keep"):
        result = result[[c for c in cc["keep"] if c in result.columns]]
    elif cc.get("remove"):
        result = result.drop(columns=[c for c in cc["remove"] if c in result.columns], errors="ignore")
    summary = generate_summary("Full Data Migration", before_count, len(result), removed_count=len(suppressed),
        extra_info={"Suppressed rows": f"{len(suppressed):,}", "Columns in output": str(len(result.columns)), "Stages applied": "7"})
    return result, suppressed, summary
