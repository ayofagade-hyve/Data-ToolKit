"Data Cleaning & File Automation Toolkit — Streamlit App (18 tools + conditional rules)."

import streamlit as st
import pandas as pd
from utils.io_helpers import load_csv, to_csv_bytes, generate_summary

st.set_page_config(page_title="Data Cleaning Toolkit", page_icon="\U0001f9f9", layout="wide")

# Sorted alphabetically (after Home)
TOOLS = [
    "\U0001f3e0 Home",
    "\U0001f3e2 Classify Organisation Type",
    "\U0001f4bc Classify Seniority & Job Function",
    "\U0001f500 Column Remapper",
    "\U0001f4ce Combine CSVs",
    "\u2696\ufe0f Compare & Remove",
    "\U0001f50d Deduplicate vs Master List",
    "\U0001f310 Extract Company Domains",
    "\U0001f524 Fix Encoding (Mojibake)",
    "\U0001f504 Full Data Migration",
    "\U0001f501 Fuzzy Duplicate Finder",
    "\U0001f50e LinkedIn Search Links",
    "\U0001f517 Merge / Split Columns",
    "\U0001f6ab Remove by Keywords / Flag",
    "\U0001f9f9 Remove Blank Rows",
    "\U0001f464 Standardise Names",
    "\U0001f4de Standardise Phone Numbers",
    "\U0001f517 Standardise URLs",
    "\U0001f3af Value Standardiser",
]

tool = st.sidebar.radio("Choose a tool", TOOLS)


# ──────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────

def show_summary(s):
    cols = st.columns(3)
    cols[0].metric("Rows before", s.get("Rows before", ""))
    cols[1].metric("Rows after", s.get("Rows after", ""))
    cols[2].metric("Removed / changed", s.get("Rows removed / changed", ""))
    for k, v in s.items():
        if k not in ("Tool", "Rows before", "Rows after", "Rows removed / changed"):
            st.info(f"**{k}:** {v}")


def dl(df, label, filename):
    st.download_button(f"\u2b07\ufe0f Download {label}", to_csv_bytes(df), filename, "text/csv")


def get_target_columns(key_prefix):
    "Let user either upload a template CSV or type column names manually."
    method = st.radio(
        "How do you want to define your output columns?",
        ["Upload a template CSV (uses its headers)", "Type column names manually"],
        key=f"{key_prefix}_method",
    )
    if method.startswith("Upload"):
        tgt_f = st.file_uploader(
            "Upload template CSV (just headers is fine)", type="csv",
            key=f"{key_prefix}_tgt",
        )
        if tgt_f:
            tgt = load_csv(tgt_f)
            return list(tgt.columns)
        return None
    else:
        raw = st.text_input(
            "Enter your output column names (comma-separated)",
            placeholder="e.g. First Name, Last Name, Email, Company, Job Title, Country",
            key=f"{key_prefix}_manual",
        )
        if raw.strip():
            return [c.strip() for c in raw.split(",") if c.strip()]
        return None


# ══════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════

if tool == TOOLS[0]:
    st.title("\U0001f9f9 Data Cleaning & File Automation Toolkit")
    st.markdown("""
Welcome! This toolkit gives you **18 powerful data-cleaning tools** in one simple web app.
No coding needed — just upload your CSV, pick a tool, configure it, and download clean results.
""")

# ══════════════════════════════════════════════════════════
# Classify Organisation Type
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[1]:
    st.header("\U0001f3e2 Classify Organisation Type")
    st.markdown("""**What it does:** Automatically tags each company with an organisation type based on
industry, company name, job titles, and other available fields.""")

# ══════════════════════════════════════════════════════════
# Classify Seniority & Job Function
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[2]:
    st.header("\U0001f4bc Classify Seniority & Job Function")
    st.markdown("""**What it does:** Reads each person's job title and automatically assigns:
- **Seniority level:** C-level, VP level, Director, Manager, Associate, or Other
- **Job function:** Sales, Marketing, IT, Finance, Legal, HR, Operations, Product, etc.""")

# ══════════════════════════════════════════════════════════
# Column Remapper
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[3]:
    st.header("\U0001f500 Column Remapper")
    st.markdown("""**What it does:** Maps columns from a source CSV into a different output structure.
For each output column, you pick which source column fills it — or set a custom default value.
Columns with matching names are auto-matched.""")

# ══════════════════════════════════════════════════════════
# Combine CSVs
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[4]:
    st.header("\U0001f4ce Combine CSVs")
    st.markdown("""**What it does:** Merges multiple CSV files into a single file, stacking all rows together.""")

# ══════════════════════════════════════════════════════════
# Compare & Remove
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[5]:
    st.header("\u2696\ufe0f Compare & Remove")
    st.markdown("""**What it does:** Compares a column in your source file against a column in a lookup file,
and removes any rows from the source that have a match in the lookup.""")

