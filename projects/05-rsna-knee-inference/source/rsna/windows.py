import random
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset


def centers(mask,count,train=False,rng=None):
    # Valid neighbors AND same slot. Unlike the public sampler, cannot cross series boundaries.
    valid=np.asarray(mask)>0
    cs=np.where(valid[:-2]&valid[1:-1]&valid[2:])[0]+1
    if not len(cs): raise ValueError('No valid adjacent-slice triplets')
    if train:
        rng=rng or np.random.default_rng()
        return rng.choice(cs,count,replace=len(cs)<count)
    return cs[np.linspace(0,len(cs)-1,count).round().astype(int)]


def slot_mask(mask,slots):
    # Mark slot endpoints unusable as centers, but keep adjacent slices available.
    allowed=np.zeros(len(mask),bool);start=0
    valid=np.asarray(mask)>0
    for _,_,n in slots:
        for c in range(start+1,start+n-1):allowed[c]=bool(valid[c-1:c+2].all())
        start+=n
    return np.where(allowed)[0]


def windows(vol,mask,config,count,train=False,rng=None,mirror_codes=None):
    cs=slot_mask(mask,config['preprocessing']['slots'])
    if not len(cs):raise ValueError('No valid within-series triplets')
    if train:
        rng=rng or np.random.default_rng();cs=rng.choice(cs,count,replace=len(cs)<count)
    else:cs=cs[np.linspace(0,len(cs)-1,count).round().astype(int)]
    a=np.stack([vol[c-1:c+2] for c in cs]).astype(np.float32)/255
    x=torch.from_numpy(a)
    res=config['resolution']
    mode=config.get('input_mode','resize')
    if mode=='crop':
        h,w=x.shape[-2:]
        if res>min(h,w):raise ValueError('Crop exceeds native cache resolution')
        oy=int(rng.integers(0,h-res+1)) if train else (h-res)//2
        ox=int(rng.integers(0,w-res+1)) if train else (w-res)//2
        x=x[...,oy:oy+res,ox:ox+res]
    elif mode=='resize':
        if x.shape[-2:]!=(res,res):x=F.interpolate(x,size=(res,res),mode='bilinear',align_corners=False)
    else:raise ValueError('Unknown input mode: '+mode)
    if train and config.get('augmentation'):
        if mirror_codes is None:raise ValueError('Augmentation needs audited geometry')
        from .augmentation import augment_windows
        x=augment_windows(x,cs,config,rng,mirror_codes)
    elif train:x=(x*(.9+.2*float(rng.random()))).clamp(0,1)
    if config['norm']=='imagenet':
        mean=torch.tensor([.485,.456,.406]).view(1,3,1,1);std=torch.tensor([.229,.224,.225]).view(1,3,1,1)
        x=(x-mean)/std
    return x


class StudyDataset(Dataset):
    def __init__(self,ids,labels,config,train=False,epoch=0):self.ids=ids;self.labels=labels;self.config=config;self.train=train;self.epoch=epoch
    def __len__(self):return len(self.ids)
    def __getitem__(self,i):
        uid=self.ids[i];p=Path(self.config['cache_dir'])/(uid+'.npz')
        with np.load(p,allow_pickle=False) as d:pack={key:d[key] for key in d.files}
        if self.config.get('augmentation'):
            from .augmentation import cached_codes
            pack['mirror_codes']=cached_codes(self.config,uid)
        # Per-study/per-epoch randomness makes sampler independent of worker scheduling.
        import hashlib
        seed=int.from_bytes(hashlib.sha256(f"{self.config['seed']}:{self.epoch}:{uid}".encode()).digest()[:8],'little')
        rng=np.random.default_rng(seed)
        k=self.config['train_windows'] if self.train else self.config['eval_windows']
        from .inputs import sample_input
        return sample_input(pack,self.config,k,self.train,rng),torch.tensor(self.labels[uid],dtype=torch.float32),uid
