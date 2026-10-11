from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import struct, subprocess, hashlib, json, itertools, os, shutil
R=Path(__file__).resolve().parents[1]
for n in ['assets','outputs','work']: (R/n).mkdir(exist_ok=True)
P=[(30,62,77),(53,95,109),(81,128,137),(140,182,176),(202,222,207),(248,236,199),(255,250,225),(231,180,113),(231,125,90),(174,75,89),(100,81,120),(114,142,190),(102,197,202),(157,217,188),(245,205,86),(255,255,255)]
from pixel_font import FONT
BIG=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',13)
from puzzles import simulate,solve,NAMES
LEVELS=json.loads((R/'assets/levels.json').read_text())
def verify():
 report=[]
 for lv in LEVELS:
  minimum,wins,checked=solve(lv)
  assert minimum==lv['par'] and simulate(lv,lv['answer'])[0]
  report.append(dict(name=lv['name'],minimum=minimum,solutions=wins,checked=checked,events=simulate(lv,lv['answer'])[1],without_cat=simulate(lv,lv['answer'],cat_power=False)[0],without_rabbit=simulate(lv,lv['answer'],rabbit_power=False)[0]))
 (R/'outputs/level-validation.json').write_text(json.dumps(report,indent=2));return report

def compressed(data,pad=True):
 out=bytearray();i=0
 while i<len(data):
  n=1
  while i+n<len(data) and data[i+n]==data[i] and n<127:n+=1
  if n>=3:out.extend([n,data[i]]);i+=n;continue
  j=i+1
  while j<len(data) and j-i<128:
   if j+2<len(data) and data[j]==data[j+1]==data[j+2]:break
   j+=1
  out.append(127+j-i);out.extend(data[i:j]);i=j
 out.append(0)
 assert len(out)<=16384,len(out)
 return bytes(out).ljust(16384,b'\0') if pad else bytes(out)

def image(size):
 im=Image.new('P',size,0);im.putpalette(sum(map(list,P),[])+[0]*720);return im
def pack(im):
 b=im.tobytes();return bytes((b[i]<<4)|b[i+1] for i in range(0,len(b),2))
def board(i,lv):
 import presentation,sys
 return presentation.board(sys.modules[__name__],i,lv)

def atlas():
 im=image((256,256));d=ImageDraw.Draw(im);d.rectangle((0,0,255,255),fill=0)
 # Pattern addresses 0,2,4,6: two strips of 16x64 each; artwork 24x24.
 for p in range(1,4):
  x=p*32;col=[0,14,8,12][p]
  d.rounded_rectangle((x+1,1,x+23,23),radius=5,fill=col,outline=6)
  if p<3:
   d.line((x+12,19,x+12,8,x+(20 if p==1 else 4),8),fill=0,width=3)
   end=x+(21 if p==1 else 3)
   d.polygon([(end,8),(end+(-5 if p==1 else 5),3),(end+(-5 if p==1 else 5),13)],fill=0)
  else:
   d.rounded_rectangle((x+6,5,x+18,19),radius=3,fill=0)
   d.ellipse((x+9,7,x+16,14),fill=15)
 # Selected socket corner brackets, two strips at pattern8.
 x=128
 for xx,yy,sx,sy in [(0,0,1,1),(27,0,-1,1),(0,27,1,-1),(27,27,-1,-1)]:
  d.line((x+xx+sx*6,yy,x+xx,yy,x+xx,yy+sy*6),fill=15,width=2)
 # Marble pattern10; source padding stays transparent.
 d.ellipse((161,1,174,14),fill=10);d.ellipse((161,1,173,12),fill=11)
 d.ellipse((162,1,171,9),fill=12);d.ellipse((164,2,168,5),fill=15)
 d.ellipse((178,10,189,14),fill=1) # shadow pattern11
 # Closed and open gate at patterns12 and13.
 d.rectangle((193,0,195,22),fill=9);d.rectangle((205,0,207,22),fill=9)
 for yy in [4,12,20]:d.rectangle((193,yy,207,yy+2),fill=8)
 d.rectangle((209,18,223,22),fill=13)
 # Celebration toy cat, two 16x64 strips at patterns64 and65.
 d.polygon([(3,81),(3,65),(12,72),(20,72),(28,65),(28,83)],fill=7)
 d.ellipse((2,71,29,95),fill=14)
 d.line((8,81,10,79,12,81),fill=1,width=2);d.line((19,81,21,79,23,81),fill=1,width=2)
 d.polygon([(14,84),(18,84),(16,87)],fill=9)
 d.arc((11,85,21,93),0,180,fill=1,width=2)
 d.rounded_rectangle((7,94,25,116),radius=5,fill=12)
 d.rectangle((12,98,21,107),fill=1);d.ellipse((15,101,18,104),fill=14)
 d.line((7,97,1,90),fill=14,width=5);d.line((25,97,31,89),fill=14,width=5)
 d.ellipse((5,113,14,120),fill=7);d.ellipse((20,113,29,120),fill=7)
 im.save(R/'assets/atlas.png');return pack(im)
