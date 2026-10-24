"""MIL head adapted from Dread Development's public twelve-finding training script.
Source and unchanged reference retained under sources/notebooks/co_atnet_train.
"""
import torch
from torch import nn


def build_backbone(arch, pretrained, resolution, initialization_file=None):
    import timm
    kw = {'pretrained_cfg_overlay': {'file': initialization_file}} if pretrained and initialization_file else {}
    # CNNs such as ConvNeXt do not accept img_size. CoAtNet's attention grid does.
    if arch.startswith(('coatnet', 'swin', 'maxvit', 'maxxvit')):
        kw['img_size'] = resolution
    elif arch.startswith('vit_'):
        kw.update(img_size=resolution, dynamic_img_size=True)
    pool='token' if arch.startswith('vit_') else 'avg'
    return timm.create_model(arch, pretrained=pretrained, num_classes=0, in_chans=3, global_pool=pool, **kw)


class RaptorClassifier(nn.Module):
    def __init__(self, arch, pretrained=False, resolution=384, gradient_checkpointing=False, chunk_size=16, initialization_file=None):
        super().__init__()
        self.backbone=build_backbone(arch,pretrained,resolution,initialization_file)
        if gradient_checkpointing:self.backbone.set_grad_checkpointing(True)
        dim=self.backbone.num_features
        self.norm=nn.LayerNorm(dim)
        self.att=nn.Sequential(nn.Linear(dim,256),nn.Tanh(),nn.Dropout(.2),nn.Linear(256,12))
        self.clsW=nn.Parameter(torch.zeros(12,dim));self.clsb=nn.Parameter(torch.zeros(12))
        nn.init.trunc_normal_(self.clsW,std=.02)
        self.chunk_size=chunk_size

    def forward(self,x):
        b,k=x.shape[:2]
        flat=x.flatten(0,1)
        features=torch.cat([self.backbone(t) for t in flat.split(self.chunk_size)],dim=0).view(b,k,-1)
        h=self.norm(features);a=torch.softmax(self.att(h),dim=1)
        pooled=torch.einsum('bkn,bkf->bnf',a,h)
        return (pooled*self.clsW).sum(-1)+self.clsb


class CompactImageClassifier(nn.Module):
    """Heliosli image attention head control, without report states or geometry embeddings.

    Uses the audited common input to isolate the ConvNeXt encoder/head first. This is
    an adaptation, not the author's full multi-view/segmentation/likelihood-ratio recipe.
    """
    def __init__(self, arch, pretrained=False, resolution=352, gradient_checkpointing=False,
                 initialization_file=None, hidden=384, chunk_size=16):
        super().__init__()
        self.backbone=build_backbone(arch,pretrained,resolution,initialization_file)
        if gradient_checkpointing:self.backbone.set_grad_checkpointing(True)
        self.proj=nn.Sequential(nn.Linear(self.backbone.num_features,hidden),nn.LayerNorm(hidden))
        self.drop=nn.Dropout(.1)
        self.win_proj=nn.Linear(hidden,hidden)
        self.q_win=nn.Parameter(torch.randn(12,hidden)*.02)
        self.out_norm=nn.LayerNorm(hidden)
        self.cls_w=nn.Parameter(torch.randn(12,hidden)*.02)
        self.bias=nn.Parameter(torch.zeros(12))
        self.chunk_size=chunk_size

    def forward(self,x):
        b,k=x.shape[:2]
        tok=torch.cat([self.backbone(t) for t in x.flatten(0,1).split(self.chunk_size)],0)
        t=self.drop(self.proj(tok.float()).view(b,k,-1))
        scores=torch.einsum('bwh,ch->bwc',torch.tanh(self.win_proj(t)),self.q_win).float()
        a=scores.softmax(1).to(t.dtype)
        study=self.out_norm(torch.einsum('bwc,bwh->bch',a,t))
        return (study*self.cls_w).sum(-1).float()+self.bias


class CompactGeometryClassifier(CompactImageClassifier):
    """Original image/slot/view/geometry attention path, with no report-state prior."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        hidden=self.proj[0].out_features
        self.slot=nn.Embedding(10,hidden);self.view=nn.Embedding(6,hidden)
        self.geom=nn.Linear(4,hidden,bias=False)
        for module in (self.slot,self.view,self.geom):nn.init.zeros_(module.weight)

    def forward(self,x):
        images,meta,mask=x['images'],x['meta'],x['mask']
        b,k=images.shape[:2]
        if meta.shape!=(b,k,6) or mask.shape!=(b,k) or mask.dtype!=torch.bool:
            raise ValueError('Invalid geometry input dimensions')
        if not mask.any(1).all():raise ValueError('Empty geometry bag')
        m=meta.masked_fill(~mask[...,None],0)
        if not torch.isfinite(m).all():raise ValueError('Nonfinite geometry metadata')
        if ((m[...,:2]<0).any() or (m[...,0]>9).any() or (m[...,1]>5).any()):
            raise ValueError('Invalid slot/view identifier')
        tok=torch.cat([self.backbone(t) for t in images[mask].split(self.chunk_size)],0)
        f=self.proj(tok.float());t=f.new_zeros((b,k,f.shape[-1]));t[mask]=f
        t=self.drop(t+self.slot(m[...,0].long())+self.view(m[...,1].long())+self.geom(m[...,2:6]))
        scores=torch.einsum('bwh,ch->bwc',torch.tanh(self.win_proj(t)),self.q_win).float()
        a=scores.masked_fill(~mask[...,None],float('-inf')).softmax(1).to(t.dtype)
        study=self.out_norm(torch.einsum('bwc,bwh->bch',a,t))
        return (study*self.cls_w).sum(-1).float()+self.bias


def build_model(config, pretrained=False, gradient_checkpointing=False):
    family=config.get('model_family','raptor')
    classes={'raptor':RaptorClassifier,'compact_image_control':CompactImageClassifier,
             'compact_geometry':CompactGeometryClassifier}
    if family not in classes:raise ValueError('Unknown model family: '+family)
    return classes[family](config['arch'],pretrained,config['resolution'],gradient_checkpointing,
                           initialization_file=config.get('initialization_file'))
