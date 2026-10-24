"""Training-only target override, copied into the chosen frozen recipe later.

No auxiliary weighting, row filtering, external writes, or held-out supervision.
"""
import numpy as np
import pandas as pd
from .common import LABELS, UID, sha256


def override_training(labels, train_ids, validation_ids, gold_ids, path, expected_sha):
    if len(set(train_ids)) != len(train_ids):
        raise ValueError('Duplicate training IDs')
    if set(train_ids) & (set(validation_ids) | set(gold_ids)):
        raise ValueError('Private training override overlaps held-out IDs')
    if sha256(path) != expected_sha:
        raise ValueError('Private training target file changed after freeze')
    # Explicit projection makes w_, dis_, keep_study and __conf irrelevant.
    frame = pd.read_csv(path, dtype={UID: str}, usecols=[UID] + LABELS)
    if frame[UID].isna().any() or frame[UID].duplicated().any():
        raise ValueError('Invalid private training target IDs')
    if not set(train_ids) <= set(frame[UID]) or not set(train_ids) <= set(labels):
        raise ValueError('Private targets omit a frozen training ID')
    values = frame.set_index(UID).loc[train_ids, LABELS].to_numpy(np.float64)
    if not np.isfinite(values).all() or ((values < 0) | (values > 1)).any():
        raise ValueError('Private training targets must be finite scores in [0,1]')
    result = dict(labels)
    for uid, target in zip(train_ids, values):
        result[uid] = target.astype(np.float32)
    return result
