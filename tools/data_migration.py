"""Full Data Migration Pipeline — remap, fixed values, conditional rules, classify, standardise."""
import pandas as pd
from tools.remap_columns import remap_columns
from tools.classify_jobs import classify_jobs, classify_org_types
from tools.value_standardizer import standardize_values
from utils.io_helpers import generate_summary


def append_semicolon(existing, new_value):
    """Append new_value with leading ; and ; separator. Skips duplicates."""
    existing = str(existing or "").strip()
    new_value = str(new_value or "").strip()
    if not new_value:
        return existing
    if not existing:
        return f";{new_value}"
    parts = [p.strip() for p in existing.split(";") if p.strip()]
    if new_value in parts:
        return existing
    return f"{existing};{new_value}"


def apply_conditional_rules(result_df, source_df, rules):
    """
    Apply IF / THEN / ELSE rules.
    
    IF conditions check SOURCE columns (the original input data).
    THEN/ELSE write into TARGET columns (the remapped output data).
    
    Each rule dict:
        col       — SOURCE column to check (IF column)
        operator  — 'equals', 'contains', 'not_empty', 'is_empty'
        value     — value to compare against
        out_col   — TARGET/output column to write to
        out_val   — value to write when TRUE
        else_val  — value to write when FALSE (optional)
        mode      — 'overwrite' | 'fill_blank' | 'append_semicolon'

    Returns: (result_df, applied_report_list, skipped_report_list)
    """
    result = result_df.copy()
    applied = []
    skipped = []

    for i, rule in enumerate(rules, 1):
        col = rule.get("col", "")
        operator = rule.get("operator", "equals")
        value = rule.get("value", "")
        out_col = rule.get("out_col", "")
        out_val = rule.get("out_val", "")
        else_val = rule.get("else_val", "")
        mode = rule.get("mode", "overwrite")

        if not col or not out_col:
            skipped.append({
                "Rule #": i,
                "Reason": "IF column or output column is blank",
                "Details": f"IF '{col}' -> THEN '{out_col}'"
            })
            continue

        # IF column must exist in SOURCE data
        if col not in source_df.columns:
            available = ", ".join(list(source_df.columns)[:10])
            skipped.append({
                "Rule #": i,
                "Reason": f"IF column '{col}' not found in source data",
                "Details": f"Available source columns: {available}..."
            })
            continue

        # THEN column: create in output if it doesn't exist
        if out_col not in result.columns:
            result[out_col] = ""

        # Build condition mask from SOURCE data
        series = source_df[col].fillna("").astype(str).str.strip()

        if operator == "equals":
            mask = series.str.lower() == str(value).strip().lower()
        elif operator == "contains":
            mask = series.str.lower().str.contains(str(value).strip().lower(), na=False)
        elif operator == "not_empty":
            mask = series != ""
        elif operator == "is_empty":
            mask = series == ""
        else:
            skipped.append({
                "Rule #": i,
                "Reason": f"Unknown operator '{operator}'",
                "Details": f"IF '{col}' {operator} '{value}'"
            })
            continue

        matched = int(mask.sum())
        unmatched = int((~mask).sum())

        # Apply THEN value to OUTPUT column
        if out_val:
            if mode == "overwrite":
                result.loc[mask, out_col] = out_val
            elif mode == "fill_blank":
                blank = mask & (result[out_col].fillna("").astype(str).str.strip() == "")
                result.loc[blank, out_col] = out_val
            elif mode == "append_semicolon":
                result.loc[mask, out_col] = result.loc[mask, out_col].apply(
                    lambda x: append_semicolon(x, out_val))

        # Apply ELSE value to OUTPUT column
        if else_val:
            if mode == "overwrite":
                result.loc[~mask, out_col] = else_val
            elif mode == "fill_blank":
                blank = (~mask) & (result[out_col].fillna("").astype(str).str.strip() == "")
                result.loc[blank, out_col] = else_val
            elif mode == "append_semicolon":
                result.loc[~mask, out_col] = result.loc[~mask, out_col].apply(
                    lambda x: append_semicolon(x, else_val))

        applied.append({
            "Rule #": i,
            "Condition": f"IF source '{col}' {operator} '{value}'",
            "THEN": f"output '{out_col}' = '{out_val}'",
            "ELSE": f"output '{out_col}' = '{else_val}'" if else_val else "(no else)",
            "Mode": mode,
            "Rows matched": f"{matched:,}",
            "Rows unmatched": f"{unmatched:,}",
        })

    return result, applied, skipped


