"""Player-facing reference sheets: selectable chips and scenery kept apart."""
from PIL import Image,ImageDraw,ImageFont
import build as m
from port_assets import terrain_tile,tool_icon
from presentation import rail
font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',16)
def sheet(items,name):
 im=Image.new('RGB',(640,((len(items)+3)//4)*108),m.P[5]);d=ImageDraw.Draw(im)
 for i,(label,tile) in enumerate(items):
  x=(i%4)*160;y=(i//4)*108
  im.paste(tile.convert('RGB').resize((56,56),Image.Resampling.NEAREST),(x+52,y+8))
  d.text((x+80,y+74),label,font=font,fill=m.P[0],anchor='mt')
 im.save(m.R/'docs/images'/name)
empty=m.image((28,28));ImageDraw.Draw(empty).rectangle((0,0,27,27),fill=1);rail(ImageDraw.Draw(empty),0,0,15)
sheet([('EMPTY',empty)]+[(label,tool_icon(m.image,p,0)) for p,label in [(1,'TURN RIGHT'),(2,'TURN LEFT'),(3,'WAIT 2'),(4,'WAIT 4'),(5,'WAIT 6'),(6,'WAIT 8')]],'player-chips.png')
sheet([(label,terrain_tile(m.image,p)) for p,label in [(1,'PUSH'),(2,'HOP'),(6,'FILL'),(9,'BRIDGE'),(4,'OPEN RED'),(3,'LOCK RED'),(8,'OPEN BLUE'),(7,'LOCK BLUE'),(14,'FLIP'),(15,'ARROW RIGHT'),(17,'ARROW DOWN'),(24,'FIXED ARROW'),(18,'PAD'),(20,'A GATE'),(10,'CAT HOME'),(13,'RABBIT HOME')]],'stage-mechanisms.png')
sheet([(label,terrain_tile(m.image,p)) for p,label in [(32,'SWAP'),(33,'I GATE'),(38,'II GATE'),(35,'WEAK'),(39,'ONCE'),(40,'USED'),(41,'!A CLOSED'),(42,'!A OPEN'),(43,'2A CLOSED'),(44,'2A OPEN')]],'new-mechanisms.png')
