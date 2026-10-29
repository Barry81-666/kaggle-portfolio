# SAP v1.4: documented label definitions and consensus-reference model selection

Version 1.4, 2026-10-29 (Asia/Shanghai). This is an **exploratory extension** after seeing all v1.2/v1.3 results. Its mappings and simulation rules are fixed before examining any new encoded outcome or new simulation result. The previous outcomes remain byte-identical. The project README, main research report and portfolio homepage will not be rewritten before owner review.

## 1. Questions and evidence boundaries

1. For labels that public documentation supports mapping to the same report-assertion target, how do agreement and positive fractions change on the same studies?
2. When model A inherits errors associated with the Steven/Pilkwang/Lixin group (G1), and B inherits errors associated with Dread/Yunus (G2), how does a five-source majority reference affect AUC and model choice? Does restricting evaluation to cases where both groups give the same definite label help, harm or leave selection unchanged?

The simulation represents a possible consequence of training on a group's label style. No model is trained, and no actual participant's training or predictions are inferred. Three votes versus two does not mathematically guarantee favoritism: within-group disagreement, label prevalence, inheritance strength and the latent truth mechanism all matter. The equal-true-AUC scenario tests directional preference rather than presuming it.

## 2. Freeze and provenance

The freeze commit contains this plan, [definition-map.csv](definition-map.csv), [source-documents.csv](source-documents.csv), [simulation-scenarios.csv](simulation-scenarios.csv), their readable tables, and links from SAP.md/DECISIONS.md. It is published on a new branch before any label file is loaded for this extension. Execution records the freeze SHA and SHA-256 of those files; a mismatch stops the new scripts. Any later change to a rule requires a separate dated amendment identifying which outcomes were already seen.

Mappings use only the public publisher descriptions cached during the 2026-10-28 audit, not observed distributions, agreement or model fit. Cache provenance is explicit: live page reads on 2026-10-29 yielded no description text. The selected five original label files and original source hashes remain unchanged. No report, image, expert annotation or personal model output is acquired. Raw labels and replicate-level draws stay outside the repository. All emitted tables are aggregates.

## 3. Documented alignment

The primary target is an explicitly affirmed report abnormality, including mild/trace, rather than any textual mention. The secondary target is moderate-or-greater abnormality. [DEFINITION_MAPPING.md](DEFINITION_MAPPING.md) and the 120-row map fix all twelve finding/source combinations for both targets. Public documentation is source-wide; no finding-specific rule is invented.

Primary any-affirmed mapping: Pilkwang YES/NO/UNK maps to 1/0/missing. Yunus 0.25, 0.55 and [0.90,1] map to 1; 0 maps to 0; 0.05, 0.50, absent values and undocumented numeric codes are missing. Moderate-or-greater uses only Yunus, with 0.25 recoded negative. Numeric code equality tolerance is 1e-8. Report counts of unknown and undocumented values without study identifiers. Unexpected verdict strings stop execution.

Steven, Dread and Lixin lack sufficiently documented positive rules for these targets and do not enter primary harmonized estimates. They retain the original operational coding only in an explicitly non-harmonized five-source sensitivity/context table. It replaces the two documented sources' codings while leaving other codes fixed, without claiming that all five definitions now agree. The simulation in section 5 is a separate exploratory analysis of the original operational labels; it is not an endorsement of the undocumented mappings.

Per target and finding, count document-alignable sources before fitting anything. Fewer than three means **no latent-class model**. Two sources support paired agreement only; one supports positive/missing fractions only. In this frozen map, all twelve findings have two any-affirmed and one moderate-or-greater sources, so no new LCM is run. Even with three sources, count alone would not establish identifiability; the simple three-binary-indicator model is just identified and cannot establish fit by its overall response-pattern degrees of freedom.

For each eligible pair, use the intersection known under both old and new mappings, and compare observed agreement, Cohen kappa, discordance, positive fractions and their changes on that **same** sample. Report all original/new known counts separately. Undefined kappa remains undefined. Use 2,000 joint study-bootstrap resamples (seed 20261029041) for paired changes; require at least 80% valid draws for percentile intervals and disclose failures. Bootstrap cannot account for repeated patients because patient IDs are unavailable. The moderate-only source's fraction change uses the same before/after known sample. Do not select definitions by resulting agreement.

