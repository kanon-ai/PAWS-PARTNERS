"""Keyboard-driven final-tier alternative-route regression; private spoilers."""
from puzzles import simulate
from pathlib import Path
import argparse,os,json,re,hashlib,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--machine',default='C-BIOS_MSX2_EU');args=ap.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('route-branches-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
levels=json.loads((R/'assets/levels.json').read_text())
index=48;lv=levels[index]
assert len(lv['sockets'])==10 and lv['name']=='STAGE 49'
codes=json.loads((R/'assets/passwords.json').read_text())
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set f [open results.txt w]'];t=8.;checks=0
def ev(c):s.append(f'after time {t:.3f} {{{c}}}')
def wait(n):
 global t
 t+=n
def key(row,mask,hold=.2):
 ev(f'keymatrixdown {row} {mask}');wait(hold);ev(f'keymatrixup {row} {mask}');wait(.5)
def chk(label,expr,value):
 global checks
 checks+=1;ev(f'puts $::f "{label} [{expr}] {value}";flush $::f')
for j,c in enumerate(codes[index].replace(' ','')):
 n=ord(c)-64
 for _ in range(n if n<=13 else 27-n):key(8,32 if n<=13 else 64,hold=.08)
 if j<7:key(8,128)
key(7,128);wait(2)
chk('selected-stage',f'debug read memory {sym["stage"]}',index)
current=[0]*len(lv['sockets'])
variants=[]
for choice in [0,1]:
 a=lv['answer'][:];a[0]=choice
 if choice==0:a[4]=1
 else:a[-1]=2
 variants.append(('branch-'+str(choice),a,False))
variants.append(('correct',lv['answer'],True))
for label,answer,success in variants:
 model=simulate(lv,answer,trace=True)
 assert model[0]==success
 final=model[2][-1]
 # Cursor position is retained by Esc. Return to first before editing.
 if label!='branch-0':
  for _ in range(len(answer)-1):key(8,16);wait(1.3)
 for j,value in enumerate(answer):
  for _ in range((value-current[j])%7):key(8,1)
  chk(label+'-part-'+str(j),f'debug read memory {sym["parts"]+j}',value)
  if j+1<len(answer):key(8,128);wait(1.3)
 current=answer[:]
 key(7,128);wait(35)
 chk(label+'-state',f'debug read memory {sym["state"]}',3 if success else 5)
 chk(label+'-gate',f'debug read memory {sym["gate"]}',final['gate'])
 for who,name in enumerate(['cat_actor','rabbit_actor']):
  for offset in [0,1,6]:chk(label+'-'+name+str(offset),f'debug read memory {sym[name]+offset}',final['actors'][who][offset])
 for j,value in enumerate(final['terrain']+[0]*(192-len(final['terrain']))):
  chk(label+'-terrain-'+str(j),f'debug read memory {sym["params"]+43+j}',value)
 ev('set throttle true');wait(.3)
 ev(f'openmsx::internal_screenshot -raw {label}.png');ev('set throttle false')
 if not success:
  # The stuck-menu retry retains all placements and resets the mechanisms.
  key(7,128);wait(2)
  chk(label+'-retry',f'debug read memory {sym["state"]}',0)
  for j,value in enumerate(answer):chk(label+'-retained-'+str(j),f'debug read memory {sym["parts"]+j}',value)
  for j,value in enumerate(lv['terrain']+[0]*(192-len(lv['terrain']))):
   chk(label+'-reset-'+str(j),f'debug read memory {sym["params"]+43+j}',value)
ev('close $::f;exit');s.append('after realtime 90 {exit}')
(W/'test.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','test.tcl'],cwd=W,env=env,capture_output=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]]
report=dict(machine=args.machine,stage=index+1,checks=len(lines),expected=checks,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/('outputs/route-branch-verification-'+args.machine+'.json')).write_text(json.dumps(report,indent=2));print(report)
assert p.returncode==0 and len(lines)==checks and not fail
