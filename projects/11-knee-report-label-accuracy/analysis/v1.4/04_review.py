"""Build aggregate-only review tables and manuscript; no raw label input."""
from pathlib import Path
import csv,json

here=Path(__file__).resolve().parent
project=here.parent.parent
results=project/'results/v1.4'
def rows(name):
    with (results/name).open() as f:return list(csv.DictReader(f))
def num(row,key):return float(row[key]) if row[key] else float('nan')
def pct(v):return f'{100*v:.1f}%'
def pp(v):return f'{100*v:+.1f}'
def mdtable(headers,data):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in data])
alignment=rows('alignment-paired-changes.csv')
ag=[r for r in alignment if r['metric']=='agreement']
kap={r['finding']:r for r in alignment if r['metric']=='kappa'}
cohort={r['finding']:r for r in rows('simulation-cohort.csv')}
sim=rows('simulation-summary.csv')
lookup={(r['finding'],r['scenario'],r['method']):r for r in sim}
paired={(r['finding'],r['scenario']):r for r in rows('simulation-paired-contrasts.csv')}
run=json.loads((results/'simulation-run.json').read_text())
assert run['completed_cells']==156 and run['attempted_replicates']==192000
advice={
 'ACL':'Use the documented any-affirmed map for report-label work; reserve clinical validation for an independent reference.',
 'MCL':'Resolve mild/grade-1 inclusion before pooling; the original apparent disagreement largely disappears for this pair.',
 'Medial Meniscus':'Specify what counts as an affirmed abnormality; adjudicate residual disagreements before interpreting accuracy.',
 'Lateral Meniscus':'Specify what counts as an affirmed abnormality; adjudicate residual disagreements before interpreting accuracy.',
 'Medial OA':'Include mild OA only if it matches the study target; do not infer an image-based grade from report agreement.',
 'Lateral OA':'Include mild OA only if it matches the study target; do not infer an image-based grade from report agreement.',
 'PF OA':'Declare the severity threshold before model evaluation; the shared report target differs from clinical grading.',
 'Effusion':'Make trace/mild effusion inclusion explicit; this definition change explains most pairwise disagreement.',
 'Synovitis':'Define mild inclusion and address missingness; only 599 studies support this paired comparison.',
 "Baker's":'Use an explicit presence target and quantify missingness; known pairs cover only about half the cohort.',
 'Contusion':'Prioritize review of residual discordance: about 9% remains even after the documented mapping.',
 'Fracture':'High agreement holds on a selected 1,485-study subset; preserve unknowns and validate independently.'}
practical=[]
for r in ag:
    f=r['finding'];c=cohort[f]
    practical.append(dict(finding=f,paired_n=r['common_n'],paired_cohort_fraction=int(r['common_n'])/4349,
       before_agreement=r['before'],after_agreement=r['after'],after_kappa=kap[f]['after'],
       simulation_complete_n=c['complete_n'],filter_retained_n=c['observed_retained_n'],
       retained_fraction_of_complete=c['retained_fraction'],retained_fraction_of_original=int(c['observed_retained_n'])/4349,
       recommendation=advice[f],evidence_boundary='report-assertion agreement; not clinical accuracy or source independence'))
