# Research decisions and amendments

I use version numbers to distinguish changes fixed before examining the primary outcomes from exploratory additions made afterward. I edited the wording on 2026-10-29 without changing that chronology or the analytic choices.

| Date | Decision | Outcome exposure |
| --- | --- | --- |
| 2026-10-28 | I adopted a public-data plan (v1.0), replacing the earlier personal-model and Gold58-reference plans. | Public write-up aggregates and dataset schemas inspected; no empirical analysis under this SAP. |
| 2026-10-28 | I clarified identification assumptions, separated selected finals from public maxima, treated external counts as versioned reports, and excluded image-derived fusion from the report-only primary cohort. | Source feasibility review only. |

## SAP v1.1 revisions and freeze

On 2026-10-28, I reviewed plan commit `0c7fecb0d2fb48203097786b54063389101ee5a7` and made four revisions before examining any empirical outcome:

1. All selected final submissions form the primary cohort; bootstrap whole teams. Private-best selection is sensitivity only.
2. Stratify the variance benchmark using the sample-size-weighted score mean M; private-score strata are sensitivity only.
3. Interpret latent estimates as report-extraction quantities. The misclassification simulations use Se/Sp grids primarily; latent-model-derived scenarios are extraction-error-only. A strict image-misclassification lower bound is not mathematically guaranteed without extra assumptions, so it is not claimed.
4. The original minimum scope covers score agreement, a sampling reference, label agreement and baseline misclassification simulations with rho=0/0.2, n=58/977. Statistical computation is capped at 120 minutes, downloads at 30 active minutes. Dependent LCM and the joint stress grid are extensions.

**Outcome exposure at amendment:** public write-up aggregate claims, file schemas and synthetic software tests had been seen. No empirical leaderboard association, label agreement or latent-accuracy result had been calculated for this project. Thus “no results seen” refers to new project empirical outcomes, not to previously read public source claims.

I fixed these choices in the commit introducing v1.1 and recorded its SHA in the execution metadata.

## Execution after the v1.1 freeze

- SAP v1.1 freeze: `074d903aebfcef77bb7418e270380a9b693cc70d`.
- 2026-10-28: I selected in-place extraction in a private Kaggle R notebook as the next acquisition approach. The proposed extractor retains all submissions, excludes names/user IDs and records dataset version/checksums. I did not create or publish that notebook.
- 2026-10-28 14:46:50–14:48:07 UTC: I completed the synthetic sampling reference (16 scenarios × 2,000 replicates; 1.29 minutes). No real leaderboard observations had been analyzed. Its table has no observed variance or excess-variance ratio, and the plot contains only simulated values; I did not substitute these for empirical comparisons.
- Remaining cumulative statistical-computation budget: approximately 118.71 minutes. Data transfers were stopped after timeouts and an HTTP 401 from the anonymous leaderboard download; I replaced the proposed full-table transfer with in-place extraction.

## SAP v1.2: focus on label agreement and misclassification

I narrowed the study to label agreement, testing a no-gold-standard model and misclassification before seeing those outcomes. I retired empirical score comparisons at an early stage and retained the completed sampling reference as an archived output. This removed the need for the four Meta Kaggle extracts.

