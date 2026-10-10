"""RAM-injected pressure boundary fixtures, separate from keyboard campaign tests."""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess
p=argparse.ArgumentParser();p.add_argument('--machine',default='C-BIOS_MSX2_EU');args=p.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/('supports-'+args.machine);W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set f [open results.txt w]']
t=8;expected=0
def ev(x):s.append(f'after time {t:.3f} {{{x}}}')
def write(addr,value):return f'debug write memory {addr} {value}'
ev('keymatrixdown 7 128');t+=.2;ev('keymatrixup 7 128');t+=2
for name,boxes,catpad,rabbitpad,move in [
 ('zero',0,0,0,0),('one-box',1,0,0,0),('two-boxes',2,0,0,0),
 ('one-again',1,0,0,0),('box-cat',1,1,0,0),('box-rabbit',1,0,1,0),
 ('two-friends',0,1,1,0),('three-holders',1,1,1,0),('clear-all',0,0,0,0),
 ('blocked-zero',0,0,0,1),('blocked-one',1,0,0,1),('pass-two',2,0,0,1),
 ('pass-then-close',1,1,0,1),('friends-then-close',0,1,1,1)]:
 cmds=[];base=sym['params'];ground=[0]*192;track=[0]*192
 for i in range(boxes):ground[32+i]=19
 ground[0]=18 if catpad else 0;ground[16]=18 if rabbitpad else 0
 ground[1]=43;track[1]=8 if move else 0
 for off,data in [(43,ground),(236,track)]:
  cmds.extend(write(base+off+i,v) for i,v in enumerate(data))
 for addr,value in [(base+445,8),(base+235,6),(base+3,7),(base+4,5),(base+443,7),(base+444,5)]:cmds.append(write(addr,value))
 for who,y in [('cat_actor',0),('rabbit_actor',2)]:
  data=[0,y,16,12+y*28,1 if move and who=='cat_actor' else 0,0,0,0,0,0,y,0,0,0,0,0]
  cmds.extend(write(sym[who]+i,v) for i,v in enumerate(data))
 cmds.extend(write(sym['parts']+i,0) for i in range(12))
 for label,v in [('paused',0),('password_mode',0),('map_mode',0),('state',1),('stuck_frames',0)]:cmds.append(write(sym[label],v))
 ev(';'.join(cmds));t+=3
 opened=move and boxes+catpad+rabbitpad>=2
 count=min(2,boxes+rabbitpad+(catpad if not opened else 0))
 for label,addr,value in [('count',sym['support_count'],count),('pressure',sym['pressure'],int(count>0)),('cat-x',sym['cat_actor'],int(opened)),('stuck',sym['state'],5)]:
  ev(f'puts $::f "{name}-{label} [debug read memory {addr}] {value}";flush $::f');expected+=1
 t+=.5
ev('close $::f;exit');s.append('after realtime 120 {exit}')
(W/'check.tcl').write_text('\n'.join(s),encoding='utf-8')
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
proc=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=130,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(proc.stdout+proc.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[line for line in lines if line.split()[1]!=line.split()[2]]
result=dict(machine=args.machine,checks=len(lines),expected=expected,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),scope='RAM-injected boundary fixtures; not player-input validation')
(R/f'outputs/support-verification-{args.machine}.json').write_text(json.dumps(result,indent=2));print(result)
assert proc.returncode==0 and len(lines)==expected and not fail
