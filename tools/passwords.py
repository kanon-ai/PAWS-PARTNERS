"""Persistent, non-secret passphrases. Never derive them from the stage number."""
import json, random
from PIL import ImageDraw, ImageFont

WORDS = 'MINT MOON PEAR FERN LIME WAVE PLUM SNOW STAR SAND RAIN PINE SILK JADE LILY GOLD DUSK DAWN LEAF ROSE BLUE RUBY HAZE BELL REED LAKE WIND CORN SAGE IRIS DEER WREN'.split()

def generate(m):
    path = m.R/'assets/passwords.json'
    if path.exists():
        codes = json.loads(path.read_text())
    else:
        # Persist once: rebuilding must not invalidate players' saved passwords.
        pairs = [a+' '+b for a in WORDS for b in WORDS if a != b]
        codes = random.SystemRandom().sample(pairs, 50)
        path.write_text(json.dumps(codes, indent=2)+'\n')
    assert len(codes) >= len(m.LEVELS)
    assert len(set(codes)) == len(codes)
    assert all(len(c)==9 and c[4]==' ' and c.replace(' ','').isalpha() for c in codes)
    inc = 'password_table:\n'+''.join(' db "'+c.replace(' ','')+'"\n' for c in codes[:len(m.LEVELS)])
    font=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',10)
    inc+='password_font:\n'
    for char in ' ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789':
        im=m.image((8,8));im.paste(5,(0,0,8,8))
        ImageDraw.Draw(im).text((1,-2),char,font=font,fill=0)
        inc+=' db '+','.join(map(str,m.pack(im)))+'\n'
    (m.R/'assets/passwords.inc').write_text(inc)
    im=m.image((256,256));d=ImageDraw.Draw(im)
    d.rectangle((0,0,255,255),fill=5)
    from PIL import Image
    from port_assets import character
    # Reuse the in-game characters; keep the password fields at their RAM UI coordinates.
    d.rounded_rectangle((5,4,250,96),radius=14,fill=4)
    d.rounded_rectangle((9,7,246,93),radius=12,outline=3,width=2)
    title=ImageFont.truetype('C:/Windows/Fonts/consolab.ttf',20)
    for x,who in [(34,0),(174,1)]:
        d.ellipse((x+2,85,x+46,93),fill=3)
        sprite=character(m,who,2,0).resize((48,48),Image.Resampling.NEAREST)
        im.paste(sprite,(x,43),sprite.point([0]+[255]*255,mode='L'))
    d.line((86,82,167,82),fill=7,width=3)
    for x in range(90,165,12):d.line((x,79,x,85),fill=7)
    d.polygon([(119,59),(119,54),(123,51),(128,55),(133,51),(137,54),(137,59),(128,68)],fill=8)
    for x,y in [(20,62),(235,61),(21,83),(235,84)]:
        d.line((x,y,x,y+6),fill=2)
        d.ellipse((x-3,y-3,x+3,y+2),fill=14)
        d.point((x,y),fill=6)
    d.rounded_rectangle((77,116,178,146),radius=5,outline=3,width=2)
    for y,text,font in [(9,'PAWS PARTNERS',title),(32,'TWO FRIENDS / ONE ADVENTURE',m.FONT),(108,'PASSWORD',m.FONT),(150,'ENTER: NEW GAME / START',m.FONT),(166,'ARROWS: LETTER / POSITION',m.FONT),(180,'SPACE: NEXT LETTER',m.FONT),(197,'ESC: BACK   F2: PASSWORD',m.FONT)]:
        width=d.textbbox((0,0),text,font=font)[2]
        d.text(((256-width)//2,y),text,font=font,fill=0)
    im.crop((0,0,256,212)).save(m.R/'outputs/password-screen.png')
    (m.R/'assets/password-screen.bin').write_bytes(m.compressed(m.pack(im)))
