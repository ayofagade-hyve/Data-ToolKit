"""Data Cleaning & File Automation Toolkit - Streamlit App (18 tools)."""
import streamlit as st
import pandas as pd
from utils.io_helpers import load_csv, to_csv_bytes, generate_summary

st.set_page_config(page_title="Data Cleaning Toolkit", page_icon="\U0001f9f9", layout="wide")

TOOLS = [
    "\U0001f3e0 Home",
    "\U0001f4ce Combine CSVs",
    "\U0001f524 Fix Encoding (Mojibake)",
    "\U0001f50d Deduplicate vs Master",
    "\U0001f501 Internal Fuzzy Dedup",
    "\U0001f310 Extract Domains",
    "\U0001f464 Standardise Names",
    "\U0001f4de Standardise Phones",
    "\U0001f517 Standardise Websites / LinkedIn",
    "\U0001f4bc Classify Seniority & Function",
    "\U0001f3e2 Classify Organisation Type",
    "\U0001f50e LinkedIn Search Links",
    "\U0001f9f9 Remove Blank Rows",
    "\U0001f6ab Remove by Keywords / Flag",
    "\u2696\ufe0f Compare & Remove",
    "\U0001f500 Column Remapper",
    "\U0001f517 Merge / Split Columns",
    "\U0001f3af Value Standardiser",
    "\U0001f504 Data Migration Pipeline",
]

tool = st.sidebar.radio("Choose a tool", TOOLS)

def show_summary(s):
    cols = st.columns(3)
    cols[0].metric("Rows before", s.get("Rows before",""))
    cols[1].metric("Rows after", s.get("Rows after",""))
    cols[2].metric("Removed / changed", s.get("Rows removed / changed",""))
    for k,v in s.items():
        if k not in ("Tool","Rows before","Rows after","Rows removed / changed"):
            st.info(f"**{k}:** {v}")

def dl(df, label, filename):
    st.download_button(f"Download {label}", to_csv_bytes(df), filename, "text/csv")

if tool == TOOLS[0]:
    st.title("Data Cleaning & File Automation Toolkit")
    st.markdown("**18 tools** for cleaning, deduplicating, classifying, standardising, and migrating CSV data. No coding required.")
    st.markdown("Pick a tool from the sidebar to get started.")

elif tool == TOOLS[1]:
    st.header("Combine CSVs")
    st.caption("Merge multiple CSV files into one.")
    files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True, key="combine")
    if files and st.button("Combine", key="combine_run"):
        from tools.combine_csvs import combine_csvs
        result, summary = combine_csvs(files)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "combined CSV", "combined.csv")

