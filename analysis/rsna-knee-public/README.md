# Public-data RSNA methodological study

Start with the [SAP](SAP.md), [source audit](SOURCE_AUDIT.md) and [project page](../../projects/11-rsna-knee-leaderboard-reliability/). This is the planning/software-foundation checkpoint. Approval of the exact SAP commit is required before empirical analysis.

## Current implementation

| File | Implemented now | Later phase |
| --- | --- | --- |
| R/00_download.R | Public metadata, pinned file-only label downloads, optional Meta Kaggle table downloads | Recheck licenses/schema when versions change |
| R/01_assemble.R | DuckDB external-memory filter and local coverage receipt | Validate competition coverage and field semantics on complete inputs |
| R/10_leaderboard.R | Paired agreement, tied strata and Deming primitives | Full T1–T4, inference, selection and rank pipelines |
| R/20_labels.R | Agreement and leave-one-out disagreement primitives | Joint bootstrap, latent models and diagnostics |
| R/30_simulation.R | Misclassification DGM and analytic AUC correction | Full ADEMP grid, paired models and uncertainty propagation |
| tests/test-foundation.R | Synthetic known-answer and independent pROC checks | Expanded tests as empirical pipelines are implemented |

The initial `renv.lock` pins the tested foundation only. DuckDB/DBI, latent-model and reporting dependencies will be added to the lock when that phase is implemented and tested; their presence in the SAP is not a claim they have run. No training or model inference is part of this project.

## Setup and synthetic tests

Run from this directory with R 4.5.1:

```r
install.packages("renv") # Once, if needed.
renv::restore(project = ".", prompt = FALSE)
renv::load(project = ".")
source("tests/test-foundation.R")
```

Use `renv::run()` for command-line scripts, or activate the project library before calling Rscript. Keep the data directory outside the checkout:

```sh
export RSNA_PUBLIC_DATA="/absolute/path/outside-this-repository/rsna-public"
Rscript -e 'renv::load(); source("R/00_download.R")' --metadata
Rscript -e 'renv::load(); source("R/00_download.R")' --labels
```

No token is read or required. Metadata acquisition does not run statistical analysis. The label downloader checks a strict schema and removes a rejected file. An interrupted download remains `.part` and is never treated as complete. Do not download entire label archives: some include expert-label files or report-related material excluded by this study.

For Meta Kaggle, the following is an explicit large download (about 3.7 GB uncompressed). Check available disk space first. Files are pinned to version 2370; a later version requires a documented amendment.

```sh
Rscript -e 'renv::load(); source("R/00_download.R")' --meta-tables
```

The equivalent local public Kaggle CLI commands are `kaggle datasets download -d kaggle/meta-kaggle -f Competitions.csv -p "$RSNA_PUBLIC_DATA"`, and the same command with `Teams.csv` and `Submissions.csv`. These CLI commands retrieve the latest version unless version support is configured; prefer the pinned R downloader and always record the actual version. Do not use competition-download or submission commands.

After SAP approval is actually given, record the approved SHA/date in DECISIONS.md and in an external `sap-approval.json` with fields `approved`, `sap_commit`, `approved_on`. The assembler requires this receipt and the DuckDB/DBI phase dependencies. It stores its database and audit outside the repository. No empirical entry point is enabled in this planning checkpoint.

## Release policy

Only aggregate result tables, figures and source manifests are publishable. No team lists, study IDs, raw Meta Kaggle tables, label tables, reports, expert labels or participant predictions belong in Git. `report.qmd` renders a status page now; statistical results are added only after their checkpoint review. See [DECISIONS.md](DECISIONS.md) for amendments and approval state.
