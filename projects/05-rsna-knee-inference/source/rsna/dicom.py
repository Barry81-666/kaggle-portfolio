"""Shared online/offline image pipeline. Adapted physical crop from public Raptor code.
Spacing respects both axes; sorting errors are recorded rather than silently ignored.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2
import pydicom
from pydicom.pixels import apply_modality_lut


def header_order(path,workers=8):
    def read(f):
        d=pydicom.dcmread(f,stop_before_pixels=True)
        iop=getattr(d,'ImageOrientationPatient',None);ipp=getattr(d,'ImagePositionPatient',None)
        if iop is not None and ipp is not None:
            pos=float(np.dot(np.asarray(ipp,float),np.cross(np.asarray(iop[:3],float),np.asarray(iop[3:],float))));method='physical'
        elif hasattr(d,'SliceLocation'):pos=float(d.SliceLocation);method='SliceLocation'
        elif hasattr(d,'InstanceNumber'):pos=float(d.InstanceNumber);method='InstanceNumber'
        else:raise ValueError('No slice ordering geometry: '+f.name)
        spacing=np.asarray(getattr(d,'PixelSpacing',[.5,.5]),float)
        if spacing.shape!=(2,) or not np.isfinite(spacing).all() or (spacing<=0).any():raise ValueError('Invalid pixel spacing')
        return pos,str(f),spacing,method,d
    files=sorted(Path(path).glob('*.dcm'))
    if workers>1:
        with ThreadPoolExecutor(max_workers=workers) as pool:records=list(pool.map(read,files))
    else:records=[read(f) for f in files]
    records.sort(key=lambda r:(r[0],r[1]))
    return records


def choose_series(rows,plane,fluid,used):
    candidates=[r for r in rows if str(r.get('Anatomical_Plane','')).casefold()==plane.casefold() and str(r['SeriesInstanceUID']) not in used]
    if fluid in (0,1):
        preferred=[r for r in candidates if str(r.get('Fluid_Sensitive','')) in (str(fluid),str(float(fluid)))]
        if preferred:return preferred[0]
    return candidates[0] if candidates else None


def crop_resize(a,spacing,config):
    h,w=a.shape;mm=config['crop_mm'];rh=min(h,max(1,int(round(mm/spacing[0]))));rw=min(w,max(1,int(round(mm/spacing[1]))))
    y=(h-rh)//2;x=(w-rw)//2
    return cv2.resize(a[y:y+rh,x:x+rw],(config['image_size'],config['image_size']),interpolation=cv2.INTER_AREA)


def build_study(uid,rows,image_root,config):
    size=config['image_size'];depth=sum(s[2] for s in config['slots'])
    volume=np.zeros((depth,size,size),np.uint8);used=set();offset=0;diagnostics=[];identity={};failures=[];patient_ids=set();mirror_codes=[]
    for plane,fluid,k in config['slots']:
        row=choose_series(rows,plane,fluid,used)
        if row is None:diagnostics.append({'plane':plane,'missing':True});mirror_codes.append(0);offset+=k;continue
        sid=str(row['SeriesInstanceUID']);used.add(sid)
        records=header_order(Path(image_root)/uid/sid,config.get('header_workers',8))
        if not records:raise ValueError('Series has no DICOMs: '+sid)
        from .augmentation import series_code
        mirror_codes.append(series_code([r[4] for r in records]))
        for _,_,_,_,head in records:
            pid=str(getattr(head,'PatientID','')).strip()
            if pid:patient_ids.add(pid)
        n=len(records);lo=int(n*config['span'][0]);hi=max(lo,int(n*config['span'][1])-1)
        picks=np.linspace(lo,hi,k).round().astype(int)
        pixels=[];spacing=[];selected=[]
        for pick in picks:
            _,file,sp,_,head=records[min(pick,n-1)]
            for key in ['PatientID','Manufacturer','ManufacturerModelName','MagneticFieldStrength']:
                if hasattr(head,key):identity[key]=str(getattr(head,key))
            selected.append((file,sp))
        def decode(file_sp):
            file,sp=file_sp
            try:
                d=pydicom.dcmread(file);a=apply_modality_lut(d.pixel_array,d).astype(np.float32)
                if a.ndim!=2:raise ValueError('Expected 2D slice')
                if str(getattr(d,'PhotometricInterpretation',''))=='MONOCHROME1':a=a.max()-a
                return a,None
            except Exception as e:
                return None,str(e)
        workers=config.get('pixel_workers',4)
        if workers>1:
            with ThreadPoolExecutor(max_workers=workers) as pool:decoded=list(pool.map(decode,selected))
        else:decoded=[decode(item) for item in selected]
        for (file,sp),(a,error) in zip(selected,decoded):
            pixels.append(a);spacing.append(sp)
            if error:failures.append({'file':Path(file).name,'error':error})
        good=[a.ravel() for a in pixels if a is not None]
        if good:low,high=np.percentile(np.concatenate(good),config['percentiles'])
        else:
            # A corrupt series is missing input, not a negative label. Retain other usable planes.
            diagnostics.append({'series':sid,'plane':plane,'fluid':fluid,'missing':True,
                'reason':'all selected slices failed decoding','slices':n})
            offset+=k;continue
        for j,(a,sp) in enumerate(zip(pixels,spacing)):
            if a is not None:
                a=np.clip((a-low)/(high-low+1e-6),0,1)
                volume[offset+j]=(crop_resize(a,sp,config)*255).astype(np.uint8)
        diagnostics.append({'series':sid,'plane':plane,'fluid':fluid,'slices':n,'positions':[r[0] for r in records],
                            'ordering_methods':sorted(set(r[3] for r in records)),'pixel_spacing':records[0][2].tolist()})
        offset+=k
    mask=(volume.reshape(depth,-1).sum(1)>0).astype(np.uint8)
    if not mask.any():raise ValueError('Study contains no usable images')
    identity['PatientID_candidates']=sorted(patient_ids)
    # Do not hide conflicting source headers by overwriting with the last ID.
    identity['PatientID_conflict']=len(patient_ids)>1
    if len(patient_ids)==1:identity['PatientID']=next(iter(patient_ids))
    elif len(patient_ids)>1:identity.pop('PatientID',None)
    return volume,mask,{'uid':uid,'series':diagnostics,'identity':identity,'decode_failures':failures,'mirror_codes':mirror_codes}
