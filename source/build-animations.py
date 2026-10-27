from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image,ImageChops,ImageOps
import io,gzip,tarfile,struct,json,hashlib,urllib.request,re,time
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'source'; ORIG=SRC/'originals'; OUT=ROOT/'dist/assets/animations'
ORIG.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((SRC/'original-manifest.json').read_text(encoding='utf-8-sig'))
keys={'alt_diverdolphins':'dolphins','alt_metropolis':'metropolis','movie1':'waterfall','meter_level01':'level01','meter_level03':'level03'}
names={'alt_airship':'Airship','alt_diverdolphins':'Dolphins','alt_dragonrider':'Dragon Rider','alt_metropolis':'Metropolis','alt_waterboard':'Waterboard','alt_wildlife':'Wildlife','alt_wrc':'WRC Rally','color_01_nightcruising':'Night Cruising','color_02_greatbarrierreef':'Great Barrier Reef','color_03_redplanet':'Red Planet','color_04_island':'Island','color_05_firedragon':'Fire Dragon','color_06_racingcart':'Racing Cart','color_07_motogp':'MotoGP'}
def blobhash(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def get_original(item):
 p=ORIG/item['name']
 if p.exists() and blobhash(p.read_bytes())==item['sha']:return item
 for attempt in range(3):
  try:
   b=urllib.request.urlopen(item['url'],timeout=60).read()
   assert blobhash(b)==item['sha'],item['name']+' Git blob differs'
   assert len(b)==item['size']
   p.write_bytes(b);return item
  except Exception:
   if attempt==2:raise
   time.sleep(1)
def name_for(stem):
 if stem in names:return names[stem]
 if stem.startswith('color_bgv'):return 'Color Background '+stem.removeprefix('color_bgv')
 if stem.startswith('color_still_bgp'):return 'Color Still '+stem.removeprefix('color_still_bgp')
 if stem.startswith('alt_bgv'):return 'Alternate Background '+stem.removeprefix('alt_bgv')
 if stem.startswith('alt_meter_li'):return 'Alternate Meter '+stem.removeprefix('alt_meter_li')
 if stem.startswith('alt_still_bgp_e'):return 'Alternate Still '+stem.removeprefix('alt_still_bgp_e')
 if stem.startswith('meter_level'):return 'Level Meter '+stem.removeprefix('meter_level').replace('_f','')
 if stem.startswith('movie'):return 'Movie '+stem.removeprefix('movie').replace('_f','').zfill(2)
 if stem.startswith('still_bgp'):return 'Still '+stem.removeprefix('still_bgp').replace('_f_','').zfill(2)
 return stem.replace('_',' ').title()
def decode(item):
 file=item['name'];raw=(ORIG/file).read_bytes();assert blobhash(raw)==item['sha']
 assert raw[:4]==b'zLKD',file
 count=struct.unpack_from('<I',raw,16)[0];assert count>0
 with tarfile.open(fileobj=io.BytesIO(gzip.decompress(raw[20:]))) as archive:
  entries=[m for m in archive.getmembers() if m.isfile()];assert len(entries)==1,(file,len(entries))
  bmp=archive.extractfile(entries[0]).read()
 native=Image.open(io.BytesIO(bmp)).convert('RGB')
 assert native.height%count==0,(file,native.size,count)
 width,height=native.width,native.height//count
 color=file.startswith('color_');stem=Path(file).stem;key=keys.get(stem,stem)
 category='Color' if color else 'Stills' if 'still' in stem else 'Meters' if 'meter' in stem else 'Backgrounds' if 'bgv' in stem else 'Movies'
 transformed=native
 if not color:
  channels=native.split();light=ImageChops.lighter(ImageChops.lighter(channels[0],channels[1]),channels[2]);transformed=ImageOps.colorize(light,(0,0,0),(255,178,71))
 frames=[transformed.crop((0,i*height,width,(i+1)*height)) for i in range(count)]
 dest=OUT/(key+'.webp')
 kwargs={'format':'WEBP','lossless':True,'method':4,'exact':True}
 if count>1:kwargs.update(save_all=True,append_images=frames[1:],duration=63,loop=0)
 frames[0].save(dest,**kwargs)
 thumb=OUT/(key+'.png');frames[min(10,count-1)].save(thumb,format='PNG',optimize=True)
 decoded=Image.open(dest);matches=0;durations=[]
 # WebP may merge adjacent identical frames; verify expanded presentation timeline.
 for frame_index in range(decoded.n_frames):
  decoded.seek(frame_index);pixel=decoded.convert('RGB');duration=decoded.info.get('duration',63)
  if decoded.n_frames==1 and count==1:duration=63
  assert duration%63==0,(file,frame_index,duration)
  repeat=max(1,duration//63);durations.append(duration)
  for _ in range(repeat):
   assert matches<count,(file,'excess frames')
   assert ImageChops.difference(pixel,frames[matches]).getbbox() is None,(file,matches,'pixel mismatch')
   matches+=1
 assert matches==count,(file,matches,count)
 decoded.close()
 meta={'name':name_for(stem),'file':file,'frames':count,'width':width,'height':height,'fps':16,'durationMs':63,'color':color,'category':category,'animation':'assets/animations/'+key+'.webp','still':'assets/animations/'+key+'.png','sourceSha256':hashlib.sha256(raw).hexdigest(),'sourceGitBlobSha':item['sha'],'encodedBytes':dest.stat().st_size,'stillBytes':thumb.stat().st_size,'decodedRgbaBytes':width*height*count*4,'decodedRgb565Bytes':width*height*count*2,'streamDoubleRgbaBytes':width*height*8}
 check={'clip':file,'sourceHashMatches':True,'allFramePixelsPreserved':True,'originalFrames':count,'encodedFrames':len(durations),'timelineDurationMs':sum(durations),'colorPreserved':color,'amberPalette':not color}
 print(json.dumps({'clip':file,'frames':count,'bytes':meta['encodedBytes'],'verified':True}),flush=True)
 return key,meta,check
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=8) as pool:
  for index,f in enumerate(as_completed([pool.submit(get_original,m) for m in manifest]),1):f.result()
 print('Downloaded and hash-verified all originals',flush=True)
 assets={};checks=[]
 with ThreadPoolExecutor(max_workers=5) as pool:
  for f in as_completed([pool.submit(decode,m) for m in manifest]):
   k,m,c=f.result();assets[k]=m;checks.append(c)
 assets=dict(sorted(assets.items(),key=lambda p:next(i for i,v in enumerate(manifest) if v['name']==p[1]['file'])))
 (SRC/'animation-assets.json').write_text(json.dumps(assets,separators=(',',':')),encoding='utf-8')
 summary={'clips':len(assets),'amberClips':sum(not m['color'] for m in assets.values()),'colorClips':sum(m['color'] for m in assets.values()),'frames':sum(m['frames'] for m in assets.values()),'originalBytes':sum(m['size'] for m in manifest),'animationBytes':sum(m['encodedBytes'] for m in assets.values()),'stillBytes':sum(m['stillBytes'] for m in assets.values()),'allClipsDecodedRgbaBytes':sum(m['decodedRgbaBytes'] for m in assets.values()),'maxActiveClipRgbaBytes':max(m['decodedRgbaBytes'] for m in assets.values()),'maxActiveClipRgb565Bytes':max(m['decodedRgb565Bytes'] for m in assets.values()),'maxStreamingDoubleRgbaBytes':max(m['streamDoubleRgbaBytes'] for m in assets.values()),'maxDimensions':[max(m['width'] for m in assets.values()),max(m['height'] for m in assets.values())],'categories':{c:sum(m['category']==c for m in assets.values()) for c in ['Movies','Backgrounds','Meters','Stills','Color']},'checks':checks}
 (SRC/'asset-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps({k:v for k,v in summary.items() if k!='checks'}),flush=True)
