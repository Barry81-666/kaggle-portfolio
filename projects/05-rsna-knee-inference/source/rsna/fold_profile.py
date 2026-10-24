"""Audit the frozen weak-label folds; never consumes expert outcomes."""
import collections
import re

import numpy as np
import pandas as pd

from .common import LABELS, UID, atomic_json


def script_hint(report):
    scripts = []
    for name, pattern in [('Greek', r'[\u0370-\u03ff\u1f00-\u1fff]{3,}'),
                          ('Cyrillic', r'[\u0400-\u04ff]{3,}')]:
        if re.search(pattern, str(report)):
            scripts.append(name)
    return '+'.join(scripts) if scripts else 'Latin_or_other'


def distribution_js(left, right):
    keys = sorted(set(left) | set(right))
    p = np.array([left.get(k, 0) for k in keys], float)
    q = np.array([right.get(k, 0) for k in keys], float)
    if not p.sum() or not q.sum():
        return None
    p /= p.sum(); q /= q.sum(); midpoint = (p + q) / 2
    return float(sum(.5 * (a[a > 0] * np.log(a[a > 0] / midpoint[a > 0])).sum() for a in [p, q]))


def write_profile(folds, metadata, labels, study_metadata, output):
    train = pd.read_csv(metadata, dtype={UID: str}).set_index(UID)
    weak = pd.read_csv(labels, dtype={UID: str}).set_index(UID)
    groups = {u: {'device': study_metadata.get(u, {}).get('device_group', 'unknown'),
                  'series_present': str(study_metadata.get(u, {}).get('series_present', 'unknown')),
                  'report_script_hint': script_hint(train.loc[u, 'Report'])}
              for u in folds['folds']}
    profiles = {}
    for fold in range(5):
        validation = [u for u, f in folds['folds'].items() if f == fold]
        training = [u for u, f in folds['folds'].items() if f != fold]
        distributions = {}
        for kind in ['device', 'series_present', 'report_script_hint']:
            tr = dict(collections.Counter(groups[u][kind] for u in training))
            va = dict(collections.Counter(groups[u][kind] for u in validation))
            distributions[kind] = {'training': tr, 'validation': va,
                                   'js_divergence_nats': distribution_js(tr, va)}
        values = weak.loc[validation, LABELS].to_numpy(float)
        profiles[str(fold)] = {'studies': len(validation), 'distributions': distributions,
                               'mean_soft_targets': dict(zip(LABELS, values.mean(0).tolist())),
                               'exact_half_targets': dict(zip(LABELS, (values == .5).sum(0).tolist()))}
    report = {'fold_hash': folds['hash'], 'labels_sha256': folds['labels_sha256'],
              'metadata_sha256': folds['metadata_sha256'], 'folds': profiles,
              'expert_targets_consumed': False,
              'limitations': 'Script hints are not language IDs. Device counts audit shift; they are not a trained leave-device-out validation result.'}
    atomic_json(output, report)
    return report
