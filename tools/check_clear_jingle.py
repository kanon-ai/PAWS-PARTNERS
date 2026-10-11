from pathlib import Path
import os,json,hashlib,re,subprocess,argparse
ap=argparse.ArgumentParser();ap.add_argument('--machine',default='C-BIOS_MSX2_EU');args=ap.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('clear-jingle-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
levels=json.loads((R/'assets/levels.json').read_text())
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set f [open results.txt w]','set trace [open trace.txt w]'];t=8.;checks=0
def ev(c):s.append(f'after time {t:.3f} {{{c}}}')
def wait(n):
 global t
 t+=n
def key(row,mask):
 ev(f'keymatrixdown {row} {mask}');wait(.15);ev(f'keymatrixup {row} {mask}');wait(.35)
def chk(label,name,val):
 global checks
 checks+=1;ev(f'puts $::f "{label} [debug read memory {sym[name]}] {val}";flush $::f')
def solve():
 for j,p in enumerate(levels[0]['answer']):
  for _ in range(p):key(8,1)
  if j+1<len(levels[0]['answer']):key(8,128);wait(1.3)
ev(f'debug set_bp {sym["music_irq_done"]} {{[debug read memory {sym["music_track"]}] == 1}} {{puts $::trace [binary encode hex [debug read_block {{PSG regs}} 0 14]];debug cont}}')
chk('title-muted','music_running',0)
ev('record start ./clear-preview.avi')
key(7,128);wait(1);chk('bgm','music_running',1);solve();ev('set before [debug read_block VRAM 8192 8192]');key(7,128);wait(9)
chk('cleared','state',3);chk('one-shot-ended','music_finished',1);chk('no-loop','music_running',0)
ev('openmsx::internal_screenshot -raw clear.png')
wait(2);chk('still-not-restarting','music_running',0)
ev('debug remove_bp bp#1')
key(7,4);wait(1);chk('clear-retry-edit','state',0)
checks+=1;ev('puts $::f "popup-restored [expr {$::before eq [debug read_block VRAM 8192 8192]}] 1"')
key(7,128);wait(9)
key(7,128);wait(1);chk('next-stage','stage',1);chk('bgm-resumed','music_running',1);chk('track-reset','music_track',0)
ev('record stop')
key(6,64);wait(1);chk('title-again','music_running',0)
ev('close $::f;close $::trace;exit');s.append('after realtime 90 {exit}')
(W/'test.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','test.tcl'],cwd=W,env=env,capture_output=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]]
trace=[bytes.fromhex(x) for x in (W/'trace.txt').read_text().splitlines()]
# Compare actual PSG registers every frame against the supplied score. Ignore I/O bits and envelope latch.
score=json.loads((R/'assets/music/clear-jingle/registers.json').read_text());shadow=[0]*14;expected=[]
for frame in range(100):
 for e in score['events']:
  if e['frame']==frame:
   for chip,reg,value in e['writes']:
    if chip==0:shadow[reg]=value
 expected.append(bytes(v & (63 if i==7 else 255) for i,v in enumerate(shadow[:13])))
actual=[bytes(v & (63 if i==7 else 255) for i,v in enumerate(x[:13])) for x in trace]
assert actual[:100]==expected, next(((i,a.hex(),b.hex()) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b),len(actual))
assert all(x[8:11]==bytes(3) for x in trace[100:]), 'phrase repeats or leaves sound on'
report=dict(machine=args.machine,checks=len(lines),expected=checks,failures=fail,exact_psg_frames=100,muted_frames=len(trace)-100,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/('outputs/clear-jingle-verification-'+args.machine+'.json')).write_text(json.dumps(report,indent=2));print(report)
assert p.returncode==0 and len(lines)==checks and not fail