def main():
 from compile_music import compile_music
 compile_music()
 import sys,presentation,passwords
 passwords.generate(sys.modules[__name__])
 report=verify();boards=bytearray();bt=[]
 for i,lv in enumerate(LEVELS):
  entries=[]
  for page in range(5):
   if page in (1,3) and lv.get('width',8)==8:
    entry=entries[page-1]
   else:
    entry=(4+len(boards)//8192,0x6000+len(boards)%8192)
    bitmap=presentation.overview(sys.modules[__name__],i,lv) if page==4 else presentation.board(sys.modules[__name__],i,lv,(page//2)*6,(page%2)*8)
    boards.extend(compressed(bitmap,False))
   entries.append(entry);bt.append(entry)
 boards=bytes(boards).ljust((len(boards)+8191)//8192*8192,b'\0')
 base=4+len(boards)//8192
 layout=dict(RESULT_BANK=base+27+(len(LEVELS)*512+8191)//8192,LEVEL_COUNT=len(LEVELS),STATUS_BANK=base,TILE_BANK=base+8,POPUP_BANK=base+12,TERRAIN_BANK=base+13,HELP_BANK=base+16,FLOOR_BANK=base+18,PASSWORD_BANK=base+19,MUSIC_BANK=base+21,SPECIAL_TILE_BANK=base+22,SPECIAL_BADGE_BANK=base+26)
 (R/'assets/layout.inc').write_text(''.join(f'{k} equ {v}\n' for k,v in layout.items()))
 (R/'assets/board_table.inc').write_text('board_table:\n'+''.join(f' db {bank}\n dw {addr}\n' for bank,addr in bt))
 (R/'assets/boards.bin').write_bytes(boards)
 stats=presentation.status(sys.modules[__name__]);(R/'assets/status.bin').write_bytes(stats)
 (R/'assets/help.bin').write_bytes(presentation.guide(sys.modules[__name__]))
 from port_assets import generate
 generate(sys.modules[__name__])
 inc='level_table:\n';level_data=bytearray()
 for i,lv in enumerate(LEVELS):
  data=lv['start']+lv['goal']+[len(lv['sockets']),lv['mask']]+lv['answer']+[0]*(12-len(lv['answer']))+sum(lv['sockets'],[])+[0]*(24-len(lv['sockets'])*2)+lv['terrain']+[0]*(192-len(lv['terrain']))+[lv.get('height',len(lv['terrain'])//8)]+lv['tracks']+[0]*(192-len(lv['tracks']))+lv['facing']+[0]*(12-len(lv['facing']))+lv['starts'][1]+lv['goals'][1]+[lv.get('width',8)]
  assert len(data)==446
  bank=base+27+len(level_data)//8192
  address=0x6000+len(level_data)%8192
  inc+=f' db {bank}\n dw {address}\n'
  level_data.extend(bytes(data).ljust(512,b'\0'))
 (R/'assets/level-data.bin').write_bytes(bytes(level_data).ljust((len(level_data)+8191)//8192*8192,b'\0'))
 (R/'assets/levels.inc').write_text(inc)
 asm=os.environ.get('PASMO') or shutil.which('pasmo') or 'C:/Software/Pasmo/pasmo.exe'
 for n in ['boot','game']:subprocess.run([asm,'--bin',str(R/f'src/{n}.asm'),str(R/f'work/{n}.bin'),str(R/f'work/{n}.symbols')],cwd=R,check=True)
 code=(R/'work/game.bin').read_bytes();assert len(code)<=24576
 rom=(R/'work/boot.bin').read_bytes()+code.ljust(24576,b'\xff')+boards+stats+b''.join((R/'assets'/n).read_bytes() for n in ['tiles.bin','popup.bin','terrain.bin','help.bin','floors.bin','password-screen.bin'])
 rom+=(R/'assets/music/music-bank.bin').read_bytes()
 rom+=(R/'assets/special-tiles.bin').read_bytes()+(R/'assets/socket-badges.bin').read_bytes()
 rom+=(R/'assets/level-data.bin').read_bytes()+(R/'assets/results.bin').read_bytes()
 used=len(rom);size=524288 if used<=524288 else 1048576
 assert used<=size
 rom=rom.ljust(size,b'\xff');(R/'outputs/PAWS-PARTNERS-MSX2.rom').write_bytes(rom)
 info=dict(stages=len(LEVELS),rom_bytes=len(rom),used_bytes=used,sha256=hashlib.sha256(rom).hexdigest(),time_limit=False,ram_kib=64,vram_kib=64,target='MSX2 Z80')
 (R/'outputs/build.json').write_text(json.dumps(info,indent=2));print(info)
if __name__=='__main__':main()
