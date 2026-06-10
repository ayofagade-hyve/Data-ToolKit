# 🧹 Data Cleaning & File Automation Toolkit

A **Streamlit-based web application** providing **20 data-cleaning tools** for non-technical users.
No coding required — upload CSV files, configure tools, and download cleaned results.

## ✨ Features

| # | Tool | Description |
|---|------|-------------|
| 1 | 🏢 Classify Organisation Type | Multi-field analysis to tag Bank, Fintech, Insurance, etc. |
| 2 | 💼 Classify Seniority & Job Function | 6 seniority levels + 10 function categories |
| 3 | 🔀 Column Remapper | Remap columns OR reorder & remove |
| 4 | 📎 Combine CSVs | Merge multiple CSV files into one |
| 5 | ⚖️ Compare & Remove | Remove rows found in a suppression list |
| 6 | 📊 Data Quality Report | Completeness %, blanks, unique values |
| 7 | 🔍 Deduplicate vs Master List | 4-key matching |
| 8 | 🌐 Extract Company Domains | Corporate domain extraction |
| 9 | 🔤 Fix Encoding (Mojibake) | 4-pass garbled character repair |
| 10 | 🔄 Full Data Migration | 7-stage pipeline |
| 11 | 🔁 Fuzzy Duplicate Finder | Blocking strategy for fast fuzzy matching |
| 12 | 🔎 LinkedIn Search Links | Generate LinkedIn search URLs |
| 13 | 🔗 Merge / Split Columns | Combine or split columns |
| 14 | 🚫 Remove by Keywords / Flag | Keyword or exact-match removal |
| 15 | 🧹 Remove Blank Rows | Remove all-empty rows |
| 16 | 👤 Standardise Names | Split names or extract from email |
| 17 | 📞 Standardise Phone Numbers | Normalise phone formatting |
| 18 | 🔗 Standardise URLs | Lowercase, add https://, clean up |
| 19 | 🎯 Value Standardiser | Rules CSV + Find & Replace + Case Converter |

## 🚀 Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

## 📄 License
MIT License
