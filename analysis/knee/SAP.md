# Statistical analysis plan: knee MRI with imperfect reference standards

Version 1, 2026-10-28. This plan is committed before any analysis of the owner's expert labels. Only synthetic data may be evaluated until the local configuration and prediction provenance are completed. This is a retrospective analysis plan, not a claim of prospective registration before model development.

## Questions and estimands

1. How do a specified report-derived labeler and expert annotations disagree, finding by finding?
2. Under which assumptions do imperfect-reference correction and validation-sample imputation estimate discrimination more accurately than an uncorrected reference?
3. How do sample size, rare findings and within-person dependence affect precision and simulated leaderboard comparisons?

Expert annotations are the operational reference, not biological truth. The empirical AUC is P(score in an expert-positive examination exceeds score in an expert-negative examination), with half credit for ties. M1 describes the verified cohort. Transport to the silver population requires assumptions about selection and case mix. AUC is not calibration or clinical utility.

The planned population is the owner's eligible held-out examinations. The counts 58 gold and 4,349 silver are provisional descriptions from other public implementations; 82% agreement is not an established result for this labeler. Count all available and excluded records. Do not force these numbers. A public implementation actually retains 57 gold records after its label merge.

## Required local decisions and execution gate

Before real-data assembly, record: gold use in tuning/model/threshold selection (yes/no/unknown); the named primary checkpoint or recipe; exact input paths; patient and duplicate metadata availability; language versus script availability; and prediction/training membership evidence. Unknown gold history is permitted only with an explicit potentially optimistic interpretation. Unknown model or training membership prevents execution. No personal competition role or private rank is inferred from source code.

The preferred initial matched analysis is one prespecified fold model, evaluated on its silver validation fold and the untouched gold cohort. All other silver folds are excluded from this analysis. An ordinary five-fold ensemble is not out of fold on all silver records. Pooled five-fold OOF versus gold ensemble is a different scoring protocol and cannot enter the joint M3/M4 analysis. A later matched cross-fitted design needs a separate amendment and gold prediction assignment fixed without labels. Do not select a model with the expert outcomes.

## Data contract and audit

Python only exports existing local CSV predictions. R performs the analysis. A local manifest identifies metadata, soft labels, predictions, checkpoint hashes, the fold file, training membership and optional duplicate map. Inputs and row-level intermediates must reside outside the repository. No cloud API receives them.

The canonical local file has one examination per row: study_id, cluster_id, gold, fold, and y_expert_*, w_soft_*, s_* for the twelve findings. Optional mentioned_* flags distinguish genuinely unmentioned findings; script, language, manufacturer and field_strength are optional. Do not infer language from script or infer unmentioned status from a soft-label value.

Cluster IDs are connected components of available patient links AND verified duplicate links. Missing patient values are not a shared patient. If no patient ID exists, explicitly record duplicate-group or study fallback. Verify: unique IDs; exact eligible prediction coverage; no training/validation or gold/training cluster overlap; one OOF prediction per included silver examination; no cross-fold clusters; probabilities in [0,1]; binary observed expert outcomes; and complete expert labels for the proposed twelve-label analysis. A missing cohort member fails the export rather than silently disappearing in an inner join. Audit counts precede metrics.

## Q1: label reliability and paired discrimination

At thresholds 0.5 (primary), 0.3 and 0.7, report per finding: expert positives/negatives, weak positives, TP/FP/FN/TN, sensitivity, specificity, PPV, NPV, observed agreement, kappa and PABAK. Clopper-Pearson intervals are examination-binomial descriptive intervals; they are not cluster-valid when examinations repeat within people. Add cluster-bootstrap intervals to the main reliability table. Exact McNemar p-values are exploratory and suppressed when clusters contain multiple examinations; they are not a primary hypothesis test or a bias estimator.

Soft-label sensitivity and specificity are explicitly named average soft scores conditional on expert state, not operating-point sensitivity or specificity. If mentioned flags are provided, repeat agreement under unmentioned-as-negative and unmentioned-excluded policies. Otherwise mark these sensitivities unavailable.

