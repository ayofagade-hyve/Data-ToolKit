"""Data Cleaning & File Automation Toolkit — Streamlit App (18 tools)."""
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
    st.download_button(f"\u2b07\ufe0f Download {label}", to_csv_bytes(df), filename, "text/csv")


# ══════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════
if tool == TOOLS[0]:
    st.title("\U0001f9f9 Data Cleaning & File Automation Toolkit")
    st.markdown("""
    Welcome! This toolkit gives you **18 powerful data-cleaning tools** in one simple web app.
    No coding needed — just upload your CSV, pick a tool, configure it, and download clean results.

    Built for **event, marketing, and sales teams** who regularly work with contact lists,
    CRM exports, Cognism pulls, and master databases.
    """)

    st.markdown("---")
    st.subheader("\U0001f9f0 All 18 Tools at a Glance")

    tool_info = [
        ("\U0001f4ce", "Combine CSVs", "Merge 2+ CSV files into one. Great when you have data split across multiple exports."),
        ("\U0001f524", "Fix Encoding", "Repair garbled characters (mojibake) like Ã© → é. Common in European-language data."),
        ("\U0001f50d", "Deduplicate vs Master", "Remove people from a new list who already exist in your master database. Matches on email, LinkedIn, name+company, and name+website."),
        ("\U0001f501", "Internal Fuzzy Dedup", "Find near-duplicate entries within a single file using fuzzy matching. E.g. 'Acme Corp' vs 'Acme Corporation'."),
        ("\U0001f310", "Extract Domains", "Pull the most common company email domain per company from a list of email addresses."),
        ("\U0001f464", "Standardise Names", "Split 'John Smith' into separate First Name and Last Name columns."),
        ("\U0001f4de", "Standardise Phones", "Strip brackets, dashes, and spaces from phone numbers. Keeps digits and + only."),
        ("\U0001f517", "Standardise URLs", "Normalise website URLs and LinkedIn profile URLs (remove http://, www., trailing slashes)."),
        ("\U0001f4bc", "Classify Seniority & Function", "Auto-tag every job title with a seniority level (C-level, VP, Director, Manager, Associate) and function (Sales, Marketing, IT, etc.)."),
        ("\U0001f3e2", "Classify Org Type", "Auto-tag companies as Bank, Fintech, Insurance, VC, Retailer, etc. based on industry and company data."),
        ("\U0001f50e", "LinkedIn Search Links", "Generate a LinkedIn people-search URL for every person in your list."),
        ("\U0001f9f9", "Remove Blank Rows", "Delete completely empty rows from your data."),
        ("\U0001f6ab", "Remove by Keywords / Flag", "Delete rows containing specific keywords, or where a flag column equals a value like 'yes' or 'duplicate'."),
        ("\u2696\ufe0f", "Compare & Remove", "Remove people from List A who appear in List B. Great for suppression lists and redemption removal."),
        ("\U0001f500", "Column Remapper", "Map columns from one CSV format into another. Upload source + target template, visually map each column."),
        ("\U0001f517", "Merge / Split Columns", "Combine multiple columns into one (e.g. First + Last → Full Name) or split one column into many."),
        ("\U0001f3af", "Value Standardiser", "Upload your own rules (e.g. 'Accountant' with aliases 'auditor, bookkeeper') and fuzzy-match raw values to your standards."),
        ("\U0001f504", "Data Migration Pipeline", "Full Cognism-style migration: remap columns, set fixed values (Brand, Source), auto-classify, and standardise — all in one step."),
    ]

    for i in range(0, len(tool_info), 3):
        row = st.columns(3)
        for j, col in enumerate(row):
            if i + j < len(tool_info):
                emoji, name, desc = tool_info[i + j]
                col.markdown(f"### {emoji} {name}")
                col.markdown(desc)

    st.markdown("---")
    st.subheader("\U0001f680 Quick Start")
    st.markdown("""
    1. **Pick a tool** from the sidebar on the left
    2. **Upload your CSV** file(s)
    3. **Configure** any options (column selectors, thresholds, etc.)
    4. **Click Run** to process
    5. **Preview** the results in the table
    6. **Download** the cleaned output

    > **Tip:** Your original files are never modified. Every tool exports a new, clean file.
    """)

    st.subheader("\U0001f4a1 Tips")
    st.markdown("""
    - **Column auto-detection**: Many tools automatically find columns like Email, Company, Job Title
      by checking common names and aliases
    - **Fuzzy matching**: Uses Levenshtein distance — you can adjust the threshold slider to be
      stricter (100% = exact only) or more lenient (50% = loose matching)
    - **Large files**: All tools handle files with 100K+ rows. Processing may take a moment for
      fuzzy-matching tools on very large datasets
    - **Encoding issues?** Run "Fix Encoding" first before other tools if you see garbled characters
    """)


