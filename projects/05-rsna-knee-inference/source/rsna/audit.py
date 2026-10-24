import argparse
import collections
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .common import UID,atomic_json,sha256


def patient_candidate_groups(identities):
    """Conservative global matching, including the same ID on another scanner.

    Header uniqueness is a heuristic; it cannot certify longitudinal identity
    after dataset de-identification. Device-scoped IDs could split one person.
    """
    candidates={}
    for uid,identity in identities.items():
        values=identity.get('PatientID_candidates',[identity.get('PatientID','')])
        for pid in {v.strip() for v in values}:
            if pid and pid.lower() not in ['anonymous','anon','removed','none','unknown','0','1','patient']:
                candidates.setdefault(pid,[]).append(uid)
    reliable=len(candidates)>=.5*len(identities) and max((len(v) for v in candidates.values()),default=0)<=20
    return candidates,reliable


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);a=ap.parse_args();c=json.loads(Path(a.config).read_text())
    cache=Path(c['cache_dir']);uids=pd.read_csv(Path(c['metadata_dir'])/'train.csv',dtype={UID:str})[UID].tolist()
    parent={u:u for u in uids}
    def find(u):
        while parent[u]!=u:parent[u]=parent[parent[u]];u=parent[u]
        return u
    def union(u,v):parent[find(u)]=find(v)
    seen={};identities={};devices=collections.Counter();missing=collections.Counter();order=collections.Counter();fail=[];study_meta={}
    for u in uids:
        with np.load(cache/(u+'.npz')) as f:
            # Equal canonical pixel volumes are conservative duplicate groups.
            h=hashlib.sha256(f['volume'].tobytes()+f['mask'].tobytes()).hexdigest()
        if h in seen:union(u,seen[h])
        else:seen[h]=u
        d=json.loads((cache/(u+'.json')).read_text());identity=d.get('identity',{})
        device='|'.join(identity.get(k,'unknown') for k in ['Manufacturer','ManufacturerModelName'])
        devices[device]+=1
        identities[u]=identity
        for s in d['series']:
            if s.get('missing'):missing[s['plane']]+=1
            else:
                for k in s['ordering_methods']:order[k]+=1
        if d.get('decode_failures'):fail.append({'uid':u,'count':len(d['decode_failures'])})
        study_meta[u]={'device_group':device,'series_present':sum(not s.get('missing',False) for s in d['series'])}
    # Avoid grouping every patient by an institution's placeholder identifier.
    if any(i.get('header_audit',{}).get('scope')!='all acquired DICOM series in the study'
           or i['header_audit'].get('files',0)<=0 for i in identities.values()):
        raise ValueError('Full-study identity audit required before freezing groups')
    patients,reliable=patient_candidate_groups(identities)
    if reliable:
        for group in patients.values():
            for u in group[1:]:union(group[0],u)
    group_map={u:hashlib.sha256(find(u).encode()).hexdigest()[:24] for u in uids}
    atomic_json(Path(c['metadata_dir'])/'duplicate_groups.json',group_map)
    atomic_json('artifacts/data_audit.json',{'studies':len(uids),'distinct_canonical_volumes':len(seen),'patient_grouping_used':reliable,
                'full_study_identity_audits':sum(i.get('header_audit',{}).get('scope')=='all acquired DICOM series in the study' for i in identities.values()),
                'identity_headers_read':sum(i.get('header_audit',{}).get('files',0) for i in identities.values()),
                'identity_headers_without_patient_id':sum(i.get('header_audit',{}).get('headers_without_patient_id',0) for i in identities.values()),
                'patient_identity_limitation':'PatientID uniqueness/consistency is a heuristic, not verified longitudinal identity after de-identification; global matching across devices is conservative' if reliable else 'No reliable header identity pattern; study and exact-volume grouping only',
                'patient_grouping_scope':'global PatientID across scanner/device groups' if reliable else 'unavailable',
                'distinct_candidate_patient_ids':len(patients),
                'studies_with_conflicting_patient_headers':sum(bool(i.get('PatientID_conflict')) for i in identities.values()),
                'candidate_cross_device_groups':sum(len({study_meta[u]['device_group'] for u in group})>1 for group in patients.values()),
                'groups':len(set(group_map.values())),'devices':dict(devices),'missing_slots':dict(missing),'ordering':dict(order),'decode_failures':fail})
    atomic_json('artifacts/study_metadata.json',study_meta)
    # Native/cache figures are generated after group/fold isolation in folds.main.
    print(json.dumps({'studies':len(uids),'patient_grouping_used':reliable,'groups':len(set(group_map.values()))}))

if __name__=='__main__':main()