elif tool == TOOLS[2]:
    st.header("Fix Encoding (Mojibake)")
    st.caption("Repair garbled characters.")
    fi = st.file_uploader("Upload CSV", type="csv", key="enc")
    if fi and st.button("Fix Encoding", key="enc_run"):
        from tools.clean_encoding import clean_encoding
        df = load_csv(fi)
        result, summary = clean_encoding(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned CSV", "encoding_fixed.csv")

elif tool == TOOLS[3]:
    st.header("Deduplicate vs Master")
    st.caption("Remove rows that already exist in a master list. Matches on email, LinkedIn, name+company, name+website.")
    master_f = st.file_uploader("Upload MASTER CSV", type="csv", key="dm_master")
    check_f = st.file_uploader("Upload file to CHECK", type="csv", key="dm_check")
    if master_f and check_f and st.button("Deduplicate", key="dm_run"):
        from tools.dedupe_master import dedupe_against_master
        master = load_csv(master_f); check = load_csv(check_f)
        cleaned, removed, summary = dedupe_against_master(master, check)
        show_summary(summary)
        st.subheader("Cleaned (unique rows)")
        st.dataframe(cleaned.head(100))
        dl(cleaned, "cleaned CSV", "deduped_clean.csv")
        if len(removed):
            st.subheader("Removed rows")
            st.dataframe(removed.head(100))
            dl(removed, "removed rows", "deduped_removed.csv")

elif tool == TOOLS[4]:
    st.header("Internal Fuzzy Dedup")
    st.caption("Find fuzzy duplicates within a single file.")
    fi = st.file_uploader("Upload CSV", type="csv", key="ifd")
    if fi:
        df = load_csv(fi)
        col = st.selectbox("Column to match on", df.columns, key="ifd_col")
        threshold = st.slider("Match threshold %", 50, 100, 90, key="ifd_th")
        if st.button("Find Duplicates", key="ifd_run"):
            from tools.dedupe_internal import dedupe_within_file
            result, summary = dedupe_within_file(df, col, threshold)
            show_summary(summary)
            st.dataframe(result.head(200))
            dl(result, "results with flags", "fuzzy_dedup.csv")

elif tool == TOOLS[5]:
    st.header("Extract Domains")
    st.caption("Find the most common email domain per company.")
    fi = st.file_uploader("Upload CSV", type="csv", key="dom")
    if fi:
        df = load_csv(fi)
        email_col = st.selectbox("Email column", df.columns, key="dom_e")
        company_col = st.selectbox("Company column", df.columns, key="dom_c")
        if st.button("Extract", key="dom_run"):
            from tools.extract_domains import extract_domains
            result, missing, summary = extract_domains(df, email_col, company_col)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "with domains", "domains.csv")
            if len(missing):
                st.warning(f"{len(missing)} companies have no domain")
                dl(missing, "missing domains", "missing_domains.csv")

elif tool == TOOLS[6]:
    st.header("Standardise Names")
    st.caption("Split a full name column into First Name and Last Name.")
    fi = st.file_uploader("Upload CSV", type="csv", key="sn")
    if fi:
        df = load_csv(fi)
        col = st.selectbox("Full name column", df.columns, key="sn_col")
        if st.button("Split Names", key="sn_run"):
            from tools.standardize_data import standardize_names
            result = standardize_names(df, col)
            st.success(f"Split {len(result):,} names")
            st.dataframe(result.head(100))
            dl(result, "with split names", "names_split.csv")

elif tool == TOOLS[7]:
    st.header("Standardise Phones")
    st.caption("Strip formatting from phone numbers (keep digits and +).")
    fi = st.file_uploader("Upload CSV", type="csv", key="sp")
    if fi:
        df = load_csv(fi)
        col = st.selectbox("Phone column", df.columns, key="sp_col")
        if st.button("Clean Phones", key="sp_run"):
            from tools.standardize_data import standardize_phones
            result = standardize_phones(df, col)
            st.success(f"Cleaned {len(result):,} rows")
            st.dataframe(result.head(100))
            dl(result, "cleaned phones", "phones_clean.csv")

elif tool == TOOLS[8]:
    st.header("Standardise Websites / LinkedIn")
    fi = st.file_uploader("Upload CSV", type="csv", key="sw")
    if fi:
        df = load_csv(fi)
        mode = st.radio("What to standardise?", ["Websites", "LinkedIn URLs"], key="sw_mode")
        col = st.selectbox("Column", df.columns, key="sw_col")
        if st.button("Standardise", key="sw_run"):
            from tools.standardize_data import standardize_websites, standardize_linkedin
            result = standardize_websites(df, col) if mode == "Websites" else standardize_linkedin(df, col)
            st.success(f"Standardised {len(result):,} rows")
            st.dataframe(result.head(100))
            dl(result, "standardised", "urls_clean.csv")

elif tool == TOOLS[9]:
    st.header("Classify Seniority & Job Function")
    st.caption("Auto-classify job titles into seniority levels and job functions.")
    fi = st.file_uploader("Upload CSV", type="csv", key="cj")
    if fi:
        df = load_csv(fi)
        title_col = st.selectbox("Job title column", df.columns, key="cj_title")
        sen_col = st.selectbox("Existing seniority column (optional)", ["-- None --"] + list(df.columns), key="cj_sen")
        dept_col = st.selectbox("Department column (optional)", ["-- None --"] + list(df.columns), key="cj_dept")
        if st.button("Classify", key="cj_run"):
            from tools.classify_jobs import classify_jobs
            sc = sen_col if sen_col != "-- None --" else None
            dc = dept_col if dept_col != "-- None --" else None
            result, summary = classify_jobs(df, title_col, sc, dc)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "classified", "classified_jobs.csv")

