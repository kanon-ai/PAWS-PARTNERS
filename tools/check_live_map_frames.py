"""Read-only verification of captured live overview pixels and sprite positions."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--machine',default='Panasonic_FS-A1ST');a=p.parse_args()
r=Path(__file__).resolve().parents[1]
levels=json.loads((r/'assets/levels.json').read_text());rom=(r/'outputs/PAWS-PARTNERS-MSX2.rom').read_bytes()
trace=r/'work'/('live-map-trials-'+a.machine)/'live-frames.txt'
frames=patches=0;errors=[];stages=set();variants=set()
jump=[0,2,3,5,6,8,9,10,11,12,13,13,14,14,14,14,14,13,13,12,11,10,9,8,6,5,3,2,0]
# Decode the authoritative 28x28 packed atlas and independently resize it
# with Pillow, rather than reproduce the assembly downsampling loop.
mini={}
for line in trace.read_text().splitlines():
 fields=line.split()
 if len(fields)!=4:continue
 kind,i,h1,h2=fields;i=int(i);lv=levels[i];w=lv.get('width',8);left=16 if w==16 else 72
 try:u=bytes.fromhex(h1);v=bytes.fromhex(h2)
 except ValueError:continue
 stages.add(i+1)
 if kind=='F':
  if len(u)!=32 or len(v)!=32:continue
  frames+=1
  for who in range(2):
   actor=u[who*16:(who+1)*16];sat=v[who*16:(who+1)*16]
   x=left+actor[0]*14-1;y=22+actor[1]*14-2
   progress=(28 if actor[8] else 14)-actor[5] if actor[5] else 0
   dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][actor[4]]
   x+=dx*progress;y+=dy*progress
   if actor[8]:y-=jump[actor[5]]//2
   if actor[6]:y=220
   if any(sat[q]!=y or sat[q+1]!=x for q in (0,4,8,12)):
    errors.append(('sprite',i+1,who,list(actor),list(sat),(x,y)))
 else:
  if len(u)!=384 or len(v)!=24320:continue
  sockets=set(map(tuple,lv['sockets']))
  for cell in range(w*lv['height']):
   bank,hi=u[cell*2:cell*2+2];x=cell%w;y=cell//w
   if bank==255 or (x,y) in sockets:continue
   key=(bank,hi);variants.add(key)
   if key not in mini:
    source=rom[bank*8192+(hi-96)*256:bank*8192+(hi-96)*256+392]
    pixels=bytes(z for b in source for z in (b>>4,b&15))
    im=Image.frombytes('L',(28,28),pixels).resize((14,14),Image.Resampling.NEAREST)
    pix=im.tobytes();mini[key]=bytes((pix[n]<<4)|pix[n+1] for n in range(0,196,2))
   expected=mini[key]
   actual=b''.join(v[(22+y*14+row)*128+(left+x*14)//2:(22+y*14+row)*128+(left+x*14)//2+7] for row in range(14))
   patches+=1
   if actual!=expected:errors.append(('terrain',i+1,cell,bank,hi))
report=dict(machine=a.machine,frames=frames,terrain_patches=patches,stages=sorted(stages),atlas_variants=len(variants),failures=errors[:20],failure_count=len(errors),rom_sha256=hashlib.sha256(rom).hexdigest(),hardware_tested=False)
(r/f'outputs/live-map-pixels-{a.machine}.json').write_text(json.dumps(report,indent=2));print(report)
assert frames and patches and not errors