# ══════════════════════════════════════════════════════════
# TOOL 1: Combine CSVs
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[1]:
    st.header("\U0001f4ce Combine CSVs")
    st.markdown("""
    **What it does:** Merges multiple CSV files into a single file, stacking all rows together.

    **When to use it:** You have data split across multiple exports — e.g. separate Cognism pulls
    for different regions, or monthly contact lists that need combining.

    **Example:** Upload `contacts_jan.csv`, `contacts_feb.csv`, and `contacts_mar.csv` →
    get one `combined.csv` with all rows from all three files.
    """)
    files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True, key="combine")
    if files and st.button("Combine", key="combine_run"):
        from tools.combine_csvs import combine_csvs
        result, summary = combine_csvs(files)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "combined CSV", "combined.csv")


# ══════════════════════════════════════════════════════════
# TOOL 2: Fix Encoding
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[2]:
    st.header("\U0001f524 Fix Encoding (Mojibake)")
    st.markdown("""
    **What it does:** Repairs garbled/broken characters caused by encoding mismatches.
    Fixes things like `Ã©` → `é`, `Ã¼` → `ü`, `Ã±` → `ñ`.

    **When to use it:** Your CSV has weird characters in names, companies, or addresses —
    especially common with European-language data exported from older systems.

    **Example:** `"José García"` appears as `"JosÃ© GarcÃ­a"` → this tool fixes it back.
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="enc")
    if fi and st.button("Fix Encoding", key="enc_run"):
        from tools.clean_encoding import clean_encoding
        df = load_csv(fi)
        result, summary = clean_encoding(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned CSV", "encoding_fixed.csv")


# ══════════════════════════════════════════════════════════
# TOOL 3: Deduplicate vs Master
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[3]:
    st.header("\U0001f50d Deduplicate vs Master")
    st.markdown("""
    **What it does:** Compares a new contact list against your master database and removes
    anyone who already exists. Matches on **4 keys** (in order):
    1. **Email** (exact match)
    2. **LinkedIn URL** (normalised match)
    3. **First Name + Last Name + Company** (exact match)
    4. **First Name + Last Name + Website/Domain** (exact match)

    **When to use it:** You've pulled a new Cognism or Apollo list and want to remove
    people you've already got in your CRM/master sheet.

    **Example:** Upload your `master_database.csv` (10,000 rows) and `new_cognism_pull.csv`
    (500 rows) → get back ~350 truly new contacts + a report of which 150 were duplicates and why.
    """)
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
            st.subheader("Removed rows (with match reason)")
            st.dataframe(removed.head(100))
            dl(removed, "removed rows", "deduped_removed.csv")


# ══════════════════════════════════════════════════════════
# TOOL 4: Internal Fuzzy Dedup
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[4]:
    st.header("\U0001f501 Internal Fuzzy Dedup")
    st.markdown("""
    **What it does:** Scans a single column for near-duplicate values using fuzzy string matching
    (Levenshtein distance). Flags each row as "Unique" or "Duplicate" with the match % and
    which row it matched against.

    **When to use it:** Your list has messy company names or person names that might be
    duplicates with slightly different spelling.

    **Example:** With threshold 90%, `"Acme Corporation"` and `"Acme Corp"` would be flagged
    as duplicates (92% match). `"Acme Corp"` and `"Ajax Corp"` would not (67% match).

    **Tip:** Set threshold to 95% for strict matching, 80% for loose matching.
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 5: Extract Domains
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[5]:
    st.header("\U0001f310 Extract Domains")
    st.markdown("""
    **What it does:** Extracts the email domain for each company by finding the most common
    non-personal domain among all contacts at that company. Ignores personal domains like
    gmail.com, yahoo.com, hotmail.com.

    **When to use it:** You have contacts with emails but no company website/domain column,
    and you need to enrich your data with company domains.

    **Example:** If 3 people at "Acme Corp" have emails `john@acme.com`, `jane@acme.com`,
    and `bob@gmail.com`, the tool assigns `acme.com` as Acme Corp's domain.
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 6: Standardise Names
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[6]:
    st.header("\U0001f464 Standardise Names")
    st.markdown("""
    **What it does:** Splits a "Full Name" column into separate "First Name" and "Last Name" columns.

    **When to use it:** Your data has a single name column like `"John Smith"` but your CRM
    or template needs separate first/last name fields.

    **Example:** `"Mary Jane Watson"` → First Name: `"Mary"`, Last Name: `"Jane Watson"`
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 7: Standardise Phones
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[7]:
    st.header("\U0001f4de Standardise Phones")
    st.markdown("""
    **What it does:** Strips all formatting from phone numbers, keeping only digits and the `+` symbol.

    **When to use it:** Phone numbers in your data have inconsistent formatting — brackets,
    dashes, dots, spaces — and you need them clean for import.

    **Example:** `"+1 (555) 123-4567"` → `"+15551234567"`
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 8: Standardise Websites / LinkedIn
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[8]:
    st.header("\U0001f517 Standardise Websites / LinkedIn")
    st.markdown("""
    **What it does:** Normalises URLs by removing `http://`, `https://`, `www.`, and trailing slashes.

    **When to use it:** Website or LinkedIn URLs in your data are inconsistent — some have
    `https://www.`, others don't, some have trailing slashes.

    **Example (Website):** `"https://www.acme.com/"` → `"acme.com"`
    **Example (LinkedIn):** `"https://www.linkedin.com/in/johnsmith/"` → `"linkedin.com/in/johnsmith"`
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 9: Classify Seniority & Function
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[9]:
    st.header("\U0001f4bc Classify Seniority & Job Function")
    st.markdown("""
    **What it does:** Reads each person's job title and automatically assigns:
    - **Seniority level:** C-level, VP level, Director, Manager, Associate, or Other
    - **Job function:** Sales, Marketing, IT, Finance, Legal, HR, Operations, Product, etc.

    Supports English, French, Portuguese, and Spanish job titles.

    **When to use it:** You have raw job titles from Cognism/Apollo/LinkedIn and need to
    segment your list by seniority or function for targeting.

    **Example:** `"Senior Vice President, Sales"` → Seniority: `VP level`, Function: `Sales`
    `"Directeur Marketing"` → Seniority: `Director level`, Function: `Marketing`
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="cj")
    if fi:
        df = load_csv(fi)
        title_col = st.selectbox("Job title column", df.columns, key="cj_title")
        sen_col = st.selectbox("Existing seniority column (optional — improves accuracy)", ["-- None --"] + list(df.columns), key="cj_sen")
        dept_col = st.selectbox("Department column (optional — improves function detection)", ["-- None --"] + list(df.columns), key="cj_dept")
        if st.button("Classify", key="cj_run"):
            from tools.classify_jobs import classify_jobs
            sc = sen_col if sen_col != "-- None --" else None
            dc = dept_col if dept_col != "-- None --" else None
            result, summary = classify_jobs(df, title_col, sc, dc)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "classified", "classified_jobs.csv")


# ══════════════════════════════════════════════════════════
# TOOL 10: Classify Org Type
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[10]:
    st.header("\U0001f3e2 Classify Organisation Type")
    st.markdown("""
    **What it does:** Automatically tags each company with an organisation type based on
    industry, company name, job titles, and other available fields.

    **Categories include:** Commercial bank, Retail bank, Credit union, Neobank, Insurance,
    Fintech, VC/PE, Wealth management, Retailer/Merchant, Media, Government, Higher education,
    Professional services, and more.

    **When to use it:** You need to segment your contact list by the type of organisation
    for event targeting, sponsorship outreach, or reporting.

    **Example:** Company `"Stripe"` with industry `"fintech"` → `"Established fintech or solution provider"`
    Company `"HSBC"` → `"Commercial or corporate bank"`
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="co")
    if fi:
        df = load_csv(fi)
        st.info("This tool auto-detects columns like Company, Industry, Job Title, Website. The more columns your data has, the more accurate the classification.")
        if st.button("Classify", key="co_run"):
            from tools.classify_jobs import classify_org_types
            result, summary = classify_org_types(df)
            show_summary(summary)
            st.dataframe(result.head(100))
            dl(result, "classified", "classified_orgs.csv")


# ══════════════════════════════════════════════════════════
# TOOL 11: LinkedIn Links
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[11]:
    st.header("\U0001f50e LinkedIn Search Links")
    st.markdown("""
    **What it does:** Generates a clickable LinkedIn people-search URL for each person,
    using their name, job title, and company as search keywords.

    **When to use it:** You have a list of contacts without LinkedIn profile URLs and want
    quick links to find them on LinkedIn.

    **Example:** Name: `"Jane Doe"`, Title: `"VP Sales"`, Company: `"Acme Corp"` →
    `https://linkedin.com/search/results/people/?keywords=Jane+Doe+VP+Sales+Acme+Corp`
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="li")
    if fi:
        df = load_csv(fi)
        name_col = st.selectbox("Name column", df.columns, key="li_name")
        title_col = st.selectbox("Title column (optional — makes search more precise)", ["-- None --"] + list(df.columns), key="li_title")
        co_col = st.selectbox("Company column (optional — makes search more precise)", ["-- None --"] + list(df.columns), key="li_co")
        if st.button("Generate Links", key="li_run"):
            from tools.linkedin_links import add_linkedin_links
            tc = title_col if title_col != "-- None --" else None
            cc = co_col if co_col != "-- None --" else None
            result = add_linkedin_links(df, name_col, tc, cc)
            st.success(f"Generated {len(result):,} links")
            st.dataframe(result.head(100))
            dl(result, "with LinkedIn links", "linkedin_links.csv")


# ══════════════════════════════════════════════════════════
# TOOL 12: Remove Blank Rows
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[12]:
    st.header("\U0001f9f9 Remove Blank Rows")
    st.markdown("""
    **What it does:** Deletes rows that are completely empty or contain only whitespace.

    **When to use it:** Your CSV has blank rows scattered throughout (common after
    copy-pasting from spreadsheets or exporting from databases).

    **Example:** A 1,000-row file with 47 blank rows → cleaned file with 953 rows.
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="rb")
    if fi and st.button("Remove Blanks", key="rb_run"):
        from tools.remove_rows import remove_blank_rows
        df = load_csv(fi)
        result, summary = remove_blank_rows(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned", "no_blanks.csv")


# ══════════════════════════════════════════════════════════
# TOOL 13: Remove by Keywords / Flag
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[13]:
    st.header("\U0001f6ab Remove by Keywords / Flag")
    st.markdown("""
    **What it does:** Two modes:
    - **Keywords mode:** Removes rows where a column contains any of your specified keywords
    - **Flag mode:** Removes rows where a column exactly equals a flag value

    **When to use it:**
    - *Keywords:* Remove contacts with certain job titles (e.g. "intern, student, retired")
    - *Flag:* After running dedup, remove rows flagged as "yes" in a Duplicate column

    **Example (Keywords):** Column: `Job Title`, Keywords: `intern, student` → removes all interns and students
    **Example (Flag):** Column: `Is Duplicate`, Flag: `yes` → removes all rows marked as duplicates
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="rk")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Keywords", "Flag value"], key="rk_mode")
        col = st.selectbox("Column", df.columns, key="rk_col")
        if mode == "Keywords":
            kw_text = st.text_input("Keywords (comma-separated)", placeholder="e.g. intern, student, retired", key="rk_kw")
            if st.button("Remove", key="rk_run"):
                from tools.remove_rows import remove_by_keywords
                kws = [k.strip() for k in kw_text.split(",") if k.strip()]
                cleaned, removed, summary = remove_by_keywords(df, col, kws)
                show_summary(summary)
                st.dataframe(cleaned.head(100))
                dl(cleaned, "cleaned", "kw_cleaned.csv")
                if len(removed): dl(removed, "removed rows", "kw_removed.csv")
        else:
            flag = st.text_input("Flag value", placeholder="e.g. yes, duplicate, remove", key="rk_flag")
            if st.button("Remove", key="rk_run2"):
                from tools.remove_rows import remove_by_flag
                cleaned, removed, summary = remove_by_flag(df, col, flag)
                show_summary(summary)
                st.dataframe(cleaned.head(100))
                dl(cleaned, "cleaned", "flag_cleaned.csv")
                if len(removed): dl(removed, "removed rows", "flag_removed.csv")


# ══════════════════════════════════════════════════════════
# TOOL 14: Compare & Remove
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[14]:
    st.header("\u2696\ufe0f Compare & Remove")
    st.markdown("""
    **What it does:** Compares a column in your source file against a column in a lookup file,
    and removes any rows from the source that have a match in the lookup.

    **When to use it:**
    - Remove redeemed/attended contacts from an invite list
    - Suppress contacts who have opted out
    - Remove companies you've already spoken to

    **Example:** Source: `event_invites.csv` (Email column), Lookup: `already_attended.csv`
    (Email column) → removes anyone who already attended from the invite list.
    """)
    src_f = st.file_uploader("Upload SOURCE CSV (your main list)", type="csv", key="cr_src")
    lkp_f = st.file_uploader("Upload LOOKUP CSV (the suppression/removal list)", type="csv", key="cr_lkp")
    if src_f and lkp_f:
        src = load_csv(src_f); lkp = load_csv(lkp_f)
        src_col = st.selectbox("Source column to compare", src.columns, key="cr_sc")
        lkp_col = st.selectbox("Lookup column to compare against", lkp.columns, key="cr_lc")
        if st.button("Compare & Remove", key="cr_run"):
            from tools.compare_lists import compare_and_remove
            cleaned, removed, summary = compare_and_remove(src, lkp, src_col, lkp_col)
            show_summary(summary)
            st.dataframe(cleaned.head(100))
            dl(cleaned, "cleaned", "compare_cleaned.csv")
            if len(removed): dl(removed, "removed rows", "compare_removed.csv")


# ══════════════════════════════════════════════════════════
# TOOL 15: Column Remapper
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[15]:
    st.header("\U0001f500 Column Remapper")
    st.markdown("""
    **What it does:** Maps columns from a source CSV into a different target column structure.
    For each target column, you pick which source column fills it — or set a custom default value.
    Columns with matching names are auto-matched.

    **When to use it:** You have data from Cognism/Apollo with columns like `"Person Full Name"`,
    `"Company"`, `"Work Email"` and need to push it into your CRM template with `"First Name"`,
    `"Last Name"`, `"Organization"`, `"Email"`.

    **Example:** Upload your Cognism export as SOURCE and your CRM import template (even just
    a row of headers) as TARGET → visually map each column → download the remapped file.
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 16: Merge / Split Columns
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[16]:
    st.header("\U0001f517 Merge / Split Columns")
    st.markdown("""
    **What it does:** Two modes:
    - **Merge:** Combine 2+ columns into one new column with a separator
    - **Split:** Break one column into multiple new columns on a separator

    **When to use it:**
    - *Merge:* Your CRM needs a "Full Name" column but you only have "First Name" and "Last Name"
    - *Split:* Your data has "City, Country" in one column and you need them separate

    **Example (Merge):** `First Name` + `Last Name` with separator `" "` → `Full Name`: `"John Smith"`
    **Example (Split):** `Location` split on `", "` → `City`: `"London"`, `Country`: `"UK"`
    """)
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


# ══════════════════════════════════════════════════════════
# TOOL 17: Value Standardiser
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[17]:
    st.header("\U0001f3af Value Standardiser")
    st.markdown("""
    **What it does:** Matches raw, messy values in your data against a list of standard terms
    you define. Uses three matching strategies in order:
    1. **Exact match** (case-insensitive) — `"accountant"` matches `"Accountant"` → 100%
    2. **Keyword match** — `"senior auditor"` contains `"auditor"` which is an alias for `"Accountant"` → 90%
    3. **Fuzzy match** (Levenshtein) — `"acountant"` is close to `"Accountant"` → 89%

    **When to use it:** You want to standardise job titles, company names, categories, or any
    column where the same thing appears with different spellings or variations.

    **How to set up your rules CSV:**

    | Standard Job Title | Aliases |
    |---|---|
    | Accountant | auditor, bookkeeper, accounts clerk, comptable |
    | Software Engineer | developer, programmer, coder, SWE |
    | Sales Manager | account manager, sales lead, BDM |

    The "Aliases" column is optional but dramatically improves matching.
    """)
    data_f = st.file_uploader("Upload DATA CSV (your messy data)", type="csv", key="vs_data")
    rules_f = st.file_uploader("Upload RULES CSV (your standards + aliases)", type="csv", key="vs_rules")
    if data_f and rules_f:
        data_df = load_csv(data_f); rules_df = load_csv(rules_f)
        col = st.selectbox("Column to standardise", data_df.columns, key="vs_col")
        std_col = st.selectbox("Standard value column (in rules CSV)", rules_df.columns, key="vs_std")
        alias_options = ["-- None --"] + list(rules_df.columns)
        alias_col = st.selectbox("Aliases column (optional but recommended)", alias_options, key="vs_alias")
        threshold = st.slider("Fuzzy match threshold % (lower = more lenient)", 50, 100, 80, key="vs_th")
        if st.button("Standardise", key="vs_run"):
            from tools.value_standardizer import standardize_values
            ac = alias_col if alias_col != "-- None --" else None
            result, report, summary = standardize_values(data_df, col, rules_df, std_col, ac, threshold)
            show_summary(summary)
            st.subheader("Standardised Data")
            st.dataframe(result.head(100))
            dl(result, "standardised CSV", "standardised.csv")
            st.subheader("Match Report (how each unique value was matched)")
            st.dataframe(report)
            dl(report, "match report", "match_report.csv")


# ══════════════════════════════════════════════════════════
# TOOL 18: Data Migration Pipeline
# ══════════════════════════════════════════════════════════
elif tool == TOOLS[18]:
    st.header("\U0001f504 Data Migration Pipeline")
    st.markdown("""
    **What it does:** Your full **cogconv / data migration replacement** — all in one step:
    1. **Remap columns** from source format to target format
    2. **Set fixed values** for columns like Brand, Source, Event Name (same value for every row)
    3. **Auto-classify** seniority, job function, and organisation type
    4. **Standardise values** using your own rules CSV (optional)

    **When to use it:** You're importing a Cognism/Apollo pull into your master database or
    CRM and need to transform the data format, fill in fixed fields, and classify everything.

    **Example workflow:**
    - Source: `cognism_pull.csv` with columns `Person Full Name`, `Job Title`, `Company`, `Work Email`
    - Target: Your CRM template with `First Name`, `Last Name`, `Title`, `Organization`, `Email`, `Brand`, `Source`, `Seniority`
    - Map the columns visually, set Brand = `"FintechMeetup"`, Source = `"Cognism"`, tick auto-classify
    - Optionally upload a rules CSV to standardise job titles
    - Download the fully migrated, classified, standardised file ready for import
    """)
    src_f = st.file_uploader("Upload SOURCE CSV (e.g. Cognism export)", type="csv", key="mig_src")
    tgt_f = st.file_uploader("Upload TARGET template CSV (your CRM/master headers)", type="csv", key="mig_tgt")
    if src_f and tgt_f:
        src = load_csv(src_f); tgt = load_csv(tgt_f)
        src_cols = list(src.columns); tgt_cols = list(tgt.columns)

        st.subheader("Step 1: Map columns")
        st.caption("For each target column, choose which source column fills it, or set a fixed value.")
        mapping = {}; defaults = {}
        src_lower = {c.lower(): c for c in src_cols}
        for tc in tgt_cols:
            auto = src_lower.get(tc.lower(), "-- Leave empty --")
            options = ["-- Leave empty --", "-- Fixed value --"] + src_cols
            idx = options.index(auto) if auto in options else 0
            choice = st.selectbox(f"**{tc}**", options, index=idx, key=f"mig_{tc}")
            if choice == "-- Fixed value --":
                val = st.text_input(f"Value for {tc}", placeholder=f"e.g. FintechMeetup, Cognism, 2026", key=f"mig_fix_{tc}")
                defaults[tc] = val
            elif choice != "-- Leave empty --":
                mapping[tc] = choice

        st.subheader("Step 2: Auto-classify")
        st.caption("Automatically add Seniority, Job Function, and Organisation Type columns based on job titles.")
        classify = st.checkbox("Auto-classify seniority, function, org type", value=True, key="mig_cls")
        title_col = None
        if classify:
            title_col = st.selectbox("Which target column has job titles?", ["-- None --"] + tgt_cols, key="mig_tcol")
            title_col = title_col if title_col != "-- None --" else None

        st.subheader("Step 3: Standardise values (optional)")
        st.caption("Upload a rules CSV to standardise a column (e.g. job titles) during migration.")
        rules_f = st.file_uploader("Upload RULES CSV (optional)", type="csv", key="mig_rules")
        std_configs = []
        if rules_f:
            rules_df = load_csv(rules_f)
            std_target_col = st.selectbox("Target column to standardise", tgt_cols, key="mig_stcol")
            std_standard_col = st.selectbox("Standard value column (in rules)", rules_df.columns, key="mig_stdcol")
            alias_options = ["-- None --"] + list(rules_df.columns)
            std_alias_col = st.selectbox("Aliases column (optional)", alias_options, key="mig_stalias")
            std_threshold = st.slider("Fuzzy threshold %", 50, 100, 80, key="mig_stth")
            std_configs.append({
                "col": std_target_col, "standards_df": rules_df,
                "standard_col": std_standard_col,
                "aliases_col": std_alias_col if std_alias_col != "-- None --" else None,
                "threshold": std_threshold,
            })

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