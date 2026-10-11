"""Real keyboard-driven checks; never inject passwords or stage RAM directly."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess
p=argparse.ArgumentParser();p.add_argument('--machine',default='C-BIOS_MSX2_EU');p.add_argument('--record',action='store_true');args=p.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('map-edit-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
codes=json.loads((R/'assets/passwords.json').read_text());levels=json.loads((R/'assets/levels.json').read_text())
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set scanline 0','set blur 0','set f [open results.txt w]'];t=8.;expected=0
def ev(cmd):s.append(f'after time {t:.3f} {{{cmd}}}')
def key(row,mask):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=.2;ev(f'keymatrixup {row} {mask}');t+=.6
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
if args.record:ev('record start ./password.avi')
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
 key(7,2);t+=1.5;check(f'{i}-map-open','map_mode',1)
 key(8,1);check(f'{i}-map-turn-left','parts',2)
 key(8,128);check(f'{i}-map-next','selected',1)
 key(8,1);expected+=1;ev(f'puts $::f "{i}-second-chip [debug read memory {sym["parts"]+1}] 1"')
 key(8,16);check(f'{i}-map-prev','selected',0)
 if i in (0,25,49):ev(f'openmsx::internal_screenshot -raw map-stage-{i+1}.png')
 # Exact selected mini-tile matches its generated atlas, including facing.
 bankdata=(R/'assets/map-tiles.bin').read_bytes();facing=levels[i]['facing'][0];tile=(facing*16+8+2)*128
 x,y=levels[i]['sockets'][0];left=16 if levels[i].get('width',8)>8 else 72
 for row in range(10):
  expected+=1;ev(f'puts $::f "{i}-map-pixels-{row} [binary encode hex [debug read_block VRAM {(22+y*14+row)*128+(left+x*14)//2} 7]] {bankdata[tile+row*7:tile+(row+1)*7].hex()}"')
 key(7,2);t+=1.5;check(f'{i}-map-close','map_mode',0);check(f'{i}-keeps-turn','parts',2)
 key(7,2);t+=1.5;check(f'{i}-map-reopen','map_mode',1)
 key(8,64);check(f'{i}-map-clear','parts',0)
 key(7,4);t+=1.5;check(f'{i}-esc-close','map_mode',0)

key(6,64);t+=.5;key(7,128);t+=1;check('blank-new-game','stage',0)
if args.record:ev('record stop')
ev('close $::f;exit');s.append('after realtime 300 {exit}')
(W/'check.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
r=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=310,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(r.stdout+r.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[l for l in lines if l.split()[1]!=l.split()[2]]
out=dict(machine=args.machine,checks=len(lines),expected=expected,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/f'outputs/map-edit-verification-{args.machine}.json').write_text(json.dumps(out,indent=2));print(out)
assert r.returncode==0 and not fail and len(lines)==expected