def split_suppression(df, suppression_rules):
    """
    Split dataframe into normal rows and suppression/opt-out rows.
    Returns: (normal_df, suppressed_df, info_dict)
    """
    if not suppression_rules:
        return df, pd.DataFrame(columns=df.columns), {"Suppressed": "0"}

    combined_mask = pd.Series([False] * len(df), index=df.index)

    for rule in suppression_rules:
        col = rule.get("col", "")
        operator = rule.get("operator", "equals")
        value = rule.get("value", "")
        if col not in df.columns:
            continue
        series = df[col].fillna("").astype(str).str.strip()
        if operator == "equals":
            mask = series.str.lower() == str(value).strip().lower()
        elif operator == "contains":
            mask = series.str.lower().str.contains(str(value).strip().lower(), na=False)
        elif operator == "not_empty":
            mask = series != ""
        else:
            continue
        combined_mask = combined_mask | mask

    suppressed = df[combined_mask].copy().reset_index(drop=True)
    normal = df[~combined_mask].copy().reset_index(drop=True)
    return normal, suppressed, {"Suppressed": f"{len(suppressed):,}", "Kept": f"{len(normal):,}"}


def run_migration(source_df, target_columns, column_mapping, fixed_values=None,
                  conditional_rules=None, classify=True, title_col_name=None,
                  standardize_configs=None, suppression_rules=None):
    """
    Complete migration pipeline:
    1. Remap columns (source -> target structure)
    2. Apply fixed (static) values
    3. Apply conditional IF/THEN/ELSE rules (on TARGET columns)
    4. Auto-classify seniority / job function / org type
    5. Standardise values against user rules
    6. Split suppression/opt-out rows into separate output

    Returns: (result, suppressed, std_reports_df, rule_applied, rule_skipped, summary)
    """
    fixed_values = fixed_values or {}
    conditional_rules = conditional_rules or []
    standardize_configs = standardize_configs or []
    suppression_rules = suppression_rules or []
    steps = []

    # Step 1: Remap columns
    result, _ = remap_columns(source_df, target_columns, column_mapping, fixed_values)
    mapped_count = sum(1 for tc in target_columns if column_mapping.get(tc))
    fixed_count = sum(1 for v in fixed_values.values() if v)
    steps.append(f"Column mapping ({mapped_count} mapped, {fixed_count} fixed)")

    # Step 2: Conditional rules (TARGET columns)
    rule_applied = []
    rule_skipped = []
    if conditional_rules:
        result, rule_applied, rule_skipped = apply_conditional_rules(result, source_df, conditional_rules)
        steps.append(f"Conditional rules ({len(rule_applied)} applied, {len(rule_skipped)} skipped)")

    # Step 3: Auto-classify
    if classify and title_col_name and title_col_name in result.columns:
        result, _ = classify_jobs(result, title_col_name)
        result, _ = classify_org_types(result)
        steps.append("Auto-classification (seniority, function, org type)")

    # Step 4: Standardise values
    std_reports = []
    for cfg in standardize_configs:
        col = cfg["col"]
        if col in result.columns:
            result, report, _ = standardize_values(
                result, col, cfg["standards_df"], cfg["standard_col"],
                cfg.get("aliases_col"), cfg.get("threshold", 80))
            std_reports.append((col, report))
            steps.append(f"Standardised: {col}")

    # Step 5: Split suppression
    suppressed = pd.DataFrame(columns=result.columns)
    if suppression_rules:
        result, suppressed, sup_info = split_suppression(result, suppression_rules)
        steps.append(f"Suppression split ({sup_info['Suppressed']} separated)")

    all_std_reports = pd.concat(
        [r.assign(Column=c) for c, r in std_reports], ignore_index=True
    ) if std_reports else pd.DataFrame()

    extra = {"Steps": " -> ".join(steps)}
    summary = generate_summary("Full Data Migration", len(source_df), len(result), extra_info=extra)

    return result, suppressed, all_std_reports, rule_applied, rule_skipped, summary