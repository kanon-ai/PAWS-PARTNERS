from pathlib import Path
import json,re,os,subprocess,hashlib
R=Path(__file__).resolve().parents[1];W=R/'work/overlay-visibility-fixture';W.mkdir(exist_ok=True)
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set f [open results.txt w]'];t=8

def ev(c):s.append(f'after time {t:.3f} {{{c}}}')
def wr(a,v):return f'debug write memory {a} {v}'
ev('keymatrixdown 7 128');t+=.2;ev('keymatrixup 7 128');t+=2
cases=[([1,19,3,7,4,8,10,13,20,18,32,24],0,0,[1,19,3,7,4,8,10,13,20,18,32,24]),([1,19,3,7,4,8,10,13,20,18,32,24],15,1,[1,19,48,49,11,12,10,13,22,18,36,24]),([33,34,41,43,35,39,40,2,6,9,14,30],0,0,[33,38,42,43,35,39,40,2,6,9,14,30]),([33,34,41,43,35,39,40,2,6,9,14,30],12,1,[37,34,41,45,35,39,40,2,6,9,16,30]),([33,34,41,43,35,39,40,2,6,9,14,30],12,2,[37,34,41,44,35,39,40,2,6,9,16,30])]
badges=(R/'assets/socket-badges.bin').read_bytes();checks=0
for k,(codes,gate,pressure,expect) in enumerate(cases):
 cmds=[];p=sym['params'];terrain=[0]*192
 for i,c in enumerate(codes):terrain[(i//6)*8+i%6]=c
 for off,data in [(43,terrain),(236,[15]*192),(19,sum(([i%6,i//6] for i in range(12)),[])),(428,[1]*12)]:cmds.extend(wr(p+off+i,v) for i,v in enumerate(data))
 cmds.extend(wr(p+o,v) for o,v in [(5,12),(235,6),(445,8)])
 for n,v in [('state',0),('gate',gate),('pressure',int(pressure>0)),('support_count',pressure),('camera_x',0),('camera_y',0),('dirty',1),('terrain_refresh',1)]:cmds.append(wr(sym[n],v))
 cmds.extend(wr(sym['parts']+i,1) for i in range(12));cmds.extend(wr(sym['terrain_visual_cache']+i,255) for i in range(384));cmds.extend([wr(sym['cat_actor']+6,1),wr(sym['rabbit_actor']+6,1)])
 ev(';'.join(cmds));t+=1
 for i,c in enumerate(expect):
  x=16+(i%6)*28;y=12+(i//6)*28+20
  for row in range(8):
   hexstr=badges[c*128+row*14:c*128+(row+1)*14].hex();addr=(y+row)*128+x//2
   ev(f'puts $::f "case{k}-slot{i}-row{row} [expr {{[binary encode hex [debug read_block VRAM {addr} 14]] eq \"{hexstr}\"}}] 1"');checks+=1
 ev('set throttle true');t+=.2;ev(f'openmsx::internal_screenshot -raw case-{k}.png');ev('set throttle false');t+=.2
ev('close $::f;exit');s.append('after realtime 60 {exit}');(W/'check.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine','C-BIOS_MSX2_EU','-cart',str(R/'outputs/PAWS-PARTNERS-MSX2.rom'),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=70,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr);lines=(W/'results.txt').read_text().splitlines();fail=[x for x in lines if x.split()[1]!=x.split()[2]];print('checks',len(lines),'expected',checks,'failures',fail[:10]);assert len(lines)==checks and not fail
(R/'outputs/overlay-visibility-verification.json').write_text(json.dumps({'checks':checks,'failures':fail,'scope':'RAM-injected rendering fixtures, byte-exact VRAM comparison','rom_sha256':hashlib.sha256((R/'outputs/PAWS-PARTNERS-MSX2.rom').read_bytes()).hexdigest()},indent=2))
