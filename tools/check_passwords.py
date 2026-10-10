"""Real keyboard-driven checks; never inject passwords or stage RAM directly."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess
p=argparse.ArgumentParser();p.add_argument('--machine',default='C-BIOS_MSX2_EU');args=p.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('password-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
codes=json.loads((R/'assets/passwords.json').read_text());levels=json.loads((R/'assets/levels.json').read_text())
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set scanline 0','set blur 0','set f [open results.txt w]'];t=8.;expected=0
def ev(cmd):s.append(f'after time {t:.3f} {{{cmd}}}')
def key(row,mask):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=.08;ev(f'keymatrixup {row} {mask}');t+=.12
def check(label,name,value):
 global expected
 expected+=1;ev(f'puts $::f "{label} [debug read memory {sym[name]}] {value}";flush $::f')
def phrase(code):
 for n,c in enumerate(code.replace(' ','')):
  steps=ord(c)-64
  if steps<=13:
   for _ in range(steps):key(8,32)
  else:
   for _ in range(27-steps):key(8,64)
  if n<7:key(8,128)
ev('record start ./password.avi')
check('boot-title','password_mode',1)
t+=1;ev('openmsx::internal_screenshot -raw title.png')
phrase('AAAAAAAA');key(7,128);check('invalid-stays','password_mode',1);check('invalid-keeps-stage','stage',0)
t+=1;ev('openmsx::internal_screenshot -raw invalid.png')
key(7,4);t+=1;check('cancel','password_mode',0)
for i,code in enumerate(codes[:len(levels)]):
 key(6,64);t+=.5;check(f'{i}-open','password_mode',1)
 phrase(code);t+=.2
 if i==len(levels)-1:ev('openmsx::internal_screenshot -raw entered.png')
 key(7,128);t+=1
 check(f'{i}-accepted','password_mode',0);check(f'{i}-stage','stage',i);check(f'{i}-planning','state',0)
 # Editing screen must remain usable after loading from password.
 key(8,1);check(f'{i}-place','parts',1)
key(6,64);t+=.5;key(7,128);t+=1;check('blank-new-game','stage',0)
ev('record stop;close $::f;exit');s.append('after realtime 180 {exit}')
(W/'check.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
r=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=190,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(r.stdout+r.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[l for l in lines if l.split()[1]!=l.split()[2]]
out=dict(machine=args.machine,checks=len(lines),expected=expected,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/f'outputs/password-verification-{args.machine}.json').write_text(json.dumps(out,indent=2));print(out)
assert r.returncode==0 and not fail and len(lines)==expected
