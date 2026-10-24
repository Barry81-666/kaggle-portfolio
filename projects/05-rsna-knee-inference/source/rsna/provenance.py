"""Immutable source snapshots tied to the code hash stored in checkpoints."""
import importlib.metadata
import json
import os
import shutil
import tempfile
from pathlib import Path
from .common import atomic_json,now,sha256,stable_hash


def source_hashes(directory=None):
    directory=Path(directory) if directory is not None else Path(__file__).resolve().parent
    files=sorted(directory.glob('*.py'))
    if not files or not (directory/'__init__.py').is_file():raise ValueError('Missing source package')
    return {'rsna/'+p.name:sha256(p) for p in files}


def source_hash(directory=None):
    return stable_hash(source_hashes(directory))


def verify_snapshot(directory, expected_code_hash=None):
    root=Path(directory);manifest=json.loads((root/'manifest.json').read_text())
    hashes=source_hashes(root/'rsna')
    if hashes!=manifest['source_hashes'] or stable_hash(hashes)!=manifest['code_hash']:
        raise ValueError('Frozen source files changed')
    if expected_code_hash is not None and manifest['code_hash']!=expected_code_hash:
        raise ValueError('Frozen source does not match checkpoint code hash')
    if sha256(root/'config-input.json')!=manifest['config_input_sha256']:
        raise ValueError('Frozen input configuration changed')
    if sha256(root/'invocation.json')!=manifest['invocation_sha256']:
        raise ValueError('Frozen invocation changed')
    return manifest


def freeze_sources(directory, config_input, invocation):
    """Called under the run lock; resumes validate rather than overwrite."""
    destination=Path(directory);current=source_hashes();code_hash=stable_hash(current)
    if destination.exists():
        manifest=verify_snapshot(destination,code_hash)
        if json.loads((destination/'config-input.json').read_text())!=config_input:
            raise ValueError('Frozen input configuration differs from this run')
        if json.loads((destination/'invocation.json').read_text())!=invocation:
            raise ValueError('Frozen invocation differs from this run')
        return manifest
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.source-staging-',dir=destination.parent))
    try:
        (staging/'rsna').mkdir()
        origin=Path(__file__).resolve().parent
        for key in current:shutil.copy2(origin/Path(key).name,staging/key)
        if source_hashes(staging/'rsna')!=current:raise ValueError('Source changed during snapshot')
        atomic_json(staging/'config-input.json',config_input)
        atomic_json(staging/'invocation.json',invocation)
        dependencies={}
        for name in ['torch','torchvision','timm','numpy','opencv-python-headless','pydicom',
                     'huggingface-hub','safetensors','pandas','scikit-learn',
                     'pylibjpeg','pylibjpeg-libjpeg','pylibjpeg-openjpeg']:
            try:dependencies[name]=importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:dependencies[name]=None
        manifest={'created_at':now(),'source_hashes':current,'code_hash':code_hash,
                  'config_input_sha256':sha256(staging/'config-input.json'),
                  'invocation_sha256':sha256(staging/'invocation.json'),
                  'dependency_versions':dependencies}
        atomic_json(staging/'manifest.json',manifest)
        os.replace(staging,destination)
        return verify_snapshot(destination,code_hash)
    finally:shutil.rmtree(staging,ignore_errors=True)
