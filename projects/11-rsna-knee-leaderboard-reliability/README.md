# How Much Can We Trust a Medical-Imaging Leaderboard?

**Reliability, Selection and Label Uncertainty in the RSNA 2026 Knee MRI Challenge, Using Public Data Only**

## Research Question

How consistent are public and private leaderboard scores? How do repeated selection and test-set sampling affect ranks? How does disagreement among report-derived labels affect model evaluation when no gold standard is available?

## Data

- Official [Meta Kaggle](https://www.kaggle.com/datasets/kaggle/meta-kaggle), Apache 2.0. The public schema contains both score precisions and selection indicators; competition-specific coverage still needs verification.
- Publicly released report-derived label tables, with source-specific permissions and versions in the [dataset manifest](../../analysis/rsna-knee-public/datasets.csv). Only approved label columns are processed locally. Derived label sets are distinguished from independent extraction families.
- Published aggregate findings, recorded with source locations and evidence status in [parameters.csv](../../analysis/rsna-knee-public/parameters.csv).

No personal competition materials, original images or reports, official Gold58 labels, or rule-gated competition files are used. Raw and individual-level records are not redistributed.

## My Contribution

This is a new, independently scoped methodological project in my portfolio, developed with AI-assisted research and coding. The current contribution is the analysis design, source audit and R software foundation. Empirical analyses and findings will be documented as they are completed; this page does not claim completed results or independent authorship of upstream label datasets.

## Methods

The [statistical analysis plan](../../analysis/rsna-knee-public/SAP.md) specifies leaderboard agreement, simulation-based noise benchmarks, conditional selection/rank analyses, label agreement, latent-class sensitivity analyses and an ADEMP simulation of AUC bias. It separates observed data summaries from model-dependent accuracy and uncertainty estimates.

## Key Results

**Planning stage.** Source feasibility and schema checks are complete to the extent recorded in the [source audit](../../analysis/rsna-knee-public/SOURCE_AUDIT.md). No leaderboard reliability, label accuracy or simulation performance findings are reported yet. The SAP requires approval before empirical analysis, followed by review of the first tables and figures.

## Limitations

Test sizes are public approximations. Meta Kaggle is a filtered snapshot and may lack required records. Same-submission and unmatched team-best comparisons answer different questions. Latent models require untestable identifying assumptions; shared label ancestry can make estimates fragile. Copied expert labels and prior panel tuning cannot be independently excluded. Any eventual conclusions concern this challenge and these public sources.

## Reproduction

Start with the [R execution guide](../../analysis/rsna-knee-public/README.md). Data must reside outside the repository. Only aggregate results and figures may be published. The original archived RSNA project is not used or modified.

## Sources

[Official RSNA challenge overview](https://www.rsna.org/artificial-intelligence/ai-image-challenge/knee-mri-ai-challenge) · [Source audit and attribution](../../analysis/rsna-knee-public/SOURCE_AUDIT.md) · [Methods references](../../analysis/rsna-knee-public/SAP.md#references)
