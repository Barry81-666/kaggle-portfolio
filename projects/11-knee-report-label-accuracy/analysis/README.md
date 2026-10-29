# Reproduce the public-label study

I compare agreement between public report-label sources, test a no-gold-standard model, and simulate how label errors bias AUC. Start with the [results report](../report.md), [project page](../) and [analysis plan](SAP.md). The [research decisions](DECISIONS.md) distinguish the primary design from the clustering and interval-method comparisons I added after seeing the results.

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

The selected files are in [datasets.csv](datasets.csv); only `primary_candidate` rows are used. Check downloaded hashes against [source_files.csv](../results/source_files.csv). A changed file/version requires a new provenance record. The raw schema permits identifiers for local alignment, 12 scores, and allowlisted confidence/verdict columns. It excludes reports and metadata.

The scripts also read a local record of the frozen plan. Keep that record when reusing an existing environment. For a fresh environment, use the [record setup saved with the completed analysis](https://github.com/Barry81-666/kaggle-portfolio/tree/11279e1c1ed7a3c422d619c96ffce2847a35a5a4). I have retained this compatibility step so the statistical scripts can run unchanged.

## Tests and execution

In the activated R session, run:

```r
source("tests/test-foundation.R")
source("tests/test-label-patterns.R")
source("tests/test-latent.R")
source("tests/test-paired.R")
source("tests/test-intervals.R")
source("R/21_label_analysis.R")
source("R/23_fit_labels.R")
source("R/32_run_simulation.R")
source("R/40_figures.R")
# Exploratory additions made after examining the primary results.
source("R/24_source_clusters.R")
source("R/34_interval_sensitivity.R")
source("R/41_review_figures.R")
knitr::knit("../report.qmd", output="../report.md", quiet=TRUE)
```

The checked Markdown report was generated with **knitr**, not a Quarto CLI installation. `report.qmd` is the source; its GFM frontmatter also permits a Quarto rendering where available. Tables are regenerated from aggregate CSVs. Narrative numbers describe this frozen run and must be reviewed if inputs or scenarios change.

| Stage | Implemented and executed |
| --- | --- |
| Agreement between label sources | Joint bootstrap; known/unknown denominators; Cohen/Fleiss kappa, PABAK; majority-disagreement summaries; prespecified threshold/unknown sensitivities |
| Testing a no-gold-standard model | Native-R constrained Gibbs sampler; 12 findings × 3 accuracy priors × 4 chains; convergence and posterior predictive diagnostics |
| How label errors bias AUC | Four baseline scenarios; naive, oracle-corrected and independent expert-n58 estimates; paired bootstrap intervals; bias, RMSE, coverage, ordering, failures and MCSE |
| Exploratory comparisons | Source clustering and 1,000 joint-bootstrap stability checks; 4,000 expert-sample interval comparisons, with up to 1,999 bootstrap draws |
| Reporting | Aggregate tables, seven figures and rendered English report |

The model code is in [R/22_latent_model.R](R/22_latent_model.R); its positive-average-Youden orientation is an assumption, not independent validation. All latent outputs are diagnostic because predictive fit fails. The misclassification simulation uses a fixed, prespecified parameter grid rather than fitting its simulation inputs to these failed models.

Raw/aligned labels, study IDs, sampler draws and Monte Carlo replicates stay outside the checkout. Per-run JSON records contain seeds, the SAP commit and elapsed analysis time. Only aggregate CSVs and figures are released. No training, MRI inference, notebook publication or competition submission occurs.

## Further analyses

A dependence-aware latent model, secondary derivative-source comparisons, alternate prevalence priors/orientations, uncertain-parameter correction and larger simulation grids remain possible extensions. I did not run them in this analysis. See the [checks](CHECKS.md) and [research decisions](DECISIONS.md) for the completed work and its limits.

I directed this study and reviewed each analytic decision; the analysis plan and R code were developed with AI assistance.
