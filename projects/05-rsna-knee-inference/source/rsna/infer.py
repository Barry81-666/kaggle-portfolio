import argparse
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from .common import LABELS,UID,atomic_json,sha256,now
from .dicom import build_study
from .windows import windows
from .runtime import require_runtime
from .inputs import build_input,sample_input,add_batch,to_device


def validate_submission(frame,test_ids):
    if list(frame.columns)!=[UID]+LABELS:raise ValueError('Wrong submission columns')
    if frame[UID].astype(str).tolist()!=list(test_ids) or frame[UID].duplicated().any():raise ValueError('Submission ID mismatch')
    p=frame[LABELS].to_numpy(float)
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():raise ValueError('Invalid submission values')


def main():
    from .model import build_model
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',required=True);ap.add_argument('--data',required=True)
    ap.add_argument('--output',default='submission.csv');ap.add_argument('--windows',type=int);ap.add_argument('--tta',choices=['none','anatomical_lr'])
    a=ap.parse_args();started=time.monotonic();ck=torch.load(a.checkpoint,map_location='cpu',weights_only=False)
    runtime=require_runtime(ck.get('preprocessing_runtime'))
    if ck['fold']!=0 or ck['config'].get('experiment','').endswith(('-smoke','-overfit')):raise ValueError('Only real fold 0 may be submitted')
    if set(ck['train_ids'])&set(ck['validation_ids']) or set(ck['train_ids'])&set(ck['gold_ids_excluded']):raise ValueError('Training provenance leakage')
    c=ck['config'];k=a.windows or c['inference']['windows']
    a.tta=a.tta or c['inference'].get('tta','none')
    if a.tta=='anatomical_lr' and c['norm']!='none':raise ValueError('This mirror recipe was frozen for norm=none')
    dev=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model=build_model(c).to(dev);model.load_state_dict(ck['model'],strict=True);model.eval()
    root=Path(a.data);test=pd.read_csv(root/'test.csv',dtype={UID:str});ids=test[UID].tolist()
    ser=pd.read_csv(root/'test_series.csv',dtype={UID:str,'SeriesInstanceUID':str});sr={u:d.to_dict('records') for u,d in ser.groupby(UID,sort=False)}
    image_root=next((root/p for p in ['test_images','test_series'] if (root/p).is_dir()),None)
    if image_root is None:raise FileNotFoundError('No test DICOM directory')
    pred=[];logs=[]
    with torch.inference_mode():
        for uid in ids:
            if time.monotonic()-started>c['inference']['max_hours']*3600:raise RuntimeError('Inference runtime budget exceeded')
            t=time.monotonic();pack,d=build_input(uid,sr.get(uid,[]),image_root,c);x=to_device(add_batch(sample_input(pack,c,k)),dev)
            if a.tta=='anatomical_lr':
                from .augmentation import predict_pair,window_slots
                cs=np.asarray(pack['mask'])
                from .windows import slot_mask
                centres=slot_mask(cs,c['preprocessing']['slots']);centres=centres[np.linspace(0,len(centres)-1,k).round().astype(int)]
                p=predict_pair(model,x,window_slots(centres,c['preprocessing']['slots']),pack['mirror_codes'],dev,torch.float16)[0].cpu().numpy()
            else:
                with torch.autocast('cuda',dtype=torch.float16,enabled=dev.type=='cuda'):logits=model(x)
                if not torch.isfinite(logits).all():
                    with torch.autocast('cuda',enabled=False):logits=model(x)
                p=logits.float().sigmoid()[0].cpu().numpy()
            if not np.isfinite(p).all():raise FloatingPointError('Nonfinite predictions; no silent fallback')
            pred.append(p);logs.append({'uid':uid,'seconds':time.monotonic()-t,'decode_failures':len(d['decode_failures'])})
    frame=pd.DataFrame(pred,columns=LABELS);frame.insert(0,UID,ids);validate_submission(frame,ids);frame.to_csv(a.output,index=False)
    atomic_json(Path(a.output).with_suffix('.receipt.json'),{'status':'complete','checkpoint_sha256':sha256(a.checkpoint),'models':1,'fold':0,
         'windows':k,'tta':a.tta,'rows':len(ids),'seconds':time.monotonic()-started,'studies':logs,'completed_at':now(),'config_hash':ck['config_hash'],
         'preprocessing_runtime':runtime})

if __name__=='__main__':main()
