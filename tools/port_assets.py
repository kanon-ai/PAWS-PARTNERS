from pixel_font import FONT as PIXEL_FONT
from PIL import Image,ImageDraw,ImageFont

def terrain_tile(image,c):
 im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1)
 if c>=32:
  font=PIXEL_FONT
  if c in (43,44,45,46,47):
   d.rectangle((2,2,5,26),fill=12);d.rectangle((22,2,25,26),fill=12)
   d.text((7,1),'2A',font=font,fill=6)
   lamps={43:0,44:2,45:1,46:0,47:1}[c]
   for i,x in enumerate((8,16)):d.rectangle((x,11,x+4,15),fill=14 if i<lamps else 0,outline=6 if i<lamps else 2)
   if c in (43,45):
    for y in (19,24):d.rectangle((4,y,23,y+1),fill=12)
  elif c in (41,42):
   d.rectangle((2,2,5,26),fill=12);d.rectangle((22,2,25,26),fill=12)
   d.text((6,1),'!A',font=font,fill=6)
   d.ellipse((11,10,17,16),outline=6)
   if c==41:
    for y in (19,24):d.rectangle((4,y,23,y+1),fill=12)
  elif c in (39,40):
   d.rounded_rectangle((1,1,26,26),radius=4,fill=14 if c==39 else 2,outline=6)
   d.text((2,1),'ONCE' if c==39 else 'USED',font=font,fill=0 if c==39 else 6)
   d.ellipse((8,12,20,24),fill=0 if c==39 else 1,outline=6)
   if c==39:d.text((12,12),'1',font=font,fill=6)
   else:d.line((10,18,14,22,21,14),fill=6,width=2)
  elif c in (32,36):
   d.rounded_rectangle((1,1,26,26),radius=4,fill=10,outline=6)
   d.text((3,1),'SWAP',font=font,fill=6)
   d.rectangle((4,14,11,22),fill=14 if c==36 else 0)
   d.rectangle((17,14,24,22),fill=0 if c==36 else 14)
   d.line((8,11,20,11),fill=6);d.point((19,10),fill=6)
  elif c==35:
   d.rectangle((1,2,26,25),fill=7,outline=6)
   for y in (7,14,21):d.line((2,y,25,y),fill=0)
   d.line((15,2,10,10,17,15,12,25),fill=9,width=2)
   d.text((2,1),'WEAK',font=font,fill=0)
  elif c in (33,34,37,38):
   d.rectangle((2,1,5,26),fill=10);d.rectangle((22,1,25,26),fill=10)
   if c in (33,34):
    for y in (11,18,24):d.rectangle((4,y,23,y+1),fill=14)
   d.text((9,1),'I' if c in (33,37) else 'II',font=font,fill=6)
  return im
 if c>=18:
  font=PIXEL_FONT
  if c in (18,19,21,29,30):
   pressed=c in (19,21,29)
   d.rectangle((1,17,26,26),fill=0)
   d.rectangle((2,15 if pressed else 11,25,23),fill=12 if pressed else 3,outline=6)
   d.text((4,16 if pressed else 12),'PAD',font=font,fill=0)
   d.rectangle((1,1,7,7),fill=12 if pressed else 0,outline=6)
   if c==19:
    d.rectangle((5,2,23,17),fill=7,outline=0)
    d.line((7,4,21,15),fill=8,width=2);d.line((7,15,21,4),fill=8,width=2)
  elif c in (20,22,28):
   col=12 if c!=28 else 11
   d.rectangle((2,2,5,25),fill=col);d.rectangle((22,2,25,25),fill=col)
   if c!=22:
    for y in (10,17,24):d.rectangle((3,y,24,y+1),fill=col)
   d.text((8,1),'A' if c!=28 else 'B',font=font,fill=6)
  elif c==31:
   d.ellipse((3,3,24,22),fill=11,outline=6);d.text((7,3),'B',font=font,fill=0)
  direction=c-23 if 23<=c<=26 else (2 if c==28 else (1 if c in (29,30,31) else None))
  if direction is not None:
   if 23<=c<=26:
    # A paved junction with a painted arrow, rather than an arrow in empty grass.
    d.rounded_rectangle((0,0,27,27),radius=4,fill=5,outline=7)
   dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][direction]
   cx,cy=(14,14) if 23<=c<=26 else ((14,8) if c in (29,30) else (14,17))
   ink=1 if 23<=c<=26 else 6
   d.line((cx-dx*5,cy-dy*5,cx+dx*5,cy+dy*5),fill=ink,width=2)
   d.polygon([(cx+dx*7,cy+dy*7),(cx+dx*2-dy*4,cy+dy*2+dx*4),(cx+dx*2+dy*4,cy+dy*2-dx*4)],fill=ink)
  return im
 if c in (10,13):
  col=7 if c==10 else 11
  d.rectangle((4,11,23,25),fill=5,outline=col,width=2)
  d.polygon([(1,12),(14,2),(26,12)],fill=col)
  d.rounded_rectangle((10,16,17,25),radius=3,fill=0)
  # White roof emblems: pointed cat ears and tall separated rabbit ears.
  if c==10:
   d.polygon([(9,5),(12,7),(15,7),(18,5),(18,10),(16,12),(11,12),(9,10)],fill=6)
  else:
   d.rectangle((11,4,12,9),fill=6)
   d.rectangle((16,4,17,9),fill=6)
   d.ellipse((11,8,17,12),fill=6)
 elif c==1:
  d.rectangle((3,3,24,24),fill=7,outline=0,width=2)
  d.line((5,5,22,22),fill=8,width=3);d.line((5,22,22,5),fill=8,width=3)
 elif c in (2,6):
  if c==2:
   d.rounded_rectangle((7,1,20,26),radius=3,fill=0,outline=11)
   d.line((2,4,5,4),fill=5,width=3);d.line((22,23,25,23),fill=5,width=3)
  else:
   d.rectangle((1,1,26,26),fill=0,outline=9,width=2)
   d.line((3,6,24,6),fill=11);d.line((3,20,24,20),fill=11)
 elif c in (3,7):
  col=8 if c==3 else 11
  d.rectangle((2,3,25,25),fill=5)
  for x in (4,11,18):d.rectangle((x,4,x+3,24),fill=col)
  d.rectangle((3,9,24,12),fill=col)
 elif c in (4,8,11,12):
  col=8 if c in (4,11) else 11
  d.rectangle((0,0,27,27),fill=5)
  d.ellipse((4,8,24,24),fill=0)
  d.ellipse((4,5 if c<10 else 12,24,21),fill=col if c<10 else 13,outline=6)
 elif c in (14,16):
  d.rectangle((1,1,26,26),fill=7,outline=6)
  d.polygon([(7,7),(7,2),(11,5),(17,5),(21,2),(21,9)],fill=1)
  d.line((7,20,20 if c==16 else 7,12),fill=6,width=3)
  d.text((3,19),'FLIP',font=PIXEL_FONT,fill=1)
 elif c in (15,17):
  d.rectangle((1,1,26,26),fill=7,outline=6)
  if c==15:
   d.line((5,15,22,15),fill=1,width=3);d.polygon([(23,15),(16,9),(16,21)],fill=1)
  else:
   d.line((14,6,14,23),fill=1,width=3);d.polygon([(14,24),(8,17),(20,17)],fill=1)
 elif c==5:
  d.rounded_rectangle((2,3,25,26),radius=6,fill=2,outline=0)
  d.line((5,6,18,6),fill=3,width=2)
 elif c==9:
  d.rectangle((0,0,27,27),fill=0)
  for y in range(1,28,6):d.rectangle((1,y,26,y+4),fill=7,outline=5)
 # Short labels reinforce the physical shape without replacing it.
 labels={1:'PUSH',2:'HOP',6:'FILL',3:'LOCK',7:'LOCK',4:'OPEN',8:'OPEN',11:'OPEN',12:'OPEN'}
 if c in labels:
  font=PIXEL_FONT
  d.rectangle((3,1,24,8),fill=5)
  d.text((4,0),labels[c],font=font,fill=1)
 return im

