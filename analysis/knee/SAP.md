# SAP v2: reliability and dependence of public report-derived knee MRI labels

2026-10-28. This amendment replaces the model-based SAP at commit `1a168398fba563abdbd976f14b0ce408740bea2e`, following the owner's change to public materials only. It is frozen before acquiring or analyzing the official expert-label table. No Barry Wang model predictions, model-selection history or competition rank are required.

## Aim, population and source freeze

Evaluate public report-derived label sets against the competition's expert annotations, describe dependence between their errors, and parameterize simulation studies of imperfect-reference AUC evaluation. Expert annotations are an operational reference, not error-free biological truth. The target of the empirical analysis is the observed expert-annotated subset; it is not a representative estimate of clinical prevalence or of the private leaderboard population.

Use only official competition tables (principally train.csv, containing expert labels and report text) and versioned Kaggle public report-label datasets. Raw tables, report text, identifiers and individual-level derived values stay outside the repository and are never sent to remote analysis or LLM services. Python handles read-only acquisition/schema normalization; R performs statistics. No imaging, weights, training or inference are needed. A Kaggle login/rules requirement must be satisfied normally; public mirrors are not a substitute for official ground truth.

Freeze dataset slugs, versions, file hashes, column mappings, score direction, threshold conventions, label-generation ancestry and Gold58-use disclosures before empirical analysis. Counts 58/4,349 and test sizes approximately 390/910 are working expectations, not forced sample sizes. Derive actual gold membership from complete official labels. Reject partial expert labels pending an amendment. Retain source coverage and missingness tables; do not silently inner-join away a missing study. Report-only sources lack verified patient identity, so use study-level bootstrap and state that unobserved repeat patients can narrow intervals. If official tables contain reliable patient links, prespecify clustering before outcomes are evaluated.

## Provenance and copied-label audit

For every source, distinguish: documented direct expert-label replacement; documented gold-informed tuning; shared-parent/derived blend; unknown gold use; and no reported replacement/tuning (not proof of independence).

Read generation code or author statements and inspect a label_source field if supplied. Flag exact agreement with binary expert labels, proportions of exact 0/1 scores, and differences between gold and non-gold endpoint mass. Perfect agreement alone is a suspicious pattern, not proof of copying. Never accuse an author of misconduct: deliberate replacement can be appropriate for training but invalid for independent validation.

Sources with documented replacement are excluded from gold accuracy rankings, dependence estimates and consensus, with an explicit exclusion reason. Sources with known gold tuning or common ancestry are shown separately; they cannot count as independent replications. Numeric checks corroborate provenance, not replace it. Do not use report-annotated additions to Gold58 as expert truth.

## Q1: agreement with expert labels

Use each source's available gold records for its standalone description and a fixed common-record intersection for paired source/consensus comparisons. Publish the respective denominators. Per finding and source: TP/FP/FN/TN, expert and apparent prevalence, Se/Sp, PPV/NPV, observed agreement, Cohen's kappa and PABAK. Se/Sp/PPV/NPV receive Clopper-Pearson 95% intervals, assuming independent examinations. Kappa has a paired study-bootstrap percentile interval (B=2,000), not a falsely labeled exact binomial interval. Shared bootstrap indices preserve dependencies across sources and findings.

Primary threshold is score >=0.5, recorded explicitly because a 0.5 may encode unmentioned rather than probability. Sensitivities use 0.3/0.7 and source-documented unmentioned-as-negative / unmentioned-excluded policies. Never infer unmentioned from 0.5 unless the source documents that encoding. Soft scores described only as rank scores are not called calibrated probabilities. Expert-reference soft-score AUC is optional descriptive discrimination of the labeler, not imaging-model validation.

Only twelve defined finding AUCs form macro AUC. Otherwise report a separately named available-finding mean and list its findings. A bootstrap interval is suppressed if fewer than 90% of attempted draws are valid (minimum 20); report attempted/valid counts and do not resample until enough draws succeed. No significance-based source ranking, tuning thresholds or choosing best source per finding on Gold58.

## Q2: dependent errors and averaging

For each pair, finding and expert state D=0/1, form binary errors E_j=1(label_j != D) on paired complete records. Report the error 2x2 table, marginal error rates, excess joint error P(E1=1,E2=1)-P(E1=1)P(E2=1), phi correlation where nondegenerate, and paired-bootstrap intervals. Constant errors make phi undefined, not zero. Small stratum counts are displayed. A near-zero phi is not proof of general independence of continuous labels. Report inherited ancestry alongside these estimates.