The SAP records source-specific abstention rules (including Yunus's unmentioned 0.05), a complete-case estimand for the independent latent model, native-R Gibbs computation with explicit orientation constraints, and the exact minimum misclassification simulation and interval design. These choices were frozen before examining the primary label and misclassification outcomes; source descriptions, schemas and the sampling reference had already been inspected.

## Label analysis and simulation after the v1.2 freeze

- SAP freeze: `968c2a9cdb3be5978bbeed5128bad8ba843985f9`. Five primary label CSVs were copied from the previously audited public-source cache into the external data directory; no report or expert-label file was read. All five cover the 4,349-study Dread intersection.
- 2026-10-28: I completed the descriptive label analysis with 2,000 joint study-bootstrap replicates and prespecified threshold/unknown sensitivities (0.11 minutes). Complete-case samples range from 573 to 3,987.
- I evaluated the independent latent models through 36 fits (12 findings × 3 accuracy priors; four chains; 1.07 minutes). Synovitis primary/uniform-prior fits failed diagnostics after the single allowed extension. The other primary fits converged but had severe response-pattern predictive misfit. Posterior estimates are retained as diagnostics, not accepted accuracy or misclassification calibration parameters. No favorable alternative prior replaced the primary analysis.
- I completed four baseline misclassification cells × 2,000 replicates, with 399 paired bootstrap resamples per interval (1.76 minutes). Every cell met bias MCSE <0.005. Parameters remain the prespecified grid, independent of the poorly fitting latent model.
- With the earlier 1.29-minute sampling reference, recorded substantive analyses total 4.22 minutes. Software tests and rendering were separate and well within the remaining 120-minute budget. Optional extensions were not needed for the revised minimum delivery; their omission is documented in the report.
- After outcomes: I added source names to the latent-parameter summaries, MCSE columns for ordering/ties/reversals, and presentation labels. These are deterministic summaries of saved draws, not new selection rules or changed analyses. I removed unused score-data acquisition from the active pipeline and made figure backgrounds white for legibility.

## Concurrent documentation update

On 2026-10-29 (Asia/Shanghai), the release check detected a separate main-branch commit `b1c9fe20cec14d51927a7a1e6b326278fe356046` refining the existing portfolio copy. Its text changes and deleted comparison page were preserved in the research branch. The homepage conflict was resolved by adding only the new research row to the updated Selected Projects table. Statistical code, inputs and results were unchanged. Main was not modified by this synchronization.

## v1.3: post-hoc interpretation and interval sensitivity, 2026-10-29

After reviewing the primary label and simulation results, I chose to add source clustering and an interval-method sensitivity analysis. **All original outcomes had been seen.** The following analyses are exploratory, not preregistered; the v1.2 primary outputs and assumptions remain unchanged. This specification was written before executing the additional analyses.

1. Cluster the five sources using average linkage and dissimilarity `1 - mean(Cohen kappa)` across the 12 findings, with equal finding weights and the primary paired-known denominators. Compare median kappa and five-source-complete-case kappa. Describe a two-cluster cut (chosen after inspecting the pairwise agreement heatmap), with 1,000 joint study-bootstrap resamples for pair co-membership stability, seed 2026102901. Display finding-specific pairwise values for effusion and synovitis. Clusters describe marginal similarity; they neither estimate an effective independent source count nor test conditional independence. Check public provenance descriptions, distinguishing the selected original files from later blends.
2. Compare four 95% intervals on the same 4,000 synthetic, independently generated, perfectly labeled samples: n=58, prevalence=0.15, binormal true AUC=0.90, seed 2026102902. Methods: ordinary percentile bootstrap with 399 and 1,999 resamples (399 is a nested prefix), DeLong normal intervals clipped to [0,1], and logit-delta intervals using DeLong variance. At least 80% valid bootstrap resamples are required. DeLong requires at least two observations in each class; zero variance gives a degenerate normal interval and an undefined logit interval. No boundary continuity correction is introduced. Report interval failures, coverage among valid intervals, successful coverage over all attempts, width and MCSE, plus paired coverage differences relative to bootstrap-399. This is a single expert-sample sensitivity because rho does not affect perfectly labeled samples; it does not rerun or change the noisy-label correction results.
3. Keep raw draws external. Add aggregate clustering and interval-comparison tables and figures. Preserve the 120-minute cumulative computation cap. Reframe findings, rename the project directory, and keep the completed sampling reference outside the main narrative. Do not assert copying, clinical definitions, conditional dependence or accuracy beyond the evidence.

### v1.3 execution

The prespecified post-hoc scripts completed on 2026-10-29: source clustering took 0.02 minutes and the 4,000-replicate interval sensitivity 0.31 minutes. Both analyses retain their post-hoc designation. All three clustering summaries and 1,000 joint bootstrap samples give the same two-group cut; this is not an independent-source count. More bootstrap draws have little effect on coverage; logit intervals improve coverage with more undefined cases. The original agreement, latent-model and misclassification results are unchanged. Figures, tables and prose were reviewed together before publication.

## Readability revision, 2026-10-29

I replaced procedural language and shorthand with descriptive research terms, consolidated limitations in the project page and report, and removed the retired sampling-reference appendix and navigation links. I retained the historical designs here and in the plan to preserve the record. No analysis code, input data or numerical result changed.

2026-10-29: files moved into a single project folder for readability; analysis content and results unchanged.

## v1.4: definition alignment and consensus-reference selection, 2026-10-29

The extension specified a document-only mapping freeze before new encoded outcomes. All prior study outcomes were known. I used only publisher documentation to define the mapping; two sources qualify for any-affirmed and one for moderate-or-greater, so no new latent model is planned. The [v1.4 specification](v1.4/SAP-v1.4.md) fixes the simulated group-inherited-error mechanism, null/effect scenarios, abstention rules and selection estimands before execution. AUC on the two-group-agreement subset must be identical for both reference rules because their labels coincide there. This is a mathematical control, not an observed result. The mapping, scenarios and results are documented in the analysis supplement and completed project report.
