"""Real-keyboard cancellation while moving and while paused."""
from pathlib import Path
import argparse,os,json,re,hashlib,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--machine',default='C-BIOS_MSX2_EU');args=ap.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('cancel-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
levels=json.loads((R/'assets/levels.json').read_text())
# Select the same crate/support board after campaign reordering.
indices=[i for i,x in enumerate(levels) if x['starts']==[[0,3,1],[0,6,1]] and x['goals']==[[1,1],[6,1]]]
assert len(indices)==1
index=indices[0];lv=levels[index]
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
for j in range(len(lv['sockets'])):
 key(8,32)
 if j+1<len(lv['sockets']):key(8,128);wait(1.3)
for name,addr,size in [('parts',sym['parts'],12),('actors',sym['cat_actor'],32),('terrain',sym['params']+43,192)]:
 ev(f'set saved_{name} [debug read_block memory {addr} {size}]')
for mode in ['moving','paused']:
 key(7,128);wait(1)
 chk(mode+'-running',f'debug read memory {sym["state"]}',1)
 chk(mode+'-actors-changed',f'expr {{[debug read_block memory {sym["cat_actor"]} 32] ne $::saved_actors}}',1)
 chk(mode+'-terrain-changed',f'expr {{[debug read_block memory {sym["params"]+43} 192] ne $::saved_terrain}}',1)
 if mode=='paused':
  key(6,128,1.2);wait(1.5);chk('paused-before-cancel',f'debug read memory {sym["paused"]}',1)
 key(7,4,1);wait(2)
 chk(mode+'-editing',f'debug read memory {sym["state"]}',0)
 chk(mode+'-unpaused',f'debug read memory {sym["paused"]}',0)
 for name,addr,size in [('parts',sym['parts'],12),('actors',sym['cat_actor'],32),('terrain',sym['params']+43,192)]:
  chk(mode+'-'+name,f'expr {{[debug read_block memory {addr} {size}] eq $::saved_{name}}}',1)
 chk(mode+'-gate-reset',f'debug read memory {sym["gate"]}',0)
 chk(mode+'-music',f'debug read memory {sym["music_running"]}',1)
ev('close $::f;exit');s.append('after realtime 90 {exit}')
(W/'test.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','test.tcl'],cwd=W,env=env,capture_output=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]]
report=dict(machine=args.machine,stage=index+1,checks=len(lines),expected=checks,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/('outputs/cancel-verification-'+args.machine+'.json')).write_text(json.dumps(report,indent=2));print(report)
assert p.returncode==0 and len(lines)==checks and not fail