def tool_icon(image,part,facing=0,compact=False):
 im=image((24,24));d=ImageDraw.Draw(im)
 if part>=3:
  d.rounded_rectangle((1,1,22,23),radius=4,fill=11,outline=6)
  font=PIXEL_FONT
  d.text((0,1),'WAIT',font=font,fill=1)
  shift=3 if compact else 0
  d.ellipse((3,10-shift,13,20-shift),outline=1);d.line((8,12-shift,8,15-shift,11,15-shift),fill=1)
  d.text((15,12-shift),str((part-2)*2),font=font,fill=1)
  return im
 if part:
  d.rounded_rectangle((1,1,22,23),radius=4,fill=14 if part==1 else 8,outline=6)
  # Keep the English label upright; rotate only the lower direction diagram.
  font=PIXEL_FONT
  d.text((0,1),'TURN',font=font,fill=1)
  arrow=image((12,12));ad=ImageDraw.Draw(arrow)
  # Separate the shaft, elbow and arrowhead on an integer pixel grid.
  ad.rectangle((5,6,6,11),fill=15)
  if part==1:
   ad.rectangle((5,5,8,6),fill=15)
   ad.polygon([(11,5),(8,2),(8,8)],fill=15)
  else:
   ad.rectangle((3,5,6,6),fill=15)
   ad.polygon([(0,5),(3,2),(3,8)],fill=15)
  arrow=arrow.rotate(-90*facing)
  mask=arrow.point([0]+[255]*255,mode='L')
  ink=image((12,12));ImageDraw.Draw(ink).rectangle((0,0,11,11),fill=1)
  im.paste(ink,(6,8 if compact else 11),mask)
 return im