with (results/'practical-evidence-table.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(practical[0]));w.writeheader();w.writerows(practical)

mapping_table=mdtable(['Source','Any affirmed abnormality','Moderate or greater','Permitted use'],[
 ['Pilkwang','YES=1; NO=0; UNK=missing','Not documented','Primary paired agreement'],
 ['Yunus','0.25/0.55/0.90–1=1; 0=0','0.55/0.90–1=1; 0/0.25=0','Both report targets; 0.05/0.50/undocumented=missing'],
 ['Steven full/v1','Positive definition not documented','Not documented','Original operational sensitivity/context only'],
 ['Dread','Not documented sufficiently','Not documented','Original operational sensitivity/context only'],
 ['Lixin','Description empty','Not documented','Original operational sensitivity/context only']])
align_table=mdtable(['Finding','Same paired n','Before','After','Change, pp (95% bootstrap interval)','Kappa before → after'],[
 [r['finding'],r['common_n'],pct(num(r,'before')),pct(num(r,'after')),
  f"{pp(num(r,'change'))} ({pp(num(r,'change_lower'))}, {pp(num(r,'change_upper'))})",
  f"{num(kap[r['finding']],'before'):.3f} → {num(kap[r['finding']],'after'):.3f}"] for r in ag])
equal_table=[];unequal_table=[];bias_table=[]
for f,c in cohort.items():
    d=lookup[f,'equal_true_auc','full_direct'];k=lookup[f,'equal_true_auc','retained_both_agree']
    equal_table.append([f,c['complete_n'],f"{c['observed_retained_n']} ({pct(num(c,'retained_fraction'))})",
      pct(num(d,'p_select_A_estimate')),pct(num(k,'p_select_A_estimate')),
      f"{num(d,'reference_delta_estimate'):+.3f}",f"{num(k,'reference_delta_estimate'):+.3f}",f"{num(k,'truth_delta_estimate'):+.3f}"])
    vals=[]
    for sc in ['A_better','B_better']:
        for method in ['full_direct','retained_both_agree']:
            z=lookup[f,sc,method];vals.append(pct(num(z,'misselection_global_estimate')))
    unequal_table.append([f]+vals)
    bias_table.append([f]+[f"{num(z,'label_bias_'+m+'_estimate'):+.3f}" for z in [d,k] for m in ['A','B']])
equal_table=mdtable(['Finding','Complete n','Observed retained n (%)','P(A), full','P(A), retained','Ref ΔAUC, full','Ref ΔAUC, retained','Truth ΔAUC, retained'],equal_table)
unequal_table=mdtable(['Finding','A better: full error','A better: retained error','B better: full error','B better: retained error'],unequal_table)
bias_table=mdtable(['Finding','Full bias A','Full bias B','Retained bias A','Retained bias B'],bias_table)
sensitivity=[]
for scenario in ['no_inheritance','weak_inheritance','strong_inheritance','swap_training_groups','truth_favors_group1','truth_favors_group2','weak_truth_alignment','strong_truth_alignment','lower_prevalence','higher_prevalence']:
    ds=[r for r in sim if r['scenario']==scenario and r['method']=='full_direct'];ks=[r for r in sim if r['scenario']==scenario and r['method']=='retained_both_agree']
    def span(rs):return f"{pct(min(num(r,'p_select_A_estimate') for r in rs))}–{pct(max(num(r,'p_select_A_estimate') for r in rs))}"
    sensitivity.append([scenario,span(ds),span(ks),str(sum(num(r,'p_select_A_estimate')>.5 for r in ds)),str(sum(num(r,'p_select_A_estimate')>.5 for r in ks))])
sens_table=mdtable(['Equal-AUC sensitivity','P(A) range, full','P(A) range, retained','Findings P(A)>50%, full /12','Retained /12'],sensitivity)
practical_table=mdtable(['Finding','After alignment','Paired coverage of 4,349','Practical next step'],[
 [r['finding'],pct(float(r['after_agreement'])),pct(r['paired_cohort_fraction']),r['recommendation']] for r in practical])
review=f'''# SAP v1.4 review: definition alignment and consensus-reference model selection

**Exploratory analysis supplement, 2026-10-29.**

**Protocol-publication deviation:** the first freeze upload was truncated. The complete plan was fixed and checked locally, but was not fully published before analysis. Missing files were repaired after results were known. See [FREEZE_DEVIATION.md](FREEZE_DEVIATION.md).

The useful research question is whether report-extraction labels with different definitions can be pooled and then used to select medical AI models. Five public label sources share 4,349 studies. The new analysis finds a large, directly documented definition effect in the two alignable sources, and shows in calibrated hypothetical simulations why consensus-reference model selection can be misleading. This is a matched comparison of public extraction outputs; it is not a causal natural experiment or an independent clinical validation.

## 1. Intended definitions and what could actually be aligned

The [attempted freeze](https://github.com/Barry81-666/kaggle-portfolio/commit/0053954a94baec9545e6f2e0c88fe43438456d3b) was published at **05:32:34 UTC**, before alignment began at **05:36:31 UTC**, but final remote checks found the transfer incomplete. The scenario and source-document CSVs were present; the full new SAP and standalone map were missing, with 113 mapping rows embedded in a malformed old SAP file. The complete intended files were fixed locally and checked before execution. Their restoration to GitHub occurred after results. Rules came only from cached public descriptions and were not changed in response to outcomes. See [readable mapping](DEFINITION_MAPPING.md), [120-row map](definition-map.csv), [source evidence](source-documents.csv), and [intended SAP](SAP-v1.4.md). All original outcomes had already been seen. This is exploratory work with a documented publication deviation, not a successful complete pre-outcome public freeze.

{mapping_table}

There are **two alignable sources** for any affirmed abnormality and **one** for moderate-or-greater, for each of twelve findings. **Zero new latent-class fits were run.** We cannot supply defensible sensitivity/specificity estimates from this two-source alignment. The three incompletely documented sources appear only in labeled non-harmonized context; the separate simulation studies their original operational joint pattern distribution, without claiming to harmonize all five definitions.

The any-affirmed target includes mild/trace findings, excludes explicit denials, and retains unmentioned/uncertain as missing. Three Yunus entries have undocumented numeric codes (one 0.40 and two 0.75); all were excluded under the frozen rule. No threshold was chosen from resulting agreement. The moderate-only Yunus coding gives zero change from the old coding on its fixed known samples; it supports no between-source comparison.

## 2. Observed changes on identical before/after samples

{align_table}

Intervals use 2,000 joint study-bootstrap draws; all change estimates have 2,000 valid draws. Pilkwang's verdict coding is unchanged. The principal change is that Yunus's documented mild code 0.25 becomes positive. For effusion, disagreement falls from 39.8% to 0.5%; for synovitis from 31.6% to 1.3%. This is evidence that these sources were answering different operational questions under the original threshold. High post-alignment agreement does not establish correct diagnosis, independent errors, or generalizability beyond the observed known pairs. Contusion retains the largest residual disagreement, about 9%.

![Paired definition alignment](../../figures/v1.4/definition-alignment.png)

Full positive-fraction changes and known/excluded counts are in [paired changes](../../results/v1.4/alignment-paired-changes.csv) and [denominators](../../results/v1.4/alignment-denominators.csv). [Five-source context](../../results/v1.4/nonharmonized-five-source-context.csv) remains explicitly non-harmonized.

## 3. Frozen simulation scenarios

G1 = Steven/Pilkwang/Lixin; G2 = Dread/Yunus. A inherits G1 style and B G2 style, except in the swap control. No participant model is trained or evaluated. The generator preserves each finding's original five-source-complete **joint label-pattern distribution** in expectation. Hypothetical truth and score-error relationships are added as assumptions; the score construction sets each model's full-population true AUC exactly. Parameters are not taken from the rejected latent fits.

The three primary scenarios are A/B true AUC = **0.85/0.85**, **0.86/0.85**, and **0.85/0.86**, with inheritance variance 0.5, equal group weight in the truth mechanism, truth slope 4, and prevalence multiplier 1. Each has 2,000 replicates per finding. Ten prespecified sensitivities (1,000 replicates each) vary inheritance, swap the inherited group, and vary the assumed truth mechanism/prevalence. See [all 13 scenario rows](SIMULATION_SCENARIOS.md) and [exact generator](SAP-v1.4.md#5-empirically-constrained-simulation-generator).

The population is the original complete-label subset (573–3,987 studies per finding), not all 4,349 reports. The prevalence anchor is a scenario proxy, not an estimate of disease prevalence. Clusters were discovered under the original operational coding; the large alignment effect warns that some apparent cluster structure may reflect definitions. The simulation therefore describes risks of using those **original** labels as a reference, not an inevitable property of a fully harmonized dataset.

## 4. Equal underlying quality: which model gets selected?

Both full-population true AUCs are 0.85, so there is no intrinsically worse model. P(A) measures selection preference. Ref ΔAUC is A minus B against the reference; truth ΔAUC is against simulated truth on the same retained cases. Retained n in the table is the observed calibration count; simulated mean n and MCSE are separately reported in [DGM summaries](../../results/v1.4/simulation-dgm.csv).

{equal_table}

Direct majority favors the model that learned the Steven/Pilkwang/Lixin labelling style in **10 of 12 findings**, but favors B for both menisci. Under the primary effusion scenario, A is selected in all 2,000 direct-majority replicates despite equal true AUC; after retaining only group-agreement cases, A is selected 8.4% of the time. These are results conditional on the specified assumptions, not estimates of actual participant bias. A 100% Monte Carlo result is not proof of certainty.

Filtering retains 58.7%–91.8% of the complete-label subset, hence abstains on 8.2%–41.3%. For effusion it retains 2,262 of 3,856 complete cases; for synovitis 354 of 573, only 8.1% of the original 4,349 studies. G2 ties and between-group disagreement are reported separately in [cohort calibration](../../results/v1.4/simulation-cohort.csv).

![Equal true AUC selection](../../figures/v1.4/equal-auc-selection.png)

**Common-sample result:** on retained cases the five-source majority label and group-agreement label are identical. Their AUCs and chosen models are therefore identical. Exhaustive checks over all 32 patterns and per-draw checks found zero violations. Comparing full versus retained results measures changed case mix and sample size; it is not evidence that a different vote improved the reference on the same cases.

## 5. AUC distortion and filtering's selection effect

The following is mean(reference AUC − synthetic-truth AUC) on identical evaluated cases, in the equal-true-AUC scenario. It isolates label-reference distortion from population selection. Exact MCSEs and valid denominators are in [the complete summary](../../results/v1.4/simulation-summary.csv).

{bias_table}

For example, effusion's full-sample reference AUC is biased by about +0.050 for A and −0.099 for B. Filtering reduces this differential but leaves about +0.030/+0.031 label-reference bias. It also changes conditional true AUCs: equal full-population AUC does not require equal performance in the retained subset. The files separately report `selection_effect = truth AUC on evaluated cases − full-population target` and `total_bias = label_bias + selection_effect`; this decomposition was checked per replicate.

![AUC label-reference bias](../../figures/v1.4/auc-label-bias.png)

## 6. When one model has higher true AUC in the simulated full population

Error here means choosing the lower **full-population** true-AUC model. The retained subset can have a different true ordering, so this is distinct from disagreement with the synthetic-truth ranking on the same realized test sample. Both endpoints, ties, failures and paired contrasts are supplied.

{unequal_table}

Filtering is not a universal improvement. For effusion, when B's true AUC is 0.86 versus A's 0.85, error falls from 100.0% to 3.8%; when A is better by the same amount, error rises from 0.0% to 80.5%. Some of this reversal reflects a different conditional true ordering after selection. Those counterexamples are part of the result. The [paired contrasts](../../results/v1.4/simulation-paired-contrasts.csv) give paired MCSEs and valid denominators rather than treating the methods' simulations as independent.

![Unequal AUC misselection](../../figures/v1.4/unequal-auc-misselection.png)

## 7. Prespecified sensitivities and precision

{sens_table}

Ranges summarize twelve heterogeneous findings; they do not pool them as independent clinical replications. Without inherited group errors, P(A) stays near 50% (47.1%–51.7% full; 46.9%–51.5% retained), providing a useful control. Swapping model-group inheritance reverses the broad direction. Changing truth assumptions changes magnitudes and sometimes directions. These controls show why the data alone cannot identify real evaluation bias.

All **156 cells and 192,000 attempted replicates** completed. No reference AUC or synthetic-truth AUC failed; ranking ties are separately counted. Primary probability MCSE is at most about 1.12 percentage points (2,000 draws), sensitivity MCSE at most 1.58 points (1,000 draws). The run used {run['elapsed_minutes']:.2f} minutes; recorded cumulative statistical compute including original runs is about {run['total_cumulative_minutes']:.2f} minutes, below the 120-minute cap. See [run record](../../results/v1.4/simulation-run.json) and [software checks](../../results/v1.4/software-checks.csv).

## 8. Practical evidence table

No row warrants a blanket claim that a label is clinically safe. The usable outputs are an explicit report target, preserved unknowns, quantified agreement/coverage, and a prioritized validation step.

{practical_table}

The [machine-readable practical table](../../results/v1.4/practical-evidence-table.csv) also includes complete-case and retained-cohort coverage. A defensible project narrative can now lead with a substantive result: **documented definition alignment resolves much of the apparent disagreement for two sources, while consensus-reference model selection remains vulnerable to shared label style and selective evaluation.** It should not promise five-source accuracy estimates, proven clinical reliability, or a universally superior voting method.

## 9. Review boundary and reproducibility

In the repaired final tree, all old analysis code, original result tables, figures, the project README, original research report and portfolio homepage remain byte-identical. The earlier malformed SAP publication remains visible in history. Only SAP.md/DECISIONS.md receive extension links; new work lives in v1.4 subdirectories. The source-file hashes pass; every old agreement point estimate and complete binary-pattern count was reproduced. No individual study identifiers, raw labels or replicate draws are released. [RUN.md](RUN.md) documents commands, checks and columns.

The definition table, assumptions and main findings are incorporated in the completed project report.
'''
(here/'REVIEW.md').write_text(review)
print('Review manuscript and practical evidence table generated from completed aggregate outputs.')
