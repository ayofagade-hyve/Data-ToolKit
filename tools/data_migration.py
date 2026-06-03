import pandas as pd
from tools.remap_columns import remap_columns
from tools.classify_jobs import classify_jobs, classify_org_types
from tools.value_standardizer import standardize_values
from utils.io_helpers import generate_summary


# ──────────────────────────────────────────────
# Conditional Rules Engine
# ──────────────────────────────────────────────

def apply_conditional_rules(df, rules):
    """
    Apply IF / THEN / ELSE rules to a DataFrame.

    Each rule is a dict:
        column          – source column to check
        condition       – one of: equals, not equals, contains, does not contain,
                          starts with, is blank, is not blank
        value           – the value to compare against (ignored for is blank / is not blank)
        output_column   – the column to write the result into
        output_value    – value to set when the condition is TRUE
        fallback_value  – value to set when the condition is FALSE (if empty, row is left unchanged)
    """
    result = df.copy()

    for rule in rules:
        col   = rule.get("column", "")
        cond  = rule.get("condition", "")
        val   = str(rule.get("value", "")).strip()
        o_col = rule.get("output_column", "")
        o_val = rule.get("output_value", "")
        fb    = rule.get("fallback_value", "")

        if not col or not o_col or col not in result.columns:
            continue

        series = result[col].fillna("").astype(str)

        # Build boolean mask
        if cond == "equals":
            mask = series.str.lower() == val.lower()
        elif cond == "not equals":
            mask = series.str.lower() != val.lower()
        elif cond == "contains":
            mask = series.str.lower().str.contains(val.lower(), na=False)
        elif cond == "does not contain":
            mask = ~series.str.lower().str.contains(val.lower(), na=False)
        elif cond == "starts with":
            mask = series.str.lower().str.startswith(val.lower())
        elif cond == "is blank":
            mask = series.str.strip() == ""
        elif cond == "is not blank":
            mask = series.str.strip() != ""
        else:
            continue

        # Apply output value where condition is met
        result.loc[mask, o_col] = o_val

        # Apply fallback where condition is NOT met (only if a fallback was given)
        if fb:
            result.loc[~mask, o_col] = fb

    return result


# ──────────────────────────────────────────────
# Full Migration Pipeline
# ──────────────────────────────────────────────

def run_migration(source_df, target_columns, column_mapping, fixed_values=None,
                  conditional_rules=None, classify=True, title_col_name=None,
                  standardize_configs=None):
    """
    Complete migration pipeline:
      1. Remap columns
      2. Apply fixed (static) values
      3. Apply conditional rules  ← NEW
      4. Auto-classify seniority / job function / org type
      5. Standardise values
    """
    fixed_values        = fixed_values or {}
    conditional_rules   = conditional_rules or []
    standardize_configs = standardize_configs or []

    # Step 1 — Column remapping (+ fixed values are injected here)
    result, _ = remap_columns(source_df, target_columns, column_mapping, fixed_values)
    steps = ["Column remapping"]

    # Step 2 — Conditional rules
    if conditional_rules:
        result = apply_conditional_rules(result, conditional_rules)
        steps.append(f"Conditional rules ({len(conditional_rules)} rules)")

    # Step 3 — Auto-classification
    if classify and title_col_name and title_col_name in result.columns:
        result, _ = classify_jobs(result, title_col_name)
        result, _ = classify_org_types(result)
        steps.append("Auto-classification")

    # Step 4 — Value standardisation
    std_reports = []
    for cfg in standardize_configs:
        col = cfg["col"]
        if col in result.columns:
            result, report, _ = standardize_values(
                result, col, cfg["standards_df"],
                cfg["standard_col"], cfg.get("aliases_col"),
                cfg.get("threshold", 80),
            )
            std_reports.append((col, report))
            steps.append(f"Standardised: {col}")

    all_reports = (
        pd.concat([r.assign(Column=c) for c, r in std_reports], ignore_index=True)
        if std_reports
        else pd.DataFrame()
    )

    extra = {"Steps": ", ".join(steps)}
    if fixed_values:
        extra["Fixed values"] = ", ".join(
            f"{k}={v}" for k, v in fixed_values.items() if v
        )
    if conditional_rules:
        extra["Conditional rules"] = f"{len(conditional_rules)} rule(s) applied"

    summary = generate_summary(
        "Data Migration Pipeline", len(source_df), len(result), extra_info=extra
    )
    return result, all_reports, summary
