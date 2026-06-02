# 🧹 Data Cleaning & File Automation Toolkit

A unified, interactive web app for non-technical users to clean, deduplicate, classify, and standardise CSV data — all from a browser.

## ✨ Features

| Tool | What it does |
|------|-------------|
| **Combine CSVs** | Merge multiple CSV files into one |
| **Fix Encoding** | Repair mojibake / garbled characters |
| **Deduplicate vs Master** | Remove rows that exist in a master file |
| **Internal Dedup** | Fuzzy-match duplicates within one file |
| **Extract Domains** | Get company domains from email addresses |
| **Standardise Data** | Clean names, phones, websites, LinkedIn |
| **Classify Seniority** | Auto-classify job seniority level |
| **Classify Job Function** | Auto-classify department / function |
| **Classify Org Type** | Auto-classify company type |
| **LinkedIn Links** | Generate LinkedIn search URLs |
| **Remove Blank Rows** | Delete empty rows |
| **Remove by Keywords** | Delete rows containing specific words |
| **Remove by Flag** | Delete rows by a flag column value |
| **Compare & Remove** | Remove matches between two lists |

## 🚀 Quick Start

```bash
# 1. Clone or unzip this project
cd data_cleaning_toolkit

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
data_cleaning_toolkit/
├── app.py                  # Streamlit web app (main entry point)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── MIGRATION_NOTES.md      # What changed from the old scripts
├── utils/                  # Shared utility modules
│   ├── text_cleaning.py    # Mojibake fixer
│   ├── matching.py         # Levenshtein / fuzzy matching
│   ├── column_mapping.py   # Auto-detect columns
│   ├── classifiers.py      # Seniority, function, org type
│   ├── domain_tools.py     # Domain extraction
│   ├── name_tools.py       # Name splitting
│   ├── linkedin_tools.py   # LinkedIn URL tools
│   └── io_helpers.py       # CSV I/O, summaries
├── tools/                  # Tool implementations
│   ├── combine_csvs.py
│   ├── clean_encoding.py
│   ├── dedupe_master.py
│   ├── dedupe_internal.py
│   ├── extract_domains.py
│   ├── standardize_data.py
│   ├── classify_jobs.py
│   ├── linkedin_links.py
│   ├── remove_rows.py
│   └── compare_lists.py
└── tests/
    └── test_classifiers.py
```

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 💡 Tips

- Every tool shows a **summary report** after running.
- Use **Preview** to check results before downloading.
- Removed rows are always available as a separate download.
- The app never modifies your original files.
