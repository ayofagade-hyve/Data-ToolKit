"""Data Cleaning & File Automation Toolkit — Streamlit App (21 tools)."""

import streamlit as st
import pandas as pd
import re
from utils.io_helpers import load_csv, to_csv_bytes, generate_summary

st.set_page_config(page_title="Data Cleaning Toolkit", page_icon="\U0001f9f9", layout="wide")

# Groq API key (free, 1000 req/day)
AI_API_KEY = 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
AI_PROVIDER = "groq"
AI_MODEL = "llama-3.3-70b-versatile"

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
    "\u26a1 Formula Bar",
    "\U0001f504 Full Data Migration",
    "\U0001f501 Fuzzy Duplicate Finder",
    "\U0001f50e LinkedIn Search Links",
    "\U0001f517 Merge / Split Columns",
    "\U0001f6ab Remove by Keywords / Flag",
    "\U0001f9f9 Remove Blank Rows",
    "\U0001f464 Standardise Names",
    "\U0001f4de Standardise Phone Numbers",
    "\U0001f517 Standardise URLs",
    "\U0001f3f7\ufe0f Value Classifier",
    "\U0001f3af Value Standardiser",
]

tool = st.sidebar.radio("Choose a tool", TOOLS)

def show_summary(s):
    cols = st.columns(3)
    cols[0].metric("Rows before", s.get("Rows before", ""))
    cols[1].metric("Rows after", s.get("Rows after", ""))
    cols[2].metric("Removed / changed", s.get("Rows removed / changed", ""))
    for k, v in s.items():
        if k not in ("Tool", "Rows before", "Rows after", "Rows removed / changed"):
            st.info(f"**{k}:** {v}")

def dl(df, label, filename):
    custom_name = st.text_input(f"File name for {label}", value=filename, key=f"dl_{filename}_{label}")
    if not custom_name.endswith(".csv"):
        custom_name += ".csv"
    st.download_button(f"\u2b07\ufe0f Download {label}", to_csv_bytes(df), custom_name, "text/csv")

def get_target_columns(key_prefix):
    """Let user either upload a template CSV or type column names manually."""
    method = st.radio(
        "How do you want to define your output columns?",
        ["Upload a template CSV (uses its headers)", "Type column names manually"],
        key=f"{key_prefix}_method",
    )
    if method.startswith("Upload"):
        tgt_f = st.file_uploader("Upload template CSV (just headers is fine)", type="csv", key=f"{key_prefix}_tgt")
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


