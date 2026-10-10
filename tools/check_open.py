from pathlib import Path
import argparse,os,re,subprocess,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--machine',default='TOY_MSX2_64');args=p.parse_args()
R=Path(__file__).resolve().parents[1];W=R/'work'/args.machine;W.mkdir(exist_ok=True)
(W/'user-data/machines').mkdir(parents=True,exist_ok=True)
profile=Path('C:/Program Files/openMSX/share/machines/C-BIOS_MSX2_JP.xml').read_text().replace('<size>512</size>','<size>64</size>').replace('<vram>128</vram>','<vram>64</vram>')
(W/'user-data/machines/TOY_MSX2_64.xml').write_text(profile)
levels=json.loads((R/'assets/levels.json').read_text());sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(R/'work/game.symbols').read_text()))
s=['set save_settings_on_exit false','set throttle false','set renderer SDLGL-PP','set minframeskip 0','set maxframeskip 0','set scanline 0','set blur 0','set f [open results.txt w]'];t=8.;expected=0;markers=[]
def ev(cmd):s.append(f'after time {t:.3f} {{{cmd}}}')
def check(label,addr,value):
 global expected
 expected+=1;addr=sym[addr] if isinstance(addr,str) else addr;ev(f'puts $::f "{label} [debug read memory {addr}] {value}";flush $::f')
def key(row,mask):
 global t
 ev(f'keymatrixdown {row} {mask}');t+=.2;ev(f'keymatrixup {row} {mask}');t+=.4
check('title','password_mode',1)
key(7,128);t+=1;check('title-start','password_mode',0)
check('initial','state',0)
key(6,32);t+=1;check('guide-open','help_mode',1);ev('openmsx::internal_screenshot -raw guide.png');key(7,4);t+=1;check('guide-close','help_mode',0)
t+=180;check('planning-unlimited','state',0)
# With no turns both walk to the ends and wait indefinitely, without dying.
key(7,128);t+=5;check('no-solution-stuck','state',5);check('stuck-message','status_id',12);check('cat-waits',sym['cat_actor']+7,1);check('rabbit-waits',sym['rabbit_actor']+7,1)
t+=180;check('stuck-choice-waits','state',5)
key(7,4);t+=1;check('stuck-exit-title','password_mode',1)
key(7,4);t+=1;check('stuck-return','state',5)
key(7,128);check('retry-edit','state',0);check('retry-cat-x',sym['cat_actor'],levels[0]['starts'][0][0])
ev('record start ./play.avi');record_start=t
for i,lv in enumerate(levels):
 markers.append(dict(stage=i+1,start=t));check(f'{i+1}-stage','stage',i)
 for j,part in enumerate(lv['answer']):
  for _ in range(part):key(8,1)
  check(f'{i+1}-part-{j}',sym['parts']+j,part)
  if j+1<len(lv['answer']):
   key(8,128);t+=1.2 if i>=20 else 0
 t+=.4;ev(f'openmsx::internal_screenshot -raw stage-{i+1}-placed.png')
 if i==22:
  key(7,2);check('wide-map-open','map_mode',1);t+=1;ev('openmsx::internal_screenshot -raw wide-map.png');key(7,2);t+=1.5;check('wide-map-close','map_mode',0)
 key(7,128);check(f'{i+1}-run','state',1)
 if i==22:
  key(8,64);t+=1.5;check('cursor-lower','camera_y',6);check('cursor-manual','camera_manual_mode',1)
  t+=1;check('cursor-stays-lower','camera_y',6);check('scroll-keeps-running','state',1)
  key(8,32);t+=1.5;check('cursor-upper','camera_y',0)
  key(7,2);t+=1;check('runtime-map-open','map_mode',1)
  ev(f'set map_cat [debug read memory {sym["cat_actor"]+1}];set map_rabbit [debug read memory {sym["rabbit_actor"]+1}]')
  t+=2;expected+=2
  ev(f'puts $::f "map-pauses-cat [debug read memory {sym["cat_actor"]+1}] $::map_cat";puts $::f "map-pauses-rabbit [debug read memory {sym["rabbit_actor"]+1}] $::map_rabbit"')
  key(7,2);t+=1.5;check('runtime-map-close','map_mode',0)
  key(7,1);t+=1.5;check('follow-restored','camera_manual_mode',0)
 if i==0:
  key(7,128);check('pause','paused',1);t+=3;check('paused-running','state',1);key(7,128);check('resume','paused',0)
 if i==2:
  t+=1;check('red-opened','gate',1);key(7,4);check('retry-gate-reset','gate',0);check('retry-box-reset',sym['params']+43+4*8+3,1);check('retry-part-retained',sym['parts'],lv['answer'][0]);key(7,128)
 if i==6:
  key(6,32);check('running-guide-open','help_mode',1)
  ev(f'set frozen_x [debug read memory {sym["cat_actor"]}];set frozen_y [debug read memory {sym["rabbit_actor"]+1}]')
  t+=3
  expected+=2;ev(f'puts $::f "guide-freezes-cat [debug read memory {sym["cat_actor"]}] $::frozen_x";puts $::f "guide-freezes-rabbit [debug read memory {sym["rabbit_actor"]+1}] $::frozen_y"')
  key(6,32);check('running-guide-close','help_mode',0);check('guide-preserves-run','state',1)
 t+=1;ev(f'openmsx::internal_screenshot -raw stage-{i+1}-moving.png')
 t+=24;check(f'{i+1}-clear','state',4 if i==len(levels)-1 else 3)
 for who,actor in enumerate(['cat_actor','rabbit_actor']):
  check(f'{i+1}-{actor}-arrived',sym[actor]+6,1);check(f'{i+1}-{actor}-x',sym[actor],lv['goals'][who][0]);check(f'{i+1}-{actor}-y',sym[actor]+1,lv['goals'][who][1])
 ev(f'openmsx::internal_screenshot -raw stage-{i+1}-clear.png')
 if i==6:
  check('filled-hole',sym['params']+43+2*8+5,9);check('both-gates-open','gate',3)
  key(7,4);check('restart-box',sym['params']+43+2*8+4,1);check('restart-wide-hole',sym['params']+43+2*8+5,6);check('restart-gates','gate',0)
  t+=1;key(7,128);t+=10;check('restart-clear','state',3)
 markers[-1]['end']=t
 if i<len(levels)-1:key(7,128);t+=1