# ══════════════════════════════════════════════════════════
# Deduplicate vs Master List
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[6]:
    st.header("\U0001f50d Deduplicate vs Master List")
    st.markdown("""**What it does:** Compares a new contact list against your master database and removes
anyone who already exists. Matches on **4 keys** (in order):
1. **Email** (exact match)
2. **LinkedIn URL** (normalised match)
3. **First Name + Last Name + Company** (exact match)
4. **First Name + Last Name + Website** (exact match)""")

# ══════════════════════════════════════════════════════════
# Extract Company Domains
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[7]:
    st.header("\U0001f310 Extract Company Domains")
    st.markdown("""**What it does:** Extracts the email domain for each company by finding the most common
non-personal domain among all contacts at that company. Ignores personal domains like
gmail.com, yahoo.com, hotmail.com.""")

# ══════════════════════════════════════════════════════════
# Fix Encoding (Mojibake)
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[8]:
    st.header("\U0001f524 Fix Encoding (Mojibake)")
    st.markdown("""**What it does:** Repairs garbled/broken characters caused by encoding mismatches.
Fixes things like Ã© → é, Ã¼ → ü, Ã± → ñ.""")

# ══════════════════════════════════════════════════════════
# Full Data Migration  ← REWRITTEN with Conditional Rules
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[9]:
    st.header("\U0001f504 Full Data Migration")

    st.markdown("""
**What it does:** Transforms your raw data into a clean, ready-to-use format — all in one go.

Think of it as an assembly line with **5 steps**:

| Step | What happens | Example |
|------|-------------|---------|
| **1. Column Mapping** | Match your source columns to your output columns | *"Company Name" → "Organisation"* |
| **2. Fixed Values** | Set columns that should be the same on every row | *Brand = "Fintech Meetup"* |
| **3. Conditional Rules** | Set values based on IF / THEN / ELSE logic | *IF Country = "UK" → Source = "UK List", ELSE Source = "International"* |
| **4. Auto-Classification** | Auto-tag seniority, job function & org type | *"VP of Sales" → Seniority: VP, Function: Sales* |
| **5. Standardisation** | Clean messy values against your own reference lists | *"acountant" → "Accountant"* |

**Real-world example:** You receive a raw attendee export from an event. You need to
remap it into your CRM format, tag everyone from the UK as "Domestic" and everyone else
as "International", auto-classify their job titles, and standardise company names.
This tool does all of that in a single click.
""")

    st.divider()

    # ── Upload source CSV ──
    src_f = st.file_uploader("Upload your source CSV", type="csv", key="mig_src")
    if src_f:
        src_df = load_csv(src_f)
        src_cols = list(src_df.columns)
        st.success(f"Source loaded: **{len(src_df):,} rows** × **{len(src_cols)} columns**")
        st.dataframe(src_df.head(5), use_container_width=True)

        # ── Define output columns ──
        tgt_cols = get_target_columns("mig")

        if tgt_cols:
            st.divider()

            # ────────────────────────────────────────
            # STEP 1 — Column Mapping
            # ────────────────────────────────────────
            st.subheader("Step 1 \U0001f500 Column Mapping")
            st.caption("For each output column, pick which source column it should pull data from.")

            col_mapping = {}
            src_lower = {c.lower(): c for c in src_cols}
            for tc in tgt_cols:
                auto = src_lower.get(tc.lower())
                options = ["-- leave empty --"] + src_cols
                idx = options.index(auto) if auto else 0
                choice = st.selectbox(
                    f"**{tc}** ←", options, index=idx, key=f"mig_map_{tc}"
                )
                if choice != "-- leave empty --":
                    col_mapping[tc] = choice

            st.divider()

            # ────────────────────────────────────────
            # STEP 2 — Fixed Values
            # ────────────────────────────────────────
            st.subheader("Step 2 \U0001f4cc Fixed Values")
            st.caption("Set a value that will be the same on **every** row (e.g. Brand, Event Name, Source).")

            fixed_values = {}
            with st.expander("\u2795 Set fixed values"):
                for tc in tgt_cols:
                    val = st.text_input(
                        f"Fixed value for **{tc}**",
                        key=f"mig_fix_{tc}",
                        placeholder="Leave blank to skip",
                    )
                    if val.strip():
                        fixed_values[tc] = val.strip()

            st.divider()

            # ────────────────────────────────────────
            # STEP 3 — Conditional Rules  ← NEW
            # ────────────────────────────────────────
            st.subheader("Step 3 \U0001f9e9 Conditional Rules")
            st.caption(
                "Set column values based on conditions. "
                "For example: *IF Country equals 'UK' → set Source = 'Domestic', otherwise 'International'*."
            )

            CONDITIONS = [
                "equals",
                "not equals",
                "contains",
                "does not contain",
                "starts with",
                "is blank",
                "is not blank",
            ]

            conditional_rules = []

            with st.expander("\u2795 Add Conditional Rules"):
                num_rules = st.number_input(
                    "How many rules do you need?", min_value=0, max_value=20, value=0,
                    key="mig_num_rules",
                )

                for i in range(int(num_rules)):
                    st.markdown(f"---")
                    st.markdown(f"**Rule {i + 1}**")

                    # Row 1 — Condition
                    c1, c2, c3 = st.columns(3)
                    r_col = c1.selectbox(
                        "IF column", src_cols, key=f"mig_rcol_{i}",
                    )
                    r_cond = c2.selectbox(
                        "condition", CONDITIONS, key=f"mig_rcond_{i}",
                    )
                    value_disabled = r_cond in ("is blank", "is not blank")
                    r_val = c3.text_input(
                        "value",
                        key=f"mig_rval_{i}",
                        disabled=value_disabled,
                        placeholder="(not needed)" if value_disabled else "e.g. UK",
                    )

                    # Row 2 — Output
                    c4, c5, c6 = st.columns(3)
                    r_out_col = c4.selectbox(
                        "THEN set column", tgt_cols, key=f"mig_routcol_{i}",
                    )
                    r_out_val = c5.text_input(
                        "to value", key=f"mig_routval_{i}",
                        placeholder="e.g. Fintech Meetup UK",
                    )
                    r_fb = c6.text_input(
                        "ELSE set to (optional)", key=f"mig_rfb_{i}",
                        placeholder="Leave blank to skip non-matches",
                        help="If left empty, rows that don't match the condition won't be changed.",
                    )

                    # Build rule dict
                    rule = {
                        "column": r_col,
                        "condition": r_cond,
                        "value": r_val,
                        "output_column": r_out_col,
                        "output_value": r_out_val,
                        "fallback_value": r_fb,
                    }
                    conditional_rules.append(rule)

                    # Plain-English summary
                    if value_disabled:
                        eng = f"\U0001f4a1 **Rule {i+1}:** IF *{r_col}* **{r_cond}** → set *{r_out_col}* = `{r_out_val}`"
                    else:
                        eng = f"\U0001f4a1 **Rule {i+1}:** IF *{r_col}* **{r_cond}** `{r_val}` → set *{r_out_col}* = `{r_out_val}`"
                    if r_fb:
                        eng += f", otherwise set *{r_out_col}* = `{r_fb}`"
                    st.info(eng)

            # Show summary of all rules outside the expander
            if conditional_rules:
                st.markdown(f"**{len(conditional_rules)} conditional rule(s) configured.**")

            st.divider()

            # ────────────────────────────────────────
            # STEP 4 — Auto-Classification
            # ────────────────────────────────────────
            st.subheader("Step 4 \U0001f916 Auto-Classification")
            st.caption("Automatically tag seniority, job function, and organisation type from job titles.")

            do_classify = st.checkbox("Enable auto-classification", value=True, key="mig_classify")
            title_col = None
            if do_classify:
                title_col = st.selectbox(
                    "Which column contains the job title?",
                    ["-- select --"] + tgt_cols,
                    key="mig_title_col",
                )
                if title_col == "-- select --":
                    title_col = None

            st.divider()

            # ────────────────────────────────────────
            # STEP 5 — Standardisation (optional)
            # ────────────────────────────────────────
            st.subheader("Step 5 \U0001f3af Standardisation (optional)")
            st.caption("Clean messy values by matching them against your own reference lists.")

            standardize_configs = []
            with st.expander("\u2795 Add standardisation rules"):
                num_std = st.number_input(
                    "How many columns to standardise?", 0, 10, 0, key="mig_num_std",
                )
                for j in range(int(num_std)):
                    st.markdown(f"---")
                    st.markdown(f"**Standardise column {j + 1}**")
                    std_col = st.selectbox(
                        "Column to standardise", tgt_cols, key=f"mig_stdcol_{j}",
                    )
                    std_file = st.file_uploader(
                        "Upload standards CSV", type="csv", key=f"mig_stdf_{j}",
                    )
                    if std_file:
                        std_df = load_csv(std_file)
                        std_col_name = st.selectbox(
                            "Standard value column", list(std_df.columns), key=f"mig_stdcn_{j}",
                        )
                        alias_col_name = st.selectbox(
                            "Aliases column (optional)",
                            ["-- none --"] + list(std_df.columns),
                            key=f"mig_stdan_{j}",
                        )
                        threshold = st.slider(
                            "Fuzzy match threshold %", 50, 100, 80, key=f"mig_stdth_{j}",
                        )
                        standardize_configs.append({
                            "col": std_col,
                            "standards_df": std_df,
                            "standard_col": std_col_name,
                            "aliases_col": alias_col_name if alias_col_name != "-- none --" else None,
                            "threshold": threshold,
                        })

            st.divider()

            # ────────────────────────────────────────
            # RUN MIGRATION
            # ────────────────────────────────────────
            st.subheader("\U0001f680 Run Migration")

            # Show a quick summary of what will happen
            st.markdown("**Pipeline summary:**")
            pipeline_items = ["Column mapping"]
            if fixed_values:
                pipeline_items.append(f"Fixed values ({len(fixed_values)})")
            if conditional_rules:
                pipeline_items.append(f"Conditional rules ({len(conditional_rules)})")
            if do_classify and title_col:
                pipeline_items.append("Auto-classification")
            if standardize_configs:
                pipeline_items.append(f"Standardisation ({len(standardize_configs)} columns)")
            st.write(" → ".join(pipeline_items))

            if st.button("\u25b6\ufe0f Run Full Data Migration", type="primary", key="mig_run"):
                from tools.data_migration import run_migration

                with st.spinner("Running migration pipeline..."):
                    result_df, reports_df, summary = run_migration(
                        source_df=src_df,
                        target_columns=tgt_cols,
                        column_mapping=col_mapping,
                        fixed_values=fixed_values,
                        conditional_rules=conditional_rules if conditional_rules else None,
                        classify=do_classify,
                        title_col_name=title_col,
                        standardize_configs=standardize_configs if standardize_configs else None,
                    )

                st.success("Migration complete!")
                show_summary(summary)

                st.subheader("Output Preview")
                st.dataframe(result_df.head(20), use_container_width=True)

                dl(result_df, "migrated data", "migrated_data.csv")

                if not reports_df.empty:
                    st.subheader("Standardisation Report")
                    st.dataframe(reports_df, use_container_width=True)
                    dl(reports_df, "standardisation report", "standardisation_report.csv")