Within gold, calculate AUC_expert, AUC_weak and their paired difference using the same examinations and the same predictions. Bootstrap whole clusters jointly across all twelve findings (B=2,000). Report every undefined replicate and the effective bootstrap count; with fewer than 90% valid replicates suppress the percentile interval. Do not repeatedly resample until a desired number of successful replicates is obtained. Report macro AUC only when all twelve findings are defined. An available-finding mean is a separately named descriptive statistic, with the included findings listed.

Conditional dependence is described by AUC of model score for weak-label status separately within expert-negative and expert-positive strata. AUC=0.5 does not prove independence; it only indicates no detected rank separation. Report per-finding estimates and a fixed, equally weighted mean over originally eligible findings, retaining shared cluster resampling. Do not pool different findings' raw scores as interchangeable observations. Dependence can bias the correction in either direction.

## Q2: estimators and uncertainty

M1 is empirical expert-reference AUC in gold. It is a descriptive anchor, not guaranteed unbiased for the silver population. M2 is weak-reference AUC in the eligible held-out silver set; a large sample does not establish accuracy.

M3 assumes score S is independent of weak label W conditional on expert disease state D, and that labeler sensitivity/specificity transport from gold to silver. Let a=P(D=1|W=1), b=P(D=0|W=0), and A be the target expert-reference AUC. Mixture expansion gives A_W = ab A + (1-a)(1-b)(1-A) + [a(1-b)+(1-a)b]/2 = 1/2 + (a+b-1)(A-1/2). Half credit for ties preserves this identity; absence of ties is unnecessary. Hence A = 1/2 + (A_W-1/2)/(a+b-1).

Estimate Se and Sp on gold and weak prevalence p_w on eligible silver. Rogan-Gladen prevalence is (p_w+Sp-1)/(Se+Sp-1). Report the raw value and any [0,1] truncation. Transform to PPV=Se*pi/p_w_model and NPV=Sp*(1-pi)/(1-p_w_model). If Se+Sp<=1, a denominator is zero, or PPV+NPV-1<=0.1, report not estimable. Preserve out-of-range corrected AUCs as a diagnostic, not a valid probability; never silently clamp them. Direct gold PPV/NPV is a sensitivity analysis. Finite-sample ratio estimates are not exactly unbiased even if the population identity holds.

M4 fits a prespecified additive Firth logistic model D ~ w_soft + score in gold and imputes silver labels M=50 times. No outcome-driven feature selection or splines. Parameter draws use the fitted covariance normal approximation and each missing outcome is a Bernoulli draw. This approximation is explicitly experimental at n=58. Inference uses an outer cluster bootstrap, refitting and re-imputing within each replicate and taking quantiles of replicate mean AUCs (Boot MI), not quantiles of pooled B*M draws or Rubin rules without valid complete-data variances. MAR requires verification independent of D conditional on the included observed variables, overlap and a sufficiently correct imputation model. Firth addresses separation, not MNAR or selection bias. Fitting failures and degenerate classes remain failures. More imputations is a Monte Carlo sensitivity check. M4 targets the silver cohort; M1 targets gold, and equality of targets requires transportability.

Resample gold and silver clusters independently within their disjoint cohorts, preserving all finding columns. These intervals are conditional on the fitted imaging models and predictions, not intervals for the entire model-training algorithm. Do not choose the headline method from gold-derived best-looking results. M1 stays the descriptive anchor; M2-M4 are assumption-sensitive comparisons. Simulations assess methods rather than turn a selected method into a validated truth estimator.

## Simulation plan (ADEMP)

Aims: quantify bias, RMSE, uncertainty and failure rates under known truth. The single-finding generator uses D~Bernoulli(pi), Z~N(sqrt(2)*qnorm(A)*D,1), score=Phi(Z), and a latent weak-label variable whose residual correlation with the score residual is rho. Conditional thresholds give specified Se/Sp. Verification selection is MCAR, depends on W (MAR) or on D (MNAR). Record the sampling mechanism and target population, not only n_gold.

