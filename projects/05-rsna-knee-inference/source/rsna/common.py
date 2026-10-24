import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

LABELS = ['ACL','MCL','Medial Meniscus','Lateral Meniscus','Medial OA','Lateral OA','PF OA','Effusion','Synovitis',"Baker's",'Contusion','Fracture']
UID = 'StudyInstanceUID'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(8 << 20), b''): h.update(b)
    return h.hexdigest()


def atomic_json(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    os.replace(tmp, p)


def now(): return datetime.now(timezone.utc).isoformat()


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
