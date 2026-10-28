# Knee Diagnostic Labels Without a Gold Standard

**Report-source agreement, latent-model diagnostics and AUC misclassification bias**

How should we evaluate labels extracted from radiology reports when an independent reference standard is unavailable? This study combines an empirical comparison of public knee-diagnosis labels with simulations of their possible effect on model evaluation.

## Data and contribution

Five public extraction sources—Dread, Steven's original full labels, Pilkwang, Yunus and Lixin—cover a common **4,349 studies** and **12 findings**. Source-specific unknown codes and verdicts are harmonized before comparison. Versions, attribution and selected-file hashes are recorded in the [source audit](../../analysis/rsna-knee-public/SOURCE_AUDIT.md).

This project's contribution is a reproducible R analysis of agreement, missingness, latent-model assumptions and AUC bias, developed with AI-assisted research and coding. Upstream authors created the label datasets. The [analysis plan](../../analysis/rsna-knee-public/SAP.md) was frozen before these outcomes. Original reports, images, expert annotations and personal competition predictions are outside this study.

## Methods and results

| Question | Result | Interpretation boundary |
| --- | --- | --- |
| Do the sources agree? | Fleiss kappa ranges from **0.390 for synovitis** to **0.868 for fracture**; 2,000 joint study-bootstrap resamples provide intervals. | Agreement is not accuracy. Complete-case sample sizes range from 573 to 3,987, with potentially informative missingness. |
| Can an independent latent-class model estimate report-state accuracy? | **11/12** primary fits pass chain diagnostics, but all 11 fail to reproduce observed response patterns; synovitis does not converge. | No sensitivity/specificity estimate is endorsed. Shared reporting conventions and source dependence cannot be disentangled here. |
| Does more validation data solve label error? | With independent errors, oracle correction has little bias. With score-dependent errors at n=977, its AUC bias is **+0.1274** and nominal 95% interval coverage is **12.4%**. | These are synthetic results for specified mechanisms, not observed RSNA model performance. The correction knows the true error parameters. |
| Does correction improve model ordering? | For true AUCs 0.90 versus 0.91 and independent errors, correct ordering is **53.65% at n=58** and **66.05% at n=977**. | A common positive correction factor leaves ordering unchanged. These are two-model probabilities, not actual competition ranks. |

![AUC bias under two error mechanisms](../../figures/rsna-knee-public/F7_auc_bias.png)

The simulation contains four prespecified scenarios, each with 2,000 repetitions and 399 paired bootstrap resamples. It also shows undercoverage of percentile intervals in an independent, perfectly labeled synthetic sample of 58 studies. The [full report](../../analysis/rsna-knee-public/report.md) includes plots, uncertainty, failures, prior sensitivities and model checks.

## What remains uncertain

Report-derived sources cannot identify the common discrepancy between reports and imaging truth. Repeat examinations may narrow study-bootstrap intervals when patient identifiers are unavailable. Thresholds and mention conventions may define different targets. A dependence-aware latent model is a possible next analysis; the failed independence model is not used to calibrate simulation parameters.

## Reproduction

The [R guide](../../analysis/rsna-knee-public/README.md) provides versioned public-file acquisition, the locked environment, tests and execution order. Individual labels, study IDs and simulation draws remain outside the repository; only aggregate tables and figures are published. An earlier leaderboard sampling simulation is retained as a supplement. Empirical leaderboard analysis was discontinued.
