# Aggregate results: public report labels and misclassification

Read the [English report](../report.md) for interpretation.

| Outputs | Content |
| --- | --- |
| [Source versions and hashes](source_files.csv) | Five primary sources: versions, URLs and hashes; no study records |
| [Agreement summaries](T4_agreement.csv) | Positive/missing fractions, kappa/PABAK, Fleiss kappa and majority-disagreement summaries with joint-bootstrap intervals |
| [Source denominators](T4_denominators.csv), [paired denominators](T4_pair_denominators.csv) | Known, complete-case and comparable-study counts |
| [Threshold and missing-label sensitivities](T4_sensitivity.csv) | Prespecified threshold and unknown-treatment variants; descriptive point estimates |
| [Source similarity groups](T5_clusters.csv), [memberships](T5_membership.csv), [focus findings](T5_focus.csv) | Post-hoc similarity groups, bootstrap co-membership and finding-specific paired denominators; not independent-source counts |
| [Model eligibility](T6_eligibility.csv) | Complete-case count and model eligibility for each finding |
| [Latent-parameter summaries](T6_latent_parameters.csv) | Sampler quantiles, R-hat/ESS and boundary fractions; diagnostic output, not endorsed accuracy estimates |
| [Predictive checks](T6_predictive_checks.csv), [pattern summaries](T6_pattern_checks.csv) | Model-fit checks on aggregated response patterns |
| [AUC simulation results](T7_simulation.csv) | Both model AUCs and paired-difference performance; MCSEs and failures |
| [Model ordering](T7_ordering.csv), [DGM checks](T7_dgm.csv) | Synthetic model ordering, ties/reversals and realized generating parameters |
| [Interval-method comparison](T8_interval_sensitivity.csv), [sample diagnostics](T8_sample_diagnostics.csv) | Post-hoc expert-sample interval methods: conditional/all-attempt coverage, paired MCSEs, failures and widths |

`labels-run.json`, `latent-run.json` and `simulation-run.json` record execution settings. `clusters-run.json` and `intervals-run.json` record exploratory-analysis settings. Labels and predictions, study/team identifiers, full sampler draws and Monte Carlo replications are not distributed.

Agreement intervals are percentile bootstrap confidence intervals. Latent-model lower/upper values are sampler quantiles; nonconverged fits do not support credible-interval interpretation, and all primary fits have serious predictive-fit limitations. Simulation coverage is conditional on valid intervals, with failures shown separately. The oracle correction knows its calibration parameters and is deliberately not clipped.

Logit intervals in the interval-method comparison are undefined at boundary AUC or zero variance. Successful coverage over all attempts treats undefined intervals as unsuccessful; valid-interval coverage is also retained. Cluster co-membership is descriptive bootstrap stability, not conditional independence.
