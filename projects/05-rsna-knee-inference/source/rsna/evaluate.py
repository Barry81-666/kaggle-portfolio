import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from .common import LABELS,UID,atomic_json,sha256,now
from .metrics import metrics
from .model import build_model
from .train import evaluate
from .windows import StudyDataset
from .runtime import require_runtime


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',required=True);ap.add_argument('--split',choices=['silver','gold'],default='silver')
    ap.add_argument('--recipe-freeze');ap.add_argument('--bootstrap',type=int,default=2000);ap.add_argument('--output',required=True);a=ap.parse_args()
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=False);c=ck['config']
    require_runtime(ck.get('preprocessing_runtime'))
    cache_manifest=json.loads((Path(c['cache_dir'])/'manifest.json').read_text())
    require_runtime(cache_manifest.get('preprocessing_runtime'),ck['preprocessing_runtime'])
    if sha256(Path(c['cache_dir'])/'manifest.json')!=ck['cache_manifest_sha256']:raise ValueError('Evaluation cache provenance mismatch')
    if a.split=='gold':
        if not a.recipe_freeze:raise ValueError('Gold evaluation requires a documented recipe freeze')
        freeze=json.loads(Path(a.recipe_freeze).read_text())
        if freeze['checkpoint_sha256']!=sha256(a.checkpoint):raise ValueError('Recipe freeze does not identify this checkpoint')
        ids=ck.get('official_gold_ids',ck['gold_ids_excluded']);df=pd.read_csv(Path(c['metadata_dir'])/'train.csv',dtype={UID:str}).set_index(UID)
        if not np.isfinite(df.loc[ids,LABELS].to_numpy(float)).all():raise ValueError('Gold evaluation requires complete official targets')
    else:ids=ck['validation_ids'];df=pd.read_csv(c['label_file'],dtype={UID:str}).set_index(UID)
    if set(ids)&set(ck['train_ids']):raise ValueError('Evaluating training samples is prohibited')
    labels={u:df.loc[u,LABELS].to_numpy(np.float32) for u in ids}
    dev=torch.device('cuda' if torch.cuda.is_available() else 'cpu');model=build_model(c).to(dev)
    model.load_state_dict(ck['model']);loader=DataLoader(StudyDataset(ids,labels,c),batch_size=1,num_workers=c['workers'])
    y,p,u=evaluate(model,loader,dev,torch.float16);result=metrics(y,p,soft=a.split=='silver')
    if a.split=='gold':
        rng=np.random.default_rng(42);scores=[]
        for _ in range(a.bootstrap):
            idx=rng.choice(len(y),len(y),replace=True);m=metrics(y[idx],p[idx],False)
            if m['macro_auc'] is not None:scores.append(m['macro_auc'])
        result['bootstrap_95_ci']=np.quantile(scores,[.025,.975]).tolist() if scores else None
        result['bootstrap_full_class_samples']=len(scores)
    result.update(checkpoint_sha256=sha256(a.checkpoint),split=a.split,evaluated_at=now())
    atomic_json(a.output,result);pd.DataFrame(p,columns=LABELS).assign(**{UID:u})[[UID]+LABELS].to_csv(Path(a.output).with_suffix('.csv'),index=False)

if __name__=='__main__':main()
