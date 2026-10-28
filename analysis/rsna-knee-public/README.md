# Reproduce the public-label study

Start with the [results report](report.md), [project page](../../projects/11-rsna-knee-leaderboard-reliability/) and [SAP](SAP.md). The primary analyses are **B: report-label agreement and latent-model diagnostics** and **C: AUC misclassification simulation**. SAP v1.2 was frozen at `968c2a9cdb3be5978bbeed5128bad8ba843985f9` before B/C outcomes. No further personal competition materials or Meta Kaggle extract are needed.

## Environment and acquisition

Run from this directory using R 4.5.1. Restore and load the project library:

```r
install.packages("renv") # Once, if needed.
renv::restore(project = ".", prompt = FALSE)
renv::load(project = ".")
```

Set an **external** data directory. The downloader uses anonymous public Kaggle APIs, pinned versions and a five-file allowlist; it never reads credentials. Do not download whole archives, because other files can include excluded reports or expert panels.

```sh
export RSNA_PUBLIC_DATA="/absolute/path/outside-this-repository/rsna-public"
Rscript -e 'renv::load(); source("R/00_download.R")' --metadata
Rscript -e 'renv::load(); source("R/00_download.R")' --labels
```

The selected files are in [datasets.csv](datasets.csv); only `primary_candidate` rows are used. Check downloaded hashes against [source_files.csv](../../results/rsna-knee-public/source_files.csv). A changed file/version requires a new provenance record. The raw schema permits identifiers for local alignment, 12 scores, and allowlisted confidence/verdict columns. It excludes reports and metadata.

The already-approved execution record is copied into the external data directory before running; this records the historical approval rather than requesting another one:

```r
dest <- Sys.getenv("RSNA_PUBLIC_DATA")
jsonlite::write_json(list(approved=TRUE,
  sap_commit="968c2a9cdb3be5978bbeed5128bad8ba843985f9",
  approved_on="2026-10-28", basis="Owner-approved v1.2 scope",
  merge_authorized=FALSE), file.path(dest,"sap-approval.json"), auto_unbox=TRUE)
```

## Tests and execution

In the activated R session, run:

```r
source("tests/test-foundation.R")
source("tests/test-label-patterns.R")
source("tests/test-latent.R")
source("tests/test-paired.R")
source("R/21_label_analysis.R")
source("R/23_fit_labels.R")
source("R/32_run_simulation.R")
source("R/40_figures.R")
knitr::knit("report.qmd", output="report.md", quiet=TRUE)
```

The checked Markdown report was generated with **knitr**, not a Quarto CLI installation. `report.qmd` is the source; its GFM frontmatter also permits a Quarto rendering where available. Tables are regenerated from aggregate CSVs. Narrative numbers describe this frozen run and must be reviewed if inputs or scenarios change.

| Stage | Implemented and executed |
| --- | --- |
| B descriptive | Joint bootstrap; known/unknown denominators; Cohen/Fleiss kappa, PABAK; majority-disagreement summaries; prespecified threshold/unknown sensitivities |
| B latent | Native-R constrained Gibbs sampler; 12 findings × 3 accuracy priors × 4 chains; convergence and posterior predictive diagnostics |
| C | Four baseline scenarios; naive, oracle-corrected and independent expert-n58 estimates; paired bootstrap intervals; bias, RMSE, coverage, ordering, failures and MCSE |
| Reporting | Aggregate tables, five B/C figures and rendered English report |

The model code is in [R/22_latent_model.R](R/22_latent_model.R); its positive-average-Youden orientation is an assumption, not independent validation. All latent outputs are diagnostic because predictive fit fails. The C script uses a fixed, prespecified parameter grid rather than fitting its simulation inputs to these failed models.

Raw/aligned labels, study IDs, sampler draws and Monte Carlo replicates stay outside the checkout. Per-run JSON receipts record seeds, the SAP commit and elapsed analysis time. Only aggregate CSVs and figures are released. No training, MRI inference, notebook publication or competition submission occurs.

## Supplement and omitted extensions

[R/11_sampling_benchmark.R](R/11_sampling_benchmark.R) produced the earlier A sampling-only reference under SAP v1.1; [R/10_leaderboard.R](R/10_leaderboard.R) retains tested mathematical primitives. Neither is part of the B/C execution sequence. Empirical leaderboard acquisition/assembly was retired and its unused extractor removed. Historical plans remain in SAP/DECISIONS for auditability.

The dependent latent model, secondary derivative-source comparisons, alternate prevalence priors/orientations, uncertain-parameter correction and larger simulation grids were not run. See [CHECKS.md](CHECKS.md) and [DECISIONS.md](DECISIONS.md) for execution evidence and limits.
