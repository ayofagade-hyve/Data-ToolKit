# Changelog — Data-ToolKit Update

## Removed
- **🤖 AI Column Classifier** — removed from TOOLS list, sidebar, home page cards, and tips
- **tools/ai_classifier.py** — no longer imported or used (you can delete this file)
- **Hugging Face API dependency** — no API tokens needed anymore
- **Old Step 5 (rules CSV upload)** — replaced with inline value mapping

## Added
- **🏷️ Value Classifier** (`tools/value_classifier.py`) — new standalone tool
  - Upload CSV/Excel, pick a column, see all unique values + counts
  - Two modes: "Map Individually" (editable table) or "Group Multiple Values" (named groups)
  - Apply mapping → new classified column → download CSV or Excel

- **Step 7: Column Cleanup** in Full Data Migration
  - Toggle between "Remove these columns" and "Keep only these columns"
  - Drop classification/intermediate columns before download
  - Makes imports as clean as possible

## Changed
- **Full Data Migration — Step 5** completely redesigned
  - OLD: Upload a rules CSV for standardisation
  - NEW: Inline value mapping with st.data_editor — select output columns, see unique values, type what each should become
- **Full Data Migration** now has **7 steps** (was 6)
- **TOOLS list** — AI Classifier removed, Value Classifier added (sorted alphabetically)
- **All TOOLS indices** updated accordingly
- **Home page** — 19 tools, new Value Classifier card, 7-stage migration description, AI references removed

## Files to update in your repo
1. `app.py` — **replace entirely** with the new version
2. `tools/value_classifier.py` — **new file**, add to tools/ directory
3. `tools/ai_classifier.py` — **safe to delete**
