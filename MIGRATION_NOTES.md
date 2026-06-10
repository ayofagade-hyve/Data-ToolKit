# Migration Notes

This document explains how the original scattered Google Apps Scripts
and Python/Colab notebooks were consolidated into this unified toolkit.

## Scripts Merged

| Original Script(s) | New Module | Notes |
|---|---|---|
| `Duplicate Matcher.gs`, `checker.gs`, `Duplicate Matcher transpose.gs` | `tools/dedupe_internal.py` + `utils/matching.py` | 3 near-identical scripts merged into one with configurable threshold and column selection |
| `text clean.gs` + `consolidate.gs` char maps + Python CSV Cleaner | `utils/text_cleaning.py` + `tools/clean_encoding.py` | Character map ported; ftfy used as first pass; cp1252→utf8 re-encoding added |
| `Data Migration Filler.gs`, `Master.gs`, `cogconv.gs`, `consolidate.gs`, `JobFunc.gs` | `utils/classifiers.py` + `tools/classify_jobs.py` | 5 overlapping classifier implementations merged; `consolidate.gs` chosen as canonical (most keywords, multilingual) |
| `Extract Domain.gs` + Python Domain Extractor | `utils/domain_tools.py` + `tools/extract_domains.py` | Merged; personal-domain blocklist expanded |
| Python CSV Deduplicater + Master List Dedupe | `tools/dedupe_master.py` | Deduplicater had more match keys (LinkedIn, name+website); both merged |
| `vlookup.gs` + `Compare.gs` | `tools/compare_lists.py` | Generalised: user picks source & lookup columns |
| Python CSV Combiner | `tools/combine_csvs.py` | Same logic, UI-friendly |
| `strsep.gs` | `utils/name_tools.py` | `split_name()` function |
| `extract company.gs` | `utils/name_tools.py` | `extract_company_from_title()` function |
| `Linin.gs` | `utils/linkedin_tools.py` + `tools/linkedin_links.py` | Direct port |
| `emptycols.gs` | `tools/remove_rows.py` → `remove_blank_rows()` | Direct port |
| `Delete duplicate rows.gs` | `tools/remove_rows.py` → `remove_by_flag()` | Generalised to any flag value |
| `duplicate words.gs` | `tools/remove_rows.py` → `remove_by_keywords()` | Generalised to any keyword list |
| `filler.gs` | Not ported | Business-rule-specific; hard-coded to Vendelux/Sponsor leads logic |

## Scripts Not Ported (API-dependent or Sheets-only)

| Script | Reason |
|---|---|
| `EuropeCheck.gs` | Requires live Wikidata SPARQL API calls |
| `enricher.gs` | Requires live API calls (Wikidata, OpenCorporates, DuckDuckGo) |
| `Domain Finder.gs` | Requires live Clearbit + DuckDuckGo API calls |
| `highlight.gs` | Google Sheets conditional formatting only |
| `filler.gs` | Hard-coded business rules for specific data sources |
| `Untitled.gs` | Just logs the script ID |

## Key Improvements

1. **No hard-coded sheet names** — users pick columns via the UI
2. **Automatic column detection** — aliases cover 15+ common header variants
3. **Non-destructive** — original files are never modified; cleaned outputs are downloaded separately
4. **Removed-rows export** — every dedup/remove tool lets you download what was removed
5. **Summary reports** — before/after counts shown after every operation
6. **Fuzzy-match threshold slider** — configurable instead of hard-coded
7. **Multilingual classifiers** — French, Portuguese, Spanish job titles supported
8. **Encoding fixes** — ftfy + cp1252 re-encoding + full character map
9. **One-click local setup** — `pip install` + `streamlit run`
