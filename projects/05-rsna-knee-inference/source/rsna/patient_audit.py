"""Patient identifiers from every acquired series, independent of model slots."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pydicom


def audit_study_identity(study_directory, identity=None, workers=8):
    directory=Path(study_directory)
    files=sorted(directory.rglob('*.dcm'))
    if not files:raise ValueError('No DICOM headers for full-study identity audit')

    def read(path):
        try:
            header=pydicom.dcmread(path,stop_before_pixels=True,
                specific_tags=['PatientID','StudyInstanceUID','SeriesInstanceUID'])
            for key,expected in [('StudyInstanceUID',directory.name),
                                 ('SeriesInstanceUID',path.parent.name)]:
                value=str(getattr(header,key,''))
                if value and value!=expected:raise ValueError(key+' differs from archive path')
            return str(getattr(header,'PatientID','')).strip()
        except Exception as exc:
            raise ValueError('Full-study identity header failed: '+
                             str(path.relative_to(directory))+' ('+type(exc).__name__+')') from exc

    if workers>1:
        with ThreadPoolExecutor(max_workers=workers) as pool:values=list(pool.map(read,files))
    else:values=[read(path) for path in files]
    patients=sorted({value for value in values if value})
    result=dict(identity or {})
    previous=set(result.get('PatientID_candidates',[]))
    if not previous.issubset(patients):raise ValueError('Selected-series patient IDs absent from full-study audit')
    result['PatientID_candidates']=patients
    result['PatientID_conflict']=len(patients)>1
    if len(patients)==1:result['PatientID']=patients[0]
    else:result.pop('PatientID',None)
    result['header_audit']={'scope':'all acquired DICOM series in the study',
                          'files':len(files),'series':len({path.parent for path in files}),
                          'headers_without_patient_id':sum(not value for value in values)}
    return result
