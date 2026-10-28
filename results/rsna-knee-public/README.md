# Aggregate results: public report labels and misclassification

Read the [English report](../../analysis/rsna-knee-public/report.md) for interpretation.

| Outputs | Content |
| --- | --- |
| [source_files.csv](source_files.csv) | Five primary sources: versions, URLs and hashes; no study records |
| [T4_agreement.csv](T4_agreement.csv) | Positive/missing fractions, kappa/PABAK, Fleiss kappa and majority-disagreement summaries with joint-bootstrap intervals |
| [T4_denominators.csv](T4_denominators.csv), [paired denominators](T4_pair_denominators.csv) | Known, complete-case and comparable-study counts |
| [T4_sensitivity.csv](T4_sensitivity.csv) | Prespecified threshold and unknown-treatment variants; descriptive point estimates |
| [T5_clusters.csv](T5_clusters.csv), [memberships](T5_membership.csv), [focus findings](T5_focus.csv) | Post-hoc similarity groups, bootstrap co-membership and finding-specific paired denominators; not independent-source counts |
| [T6_eligibility.csv](T6_eligibility.csv) | Complete-case count and model eligibility for each finding |
| [T6_latent_parameters.csv](T6_latent_parameters.csv) | Sampler quantiles, R-hat/ESS and boundary fractions; diagnostic output, not endorsed accuracy estimates |
| [T6_predictive_checks.csv](T6_predictive_checks.csv), [pattern summaries](T6_pattern_checks.csv) | Model-fit checks on aggregated response patterns |
| [T7_simulation.csv](T7_simulation.csv) | AUC_A, AUC_B and paired-difference performance; MCSEs and failures |
| [T7_ordering.csv](T7_ordering.csv), [DGM checks](T7_dgm.csv) | Synthetic model ordering, ties/reversals and realized generating parameters |
| [T8_interval_sensitivity.csv](T8_interval_sensitivity.csv), [sample diagnostics](T8_sample_diagnostics.csv) | Post-hoc expert-sample interval methods: conditional/all-attempt coverage, paired MCSEs, failures and widths |
| [T3_sampling_benchmark.csv](T3_sampling_benchmark.csv) | Supplement only: earlier synthetic sampling reference; empty observed fields are unmeasured, not zero |

`labels-run.json`, `latent-run.json`, `simulation-run.json` and `sampling-run.json` record execution settings. `clusters-run.json` and `intervals-run.json` record post-hoc v1.3 settings. Labels and predictions, study/team identifiers, full sampler draws and Monte Carlo replications are not distributed.

T4 intervals are percentile bootstrap confidence intervals. T6 lower/upper values are sampler quantiles; nonconverged fits do not support credible-interval interpretation, and all primary fits have serious predictive-fit limitations. T7 coverage is conditional on valid intervals, with failures shown separately. The oracle correction knows its calibration parameters and is deliberately not clipped.

T8 logit intervals are undefined at boundary AUC or zero variance. Successful coverage over all attempts treats undefined intervals as unsuccessful; valid-interval coverage is also retained. T5 co-membership is descriptive bootstrap stability, not conditional independence.
