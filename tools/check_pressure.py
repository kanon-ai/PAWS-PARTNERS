"""Regression and mechanism necessity checks for the three replacements."""
import json,importlib.util,hashlib
from copy import deepcopy
from puzzles import R,simulate,solve

levels=json.loads((R/'assets/levels.json').read_text())
backup=R/'work/before-pressure-stages'
old=json.loads((backup/'assets/levels.json').read_text())
spec=importlib.util.spec_from_file_location('old_puzzles',backup/'tools/puzzles.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
unchanged=[];checks=[]
for i,lv in enumerate(levels):
 if i not in (21,25,29):
  assert lv==old[i],i+1
  assert simulate(lv,lv['answer'],trace=True)==module.simulate(old[i],old[i]['answer'],trace=True),i+1
  unchanged.append(i+1)
 else:
  ok,events,frames,reason=simulate(lv,lv['answer'],trace=True)
  assert ok,(i,reason)
  assert not simulate(lv,[0]*len(lv['sockets']))[0]
  checks.append(dict(stage=i+1,frames=len(frames),events=events,minimum=solve(lv)[0]))
assert (R/'assets/passwords.json').read_bytes()==(backup/'assets/passwords.json').read_bytes()
lv=levels[29]
ablations={}
for name,index in [('first-pad',3*8+4),('handoff-pad',4*8+6),('button',1*8+7)]:
 s=deepcopy(lv);s['terrain'][index]=24 if s['terrain'][index]==30 else 0
 count=len(solve(s)[1]);assert count==0,(name,count);ablations[name]=count
assert not solve(lv,cat_power=False)[1]
waits=[]
for part in (3,4,5,6):
 answer=lv['answer'][:];answer[1]=part
 if simulate(lv,answer)[0]:waits.append((part-2)*2)
assert waits==[2,4,6,8],waits
result=dict(unchanged_stage_traces=unchanged,replacements=checks,ablations=ablations,valid_waits=waits,passwords_unchanged=True,rom_sha256=hashlib.sha256((R/'outputs/PAWS-PARTNERS-MSX2.rom').read_bytes()).hexdigest())
(R/'outputs/pressure-validation.json').write_text(json.dumps(result,indent=2))
print(result)