# ══════════════════════════════════════════════════════════
# Fuzzy Duplicate Finder
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[10]:
    st.header("\U0001f501 Fuzzy Duplicate Finder")
    st.markdown("""**What it does:** Scans a single column for near-duplicate values using fuzzy string
matching (Levenshtein distance). Flags each row as "Unique" or "Duplicate" with the
match percentage and which row it matched against.""")

# ══════════════════════════════════════════════════════════
# LinkedIn Search Links
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[11]:
    st.header("\U0001f50e LinkedIn Search Links")
    st.markdown("""**What it does:** Generates a clickable LinkedIn people-search URL for each person,
using their name, job title, and company as search keywords.""")

# ══════════════════════════════════════════════════════════
# Merge / Split Columns
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[12]:
    st.header("\U0001f517 Merge / Split Columns")
    st.markdown("""**What it does:** Two modes:
- **Merge:** Combine 2+ columns into one new column with a separator
- **Split:** Break one column into multiple new columns on a separator""")

# ══════════════════════════════════════════════════════════
# Remove by Keywords / Flag
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[13]:
    st.header("\U0001f6ab Remove by Keywords / Flag")
    st.markdown("""**What it does:** Two modes:
- **Keywords mode:** Removes rows where a column contains any of your specified keywords
- **Flag mode:** Removes rows where a column exactly equals a flag value""")

