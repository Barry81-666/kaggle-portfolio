"""Target-blind, training-fold-only native/cached MRI review before baseline fit."""
import json
import re
import shutil
import tempfile
import time
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

import numpy as np
import pandas as pd
import pydicom
from pydicom.pixels import apply_modality_lut

from .common import UID, atomic_json, now, sha256, stable_hash
from .dicom import header_order
from .preprocess import safe_extract


def select_samples(folds, details, reports, count=12):
    # Neither expert studies/related groups nor outer validation images are used.
    excluded = set(folds.get('gold_ids',[])) | set(folds.get('gold_related_ids_excluded',[]))
    eligible = sorted(u for u, fold in folds['folds'].items() if fold != 0 and u not in excluded)
    selected = {}; devices = Counter(details[u]['device_group'] for u in eligible)
    def add(uid, reason):
        if uid in selected:selected[uid].append(reason)
        elif len(selected) < count:selected[uid] = [reason]
    bilateral = re.compile(r'bilateral|both knees|both knee|beide knie|deux genoux|双膝', re.I)
    for u in eligible:
        if bilateral.search(reports.get(u, '')):add(u, 'report suggests bilateral; not a confirmed image finding')
        if len(selected) >= 2:break
    for u in sorted(eligible, key=lambda u:(details[u]['series_present'], u))[:2]:
        add(u, 'fewest usable input slots')
    for device in sorted(devices, key=lambda d:(devices[d],d)):
        add(next(u for u in eligible if details[u]['device_group'] == device), 'device diversity')
        if len(selected) >= max(6,count-3):break
    for u in sorted(eligible, key=lambda u:(-details[u].get('spacing_ratio',1),u))[:2]:
        add(u, 'largest observed in-plane spacing ratio')
    for u in eligible:
        if details[u].get('decode_failure_count',0):add(u,'recorded pixel decode failure')
    for u in eligible:add(u,'deterministic coverage')
    return selected


def review_passed(review_path, audit):
    path = Path(review_path)
    if not path.is_file():return False
    review = json.loads(path.read_text())
    expected = sorted(v['sha256'] for v in audit['figures'])
    return (review.get('status') == 'passed' and review.get('review_id') == audit['review_id']
            and sorted(review.get('reviewed_figure_hashes',[])) == expected
            and all(Path(v['path']).is_file() and sha256(v['path']) == v['sha256'] for v in audit['figures']))


