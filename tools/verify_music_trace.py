from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
song=json.loads((R/'assets/music/registers.json').read_text())
events={}
for e in song['events']:events.setdefault(e['frame'],[]).extend((q,v) for c,q,v in e['writes'] if c==0)
actual=(R/'work/music-check/music-trace.txt').read_text().splitlines()
regs=[0]*14;pos=0;resets=[]
for i,line in enumerate(actual):
 if pos==song['frames']:
  for q,v in events.get(pos,[]):regs[q]=v
  pos=0
 previous=regs[:]
 for q,v in events.get(pos,[]):regs[q]=v
 if line!=bytes(regs).hex():
  regs=previous
  for q,v in events[0]:regs[q]=v
  assert line==bytes(regs).hex(),(i,pos,line)
  resets.append(i);pos=0
 pos+=1
assert len(actual)>song['frames']*2 and len(resets)==1
report=dict(frames=len(actual),restarts=resets,errors=[],source_hz=60,rom_sha256=hashlib.sha256((R/'outputs/PAWS-PARTNERS-MSX2.rom').read_bytes()).hexdigest())
(R/'outputs/music-stream-verification.json').write_text(json.dumps(report,indent=2));print(report)
