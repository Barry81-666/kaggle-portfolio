"""Heliosli v1 geometry-only input adaptation, without auxiliary learned weights.

Keeps complete physical series and renders global/100mm detail views with
letterboxing. Uses uint16 series encoding, companding and explicit thin-slice
slabs from the audited source recipe. No expert labels or diagnostic rules.
This representation is separate from the production 44-slot baseline.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import pydicom
from pydicom.pixels import apply_modality_lut

TARGET = {'Sagittal': ([0,-1,0],[0,0,-1]),
          'Coronal': ([1,0,0],[0,0,-1]), 'Axial': ([1,0,0],[0,1,0])}
NORMAL = {'Sagittal': [1,0,0], 'Coronal': [0,1,0], 'Axial': [0,0,1]}
SLOTS = {('Sagittal',1):1, ('Sagittal',0):2, ('Coronal',1):3,
         ('Coronal',0):4, ('Axial',1):5, ('Axial',0):6,
         ('Sagittal',-1):7, ('Coronal',-1):8, ('Axial',-1):9}
META_COLUMNS = ['slot','view','relative_position','log_spacing_mm','extent_130','fluid']


def canonical_operation(iop, plane):
    iop=np.asarray(iop,np.float64)
    if iop.shape!=(6,) or not np.isfinite(iop).all():raise ValueError('Invalid IOP')
    c,r=iop[:3],iop[3:]
    if min(np.linalg.norm(c),np.linalg.norm(r))<1e-6:raise ValueError('Zero IOP axis')
    c=c/np.linalg.norm(c);r=r/np.linalg.norm(r)
    if abs(c@r)>1e-3:raise ValueError('Non-orthogonal IOP')
    axes=[(c,r),(r,-c),(-c,-r),(-r,c),(-c,r),(c,-r),(r,c),(-r,-c)]
    tc,tr=map(np.asarray,TARGET[plane])
    score=[float(a@tc+b@tr) for a,b in axes]
    return int(np.argmax(score))


def canonical_pixels(image, spacing, operation):
    transformations=[lambda a:a,lambda a:np.rot90(a),lambda a:np.rot90(a,2),
                     lambda a:np.rot90(a,3),lambda a:a[:,::-1],lambda a:a[::-1],
                     lambda a:a.T,lambda a:a[::-1,::-1].T]
    spacing=np.asarray(spacing,np.float64)
    if operation in (1,3,6,7):spacing=spacing[::-1]
    return np.ascontiguousarray(transformations[operation](image)),spacing


def view_bounds(shape, spacing, size, crop_mm=None, center=(.5,.5)):
    h,w=shape;sy,sx=map(float,spacing)
    if min(h,w,size)<1 or not np.isfinite([sy,sx]).all() or min(sy,sx)<=0:
        raise ValueError('Invalid physical view geometry')
    ch,cw=h,w;y=x=0
    if crop_mm is not None:
        if not np.isfinite(crop_mm) or crop_mm<=0:raise ValueError('Invalid crop size')
        extent=min(crop_mm,h*sy,w*sx)
        ch=min(h,max(1,round(extent/sy)));cw=min(w,max(1,round(extent/sx)))
        y=int(np.clip(round(center[0]*(h-1)-(ch-1)/2),0,h-ch))
        x=int(np.clip(round(center[1]*(w-1)-(cw-1)/2),0,w-cw))
    extent=max(ch*sy,cw*sx)
    oh=min(size,max(1,round(size*ch*sy/extent)))
    ow=min(size,max(1,round(size*cw*sx/extent)))
    py=(size-oh)//2;px=(size-ow)//2
    return (y,y+ch,x,x+cw),(py,py+oh,px,px+ow),float(extent)


def view_plan(plane, shape, spacing, size, local_mm=100.):
    proposed=[(0,None,(.5,.5))]
    proposed += [(2,local_mm,(.5,.25)),(3,local_mm,(.5,.75))] if plane=='Coronal' else [(1,local_mm,(.5,.5))]
    result=[];seen=set()
    for view,crop,center in proposed:
        bounds=view_bounds(shape,spacing,size,crop,center)
        # Do not repeat full-frame locals or identical clamped bilateral views.
        if bounds[:2] not in seen:
            result.append((view,bounds));seen.add(bounds[:2])
    return result


def quantize_series(volume):
    a=np.asarray(volume,np.float32)
    if a.ndim!=3 or not np.isfinite(a).all():raise ValueError('Invalid native series')
    lo=float(a.min());hi=float(a.max())
    if hi<=lo:raise ValueError('Series has no intensity variation')
    encoded=np.rint((a-lo)/max(hi-lo,1e-6)*65535).clip(0,65535).astype(np.uint16)
    window=np.percentile(encoded[:,::4,::4],[1,99]).astype(np.float64)
    return encoded,window


def compand(image, window):
    lo,hi=map(float,window)
    if not np.isfinite([lo,hi]).all() or not 0<=lo<=hi<=65535:raise ValueError('Invalid intensity window')
    knots=[(0.,0.)]
    if hi-lo<1:knots.append((65535.,1.))
    else:
        if lo>0:knots.append((lo,.02))
        knots.append((hi,.90 if hi<65535 else 1.))
        if hi<65535:knots.append((65535.,1.))
    return np.interp(image,np.asarray(knots)[:,0],np.asarray(knots)[:,1]).astype(np.float32)


def slab_series(volume, positions, thin_mm=1.75, slab_mm=3.5, tail_policy='author_half'):
    pos=np.asarray(positions,np.float64)
    if len(pos)!=len(volume) or not len(pos) or not np.isfinite(pos).all():raise ValueError('Incomplete position mapping')
    if len(pos)>1 and (np.diff(pos)<=1e-4).any():raise ValueError('Duplicate/non-increasing slice positions')
    spacing=float(np.median(np.diff(pos))) if len(pos)>1 else 0.
    if tail_policy not in ('author_half','retain_all'):raise ValueError('Unknown slab tail policy')
    groups=[list(range(i,i+1)) for i in range(len(pos))]
    dropped=[]
    if 0<spacing<thin_mm:
        n=max(1,round(slab_mm/spacing));chunks=[list(range(i,min(i+n,len(pos)))) for i in range(0,len(pos),n)]
        if tail_policy=='author_half' and len(chunks[-1])<max(1,n//2):dropped=chunks.pop()
        if len(chunks)>=2:
            groups=chunks
            volume=np.stack([np.rint(volume[g].astype(np.float32).mean(0)).astype(volume.dtype) for g in groups])
            pos=np.array([pos[g].mean() for g in groups]);spacing=float(np.median(np.diff(pos)))
        else:dropped=[]
    return volume,pos,spacing,groups,dropped


def _flag(value):
    try:result=int(float(value))
    except (TypeError,ValueError,OverflowError):return -1
    return result if result in (0,1) else -1


def _headers(uid, row, root, workers):
    sid=str(row['SeriesInstanceUID']);plane=row['Anatomical_Plane']
    files=sorted((Path(root)/uid/sid).glob('*.dcm'))
    if not files:raise ValueError('No DICOM files')
    def read(path):
        ds=pydicom.dcmread(path,stop_before_pixels=True)
        for key,want in [('StudyInstanceUID',uid),('SeriesInstanceUID',sid)]:
            if str(getattr(ds,key,''))!=want:raise ValueError('DICOM identity mismatch')
        sp=np.asarray(getattr(ds,'PixelSpacing',None),np.float64)
        iop=np.asarray(getattr(ds,'ImageOrientationPatient',None),np.float64)
        ipp=np.asarray(getattr(ds,'ImagePositionPatient',None),np.float64)
        if sp.shape!=(2,) or not np.isfinite(sp).all() or (sp<=0).any():raise ValueError('Missing/invalid PixelSpacing')
        if ipp.shape!=(3,) or not np.isfinite(ipp).all():raise ValueError('Missing/invalid IPP')
        operation=canonical_operation(iop,plane)
        normal=np.cross(iop[:3],iop[3:]);normal/=np.linalg.norm(normal)
        if normal@np.asarray(NORMAL[plane])<0:normal=-normal
        return dict(file=path,ds=ds,spacing=sp,iop=iop,ipp=ipp,normal=normal,operation=operation)
    if workers>1:
        with ThreadPoolExecutor(max_workers=workers) as pool:records=list(pool.map(read,files))
    else:records=[read(path) for path in files]
    ref=records[0]
    for record in records:
        if not np.allclose(record['spacing'],ref['spacing'],rtol=0,atol=1e-5):raise ValueError('Spacing varies within series')
        if record['operation']!=ref['operation']:raise ValueError('Canonical orientation changes within series')
        if np.dot(record['iop'][:3],ref['iop'][:3])<.995 or np.dot(record['iop'][3:],ref['iop'][3:])<.995:
            raise ValueError('Orientation varies within series')
    frames={str(getattr(r['ds'],'FrameOfReferenceUID','')) for r in records}-{''}
    if len(frames)>1:raise ValueError('FrameOfReferenceUID changes within series')
    for r in records:r['position']=float(r['ipp']@ref['normal'])
    records.sort(key=lambda r:r['position'])
    if len(records)>1 and (np.diff([r['position'] for r in records])<=1e-4).any():raise ValueError('Duplicate physical position')
    return records


def build_views(uid, rows, image_root, config):
    """Return variable-depth views, six-column metadata, and source mapping.

    Missing/corrupt series are recorded; a wholly unusable study fails. No
    slice joins another series/view. No 0.5mm fallback or learned side detector.
    """
    size=config['image_size'];prepared=[];errors=[];patients=set();tags=set();sagittal=[]
    for row in sorted(rows,key=lambda x:str(x['SeriesInstanceUID'])):
        plane=row.get('Anatomical_Plane')
        if plane not in TARGET:continue
        sid=str(row['SeriesInstanceUID'])
        try:records=_headers(uid,row,image_root,config.get('header_workers',8))
        except Exception as exc:
            errors.append({'series':sid,'stage':'headers','error':str(exc)});continue
        for r in records:
            ds=r['ds'];patient=str(getattr(ds,'PatientID','')).strip()
            if patient:patients.add(patient)
            for key in ['Laterality','ImageLaterality']:
                tag=str(getattr(ds,key,'')).strip().upper()
                if tag in ('L','R'):tags.add(tag)
        if plane=='Sagittal':sagittal.append(float(np.median([r['ipp'][0] for r in records])))
        prepared.append((row,records))
    if len(patients)>1:raise ValueError('Conflicting PatientID within study')
    side=next(iter(tags)) if len(tags)==1 else None
    side_source='dicom_laterality' if side else ('conflicting_tags' if len(tags)>1 else 'unknown')
    if not tags and sagittal:
        side='L' if np.median(sagittal)>=0 else 'R';side_source='sagittal_ipp_x'
    images=[];metadata=[];groups=[];triplets=[];series_receipts=[];duplicates=[];native_seen=[]
    for row,records in prepared:
        sid=str(row['SeriesInstanceUID']);plane=row['Anatomical_Plane'];decoded=[];positions=[];names=[];sp=None
        for r in records:
            try:
                ds=pydicom.dcmread(r['file']);a=apply_modality_lut(ds.pixel_array,ds).astype(np.float32)
                if a.ndim!=2 or not np.isfinite(a).all():raise ValueError('Invalid decoded pixels')
                photo=str(getattr(ds,'PhotometricInterpretation','')).upper()
                if photo=='MONOCHROME1':a=float(a.min())+float(a.max())-a
                elif photo!='MONOCHROME2':raise ValueError('Unsupported photometric interpretation')
                a,spacing=canonical_pixels(a,r['spacing'],r['operation'])
                if side=='R' and plane!='Sagittal':a=a[:,::-1]
                if decoded and a.shape!=decoded[0].shape:raise ValueError('Pixel matrix changes within series')
                decoded.append(np.ascontiguousarray(a));positions.append(r['position']);names.append(r['file'].name);sp=spacing
            except Exception as exc:errors.append({'series':sid,'file':r['file'].name,'stage':'pixels','error':str(exc)})
        if not decoded:continue
        try:
            native=np.stack(decoded);encoded,window=quantize_series(native);pos=np.asarray(positions,np.float64)
            if plane=='Sagittal' and side=='R':
                encoded=encoded[::-1];pos=-pos[::-1];names=names[::-1];positions=positions[::-1]
            fat=_flag(row.get('Fat_Suppression'));fluid=_flag(row.get('Fluid_Sensitive'))
            # Strict within-study dedup only, not a substitute for fold group audit.
            signature=(plane,fat,fluid,tuple(sp),tuple(pos),tuple(records[0]['iop']),side,
                       float(native.min()),float(native.max()),
                       tuple(sorted({str(getattr(r['ds'],'FrameOfReferenceUID','')) for r in records})))
            duplicate=next((old_sid for old_sig,old,old_sid in native_seen if old_sig==signature and np.array_equal(old,encoded)),None)
            if duplicate:
                duplicates.append({'series':sid,'same_as':duplicate});continue
            vol,pos,spacing,slab_groups,dropped=slab_series(encoded,pos,config.get('thin_mm',1.75),config.get('slab_mm',3.5),config.get('slab_tail','author_half'))
            receipt={'series':sid,'plane':plane,'slot':SLOTS[(plane,fat)],'files':names,
                'source_positions_mm':positions,'ordered_positions_mm':pos.tolist(),
                'pixel_spacing_mm':sp.tolist(),'orientation_operation':records[0]['operation'],
                'window_uint16':window.tolist(),'slab_source_groups':slab_groups,'slab_dropped_source_indices':dropped,'views':[]}
            begin=len(images);new_images=[];new_metadata=[];new_groups=[];new_triplets=[]
            for view,(crop,bounds,extent) in view_plan(plane,vol.shape[1:],sp,size,config.get('local_mm',100.)):
                y,y1,x,x1=crop;py,py1,px,px1=bounds;start=begin+len(new_images);group=len(receipt['views'])+sum(len(s['views']) for s in series_receipts)
                for k in range(len(vol)):
                    a=cv2.resize(vol[k,y:y1,x:x1].astype(np.float32),(px1-px,py1-py),interpolation=cv2.INTER_AREA)
                    out=np.zeros((size,size),np.uint8);out[py:py1,px:px1]=np.rint(compand(a,window)*255).astype(np.uint8)
                    new_images.append(out);new_groups.append(group)
                    relative=2*(pos[k]-pos[0])/max(pos[-1]-pos[0],1e-6)-1
                    new_metadata.append([SLOTS[(plane,fat)],view,relative,np.log1p(abs(spacing)),extent/130.,fluid])
                    new_triplets.append([start+max(0,k-1),start+k,start+min(len(vol)-1,k+1)])
                receipt['views'].append({'id':view,'start':start,'depth':len(vol),'crop_yxyx':list(crop),'valid_yxyx':list(bounds),'extent_mm':extent})
            images.extend(new_images);metadata.extend(new_metadata);groups.extend(new_groups);triplets.extend(new_triplets)
            native_seen.append((signature,encoded,sid))
            series_receipts.append(receipt)
        except Exception as exc:errors.append({'series':sid,'stage':'views','error':str(exc)})
    if not images:raise ValueError('No usable geometry views')
    return {'volume':np.stack(images),'meta':np.asarray(metadata,np.float32),
            'groups':np.asarray(groups,np.int32),'triplets':np.asarray(triplets,np.int32)}, {
            'uid':uid,'side':side,'side_source':side_source,'series':series_receipts,
            'decode_failures':errors,'duplicates_removed':duplicates,'PatientID':next(iter(patients),'')}


def model_input(pack, config, count, train=False, rng=None):
    """Fixed sampled training bag or all deterministic evaluation windows."""
    import torch
    n=len(pack['volume'])
    if not n:raise ValueError('Empty geometry input')
    triplets=np.asarray(pack['triplets'])
    if triplets.shape!=(n,3) or (triplets<0).any() or (triplets>=n).any():raise ValueError('Invalid source triplets')
    if not np.all(pack['groups'][triplets]==pack['groups'][:,None]):raise ValueError('Triplet crosses series/view boundary')
    if train:
        if count<1:raise ValueError('Training window count must be positive')
        rng=rng or np.random.default_rng();indices=rng.choice(n,count,replace=n<count)
    elif count:
        indices=np.linspace(0,n-1,count).round().astype(int)
    else:indices=np.arange(n)
    a=pack['volume'][triplets[indices]].astype(np.float32)/255
    x=torch.from_numpy(a);resolution=config['resolution'];h,w=x.shape[-2:]
    if config.get('input_mode','crop')!='crop':raise ValueError('Geometry representation requires native crop')
    if resolution>min(h,w):raise ValueError('Crop exceeds geometry cache')
    oy=int(rng.integers(0,h-resolution+1)) if train else (h-resolution)//2
    ox=int(rng.integers(0,w-resolution+1)) if train else (w-resolution)//2
    x=x[...,oy:oy+resolution,ox:ox+resolution]
    if train:x=(x*(.9+.2*float(rng.random()))).clamp(0,1)
    if config['norm']=='imagenet':
        x=(x-torch.tensor([.485,.456,.406]).view(1,3,1,1))/torch.tensor([.229,.224,.225]).view(1,3,1,1)
    return {'images':x,'meta':torch.from_numpy(pack['meta'][indices]),'mask':torch.ones(len(indices),dtype=torch.bool)}
