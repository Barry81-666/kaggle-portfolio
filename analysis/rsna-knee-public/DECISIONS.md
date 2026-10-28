# Decisions and amendments

| Date | Decision | Outcome exposure |
| --- | --- | --- |
| 2026-10-28 | Adopt public-only leaderboard/label SAP v1.0; supersede personal-model and Gold58-reference plans. | Public write-up aggregates and dataset schemas inspected; no empirical analysis under this SAP. |
| 2026-10-28 | Correct identification assumptions, separate selected finals from public maxima, treat external counts as versioned reports, and exclude image-derived fusion from the report-only primary cohort. | Source feasibility review only. |

## SAP v1.1 approval and freeze

The owner approved SAP commit `0c7fecb0d2fb48203097786b54063389101ee5a7` on 2026-10-28, conditional on four amendments, and explicitly authorized the first A checkpoint without merging main. These amendments were recorded before any empirical outcome analysis:

1. All selected final submissions form the primary cohort; bootstrap whole teams. Private-best selection is sensitivity only.
2. Stratify the variance benchmark using the sample-size-weighted score mean M; private-score strata are sensitivity only.
3. Interpret latent estimates as report-extraction quantities. C uses Se/Sp grids primarily; B-derived scenarios are extraction-error-only. A strict image-misclassification lower bound is not mathematically guaranteed without extra assumptions, so it is not claimed.
4. Minimum delivery is A3.1/A3.2/B4.1 and C baseline rho=0/0.2, n=58/977. Statistical computation is capped at 120 minutes, downloads at 30 active minutes. Dependent LCM and the joint stress grid are extensions.

**Outcome exposure at amendment:** public write-up aggregate claims, file schemas and synthetic software tests had been seen. No empirical leaderboard association, label agreement or latent-accuracy result had been calculated for this project. Thus “no results seen” refers to new project empirical outcomes, not to previously read public source claims.

The v1.1 freeze is the Git commit introducing this section and the matching SAP version. Its exact SHA is stored in the local approval receipt and later execution records. Main must not be merged without separate owner approval.

## Execution after the v1.1 freeze

- SAP v1.1 freeze: `074d903aebfcef77bb7418e270380a9b693cc70d`.
- 2026-10-28: owner chose in-place extraction in a private Kaggle R notebook. The new extractor retains all submissions, excludes names/user IDs and records dataset version/checksums. No notebook was created, published or modified by this assistant.
- 2026-10-28 14:46:50–14:48:07 UTC: completed the synthetic A3.2 reference (16 scenarios × 2,000 replicates; 1.29 minutes). No real leaderboard observations had been analyzed. T3 currently has no observed variance or excess-variance ratio; F2 contains only the sampling reference. This is a staged deliverable, not a substitution for empirical T1/T2/F1.
- Remaining cumulative statistical-computation budget: approximately 118.71 minutes. Data transfers were stopped after timeouts and an HTTP 401 from the anonymous leaderboard download; full-table acquisition is superseded by the owner's in-place extraction.

## SAP v1.2: owner-directed B/C focus

Before any B or C outcomes, the owner instructed that label evaluation and misclassification become the main project, and that empirical A be dropped because little A work had been done. The completed A sampling reference is retained only as a supplement. The owner no longer needs to produce the four Meta Kaggle files.