def character(m,who,direction,phase):
 im=m.image((16,16));d=ImageDraw.Draw(im)
 body=7 if who==0 else 6;accent=12 if who==0 else 11
 # Round, original toy characters: pointed cat ears vs tall rabbit ears.
 if who==0:
  d.polygon([(2,6),(2,1),(6,4),(10,4),(13,1),(13,7)],fill=body)
 else:
  d.rounded_rectangle((3,0,6,6),radius=1,fill=body)
  d.rounded_rectangle((9,0,12,6),radius=1,fill=body)
 d.ellipse((2,4,13,12),fill=body)
 d.rounded_rectangle((4,10,12,14),radius=2,fill=accent)
 if direction!=0:
  if direction==1:eyes=[10,13]
  elif direction==3:eyes=[2,5]
  else:eyes=[5,10]
  for x in eyes:d.point((x,7),fill=1)
  d.point((11 if direction==1 else 3 if direction==3 else 7,9),fill=1)
  if who==0:d.line((5,10,10,10),fill=6)
 for x,y in [(4,14+phase),(10,15-phase)]:d.rectangle((x,y,x+2,y),fill=body)
 if who==0:d.line((3,12,1,10,0,11),fill=body)
 return im

def generate(m):
 from presentation import rail
 R=m.R;pack=m.pack;image=m.image
 results=bytearray()
 for title,lines,color in [('CLEAR!', ['ENTER: NEXT','ESC: RETRY'],13),('NO WAY', ['ENTER: RETRY','ESC: TITLE'],8)]:
  im=image((128,64));d=ImageDraw.Draw(im)
  d.rectangle((0,0,127,63),fill=0,outline=6,width=2)
  d.rectangle((4,4,123,23),fill=color)
  label=Image.new('L',(len(title)*6-1,7),0)
  ImageDraw.Draw(label).text((0,0),title,font=PIXEL_FONT,fill=255)
  label=label.resize((label.width*2,14),Image.Resampling.NEAREST)
  im.paste(0,((128-label.width)//2,7),label)
  for i,line in enumerate(lines):d.text(((128-(len(line)*6-1))//2,29+i*10),line,font=PIXEL_FONT,fill=6)
  results.extend(pack(im))
 (R/'assets/results.bin').write_bytes(results)
 tiles=bytearray()
 for facing in range(4):
  for selected in range(2):
   for part in range(8):
    im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1);rail(d,0,0,15)
    if part in range(1,7):
     icon=tool_icon(image,part,facing);im.paste(icon,(2,2),icon.point([0]+[255]*255,mode='L'))
    if selected:
     for x,y,sx,sy in [(0,0,1,1),(27,0,-1,1),(0,27,1,-1),(27,27,-1,-1)]:d.line((x+sx*6,y,x,y,x,y+sy*6),fill=15,width=2)
    tiles.extend(pack(im).ljust(512,b'\0'))
 (R/'assets/tiles.bin').write_bytes(tiles)
 mini=bytearray()
 for facing in range(4):
  for selected in range(2):
   for part in range(8):
    im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1);rail(d,0,0,15)
    if part in range(1,7):
     icon=tool_icon(image,part,facing,compact=True);im.paste(icon,(2,0),icon.point([0]+[255]*255,mode='L'))
    im=im.resize((14,14),Image.Resampling.NEAREST)
    if selected:ImageDraw.Draw(im).rectangle((0,0,13,9),outline=15)
    mini.extend(pack(im).ljust(128,b'\0'))
 for code in range(64):
  badge=mechanism_badge(image,code).resize((14,4),Image.Resampling.NEAREST)
  mini.extend(pack(badge).ljust(32,b'\0'))
 (R/'assets/map-tiles.bin').write_bytes(mini.ljust(16384,b'\0'))

 # Compact chips reserve their lower eight pixels for the underlying floor.
 special=bytearray()
 for facing in range(4):
  for selected in range(2):
   for part in range(8):
    im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1);rail(d,0,0,15)
    if part in range(1,7):
     icon=tool_icon(image,part,facing,compact=True);im.paste(icon,(2,0),icon.point([0]+[255]*255,mode='L'))
    if selected:
     for x,y,sx,sy in [(0,0,1,1),(27,0,-1,1)]:d.line((x+sx*6,y,x,y,x,y+sy*6),fill=15,width=2)
    special.extend(pack(im).ljust(512,b'\0'))
 (R/'assets/special-tiles.bin').write_bytes(special)
 badges=bytearray()
 for code in range(64):
  badges.extend(pack(mechanism_badge(image,code)).ljust(128,b'\0'))
 (R/'assets/socket-badges.bin').write_bytes(badges)
 (R/'assets/gates.bin').write_bytes(bytes(8192))
 popup=image((128,112));d=ImageDraw.Draw(popup);d.rounded_rectangle((0,0,127,111),radius=8,fill=5,outline=7,width=2)
 d.text((14,5),'TOGETHER!',font=m.BIG,fill=0)
 for who,x in [(0,9),(1,69)]:
  c=character(m,who,2,0).resize((48,48),Image.Resampling.NEAREST);popup.paste(c,(x,34),c.point([0]+[255]*255,mode='L'))
 d.text((20,92),'THANK YOU!',font=m.FONT,fill=0)
 popup.save(R/'assets/celebration.png');(R/'assets/popup.bin').write_bytes(pack(popup).ljust(8192,b'\0'))
 (R/'assets/terrain.bin').write_bytes(b''.join(pack(terrain_tile(image,c)).ljust(512,b'\0') for c in range(48)))
 (R/'assets/rails.bin').write_bytes(bytes(8192))
 floors=bytearray()
 for mask in range(16):
  im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1);rail(d,0,0,mask);floors.extend(pack(im).ljust(512,b'\0'))
 (R/'assets/floors.bin').write_bytes(floors)
 patterns=bytearray();colors=bytearray()
 sheet=image((128,64))
 for who,palette in [(0,[1,7,6,12]),(1,[1,6,11,9])]:
  for direction in range(4):
   for phase in range(2):
    im=character(m,who,direction,phase);sheet.paste(im,(direction*32+phase*16,who*32))
    for color in palette:
     for half in range(2):
      for y in range(16):patterns.append(sum(1<<(7-x) for x in range(8) if im.getpixel((half*8+x,y))==color))
  for color in palette:colors.extend([color]*16)
 assert len(patterns)==2048 and len(colors)==128
 sheet.resize((512,256),Image.Resampling.NEAREST).save(R/'outputs/characters.png')
 (R/'assets/sprite2.inc').write_text('sprite_patterns:\n db '+','.join(map(str,patterns))+'\nsprite_colors:\n db '+','.join(map(str,colors))+'\n')
 (R/'assets/palettes.inc').write_text('initial_palette:\n db '+','.join(str(n) for r,g,b in m.P for n in [(round(r*7/255)<<4)|round(b*7/255),round(g*7/255)])+'\n')