## 4. Reference rules and the common-sample identity

Simulation calibration uses original v1.2 five-source-complete binary observations separately for each finding. Unknowns are not set negative. The number excluded and resulting positive fractions are reported; conclusions concern this selected population. G1 contains Steven/Pilkwang/Lixin; G2 contains Dread/Yunus, fixed from the prior exploratory clustering.

- **Direct majority:** at least three of five labels are positive; otherwise negative. This odd-sized rule has no ties on complete cases.
- **Group-agreement filter:** G1 uses its strict 2-of-3 majority. G2 gives a label only when its two sources agree; a 1:1 split abstains. Keep a case only when G2 is definite and equals G1. The reference on retained cases is that common group label. This is **retaining only cases where both groups agree**, not a new full-cohort weighted voting rule. No favorable tie-breaking or imputation is allowed.

On retained cases, at least four of five sources support that common group label. Consequently the direct-majority label and group-agreement label are identical on every retained case. Their AUC, selected model and errors must be exactly equal on the common evaluable sample. Verify this as an exhaustive 32-pattern test and on every simulation replicate. Apparent benefit comes only from changing which cases are evaluated, not from a different label on the same retained cases.

Report three panels: direct-majority evaluation on all simulated complete cases; direct-majority and group-agreement evaluation on the same retained cases (identity control); and synthetic-truth evaluation on all/retained cases to expose selection-induced changes. Report overall abstention, G2-tie versus between-group-disagreement reasons, retained n, and retained true prevalence. Reference AUC is undefined if either reference class is absent; truth AUC is undefined if either truth class is absent. All attempted replicates remain in failure denominators.

## 5. Empirically constrained simulation generator

Observed positive rates and pairwise agreement do not identify disease prevalence, source error rates or score-error dependence. The generator therefore reproduces the **entire observed five-source joint binary-pattern distribution** but varies the unobserved truth and score relationships. It does not calibrate from the rejected latent fits.

For each finding, let p_l be the empirical frequency of each of 32 complete binary patterns, g1(l) the positive fraction among three G1 labels and g2(l) that among two G2 labels. Sample patterns with replacement from p_l. Primary n equals that finding's original five-source-complete sample size. If n<100 or either majority-reference class has fewer than five observed cases, skip the finding's simulation and report the reason; never replace it with a more favorable sample.

Define z_l = w*g1(l)+(1-w)*g2(l). Set a prevalence proxy pi0 to the empirical mean of (g1+g2)/2. This is a **scenario anchor, not estimated disease prevalence**. Scenario pi is pi0 times the specified multiplier, bounded to [0.02,0.98]; record all values and any bounding. Let q_l = logistic(alpha + beta*(z_l-0.5)), with alpha uniquely chosen so sum(p_l*q_l)=pi. Generate latent truth Y|l ~ Bernoulli(q_l). Primary w=0.5 treats the two groups symmetrically in the truth mechanism, beta=4; sensitivities vary w, beta and pi. These assumptions are not learned as ground truth.

To give models exactly specified **full-population** true AUCs while making their errors share group style, form randomized conditional probability-integral transforms of each group's positive fraction given Y. For group g, its finite conditional distribution is derived exactly from p_l*q_l or p_l*(1-q_l). For its observed group fraction v, sample U uniformly between F_g(v-|Y) and F_g(v|Y), then Z_g=Phi^-1(U). Z_g is standard normal within each truth class and increases with that group's tendency to call the study positive. Independent uniforms are used for the two groups. Numerical endpoint clipping at 1e-12 only prevents infinite normal quantiles.

Model scores are S_A = sqrt(2)*Phi^-1(AUC_A)*Y + sqrt(lambda)*Z_G1 + sqrt(1-lambda)*epsilon_A, and analogously S_B with Z_G2; epsilon terms are independent standard normals. Thus each marginal score is binormal with the specified full-population true AUC. Lambda is an assumed group-style inheritance variance fraction, not fitted from these labels. A swap sensitivity exchanges which model inherits which group while keeping target AUCs unchanged. The actual conditional correlations and source sensitivities implied by this generator are model quantities, not empirical accuracy estimates.

