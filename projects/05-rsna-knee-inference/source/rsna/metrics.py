import numpy as np
from sklearn.metrics import roc_auc_score
from .common import LABELS


def prior_baselines(train_targets, validation_targets):
    """Constant comparators fitted only on the current training fold."""
    train = np.asarray(train_targets, float)
    validation = np.asarray(validation_targets, float)
    if train.ndim != 2 or train.shape[1] != len(LABELS):
        raise ValueError('Invalid prior target shape')
    if not np.isfinite(train).any(axis=0).all():
        raise ValueError('A class has no observed training targets')
    prior = np.nanmean(train, axis=0)
    return {'train_only_mean_targets': dict(zip(LABELS, prior.tolist())),
            'train_prior': metrics(validation, np.broadcast_to(prior, validation.shape)),
            'constant_half': metrics(validation, np.full(validation.shape, .5))}


def metrics(truth, pred, soft=True):
    y, p = np.asarray(truth, float), np.asarray(pred, float)
    if y.shape != p.shape or y.ndim != 2 or y.shape[1] != len(LABELS): raise ValueError('Invalid metric shape')
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any(): raise ValueError('Invalid predictions')
    valid = np.isfinite(y)
    if not valid.any(): raise ValueError('No valid targets')
    if ((y[valid] < 0) | (y[valid] > 1)).any(): raise ValueError('Invalid targets')
    q = np.clip(p, 1e-7, 1-1e-7)
    bce = -(y * np.log(q) + (1-y)*np.log1p(-q))
    aucs, counts = {}, {}
    for j, name in enumerate(LABELS):
        v = valid[:,j]; t = (y[v,j] >= .5).astype(int) if soft else y[v,j]
        counts[name] = {'n': int(v.sum()), 'positive': int((t == 1).sum()), 'negative': int((t == 0).sum())}
        aucs[name] = float(roc_auc_score(t, p[v,j])) if len(np.unique(t)) == 2 else None
    defined = [v for v in aucs.values() if v is not None]
    return {'bce': float(bce[valid].mean()), 'brier': float(((p-y)**2)[valid].mean()),
            'macro_auc': float(np.mean(defined)) if len(defined) == 12 else None,
            'available_class_mean_auc': float(np.mean(defined)) if defined else None,
            'auc_classes': len(defined), 'per_class_auc': aucs, 'counts': counts,
            'target_kind': 'report-derived weak labels, threshold 0.5' if soft else 'expert labels'}