def mechanism_badge(image,code):
 """An icon plus identity/state; never replace a mechanism with a chip alone."""
 im=image((28,8));d=ImageDraw.Draw(im);d.rectangle((0,0,27,7),fill=0)
 if not code:return im
 font=PIXEL_FONT
 labels={1:'BOX',2:'HOP',3:'R',4:'R',5:'ROCK',6:'FILL',7:'B',8:'B',9:'BRG',10:'CAT',11:'R',12:'B',13:'RAB',14:'FLP',15:'FIX',16:'FLP',17:'FIX',18:'PAD',19:'PAD',20:'A',21:'PAD',22:'A',23:'FIX',24:'FIX',25:'FIX',26:'FIX',28:'B',29:'PAD',30:'PAD',31:'B',32:'II',33:'I',34:'II',35:'WEAK',36:'I',37:'I',38:'II',39:'ONE',40:'USED',41:'!A',42:'!A',43:'2A',44:'2A',45:'2A',46:'2A',47:'2A',48:'R',49:'B'}
 label=labels.get(code,'?')
 label={'ROCK':'ROK','FILL':'GAP','WEAK':'WEK','USED':'OFF'}.get(label,label)
 d.text((11,0),label,font=font,fill=6)
 if code in (1,19):
  d.rectangle((1,0,9,5 if code==19 else 7),fill=7,outline=6)
  d.line((2,1,8,4 if code==19 else 6),fill=8);d.line((8,1,2,4 if code==19 else 6),fill=8)
  if code==19:d.line((0,7,10,7),fill=12);d.point((0,6),fill=12)
 elif code in (3,7,20,22,28,33,34,37,38,41,42,43,44,45,46,47,48,49):
  col=8 if code in (3,48) else (11 if code in (7,28,49) else (10 if code in (33,34,37,38) else 12))
  d.line((1,1,1,7),fill=col);d.line((9,1,9,7),fill=col)
  if code in (3,7,20,28,33,34,41,43,45):
   d.line((1,3,9,3),fill=col);d.line((1,6,9,6),fill=col)
  if code in (43,44,45,46,47):
   n={43:0,44:2,45:1,46:0,47:1}[code]
   for i in range(2):d.rectangle((3+i*3,0,4+i*3,1),fill=14 if i<n else 2)
 elif code in (4,8,11,12,31):
  col=8 if code in (4,11) else 11;pressed=code in (11,12)
  d.ellipse((1,3 if pressed else 0,9,7),fill=13 if pressed else col,outline=6)
 elif code in (18,21,29,30):
  pressed=code in (21,29);d.rectangle((1,3,9,7),fill=12 if pressed else 2,outline=6);d.rectangle((1,0,3,1),fill=12 if pressed else 2)
  if code in (29,30):d.line((5,1,9,1),fill=6);d.point((8,0),fill=6);d.point((8,2),fill=6)
 elif code in (10,13):
  col=7 if code==10 else 11;d.polygon([(0,4),(5,0),(10,4)],fill=col);d.rectangle((2,4,8,7),fill=5);d.rectangle((4,5,6,7),fill=0)
 elif code in (15,17,23,24,25,26):
  dx,dy={15:(1,0),17:(0,1),23:(0,-1),24:(1,0),25:(0,1),26:(-1,0)}[code]
  d.line((5-dx*3,4-dy*3,5+dx*3,4+dy*3),fill=6)
  d.polygon([(5+dx*4,4+dy*3),(5-dy*2,4+dx*2),(5+dy*2,4-dx*2)],fill=6)
 elif code in (32,36):
  d.rectangle((0,1,4,6),fill=14 if code==36 else 2);d.rectangle((6,1,10,6),fill=14 if code==32 else 2)
 elif code in (2,6):
  d.rectangle((2,0,8,7),outline=11 if code==2 else 9);d.line((3,6,7,6),fill=11)
 elif code==9:
  for y in (0,3,6):d.rectangle((1,y,9,y+1),fill=7)
 elif code in (39,40):
  d.ellipse((1,0,9,7),fill=14 if code==39 else 2)
  if code==40:d.line((2,4,4,6,8,1),fill=6)
  else:d.line((5,1,5,6),fill=0)
 elif code in (14,16):
  d.rectangle((1,0,9,7),fill=7);d.line((3,6,7 if code==16 else 3,2),fill=0,width=2)
 elif code==35:
  d.rectangle((1,0,9,7),fill=7);d.line((5,0,3,3,7,4,4,7),fill=9)
 else:d.rectangle((1,1,9,6),fill=2,outline=6)
 return im
