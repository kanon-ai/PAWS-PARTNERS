"""Keyboard-only, real-speed emulator demonstration of the current ROM."""
from pathlib import Path
import os,json,hashlib,re,subprocess,argparse
parser=argparse.ArgumentParser();parser.add_argument("--machine",default="C-BIOS_MSX2_EU");args=parser.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('music-check-'+args.machine);W.mkdir(exist_ok=True)
levels=json.loads((R/'assets/levels.json').read_text());codes=json.loads((R/'assets/passwords.json').read_text())
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set scanline 0','set blur 0','set f [open results.txt w]'];t=8.;checks=0;clips=[]
def ev(cmd):s.append(f'after time {t:.3f} {{{cmd}}}')
def key(row,mask,hold=.12):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=hold;ev(f'keymatrixup {row} {mask}');t+=.25
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

ev('set musiclog [open music-trace.txt w]')
ev(f'debug set_bp {sym["music_output"]} {{}} {{puts $::musiclog [binary encode hex [debug read_block memory {sym["music_shadow"]} 14]];debug cont}}')
record('bgm-test');wait(2);check('title-muted','music_running',0)
key(7,128);wait(1);check('game-music-on','music_running',1);shot('game-music');ev('set before [debug read_block VRAM 8192 8192]')
wait(61);checks+=1;ev(f'puts $::f "loop-twice [expr {{[debug read memory {sym["music_loops"]}]>=2}}] 1"')
key(7,2);wait(1);check('map-music-on','music_running',1);key(7,2);wait(1.5)
key(7,128);wait(5);check('stuck-state','state',5);check('stuck-muted','music_running',0);shot('stuck-muted')
# PSG debug names are recorded as evidence, and actual volumes checked.
ev('puts $::f "psg-muted [expr {[debug read {PSG regs} 8]+[debug read {PSG regs} 9]+[debug read {PSG regs} 10]}] 0"');checks+=1
key(7,128);wait(1);check('retry-restarts','music_running',1)
checks+=1;ev('puts $::f "stuck-popup-restored [expr {$::before eq [debug read_block VRAM 8192 8192]}] 1"')
key(6,32);wait(1);check('help-music-on','music_running',1);key(6,32);wait(1)
prepare(0);key(7,128);wait(.2);key(6,128,hold=1.2);wait(1.5)
check('paused-state','paused',1);check('paused-music-on','music_running',1)
wait(1);key(7,128);wait(30);check('clear-state','state',3);check('clear-jingle-finished','music_finished',1);check('clear-muted-after-phrase','music_running',0)
key(6,64);wait(1);check('back-title-muted','music_running',0)
stop();ev('close $::musiclog')

ev('close $::f;exit');s.append('after realtime 180 {exit}')
(W/'capture.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','capture.tcl'],cwd=W,env=env,capture_output=True,timeout=190,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]]
report=dict(rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),machine=args.machine,hardware_tested=False,speed='unthrottled emulator; PSG stream correctness, not a performance benchmark',checks=len(lines),expected=checks,failures=fail,clips=clips)
(R/('outputs/music-verification-'+args.machine+'.json')).write_text(json.dumps(report,indent=2));print(report)
assert p.returncode==0 and len(lines)==checks and not fail