key(7,128);t+=1;check('replay','stage',0);key(8,32);check('hint','status_id',6);key(8,64);check('clear','state',0);check('cleared-slot','parts',0)
ev('record stop');t+=.2;ev('close $::f;exit');s.append('after realtime 300 {exit}')
(W/'check.tcl').write_text('\n'.join(s));(W/'markers.json').write_text(json.dumps(dict(record_start=record_start,stages=markers),indent=2))
env=os.environ.copy();env.update(OPENMSX_HOME=str(W/'home'),OPENMSX_USER_DATA=str(W/'user-data'),OPENMSX_SYSTEM_DATA='C:/Program Files/openMSX/share')
rom=R/'outputs/PAWS-PARTNERS-MSX2.rom'
r=subprocess.run(['C:/Program Files/openMSX/openmsx.exe','-machine',args.machine,'-cart',str(rom),'-romtype','ASCII8','-script','check.tcl'],cwd=W,env=env,capture_output=True,timeout=310,creationflags=subprocess.CREATE_NO_WINDOW)
(W/'launch.log').write_bytes(r.stdout+r.stderr)
lines=(W/'results.txt').read_text().splitlines();fail=[l for l in lines if l.split()[1]!=l.split()[2]]
out=dict(machine=args.machine,checks=len(lines),expected=expected,failures=fail,rom_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),hardware_tested=False)
(R/f'outputs/verification-{args.machine}.json').write_text(json.dumps(out,indent=2));print(out)
assert r.returncode==0 and not fail and len(lines)==expected
