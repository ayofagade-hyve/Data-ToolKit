"""Formula Engine — executes parsed commands on DataFrames."""
import re
import pandas as pd
from utils.nl_parser import ParsedCommand


def execute_command(df: pd.DataFrame, cmd: ParsedCommand) -> tuple:
    """Execute a parsed command on a DataFrame.
    
    Args:
        df: Input DataFrame
        cmd: ParsedCommand from the parser
    
    Returns:
        Tuple of (result_df, description_str, rows_affected_int)
    """
    result = df.copy()
    before = len(result)
    action = cmd.action
    col = cmd.column
    val = cmd.value
    
    # Helper: build a boolean mask for row conditions
    def _build_mask(series, condition, value):
        s = series.fillna("").astype(str).str.strip()
        if condition == "contains":
            return s.str.contains(value, case=False, regex=False, na=False)
        elif condition == "equals":
            return s.str.lower() == value.lower()
        elif condition == "is_empty":
            return s == ""
        elif condition == "not_empty":
            return s != ""
        elif condition == "starts_with":
            return s.str.lower().str.startswith(value.lower())
        elif condition == "ends_with":
            return s.str.lower().str.endswith(value.lower())
        return pd.Series([False] * len(s), index=s.index)
    
    try:
        # ── REMOVE ROWS ──
        if action == "remove_rows":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            mask = _build_mask(result[col], cmd.condition, val)
            removed = int(mask.sum())
            result = result[~mask].copy()
            desc = f"🗑️ Removed **{removed:,}** rows where **{col}** {cmd.condition} \"{val}\""
            if cmd.condition in ("is_empty", "not_empty"):
                desc = f"🗑️ Removed **{removed:,}** rows where **{col}** {cmd.condition.replace('_', ' ')}"
            return result, desc, removed
        
        # ── KEEP ROWS ──
        elif action == "keep_rows":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            mask = _build_mask(result[col], cmd.condition, val)
            kept = int(mask.sum())
            removed = before - kept
            result = result[mask].copy()
            desc = f"✅ Kept **{kept:,}** rows where **{col}** {cmd.condition} \"{val}\" (removed {removed:,})"
            return result, desc, removed
        
        # ── REPLACE VALUES ──
        elif action == "replace_values":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            series = result[col].fillna("").astype(str)
            count = int(series.str.contains(val, case=False, regex=False, na=False).sum())
            pattern = re.compile(re.escape(val), re.IGNORECASE)
            result[col] = series.apply(lambda x: pattern.sub(cmd.value2, x))
            desc = f"🔄 Replaced \"{val}\" with \"{cmd.value2}\" in **{col}** — **{count:,}** cells changed"
            return result, desc, count
        
        # ── DELETE COLUMN ──
        elif action == "delete_column":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            result = result.drop(columns=[col])
            desc = f"🗑️ Deleted column **{col}** ({before:,} rows unchanged)"
            return result, desc, 0
        
        # ── FILL BLANKS ──
        elif action == "fill_blanks":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            series = result[col].fillna("").astype(str).str.strip()
            blanks = int((series == "").sum())
            result.loc[series == "", col] = val
            desc = f"📝 Filled **{blanks:,}** blank cells in **{col}** with \"{val}\""
            return result, desc, blanks
        
        # ── CHANGE CASE ──
        elif action == "change_case":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            series = result[col].fillna("").astype(str)
            mode = cmd.case_mode
            if mode == "upper":
                result[col] = series.str.upper()
                desc = f"🔠 Converted **{col}** to UPPER CASE"
            elif mode == "lower":
                result[col] = series.str.lower()
                desc = f"🔡 Converted **{col}** to lower case"
            elif mode == "title":
                result[col] = series.str.title()
                desc = f"🔤 Converted **{col}** to Title Case"
            elif mode == "sentence":
                result[col] = series.apply(
                    lambda x: ". ".join(s.strip().capitalize() for s in x.split(".") if s.strip()) if x else x
                )
                desc = f"📝 Converted **{col}** to Sentence case"
            else:
                desc = f"Changed case of **{col}**"
            return result, desc, before
        
        # ── TRIM ──
        elif action == "trim":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            original = result[col].fillna("").astype(str)
            result[col] = original.str.strip()
            changed = int((original != result[col]).sum())
            desc = f"✂️ Trimmed whitespace in **{col}** — **{changed:,}** cells changed"
            return result, desc, changed
        
        # ── SORT ──
        elif action == "sort":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            ascending = cmd.sort_order != "desc"
            result = result.sort_values(by=col, ascending=ascending, na_position="last").reset_index(drop=True)
            order_label = "A→Z" if ascending else "Z→A"
            desc = f"📊 Sorted by **{col}** ({order_label})"
            return result, desc, 0
        
        # ── REMOVE DUPLICATES ──
        elif action == "remove_dupes":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            before_len = len(result)
            result = result.drop_duplicates(subset=[col], keep="first").reset_index(drop=True)
            removed = before_len - len(result)
            desc = f"🧹 Removed **{removed:,}** duplicate rows based on **{col}** (kept first occurrence)"
            return result, desc, removed
        
        # ── ADD COLUMN ──
        elif action == "add_column":
            result[col] = val
            desc = f"➕ Added column **{col}** with value \"{val}\" ({before:,} rows)"
            return result, desc, 0
        
        # ── RENAME COLUMN ──
        elif action == "rename_column":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            result = result.rename(columns={col: val})
            desc = f"✏️ Renamed **{col}** → **{val}**"
            return result, desc, 0
        
        # ── EXTRACT DOMAIN ──
        elif action == "extract_domain":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            def _get_domain(email):
                email = str(email).strip().lower()
                if "@" not in email:
                    return ""
                return email.rsplit("@", 1)[1]
            result["Email Domain"] = result[col].fillna("").astype(str).apply(_get_domain)
            extracted = int((result["Email Domain"] != "").sum())
            desc = f"🌐 Extracted domains from **{col}** — **{extracted:,}** domains found"
            return result, desc, extracted
        
        # ── SPLIT COLUMN ──
        elif action == "split_column":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            delimiter = val if val and val != "space" else " "
            new_cols = cmd.extra.get("new_columns", ["Part 1", "Part 2"])
            split_data = result[col].fillna("").astype(str).str.split(delimiter, expand=True)
            for i, name in enumerate(new_cols):
                if i < split_data.shape[1]:
                    result[name] = split_data[i].str.strip()
                else:
                    result[name] = ""
            desc = f"✂️ Split **{col}** by \"{delimiter}\" into {', '.join(new_cols)}"
            return result, desc, before
        
        # ── MERGE COLUMNS ──
        elif action == "merge_columns":
            col2 = cmd.value
            new_name = cmd.value2 or "Merged"
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            if col2 not in result.columns:
                return df, f"❌ Column '{col2}' not found.", 0
            result[new_name] = (
                result[col].fillna("").astype(str).str.strip() + " " +
                result[col2].fillna("").astype(str).str.strip()
            ).str.strip()
            desc = f"🔗 Merged **{col}** + **{col2}** → **{new_name}**"
            return result, desc, before
        
        # ── COUNT ──
        elif action == "count":
            if col not in result.columns:
                return df, f"❌ Column '{col}' not found.", 0
            mask = _build_mask(result[col], cmd.condition, val)
            count = int(mask.sum())
            desc = f"📊 **{count:,}** rows where **{col}** {cmd.condition} \"{val}\" (out of {before:,} total)"
            return df, desc, count  # Don't modify the DataFrame for count
        
        else:
            return df, f"❌ Unknown action: {action}", 0
    
    except Exception as e:
        return df, f"❌ Error: {str(e)}", 0