Prespecify an equal-weight mean of base sources with no documented direct replacement or gold tuning; do not add a derived blend alongside its parents. Unknown prior use remains an explicit limitation. Source membership is fixed from provenance, not observed accuracy. If fewer than two eligible sources have joint coverage, do not produce a consensus. Use the same common gold subset to compare each member and the mean, with paired intervals for Se/Sp/kappa and AUC differences. Equal averaging of heterogeneous rank/soft scales is an operational sensitivity analysis, not a calibrated risk estimate.

## Q3: simulation (ADEMP)

Aims: quantify AUC evaluation bias and correction under noisy references; precision at 58 and approximately 910 examinations; and public/private ranking instability. The simulated imaging score is hypothetical. There is no empirical estimate of its conditional association with report labels in this public-only design.

Parameterization: Q1 supplies each finding's Se/Sp and Gold58 prevalence; Q2 supplies joint error probabilities conditional on expert state. These are estimates in the verified sample. Use bootstrap-derived parameter uncertainty and prevalence sensitivity values (0.05/0.15/0.40), rather than treating Gold58 prevalence as population prevalence. Before official data are available, only clearly labeled hypothetical scenarios can run. Do not substitute published aggregate results for a new empirical run.

For pairwise reference labels, simulate the observed conditional 2x2 probabilities directly; contrast with independent errors at the same marginal Se/Sp. This preserves binary dependence without equating phi with latent Gaussian correlation. To investigate dependence between the hypothetical model score and label error, vary a separately identified sensitivity parameter. This parameter cannot be estimated from label-label dependence. Fix true AUC at 0.80/0.90/0.95, use a binormal score model and explicitly document ties in label means. Gold-dependent tuning and direct gold replacement receive separate contamination scenarios; they are not corrections to clinical truth.

Compare oracle expert-reference AUC, naive weak-reference AUC and the conditional-independence correction. With a=P(D=1|W=1), b=P(D=0|W=0), A_W = ab A + (1-a)(1-b)(1-A) + [a(1-b)+(1-a)b]/2 = 1/2+(a+b-1)(A-1/2). Midrank handling preserves this identity with ties. Estimate Se/Sp on simulated gold and weak prevalence on simulated silver; use Rogan-Gladen prevalence, preserving the raw value and recording truncation. Reject Se+Sp<=1 or attenuation a+b-1<=0.1. Flag corrected AUC outside [0,1] instead of silently clamping. Estimated ratios need not be finite-sample unbiased. Also run oracle-parameter checks to separate formula validity from estimation error.

Bootstrap gold and silver separately, refitting correction in every draw. Report bias, empirical SD, RMSE, coverage, interval width and failure/out-of-range rates with Monte Carlo standard errors. A pilot validates software only. Full scenarios require at least 1,000 repetitions (up to 2,000 when bias MCSE exceeds 0.005); unachieved precision is reported. No M4 true-label imputation is used in the public-only empirical analysis.

For precision and rankings, simulate twelve outcomes jointly, varying their correlation and paired-model residual correlations 0.6/0.8/0.9. Compare n=58 and n=910 with the same estimand. Public and private samples are independent draws, with paired model scores within each sample. Approximate sizes 390/910 and three-decimal display are scenario parameters; vary sample sizes. True macro-AUC differences are 0.001/0.002/0.005/0.01. Report strict reversal, public error and display ties separately, plus undefined-macro frequency. Do not infer private rank or clinical generalization. Power/minimum detectable difference requires a separately calibrated paired test and is not claimed by this version.

## Reproducibility and publication

Publish only aggregate tables, figures, source/version manifests, scripts and sanitized session information. Store raw input hashes and execution settings locally; the public manifest contains hashes but no records/IDs/reports. Every numerical empirical result must be script-generated; absent official inputs means no empirical T1/T2 is filled. Record implemented, executed and inferred states separately. The author's imaging model can be added later under a new SAP amendment.

## References

- [Morris, White and Crowther (2019), simulation design and Monte Carlo error](https://doi.org/10.1002/sim.8086).
- [Maier-Hein et al. (2018), challenge-ranking instability](https://doi.org/10.1038/s41467-018-07619-7).
- [Comparative diagnostic accuracy with imperfect reference standards (2021)](https://pubmed.ncbi.nlm.nih.gov/33845775/). The AUC mixture identity is derived above rather than attributed to an unverified formula citation.
- [Public RSNA code review](SOURCES.md).
