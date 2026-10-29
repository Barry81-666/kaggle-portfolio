# Validation of the Nine Archived Kaggle Notebooks

This page covers the **nine archived notebooks in [the project catalog](meta/catalog.json)**, their English annotations, provenance and supporting portfolio navigation. Static checks were repeated on **2026-10-29** against the original notebook baseline at commit `a3bc52f16e600f914ce0c0165173fd267ab02620`; results are in the [archive validation report](meta/archive-validation.json). Archived training and inference were not executed.

The later knee report-label study is outside this notebook-validation scope. Its aggregate CSV tables are documented in the [research results](projects/11-knee-report-label-accuracy/results/) and its own [checks](projects/11-knee-report-label-accuracy/analysis/CHECKS.md).

| Check | Result and scope |
| --- | --- |
| Original public versions | The nine original-version downloads matched their recorded SHA-256 values on 2026-10-28; [download record](meta/source-download-checks.json) |
| English annotations | The translation record covers 456 comment occurrences and 12 Markdown cells in seven notebooks; existing English comments and Markdown were retained |
| Code consistency | All 148 code cells accounted for: 136 have strict non-comment token equality; 10 more match after the 88 exact documentation/display-text substitutions in the ledger; two non-Python-lexable installation cells are source-identical |
| Literal changes | All 88 occurrences match the [before/after ledger](meta/translation-exceptions.json); no additional token changes accepted |
| Metadata and provenance | Current archived hashes agree with the catalog and per-project provenance; original download hashes and Kaggle version identities are preserved |
| Supporting navigation | Local Markdown links and section anchors in the checked archives and supporting portfolio documents resolve; current counts are in the archive validation report |
| Kaggle URL observations | The 64 URL checks recorded on 2026-10-28 cover 63 pages and one image; [per-URL results](meta/link-checks.json). These are dated observations, not a fresh reachability check |
| Credentials and structure | No credential-pattern flags in the checked scope; JSON parses and Python source passes static syntax checks. Notebook shell/R cells are not treated as executable Python |
| Archive inputs | Dataset and model-weight inputs are not included in the notebook archives. The separate research project publishes aggregate CSV tables |

The token comparison distinguishes comment edits from the documented display-string and docstring substitutions. A Chinese output filename remains unchanged to preserve the original file path. Pattern scans are a static check, not a comprehensive security audit.

## Re-run the Archive Checks

Use Python 3.12 or later with the original baseline checkout available locally:

```bash
python scripts/validate_portfolio.py --original-root /path/to/baseline-checkout --archive-only --report meta/archive-validation.json
```

The [validator](scripts/validate_portfolio.py) checks notebook token sequences, the literal-change ledger, provenance hashes, supporting local links and credential patterns without executing archived code. External-link reachability and original-download checks remain separately dated records.

[Archive notes](docs/ARCHIVE_NOTES.md)
