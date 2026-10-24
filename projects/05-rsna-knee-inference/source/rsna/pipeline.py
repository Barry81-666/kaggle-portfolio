"""Idempotent server-side continuation: download -> preprocessing -> checks -> fold 0."""
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from .common import atomic_json,now


def run_stage(name,args,root):
    status=root/'status/pipeline.json'
    atomic_json(status,{'stage':name,'status':'running','updated_at':now(),'command':args})
    with open(root/'logs'/f'{name}.log','a') as log:
        rc=subprocess.run([sys.executable]+args,stdout=log,stderr=subprocess.STDOUT).returncode
    if rc:raise RuntimeError(f'{name} failed, exit {rc}; see logs/{name}.log')


def download_processes(archive):
    found=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            cmd=(p/'cmdline').read_bytes().decode(errors='replace').split('\x00')
            if any(Path(x).name=='kaggle' for x in cmd) and 'competitions' in cmd and 'download' in cmd:
                if Path(os.readlink(p/'cwd'))==archive.parent:found.append(int(p.name))
        except OSError:pass
    return found


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive',default='/hy-tmp/data/rsna-knee-abnormality-detection.zip')
    ap.add_argument('--bytes',type=int,default=265018939620);ap.add_argument('--config',default='configs/exp001.json');ap.add_argument('--interval',type=int,default=600)
    a=ap.parse_args();root=Path.cwd();(root/'status').mkdir(exist_ok=True);(root/'logs').mkdir(exist_ok=True)
    lock=open(root/'status/pipeline.lock','a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    archive=Path(a.archive);last_size=-1;last_growth=time.monotonic()
    try:
        while True:
            size=archive.stat().st_size if archive.exists() else 0;pids=download_processes(archive)
            if size!=last_size:last_growth=time.monotonic();last_size=size
            stalled=time.monotonic()-last_growth>1800
            state={'stage':'download','status':'stalled' if stalled else 'waiting','bytes':size,'expected_bytes':a.bytes,
                   'fraction':size/a.bytes,'download_pids':pids,'free_bytes':shutil.disk_usage(root).free,'updated_at':now()}
            atomic_json(root/'status/pipeline.json',state);print(json.dumps(state),flush=True)
            if size>a.bytes:raise RuntimeError('Archive larger than pinned expected size')
            if not pids:
                if size!=a.bytes:raise RuntimeError('Downloader stopped before archive completion')
                with zipfile.ZipFile(archive) as z:
                    if not z.infolist():raise RuntimeError('Empty ZIP directory')
                break
            time.sleep(a.interval)
        # Independent environment checks must pass before processing/training can proceed.
        gpu_receipt=root/'status/gpu-smoke.json'
        for _ in range(120):
            if gpu_receipt.exists() and json.loads(gpu_receipt.read_text()).get('status')=='passed':break
            boot=root/'status/bootstrap.json'
            if boot.exists() and json.loads(boot.read_text()).get('status')=='failed':raise RuntimeError('Environment/GPU bootstrap failed')
            atomic_json(root/'status/pipeline.json',{'stage':'environment','status':'waiting','updated_at':now()})
            time.sleep(60)
        else:raise RuntimeError('Timed out waiting for verified GPU environment')
        run_stage('initialization',['scripts/pretrain_probe.py'],root)
        run_stage('preprocess',['-m','rsna.preprocess','--config',a.config,'--archive',str(archive)],root)
        run_stage('audit',['-m','rsna.audit','--config',a.config],root)
        run_stage('folds',['-m','rsna.folds','--config',a.config],root)
        run_stage('data_smoke',['-m','rsna.train','--config',a.config,'--fold','0','--smoke','--resume'],root)
        run_stage('overfit',['-m','rsna.train','--config',a.config,'--fold','0','--overfit','--resume'],root)
        run_stage('train_fold0',['-m','rsna.train','--config',a.config,'--fold','0','--resume'],root)
        atomic_json(root/'status/pipeline.json',{'stage':'candidate_ready','status':'complete','updated_at':now(),
                     'next':'sync logs/checkpoint, validate offline inference, upload private Kaggle bundle and submit'})
    except Exception as e:
        atomic_json(root/'status/pipeline.json',{'stage':'error','status':'failed','error':str(e),'updated_at':now()});raise

if __name__=='__main__':main()