elif tool == TOOLS[10]:
    st.header("Classify Organisation Type")
    st.caption("Auto-classify companies into org types (bank, fintech, insurance, etc.).")
    fi = st.file_uploader("Upload CSV", type="csv", key="co")
    if fi:
        df = load_csv(fi)
        if st.button("Classify", key="co_run"):
            from tools.classify_jobs import classify_org_types
            result, summary = classify_org_types(df)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "classified", "classified_orgs.csv")

elif tool == TOOLS[11]:
    st.header("LinkedIn Search Links")
    st.caption("Generate LinkedIn search URLs for each person.")
    fi = st.file_uploader("Upload CSV", type="csv", key="li")
    if fi:
        df = load_csv(fi)
        name_col = st.selectbox("Name column", df.columns, key="li_name")
        title_col = st.selectbox("Title column (optional)", ["-- None --"] + list(df.columns), key="li_title")
        co_col = st.selectbox("Company column (optional)", ["-- None --"] + list(df.columns), key="li_co")
        if st.button("Generate Links", key="li_run"):
            from tools.linkedin_links import add_linkedin_links
            tc = title_col if title_col != "-- None --" else None
            cc = co_col if co_col != "-- None --" else None
            result = add_linkedin_links(df, name_col, tc, cc)
            st.success(f"Generated {len(result):,} links")
            st.dataframe(result.head(100))
            dl(result, "with LinkedIn links", "linkedin_links.csv")

elif tool == TOOLS[12]:
    st.header("Remove Blank Rows")
    fi = st.file_uploader("Upload CSV", type="csv", key="rb")
    if fi and st.button("Remove Blanks", key="rb_run"):
        from tools.remove_rows import remove_blank_rows
        df = load_csv(fi)
        result, summary = remove_blank_rows(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned", "no_blanks.csv")

elif tool == TOOLS[13]:
    st.header("Remove by Keywords / Flag")
    fi = st.file_uploader("Upload CSV", type="csv", key="rk")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Keywords", "Flag value"], key="rk_mode")
        col = st.selectbox("Column", df.columns, key="rk_col")
        if mode == "Keywords":
            kw_text = st.text_input("Keywords (comma-separated)", key="rk_kw")
            if st.button("Remove", key="rk_run"):
                from tools.remove_rows import remove_by_keywords
                kws = [k.strip() for k in kw_text.split(",") if k.strip()]
                cleaned, removed, summary = remove_by_keywords(df, col, kws)
                show_summary(summary)
                st.dataframe(cleaned.head(100))
                dl(cleaned, "cleaned", "kw_cleaned.csv")
                if len(removed): dl(removed, "removed", "kw_removed.csv")
        else:
            flag = st.text_input("Flag value (e.g. yes, duplicate)", key="rk_flag")
            if st.button("Remove", key="rk_run2"):
                from tools.remove_rows import remove_by_flag
                cleaned, removed, summary = remove_by_flag(df, col, flag)
                show_summary(summary)
                st.dataframe(cleaned.head(100))
                dl(cleaned, "cleaned", "flag_cleaned.csv")
                if len(removed): dl(removed, "removed", "flag_removed.csv")

elif tool == TOOLS[14]:
    st.header("Compare & Remove")
    st.caption("Remove rows from source that exist in a lookup list.")
    src_f = st.file_uploader("Upload SOURCE CSV", type="csv", key="cr_src")
    lkp_f = st.file_uploader("Upload LOOKUP CSV", type="csv", key="cr_lkp")
    if src_f and lkp_f:
        src = load_csv(src_f); lkp = load_csv(lkp_f)
        src_col = st.selectbox("Source column", src.columns, key="cr_sc")
        lkp_col = st.selectbox("Lookup column", lkp.columns, key="cr_lc")
        if st.button("Compare & Remove", key="cr_run"):
            from tools.compare_lists import compare_and_remove
            cleaned, removed, summary = compare_and_remove(src, lkp, src_col, lkp_col)
            show_summary(summary)
            st.dataframe(cleaned.head(100))
            dl(cleaned, "cleaned", "compare_cleaned.csv")
            if len(removed): dl(removed, "removed", "compare_removed.csv")

elif tool == TOOLS[15]:
    st.header("Column Remapper")
    st.caption("Map columns from a source CSV into a target template.")
    src_f = st.file_uploader("Upload SOURCE CSV (your data)", type="csv", key="rm_src")
    tgt_f = st.file_uploader("Upload TARGET template CSV (just headers is fine)", type="csv", key="rm_tgt")
    if src_f and tgt_f:
        src = load_csv(src_f); tgt = load_csv(tgt_f)
        src_cols = list(src.columns); tgt_cols = list(tgt.columns)
        st.subheader("Map each target column to a source column")
        mapping = {}; defaults = {}
        src_lower = {c.lower(): c for c in src_cols}
        for tc in tgt_cols:
            auto = src_lower.get(tc.lower(), "-- Leave empty --")
            options = ["-- Leave empty --", "-- Custom default --"] + src_cols
            idx = options.index(auto) if auto in options else 0
            choice = st.selectbox(f"Target: **{tc}**", options, index=idx, key=f"rm_{tc}")
            if choice == "-- Custom default --":
                val = st.text_input(f"Default value for {tc}", key=f"rm_def_{tc}")
                defaults[tc] = val
            elif choice != "-- Leave empty --":
                mapping[tc] = choice
        if st.button("Remap & Preview", key="rm_run"):
            from tools.remap_columns import remap_columns
            result, summary = remap_columns(src, tgt_cols, mapping, defaults)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "remapped CSV", "remapped.csv")

