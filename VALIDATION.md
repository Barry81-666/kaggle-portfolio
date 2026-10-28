# Validation of the English Portfolio Edition

Checks performed on **2026-10-28**, against repository commit `a3bc52f16e600f914ce0c0165173fd267ab02620`. This is a static source and evidence review; archived training/inference was not executed.

| Check | Result and scope |
| --- | --- |
| Original public versions | All 9 retained downloads matched their previously recorded original SHA-256 values; [download checks](meta/source-download-checks.json) |
| Notebook translation | 456 comment occurrences and 12 Markdown cells translated in 7 notebooks; original English comments and Markdown retained |
| Code consistency | All 148 code cells accounted for: 136 have strict non-comment token equality; 10 more match after only the 88 exact documentation/display-text substitutions in the ledger; 2 non-Python-lexable installation cells are source-identical |
| Literal changes | All 88 occurrences individually matched to the [before/after ledger](meta/translation-exceptions.json); no extra token changes accepted |
| Metadata | Original hashes and Kaggle version identities preserved; current hashes, project catalog and provenance agree |
| Local navigation | All local Markdown file/directory links and section anchors resolved; exact count in the [machine-readable report](meta/validation.json) |
| Kaggle links | The 64 retained Kaggle URLs have successful checks recorded on 2026-10-28: 63 specific pages and 1 image; [per-URL results](meta/link-checks.json) |
| Credentials | No flags from private-key, common token-prefix, AWS key-ID or long literal credential patterns |
| Package contents | No dataset, model-weight or credential files added; the only CSV is the project index. New results are aggregate historical metrics and an original EDA image. |
| Syntax and structure | JSON parses; all Python files parse statically. Notebook shell/R cells were not represented as executable Python. |

The token check deliberately distinguishes **comment-only equality** from the requested translation of display strings/docstrings. Claiming every token is literally unchanged would be incorrect. The preserved Chinese output filename is a documented exception to full language conversion because changing it would alter a file path.

A resolved Kaggle page verifies the URL's routing, not authorization to private inputs, the continued availability of every dependency, or a leaderboard claim. The 11 historical team results retain the prior authenticated verification date; they were not newly verified while logged in during this revision. Pattern scans reduce accidental credential exposure but are not a comprehensive security audit.

## Re-run the Static Checks

Use Python 3.12 or later (this run used 3.14), with a clean checkout of the baseline commit available locally:

```bash
python scripts/validate_portfolio.py --original-root /path/to/baseline-checkout
```

The [validator](scripts/validate_portfolio.py) does not run archived code. It checks token sequences, the exact literal whitelist, provenance hashes, local links, file types and credential patterns. External-link reachability and original public-download checks are separately recorded observations, not network actions performed by this script.

[Archive notes](docs/ARCHIVE_NOTES.md)
