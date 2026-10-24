"""Series-shared MRI augmentation and geometry-audited L/R reflection.

Affine/gamma/gain adapted from goodpjw2008's published reader dependency;
probability TTA from nartaa's .949 author-reported recipe. Never swaps targets.
"""
import functools
import json
import math
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from .common import sha256


def lr_code(iop, minimum=.9):
    if iop is None:
        return 0
    v = np.asarray(iop, dtype=float)
    if v.shape != (6,) or not np.isfinite(v).all():
        return 0
    w, h = v[:3], v[3:]
    if abs(np.linalg.norm(w)-1)>.01 or abs(np.linalg.norm(h)-1)>.01 or abs(w@h)>.01:
        return 0
    scores = np.abs([np.cross(w,h)[0], w[0], h[0]])
    return int(np.argmax(scores))+1 if scores.max() >= minimum else 0


def series_code(headers, minimum=.9):
    orientations = [getattr(h, 'ImageOrientationPatient', None) for h in headers]
    codes = [lr_code(v, minimum) for v in orientations]
    if not codes or 0 in codes or len(set(codes)) != 1:
        return 0
    first = np.asarray(orientations[0], float)
    if any(np.max(np.abs(np.asarray(v,float)-first)) > .01 for v in orientations):
        return 0
    return codes[0]


def window_slots(centres, slots):
    return np.searchsorted(np.cumsum([s[2] for s in slots]), centres, side='right')


def mirror_windows(x, slot_ids, codes):
    if len(slot_ids)!=len(x) or any(int(c) not in (0,1,2,3) for c in codes):
        raise ValueError('Invalid L/R window metadata')
    out=x.clone()
    for s, code in enumerate(codes):
        sel=torch.as_tensor(np.asarray(slot_ids)==s, device=x.device)
        if int(code) and sel.any():
            out[sel]=x[sel].flip({1:1,2:-1,3:-2}[int(code)])
    return out


def augment_windows(x, centres, config, rng, codes):
    a=config['augmentation'];sid=window_slots(centres,config['preprocessing']['slots'])
    if rng.random()<a['lr_mirror_probability']:
        x=mirror_windows(x,sid,codes)
    out=x.clone()
    for s in np.unique(sid):
        selected=torch.as_tensor(sid==s,device=x.device)
        angle=math.radians(float(rng.uniform(-a['rotation_degrees'],a['rotation_degrees'])))
        scale=float(rng.uniform(1-a['scale_fraction'],1+a['scale_fraction']))
        tx,ty=rng.uniform(-a['translation_fraction'],a['translation_fraction'],2)
        co,si=math.cos(angle)*scale,math.sin(angle)*scale
        theta=x.new_tensor([[co,-si,tx],[si,co,ty]])[None].expand(int(selected.sum()),-1,-1)
        z=x[selected];grid=F.affine_grid(theta,z.shape,align_corners=False)
        z=F.grid_sample(z,grid,mode='bilinear',padding_mode='zeros',align_corners=False)
        gamma=math.exp(float(rng.uniform(-a['gamma_log_range'],a['gamma_log_range'])))
        gain=float(rng.uniform(1-a['gain_fraction'],1+a['gain_fraction']))
        out[selected]=(z.clamp(0,1).pow(gamma)*gain).clamp(0,1)
    return out


@functools.lru_cache(maxsize=2)
def orientation_metadata(path, expected_hash):
    if sha256(path)!=expected_hash:
        raise ValueError('Augmentation geometry metadata changed')
    return json.loads(Path(path).read_text())['studies']


def cached_codes(config, uid):
    entry=orientation_metadata(config['augmentation_metadata_file'],config['augmentation_metadata_sha256']).get(uid)
    if entry is None:
        raise ValueError('Missing predeclared training/validation orientation: '+uid)
    return np.asarray(entry['codes'],dtype=np.int8)


def require_augmentation_review(config):
    if not config.get('augmentation'):
        return
    r=json.loads(Path(config['augmentation_review_file']).read_text())
    if r.get('status')!='passed' or r.get('orientation_sha256')!=sha256(config['augmentation_metadata_file']):
        raise ValueError('Augmentation figures/geometry require actual review')
    for p,digest in r['figures'].items():
        if sha256(p)!=digest:
            raise ValueError('Reviewed augmentation figure changed')


def predict_pair(model, x, slot_ids, codes, device, amp):
    if any(m.training for m in model.modules()):
        raise ValueError('TTA requires eval mode without dropout/BN updates')
    def one(z):
        with torch.autocast('cuda',dtype=amp,enabled=device.type=='cuda'):
            logits=model(z)
        if not torch.isfinite(logits).all():
            with torch.autocast('cuda',enabled=False):logits=model(z.float())
        if not torch.isfinite(logits).all():
            raise FloatingPointError('Nonfinite TTA logits')
        return logits.float().sigmoid()
    plain=one(x)
    # Reflection precedes any channel-specific normalization. This experiment is norm=none.
    mirror=mirror_windows(x[0],slot_ids,codes)[None]
    return .5*(plain+one(mirror))
