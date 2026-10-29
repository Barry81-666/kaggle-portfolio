"""Check aggregate outputs, frozen files, baseline preservation and release privacy."""
from pathlib import Path
import argparse,csv,hashlib,json,math,re,datetime

ap=argparse.ArgumentParser()
ap.add_argument('--baseline',required=True,help='Read-only checkout of the pre-extension main commit')
ap.add_argument('--raw',required=True,help='External directory containing the five approved public files')
args=ap.parse_args()
here=Path(__file__).resolve().parent;repo=here.parents[3];baseline=Path(args.baseline)
project=here.parent.parent;results=project/'results/v1.4'
def readcsv(p):
    with p.open() as f:return list(csv.DictReader(f))
def n(r,k):return float(r[k]) if r[k] else float('nan')
manifest=json.loads((here/'freeze-manifest.json').read_text())
for path,sha in manifest['files'].items():
    assert hashlib.sha256((repo/path).read_bytes()).hexdigest()==sha,path
expected_changed={'projects/11-knee-report-label-accuracy/analysis/SAP.md','projects/11-knee-report-label-accuracy/analysis/DECISIONS.md'}
changed=[]
for old in baseline.rglob('*'):
    if old.is_file():
        rel=old.relative_to(baseline);new=repo/rel
        assert new.is_file(),str(rel)
        if new.read_bytes()!=old.read_bytes():changed.append(str(rel))
assert set(changed)==expected_changed,changed
new_files=[p for p in repo.rglob('*') if p.is_file() and not (baseline/p.relative_to(repo)).exists()]
uids=set()
for r in readcsv(project/'results/source_files.csv'):
    p=Path(args.raw)/r['dataset'].replace('/','__')/r['filename']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
    uids.update(row['StudyInstanceUID'] for row in readcsv(p))
leaks=[];links=[]
for p in new_files:
    if p.suffix=='.png':continue
    text=p.read_text()
    for uid in uids:
        if uid in text:leaks.append(str(p.relative_to(repo)));break
    if p.suffix=='.md':
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
            target=link.split('#')[0]
            if target and not re.match(r'^[a-z]+:',target):
                assert (p.parent/target).exists(),(str(p),target)
                links.append(link)
assert not leaks,leaks
s=readcsv(results/'simulation-summary.csv');d=readcsv(results/'simulation-dgm.csv')
assert len(s)==312 and len(d)==156
assert sum(int(r['attempted']) for r in d)==192000
maxz=0
for r in s:
    R=int(r['attempted'])
    assert int(r['reference_failed'])==0 and int(r['truth_failed'])==0
    assert abs(sum(n(r,k+'_all_attempted') for k in ['p_select_A','p_select_B','p_tie'])-1)<1e-10
    assert abs(n(r,'preference_estimate')-(n(r,'p_select_A_estimate')-n(r,'p_select_B_estimate')))<1e-10
    for m in ['A','B']:
        assert abs(n(r,f'total_bias_{m}_estimate')-n(r,f'label_bias_{m}_estimate')-n(r,f'selection_effect_{m}_estimate'))<1e-10
        if r['method']=='full_direct':
            z=abs(n(r,f'truth_auc_{m}_estimate')-n(r,f'target_auc_{m}'))/n(r,f'truth_auc_{m}_mcse')
            maxz=max(maxz,z)
    if r['scenario']=='equal_true_auc':assert not r['misselection_global_estimate']
    assert n(r,'p_tie_valid')==R
assert maxz<5,maxz
for r in d:
    assert abs(n(r,'retained_n_estimate')+n(r,'g2_tie_n_estimate')+n(r,'group_disagree_n_estimate')-n(r,'n'))<1e-8
for r in readcsv(results/'simulation-paired-contrasts.csv'):
    for k in ['common_subset_auc_difference_A','common_subset_auc_difference_B','common_subset_selection_difference']:assert n(r,k)==0
for r in readcsv(results/'alignment-eligibility.csv'):
    assert r['lcm_permitted']=='FALSE' and int(r['alignable_sources'])<3
for r in readcsv(results/'alignment-paired-changes.csv'):
    assert abs(n(r,'after')-n(r,'before')-n(r,'change'))<1e-10
    assert n(r,'bootstrap_valid')==2000
record={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'freeze_commit':manifest['freeze_commit'],'frozen_files_verified':len(manifest['files']),
 'baseline_files_checked':sum(p.is_file() for p in baseline.rglob('*')),'changed_existing_files':changed,
 'legacy_results_code_pages_preserved':True,'new_text_files_scanned':sum(p.suffix!='.png' for p in new_files),
 'individual_identifier_matches':0,'local_markdown_links_verified':len(links),'source_hashes_verified':5,
 'simulation_cells':156,'attempted_replicates':192000,'reference_auc_failures':0,'truth_auc_failures':0,
 'maximum_full_truth_auc_target_deviation_in_mcse':maxz,'all_summary_identities_pass':True,
 'new_lcm_fits':0,'status':'passed'}
(results/'validation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
