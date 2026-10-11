"""Verify all overview labels fit a scanline and actual VRAM glyph rows survive."""
from pathlib import Path
import re,json,hashlib
r=Path(__file__).resolve().parents[1]
labels=dict(re.findall(r'(map_\w+):\s+db "([^\"]*)",0',(r/'src/wide.asm').read_text()))
assert len(labels)==11
assert all(len(t)==32 for t in labels.values()), {k:len(v) for k,v in labels.items()}
sym=dict((n,int(v,16)) for n,v in re.findall(r'(?m)^(\w+)\s+EQU\s+0([0-9A-F]+)H',(r/'work/game.symbols').read_text()))
code=(r/'work/game.bin').read_bytes();font=code[sym['password_font']-0x8000:]
levels=json.loads((r/'assets/levels.json').read_text());part=levels[25]['answer'][-1]
planning=['map_empty','map_right','map_left','map_wait2','map_wait4','map_wait6','map_wait8'][part]
reports=[]
for machine in ['C-BIOS_MSX2_EU','Panasonic_FS-A1ST']:
 for state,label in [('planning',planning),('paused','map_paused'),('running','map_running'),('clear','map_result')]:
  text=labels[label];glyphs=[]
  for c in text:
   index=int(c)+28 if c.isdigit() else ord(c)-64 if 'A'<=c<='Z' else 0
   glyphs.append(font[index*32:index*32+32])
  expected=b''.join(b''.join(g[y*4:y*4+4] for g in glyphs) for y in range(8))
  actual=(r/'work'/('map-play-'+machine)/('footer-'+state+'.bin')).read_bytes()
  assert actual[384:1408]==expected,(machine,state)
  assert actual[1408:1536]==bytes([0x55])*128,(machine,state,'overflow below footer')
  reports.append(dict(machine=machine,state=state,pixels_checked=256*8,guard_row_intact=True))
report=dict(labels_checked=len(labels),captures=reports,rom_sha256=hashlib.sha256((r/'outputs/PAWS-PARTNERS-MSX2.rom').read_bytes()).hexdigest(),hardware_tested=False)
(r/'outputs/map-footer-verification.json').write_text(json.dumps(report,indent=2));print('PASS: 11 labels; 8 full footer captures; no scanline overflow on either machine.')
