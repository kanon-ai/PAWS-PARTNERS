from PIL import ImageDraw,ImageFont
JP=ImageFont.truetype('C:/Windows/Fonts/msgothic.ttc',10)
def rail(d,x,y,mask):
 for di,(dx,dy) in enumerate([(0,-1),(1,0),(0,1),(-1,0)]):
  if mask&(1<<di):
   d.line((x+14,y+14,x+14+dx*14,y+14+dy*14),fill=7,width=18)
   d.line((x+14,y+14,x+14+dx*14,y+14+dy*14),fill=5,width=14)
 d.ellipse((x+10,y+10,x+18,y+18),fill=5)
def initial_display_tiles(lv):
 # Static pages and START MAP depict reset state, never the current run.
 tiles=list(lv['terrain'])
 occupied={y*lv.get('width',8)+x for x,y,_ in lv['starts']}
 supports=sum(t==19 for t in tiles)+sum(tiles[p] in (18,30) for p in occupied)
 pressure=supports>0
 for p,t in enumerate(tiles):
  if t==20 and pressure:tiles[p]=22
  elif t==41 and not pressure:tiles[p]=42
  elif t==34:tiles[p]=38
  elif t==43:tiles[p]=44 if supports>=2 else (45 if supports==1 else 43)
  elif p in occupied and t in (18,30):tiles[p]={18:21,30:29}[t]
 return tiles

def board(m,i,lv,offset=0,xoffset=0):
 from port_assets import terrain_tile
 im=m.image((256,256));d=ImageDraw.Draw(im);d.rectangle((0,0,255,211),fill=1)
 d.rectangle((0,0,255,11),fill=0)
 d.text((3,0),f'STAGE {i+1:02} / {len(m.LEVELS):02}',font=m.FONT,fill=6)
 d.text((206,0),'MIN '+str(lv['par']),font=m.FONT,fill=14)
 d.text((120,0),('L' if xoffset==0 else 'R')+(' / TOP' if offset==0 else ' / LOW'),font=m.FONT,fill=6)
 tiles=initial_display_tiles(lv)
 for y in range(6):
  for x in range(8):
   xx=16+x*28;yy=12+y*28;idx=(y+offset)*lv.get('width',8)+x+xoffset;t=tiles[idx] if idx<len(tiles) else 0;mask=lv['tracks'][idx] if idx<len(lv['tracks']) else 0
   if mask:rail(d,xx,yy,mask)
   else:
    d.line((xx+7,yy+17,xx+9,yy+14,xx+11,yy+17),fill=2)
    if (x+y)%3==0:d.ellipse((xx+19,yy+8,xx+21,yy+10),fill=9)
   if t:im.paste(terrain_tile(m.image,t),(xx,yy))
 # A parked blue rocket beside the rabbit's home: decoration only.
 gx,gy=lv['goals'][1]
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]:
  rx,ry=gx+dx,gy+dy
  if not(0<=rx<lv.get('width',8) and 0<=ry<lv.get('height',6)):continue
  index=ry*lv.get('width',8)+rx
  if lv['tracks'][index] or lv['terrain'][index]:continue
  if offset<=ry<offset+6 and xoffset<=rx<xoffset+8:
   xx,yy=16+(rx-xoffset)*28,12+(ry-offset)*28
   d.ellipse((xx+3,yy+23,xx+25,yy+27),fill=0)
   d.polygon([(xx+8,yy+15),(xx+3,yy+24),(xx+10,yy+22)],fill=11)
   d.polygon([(xx+20,yy+15),(xx+25,yy+24),(xx+18,yy+22)],fill=11)
   d.rounded_rectangle((xx+8,yy+8,xx+20,yy+23),radius=3,fill=11,outline=0)
   d.polygon([(xx+8,yy+9),(xx+14,yy+1),(xx+20,yy+9)],fill=12)
   d.line((xx+10,yy+10,xx+10,yy+21),fill=6)
   d.ellipse((xx+11,yy+11,xx+17,yy+17),fill=0,outline=6)
   d.rectangle((xx+11,yy+23,xx+17,yy+25),fill=2)
  break
 for who,(x,y,di) in enumerate(lv['starts']):
  y-=offset;x-=xoffset
  if not(0<=y<6 and 0<=x<8):continue
  xx=16+x*28;yy=12+y*28
  d.ellipse((xx+3,yy+3,xx+25,yy+25),outline=14 if who==0 else 6,width=2)
  dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][di]
  cx=xx+14+dx*10;cy=yy+14+dy*10
  d.polygon([(cx+dx*3,cy+dy*3),(cx-dy*3-dx*2,cy+dx*3-dy*2),(cx+dy*3-dx*2,cy-dx*3-dy*2)],fill=0)
 im.crop((0,0,256,212)).save(m.R/f'outputs/stage-{i+1}-page-{offset//6*2+xoffset//8}.png')
 return m.pack(im)