elif tool == TOOLS[16]:
    st.header("Merge / Split Columns")
    fi = st.file_uploader("Upload CSV", type="csv", key="ms")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Merge columns into one", "Split one column into many"], key="ms_mode")
        if mode.startswith("Merge"):
            cols = st.multiselect("Columns to merge", df.columns, key="ms_cols")
            sep = st.text_input("Separator", " ", key="ms_sep")
            name = st.text_input("New column name", "Merged", key="ms_name")
            if cols and st.button("Merge", key="ms_run"):
                from tools.remap_columns import merge_columns
                result = merge_columns(df, cols, sep, name)
                st.dataframe(result.head(100))
                dl(result, "merged", "merged.csv")
        else:
            col = st.selectbox("Column to split", df.columns, key="ms_scol")
            sep = st.text_input("Separator", " ", key="ms_ssep")
            names = st.text_input("New column names (comma-separated)", "Part 1, Part 2", key="ms_snames")
            if st.button("Split", key="ms_srun"):
                from tools.remap_columns import split_column
                new_names = [n.strip() for n in names.split(",") if n.strip()]
                result = split_column(df, col, sep, new_names)
                st.dataframe(result.head(100))
                dl(result, "split", "split.csv")

elif tool == TOOLS[17]:
    st.header("Value Standardiser")
    st.caption("Match raw values to your own standard terms using exact, keyword, and fuzzy matching.")
    st.markdown("""
    **How it works:** Upload your data CSV and a rules CSV. The rules CSV needs a column\n
    with your standard values (e.g. Standard Job Title). Optionally add an Aliases column\n
    with comma-separated alternatives (e.g. auditor, bookkeeper, accounts clerk).\n
    """)
    data_f = st.file_uploader("Upload DATA CSV", type="csv", key="vs_data")
    rules_f = st.file_uploader("Upload RULES CSV (your standards)", type="csv", key="vs_rules")
    if data_f and rules_f:
        data_df = load_csv(data_f); rules_df = load_csv(rules_f)
        col = st.selectbox("Column to standardise", data_df.columns, key="vs_col")
        std_col = st.selectbox("Standard value column (in rules)", rules_df.columns, key="vs_std")
        alias_options = ["-- None --"] + list(rules_df.columns)
        alias_col = st.selectbox("Aliases column (optional)", alias_options, key="vs_alias")
        threshold = st.slider("Fuzzy match threshold %", 50, 100, 80, key="vs_th")
        if st.button("Standardise", key="vs_run"):
            from tools.value_standardizer import standardize_values
            ac = alias_col if alias_col != "-- None --" else None
            result, report, summary = standardize_values(data_df, col, rules_df, std_col, ac, threshold)
            show_summary(summary)
            st.subheader("Standardised Data")
            st.dataframe(result.head(100))
            dl(result, "standardised CSV", "standardised.csv")
            st.subheader("Match Report")
            st.dataframe(report)
            dl(report, "match report", "match_report.csv")

