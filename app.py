"""
🧹 Data Cleaning & File Automation Toolkit
=============================================
A Streamlit web app that consolidates CSV cleaning, deduplication,
classification, and standardisation tools into one interactive UI.

Launch with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime

from utils.io_helpers import load_csv, to_csv_bytes, generate_summary

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Cleaning Toolkit",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────
st.sidebar.image(
    "https://img.icons8.com/fluency/96/broom.png",
    width=64,
)
st.sidebar.title("🧹 Data Toolkit")
st.sidebar.markdown("Choose a tool below to get started.")

TOOLS = [
    "🏠 Home",
    "📎 Combine CSVs",
    "🔤 Fix Encoding (Mojibake)",
    "🗂️ Deduplicate vs Master",
    "🔍 Internal Fuzzy Dedup",
    "🌐 Extract Domains",
    "👤 Standardise Names",
    "📞 Standardise Phones",
    "🔗 Standardise Websites / LinkedIn",
    "🏷️ Classify Seniority & Job Function",
    "🏢 Classify Organisation Type",
    "💼 Generate LinkedIn Links",
    "🧽 Remove Blank Rows",
    "🚫 Remove by Keywords / Flag",
    "⚖️ Compare & Remove",
]

tool = st.sidebar.radio("Select Tool", TOOLS, index=0)

# ── Helpers ────────────────────────────────────────────────────

def show_summary(summary: dict):
    """Display a summary card."""
    st.success("✅ Done!")
    cols = st.columns(3)
    keys = list(summary.keys())
    for i, key in enumerate(keys[:3]):
        cols[i].metric(key, summary[key])
    if len(keys) > 3:
        st.markdown("**Details:**")
        for key in keys[3:]:
            val = summary[key]
            if isinstance(val, dict):
                for k, v in val.items():
                    st.markdown(f"- **{k}**: {v}")
            else:
                st.markdown(f"- **{key}**: {val}")


def download_btn(label, data_bytes, filename, key=None):
    """Wrapper for a styled download button."""
    st.download_button(
        label=f"⬇️ {label}",
        data=data_bytes,
        file_name=filename,
        mime="text/csv",
        key=key,
    )


def preview_df(df, title="Preview (first 100 rows)"):
    with st.expander(title, expanded=True):
        st.dataframe(df.head(100), use_container_width=True)


def col_selector(df, label, key, default_substring=None):
    """Let user pick a column from a dataframe."""
    cols = list(df.columns)
    default_idx = 0
    if default_substring:
        for i, c in enumerate(cols):
            if default_substring.lower() in c.lower():
                default_idx = i
                break
    return st.selectbox(label, cols, index=default_idx, key=key)


# ── HOME ───────────────────────────────────────────────────────

if tool == "🏠 Home":
    st.title("🧹 Data Cleaning & File Automation Toolkit")
    st.markdown("""
    Welcome! This app brings together **14 data-cleaning tools** in one place.
    Upload your CSV files, pick a tool from the sidebar, configure options, and
    download clean results — no coding required.

    ---

    ### 🛠️ Available Tools

    | Category | Tools |
    |----------|-------|
    | **Combine** | Merge multiple CSVs into one |
    | **Clean** | Fix encoding errors (mojibake), remove blank rows |
    | **Deduplicate** | Against a master list, or fuzzy-match within a file |
    | **Extract** | Domains from email addresses |
    | **Standardise** | Names, phones, websites, LinkedIn URLs |
    | **Classify** | Job seniority, function, and organisation type |
    | **Generate** | LinkedIn people-search links |
    | **Compare** | Remove rows that exist in another list |

    ---

    ### 💡 How to use
    1. **Pick a tool** from the sidebar.
    2. **Upload** your CSV file(s).
    3. **Configure** options (column selectors, thresholds, etc.).
    4. **Click Run** and review the preview.
    5. **Download** your cleaned file.

    Every tool shows a summary report with before/after row counts.
    Removed rows are always available as a separate download.
    Your original files are **never modified**.
    """)

# ── COMBINE CSVs ───────────────────────────────────────────────

elif tool == "📎 Combine CSVs":
    st.header("📎 Combine Multiple CSV Files")
    st.info("Upload two or more CSV files and merge them into one. Columns are matched by name.")

    files = st.file_uploader(
        "Upload CSV files",
        type=["csv"],
        accept_multiple_files=True,
        key="combine_upload",
    )

    if files and len(files) >= 2:
        if st.button("🚀 Combine Files", key="combine_run"):
            from tools.combine_csvs import combine_csvs
            combined, summary = combine_csvs(files)
            show_summary(summary)
            preview_df(combined)
            download_btn(
                "Download Combined CSV",
                to_csv_bytes(combined),
                f"combined_{datetime.now():%Y%m%d_%H%M}.csv",
                key="combine_dl",
            )
    elif files:
        st.warning("Please upload at least 2 files to combine.")

# ── FIX ENCODING ───────────────────────────────────────────────

elif tool == "🔤 Fix Encoding (Mojibake)":
    st.header("🔤 Fix Encoding (Mojibake)")
    st.info("Repair garbled characters (e.g. `Ã©` → `é`, `Ã¼` → `ü`). Works on all text columns.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="encoding_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows × {len(df.columns)} columns")
        if st.button("🚀 Fix Encoding", key="encoding_run"):
            from tools.clean_encoding import clean_encoding
            cleaned, summary = clean_encoding(df)
            show_summary(summary)
            preview_df(cleaned)
            download_btn(
                "Download Cleaned CSV",
                to_csv_bytes(cleaned),
                f"encoding_fixed_{datetime.now():%Y%m%d_%H%M}.csv",
                key="encoding_dl",
            )

# ── DEDUPLICATE VS MASTER ─────────────────────────────────────

elif tool == "🗂️ Deduplicate vs Master":
    st.header("🗂️ Deduplicate Against a Master List")
    st.info(
        "Remove rows from your file that already exist in a master file. "
        "Matches on: **email**, **LinkedIn URL**, **name + company**, and **name + website**."
    )

    col1, col2 = st.columns(2)
    with col1:
        master_file = st.file_uploader("Upload MASTER file", type=["csv"], key="dedup_master_file")
    with col2:
        check_file = st.file_uploader("Upload FILE TO CLEAN", type=["csv"], key="dedup_check_file")

    if master_file and check_file:
        master_df = load_csv(master_file)
        check_df = load_csv(check_file)
        st.write(f"Master: **{len(master_df):,}** rows | File to clean: **{len(check_df):,}** rows")

        if st.button("🚀 Deduplicate", key="dedup_master_run"):
            from tools.dedupe_master import dedupe_against_master
            cleaned, removed, summary = dedupe_against_master(master_df, check_df)
            show_summary(summary)

            tab1, tab2 = st.tabs(["✅ Cleaned", "❌ Removed"])
            with tab1:
                preview_df(cleaned, "Cleaned rows")
                download_btn("Download Cleaned", to_csv_bytes(cleaned),
                    f"deduped_cleaned_{datetime.now():%Y%m%d_%H%M}.csv", key="dedup_clean_dl")
            with tab2:
                preview_df(removed, "Removed rows (with match reason)")
                download_btn("Download Removed", to_csv_bytes(removed),
                    f"deduped_removed_{datetime.now():%Y%m%d_%H%M}.csv", key="dedup_rem_dl")

# ── INTERNAL FUZZY DEDUP ──────────────────────────────────────

elif tool == "🔍 Internal Fuzzy Dedup":
    st.header("🔍 Internal Fuzzy Deduplication")
    st.info(
        "Find fuzzy duplicates within a single file using Levenshtein similarity. "
        "Each row is compared against all earlier rows."
    )

    file = st.file_uploader("Upload CSV", type=["csv"], key="fuzzy_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        column = col_selector(df, "Column to check for duplicates", "fuzzy_col", "company")
        threshold = st.slider(
            "Similarity threshold (%)",
            min_value=50, max_value=100, value=90, step=5,
            key="fuzzy_threshold",
            help="Higher = stricter matching. 100 = exact matches only.",
        )

        if st.button("🚀 Find Duplicates", key="fuzzy_run"):
            from tools.dedupe_internal import dedupe_within_file
            with st.spinner("Comparing rows… this may take a moment for large files."):
                result, summary = dedupe_within_file(df, column, threshold)
            show_summary(summary)
            preview_df(result)
            download_btn("Download Results", to_csv_bytes(result),
                f"fuzzy_dedup_{datetime.now():%Y%m%d_%H%M}.csv", key="fuzzy_dl")

# ── EXTRACT DOMAINS ───────────────────────────────────────────

elif tool == "🌐 Extract Domains":
    st.header("🌐 Extract Domains from Email Addresses")
    st.info(
        "Extract company domains from email addresses. "
        "Personal domains (gmail, yahoo, etc.) are excluded. "
        "The most common domain per company is used."
    )

    file = st.file_uploader("Upload CSV", type=["csv"], key="domain_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        col1, col2 = st.columns(2)
        with col1:
            email_col = col_selector(df, "Email column", "domain_email_col", "email")
        with col2:
            company_col = col_selector(df, "Company column", "domain_company_col", "company")

        if st.button("🚀 Extract Domains", key="domain_run"):
            from tools.extract_domains import extract_domains
            result, missing, summary = extract_domains(df, email_col, company_col)
            show_summary(summary)

            tab1, tab2 = st.tabs(["✅ Results", "⚠️ Missing Domains"])
            with tab1:
                preview_df(result)
                download_btn("Download Results", to_csv_bytes(result),
                    f"domains_{datetime.now():%Y%m%d_%H%M}.csv", key="domain_dl")
            with tab2:
                preview_df(missing, "Companies with no domain found")
                download_btn("Download Missing", to_csv_bytes(missing),
                    f"no_domain_companies_{datetime.now():%Y%m%d_%H%M}.csv", key="domain_miss_dl")

# ── STANDARDISE NAMES ─────────────────────────────────────────

elif tool == "👤 Standardise Names":
    st.header("👤 Standardise Names")
    st.info("Split a full-name column into separate First Name and Last Name columns.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="names_upload")
    if file:
        df = load_csv(file)
        name_col = col_selector(df, "Full Name column", "names_col", "name")

        if st.button("🚀 Split Names", key="names_run"):
            from tools.standardize_data import standardize_names
            result = standardize_names(df, name_col)
            st.success(f"✅ Added **First Name** and **Last Name** columns to {len(result):,} rows.")
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"names_split_{datetime.now():%Y%m%d_%H%M}.csv", key="names_dl")

# ── STANDARDISE PHONES ────────────────────────────────────────

elif tool == "📞 Standardise Phones":
    st.header("📞 Standardise Phone Numbers")
    st.info("Strip formatting characters, keeping only digits and leading `+`.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="phone_upload")
    if file:
        df = load_csv(file)
        phone_col = col_selector(df, "Phone column", "phone_col", "phone")

        if st.button("🚀 Clean Phones", key="phone_run"):
            from tools.standardize_data import standardize_phones
            result = standardize_phones(df, phone_col)
            st.success(f"✅ Cleaned phone numbers in **{phone_col}**.")
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"phones_cleaned_{datetime.now():%Y%m%d_%H%M}.csv", key="phone_dl")

# ── STANDARDISE WEBSITES / LINKEDIN ───────────────────────────

elif tool == "🔗 Standardise Websites / LinkedIn":
    st.header("🔗 Standardise Websites & LinkedIn URLs")
    st.info("Normalise URLs by removing `http(s)://`, `www.`, and trailing slashes.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="url_upload")
    if file:
        df = load_csv(file)

        option = st.radio("What to standardise?", ["Website / Domain", "LinkedIn URL", "Both"], key="url_option")

        web_col = None
        li_col = None
        if option in ("Website / Domain", "Both"):
            web_col = col_selector(df, "Website column", "url_web_col", "website")
        if option in ("LinkedIn URL", "Both"):
            li_col = col_selector(df, "LinkedIn column", "url_li_col", "linkedin")

        if st.button("🚀 Standardise", key="url_run"):
            from tools.standardize_data import standardize_websites, standardize_linkedin
            result = df.copy()
            if web_col:
                result = standardize_websites(result, web_col)
            if li_col:
                result = standardize_linkedin(result, li_col)
            st.success("✅ URLs standardised.")
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"urls_standardised_{datetime.now():%Y%m%d_%H%M}.csv", key="url_dl")

# ── CLASSIFY SENIORITY & JOB FUNCTION ─────────────────────────

elif tool == "🏷️ Classify Seniority & Job Function":
    st.header("🏷️ Classify Job Seniority & Function")
    st.info(
        "Automatically classify seniority (C-level, VP, Director, Manager, Associate, Other) "
        "and job function (Sales, Marketing, IT, Finance, etc.) from job titles."
    )

    file = st.file_uploader("Upload CSV", type=["csv"], key="classify_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        title_col = col_selector(df, "Job Title column", "classify_title_col", "title")
        with st.expander("⚙️ Advanced options"):
            use_seniority = st.checkbox("Use existing seniority column as hint?", key="classify_use_sen")
            sen_col = None
            dept_col = None
            if use_seniority:
                sen_col = col_selector(df, "Existing Seniority column", "classify_sen_col", "seniority")
            use_dept = st.checkbox("Use department column for better function classification?", key="classify_use_dept")
            if use_dept:
                dept_col = col_selector(df, "Department column", "classify_dept_col", "department")

        if st.button("🚀 Classify", key="classify_run"):
            from tools.classify_jobs import classify_jobs
            result, summary = classify_jobs(df, title_col, sen_col, dept_col)
            show_summary(summary)
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"classified_{datetime.now():%Y%m%d_%H%M}.csv", key="classify_dl")

# ── CLASSIFY ORG TYPE ─────────────────────────────────────────

elif tool == "🏢 Classify Organisation Type":
    st.header("🏢 Classify Organisation Type")
    st.info(
        "Auto-classify companies into categories like Bank, Fintech, Insurance, "
        "Government, etc. based on available columns."
    )

    file = st.file_uploader("Upload CSV", type=["csv"], key="org_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        st.markdown("The tool will auto-detect columns named *Company*, *Industries*, *Job Title*, *Website*, etc.")

        if st.button("🚀 Classify", key="org_run"):
            from tools.classify_jobs import classify_org_types
            result, summary = classify_org_types(df)
            show_summary(summary)
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"org_classified_{datetime.now():%Y%m%d_%H%M}.csv", key="org_dl")

# ── LINKEDIN LINKS ────────────────────────────────────────────

elif tool == "💼 Generate LinkedIn Links":
    st.header("💼 Generate LinkedIn Search Links")
    st.info("Create clickable LinkedIn people-search URLs from name, title, and company columns.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="li_upload")
    if file:
        df = load_csv(file)
        name_col = col_selector(df, "Name column", "li_name_col", "name")
        with st.expander("⚙️ Optional columns (improve search quality)"):
            title_col = col_selector(df, "Job Title column (optional)", "li_title_col", "title")
            company_col = col_selector(df, "Company column (optional)", "li_company_col", "company")

        if st.button("🚀 Generate Links", key="li_run"):
            from tools.linkedin_links import add_linkedin_links
            result = add_linkedin_links(df, name_col, title_col, company_col)
            st.success(f"✅ Added **LinkedIn Search URL** column to {len(result):,} rows.")
            preview_df(result)
            download_btn("Download", to_csv_bytes(result),
                f"linkedin_links_{datetime.now():%Y%m%d_%H%M}.csv", key="li_dl")

# ── REMOVE BLANK ROWS ────────────────────────────────────────

elif tool == "🧽 Remove Blank Rows":
    st.header("🧽 Remove Blank Rows")
    st.info("Delete rows where every cell is empty or whitespace-only.")

    file = st.file_uploader("Upload CSV", type=["csv"], key="blank_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        if st.button("🚀 Remove Blanks", key="blank_run"):
            from tools.remove_rows import remove_blank_rows
            cleaned, summary = remove_blank_rows(df)
            show_summary(summary)
            preview_df(cleaned)
            download_btn("Download", to_csv_bytes(cleaned),
                f"no_blanks_{datetime.now():%Y%m%d_%H%M}.csv", key="blank_dl")

# ── REMOVE BY KEYWORDS / FLAG ────────────────────────────────

elif tool == "🚫 Remove by Keywords / Flag":
    st.header("🚫 Remove Rows by Keywords or Flag Value")

    file = st.file_uploader("Upload CSV", type=["csv"], key="kw_upload")
    if file:
        df = load_csv(file)
        st.write(f"**Loaded:** {len(df):,} rows")

        mode = st.radio("Removal mode", ["Keywords (partial match)", "Exact flag value"], key="kw_mode")
        column = col_selector(df, "Column to check", "kw_col")

        if mode == "Keywords (partial match)":
            kw_text = st.text_area(
                "Keywords (one per line)",
                placeholder="Pipeline\nClosed Won Contracts\nVendelux Data",
                key="kw_keywords",
            )
            if st.button("🚀 Remove Matching Rows", key="kw_run"):
                keywords = [k.strip() for k in kw_text.strip().split("\n") if k.strip()]
                if not keywords:
                    st.error("Please enter at least one keyword.")
                else:
                    from tools.remove_rows import remove_by_keywords
                    cleaned, removed, summary = remove_by_keywords(df, column, keywords)
                    show_summary(summary)
                    tab1, tab2 = st.tabs(["✅ Cleaned", "❌ Removed"])
                    with tab1:
                        preview_df(cleaned)
                        download_btn("Download Cleaned", to_csv_bytes(cleaned),
                            f"kw_cleaned_{datetime.now():%Y%m%d_%H%M}.csv", key="kw_clean_dl")
                    with tab2:
                        preview_df(removed)
                        download_btn("Download Removed", to_csv_bytes(removed),
                            f"kw_removed_{datetime.now():%Y%m%d_%H%M}.csv", key="kw_rem_dl")
        else:
            flag_value = st.text_input("Flag value to match (e.g. 'yes', 'duplicate')", key="kw_flag")
            if st.button("🚀 Remove Flagged Rows", key="kw_flag_run"):
                if not flag_value.strip():
                    st.error("Please enter a flag value.")
                else:
                    from tools.remove_rows import remove_by_flag
                    cleaned, removed, summary = remove_by_flag(df, column, flag_value)
                    show_summary(summary)
                    tab1, tab2 = st.tabs(["✅ Cleaned", "❌ Removed"])
                    with tab1:
                        preview_df(cleaned)
                        download_btn("Download Cleaned", to_csv_bytes(cleaned),
                            f"flag_cleaned_{datetime.now():%Y%m%d_%H%M}.csv", key="flag_clean_dl")
                    with tab2:
                        preview_df(removed)
                        download_btn("Download Removed", to_csv_bytes(removed),
                            f"flag_removed_{datetime.now():%Y%m%d_%H%M}.csv", key="flag_rem_dl")

# ── COMPARE & REMOVE ─────────────────────────────────────────

elif tool == "⚖️ Compare & Remove":
    st.header("⚖️ Compare Two Lists & Remove Matches")
    st.info(
        "Upload a **source file** and a **lookup file**. "
        "Any rows in the source whose column value appears in the lookup will be removed."
    )

    col1, col2 = st.columns(2)
    with col1:
        source_file = st.file_uploader("Upload SOURCE file", type=["csv"], key="cmp_source")
    with col2:
        lookup_file = st.file_uploader("Upload LOOKUP file", type=["csv"], key="cmp_lookup")

    if source_file and lookup_file:
        source_df = load_csv(source_file)
        lookup_df = load_csv(lookup_file)
        st.write(f"Source: **{len(source_df):,}** rows | Lookup: **{len(lookup_df):,}** rows")

        col1, col2 = st.columns(2)
        with col1:
            source_col = col_selector(source_df, "Source column to compare", "cmp_src_col", "company")
        with col2:
            lookup_col = col_selector(lookup_df, "Lookup column to compare against", "cmp_lkp_col", "company")

        if st.button("🚀 Compare & Remove", key="cmp_run"):
            from tools.compare_lists import compare_and_remove
            cleaned, removed, summary = compare_and_remove(source_df, lookup_df, source_col, lookup_col)
            show_summary(summary)
            tab1, tab2 = st.tabs(["✅ Cleaned", "❌ Removed"])
            with tab1:
                preview_df(cleaned)
                download_btn("Download Cleaned", to_csv_bytes(cleaned),
                    f"compared_cleaned_{datetime.now():%Y%m%d_%H%M}.csv", key="cmp_clean_dl")
            with tab2:
                preview_df(removed)
                download_btn("Download Removed", to_csv_bytes(removed),
                    f"compared_removed_{datetime.now():%Y%m%d_%H%M}.csv", key="cmp_rem_dl")

# ── Footer ─────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small>Data Cleaning Toolkit v1.0<br>"
    "Built with ❤️ using Streamlit</small>",
    unsafe_allow_html=True,
)
