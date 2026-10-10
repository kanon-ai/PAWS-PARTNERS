from PIL import Image,ImageDraw,ImageFont

def terrain_tile(image,c):
 im=image((28,28));d=ImageDraw.Draw(im);d.rectangle((0,0,27,27),fill=1)
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
  d.text((3,19),'FLIP',font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',8),fill=1)
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
  font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',8)
  d.rectangle((3,1,24,8),fill=5)
  d.text((4,0),labels[c],font=font,fill=1)
 return im

def tool_icon(image,part,facing=0):
 im=image((24,24));d=ImageDraw.Draw(im)
 if part>=3:
  d.rounded_rectangle((1,1,22,23),radius=4,fill=11,outline=6)
  font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',8)
  d.text((2,1),'WAIT',font=font,fill=1)
  d.ellipse((3,10,13,20),outline=1);d.line((8,12,8,15,11,15),fill=1)
  d.text((15,12),str((part-2)*2),font=font,fill=1)
  return im
 if part:
  d.rounded_rectangle((1,1,22,23),radius=4,fill=14 if part==1 else 8,outline=6)
  # Keep the English label upright; rotate only the lower direction diagram.
  font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',8)
  d.text((2,1),'TURN',font=font,fill=1)
  arrow=image((12,12));ad=ImageDraw.Draw(arrow)
  ad.line((5,11,5,5,10 if part==1 else 0,5),fill=15,width=2)
  ad.polygon([(10,5),(7,2),(7,8)] if part==1 else [(0,5),(3,2),(3,8)],fill=15)
  arrow=arrow.rotate(-90*facing)
  mask=arrow.point([0]+[255]*255,mode='L')
  ink=image((12,12));ImageDraw.Draw(ink).rectangle((0,0,11,11),fill=1)
  im.paste(ink,(6,11),mask)
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
 (R/'assets/gates.bin').write_bytes(bytes(8192))
 popup=image((128,112));d=ImageDraw.Draw(popup);d.rounded_rectangle((0,0,127,111),radius=8,fill=5,outline=7,width=2)
 d.text((14,5),'TOGETHER!',font=m.BIG,fill=0)
 for who,x in [(0,9),(1,69)]:
  c=character(m,who,2,0).resize((48,48),Image.Resampling.NEAREST);popup.paste(c,(x,34),c.point([0]+[255]*255,mode='L'))
 d.text((20,92),'THANK YOU!',font=m.FONT,fill=0)
 popup.save(R/'assets/celebration.png');(R/'assets/popup.bin').write_bytes(pack(popup).ljust(8192,b'\0'))
 (R/'assets/terrain.bin').write_bytes(b''.join(pack(terrain_tile(image,c)).ljust(512,b'\0') for c in range(18)).ljust(16384,b'\0'))
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
