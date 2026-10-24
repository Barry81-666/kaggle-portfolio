"""Record and enforce the numerical/decoder runtime that generated training inputs."""
from importlib.metadata import version, PackageNotFoundError
import cv2
import numpy as np
import pydicom


def preprocessing_runtime():
    result = {'numpy': np.__version__, 'cv2': cv2.__version__, 'pydicom': pydicom.__version__}
    for package in ['opencv-python-headless', 'pylibjpeg', 'pylibjpeg-libjpeg', 'pylibjpeg-openjpeg']:
        try:
            result[package] = version(package)
        except PackageNotFoundError:
            result[package] = None
    return result


def require_runtime(expected, observed=None):
    observed = preprocessing_runtime() if observed is None else observed
    if not expected or expected != observed:
        raise ValueError(f'Preprocessing runtime mismatch: expected={expected}, observed={observed}')
    return observed
