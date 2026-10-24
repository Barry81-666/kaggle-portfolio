"""Shared representation dispatch for cached training and online inference."""
import torch


def geometry_input(config):
    return config['preprocessing'].get('representation')=='geometry_views'


def build_input(uid, rows, root, config):
    if geometry_input(config):
        from .geometry_views import build_views
        return build_views(uid,rows,root,config['preprocessing'])
    from .dicom import build_study
    volume,mask,details=build_study(uid,rows,root,config['preprocessing'])
    pack={'volume':volume,'mask':mask}
    pack['mirror_codes']=details['mirror_codes']
    return pack,details


def sample_input(pack, config, count, train=False, rng=None):
    if geometry_input(config):
        from .geometry_views import model_input
        return model_input(pack,config,count,train,rng)
    from .windows import windows
    return windows(pack['volume'],pack['mask'],config,count,train,rng,pack.get('mirror_codes'))


def to_device(x, device):
    return {k:v.to(device,non_blocking=True) for k,v in x.items()} if isinstance(x,dict) else x.to(device,non_blocking=True)


def add_batch(x):
    return {k:v.unsqueeze(0) for k,v in x.items()} if isinstance(x,dict) else x.unsqueeze(0)


def batch_size(x):
    return x['images'].size(0) if isinstance(x,dict) else x.size(0)
