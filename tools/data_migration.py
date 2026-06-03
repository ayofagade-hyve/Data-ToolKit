import pandas as pd
from tools.remap_columns import remap_columns
from tools.classify_jobs import classify_jobs, classify_org_types
from tools.value_standardizer import standardize_values
from utils.io_helpers import generate_summary

def run_migration(source_df, target_columns, column_mapping, fixed_values=None,
                  classify=True, title_col_name=None, standardize_configs=None):
    fixed_values = fixed_values or {}; standardize_configs = standardize_configs or []
    result, _ = remap_columns(source_df, target_columns, column_mapping, fixed_values)
    steps = ["Column remapping"]
    if classify and title_col_name and title_col_name in result.columns:
        result, _ = classify_jobs(result, title_col_name)
        result, _ = classify_org_types(result)
        steps.append("Auto-classification")
    std_reports = []
    for cfg in standardize_configs:
        col = cfg["col"]
        if col in result.columns:
            result, report, _ = standardize_values(result, col, cfg["standards_df"],
                cfg["standard_col"], cfg.get("aliases_col"), cfg.get("threshold", 80))
            std_reports.append((col, report))
            steps.append(f"Standardised: {col}")
    all_reports = pd.concat([r.assign(Column=c) for c,r in std_reports], ignore_index=True) if std_reports else pd.DataFrame()
    extra = {"Steps": ", ".join(steps)}
    if fixed_values: extra["Fixed values"] = ", ".join(f"{k}={v}" for k,v in fixed_values.items() if v)
    summary = generate_summary("Data Migration Pipeline", len(source_df), len(result), extra_info=extra)
    return result, all_reports, summary
