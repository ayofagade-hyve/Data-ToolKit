"""Data Cleaning & File Automation Toolkit — Streamlit App."""
import streamlit as st
import pandas as pd
import re

from utils.io_helpers import load_csv, to_csv_bytes, generate_summary

TOOLS = [
    "\U0001f3e0 Home",
    "\U0001f3e2 Classify Organisation Type",
    "\U0001f4bc Classify Seniority & Job Function",
    "\U0001f500 Column Remapper",
    "\U0001f4ce Combine CSVs",
    "\u2696\ufe0f Compare & Remove",
    "\U0001f4ca Data Quality Report",
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

st.set_page_config(page_title="Data Cleaning Toolkit", page_icon="\U0001f9f9", layout="wide")
st.sidebar.title("\U0001f9f0 Data Cleaning Toolkit")
tool = st.sidebar.radio("Select a tool", TOOLS, index=0)


def get_target_columns(key_prefix):
    st.markdown("**Option A:** Upload a CSV template (first row = column names)")
    tpl_file = st.file_uploader("Upload template CSV", type="csv", key=f"{key_prefix}_tpl")
    if tpl_file:
        return list(load_csv(tpl_file).columns)
    st.markdown("**Option B:** Type column names (comma-separated)")
    cols_text = st.text_input("Column names", key=f"{key_prefix}_cols_text")
    if cols_text:
        return [c.strip() for c in cols_text.split(",") if c.strip()]
    return None


def show_summary(s):
    st.info("  \n".join(f"**{k}:** {v}" for k, v in s.items()))


def dl(df, label, default_filename):
    custom_name = st.text_input(f"File name for {label}", value=default_filename, key=f"dl_{default_filename}_{label}")
    if not custom_name.endswith(".csv"):
        custom_name += ".csv"
    st.download_button(f"\u2b07\ufe0f Download {label}", to_csv_bytes(df), custom_name, "text/csv")


# ══════════════════════════════════════════════════════════════
# TOOLS[0] — Home
# ══════════════════════════════════════════════════════════════
if tool == TOOLS[0]:
    st.title("\U0001f3e0 Data Cleaning Toolkit")
    st.markdown("Welcome! Pick a tool from the sidebar. Upload your CSV, configure, and download cleaned data.")
    tool_cards = [
        ("\U0001f3e2", "Classify Organisation Type", "Tags each company as Bank, Fintech, Insurance, etc.", "Tag 5,000 contacts by org type."),
        ("\U0001f4bc", "Classify Seniority & Job Function", "Assigns seniority and function from job titles.", "'VP of Engineering' → VP level + Engineering."),
        ("\U0001f500", "Column Remapper", "Remap columns or reorder & remove them.", "Map CRM export to target template."),
        ("\U0001f4ce", "Combine CSVs", "Merge multiple CSVs into one.", "Combine 12 monthly exports."),
        ("\u2696\ufe0f", "Compare & Remove", "Remove rows found in a suppression list.", "Remove 500 opt-outs from 10K list."),
        ("\U0001f4ca", "Data Quality Report", "Completeness %, blanks, unique values for every column.", "Spot 90% blank columns before migration."),
        ("\U0001f50d", "Deduplicate vs Master List", "4-key matching to remove existing contacts.", "Dedupe 3K leads against 50K CRM."),
        ("\U0001f310", "Extract Company Domains", "Corporate domain extraction from emails.", "Find all 'Acme Corp' uses @acme.com."),
        ("\U0001f524", "Fix Encoding (Mojibake)", "4-pass repair of garbled characters.", "Fix 'CafÃ©' → 'Café'."),
        ("\U0001f504", "Full Data Migration", "7-stage pipeline with conditional rules.", "Transform CRM export in one go."),
        ("\U0001f501", "Fuzzy Duplicate Finder", "Blocking strategy for 100-1000x faster fuzzy matching.", "'Acme Corporation' ≈ 'Acme Corp' (92%)."),
        ("\U0001f50e", "LinkedIn Search Links", "Generate LinkedIn search URLs.", "Create links for event attendees."),
        ("\U0001f517", "Merge / Split Columns", "Combine or split columns.", "Merge First+Last into Full Name."),
        ("\U0001f6ab", "Remove by Keywords / Flag", "Keyword or exact-match row removal.", "Remove 'test'/'spam' emails."),
        ("\U0001f9f9", "Remove Blank Rows", "Remove all-empty rows.", "Clean up 200 blank rows."),
        ("\U0001f464", "Standardise Names", "Split names or extract from emails.", "Parse john.smith@acme.com → John Smith."),
        ("\U0001f4de", "Standardise Phone Numbers", "Normalise phone formatting.", "(020) 7946-0958 → 020 7946 0958."),
        ("\U0001f517", "Standardise URLs", "Lowercase, add https://, clean up.", "HTTP://WWW.Acme.COM/ → https://acme.com."),
        ("\U0001f3af", "Value Standardiser", "Rules CSV + Find & Replace + Case Converter.", "47 UK spellings → 1 standard."),
    ]
    for i in range(0, len(tool_cards), 3):
        cols = st.columns(3)
        for j, col_ui in enumerate(cols):
            idx = i + j
            if idx < len(tool_cards):
                emoji, title, desc, ex = tool_cards[idx]
                with col_ui:
                    st.markdown(f"### {emoji} {title}\n{desc}\n\n*Example: {ex}*")

# ══════════════════════════════════════════════════════════════
# TOOLS[1] — Classify Organisation Type
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[1]:
    st.header("\U0001f3e2 Classify Organisation Type")
    fi = st.file_uploader("Upload CSV", type="csv", key="co")
    if fi:
        df = load_csv(fi)
        st.dataframe(df.head(20))
        if st.button("Classify", key="co_run"):
            from tools.classify_jobs import classify_org_types
            result, summary = classify_org_types(df)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "classified CSV", "org_types_classified.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[2] — Classify Seniority & Job Function
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[2]:
    st.header("\U0001f4bc Classify Seniority & Job Function")
    fi = st.file_uploader("Upload CSV", type="csv", key="cj")
    if fi:
        df = load_csv(fi)
        title_col = st.selectbox("Job title column", df.columns, key="cj_title")
        seniority_col = st.selectbox("Existing seniority column (optional)", ["-- None --"] + list(df.columns), key="cj_sen")
        dept_col = st.selectbox("Department column (optional)", ["-- None --"] + list(df.columns), key="cj_dept")
        if st.button("Classify", key="cj_run"):
            from tools.classify_jobs import classify_jobs
            sc = seniority_col if seniority_col != "-- None --" else None
            dc = dept_col if dept_col != "-- None --" else None
            result, summary = classify_jobs(df, title_col, sc, dc)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "classified CSV", "seniority_function.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[3] — Column Remapper (+ Reorder & Remove)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[3]:
    st.header("\U0001f500 Column Remapper")
    st.markdown("**Remap columns** or **Reorder & remove columns**.")
    fi = st.file_uploader("Upload CSV", type="csv", key="rm_src")
    if fi:
        src = load_csv(fi); src_cols = list(src.columns)
        mode = st.radio("Mode", ["Remap to a new column structure", "Reorder & remove columns (keep what you need)"], key="rm_mode")
        if mode.startswith("Remap"):
            tgt_cols = get_target_columns("rm")
            if tgt_cols:
                mapping = {}; defaults = {}
                src_lower = {c.lower(): c for c in src_cols}
                for tc in tgt_cols:
                    auto = src_lower.get(tc.lower(), "-- Leave empty --")
                    options = ["-- Leave empty --", "-- Custom default --"] + src_cols
                    idx2 = options.index(auto) if auto in options else 0
                    choice = st.selectbox(f"Output: **{tc}**", options, index=idx2, key=f"rm_{tc}")
                    if choice == "-- Custom default --":
                        defaults[tc] = st.text_input(f"Default for {tc}", key=f"rm_def_{tc}")
                    elif choice != "-- Leave empty --":
                        mapping[tc] = choice
                if st.button("Remap & Preview", key="rm_run"):
                    from tools.remap_columns import remap_columns
                    result, summary = remap_columns(src, tgt_cols, mapping, defaults)
                    show_summary(summary); st.dataframe(result.head(100)); dl(result, "remapped CSV", "remapped.csv")
        else:
            selected = st.multiselect("Columns to keep (pick in order)", options=src_cols, default=src_cols, key="rm_reorder_cols")
            if selected:
                for i, cn in enumerate(selected, 1): st.text(f"  {i}. {cn}")
                if st.button("Apply & Preview", key="rm_reorder_run"):
                    result = src[selected].copy()
                    st.success(f"Kept {len(selected)} columns, removed {len(src_cols)-len(selected)}")
                    st.dataframe(result.head(100)); dl(result, "reordered CSV", "columns_reordered.csv")
            else:
                st.warning("Select at least one column.")

# ══════════════════════════════════════════════════════════════
# TOOLS[4] — Combine CSVs
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[4]:
    st.header("\U0001f4ce Combine CSVs")
    files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True, key="cc")
    if files:
        dfs = [load_csv(f) for f in files]
        st.write(f"{len(dfs)} file(s), {sum(len(d) for d in dfs):,} total rows")
        if st.button("Combine", key="cc_run"):
            from tools.combine_csvs import combine_csvs
            result, summary = combine_csvs(dfs)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "combined CSV", "combined.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[5] — Compare & Remove
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[5]:
    st.header("\u2696\ufe0f Compare & Remove")
    c1, c2 = st.columns(2)
    main_file = c1.file_uploader("Upload MAIN CSV", type="csv", key="cr_main")
    comp_file = c2.file_uploader("Upload SUPPRESSION CSV", type="csv", key="cr_comp")
    if main_file and comp_file:
        main_df = load_csv(main_file); comp_df = load_csv(comp_file)
        main_col = st.selectbox("Column in main file", main_df.columns, key="cr_mc")
        comp_col = st.selectbox("Column in suppression file", comp_df.columns, key="cr_cc")
        if st.button("Compare & Remove", key="cr_run"):
            from tools.compare_lists import compare_and_remove
            cleaned, removed, summary = compare_and_remove(main_df, comp_df, main_col, comp_col)
            show_summary(summary); st.dataframe(cleaned.head(100)); dl(cleaned, "cleaned CSV", "cleaned.csv")
            if len(removed) > 0:
                st.subheader("Removed Rows"); st.dataframe(removed.head(100)); dl(removed, "removed rows", "removed.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[6] — Data Quality Report (NEW)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[6]:
    st.header("\U0001f4ca Data Quality Report")
    fi = st.file_uploader("Upload CSV", type="csv", key="dq")
    if fi:
        df = load_csv(fi)
        if st.button("Generate Report", key="dq_run"):
            rows = len(df); report_data = []
            for col_name in df.columns:
                series = df[col_name].fillna("").astype(str).str.strip()
                non_blank = series[series != ""]
                blank_count = rows - len(non_blank)
                completeness = round((len(non_blank) / rows) * 100, 1) if rows > 0 else 0
                unique_count = non_blank.nunique()
                top_values = non_blank.value_counts().head(5)
                top_str = ", ".join(f"{v} ({c})" for v, c in top_values.items())
                sample = non_blank.iloc[0] if len(non_blank) > 0 else ""
                report_data.append({"Column": col_name, "Completeness %": completeness,
                    "Filled Rows": f"{len(non_blank):,}", "Blank Rows": f"{blank_count:,}",
                    "Unique Values": f"{unique_count:,}", "Top 5 Values": top_str, "Sample": str(sample)[:80]})
            report_df = pd.DataFrame(report_data)
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Rows", f"{rows:,}"); mc2.metric("Total Columns", f"{len(df.columns):,}")
            mc3.metric("Avg Completeness", f"{report_df['Completeness %'].mean():.1f}%")
            low_q = report_df[report_df["Completeness %"] < 50]
            if len(low_q):
                st.warning(f"\u26a0\ufe0f {len(low_q)} column(s) < 50% complete:")
                for _, r in low_q.iterrows():
                    st.markdown(f"- **{r['Column']}** — {r['Completeness %']}% ({r['Blank Rows']} blanks)")
            st.subheader("Full Report"); st.dataframe(report_df, use_container_width=True); dl(report_df, "quality report", "data_quality_report.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[7] — Deduplicate vs Master List
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[7]:
    st.header("\U0001f50d Deduplicate vs Master List")
    c1, c2 = st.columns(2)
    master_file = c1.file_uploader("Upload MASTER CSV", type="csv", key="dm_master")
    check_file = c2.file_uploader("Upload CHECK CSV", type="csv", key="dm_check")
    if master_file and check_file:
        master_df = load_csv(master_file); check_df = load_csv(check_file)
        st.write(f"Master: {len(master_df):,} rows | Check: {len(check_df):,} rows")
        if st.button("Deduplicate", key="dm_run"):
            from tools.dedupe_master import dedupe_against_master
            cleaned, removed, summary = dedupe_against_master(master_df, check_df)
            show_summary(summary); st.dataframe(cleaned.head(100)); dl(cleaned, "unique contacts", "deduped.csv")
            if len(removed) > 0:
                st.subheader("Duplicates Found"); st.dataframe(removed.head(100)); dl(removed, "duplicates", "duplicates.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[8] — Extract Company Domains
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[8]:
    st.header("\U0001f310 Extract Company Domains")
    fi = st.file_uploader("Upload CSV", type="csv", key="ed")
    if fi:
        df = load_csv(fi)
        email_col = st.selectbox("Email column", df.columns, key="ed_email")
        company_col = st.selectbox("Company column", df.columns, key="ed_comp")
        if st.button("Extract Domains", key="ed_run"):
            from tools.extract_domains import extract_domains
            result, missing, summary = extract_domains(df, email_col, company_col)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "with domains", "domains_extracted.csv")
            if len(missing) > 0:
                st.subheader("Companies Without Domain"); st.dataframe(missing); dl(missing, "missing domains", "missing_domains.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[9] — Fix Encoding (Mojibake)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[9]:
    st.header("\U0001f524 Fix Encoding (Mojibake)")
    fi = st.file_uploader("Upload CSV", type="csv", key="fe")
    if fi:
        df = load_csv(fi)
        cols = st.multiselect("Columns to fix", df.columns, default=list(df.columns), key="fe_cols")
        if cols and st.button("Fix Encoding", key="fe_run"):
            from tools.clean_encoding import clean_encoding
            result, summary = clean_encoding(df, cols)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "fixed encoding", "encoding_fixed.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[10] — Full Data Migration (7-stage pipeline)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[10]:
    st.header("\U0001f504 Full Data Migration")
    fi = st.file_uploader("Upload CSV", type="csv", key="fdm")
    if fi:
        df = load_csv(fi); src_cols = list(df.columns); config = {}
        st.write(f"{len(df):,} rows, {len(df.columns)} columns")
        with st.expander("Stage 1: Column Mapping"):
            tgt_cols = get_target_columns("fdm_s1"); col_mapping = {}
            if tgt_cols:
                src_lower = {c.lower(): c for c in src_cols}
                for tc in tgt_cols:
                    auto = src_lower.get(tc.lower(), "-- Skip --")
                    opts = ["-- Skip --"] + src_cols; idx2 = opts.index(auto) if auto in opts else 0
                    ch = st.selectbox(f"{tc}", opts, index=idx2, key=f"fdm_s1_{tc}")
                    if ch != "-- Skip --": col_mapping[tc] = ch
            config["column_mapping"] = col_mapping
        with st.expander("Stage 2: Fixed Values"):
            nf = st.number_input("Fixed value rules", 0, 50, 0, key="fdm_s2_num"); fv = {}
            for i in range(int(nf)):
                a, b = st.columns(2)
                cn = a.text_input(f"Column {i+1}", key=f"fdm_s2_col_{i}")
                vv = b.text_input(f"Value {i+1}", key=f"fdm_s2_val_{i}")
                if cn: fv[cn] = vv
            config["fixed_values"] = fv
        with st.expander("Stage 3: Conditional Rules"):
            nr = st.number_input("Rules", 0, 50, 0, key="fdm_s3_num"); cr = []
            for i in range(int(nr)):
                st.markdown(f"**Rule {i+1}**")
                rc = st.selectbox("IF column", src_cols, key=f"fdm_s3_col_{i}")
                ro = st.selectbox("Operator", ["equals","contains","not_empty","is_empty"], key=f"fdm_s3_op_{i}")
                rv = st.text_input("Value", key=f"fdm_s3_val_{i}")
                roc = st.text_input("THEN write to column", key=f"fdm_s3_out_{i}")
                rov = st.text_input("Write value", key=f"fdm_s3_outval_{i}")
                rev = st.text_input("ELSE value", key=f"fdm_s3_else_{i}")
                rm = st.selectbox("Write mode", ["overwrite","fill_blank","append_semicolon"], key=f"fdm_s3_mode_{i}")
                cr.append({"col":rc,"operator":ro,"value":rv,"out_col":roc,"out_val":rov,"else_val":rev,"mode":rm})
            config["conditional_rules"] = cr
        with st.expander("Stage 4: Auto-Classification"):
            config["auto_classify"] = {"seniority": st.checkbox("Seniority", key="fdm_s4_s"),
                "job_function": st.checkbox("Job Function", key="fdm_s4_f"), "org_type": st.checkbox("Org Type", key="fdm_s4_o")}
        with st.expander("Stage 5: Value Mapping"):
            mc = st.selectbox("Column to map", ["-- None --"] + src_cols, key="fdm_s5_col"); vm = {}
            if mc != "-- None --" and mc in df.columns:
                uv = [v for v in df[mc].fillna("").astype(str).str.strip().unique().tolist() if v][:200]
                if uv:
                    mdf = pd.DataFrame({"Original": uv, "Map To": uv})
                    ed = st.data_editor(mdf, num_rows="fixed", key="fdm_s5_editor")
                    if ed is not None:
                        m = {r["Original"]: r["Map To"] for _, r in ed.iterrows() if r["Original"] != r["Map To"]}
                        if m: vm[mc] = m
            config["value_mapping"] = vm
        with st.expander("Stage 6: Suppression Split"):
            ns = st.number_input("Suppression rules", 0, 20, 0, key="fdm_s6_num"); sr = []
            for i in range(int(ns)):
                sc2 = st.selectbox("Column", src_cols, key=f"fdm_s6_col_{i}")
                so = st.selectbox("Operator", ["equals","contains","not_empty"], key=f"fdm_s6_op_{i}")
                sv = st.text_input("Value", key=f"fdm_s6_val_{i}")
                sr.append({"col":sc2,"operator":so,"value":sv})
            config["suppression_rules"] = sr
        with st.expander("Stage 7: Column Cleanup"):
            cm = st.radio("Mode", ["Keep all","Keep only selected","Remove selected"], key="fdm_s7_mode"); cc2 = {}
            if cm == "Keep only selected": cc2["keep"] = st.multiselect("Keep", src_cols, key="fdm_s7_keep")
            elif cm == "Remove selected": cc2["remove"] = st.multiselect("Remove", src_cols, key="fdm_s7_remove")
            config["column_cleanup"] = cc2
        if st.button("\U0001f680 Run Full Migration", key="fdm_run"):
            from tools.data_migration import run_migration
            result, suppressed, summary = run_migration(df, config)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "migrated CSV", "migrated.csv")
            if len(suppressed) > 0:
                st.subheader("Suppressed"); st.dataframe(suppressed.head(100)); dl(suppressed, "suppressed CSV", "suppressed.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[11] — Fuzzy Duplicate Finder (PERFORMANCE FIX)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[11]:
    st.header("\U0001f501 Fuzzy Duplicate Finder")
    st.markdown("Scans a column for near-duplicates using fuzzy matching with blocking strategy.")
    fi = st.file_uploader("Upload CSV", type="csv", key="ifd")
    if fi:
        df = load_csv(fi)
        col = st.selectbox("Column to match on", df.columns, key="ifd_col")
        threshold = st.slider("Match threshold %", 50, 100, 90, key="ifd_th")
        uc = df[col].dropna().astype(str).str.strip().nunique()
        st.caption(f"{len(df):,} rows, {uc:,} unique values")
        if uc > 5000:
            st.warning(f"\u26a0\ufe0f {uc:,} unique values — may take a while. Consider 95%+ threshold or exact dedup first.")
        if st.button("Find Duplicates", key="ifd_run"):
            from tools.dedupe_internal import dedupe_within_file
            with st.spinner("Finding duplicates..."):
                result, summary = dedupe_within_file(df, col, threshold)
            show_summary(summary); st.dataframe(result.head(200)); dl(result, "results with flags", "fuzzy_dedup.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[12] — LinkedIn Search Links
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[12]:
    st.header("\U0001f50e LinkedIn Search Links")
    fi = st.file_uploader("Upload CSV", type="csv", key="ll")
    if fi:
        df = load_csv(fi)
        first_col = st.selectbox("First name column", df.columns, key="ll_first")
        last_col = st.selectbox("Last name column", df.columns, key="ll_last")
        company_col = st.selectbox("Company column (optional)", ["-- None --"] + list(df.columns), key="ll_comp")
        if st.button("Generate Links", key="ll_run"):
            from tools.linkedin_links import generate_links
            cc3 = company_col if company_col != "-- None --" else None
            result, summary = generate_links(df, first_col, last_col, cc3)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "with LinkedIn links", "linkedin_links.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[13] — Merge / Split Columns
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[13]:
    st.header("\U0001f517 Merge / Split Columns")
    fi = st.file_uploader("Upload CSV", type="csv", key="ms")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Merge columns", "Split a column"], key="ms_mode")
        if mode == "Merge columns":
            cols = st.multiselect("Columns to merge", df.columns, key="ms_cols")
            sep = st.text_input("Separator", value=" ", key="ms_sep")
            new_name = st.text_input("New column name", value="Merged", key="ms_name")
            if cols and st.button("Merge", key="ms_run"):
                from tools.remap_columns import merge_columns
                result = merge_columns(df, cols, sep, new_name)
                st.success(f"Merged {len(cols)} columns"); st.dataframe(result.head(100)); dl(result, "merged CSV", "merged.csv")
        else:
            col = st.selectbox("Column to split", df.columns, key="ms_scol")
            sep = st.text_input("Delimiter", value=",", key="ms_ssep")
            nn = st.text_input("New column names (comma-separated)", value="Part 1, Part 2", key="ms_snames")
            if st.button("Split", key="ms_srun"):
                from tools.remap_columns import split_column
                names = [n.strip() for n in nn.split(",") if n.strip()]
                result = split_column(df, col, sep, names)
                st.success(f"Split into {len(names)} columns"); st.dataframe(result.head(100)); dl(result, "split CSV", "split.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[14] — Remove by Keywords / Flag
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[14]:
    st.header("\U0001f6ab Remove by Keywords / Flag")
    fi = st.file_uploader("Upload CSV", type="csv", key="rk")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Remove by keywords", "Remove by flag value"], key="rk_mode")
        col = st.selectbox("Column to check", df.columns, key="rk_col")
        if mode.startswith("Remove by keywords"):
            kw = st.text_input("Keywords (comma-separated)", key="rk_kw")
            if kw and st.button("Remove", key="rk_krun"):
                from tools.remove_rows import remove_by_keywords
                keywords = [k.strip() for k in kw.split(",") if k.strip()]
                cleaned, removed, summary = remove_by_keywords(df, col, keywords)
                show_summary(summary); st.dataframe(cleaned.head(100)); dl(cleaned, "cleaned CSV", "keywords_removed.csv")
                if len(removed) > 0: st.subheader("Removed"); st.dataframe(removed.head(100)); dl(removed, "removed", "kw_removed_rows.csv")
        else:
            flag = st.text_input("Flag value (exact match)", key="rk_flag")
            if flag and st.button("Remove", key="rk_frun"):
                from tools.remove_rows import remove_by_flag
                cleaned, removed, summary = remove_by_flag(df, col, flag)
                show_summary(summary); st.dataframe(cleaned.head(100)); dl(cleaned, "cleaned CSV", "flag_removed.csv")
                if len(removed) > 0: st.subheader("Removed"); st.dataframe(removed.head(100)); dl(removed, "removed", "flag_removed_rows.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[15] — Remove Blank Rows
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[15]:
    st.header("\U0001f9f9 Remove Blank Rows")
    fi = st.file_uploader("Upload CSV", type="csv", key="rb")
    if fi:
        df = load_csv(fi); st.write(f"{len(df):,} rows loaded")
        if st.button("Remove Blank Rows", key="rb_run"):
            from tools.remove_rows import remove_blank_rows
            result, summary = remove_blank_rows(df)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "cleaned CSV", "blanks_removed.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[16] — Standardise Names (+ Email Extraction)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[16]:
    st.header("\U0001f464 Standardise Names")
    st.markdown("Split full names **or** extract names from email addresses.")
    fi = st.file_uploader("Upload CSV", type="csv", key="sn")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Split a full name column", "Extract names from email addresses"], key="sn_mode")
        if mode.startswith("Split"):
            col = st.selectbox("Full name column", df.columns, key="sn_col")
            if st.button("Split Names", key="sn_run"):
                from tools.standardize_data import standardize_names
                result = standardize_names(df, col)
                st.success(f"Split {len(result):,} names"); st.dataframe(result.head(100)); dl(result, "split names", "names_split.csv")
        else:
            email_col = st.selectbox("Email column", df.columns, key="sn_ecol")
            overwrite = st.radio("If First/Last Name exist:", ["Only fill blanks", "Overwrite everything"], key="sn_ow")
            if st.button("Extract Names", key="sn_erun"):
                result = df.copy(); fn_list, ln_list, dom_list = [], [], []
                for email in result[email_col].fillna("").astype(str):
                    email = email.strip().lower()
                    if "@" not in email:
                        fn_list.append(""); ln_list.append(""); dom_list.append(""); continue
                    local, domain = email.rsplit("@", 1); dom_list.append(domain)
                    parts = re.split(r'[._\-]', local); parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) == 0: fn_list.append(""); ln_list.append("")
                    elif len(parts) == 1: fn_list.append(parts[0].title()); ln_list.append("")
                    elif len(parts) == 2: fn_list.append(parts[0].title()); ln_list.append(parts[1].title())
                    else: fn_list.append(parts[0].title()); ln_list.append(" ".join(p.title() for p in parts[1:]))
                for c in ["First Name", "Last Name", "Email Domain"]:
                    if c not in result.columns: result[c] = ""
                if overwrite.startswith("Only"):
                    for i in range(len(result)):
                        if str(result.at[i,"First Name"]).strip() == "": result.at[i,"First Name"] = fn_list[i]
                        if str(result.at[i,"Last Name"]).strip() == "": result.at[i,"Last Name"] = ln_list[i]
                        if str(result.at[i,"Email Domain"]).strip() == "": result.at[i,"Email Domain"] = dom_list[i]
                else:
                    result["First Name"] = fn_list; result["Last Name"] = ln_list; result["Email Domain"] = dom_list
                ext = sum(1 for f in fn_list if f)
                st.success(f"Extracted from {ext:,} of {len(result):,} emails"); st.dataframe(result.head(100))
                dl(result, "extracted names", "email_names_extracted.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[17] — Standardise Phone Numbers
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[17]:
    st.header("\U0001f4de Standardise Phone Numbers")
    fi = st.file_uploader("Upload CSV", type="csv", key="sp")
    if fi:
        df = load_csv(fi); col = st.selectbox("Phone column", df.columns, key="sp_col")
        if st.button("Standardise", key="sp_run"):
            from tools.standardize_data import standardize_phones
            result, summary = standardize_phones(df, col)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "standardised phones", "phones_standardised.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[18] — Standardise URLs
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[18]:
    st.header("\U0001f517 Standardise URLs")
    fi = st.file_uploader("Upload CSV", type="csv", key="su")
    if fi:
        df = load_csv(fi); col = st.selectbox("URL column", df.columns, key="su_col")
        if st.button("Standardise", key="su_run"):
            from tools.standardize_data import standardize_urls
            result, summary = standardize_urls(df, col)
            show_summary(summary); st.dataframe(result.head(100)); dl(result, "standardised URLs", "urls_standardised.csv")

# ══════════════════════════════════════════════════════════════
# TOOLS[19] — Value Standardiser (+ Find & Replace + Case Converter)
# ══════════════════════════════════════════════════════════════
elif tool == TOOLS[19]:
    st.header("\U0001f3af Value Standardiser")
    st.markdown("Three modes: **Rules CSV**, **Find & Replace**, **Case Converter**.")
    fi = st.file_uploader("Upload CSV", type="csv", key="vs_data")
    if fi:
        data_df = load_csv(fi)
        mode = st.radio("Mode", ["Standardise with rules CSV", "Find & Replace", "Case Converter"], key="vs_mode")
        if mode.startswith("Standardise"):
            rules_f = st.file_uploader("Upload RULES CSV", type="csv", key="vs_rules")
            if rules_f:
                rules_df = load_csv(rules_f)
                col = st.selectbox("Column to standardise", data_df.columns, key="vs_col")
                std_col = st.selectbox("Standard value column", rules_df.columns, key="vs_std")
                alias_opts = ["-- None --"] + list(rules_df.columns)
                alias_col = st.selectbox("Aliases column (optional)", alias_opts, key="vs_alias")
                threshold = st.slider("Fuzzy threshold %", 50, 100, 80, key="vs_th")
                if st.button("Standardise", key="vs_run"):
                    from tools.value_standardizer import standardize_values
                    ac2 = alias_col if alias_col != "-- None --" else None
                    result, report, summary = standardize_values(data_df, col, rules_df, std_col, ac2, threshold)
                    show_summary(summary); st.dataframe(result.head(100)); dl(result, "standardised CSV", "standardised.csv")
                    st.subheader("Match Report"); st.dataframe(report); dl(report, "match report", "match_report.csv")
        elif mode.startswith("Find"):
            cols = st.multiselect("Columns", data_df.columns, default=list(data_df.columns), key="fr_cols")
            mm = st.radio("Match mode", ["Contains (replace within text)", "Exact match (whole cell only)"], key="fr_match")
            cs = st.checkbox("Case sensitive", value=False, key="fr_case")
            np2 = st.number_input("Find/replace pairs", 1, 50, 1, key="fr_num"); pairs = []
            for i in range(int(np2)):
                a, b = st.columns(2)
                ft = a.text_input(f"Find {i+1}", key=f"fr_find_{i}"); rt = b.text_input(f"Replace {i+1}", key=f"fr_replace_{i}")
                if ft: pairs.append((ft, rt))
            if pairs and cols and st.button("Run Find & Replace", key="fr_run"):
                result = data_df.copy(); total = 0
                for cn in cols:
                    series = result[cn].fillna("").astype(str)
                    for ft, rt in pairs:
                        if mm.startswith("Contains"):
                            if cs:
                                total += int(series.str.contains(ft, regex=False, na=False).sum())
                                series = series.str.replace(ft, rt, regex=False)
                            else:
                                total += int(series.str.contains(ft, case=False, regex=False, na=False).sum())
                                pat = re.compile(re.escape(ft), re.IGNORECASE)
                                series = series.apply(lambda x: pat.sub(rt, x))
                        else:
                            mask = (series == ft) if cs else (series.str.lower() == ft.lower())
                            total += int(mask.sum()); series = series.where(~mask, rt)
                    result[cn] = series
                st.success(f"{total:,} replacements across {len(cols)} column(s)"); st.dataframe(result.head(100))
                dl(result, "replaced", "find_replace_result.csv")
        else:
            cols = st.multiselect("Columns to convert", data_df.columns, key="cc_cols")
            cm2 = st.selectbox("Convert to", ["Title Case","UPPER CASE","lower case","Sentence case"], key="cc_case")
            if cols and st.button("Convert", key="cc_run"):
                result = data_df.copy()
                for c in cols:
                    s = result[c].fillna("").astype(str)
                    if cm2 == "Title Case": result[c] = s.str.title()
                    elif cm2 == "UPPER CASE": result[c] = s.str.upper()
                    elif cm2 == "lower case": result[c] = s.str.lower()
                    elif cm2 == "Sentence case":
                        result[c] = s.apply(lambda x: ". ".join(p.strip().capitalize() for p in x.split(".") if p.strip()) if x else x)
                st.success(f"Converted {len(cols)} column(s) to {cm2}"); st.dataframe(result.head(100))
                dl(result, "converted", "case_converted.csv")