# ══════════════════════════════════════════════════════════
# Remove Blank Rows
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[14]:
    st.header("\U0001f9f9 Remove Blank Rows")
    st.markdown("""**What it does:** Deletes rows that are completely empty or contain only whitespace.""")

# ══════════════════════════════════════════════════════════
# Standardise Names
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[15]:
    st.header("\U0001f464 Standardise Names")
    st.markdown("""**What it does:** Splits a "Full Name" column into separate "First Name" and "Last Name" columns.""")

# ══════════════════════════════════════════════════════════
# Standardise Phone Numbers
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[16]:
    st.header("\U0001f4de Standardise Phone Numbers")
    st.markdown("""**What it does:** Strips all formatting from phone numbers, keeping only digits and the + symbol.""")

# ══════════════════════════════════════════════════════════
# Standardise URLs
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[17]:
    st.header("\U0001f517 Standardise URLs")
    st.markdown("""**What it does:** Normalises URLs by removing http://, https://, www., and trailing slashes.""")

# ══════════════════════════════════════════════════════════
# Value Standardiser
# ══════════════════════════════════════════════════════════

elif tool == TOOLS[18]:
    st.header("\U0001f3af Value Standardiser")
    st.markdown("""**What it does:** Matches raw, messy values in your data against a list of standard terms
you define. Uses three matching strategies in order:
1. **Exact match** (case-insensitive) — "accountant" matches "Accountant" → 100%
2. **Keyword match** — "senior auditor" contains "auditor" (an alias) → 90%
3. **Fuzzy match** (Levenshtein) — "acountant" is close to "Accountant" → 89%""")
