import argparse
import copy
import fcntl
import json
import math
import os
import random
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from .common import LABELS,UID,atomic_json,sha256,stable_hash,now
from .metrics import metrics,prior_baselines
from .model import build_model
from .windows import StudyDataset
from .runtime import require_runtime
from .inputs import to_device,batch_size
from .provenance import source_hash,freeze_sources
from .visual_audit import require_review


def save_checkpoint(path,obj):
    tmp=Path(str(path)+'.tmp');torch.save(obj,tmp);os.replace(tmp,path)


@torch.no_grad()
def evaluate(model,loader,device,amp):
    model.eval();pred=[];truth=[];uids=[]
    for x,y,uid in loader:
        with torch.autocast('cuda',dtype=amp,enabled=device.type=='cuda'):
            logits=model(to_device(x,device))
        pred.append(logits.float().sigmoid().cpu().numpy());truth.append(y.numpy());uids.extend(uid)
    return np.concatenate(truth),np.concatenate(pred),uids


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--fold',type=int,default=0)
    ap.add_argument('--resume',nargs='?',const='auto');ap.add_argument('--smoke',action='store_true');ap.add_argument('--overfit',action='store_true')
    a=ap.parse_args();c=json.loads(Path(a.config).read_text());config_input=copy.deepcopy(c);folds=json.loads(Path(c['fold_file']).read_text())
    cache_manifest=json.loads((Path(c['cache_dir'])/'manifest.json').read_text())
    if not (a.smoke or a.overfit) and json.loads((Path(c['cache_dir'])/'progress.json').read_text()).get('status')!='complete':
        raise ValueError('Production training requires a complete preprocessing cache')
    preprocessing_runtime=require_runtime(cache_manifest.get('preprocessing_runtime'))
    if cache_manifest['preprocessing_hash']!=stable_hash(c['preprocessing']):raise ValueError('Training/cache preprocessing mismatch')
    if not 0<=a.fold<5:raise ValueError('Invalid fold')
    if sha256(c['label_file'])!=folds['labels_sha256']:raise ValueError('Label file changed after fold freeze')
    if sha256(Path(c['metadata_dir'])/'train.csv')!=folds['metadata_sha256']:raise ValueError('Metadata changed after fold freeze')
    fhash=folds.pop('hash')
    if stable_hash(folds)!=fhash:raise ValueError('Fold manifest hash mismatch')
    visual_review_id=require_review(c,fhash)
    from .augmentation import require_augmentation_review
    require_augmentation_review(c)
    train_ids=sorted(u for u,f in folds['folds'].items() if f!=a.fold);val_ids=sorted(u for u,f in folds['folds'].items() if f==a.fold)
    held_out=set(folds['gold_ids'])|set(folds.get('gold_related_ids_excluded',[]))
    if set(train_ids)&set(val_ids) or (set(train_ids)|set(val_ids))&held_out:raise ValueError('Split leakage')
    tg={folds['group_ids'][u] for u in train_ids};vg={folds['group_ids'][u] for u in val_ids}
    if tg&vg:raise ValueError('Patient/duplicate group leakage')
    labels_df=pd.read_csv(c['label_file'],dtype={UID:str}).set_index(UID)
    labels={u:labels_df.loc[u,LABELS].to_numpy(np.float32) for u in train_ids+val_ids}
    if c.get('training_label_file'):
        from .training_labels import override_training
        labels=override_training(labels,train_ids,val_ids,held_out,
                                 c['training_label_file'],c['training_label_sha256'])
    if a.smoke:
        c.update(experiment=c['experiment']+'-smoke',epochs=2,batch_size=1,accumulation=1,workers=0,train_windows=2,eval_windows=2)
        train_ids=train_ids[:8];val_ids=val_ids[:4]
    if a.overfit:
        c.update(experiment=c['experiment']+'-overfit',epochs=20,batch_size=1,accumulation=1,workers=0,train_windows=2,eval_windows=2,head_lr=.003)
        # Wiring overfit diagnostic uses deterministic original images; production retains augmentation.
        c.pop('augmentation',None)
        train_ids=train_ids[:4];val_ids=train_ids.copy()
    c['fold']=a.fold;run=Path(c['run_root'])/c['experiment']/f'fold{a.fold}';run.mkdir(parents=True,exist_ok=True)
    lock=open(run/'train.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    Path('status').mkdir(exist_ok=True)
    gpu_lock=open('status/gpu-job.lock','a');fcntl.flock(gpu_lock,fcntl.LOCK_EX)
    torch.manual_seed(c['seed']);np.random.seed(c['seed']);random.seed(c['seed'])
    if not torch.cuda.is_available():raise RuntimeError('Actual CUDA is required for training')
    device=torch.device('cuda');torch.backends.cudnn.benchmark=True
    amp=torch.bfloat16 if c['mixed_precision']=='bf16' else torch.float16
    if amp==torch.bfloat16 and not torch.cuda.is_bf16_supported():raise RuntimeError('bf16 unsupported')
    ckdir=run/'checkpoints';ckdir.mkdir(exist_ok=True);resume=ckdir/'last.pt' if a.resume=='auto' else (Path(a.resume) if a.resume else None)
    config_hash=stable_hash(c);code_hash=source_hash()
    snapshot=freeze_sources(run/'source',config_input,{'fold':a.fold,'smoke':a.smoke,'overfit':a.overfit,'workspace':str(Path.cwd())})
    receipt={'status':'running','started_at':now(),'config':c,'config_hash':config_hash,'code_hash':code_hash,
             'fold_hash':fhash,'labels_sha256':sha256(c['label_file']),'train_ids':train_ids,'validation_ids':val_ids,
             'gold_ids_excluded':sorted(held_out),'official_gold_ids':folds['gold_ids'],'gpu':torch.cuda.get_device_name(),'torch':torch.__version__,
             'selection':'minimum unweighted held-out weak-label BCE','is_smoke':a.smoke,'is_overfit':a.overfit,
             'preprocessing_runtime':preprocessing_runtime,'cache_manifest_sha256':sha256(Path(c['cache_dir'])/'manifest.json'),
             'visual_review_id':visual_review_id,
             'source_snapshot':str(run/'source'),'source_snapshot_manifest_sha256':sha256(run/'source/manifest.json')}
    receipt['training_labels_sha256']=c.get('training_label_sha256',receipt['labels_sha256'])
    receipt['training_labels_file']=c.get('training_label_file',c['label_file'])
    receipt['validation_labels_file']=c['label_file']
    if c.get('initialization_file') and not(resume and resume.exists()):
        if sha256(c['initialization_file'])!=c['initialization_sha256']:raise ValueError('Initialization SHA256 mismatch')
    receipt['initialization_sha256']=c.get('initialization_sha256')
    receipt['weak_validation_baselines']=prior_baselines(
        np.stack([labels[u] for u in train_ids]),np.stack([labels[u] for u in val_ids]))
    # Pretrain only when a valid resume checkpoint does not exist; it will fully overwrite weights.
    model=build_model(c,pretrained=not(resume and resume.exists()),gradient_checkpointing=c['gradient_checkpointing']).to(device)
    bp=[p for n,p in model.named_parameters() if n.startswith('backbone.')]
    hp=[p for n,p in model.named_parameters() if not n.startswith('backbone.')]
    opt=torch.optim.AdamW([{'params':bp,'lr':c['backbone_lr']},{'params':hp,'lr':c['head_lr']}],weight_decay=c['weight_decay'])
    steps=math.ceil(math.ceil(len(train_ids)/c['batch_size'])/c['accumulation'])
    sched=torch.optim.lr_scheduler.OneCycleLR(opt,max_lr=[c['backbone_lr'],c['head_lr']],total_steps=steps*c['epochs'],pct_start=.15)
    mean=np.clip(np.nanmean(np.stack([labels[u] for u in train_ids]),axis=0),.03,.7)
    pw=torch.tensor(np.clip((1-mean)/mean,1,10),device=device,dtype=torch.float32)
    if c.get('positive_weighting','train_only')=='none':pw=torch.ones_like(pw)
    elif c.get('positive_weighting','train_only')!='train_only':raise ValueError('Unknown positive weighting')
    receipt['positive_weights_train_only']=dict(zip(LABELS,pw.cpu().tolist()))
    scaler=torch.amp.GradScaler('cuda',enabled=amp==torch.float16)
    start_epoch=0;best=float('inf');history=[];elapsed_before=0.
    if resume and resume.exists():
        state=torch.load(resume,map_location='cpu',weights_only=False)
        if state['config_hash']!=config_hash or state['fold_hash']!=fhash or state['code_hash']!=code_hash:raise ValueError('Resume provenance mismatch')
        if state.get('cache_manifest_sha256')!=receipt['cache_manifest_sha256']:raise ValueError('Resume cache provenance mismatch')
        model.load_state_dict(state['model']);opt.load_state_dict(state['optimizer']);sched.load_state_dict(state['scheduler']);scaler.load_state_dict(state['scaler'])
        start_epoch=state['epoch']+1;best=state['best_bce'];history=state['history'];elapsed_before=state.get('gpu_seconds',0.)
        random.setstate(state['random_state']);np.random.set_state(state['numpy_state']);torch.set_rng_state(state['torch_rng'])
        torch.cuda.set_rng_state_all(state['cuda_rng'])
    atomic_json(run/'config.json',c);atomic_json(run/'receipt.json',receipt)
    started=time.monotonic()
    vl=DataLoader(StudyDataset(val_ids,labels,c,False),batch_size=c['eval_batch_size'],num_workers=c['workers'],shuffle=False,pin_memory=True)
    for epoch in range(start_epoch,c['epochs']):
        # Explicit generator restores the same epoch order after an interrupted epoch.
        gen=torch.Generator().manual_seed(c['seed']+epoch)
        tl=DataLoader(StudyDataset(train_ids,labels,c,True,epoch),batch_size=c['batch_size'],num_workers=c['workers'],shuffle=True,generator=gen,pin_memory=True)
        model.train();opt.zero_grad(set_to_none=True);loss_sum=0.;n=0
        for batch,(x,y,_) in enumerate(tl):
            x=to_device(x,device);y=y.to(device,non_blocking=True);valid=torch.isfinite(y)
            with torch.autocast('cuda',dtype=amp):logits=model(x)
            raw=F.binary_cross_entropy_with_logits(logits.float(),torch.nan_to_num(y),pos_weight=pw,reduction='none')
            loss=raw[valid].mean()
            if not torch.isfinite(loss):raise FloatingPointError('Non-finite training loss')
            window_start=(batch//c['accumulation'])*c['accumulation']
            # Weight by sample count, including a shorter final batch, to preserve effective batch semantics.
            window_samples=min(c['batch_size']*c['accumulation'],len(train_ids)-window_start*c['batch_size'])
            scaler.scale(loss*batch_size(x)/window_samples).backward()
            loss_sum+=loss.item()*batch_size(x);n+=batch_size(x)
            if (batch+1)%c['accumulation']==0 or batch+1==len(tl):
                scaler.unscale_(opt);torch.nn.utils.clip_grad_norm_(model.parameters(),5.)
                scaler.step(opt);scaler.update();sched.step();opt.zero_grad(set_to_none=True)
            if batch%100==0:print(json.dumps({'epoch':epoch,'batch':batch,'train_bce_weighted':loss.item(),'seconds':time.monotonic()-started}),flush=True)
        y,p,ids=evaluate(model,vl,device,amp);m=metrics(y,p,soft=True)
        improved=m['bce']<best
        if improved:best=m['bce']
        record={'epoch':epoch,'train_bce_weighted':loss_sum/n,'validation':m,'gpu_seconds':elapsed_before+time.monotonic()-started,
                'peak_gpu_bytes':torch.cuda.max_memory_allocated(),'selected':improved};history.append(record)
        state={'model':{k:v.detach().cpu() for k,v in model.state_dict().items()},'optimizer':opt.state_dict(),'scheduler':sched.state_dict(),
               'scaler':scaler.state_dict(),'epoch':epoch,'best_bce':best,'history':history,'config':c,'config_hash':config_hash,'code_hash':code_hash,
               'fold':a.fold,'fold_hash':fhash,'train_ids':train_ids,'validation_ids':val_ids,'gold_ids_excluded':sorted(held_out),'official_gold_ids':folds['gold_ids'],
               'labels_sha256':receipt['labels_sha256'],'preprocessing':c['preprocessing'],'lab':LABELS,'arch':c['arch'],'res':c['resolution'],
               'preprocessing_runtime':preprocessing_runtime,'cache_manifest_sha256':receipt['cache_manifest_sha256'],
               'visual_review_id':visual_review_id,
               'source_snapshot_manifest_sha256':receipt['source_snapshot_manifest_sha256'],
               'random_state':random.getstate(),'numpy_state':np.random.get_state(),'torch_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all(),
               'gpu_seconds':record['gpu_seconds']}
        save_checkpoint(ckdir/'last.pt',state)
        if improved:
            # Deploy only a single model, not an epoch ensemble.
            deploy={k:v for k,v in state.items() if k not in ['optimizer','scheduler','scaler','random_state','numpy_state','torch_rng','cuda_rng']}
            save_checkpoint(ckdir/'best.pt',deploy)
            pd.DataFrame(p,columns=LABELS).assign(**{UID:ids})[[UID]+LABELS].to_csv(run/'validation_predictions.csv',index=False)
        atomic_json(run/'history.json',history)
        print(json.dumps(record),flush=True)
    receipt.update(status='complete',completed_at=now(),best_bce=best,checkpoint_sha256=sha256(ckdir/'best.pt'),gpu_seconds=elapsed_before+time.monotonic()-started,
                   peak_gpu_bytes=torch.cuda.max_memory_allocated())
    if a.overfit:
        receipt['overfit_loss_decreased']=history[-1]['train_bce_weighted']<history[0]['train_bce_weighted']
        if not receipt['overfit_loss_decreased']:raise RuntimeError('Small-sample overfit check failed')
    atomic_json(run/'receipt.json',receipt)
    print(json.dumps({'status':'complete','checkpoint':str(ckdir/'best.pt'),'best_bce':best}),flush=True)

if __name__=='__main__':main()
