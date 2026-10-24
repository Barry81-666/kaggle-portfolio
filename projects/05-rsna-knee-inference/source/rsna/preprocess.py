import argparse
import fcntl
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path,PurePosixPath
import numpy as np
import pandas as pd
from .common import UID,LABELS,atomic_json,stable_hash,sha256,now
from .dicom import build_study
from .runtime import preprocessing_runtime,require_runtime
from .inputs import build_input,geometry_input
from .patient_audit import audit_study_identity


def safe_extract(z,info,destination):
    name=PurePosixPath(info.filename)
    if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe ZIP member')
    out=Path(destination).joinpath(*name.parts)
    out.parent.mkdir(parents=True,exist_ok=True)
    if not info.is_dir():
        # ZipExtFile validates CRC on EOF; never trust sizes alone.
        with z.open(info) as src,open(out,'wb') as dst:shutil.copyfileobj(src,dst,8<<20)
    return out


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--archive',required=True)
    ap.add_argument('--limit',type=int,default=0);a=ap.parse_args();c=json.loads(Path(a.config).read_text())
    out=Path(c['cache_dir']);out.mkdir(parents=True,exist_ok=True);meta=Path(c['metadata_dir']);meta.mkdir(parents=True,exist_ok=True)
    lock=open(out/'preprocess.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    prep_hash=stable_hash(c['preprocessing']);manifest_path=out/'manifest.json'
    names=['dicom.py','preprocess.py','inputs.py','patient_audit.py']
    if geometry_input(c):names.append('geometry_views.py')
    implementation_hash=stable_hash({name:sha256(Path(__file__).parent/name) for name in names})
    runtime=preprocessing_runtime()
    if manifest_path.exists() and json.loads(manifest_path.read_text())['preprocessing_hash']!=prep_hash:raise ValueError('Cache preprocessing changed')
    if manifest_path.exists() and json.loads(manifest_path.read_text()).get('implementation_hash')!=implementation_hash:raise ValueError('Cache implementation changed; use a new cache lineage')
    if manifest_path.exists():require_runtime(json.loads(manifest_path.read_text()).get('preprocessing_runtime'),runtime)
    with zipfile.ZipFile(a.archive) as z:
        entries=z.infolist();uncompressed=sum(i.file_size for i in entries);free=shutil.disk_usage(out).free
        by_study={};roots=set()
        for i in entries:
            parts=PurePosixPath(i.filename).parts
            if 'train_images' in parts or 'train_series' in parts:
                k=parts.index('train_images') if 'train_images' in parts else parts.index('train_series')
                if len(parts)>k+2 and parts[-1].endswith('.dcm'):
                    by_study.setdefault(parts[k+1],[]).append(i);roots.add('/'.join(parts[:k+1]))
            if len(parts)==1 and parts[0] in ['train.csv','train_series.csv','test.csv','test_series.csv','sample_submission.csv']:
                p=meta/parts[0]
                with z.open(i) as f:b=f.read()
                if p.exists() and p.read_bytes()!=b:raise ValueError('Archive metadata differs from frozen metadata')
                if not p.exists():p.write_bytes(b)
        if not by_study:raise ValueError('No recognized training DICOM tree')
        if len(roots)!=1:raise ValueError('Multiple training image roots')
        tr=pd.read_csv(meta/'train.csv',dtype={UID:str});series=pd.read_csv(meta/'train_series.csv',dtype={UID:str,'SeriesInstanceUID':str})
        sr={u:d.to_dict('records') for u,d in series.groupby(UID,sort=False)}
        missing=set(tr[UID])-set(by_study)
        if missing:raise ValueError(f'Archive missing {len(missing)} studies')
        # Reserve uncompressed caches plus worst-case one-study temporary storage and safety margin.
        if geometry_input(c):
            chosen=tr[UID].tolist()[:a.limit or len(tr)]
            # Conservative bound, BEFORE slab reduction or compression. A full
            # geometry cache requires this space gate or a separately audited
            # capacity strategy; never extrapolate one compressed test study.
            estimated=sum(len(by_study[u]) for u in chosen)*3*c['preprocessing']['image_size']**2
        else:estimated=len(tr)*sum(s[2] for s in c['preprocessing']['slots'])*c['preprocessing']['image_size']**2
        margin=20<<30;max_study=max(sum(i.file_size for i in infos) for infos in by_study.values())
        if free<estimated+max_study+margin:raise RuntimeError('Insufficient space for caches and a temporary study')
        full=free>uncompressed+estimated+margin
        rawroot=Path('data/raw');rawroot.mkdir(parents=True,exist_ok=True)
        if a.limit:full=False
        if full:
            for i in entries:
                if i.filename.endswith('.dcm'):safe_extract(z,i,rawroot)
        manifest={'created_at':now(),'preprocessing':c['preprocessing'],'preprocessing_hash':prep_hash,'implementation_hash':implementation_hash,
                  'preprocessing_runtime':runtime,
                  'archive_bytes':Path(a.archive).stat().st_size,'uncompressed_bytes':uncompressed,
                  'mode':'full_extract' if full else 'study_batches','source':'original competition DICOMs',
                  'geometry_parity':'same rsna.dicom.build_study used at inference; not bit-exact with undocumented public 44-slice cache'}
        if manifest_path.exists():
            existing=json.loads(manifest_path.read_text())
            for key in ['archive_bytes','uncompressed_bytes']:
                if existing.get(key)!=manifest[key]:raise ValueError('Cache archive provenance changed')
            # Preserve immutable cache lineage across idempotent resumes.
        else:atomic_json(manifest_path,manifest)
        completed=0;failures=[]
        order=tr[UID].tolist()
        # Do not consume expert labels for prioritization or selection.
        for uid in order[:a.limit or len(order)]:
            target=out/(uid+'.npz')
            if target.exists() and (out/(uid+'.json')).exists():
                with np.load(target,allow_pickle=False) as cache:
                    if str(cache['preprocessing_hash'])!=prep_hash:raise ValueError('Per-study cache hash mismatch')
                    if geometry_input(c):
                        n=len(cache['volume']);size=c['preprocessing']['image_size']
                        if cache['volume'].shape!=(n,size,size) or cache['meta'].shape!=(n,6):raise ValueError('Invalid geometry cache shape')
                        if cache['triplets'].shape!=(n,3) or cache['groups'].shape!=(n,):raise ValueError('Invalid geometry cache mapping')
                        if not n or (cache['triplets']<0).any() or (cache['triplets']>=n).any():raise ValueError('Invalid geometry triplet')
                        if not np.all(cache['groups'][cache['triplets']]==cache['groups'][:,None]):raise ValueError('Geometry triplet crosses view')
                    else:
                        expected=(sum(s[2] for s in c['preprocessing']['slots']),c['preprocessing']['image_size'],c['preprocessing']['image_size'])
                        if cache['volume'].shape!=expected or cache['mask'].shape!=(expected[0],):raise ValueError('Invalid cached shape')
                completed+=1;continue
            temp=None
            try:
                if full:root=rawroot
                else:
                    temp=tempfile.TemporaryDirectory(prefix='rsna-study-',dir='data/raw');root=Path(temp.name)
                    for info in by_study[uid]:safe_extract(z,info,root)
                pack,d=build_input(uid,sr.get(uid,[]),root/next(iter(roots)),c)
                d['identity']=audit_study_identity(root/next(iter(roots))/uid,
                    d.get('identity'),c['preprocessing'].get('header_workers',8))
                tmp=out/(uid+'.npz.tmp')
                with open(tmp,'wb') as f:np.savez_compressed(f,**pack,preprocessing_hash=prep_hash)
                os.replace(tmp,target);atomic_json(out/(uid+'.json'),d);completed+=1
                # Read path must roundtrip exactly; detects accidental dtype/normalization changes.
                with np.load(target,allow_pickle=False) as cached:
                    if not all(np.array_equal(value,cached[key]) for key,value in pack.items()):raise ValueError('Cache roundtrip mismatch')
            except Exception as e:
                failures.append({'uid':uid,'error':str(e)});print(json.dumps({'uid':uid,'error':str(e)}),flush=True)
            finally:
                if temp:temp.cleanup()
            atomic_json(out/'progress.json',{'status':'processing','completed':completed,'total':len(order),'failures':failures,'updated_at':now(),
                                            'extraction_mode_this_run':'full_extract' if full else 'study_batches'})
            if completed%25==0:print(json.dumps({'cached':completed,'total':len(order)}),flush=True)
        atomic_json(out/'progress.json',{'status':'failed' if failures else ('complete' if not a.limit else 'partial'),
                    'completed':completed,'total':len(order),'failures':failures,'updated_at':now()})
        if failures:raise RuntimeError(f'{len(failures)} preprocessing failures; no silent dropping')

if __name__=='__main__':main()
