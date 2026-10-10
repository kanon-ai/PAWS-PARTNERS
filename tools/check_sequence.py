"""Keyboard-only, real-speed emulator demonstration of the current ROM."""
from pathlib import Path
import os,json,hashlib,re,subprocess
R=Path(__file__).resolve().parents[1];W=R/'work/showcase-sequence';W.mkdir(exist_ok=True)
levels=json.loads((R/'assets/levels.json').read_text());codes=json.loads((R/'assets/passwords.json').read_text())
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set scanline 0','set blur 0','set f [open results.txt w]'];t=8.;checks=0;clips=[]
def ev(cmd):s.append(f'after time {t:.3f} {{{cmd}}}')
def key(row,mask):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=.12;ev(f'keymatrixup {row} {mask}');t+=.25
def wait(n):
 global t
 t+=n
def check(label,name,value):
 global checks
 checks+=1;ev(f'puts $::f "{label} [debug read memory {sym[name]}] {value}";flush $::f')
def shot(name):ev(f'openmsx::internal_screenshot -raw {name}.png')
def record(name):
 ev(f'record start ./{name}.avi');clips.append(dict(name=name,start=t))
def stop():
 ev('record stop');clips[-1]['duration']=t-clips[-1]['start'];wait(.5)
def load(i):
 key(6,64);wait(1.5)
 for j,c in enumerate(codes[i].replace(' ','')):
  n=ord(c)-64
  for _ in range(n if n<=13 else 27-n):key(8,32 if n<=13 else 64)
  if j<7:key(8,128)
 key(7,128);wait(1.8);check(f'loaded-{i+1}','stage',i)
def prepare(i):
 for j,p in enumerate(levels[i]['answer']):
  for _ in range(p):key(8,1)
  if j+1<len(levels[i]['answer']):key(8,128);wait(1.3)

sym['rabbit_wait']=sym['rabbit_actor']+11
key(7,128);wait(1.5)
load(20)
correct=levels[20]['answer'][:]
levels[20]['answer'][-1]=3
prepare(20);record('01-early');key(7,128);wait(5)
check('early-arrival-stuck','state',5);shot('early-stuck');wait(2);stop()
key(7,128);wait(1);check('retry-clears-wait','rabbit_wait',0);check('retry-clears-switch','gate',0)
# Selected socket is the WAIT tile. Increase WAIT 2 to WAIT 4.
key(8,1);wait(.5);record('02-timed');key(7,128);wait(.8);key(7,128)
check('paused','paused',1);check('waiting-not-stuck','state',1)
checks+=1;ev(f'puts $::f "wait-active [expr {{[debug read memory {sym["rabbit_wait"]}]>0}}] 1"')
ev(f'set remaining_wait [debug read memory {sym["rabbit_wait"]}]')
wait(2);checks+=1;ev(f'puts $::f "pause-freezes-wait [debug read memory {sym["rabbit_wait"]}] $::remaining_wait"')
key(7,2);wait(2);checks+=1;ev(f'puts $::f "map-freezes-wait [debug read memory {sym["rabbit_wait"]}] $::remaining_wait"')
key(7,2);wait(1.5);key(7,128);wait(.2);shot('countdown');wait(5)
check('timed-route-clear','state',3);check('two-switches-reset-direction','gate',0);shot('timed-clear');wait(2);stop()
# Too long also fails: the cat has already switched the arrows back.
key(7,4);wait(1);key(8,1);key(8,1);record('03-late');key(7,128);wait(6)
check('late-arrival-stuck','state',5);shot('late-stuck');wait(2);stop()
ev('close $::f;exit');s.append('after realtime 180 {exit}')
(W/'capture.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine','C-BIOS_MSX2_EU','-cart',str(rom),'-romtype','ASCII8','-script','capture.tcl'],cwd=W,env=env,capture_output=True,timeout=190,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]]
report=dict(rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),machine='C-BIOS_MSX2_EU',hardware_tested=False,speed='1x emulator time',checks=len(lines),expected=checks,failures=fail,clips=clips)
(R/'outputs/sequence-verification.json').write_text(json.dumps(report,indent=2));print(report)
assert p.returncode==0 and len(lines)==checks and not fail