Baseline: n_silver=4,349, n_gold=58, pi=0.15, Se=0.85, Sp=0.90, A=0.90, rho=0. These are hypothetical parameters. One-factor sensitivities: gold 150/300; prevalence 0.05/0.40; A 0.80/0.95; rho +/-0.2 and +/-0.4; Se/Sp 0.70/0.80 and 0.95/0.98; MAR and MNAR. After cohort confirmation, add the actual eligible fold size. A smoke mode is software validation, not the final simulation study.

The full run uses at least 1,000 replicates, increasing to a prespecified maximum of 2,000 when bias MCSE exceeds 0.005, and reports unmet precision targets. Publish attempted/valid counts, bias, empirical SD, RMSE, interval coverage and mean width with Monte Carlo standard errors. MCSE for empirical SD uses the sample fourth moment; RMSE uses the delta method. Report coverage conditional on finite intervals and the unconditional fraction of attempted replications yielding a covering interval. No selective reporting of successful correction/imputation. M3 population identity is tested with oracle parameters separately from estimated-parameter performance. Rare outcomes and undefined macro AUC are part of the results.

## Q3: precision and leaderboard scenarios

On real gold predictions, compare study versus cluster bootstrap variances and report their ratio only if both are defined and positive. Interpret a ratio of one under study fallback as absence of identifiable clustering, not proof of independent patients.

Leaderboard experiments simulate all twelve findings jointly, with shared subject-level latent variation. Vary disease and score correlation across findings as well as paired-model residual correlation (0.6/0.8/0.9); this residual correlation is not assumed to equal the observed raw-score correlation. Public/private samples are independently drawn, with paired model scores inside each sample. Use approximate sample sizes 390/910 plus sensitivity values, and Delta in {0.001,0.002,0.005,0.01}. Report strict ranking reversal, public error and displayed ties separately; ties are not reversals. Three-decimal rounding is a display scenario. Exclude undefined macro values only with explicit counts. These are hypothetical sampling calculations, not an estimate of Barry Wang's private ranking.

Minimum detectable differences require a calibrated paired test with the same multilabel dependence. Do not infer them from a single-finding DeLong formula or a fixed correlation alone. Implementation and execution of the full power grid remain a later milestone after the null type-I-error check and cohort design are settled. The optional winner's curse, latent-class model and subgroup meta-analysis are deferred.

## Outputs and deviations

Only aggregate tables, figures, software checks and session information may be published. T1/T2/T3 and real-data precision tables are generated only from authenticated local inputs; synthetic outputs carry a simulation label. Each result links to a command, seed, configuration and software version. No images, report excerpts, IDs, row-level predictions or model weights enter Git. The report distinguishes implemented, executed and inferred.

Prespecified changes from the supplied draft: provisional counts; matched single-fold estimand; no unconditional 'unbiased M1' assertion; dependence has no fixed bias direction; cluster caveat for exact binomial/McNemar inference; M4 parameter uncertainty and Boot MI; no data-dependent headline-method selection; no untested macro-AUC power claim. Subsequent changes belong in [DEVIATIONS.md](DEVIATIONS.md).

## Method references

- [Morris, White and Crowther (2019), ADEMP and Monte Carlo error](https://doi.org/10.1002/sim.8086).
- [Schomaker and Heumann (2018), bootstrap and multiple imputation](https://doi.org/10.1002/sim.7654).
- [Maier-Hein et al. (2018), challenge-ranking instability](https://doi.org/10.1038/s41467-018-07619-7).
- [Firth logistic regression implementation and manual](https://cran.r-project.org/web/packages/logistf/logistf.pdf).
- [Comparative diagnostic accuracy with imperfect references (2021)](https://pubmed.ncbi.nlm.nih.gov/33845775/). Staquet/Brenner sensitivity/specificity corrections motivate assumption checking; they are not cited as the source of an unverified AUC formula. The mixture identity is derived above.
