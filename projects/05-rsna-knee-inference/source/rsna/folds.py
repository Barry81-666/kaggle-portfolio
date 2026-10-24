import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from .common import LABELS, UID, atomic_json, sha256, stable_hash


def make_folds(metadata, labels, output, seed=42):
    tr = pd.read_csv(metadata, dtype={UID:str})
    lab = pd.read_csv(labels, dtype={UID:str})
    if tr[UID].duplicated().any() or lab[UID].duplicated().any(): raise ValueError('Duplicate study identifiers')
    if not set(LABELS) <= set(lab): raise ValueError('Missing label columns')
    y = lab[LABELS].to_numpy(float)
    if not np.isfinite(y).all() or ((y<0)|(y>1)).any(): raise ValueError('Invalid weak labels')
    gold = sorted(tr.loc[tr[LABELS].notna().any(axis=1),UID].tolist())
    silver = tr[~tr[UID].isin(gold)].merge(lab[[UID]+LABELS], on=UID, how='inner', suffixes=('_official',''))
    if len(silver) != len(tr)-len(gold): raise ValueError('Labels do not cover all non-gold studies')
    silver = silver.sort_values(UID).reset_index(drop=True)
    grouping = next((c for c in ['PatientID','PatientId','patient_id'] if c in silver and silver[c].notna().all()),None)
    # A verified duplicate-map may be supplied before the initial fold freeze.
    duplicate_map = Path(metadata).parent/'duplicate_groups.json'
    duplicate_groups = json.loads(duplicate_map.read_text()) if duplicate_map.exists() else {}
    group_lookup={u:duplicate_groups.get(u,u) for u in tr[UID]}
    if grouping:
        # Patient metadata adds associations; it cannot erase an audited
        # duplicate/header association, including an association with Gold.
        parent={g:g for g in group_lookup.values()}
        def find(g):
            while parent[g]!=g:parent[g]=parent[parent[g]];g=parent[g]
            return g
        patient_first={}
        for u,pid in zip(tr[UID],tr[grouping].astype(str)):
            g=group_lookup[u]
            if pid in patient_first:
                left,right=find(g),find(patient_first[pid])
                parent[max(left,right)]=min(left,right)
            else:patient_first[pid]=g
        group_lookup={u:find(g) for u,g in group_lookup.items()}
    gold_groups={group_lookup[u] for u in gold}
    related=sorted(u for u in silver[UID] if group_lookup[u] in gold_groups)
    silver=silver[~silver[UID].isin(related)].reset_index(drop=True)
    groups = [str(group_lookup[u]) for u in silver[UID]]
    group_to_rows = {}
    for i,g in enumerate(groups): group_to_rows.setdefault(g,[]).append(i)
    group_names = sorted(group_to_rows)
    gy = np.array([(silver.iloc[group_to_rows[g]][LABELS].to_numpy(float)>=.5).max(axis=0) for g in group_names])
    splitter = MultilabelStratifiedKFold(n_splits=5,shuffle=True,random_state=seed)
    assignments = {}
    for f,(_,vi) in enumerate(splitter.split(np.zeros(len(group_names)),gy)):
        for gidx in vi:
            for row in group_to_rows[group_names[gidx]]: assignments[silver.loc[row,UID]] = f
    obj = {'seed':seed,'n_folds':5,'gold_ids':gold,'gold_related_ids_excluded':related,'folds':assignments,'grouping':grouping or 'study/verified duplicate group',
           'group_ids':dict(zip(silver[UID],groups)), 'metadata_sha256':sha256(metadata),'labels_sha256':sha256(labels),
           'patient_identity_available':bool(grouping),'duplicate_audit':'verified map' if duplicate_groups else 'pending DICOM audit',
           'fold_sizes':{str(i):sum(f==i for f in assignments.values()) for i in range(5)}}
    obj['hash'] = stable_hash(obj)
    if Path(output).exists():
        old=json.loads(Path(output).read_text())
        if old!=obj: raise RuntimeError('Refusing to replace frozen folds: use a new experiment lineage')
    else: atomic_json(output,obj)
    return obj


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);a=p.parse_args();c=json.loads(Path(a.config).read_text())
    f=make_folds(Path(c['metadata_dir'])/'train.csv',c['label_file'],c['fold_file'],c['seed'])
    study_file=Path('artifacts/study_metadata.json')
    if study_file.exists():
        from .fold_profile import write_profile
        write_profile(f,Path(c['metadata_dir'])/'train.csv',c['label_file'],
                      json.loads(study_file.read_text()),Path(c['fold_file']).with_name('fold_profile.json'))
    from .visual_audit import create_audit,wait_for_review
    audit=create_audit(c,f)
    wait_for_review(audit)
    print(json.dumps({'gold':len(f['gold_ids']),'sizes':f['fold_sizes'],'hash':f['hash'],'grouping':f['grouping']}))

if __name__=='__main__':main()