MESSAGES=[
 ('GUIDE BOTH FRIENDS HOME','CAT PUSHES / RABBIT HOPS'),
 ('WALKING: ENTER PAUSE / ESC RETRY','ARROWS VIEW / F4 FOLLOW / F5 MAP'),
 ('ESC TO TRY AGAIN','TURNS STAY / OBJECTS RESET'),
 ('CLEAR! ENTER: NEXT STAGE',''),('ALL CLEAR! ENTER: REPLAY',''),
 ('USE AS MANY TURNS AS NEEDED',''),('A HINT FOR THIS TILE','UP HINT / DOWN CLEAR'),
 ('PAUSED: ENTER TO CONTINUE','F3 VIEW PAGE / F4 FRIEND / F5 MAP'),
 ('PLACE TURNS / ENTER TO START',''),
 ('EMPTY: KEEP WALKING STRAIGHT','WAIT IF THE WAY IS BLOCKED'),
 ('TURN RIGHT WHEN YOU REACH THIS TILE','BOTH FRIENDS USE THE SAME TURN'),
 ('TURN LEFT WHEN YOU REACH THIS TILE','BOTH FRIENDS USE THE SAME TURN'),
 ('NO WAY FORWARD','ENTER RETRY / ESC TITLE'),
 ('WAIT: PAUSE FOR THE NUMBER OF STEPS','FLIP: CAT CHANGES THE ORANGE ARROWS')]

def status(m):
 out=bytearray()
 for index,(a,b) in enumerate(MESSAGES+[("","")]*(16-len(MESSAGES))):
  im=m.image((256,32));d=ImageDraw.Draw(im);d.rectangle((0,0,255,31),fill=5)
  d.text((3,0),a,font=m.FONT,fill=0);d.text((3,10),b,font=m.FONT,fill=0)
  d.text((3,21),('RETRY KEEPS YOUR TURN TILES' if index==12 else 'SPACE TURN / ENTER GO / F1 HELP'),font=m.FONT,fill=0)
  out.extend(m.pack(im))
 return bytes(out)
def guide(m):
 from port_assets import terrain_tile,character
 im=m.image((256,256));d=ImageDraw.Draw(im);d.rectangle((0,0,255,211),fill=5)
 d.text((8,3),'TWO FRIENDS / F1 OR ESC TO RETURN',font=m.FONT,fill=0)
 for who,y,lines in [(0,24,['CAT: PUSH ONE BOX','FILL A HOLE TO MAKE A BRIDGE']), (1,65,['RABBIT: HOP SMALL HOLES','NEEDS A BRIDGE FOR BIG HOLES'])]:
  c=character(m,who,2,0).resize((32,32));im.paste(c,(8,y),c.point([0]+[255]*255,mode='L'))
  for k,line in enumerate(lines):d.text((45,y+4+k*13),line,font=m.FONT,fill=0)
 for n,(t,line) in enumerate([(2,'HOP: RABBIT CAN CROSS'),(6,'FILL: PUSH A BOX INTO THE HOLE'),(4,'OPEN: UNLOCK SAME-COLOUR GATES'),(18,'PAD: FRIEND OR BOX HOLDS A OPEN')]):
  y=105+n*19;tile=terrain_tile(m.image,t).resize((18,18));im.paste(tile,(7,y));d.text((30,y+4),line,font=m.FONT,fill=0)
 d.text((5,182),'RUN: ARROWS SCROLL / F4 FOLLOW',font=m.FONT,fill=0)
 d.text((5,193),'F5 MAP / F2 PASSWORD / NO TIME LIMIT',font=m.FONT,fill=0)
 im.crop((0,0,256,212)).save(m.R/'outputs/guide.png')
 return m.compressed(m.pack(im))


def overview(m,i,lv):
 from PIL import Image
 from port_assets import character
 im=m.image((256,256));im.paste(5,(0,0,256,256));d=ImageDraw.Draw(im)
 d.text((12,3),f'STAGE {i+1:02} / MAP',font=m.BIG,fill=0)
 left=16 if lv.get('width',8)>8 else 72
 for py in range(2):
  for px in range(2 if lv.get('width',8)>8 else 1):
   board(m,i,lv,py*6,px*8)
   part=Image.open(m.R/f'outputs/stage-{i+1}-page-{py*2+px}.png').crop((16,12,240,180)).resize((112,84),Image.Resampling.NEAREST)
   im.paste(part,(left+px*112,22+py*84))
 for x,y in lv['sockets']:
  d.rectangle((left+x*14,22+y*14,left+x*14+13,35+y*14),outline=14)
 d.text((10,193),'F5 VIEW / ENTER GO-PAUSE',font=m.FONT,fill=0)
 im.crop((0,0,256,212)).save(m.R/f'outputs/map-{i+1}.png')
 return m.pack(im)
