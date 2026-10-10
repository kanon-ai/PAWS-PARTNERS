"""Keyboard-driven prototype checks. Spoiler material stays local."""
from pathlib import Path
import json,re,os,subprocess,hashlib,argparse
from puzzles import simulate
parser=argparse.ArgumentParser();parser.add_argument('--machine',default='C-BIOS_MSX2_EU')
parser.add_argument('--record',action='store_true')
parser.add_argument('--wrong-paths',action='store_true');args=parser.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/(('wrong-trials-' if args.wrong_paths else 'trials-')+args.machine);W.mkdir(exist_ok=True)
levels=json.loads((R/'assets/levels.json').read_text());sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set f [open results.txt w]'];t=8.;expected=0
def ev(c):s.append(f'after time {t:.3f} {{{c}}}')
def wait(n):
 global t
 t+=n
def key(row,mask,hold=.12):
 ev(f'keymatrixdown {row} {mask}');wait(hold);ev(f'keymatrixup {row} {mask}');wait(.3)
def check(label,address,value):
 global expected
 expected+=1
 if isinstance(address,str):address=sym[address]
 ev(f'puts $::f "{label} [debug read memory {address}] {value}";flush $::f')
key(7,128);wait(2)
for i,lv in enumerate(levels):
 initial_pressure=int(19 in lv['terrain'] or any(lv['terrain'][y*lv.get('width',8)+x] in (18,30) for x,y,d in lv['starts']))
 check(f'{i}-loaded','stage',i)
 check(f'{i}-initial-pressure','pressure',initial_pressure)
 initial_supports=min(2,sum(t==19 for t in lv['terrain'])+sum(lv['terrain'][y*lv.get('width',8)+x] in (18,30) for x,y,d in lv['starts']))
 check(f'{i}-initial-supports','support_count',initial_supports)
 check(f'{i}-height',sym['params']+235,lv['height'])
 check(f'{i}-width',sym['params']+445,lv.get('width',8))
 # F3 must depend on actual map size, not campaign position.
 bottom=6 if lv['height']>6 else 0
 pages=([(8,0),(0,6),(8,6),(0,0)] if bottom else [(8,0),(0,0)]) if lv.get('width',8)>8 else [(0,bottom),(0,0)]
 for page,(cx,cy) in enumerate(pages):
  key(6,128);wait(1.5)
  check(f'{i}-page-{page}-x','camera_x',cx)
  check(f'{i}-page-{page}-y','camera_y',cy)
  if lv.get('width',8)>8 or 41 in lv['terrain'] or 43 in lv['terrain']:
   ev('set throttle true');wait(.25)
   ev(f'openmsx::internal_screenshot -raw wide-{i+1}-{cx}-{cy}.png');ev('set throttle false')
 if lv.get('width',8)>8:
  key(7,2);wait(1.5);check(f'{i}-map-open','map_mode',1)
  ev('set throttle true');wait(.25)
  ev(f'openmsx::internal_screenshot -raw wide-{i+1}-map.png');ev('set throttle false')
  key(7,2);wait(1.5);check(f'{i}-map-close','map_mode',0)
 if args.wrong_paths:
  wrong=simulate(lv,[0]*len(lv['sockets']),trace=True)
  assert not wrong[0]
  final=wrong[2][-1]
  assert all((a[6] or a[8]) and not a[3] and not a[9] for a in final['actors'])
  key(7,128);wait(28);check(f'{i}-wrong-stuck','state',5)
  check(f'{i}-wrong-gate','gate',final['gate'])
  for who,name in enumerate(['cat_actor','rabbit_actor']):
   for offset,index in [(0,0),(1,1),(6,6)]:
    check(f'{i}-wrong-{name}-{offset}',sym[name]+offset,final['actors'][who][index])
  for index,value in enumerate(final['terrain']+[0]*(192-len(final['terrain']))):
   check(f'{i}-wrong-terrain-{index}',sym['params']+43+index,value)
  if i in (0,len(levels)-2):
   ev('set throttle true');wait(.25)
   ev(f'openmsx::internal_screenshot -raw stuck-{i+1}.png');ev('set throttle false')
  key(7,128);wait(2);check(f'{i}-wrong-retry','state',0)
  check(f'{i}-wrong-reset-pressure','pressure',initial_pressure)
  check(f'{i}-wrong-reset-supports','support_count',initial_supports)
  for index,value in enumerate(lv['terrain']+[0]*(192-len(lv['terrain']))):
   check(f'{i}-wrong-reset-terrain-{index}',sym['params']+43+index,value)
  key(7,128);wait(28);check(f'{i}-wrong-repeat-stuck','state',5)
  key(7,4);wait(2);check(f'{i}-wrong-title','password_mode',1)
  key(7,4);wait(2);check(f'{i}-wrong-return','password_mode',0)
  check(f'{i}-wrong-return-state','state',5)
  check(f'{i}-wrong-return-stage','stage',i)
  key(7,128);wait(2);check(f'{i}-wrong-final-retry','state',0)
 for j,p in enumerate(lv['answer']):
  for _ in range(p):key(8,1)
  check(f'{i}-part-{j}',sym['parts']+j,p)
  if j<len(lv['answer'])-1:key(8,128);wait(1.3)
 # Give SDL a real presentation interval: unthrottled screenshots can contain
 # the previous displayed frame even after game RAM has advanced correctly.
 wait(1.5);ev('set throttle true');wait(.25)
 ev(f'openmsx::internal_screenshot -raw trial-{i+1}-placed.png');ev('set throttle false')
 if args.record:ev(f'record start ./trial-{i+1}.avi')
 key(7,128)
 if lv.get('width',8)>8:
  # Pause through the real keyboard before browsing. Camera operations must
  # leave both actors and every mutable terrain cell exactly unchanged.
  # F3 explicitly pauses instead of toggling pause, and the held key spans
  # a possible terrain redraw caused by the first crate interaction.
  wait(2);key(6,128,hold=1.2);wait(1.5);check('wide-paused','paused',1)
  ev(f'set frozen [debug read_block memory {sym["cat_actor"]} 32]; set ground [debug read_block memory {sym["params"]+43} 192]')
  for row,mask,cx,cy in [(8,16,0,None),(8,32,0,0),(8,128,8,0),(8,64,8,bottom),(8,16,0,bottom)]:
   key(row,mask);wait(.5)
   check(f'wide-cursor-{mask}-x','camera_x',cx)
   if cy is not None:check(f'wide-cursor-{mask}-y','camera_y',cy)
  expected+=2
  ev(f'puts $::f "wide-frozen-actors [expr {{[debug read_block memory {sym["cat_actor"]} 32] eq $::frozen}}] 1"')
  ev(f'puts $::f "wide-frozen-terrain [expr {{[debug read_block memory {sym["params"]+43} 192] eq $::ground}}] 1";flush $::f')
  for switch in range(2):
   ev(f'set expected_follow [expr {{1 - [debug read memory {sym["follow_actor"]}]}}]')
   ev(f'if {{[debug read memory [expr {{{sym["cat_actor"]}+16*$::expected_follow+6}}]]}} {{set expected_follow [expr {{1-$::expected_follow}}]}}')
   ev(f'set expected_actor [expr {{{sym["cat_actor"]}+16*$::expected_follow}}]')
   key(7,1,hold=.3);wait(2)
   expected+=3
   ev(f'puts $::f "{i}-follow-{switch} [debug read memory {sym["follow_actor"]}] $::expected_follow"')
   ev(f'puts $::f "{i}-follow-{switch}-x [debug read memory {sym["camera_x"]}] [expr {{[debug read memory $::expected_actor] & 8}}]"')
   ev(f'puts $::f "{i}-follow-{switch}-y [debug read memory {sym["camera_y"]}] [expr {{[debug read memory [expr {{$::expected_actor+1}}]] >= 6 ? 6 : 0}}]";flush $::f')
  check('wide-follow-manual-off','camera_manual_mode',0)
  key(7,128);check('wide-resumed','paused',0)
 for n in range(8):wait(.35);ev(f'openmsx::internal_screenshot -raw trial-{i+1}-{n}.png')
 wait(24);check(f'{i}-clear','state',4 if i==len(levels)-1 else 3)
 for who,name in enumerate(['cat_actor','rabbit_actor']):
  check(f'{i}-{name}-done',sym[name]+6,1)
  check(f'{i}-{name}-x',sym[name],lv['goals'][who][0]);check(f'{i}-{name}-y',sym[name]+1,lv['goals'][who][1])
 model=simulate(lv,lv['answer'],trace=True)
 assert model[0]
 check(f'{i}-gate-model','gate',model[2][-1]['gate'])
 for index,value in enumerate(model[2][-1]['terrain']+[0]*(192-len(model[2][-1]['terrain']))):
  check(f'{i}-terrain-{index}',sym['params']+43+index,value)
 for cell,tile in enumerate(lv['terrain']):
  if tile==35:check(f'{i}-fragile-result-{cell}',sym['params']+43+cell,model[2][-1]['terrain'][cell])
 if args.record:ev('record stop')
 key(7,4);wait(1)
 check(f'{i}-retry','state',0);check(f'{i}-gate-reset','gate',0);check(f'{i}-pad-reset','pressure',initial_pressure);check(f'{i}-supports-reset','support_count',initial_supports)
 for index,value in enumerate(lv['terrain']+[0]*(192-len(lv['terrain']))):
  check(f'{i}-reset-terrain-{index}',sym['params']+43+index,value)
 for cell,tile in enumerate(lv['terrain']):
  if tile==35:check(f'{i}-fragile-reset-{cell}',sym['params']+43+cell,35)
 key(7,128);wait(28);check(f'{i}-repeat-clear','state',4 if i==len(levels)-1 else 3)
 key(7,128);wait(2)
check('wrap','stage',0);ev('close $::f;exit')
deadline=max(180,len(levels)*(14 if args.wrong_paths else 8))
s.append(f'after realtime {deadline} {{exit}}')
(W/'check.tcl').write_text('\n'.join(s))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
p=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=deadline+10,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(p.stdout+p.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[l for l in lines if l.split()[1]!=l.split()[2]]
out=dict(machine=args.machine,checks=len(lines),expected=expected,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False,wrong_paths=args.wrong_paths)
prefix='wrong-trial-verification' if args.wrong_paths else 'trial-verification'
(R/f'outputs/{prefix}-{args.machine}.json').write_text(json.dumps(out,indent=2));print(out)
assert p.returncode==0 and not fail and len(lines)==expected