elif tool == TOOLS[18]:
    st.header("Data Migration Pipeline")
    st.caption("Full migration: remap columns + set fixed values + auto-classify + standardise values.")
    src_f = st.file_uploader("Upload SOURCE CSV", type="csv", key="mig_src")
    tgt_f = st.file_uploader("Upload TARGET template CSV (headers)", type="csv", key="mig_tgt")
    if src_f and tgt_f:
        src = load_csv(src_f); tgt = load_csv(tgt_f)
        src_cols = list(src.columns); tgt_cols = list(tgt.columns)
        st.subheader("Step 1: Map columns")
        mapping = {}; defaults = {}
        src_lower = {c.lower(): c for c in src_cols}
        for tc in tgt_cols:
            auto = src_lower.get(tc.lower(), "-- Leave empty --")
            options = ["-- Leave empty --", "-- Fixed value --"] + src_cols
            idx = options.index(auto) if auto in options else 0
            choice = st.selectbox(f"**{tc}**", options, index=idx, key=f"mig_{tc}")
            if choice == "-- Fixed value --":
                val = st.text_input(f"Value for {tc}", key=f"mig_fix_{tc}")
                defaults[tc] = val
            elif choice != "-- Leave empty --":
                mapping[tc] = choice
        st.subheader("Step 2: Auto-classify")
        classify = st.checkbox("Auto-classify seniority, function, org type", value=True, key="mig_cls")
        title_col = None
        if classify:
            title_col = st.selectbox("Which target column has job titles?", ["-- None --"] + tgt_cols, key="mig_tcol")
            title_col = title_col if title_col != "-- None --" else None
        st.subheader("Step 3: Standardise values (optional)")
        rules_f = st.file_uploader("Upload RULES CSV (optional)", type="csv", key="mig_rules")
        std_configs = []
        if rules_f:
            rules_df = load_csv(rules_f)
            std_target_col = st.selectbox("Target column to standardise", tgt_cols, key="mig_stcol")
            std_standard_col = st.selectbox("Standard value column (in rules)", rules_df.columns, key="mig_stdcol")
            alias_options = ["-- None --"] + list(rules_df.columns)
            std_alias_col = st.selectbox("Aliases column (optional)", alias_options, key="mig_stalias")
            std_threshold = st.slider("Fuzzy threshold %", 50, 100, 80, key="mig_stth")
            std_configs.append({"col": std_target_col, "standards_df": rules_df,
                "standard_col": std_standard_col,
                "aliases_col": std_alias_col if std_alias_col != "-- None --" else None,
                "threshold": std_threshold})
        if st.button("Run Migration", key="mig_run"):
            from tools.data_migration import run_migration
            result, report, summary = run_migration(src, tgt_cols, mapping, defaults, classify, title_col, std_configs)
            show_summary(summary)
            st.subheader("Migrated Data")
            st.dataframe(result.head(100))
            dl(result, "migrated CSV", "migrated.csv")
            if len(report):
                st.subheader("Standardisation Report")
                st.dataframe(report)
                dl(report, "standardisation report", "std_report.csv")
