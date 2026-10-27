from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageChops,ImageOps
import gzip,io,tarfile,struct,json,hashlib

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'source'
ORIG=SRC/'originals'
OUT=ROOT/'dist/assets/animations-cyan'
OUT.mkdir(parents=True,exist_ok=True)

def git_blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_one(item):
    key,meta,original=item
    raw=(ORIG/meta['file']).read_bytes()
    assert len(raw)==original['size'],meta['file']
    assert git_blob_sha(raw)==original['sha'],meta['file']+' source Git blob mismatch'
    assert raw[:4]==b'zLKD',meta['file']
    count=struct.unpack_from('<I',raw,16)[0]
    with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw[20:]))) as archive:
        members=[m for m in archive.getmembers() if m.isfile()]
        assert len(members)==1,meta['file']
        bitmap=archive.extractfile(members[0]).read()
    native=Image.open(io.BytesIO(bitmap)).convert('RGB')
    assert native.height%count==0,meta['file']
    width,height=native.width,native.height//count
    assert (width,height,count)==(meta['width'],meta['height'],meta['frames']),meta['file']
    r,g,b=native.split()
    light=ImageChops.lighter(ImageChops.lighter(r,g),b)
    cyan=ImageOps.colorize(light,(0,0,0),(0,255,255))
    frames=[cyan.crop((0,i*height,width,(i+1)*height)) for i in range(count)]
    destination=OUT/(key+'.webp')
    options={'format':'WEBP','lossless':True,'exact':True,'method':4}
    if count>1:
        options.update(save_all=True,append_images=frames[1:],duration=63,loop=0)
    frames[0].save(destination,**options)
    thumbnail=OUT/(key+'.png')
    frames[min(10,count-1)].save(thumbnail,format='PNG',optimize=True)
    decoded=Image.open(destination)
    assert decoded.size==(width,height),meta['file']
    matches=0
    timeline=0
    for i in range(decoded.n_frames):
        decoded.seek(i)
        pixel=decoded.convert('RGB')
        duration=decoded.info.get('duration',63)
        if count==1:duration=63
        assert duration%63==0,(meta['file'],duration)
        timeline+=duration
        for _ in range(duration//63):
            assert matches<count,(meta['file'],'extra frame')
            assert ImageChops.difference(pixel,frames[matches]).getbbox() is None,(meta['file'],matches)
            matches+=1
    assert matches==count,(meta['file'],matches,count)
    assert timeline==count*63,meta['file']
    if count>1:assert decoded.info.get('loop')==0,meta['file']
    assert ImageChops.difference(Image.open(thumbnail).convert('RGB'),frames[min(10,count-1)]).getbbox() is None,meta['file']
    encoded_frames=decoded.n_frames
    decoded.close()
    return key,{
        'animation':'assets/animations-cyan/'+key+'.webp',
        'still':'assets/animations-cyan/'+key+'.png',
        'encodedBytes':destination.stat().st_size,
        'stillBytes':thumbnail.stat().st_size
    },{
        'id':key,'file':meta['file'],'sourceGitBlobSha':original['sha'],
        'sourceHashMatches':True,'dimensions':[width,height],
        'originalFrames':count,'encodedFrames':encoded_frames,
        'timelineDurationMs':timeline,'allCyanFramePixelsVerified':True,
        'thumbnailVerified':True,'outputSha256':file_sha(destination)
    }

if __name__=='__main__':
    assets=json.loads((SRC/'animation-assets.json').read_text(encoding='utf-8'))
    originals={m['name']:m for m in json.loads((SRC/'original-manifest.json').read_text(encoding='utf-8-sig'))}
    color_paths=[ROOT/'dist'/a[f] for a in assets.values() if a['color'] for f in ['animation','still']]
    before={str(p.relative_to(ROOT)):file_sha(p) for p in color_paths}
    items=[(key,a,originals[a['file']]) for key,a in assets.items() if not a['color']]
    assert len(items)==59
    with ThreadPoolExecutor(max_workers=5) as pool:
        results=list(pool.map(build_one,items))
    variants={key:meta for key,meta,check in results}
    assert all(file_sha(ROOT/path)==sha for path,sha in before.items()),'Full-color assets changed'
    (SRC/'cyan-animation-assets.json').write_text(json.dumps(variants,separators=(',',':')),encoding='utf-8')
    report={
        'clips':len(variants),'frames':sum(check['originalFrames'] for _,_,check in results),
        'animationBytes':sum(a['encodedBytes'] for a in variants.values()),
        'stillBytes':sum(a['stillBytes'] for a in variants.values()),
        'palette':{'black':[0,0,0],'cyan':[0,255,255],'brightness':'max native RGB channel'},
        'frameDurationMs':63,'resized':False,'sourceAndFrameChecksPassed':True,
        'fullColorAssetsUntouched':len(before),'checks':[check for _,_,check in results]
    }
    (SRC/'cyan-asset-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