# ======================================================================
# HOME
# ======================================================================
if tool == TOOLS[0]:
    st.title("\U0001f9f9 Data Cleaning & File Automation Toolkit")
    st.markdown("""
    Welcome! This toolkit gives you **21 powerful data-cleaning tools** in one simple web app.
    No coding needed — just upload your CSV, pick a tool, configure it, and download clean results.

    Training Videos can be found [Here](https://iteevents-my.sharepoint.com/:f:/g/personal/ayo_fagade_hyve_group/IgAWjPM84OZ8QIy6vfPP-8yBAa9A-hb-FJlnzVu9BbuUegQ?e=3Zo1WV)
    """)
    st.markdown("---")
    st.subheader("\U0001f680 Getting Started")
    st.markdown("""
    1. **Pick a tool** from the sidebar on the left
    2. **Upload your CSV** file
    3. **Configure** the options
    4. **Click Run** to process
    5. **Preview** the results
    6. **Download** your clean output

    > **Tip:** Your original files are never modified. Every tool exports a new, clean file.
    """)
    st.markdown("---")
    st.subheader("\U0001f4e6 All Tools at a Glance")

    tool_cards = [
        ("\U0001f3e2", "Classify Organisation Type",
         "Automatically tags each company with an organisation type (e.g. Bank, Fintech, Insurance, VC, Retailer) based on industry, company name, job titles, and other available fields.",
         "You have 5,000 attendees and need to know how many are from banks vs fintechs vs regulators \u2014 this auto-tags them all in seconds."),
        ("\U0001f4bc", "Classify Seniority & Function",
         "Reads each person\u2019s job title and automatically assigns a **seniority level** (C-level, VP, Director, Manager, Associate, Other) and a **job function** (Sales, Marketing, IT, Finance, Legal, HR, Operations, Product, etc.).",
         "You need to filter an event list to only VPs and above in Sales \u2014 this classifies everyone so you can filter instantly."),
        ("\U0001f500", "Column Remapper",
         "Maps columns from a source CSV into a different output structure. For each output column, you pick which source column fills it \u2014 or set a custom default value. Auto-matches columns with the same name. Also has a **Reorder & Remove** mode to quickly keep only the columns you need.",
         "Your event platform exports \u2018Organisation\u2019 but your CRM needs \u2018Company Name\u2019 \u2014 this remaps it without manual copy-pasting."),
        ("\U0001f4ce", "Combine CSVs",
         "Merges multiple CSV files into a single file, stacking all rows together. Handles mismatched columns gracefully.",
         "You have 6 monthly attendee exports and need them all in one master file \u2014 just upload them all and combine."),
        ("\u2696\ufe0f", "Compare & Remove",
         "Compares a column in your source file against a column in a lookup file, and removes any matching rows from the source.",
         "You have a \u2018do not contact\u2019 list and need to remove those people from your outreach file \u2014 upload both and it strips them out."),
        ("\U0001f4ca", "Data Quality Report",
         "Generates a full quality report for every column in your CSV \u2014 completeness %, blank count, unique values, top 5 values, and sample data. Instantly spots problem columns before you start cleaning.",
         "You receive a raw data file and need to know which columns are 90% blank before running a migration \u2014 this tells you in seconds."),
        ("\U0001f50d", "Deduplicate vs Master List",
         "Compares a new contact list against your master database and removes anyone who already exists. Matches on **4 keys**: Email, LinkedIn URL, Name+Company, Name+Website.",
         "Before importing new leads into your CRM, check them against your existing database to avoid duplicates."),
        ("\U0001f310", "Extract Company Domains",
         "Finds the most common non-personal email domain per company. Ignores personal domains like gmail.com, yahoo.com, hotmail.com.",
         "You need a list of company domains for ad targeting \u2014 this pulls the corporate domain from your contact emails."),
        ("\U0001f524", "Fix Encoding (Mojibake)",
         "Repairs garbled/broken characters caused by encoding mismatches. Fixes broken accented characters back to their correct form.",
         "Your CSV export has names showing garbled characters \u2014 this fixes all of them automatically."),
        ("\u26a1", "Formula Bar",
         "Type plain English commands like \u2018remove rows where email contains test\u2019 and they execute instantly. "
         "Built-in regex parser handles 15+ patterns for free; Gemini AI handles anything else. Includes undo, command history, and chaining.",
         "Type \u2018delete rows where country is empty\u2019 \u2014 done. Then \u2018uppercase company\u2019 \u2014 done. Then \u2018sort by last name a-z\u2019 \u2014 done."),
        ("\U0001f504", "Full Data Migration",
         "A complete data transformation pipeline \u2014 all in one step. Combines **7 stages**: column remapping, fixed values, conditional IF/THEN/ELSE rules, auto-classification, value mapping, suppression splitting, and column cleanup.",
         "You receive a raw attendee export and need to remap it into CRM format, tag attendees by region, auto-classify job titles, reclassify values, separate opt-outs, and drop unwanted columns \u2014 all in one click."),
        ("\U0001f501", "Fuzzy Duplicate Finder",
         "Scans a single column for near-duplicate values using fuzzy string matching (Levenshtein distance). Flags each row as \u2018Unique\u2019 or \u2018Duplicate\u2019 with the match percentage.",
         "You suspect your company list has duplicates like \u2018JP Morgan\u2019 and \u2018JPMorgan Chase\u2019 \u2014 this finds and flags them."),
        ("\U0001f50e", "LinkedIn Search Links",
         "Generates a clickable LinkedIn people-search URL for each person, using their name, job title, and company as search keywords.",
         "You have a list of 200 prospects and need to quickly find their LinkedIn profiles \u2014 this builds a search link for each one."),
        ("\U0001f517", "Merge / Split Columns",
         "**Merge** combines 2+ columns into one new column with a separator. **Split** breaks one column into multiple new columns on a separator.",
         "Merge \u2018First Name\u2019 and \u2018Last Name\u2019 into \u2018Full Name\u2019, or split \u2018London, UK\u2019 into separate City and Country columns."),
        ("\U0001f6ab", "Remove by Keywords / Flag",
         "**Keywords mode** removes rows where a column contains any of your specified keywords. **Flag mode** removes rows where a column exactly equals a flag value.",
         "Remove all rows where the Job Title contains \u2018Student\u2019, \u2018Intern\u2019, or \u2018Retired\u2019."),
        ("\U0001f9f9", "Remove Blank Rows",
         "Deletes rows that are completely empty or contain only whitespace. Quick cleanup for messy exports.",
         "Your CRM export has 500 blank rows scattered throughout \u2014 this strips them all out instantly."),
        ("\U0001f464", "Standardise Names",
         "Splits a \u2018Full Name\u2019 column into separate \u2018First Name\u2019 and \u2018Last Name\u2019 columns. Also extracts names from email addresses (e.g. john.smith@acme.com \u2192 John Smith).",
         "Your list has \u2018Gary Dempsey\u2019 in one column but your CRM needs First Name and Last Name separately."),
        ("\U0001f4de", "Standardise Phone Numbers",
         "Strips all formatting from phone numbers, keeping only digits and the + symbol.",
         "Your data has phone numbers like \u2018(+44) 020-7946 0958\u2019 \u2014 this normalises them all to \u2018+4402079460958\u2019."),
        ("\U0001f517", "Standardise URLs",
         "Normalises URLs by removing http://, https://, www., and trailing slashes.",
         "You have \u2018https://www.google.com/\u2019 and \u2018google.com\u2019 \u2014 this standardises both to \u2018google.com\u2019."),
        ("\U0001f3f7\ufe0f", "Value Classifier",
         "Upload any spreadsheet, pick a column, and see every unique value with its count. Then map each value to a new category \u2014 either one-by-one in an editable table, or by creating named groups and assigning multiple values at once. No AI, no setup \u2014 just simple, manual control.",
         "Your Industry column has \u2018Fintech\u2019, \u2018InsurTech\u2019, \u2018SaaS\u2019, \u2018PaaS\u2019 \u2014 map them to \u2018Financial Services\u2019 and \u2018Software\u2019 in seconds."),
        ("\U0001f3af", "Value Standardiser",
         "Matches raw, messy values against a list of standard terms you define. Uses exact match, keyword match, and fuzzy match (Levenshtein distance). Also has **Find & Replace** and **Case Converter** modes.",
         "Your Country column has \u2018UK\u2019, \u2018United Kingdom\u2019, \u2018england\u2019, \u2018Great Britain\u2019 \u2014 upload a standards list and it maps them all to \u2018United Kingdom\u2019."),
    ]

    for i in range(0, len(tool_cards), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(tool_cards):
                emoji, name, desc, example = tool_cards[i + j]
                with col:
                    with st.container(border=True):
                        st.markdown(f"### {emoji} {name}")
                        st.markdown(desc)
                        st.caption(f"\U0001f4a1 {example}")

    st.markdown("---")
    st.subheader("\U0001f4a1 Tips")
    st.markdown("""
    - **Column auto-detection**: Many tools automatically find columns like Email, Company, Job Title by checking common names and aliases
    - **Fuzzy matching**: Uses Levenshtein distance — adjust the threshold slider to be stricter (100% = exact only) or more lenient (50% = loose matching)
    - **Large files**: All tools handle 100K+ rows. Fuzzy matching may take a moment on very large datasets
    - **Encoding issues?** Run "Fix Encoding" first before other tools if you see garbled characters
    """)

# ======================================================================
# Classify Organisation Type
# ======================================================================
elif tool == TOOLS[1]:
    st.header("\U0001f3e2 Classify Organisation Type")
    st.markdown("""
    **What it does:** Automatically tags each company with an organisation type based on
    industry, company name, job titles, and other available fields.

    **Categories include:** Commercial bank, Retail bank, Credit union, Neobank, Insurance,
    Fintech, VC/PE, Wealth management, Retailer/Merchant, Media, Government, Higher education,
    Professional services, and more.

    **When to use it:** You need to segment your contact list by the type of organisation
    for targeting, outreach, or reporting.

    **Example:** Company `"Stripe"` with industry `"fintech"` -> `"Established fintech or solution provider"`
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

# ======================================================================
# Classify Seniority & Job Function
# ======================================================================
elif tool == TOOLS[2]:
    st.header("\U0001f4bc Classify Seniority & Job Function")
    st.markdown("""
    **What it does:** Reads each person's job title and automatically assigns:
    - **Seniority level:** C-level, VP level, Director, Manager, Associate, or Other
    - **Job function:** Sales, Marketing, IT, Finance, Legal, HR, Operations, Product, etc.

    Supports English, French, Portuguese, and Spanish job titles.

    **Example:** `"Senior Vice President, Sales"` -> Seniority: `VP level`, Function: `Sales`
    """)
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

# ======================================================================
# Column Remapper (+ Reorder & Remove mode)
# ======================================================================
elif tool == TOOLS[3]:
    st.header("\U0001f500 Column Remapper")
    st.markdown("""
    **What it does:** Maps columns from a source CSV into a different output structure.
    For each output column, you pick which source column fills it — or set a custom default value.
    Columns with matching names are auto-matched.

    You can either **upload a template CSV** (just the headers row) or **type your output
    column names** manually.

    **Example:** Your data has `"Person Full Name"`, `"Company"`, `"Work Email"` and you need
    `"First Name"`, `"Last Name"`, `"Organization"`, `"Email"` — just map them visually.
    """)
    src_f = st.file_uploader("Upload SOURCE CSV (your data)", type="csv", key="rm_src")
    if src_f:
        src = load_csv(src_f)
        src_cols = list(src.columns)

        mode = st.radio("Mode", ["Remap to a new column structure", "Reorder & remove columns (keep what you need)"], key="rm_mode")

        if mode.startswith("Remap"):
            st.subheader("Define your output columns")
            tgt_cols = get_target_columns("rm")
            if tgt_cols:
                st.subheader("Map each output column to a source column")
                mapping = {}; defaults = {}
                src_lower = {c.lower(): c for c in src_cols}
                for tc in tgt_cols:
                    auto = src_lower.get(tc.lower(), "-- Leave empty --")
                    options = ["-- Leave empty --", "-- Custom default --"] + src_cols
                    idx = options.index(auto) if auto in options else 0
                    choice = st.selectbox(f"Output: **{tc}**", options, index=idx, key=f"rm_{tc}")
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
        else:
            st.subheader("Select and reorder columns")
            st.caption("Pick the columns you want to keep, in the order you want them. Everything else will be dropped.")
            selected = st.multiselect("Columns to keep (in order)", options=src_cols, default=src_cols, key="rm_reorder_cols")
            if selected:
                for i, cn in enumerate(selected, 1):
                    st.text(f"  {i}. {cn}")
                if st.button("Apply & Preview", key="rm_reorder_run"):
                    result = src[selected].copy()
                    st.success(f"Kept {len(selected)} columns, removed {len(src_cols) - len(selected)}")
                    st.dataframe(result.head(100))
                    dl(result, "reordered CSV", "columns_reordered.csv")
            else:
                st.warning("Select at least one column.")

# ======================================================================
# Combine CSVs
# ======================================================================
elif tool == TOOLS[4]:
    st.header("\U0001f4ce Combine CSVs")
    st.markdown("""
    **What it does:** Merges multiple CSV files into a single file, stacking all rows together.

    **When to use it:** You have data split across multiple exports — e.g. separate regional
    lists or monthly contact files that need combining.

    **Example:** Upload `contacts_jan.csv`, `contacts_feb.csv`, `contacts_mar.csv` ->
    one `combined.csv` with all rows.
    """)
    files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True, key="combine")
    if files and st.button("Combine", key="combine_run"):
        from tools.combine_csvs import combine_csvs
        result, summary = combine_csvs(files)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "combined CSV", "combined.csv")

# ======================================================================
# Compare & Remove
# ======================================================================
elif tool == TOOLS[5]:
    st.header("\u2696\ufe0f Compare & Remove")
    st.markdown("""
    **What it does:** Compares a column in your source file against a column in a lookup file,
    and removes any rows from the source that have a match in the lookup.

    **When to use it:** Remove people who already attended from an invite list, suppress
    contacts who opted out, or remove companies you've already contacted.

    **Example:** Source: `event_invites.csv` (Email), Lookup: `already_attended.csv` (Email)
    -> removes anyone who already attended.
    """)
    src_f = st.file_uploader("Upload SOURCE CSV (your main list)", type="csv", key="cr_src")
    lkp_f = st.file_uploader("Upload LOOKUP CSV (the removal list)", type="csv", key="cr_lkp")
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

# ======================================================================
# Data Quality Report  ← NEW
# ======================================================================
elif tool == TOOLS[6]:
    st.header("\U0001f4ca Data Quality Report")
    st.markdown("""
    **What it does:** Generates a full quality report for every column in your CSV —
    completeness %, blank count, unique values, top 5 values, and a sample.

    **When to use it:** Before running any migration or cleanup, check which columns
    are mostly empty, which have messy data, and which are ready to go.

    **Example:** You receive a raw export with 40 columns. This tells you instantly that
    3 columns are 90%+ blank and can be dropped, and 5 columns need standardisation.
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="dq")
    if fi:
        df = load_csv(fi)
        if st.button("Generate Report", key="dq_run"):
            rows = len(df)
            report_data = []
            for col_name in df.columns:
                series = df[col_name].fillna("").astype(str).str.strip()
                non_blank = series[series != ""]
                blank_count = rows - len(non_blank)
                completeness = round((len(non_blank) / rows) * 100, 1) if rows > 0 else 0
                unique_count = non_blank.nunique()
                top_values = non_blank.value_counts().head(5)
                top_str = ", ".join(f"{v} ({c})" for v, c in top_values.items())
                sample = non_blank.iloc[0] if len(non_blank) > 0 else ""
                report_data.append({
                    "Column": col_name,
                    "Completeness %": completeness,
                    "Filled Rows": f"{len(non_blank):,}",
                    "Blank Rows": f"{blank_count:,}",
                    "Unique Values": f"{unique_count:,}",
                    "Top 5 Values": top_str,
                    "Sample": str(sample)[:80],
                })
            report_df = pd.DataFrame(report_data)

            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Total Rows", f"{rows:,}")
            mc2.metric("Total Columns", f"{len(df.columns):,}")
            mc3.metric("Avg Completeness", f"{report_df['Completeness %'].mean():.1f}%")

            low_q = report_df[report_df["Completeness %"] < 50]
            if len(low_q):
                st.warning(f"\u26a0\ufe0f {len(low_q)} column(s) below 50% complete:")
                for _, r in low_q.iterrows():
                    st.markdown(f"- **{r['Column']}** — {r['Completeness %']}% ({r['Blank Rows']} blanks)")

            st.subheader("Full Report")
            st.dataframe(report_df, use_container_width=True)
            dl(report_df, "quality report", "data_quality_report.csv")

# ======================================================================
# Deduplicate vs Master List
# ======================================================================
elif tool == TOOLS[7]:
    st.header("\U0001f50d Deduplicate vs Master List")
    st.markdown("""
    **What it does:** Compares a new contact list against your master database and removes
    anyone who already exists. Matches on **4 keys** (in order):
    1. **Email** (exact)  2. **LinkedIn URL** (normalised)
    3. **First + Last Name + Company**  4. **First + Last Name + Website**

    **Example:** Upload `master.csv` (10,000 rows) and `new_contacts.csv` (500 rows) ->
    get ~350 truly new contacts + a report showing which 150 were duplicates and why.
    """)
    master_f = st.file_uploader("Upload MASTER CSV (your existing database)", type="csv", key="dm_master")
    check_f = st.file_uploader("Upload file to CHECK (new contacts)", type="csv", key="dm_check")
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

# ======================================================================
# Extract Company Domains
# ======================================================================
elif tool == TOOLS[8]:
    st.header("\U0001f310 Extract Company Domains")
    st.markdown("""
    **What it does:** Finds the most common non-personal email domain per company.
    Ignores gmail.com, yahoo.com, hotmail.com, etc.

    **Example:** 3 people at "Acme Corp" with `john@acme.com`, `jane@acme.com`,
    `bob@gmail.com` -> assigns `acme.com` as Acme Corp's domain.
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

# ======================================================================
# Fix Encoding (Mojibake)
# ======================================================================
elif tool == TOOLS[9]:
    st.header("\U0001f524 Fix Encoding (Mojibake)")
    st.markdown("""
    **What it does:** Repairs garbled characters caused by encoding mismatches.
    Common fixes include broken accented characters in European names and addresses.

    **When to use it:** Your CSV has weird characters in names or addresses — especially
    common with European-language data exported from older systems.
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="enc")
    if fi and st.button("Fix Encoding", key="enc_run"):
        from tools.clean_encoding import clean_encoding
        df = load_csv(fi)
        result, summary = clean_encoding(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned CSV", "encoding_fixed.csv")

# ======================================================================
# Formula Bar  ← NEW
# ======================================================================
elif tool == TOOLS[10]:
    st.header("\u26a1 Formula Bar")
    st.markdown("""
    **What it does:** Type plain English commands to clean your data — no coding needed.

    The built-in regex parser handles **15+ command patterns instantly for free**.
    For complex or unusual requests, Gemini AI kicks in automatically.

    **Examples:** `remove rows where email contains "test"` · `uppercase company` ·
    `replace "UK" with "United Kingdom" in country` · `sort by last name a-z`
    """)

    # Sidebar: model override
    st.sidebar.markdown("---")
    st.sidebar.subheader("\u26a1 Formula Bar Settings")
    gemini_model = st.sidebar.selectbox(
        "AI Model (for complex commands)",
        ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0, key="fb_gemini_model",
        help="Only used when the regex parser can't understand your command",
    )
    st.sidebar.success("\u2705 AI fallback enabled (API key built in)")

    fi = st.file_uploader("Upload CSV", type="csv", key="fb_upload")
    if fi:
        # Initialise session state
        if "fb_df" not in st.session_state or st.session_state.get("fb_file_name") != fi.name:
            st.session_state.fb_df = load_csv(fi)
            st.session_state.fb_file_name = fi.name
            st.session_state.fb_history = []
            st.session_state.fb_undo_stack = []

        current_df = st.session_state.fb_df

        st.markdown(f"**{len(current_df):,}** rows \u00d7 **{len(current_df.columns)}** columns")
        with st.expander("\U0001f4cb Preview data (first 10 rows)", expanded=False):
            st.dataframe(current_df.head(10), use_container_width=True)

        st.markdown("---")
        command_text = st.text_input(
            "\U0001f52e Type your command",
            placeholder='e.g. remove rows where email contains "test"',
            key="fb_command",
        )

        col_run, col_undo = st.columns([1, 1])
        run_pressed = col_run.button("\u25b6\ufe0f Run", key="fb_run", type="primary", use_container_width=True)
        undo_pressed = col_undo.button(
            "\u21a9\ufe0f Undo last", key="fb_undo",
            disabled=len(st.session_state.fb_undo_stack) == 0,
            use_container_width=True,
        )

        # Undo
        if undo_pressed and st.session_state.fb_undo_stack:
            st.session_state.fb_df = st.session_state.fb_undo_stack.pop()
            if st.session_state.fb_history:
                undone = st.session_state.fb_history.pop()
                st.success(f"\u21a9\ufe0f Undone: {undone[0]}")
            else:
                st.success("\u21a9\ufe0f Undone last command")
            st.rerun()

        # Run command
        if run_pressed and command_text:
            from utils.nl_parser import parse_command
            from tools.formula_engine import execute_command

            cmd = parse_command(command_text, list(current_df.columns), GEMINI_API_KEY)

            if cmd.error:
                st.error(cmd.error)
            else:
                source_label = "\U0001f9e0 AI" if cmd.source == "ai" else "\u26a1 Regex"
                conf_pct = int(cmd.confidence * 100)
                st.caption(f"Parsed by: **{source_label}** | Action: `{cmd.action}` | Confidence: {conf_pct}%")

                result_df, description, rows_affected = execute_command(current_df, cmd)
                st.markdown(description)

                if cmd.action != "count":
                    st.session_state.fb_undo_stack.append(current_df.copy())
                    if len(st.session_state.fb_undo_stack) > 20:
                        st.session_state.fb_undo_stack.pop(0)
                    st.session_state.fb_df = result_df
                    st.session_state.fb_history.append((command_text, description, rows_affected))

                    if len(result_df) != len(current_df):
                        delta = len(result_df) - len(current_df)
                        mc1, mc2, mc3 = st.columns(3)
                        mc1.metric("Before", f"{len(current_df):,}")
                        mc2.metric("After", f"{len(result_df):,}")
                        mc3.metric("Changed", f"{delta:+,}")

                    st.dataframe(result_df.head(50), use_container_width=True)
                    dl(result_df, "formula result", "formula_result.csv")

        # Command history
        if st.session_state.fb_history:
            st.markdown("---")
            with st.expander(f"\U0001f4dc Command History ({len(st.session_state.fb_history)} commands)", expanded=False):
                for i, (cmd_text, desc, affected) in enumerate(reversed(st.session_state.fb_history), 1):
                    step_num = len(st.session_state.fb_history) - i + 1
                    st.markdown(f"**Step {step_num}:** `{cmd_text}`")
                    st.caption(f"  {desc} ({affected:,} rows affected)")

        # Example commands
        st.markdown("---")
        with st.expander("\U0001f4a1 Example Commands (no API key needed)", expanded=False):
            from utils.nl_parser import EXAMPLE_COMMANDS
            st.markdown("| Category | Command |")
            st.markdown("|----------|---------|")
            for category, example in EXAMPLE_COMMANDS:
                st.markdown(f"| {category} | `{example}` |")
            st.info(
                "\U0001f4a1 **Tip:** These all work with the built-in regex parser — no API needed. "
                "For more complex commands like 'remove all European contacts' or "
                "'clean up the phone numbers', Gemini AI kicks in automatically."
            )

# ======================================================================
# Full Data Migration
# ======================================================================
elif tool == TOOLS[11]:
    st.header("\U0001f504 Full Data Migration")
    st.markdown("""
    **What it does:** Transforms your raw data into a clean, ready-to-import format — all in one go.

    | Step | What happens | Example |
    |------|-------------|---------|
    | **1. Column Mapping** | Match source columns to output columns | *"Company Name" -> "Organisation"* |
    | **2. Fixed Values** | Set columns that are the same on every row | *Brand = "My Event"* |
    | **3. Conditional Rules** | Set values based on IF / THEN / ELSE logic | *IF Country = "UK" -> Region = "Domestic"* |
    | **4. Auto-Classification** | Auto-tag seniority, job function & org type | *"VP of Sales" -> Seniority: VP, Function: Sales* |
    | **5. Value Mapping** | Reclassify values in any column using an editable table | *"Fintech" -> "Financial Services"* |
    | **6. Suppression Split** | Separate opt-outs/unsubscribes into a different file | *Opted-out contacts -> separate CSV* |
    | **7. Column Cleanup** | Drop unwanted columns from the final output | *Remove "Org Type", keep only import-ready fields* |
    """)
    src_f = st.file_uploader("Upload SOURCE CSV (your raw data)", type="csv", key="mig_src")
    if src_f:
        src = load_csv(src_f)
        src_cols = list(src.columns)

        st.subheader("Step 1: Define your output columns")
        tgt_cols = get_target_columns("mig")

        if tgt_cols:
            st.subheader("Step 2: Map columns & set fixed values")
            st.caption("For each output column, choose a source column, set a fixed value, or leave empty.")
            with st.expander("\u26a0\ufe0f Fields you should NOT map (DNI guidance)"):
                st.markdown("""
                **Do Not Import (DNI)** — leave these unmapped, they're managed by your target system:
                - **Record owner / assigned to** — set by assignment rules
                - **Contact status / lead status** — set by workflow automation
                - **Opt-out / unsubscribe flags** — use Suppression Split in Step 6 instead
                - **Activity dates** (last contacted, last modified) — auto-tracked
                - **Record IDs / internal IDs** — auto-generated, never import
                - **Duplicate check flags** — handled by your dedup process

                Simply leave these as "-- Leave empty --" below.
                """)

            mapping = {}; defaults = {}
            src_lower = {c.lower(): c for c in src_cols}
            for tc in tgt_cols:
                auto = src_lower.get(tc.lower(), "-- Leave empty --")
                options = ["-- Leave empty --", "-- Fixed value --"] + src_cols
                idx = options.index(auto) if auto in options else 0
                choice = st.selectbox(f"**{tc}**", options, index=idx, key=f"mig_{tc}")
                if choice == "-- Fixed value --":
                    val = st.text_input(f"Value for {tc}", placeholder="Same value for every row", key=f"mig_fix_{tc}")
                    defaults[tc] = val
                elif choice != "-- Leave empty --":
                    mapping[tc] = choice

            st.subheader("Step 3: Conditional rules (optional)")
            st.caption("Check your **source/input** columns, then write values into your **output** columns.")
            st.info("Example: IF source column 'STS26 Ticket Type' contains 'Attendee' THEN set output column 'GLOBAL_Previous event attendance' to ';Shoptalk Luxe 2026'")
            st.warning("\u26a0\ufe0f **Rule order matters:** Later rules can overwrite values set by earlier rules on the same output column.")
            num_rules = st.number_input("Number of conditional rules", 0, 20, 0, key="mig_nrules")
            conditional_rules = []
            for i in range(int(num_rules)):
                st.markdown(f"---\n**Rule {i+1}**")
                c1, c2, c3 = st.columns(3)
                r_col = c1.selectbox("IF source column", src_cols, key=f"mig_rcol_{i}")
                r_op = c2.selectbox("Operator", ["equals", "contains", "not_empty", "is_empty"], key=f"mig_rop_{i}")
                r_val = c3.text_input("Value", key=f"mig_rval_{i}", disabled=(r_op in ("not_empty", "is_empty")))
                c4, c5 = st.columns(2)
                r_out_col = c4.selectbox("THEN set output column", tgt_cols, key=f"mig_routcol_{i}")
                r_out_val = c5.text_input("THEN value", key=f"mig_routval_{i}")
                c6, c7 = st.columns(2)
                r_else_val = c6.text_input("ELSE value (optional)", key=f"mig_relse_{i}")
                r_mode = c7.selectbox("Write mode", [
                    "Overwrite always", "Only fill blanks", "Append with semicolon (;value;value)"
                ], key=f"mig_rmode_{i}")
                mode_map = {"Overwrite always": "overwrite", "Only fill blanks": "fill_blank", "Append with semicolon (;value;value)": "append_semicolon"}
                conditional_rules.append({
                    "col": r_col, "operator": r_op, "value": r_val,
                    "out_col": r_out_col, "out_val": r_out_val,
                    "else_val": r_else_val, "mode": mode_map[r_mode],
                })

            st.subheader("Step 4: Auto-classify (optional)")
            st.caption("Automatically add Seniority, Job Function, and Organisation Type columns.")
            classify = st.checkbox("Auto-classify seniority, function, and org type", value=True, key="mig_cls")
            title_col = None
            if classify:
                title_col = st.selectbox("Which output column has job titles?", ["-- None --"] + tgt_cols, key="mig_tcol")
                title_col = title_col if title_col != "-- None --" else None

            st.subheader("Step 5: Value mapping (optional)")
            st.caption("Reclassify values in any output column. Select columns to map, then define what each unique value should become.")
            mappable_cols = [tc for tc in tgt_cols if tc in mapping]
            value_map_cols = st.multiselect("Which output columns do you want to remap values in?", options=mappable_cols, key="mig_vm_cols")
            value_mappings = {}
            for vm_col in value_map_cols:
                src_col_name = mapping[vm_col]
                col_data = src[src_col_name].fillna("(blank)").astype(str)
                vc = col_data.value_counts().reset_index()
                vc.columns = ["Original Value", "Count"]
                vc = vc.sort_values("Original Value").reset_index(drop=True)
                with st.expander(f"\U0001f3f7\ufe0f Map values for **{vm_col}** ({len(vc)} unique values from source column \"{src_col_name}\")"):
                    edit_df = vc.copy()
                    edit_df["Map To"] = ""
                    edited = st.data_editor(
                        edit_df,
                        column_config={
                            "Original Value": st.column_config.TextColumn("Original Value", disabled=True),
                            "Count": st.column_config.NumberColumn("Count", disabled=True),
                            "Map To": st.column_config.TextColumn("Map To", help="New value. Leave blank to keep original."),
                        },
                        hide_index=True, use_container_width=True, num_rows="fixed", key=f"mig_vm_{vm_col}",
                    )
                    col_mapping_inner = {}
                    for _, row in edited.iterrows():
                        map_to = str(row["Map To"]).strip()
                        if map_to and map_to != "nan":
                            col_mapping_inner[row["Original Value"]] = map_to
                    if col_mapping_inner:
                        value_mappings[vm_col] = col_mapping_inner
                        st.success(f"{len(col_mapping_inner)} value(s) will be remapped in **{vm_col}**")

            st.subheader("Step 6: Suppression split (optional)")
            st.caption("Separate opt-outs, unsubscribes, or other exclusions into a different file so they're not mixed into your normal import.")
            num_sup = st.number_input("Number of suppression rules", 0, 10, 0, key="mig_nsup")
            suppression_rules = []
            for i in range(int(num_sup)):
                sc1, sc2, sc3 = st.columns(3)
                s_col = sc1.selectbox(f"Suppression column {i+1}", tgt_cols, key=f"mig_supcol_{i}")
                s_op = sc2.selectbox(f"Operator {i+1}", ["equals", "contains", "not_empty"], key=f"mig_supop_{i}")
                s_val = sc3.text_input(f"Value {i+1}", key=f"mig_supval_{i}", disabled=(s_op == "not_empty"))
                suppression_rules.append({"col": s_col, "operator": s_op, "value": s_val})

            st.subheader("Step 7: Column cleanup (optional)")
            st.caption("Drop unwanted columns from the final output — useful for removing classification columns, intermediate fields, or anything your import doesn't need.")
            cleanup_mode = st.radio("Cleanup mode:", ["Remove selected columns", "Keep only selected columns"], horizontal=True, key="mig_cleanup_mode")

            if st.button("\U0001f680 Run Migration", key="mig_run"):
                from tools.data_migration import run_migration
                result, suppressed, std_report, rule_applied, rule_skipped, summary = run_migration(
                    src, tgt_cols, mapping, defaults, conditional_rules,
                    classify, title_col, [], suppression_rules)
                for vm_col, vm_map in value_mappings.items():
                    if vm_col in result.columns:
                        result[vm_col] = (
                            result[vm_col].fillna("(blank)").astype(str)
                            .map(lambda v, m=vm_map: m.get(v, v))
                            .replace("(blank)", pd.NA)
                        )
                st.session_state["mig_result_raw"] = result.copy()
                st.session_state["mig_suppressed"] = suppressed
                st.session_state["mig_std_report"] = std_report
                st.session_state["mig_rule_applied"] = rule_applied
                st.session_state["mig_rule_skipped"] = rule_skipped
                st.session_state["mig_summary"] = summary
                st.session_state["mig_value_mappings"] = value_mappings
                st.session_state["mig_col_mapping"] = mapping
                st.session_state["mig_defaults"] = defaults
                st.session_state["mig_tgt_cols"] = tgt_cols
                st.session_state["mig_ran"] = True

            if st.session_state.get("mig_ran"):
                result = st.session_state["mig_result_raw"].copy()
                suppressed = st.session_state["mig_suppressed"]
                std_report = st.session_state["mig_std_report"]
                rule_applied = st.session_state["mig_rule_applied"]
                rule_skipped = st.session_state["mig_rule_skipped"]
                summary = st.session_state["mig_summary"]
                value_mappings = st.session_state["mig_value_mappings"]
                col_mapping = st.session_state["mig_col_mapping"]
                defaults_saved = st.session_state["mig_defaults"]
                tgt_cols_saved = st.session_state["mig_tgt_cols"]

                show_summary(summary)

                st.subheader("\U0001f9f9 Step 7: Column Cleanup")
                all_result_cols = list(result.columns)
                if cleanup_mode == "Remove selected columns":
                    cols_to_remove = st.multiselect("Select columns to **remove** from the final output:", options=all_result_cols, key="mig_cols_remove")
                    if cols_to_remove:
                        result = result.drop(columns=cols_to_remove)
                        st.info(f"Removed {len(cols_to_remove)} column(s): {', '.join(cols_to_remove)}")
                else:
                    cols_to_keep = st.multiselect("Select columns to **keep** in the final output (all others will be dropped):", options=all_result_cols, default=all_result_cols, key="mig_cols_keep")
                    if cols_to_keep and len(cols_to_keep) < len(all_result_cols):
                        removed_cols = [c for c in all_result_cols if c not in cols_to_keep]
                        result = result[cols_to_keep]
                        st.info(f"Keeping {len(cols_to_keep)} column(s), removed: {', '.join(removed_cols)}")

                with st.expander("\U0001f4cb Migration Preview Report"):
                    st.markdown("**Column Mapping:**")
                    for tc in tgt_cols_saved:
                        if tc in col_mapping:
                            st.markdown(f"- {col_mapping[tc]} -> **{tc}**")
                        elif tc in defaults_saved and defaults_saved[tc]:
                            st.markdown(f"- *(fixed)* **{tc}** = `{defaults_saved[tc]}`")
                        else:
                            st.markdown(f"- *(empty)* **{tc}**")
                    if rule_applied:
                        st.markdown("**Conditional Rules Applied:**")
                        st.dataframe(pd.DataFrame(rule_applied))
                    if rule_skipped:
                        st.markdown("**\u26a0\ufe0f Conditional Rules SKIPPED (check these!):**")
                        st.dataframe(pd.DataFrame(rule_skipped))
                    if value_mappings:
                        st.markdown("**Value Mappings Applied:**")
                        for vm_col, vm_map in value_mappings.items():
                            st.markdown(f"- **{vm_col}**: {len(vm_map)} value(s) remapped")
                            with st.expander(f"Details for {vm_col}"):
                                st.json(vm_map)

                st.subheader("\u2705 Migrated Data")
                st.dataframe(result.head(100))
                dl(result, "migrated CSV", "migrated.csv")

                if len(suppressed):
                    st.subheader(f"\U0001f6ab Suppressed / Opt-Out Rows ({len(suppressed):,})")
                    st.caption("These rows were separated. Import separately or keep for records.")
                    st.dataframe(suppressed.head(100))
                    dl(suppressed, "suppressed CSV", "suppressed.csv")

                if len(std_report):
                    st.subheader("Standardisation Report")
                    st.dataframe(std_report)
                    dl(std_report, "standardisation report", "std_report.csv")

                if rule_skipped:
                    st.error(f"\u26a0\ufe0f {len(rule_skipped)} conditional rule(s) were SKIPPED because columns were missing. Check the Migration Preview Report above.")

# ======================================================================
# Fuzzy Duplicate Finder (with spinner + warning)
# ======================================================================
elif tool == TOOLS[12]:
    st.header("\U0001f501 Fuzzy Duplicate Finder")
    st.markdown("""
    **What it does:** Scans a column for near-duplicate values using fuzzy string matching.
    Flags each row as "Unique" or "Duplicate" with the match % and which row it matched.

    **Example:** At 90% threshold, `"Acme Corporation"` and `"Acme Corp"` = duplicate (92%).
    `"Acme Corp"` and `"Ajax Corp"` = unique (67%).

    **Tip:** 95% = strict, 80% = loose.
    """)
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
            show_summary(summary)
            st.dataframe(result.head(200))
            dl(result, "results with flags", "fuzzy_dedup.csv")

# ======================================================================
# LinkedIn Search Links
# ======================================================================
elif tool == TOOLS[13]:
    st.header("\U0001f50e LinkedIn Search Links")
    st.markdown("""
    **What it does:** Generates a clickable LinkedIn people-search URL for each person.

    **Example:** Name: `"Jane Doe"`, Title: `"VP Sales"`, Company: `"Acme Corp"` ->
    LinkedIn search URL with those keywords.
    """)
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

# ======================================================================
# Merge / Split Columns
# ======================================================================
elif tool == TOOLS[14]:
    st.header("\U0001f517 Merge / Split Columns")
    st.markdown("""
    **What it does:**
    - **Merge:** Combine 2+ columns into one with a separator
    - **Split:** Break one column into multiple on a separator

    **Example (Merge):** `First Name` + `Last Name` -> `Full Name`: `"John Smith"`
    **Example (Split):** `Location` on `", "` -> `City`: `"London"`, `Country`: `"UK"`
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

# ======================================================================
# Remove by Keywords / Flag
# ======================================================================
elif tool == TOOLS[15]:
    st.header("\U0001f6ab Remove by Keywords / Flag")
    st.markdown("""
    **What it does:**
    - **Keywords:** Remove rows where a column contains any keyword you specify
    - **Flag:** Remove rows where a column exactly equals a value

    **Example (Keywords):** Column: `Job Title`, Keywords: `intern, student` -> removes all interns/students
    **Example (Flag):** Column: `Is Duplicate`, Flag: `yes` -> removes flagged rows
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

# ======================================================================
# Remove Blank Rows
# ======================================================================
elif tool == TOOLS[16]:
    st.header("\U0001f9f9 Remove Blank Rows")
    st.markdown("""
    **What it does:** Deletes rows that are completely empty or whitespace-only.

    **Example:** 1,000-row file with 47 blank rows -> cleaned file with 953 rows.
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="rb")
    if fi and st.button("Remove Blanks", key="rb_run"):
        from tools.remove_rows import remove_blank_rows
        df = load_csv(fi)
        result, summary = remove_blank_rows(df)
        show_summary(summary)
        st.dataframe(result.head(100))
        dl(result, "cleaned", "no_blanks.csv")

# ======================================================================
# Standardise Names (+ Email Extraction mode)
# ======================================================================
elif tool == TOOLS[17]:
    st.header("\U0001f464 Standardise Names")
    st.markdown("""
    **What it does:** Two modes:
    - **Split full name:** Splits a "Full Name" column into "First Name" and "Last Name"
    - **Extract from email:** Parses `john.smith@acme.com` into First: `John`, Last: `Smith`

    **Example:** `"Mary Jane Watson"` -> First: `"Mary"`, Last: `"Jane Watson"`
    **Example:** `"john.smith@acme.com"` -> First: `"John"`, Last: `"Smith"`
    """)
    fi = st.file_uploader("Upload CSV", type="csv", key="sn")
    if fi:
        df = load_csv(fi)
        mode = st.radio("Mode", ["Split a full name column", "Extract names from email addresses"], key="sn_mode")

        if mode.startswith("Split"):
            col = st.selectbox("Full name column", df.columns, key="sn_col")
            if st.button("Split Names", key="sn_run"):
                from tools.standardize_data import standardize_names
                result = standardize_names(df, col)
                st.success(f"Split {len(result):,} names")
                st.dataframe(result.head(100))
                dl(result, "with split names", "names_split.csv")
        else:
            email_col = st.selectbox("Email column", df.columns, key="sn_ecol")
            overwrite = st.radio("If First/Last Name columns already exist:", ["Only fill blanks", "Overwrite everything"], key="sn_ow")
            if st.button("Extract Names", key="sn_erun"):
                result = df.copy()
                fn_list, ln_list, dom_list = [], [], []
                for email in result[email_col].fillna("").astype(str):
                    email = email.strip().lower()
                    if "@" not in email:
                        fn_list.append(""); ln_list.append(""); dom_list.append(""); continue
                    local, domain = email.rsplit("@", 1)
                    dom_list.append(domain)
                    parts = re.split(r'[._\-]', local)
                    parts = [p.strip() for p in parts if p.strip()]
                    if len(parts) == 0:
                        fn_list.append(""); ln_list.append("")
                    elif len(parts) == 1:
                        fn_list.append(parts[0].title()); ln_list.append("")
                    elif len(parts) == 2:
                        fn_list.append(parts[0].title()); ln_list.append(parts[1].title())
                    else:
                        fn_list.append(parts[0].title()); ln_list.append(" ".join(p.title() for p in parts[1:]))

                for c in ["First Name", "Last Name", "Email Domain"]:
                    if c not in result.columns:
                        result[c] = ""

                if overwrite.startswith("Only"):
                    for i in range(len(result)):
                        if str(result.at[result.index[i], "First Name"]).strip() == "":
                            result.at[result.index[i], "First Name"] = fn_list[i]
                        if str(result.at[result.index[i], "Last Name"]).strip() == "":
                            result.at[result.index[i], "Last Name"] = ln_list[i]
                        if str(result.at[result.index[i], "Email Domain"]).strip() == "":
                            result.at[result.index[i], "Email Domain"] = dom_list[i]
                else:
                    result["First Name"] = fn_list
                    result["Last Name"] = ln_list
                    result["Email Domain"] = dom_list

                ext = sum(1 for f in fn_list if f)
                st.success(f"Extracted from {ext:,} of {len(result):,} emails")
                st.dataframe(result.head(100))
                dl(result, "extracted names", "email_names_extracted.csv")

# ======================================================================
# Standardise Phone Numbers
# ======================================================================
elif tool == TOOLS[18]:
    st.header("\U0001f4de Standardise Phone Numbers")
    st.markdown("""
    **What it does:** Strips all formatting, keeping only digits and `+`.

    **Example:** `"+1 (555) 123-4567"` -> `"+15551234567"`
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

# ======================================================================
# Standardise URLs
# ======================================================================
elif tool == TOOLS[19]:
    st.header("\U0001f517 Standardise URLs")
    st.markdown("""
    **What it does:** Normalises URLs by removing `http://`, `https://`, `www.`, trailing slashes.

    **Example (Website):** `"https://www.acme.com/"` -> `"acme.com"`
    **Example (LinkedIn):** `"https://www.linkedin.com/in/johnsmith/"` -> `"linkedin.com/in/johnsmith"`
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

# ======================================================================
# Value Classifier
# ======================================================================
elif tool == TOOLS[20]:
    from tools.value_classifier import render_value_classifier
    render_value_classifier()

# ======================================================================
# Value Standardiser (+ Find & Replace + Case Converter)
# ======================================================================
elif tool == TOOLS[21]:
    st.header("\U0001f3af Value Standardiser")
    st.markdown("""
    **What it does:** Three modes:
    1. **Rules CSV** — Match messy values against standard terms using exact, keyword, and fuzzy matching
    2. **Find & Replace** — Simple find/replace across one or more columns
    3. **Case Converter** — Convert columns to Title Case, UPPER, lower, or Sentence case

    **How to set up your rules CSV:**

    | Standard Value | Aliases |
    |---|---|
    | Accountant | auditor, bookkeeper, accounts clerk |
    | Software Engineer | developer, programmer, coder, SWE |
    | Sales Manager | account manager, sales lead, BDM |

    The "Aliases" column is optional but dramatically improves matching.
    """)

    mode = st.radio("Mode", ["Standardise with rules CSV", "Find & Replace", "Case Converter"], key="vs_mode")

    if mode.startswith("Standardise"):
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

    elif mode.startswith("Find"):
        data_f = st.file_uploader("Upload CSV", type="csv", key="fr_data")
        if data_f:
            data_df = load_csv(data_f)
            fr_cols = st.multiselect("Columns to search", data_df.columns, default=list(data_df.columns), key="fr_cols")
            match_mode = st.radio("Match mode", ["Contains (replace within text)", "Exact match (whole cell only)"], key="fr_match")
            case_sensitive = st.checkbox("Case sensitive", value=False, key="fr_case")
            num_pairs = st.number_input("Number of find/replace pairs", 1, 50, 1, key="fr_num")
            pairs = []
            for i in range(int(num_pairs)):
                a, b = st.columns(2)
                ft = a.text_input(f"Find {i+1}", key=f"fr_find_{i}")
                rt = b.text_input(f"Replace {i+1}", key=f"fr_replace_{i}")
                if ft:
                    pairs.append((ft, rt))
            if pairs and fr_cols and st.button("Run Find & Replace", key="fr_run"):
                result = data_df.copy()
                total = 0
                for cn in fr_cols:
                    series = result[cn].fillna("").astype(str)
                    for ft, rt in pairs:
                        if match_mode.startswith("Contains"):
                            if case_sensitive:
                                total += int(series.str.contains(ft, regex=False, na=False).sum())
                                series = series.str.replace(ft, rt, regex=False)
                            else:
                                total += int(series.str.contains(ft, case=False, regex=False, na=False).sum())
                                pat = re.compile(re.escape(ft), re.IGNORECASE)
                                series = series.apply(lambda x, p=pat, r=rt: p.sub(r, x))
                        else:
                            mask = (series == ft) if case_sensitive else (series.str.lower() == ft.lower())
                            total += int(mask.sum())
                            series = series.where(~mask, rt)
                    result[cn] = series
                st.success(f"{total:,} replacements across {len(fr_cols)} column(s)")
                st.dataframe(result.head(100))
                dl(result, "replaced", "find_replace_result.csv")

    else:  # Case Converter
        data_f = st.file_uploader("Upload CSV", type="csv", key="cc_data")
        if data_f:
            data_df = load_csv(data_f)
            cc_cols = st.multiselect("Columns to convert", data_df.columns, key="cc_cols")
            case_choice = st.selectbox("Convert to", ["Title Case", "UPPER CASE", "lower case", "Sentence case"], key="cc_case")
            if cc_cols and st.button("Convert", key="cc_run"):
                result = data_df.copy()
                for c in cc_cols:
                    s = result[c].fillna("").astype(str)
                    if case_choice == "Title Case":
                        result[c] = s.str.title()
                    elif case_choice == "UPPER CASE":
                        result[c] = s.str.upper()
                    elif case_choice == "lower case":
                        result[c] = s.str.lower()
                    elif case_choice == "Sentence case":
                        result[c] = s.apply(lambda x: ". ".join(p.strip().capitalize() for p in x.split(".") if p.strip()) if x else x)
                st.success(f"Converted {len(cc_cols)} column(s) to {case_choice}")
                st.dataframe(result.head(100))
                dl(result, "converted", "case_converted.csv")