The SAP records source-specific abstention rules (including Yunus's unmentioned 0.05), a complete-case estimand for the independent latent model, native-R Gibbs computation with explicit orientation constraints, and the exact C minimum simulation/interval design. These choices were frozen before the first B/C analysis; source descriptions, schemas and A simulations had already been inspected.

## B/C execution after the v1.2 freeze

- SAP freeze: `968c2a9cdb3be5978bbeed5128bad8ba843985f9`. Five primary label CSVs were copied from the previously audited public-source cache into the external data directory; no report or expert-label file was read. All five cover the 4,349-study Dread intersection.
- 2026-10-28: B descriptive analysis completed 2,000 joint study-bootstrap replicates and prespecified threshold/unknown sensitivities (0.11 minutes). Complete-case samples range from 573 to 3,987.
- B independent latent models completed 36 fits (12 findings × 3 accuracy priors; four chains; 1.07 minutes). Synovitis primary/uniform-prior fits failed diagnostics after the single allowed extension. The other primary fits converged but had severe response-pattern predictive misfit. Posterior estimates are retained as diagnostics, not accepted accuracy or C calibration parameters. No favorable alternative prior replaced the primary analysis.
- C completed four baseline cells × 2,000 replicates, with 399 paired bootstrap resamples per interval (1.76 minutes). Every cell met bias MCSE <0.005. Parameters remain the prespecified grid, independent of B's failed model.
- With the earlier 1.29-minute A supplement, recorded substantive analyses total 4.22 minutes. Software tests and rendering were separate and well within the remaining 120-minute budget. Optional extensions were not needed for the revised minimum delivery; their omission is documented in the report.
- After outcomes: added source names to T6, MCSE columns for ordering/ties/reversals, and presentation labels. These are deterministic summaries of saved draws, not new selection rules or changed analyses. Removed unused empirical A acquisition/assembly from the active pipeline. Made figure backgrounds white for legibility. No main merge is authorized.

## Concurrent documentation update

On 2026-10-29 (Asia/Shanghai), the release check detected a separate main-branch commit `b1c9fe20cec14d51927a7a1e6b326278fe356046` refining the existing portfolio copy. Its text changes and deleted comparison page were preserved in the research branch. The homepage conflict was resolved by adding only the new research row to the updated Selected Projects table. Statistical code, inputs and results were unchanged. Main was not modified by this synchronization.

## v1.3: post-hoc interpretation and interval sensitivity, 2026-10-29

The owner reviewed the full B/C results, requested source clustering and an interval sensitivity analysis, and authorized merging after revisions. This supersedes the earlier no-merge status. **All original outcomes had been seen.** The following analyses are exploratory, not preregistered; the v1.2 primary outputs and assumptions remain unchanged. This specification was written before executing the additional analyses.

1. Cluster the five sources using average linkage and dissimilarity `1 - mean(Cohen kappa)` across the 12 findings, with equal finding weights and the primary paired-known denominators. Compare median kappa and five-source-complete-case kappa. Describe a two-cluster cut (chosen after inspecting F5), with 1,000 joint study-bootstrap resamples for pair co-membership stability, seed 2026102901. Display finding-specific pairwise values for effusion and synovitis. Clusters describe marginal similarity; they neither estimate an effective independent source count nor test conditional independence. Check public provenance descriptions, distinguishing the selected original files from later blends.
2. Compare four 95% intervals on the same 4,000 synthetic, independently generated, perfectly labeled samples: n=58, prevalence=0.15, binormal true AUC=0.90, seed 2026102902. Methods: ordinary percentile bootstrap with 399 and 1,999 resamples (399 is a nested prefix), DeLong normal intervals clipped to [0,1], and logit-delta intervals using DeLong variance. At least 80% valid bootstrap resamples are required. DeLong requires at least two observations in each class; zero variance gives a degenerate normal interval and an undefined logit interval. No boundary continuity correction is introduced. Report interval failures, coverage among valid intervals, successful coverage over all attempts, width and MCSE, plus paired coverage differences relative to bootstrap-399. This is a single expert-sample sensitivity because rho does not affect perfectly labeled samples; it does not rerun or change the noisy-label correction results.
3. Keep raw draws external. Add aggregate T5/T8 and figures F5c/F8. Preserve the 120-minute cumulative computation cap. Reframe findings, rename the project directory, and place the completed leaderboard reference only in the report supplement. Do not assert copying, clinical definitions, conditional dependence or accuracy beyond the evidence.

### v1.3 execution

The prespecified post-hoc scripts completed on 2026-10-29: source clustering took 0.02 minutes and the 4,000-replicate interval sensitivity 0.31 minutes. Both analyses retain their post-hoc designation. All three clustering summaries and 1,000 joint bootstrap samples give the same two-group cut; this is not an independent-source count. More bootstrap draws have little effect on coverage; logit intervals improve coverage with more undefined cases. The original T4/T6/T7 results are unchanged. Figures, tables and prose were reviewed together before publication.