def create_audit(c, folds, archive='/hy-tmp/data/rsna-knee-abnormality-detection.zip'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    cache = Path(c['cache_dir']); prep = c['preprocessing']
    excluded = set(folds.get('gold_ids',[])) | set(folds.get('gold_related_ids_excluded',[]))
    allowed = {u for u, f in folds['folds'].items() if f != 0 and u not in excluded}
    reports = pd.read_csv(Path(c['metadata_dir'])/'train.csv',usecols=[UID,'Report'],
                          dtype={UID:str}).set_index(UID)['Report'].fillna('').to_dict()
    details = {}
    for u in sorted(allowed):
        info = json.loads((cache/(u+'.json')).read_text())
        identity = info.get('identity',{})
        spacing = [s['pixel_spacing'] for s in info['series'] if 'pixel_spacing' in s]
        details[u] = {'device_group':'|'.join(identity.get(k,'unknown') for k in ['Manufacturer','ManufacturerModelName']),
                      'series_present':sum(not s.get('missing',False) for s in info['series']),
                      'spacing_ratio':max((max(s)/min(s) for s in spacing),default=1),
                      'decode_failure_count':len(info.get('decode_failures',[]))}
    selected = select_samples(folds,details,reports)
    bindings = {'fold_hash':folds['hash'],'cache_manifest_sha256':sha256(cache/'manifest.json'),
                'config_hash':stable_hash(c),'visual_implementation_sha256':sha256(__file__)}
    dest = Path('artifacts/visualizations/pretrain')/cache.name;dest.mkdir(parents=True,exist_ok=True)
    figures = []
    with zipfile.ZipFile(archive) as z:
        by_series = {}
        wanted = {(u,s['series']) for u in selected for s in json.loads((cache/(u+'.json')).read_text())['series'] if 'series' in s}
        for entry in z.infolist():
            parts = PurePosixPath(entry.filename).parts
            if len(parts)>=4 and (parts[-3],parts[-2]) in wanted and parts[-1].endswith('.dcm'):
                by_series.setdefault((parts[-3],parts[-2]),[]).append(entry)
        for uid, reasons in selected.items():
            info = json.loads((cache/(uid+'.json')).read_text())
            with np.load(cache/(uid+'.npz'),allow_pickle=False) as pack:
                volume, mask = pack['volume'],pack['mask']
            fig, axes = plt.subplots(len(prep['slots']),2,figsize=(10,3*len(prep['slots'])),squeeze=False)
            record = {'uid':uid,'selection_reasons':reasons,'device':details[uid]['device_group'],
                      'cache_sha256':sha256(cache/(uid+'.npz')),'slots':[]}
            start = 0
            try:
                for index,((plane,fluid,n),slot) in enumerate(zip(prep['slots'],info['series'])):
                    valid = np.flatnonzero(mask[start:start+n]); j = min(valid,key=lambda v:abs(v-n//2)) if len(valid) else n//2
                    axes[index,1].imshow(volume[start+j],cmap='gray',vmin=0,vmax=255)
                    axes[index,1].set_title(f'{plane}/fluid{fluid}: cached {int(mask[start:start+n].sum())}/{n}')
                    item = {'plane':plane,'fluid':fluid,'cache_slice_index':int(start+j),'missing':not bool(len(valid))}
                    axes[index,0].set_title('Native slice, p2/p98 display; rectangle = configured crop')
                    if 'series' in slot and not slot.get('missing'):
                        entries = by_series[(uid,slot['series'])]
                        needed = sum(e.file_size for e in entries)
                        if shutil.disk_usage(dest).free < needed+(1<<30):raise RuntimeError('Insufficient review temporary space')
                        with tempfile.TemporaryDirectory(prefix='rsna-visual-',dir=dest) as temp:
                            paths = [safe_extract(z,e,temp) for e in entries]
                            ordered = header_order(paths[0].parent,prep.get('header_workers',8))
                            count = len(ordered);lo=int(count*prep['span'][0]);hi=max(lo,int(count*prep['span'][1])-1)
                            pick=int(np.linspace(lo,hi,n).round().astype(int)[j])
                            pos,file,spacing,method,_ = ordered[min(pick,count-1)]
                            ds=pydicom.dcmread(file);a=apply_modality_lut(ds.pixel_array,ds).astype(np.float32)
                            if str(getattr(ds,'PhotometricInterpretation',''))=='MONOCHROME1':a=a.max()-a
                            low,high=np.percentile(a,[2,98]);display=np.clip((a-low)/max(high-low,1e-6),0,1)
                            axes[index,0].imshow(display,cmap='gray',vmin=0,vmax=1)
                            h,w=a.shape;rh=min(h,max(1,int(round(prep['crop_mm']/spacing[0]))));rw=min(w,max(1,int(round(prep['crop_mm']/spacing[1]))))
                            axes[index,0].add_patch(Rectangle(((w-rw)//2,(h-rh)//2),rw,rh,fill=False,edgecolor='red',linewidth=1))
                            item.update(series=slot['series'],file=Path(file).name,native_shape=[h,w],spacing=spacing.tolist(),
                                        physical_fov_mm=[float(h*spacing[0]),float(w*spacing[1])],position=pos,ordering=method,
                                        laterality=str(getattr(ds,'ImageLaterality',getattr(ds,'Laterality','unknown'))))
                    else:axes[index,0].text(.5,.5,'MISSING / unusable slot',ha='center',va='center')
                    record['slots'].append(item)
                    for ax in axes[index]:ax.axis('off')
                    start += n
                fig.suptitle(uid+'\n'+record['device']+' / '+', '.join(reasons),fontsize=9)
                fig.tight_layout(rect=[0,0,1,.96]);path=dest/(uid+'.png');fig.savefig(path,dpi=110)
                atomic_json(dest/(uid+'.json'),record)
                figures.append({'uid':uid,'path':str(path),'sha256':sha256(path)})
            finally:plt.close(fig)
    audit={'status':'awaiting_visual_review','created_at':now(),'bindings':bindings,'figures':figures,
           'cache_dir':str(cache),'review_file':str(cache/'visual-review.json'),
           'sample_ids':list(selected),'selection_scope':'outer fold0 training images only; expert and related groups excluded',
           'native_display':'single-slice p2/p98 for viewing, not the series normalization used by cached input',
           'review_checks':['knee inside configured crop','native vs cached orientation/content','missing slots and decoder handling','different devices and spacing','suspected bilateral images']}
    audit['review_id']=stable_hash({'bindings':bindings,'figures':figures})
    atomic_json(cache/'visual-audit.json',audit)
    atomic_json('status/visual-audit.json',audit)
    return audit


def wait_for_review(audit):
    while not review_passed(audit['review_file'],audit):
        print(json.dumps({'stage':'visual_review','status':'waiting','review_id':audit['review_id'],'updated_at':now()}),flush=True)
        time.sleep(60)
    atomic_json('status/visual-review.json',json.loads(Path(audit['review_file']).read_text()))


def require_review(c, fold_hash):
    cache = Path(c['cache_dir']);path=cache/'visual-audit.json'
    if not path.is_file():raise ValueError('Native/cache visual audit not generated')
    audit=json.loads(path.read_text())
    if audit['bindings']['fold_hash']!=fold_hash or audit['bindings']['cache_manifest_sha256']!=sha256(cache/'manifest.json'):
        raise ValueError('Visual review belongs to a different cache/fold lineage')
    if not review_passed(cache/'visual-review.json',audit):
        raise ValueError('Native/cache figures require actual inspection before fitting')
    return audit['review_id']
