"""Keyboard-only new stage failure/retry and pressure persistence checks."""
from pathlib import Path
import json,re,os,subprocess,hashlib
R=Path(__file__).resolve().parents[1];W=R/'work/pressure-check';W.mkdir(exist_ok=True)
levels=json.loads((R/'assets/levels.json').read_text());codes=json.loads((R/'assets/passwords.json').read_text())
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set f [open results.txt w]'];t=8.;checks=0
def ev(c):s.append(f'after time {t:.3f} {{{c}}}')
def key(row,mask):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=.12;ev(f'keymatrixup {row} {mask}');t+=.3
def wait(n):
 global t
 t+=n
def check(label,address,value):
 global checks
 checks+=1
 if isinstance(address,str):address=sym[address]
 ev(f'puts $::f "{label} [debug read memory {address}] {value}";flush $::f')
def load(i):
 key(6,64);wait(1.5)
 for j,c in enumerate(codes[i].replace(' ','')):
  n=ord(c)-64
  for _ in range(n if n<=13 else 27-n):key(8,32 if n<=13 else 64)
  if j<7:key(8,128)
 key(7,128);wait(2);check(f'load-{i+1}','stage',i)
def prepare(i):
 for j,p in enumerate(levels[i]['answer']):
  for _ in range(p):key(8,1)
  if j+1<len(levels[i]['answer']):key(8,128);wait(1.3)
key(7,128);wait(1)
for i in [21,25,29]:
 load(i);key(7,128);wait(12);check(f'{i+1}-empty-fails','state',5)
 key(7,128);wait(1);check(f'{i+1}-retry-edit','state',0);check(f'{i+1}-pressure-reset','pressure',0);check(f'{i+1}-latch-reset','gate',0)
 prepare(i);ev(f'record start ./stage-{i+1}.avi');key(7,128)
 for n in range(6):
  wait(.35);ev(f'openmsx::internal_screenshot -raw stage-{i+1}-{n}.png')
 wait(10);check(f'{i+1}-clear','state',3)
 if i==21:
  check('box-stays-on-pad',sym['params']+43+28,19);check('box-holds-gate','pressure',1)
 if i==29:
  check('pad-restored-after-push',sym['params']+43+28,18);check('box-became-bridge',sym['params']+43+29,9)
 ev('record stop');key(7,4);wait(1)
 check(f'{i+1}-restart-pressure','pressure',0);check(f'{i+1}-restart-latch','gate',0)
 for j,p in enumerate(levels[i]['answer']):check(f'{i+1}-retry-part-{j}',sym['parts']+j,p)
 if i in [21,29]:check(f'{i+1}-box-reset',sym['params']+43+26,1);check(f'{i+1}-pad-reset',sym['params']+43+28,18)
ev('close $::f;exit');s.append('after realtime 180 {exit}')
(W/'check.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine','C-BIOS_MSX2_EU','-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=190,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[l for l in lines if l.split()[1]!=l.split()[2]]
out=dict(checks=len(lines),expected=checks,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/'outputs/pressure-emulator.json').write_text(json.dumps(out,indent=2));print(out)
assert p.returncode==0 and not fail and len(lines)==checks
