# Reproducing the exploratory v1.4 extension

Read [FREEZE_DEVIATION.md](FREEZE_DEVIATION.md) first: the initial remote upload was incomplete. The hash gate verifies the intended local pre-execution snapshot, not a complete public freeze. The final repaired tree contains the unchanged intended rules; repair occurred after outcomes.

Start in `projects/11-knee-report-label-accuracy/analysis/v1.4`. Use R 4.5.1 and the existing parent `renv.lock`; new analysis needs data.table and jsonlite, figures additionally use ggplot2. No new packages were introduced.

Set `RSNA_PUBLIC_DATA` to the existing external directory holding the five approved, versioned public label files listed in `../../results/source_files.csv`. Set `RSNA_V14_WORK` to a different directory outside the checkout for bootstrap and simulation replicate arrays. Do not put raw labels, reports or study identifiers in this repository.

```sh
Rscript test-core.R
Rscript 01_alignment.R
Rscript 02_simulation.R
Rscript 03_figures.R
python3 04_review.py
python3 05_validate.py --baseline /path/to/pre-extension-checkout --raw "$RSNA_PUBLIC_DATA"
```

The freeze manifest verifies eight files against the intended local SAP v1.4 snapshot. The alignment entry point checks the five source-file hashes and schema before use, aligns the original 4,349 IDs in memory, and reconstructs all previous agreement point estimates and complete binary pattern counts. An altered source or frozen rule stops the run. Seeds are documented in IMPLEMENTATION.md. The simulation consumes only the resulting aggregate pattern counts; it does not need individual reports, images, expert annotations or actual model predictions. Existing v1.2/v1.3 scripts and results are not overwritten.

## Aggregate outputs in `../../results/v1.4`

- `alignment-eligibility.csv`: count screen for both targets; all 24 rows exclude a new LCM.
- `alignment-denominators.csv`, `yunus-code-counts.csv`: known/positive/excluded counts and all observed numeric-code counts, including undocumented codes retained as missing.
- `alignment-paired-changes.csv`: Pilkwang/Yunus agreement, kappa, discordance and both positive fractions before/after on fixed paired samples; 2,000 joint cohort bootstrap draws, percentile intervals and valid denominators.
- `alignment-moderate-single-source.csv`: Yunus-only fraction comparison; no paired agreement is possible.
- `nonharmonized-five-source-context.csv`: before/after pairwise context with the other three operational codings unchanged; this is not five-source harmonization.
- `simulation-pattern-calibration.csv`, `simulation-cohort.csv`: original five-complete patterns, selected population, positive fractions, filter retention and abstention reasons.
- `simulation-dgm.csv`: each scenario's assumptions, seed, retained sample summary, truth prevalence and timing. The prevalence proxy and all truth parameters are scenario quantities, not estimated disease truth.
- `simulation-summary.csv`: full and retained-sample results. Suffixes `_estimate`, `_mcse`, `_valid` give conditional-on-valid means/proportions, Monte Carlo SEs and valid replicate counts. Selection probabilities also have all-attempt denominators; reference/truth failures and oracle non-tied denominators are explicit. Equal true AUC leaves global misselection blank. Tied reference rankings are reported separately and do not count as selecting either model.
- `simulation-paired-contrasts.csv`: retained-minus-full differences on jointly valid replicates; these combine sample selection and sample-size changes. The three `common_subset_*` contrasts are zero because reference labels coincide on that subset, as asserted on all 32 patterns and every draw.
- `software-checks.csv` and run JSONs: meaningful synthetic checks, freeze/source checks, original result reconstruction, attempted/completed counts and cumulative compute time.

`label_bias` compares reference AUC with synthetic-truth AUC on identical evaluated cases. `selection_effect` compares that subset's synthetic-truth AUC with specified full-population AUC; `total_bias = label_bias + selection_effect` is checked in every replicate. For unequal AUCs, `misselection_global` uses the full-population target ordering. `oracle_disagreement` compares non-tied reference and truth orderings on the same realized sample; it is a distinct finite-sample endpoint and can differ from global misselection. Monte Carlo SE describes simulation precision conditional on assumptions, not uncertainty about actual clinical accuracy.

The project page and original report await owner review. See [REVIEW.md](REVIEW.md) for the findings, figures and source-definition review package.