This construction is an explicitly hypothetical joint extension of observed labels to truth and scores. Many other truth assignments reproduce the same observed labels. It demonstrates sensitivity of model selection to those assumptions, not the actual bias of any competition system. It samples test cases without fitting/tuning a model on those same cases.

## 6. Scenarios, estimands and Monte Carlo precision

[SIMULATION_SCENARIOS.md](SIMULATION_SCENARIOS.md) fixes all 13 cells per finding. Primary cells: AUC_A/AUC_B = .85/.85, .86/.85, .85/.86; inheritance lambda=.5, w=.5, beta=4, pi multiplier=1. Sensitivities at equal true AUC vary lambda=0/.25/.75, swap inheritance, w=.25/.75, beta=2/8, and pi multiplier=.5/1.5. No parameter is adjusted to produce a desired winner. Use 2,000 attempted replicates per primary cell and 1,000 per sensitivity cell, seed 20261029042 plus fixed finding/scenario offsets. Same synthetic sample and model scores feed all evaluation rules within each replicate.

Report AUC_A, AUC_B and their difference. Distinguish:

1. **Label-reference bias on the evaluated population:** mean(AUC against consensus - AUC against simulated Y) on the exact same cases, plus paired MCSE. This isolates reference-label distortion from the change in case mix.
2. **Population/selection effect:** mean truth-AUC on retained cases minus the specified full-population true AUC. Also report total consensus-AUC minus the full-population target. Their sum checks the decomposition.
3. **Model selection:** pick the larger reference AUC, with numerical ties at absolute difference <=1e-12 reported separately. For unequal full-population AUCs, misselection means choosing the lower-full-population-AUC model; disclose that filtering may change the retained-population true ordering. Additionally report disagreement with the simulated-Y AUC ordering on the same realized test sample, which is a different finite-sample endpoint. For equal true AUC, report P(select A), P(select B), ties and preference P(A)-P(B), never label a tie in underlying quality as choosing the wrong model.
4. **Paired method contrast:** filtering minus full direct-majority changes in label bias, global-target misselection/preference, and oracle-ranking disagreement, restricted to replicates valid for both; show paired denominators and MCSEs. These contrasts combine altered case mix and sample size and are not pure voting-rule effects. Common-retained-sample method contrasts must be identically zero.

Report conditional-on-valid estimates, attempted/valid counts and failure rates; selection probabilities also have all-attempt denominators with failures separate. Probability MCSE is sqrt(p*(1-p)/R_valid); paired contrasts use SD of replicate differences/sqrt(R_paired); means use SD/sqrt(R_valid). Replicate count is fixed, with no significance-based stopping. Do not claim frequentist confidence-interval coverage from MCSE bands. Per-finding results are primary summaries; any overall summary equally weights findings and does not treat overlapping studies as independent clinical replications.

## 7. Software checks, compute and review delivery

Use R 4.5.1 and existing locked dependencies; do not mutate legacy analysis scripts or outputs. New scripts write only v1.4 subdirectories and verify frozen-file hashes, source-file hashes and absence of new study identifiers in release files. Tests include documented-code mapping, unrecognized-code handling, fewer-than-three LCM gate, old-pattern reconstruction against stored aggregates, all-32-pattern voting identity, PIT probability normalization, known binormal AUC recovery, zero-inheritance equal-AUC symmetry, and exact decomposition/common-sample identities. Synthetic tests do not select simulation scenarios.

Run all primary cells first, followed by sensitivities in frozen table order. Retain the original cumulative 120-minute statistical-computation cap; approximately 4.55 minutes were previously used. Record new wall time. If less than 5 minutes remain, stop at a completed replicate batch/cell and disclose attempted/unfinished cells; do not fill missing results with extrapolation. Raw individual labels, scores and replicate arrays stay external. Publish aggregate mappings, scenarios, empirical changes, simulation summaries and scientific plots for review.

The review document reports results even when alignment worsens agreement, group filtering does not help, or the three-source group has no consistent advantage. It includes a practical evidence table for each finding without declaring any label clinically reliable from agreement alone. The owner reviews this package before any rewrite of the project page or original report.
