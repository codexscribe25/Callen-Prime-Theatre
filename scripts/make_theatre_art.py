"""Generate original lightweight theatre textures (no external art or fonts shipped)."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'addon/plugin.video.callenprime/resources/skins/Default/media'
AD = ROOT / 'addon/plugin.video.callenprime/resources'
MEDIA.mkdir(parents=True, exist_ok=True)

def font(size, bold=False):
    options = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'] if bold else [
                   '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for name in options:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def atmosphere(size=(1920,1080)):
    w,h=size
    im=Image.new('RGB',size)
    pix=im.load()
    # restrained dark petrol with auburn light, fully generated in-project
    for y in range(h):
        for x in range(w):
            u,v=x/w,y/h
            gl=math.exp(-(((u-.84)/.30)**2+((v-.30)/.42)**2)*1.4)
            gl2=math.exp(-(((u-.33)/.4)**2+((v-.90)/.40)**2)*1.8)
            pix[x,y]=(int(6+32*gl+5*gl2),int(12+23*gl+7*gl2),int(22+20*gl+11*gl2))
    d=ImageDraw.Draw(im,'RGBA')
    for index in range(8):
        cx=1390+100*math.sin(index*1.7)
        cy=420+30*math.sin(index*2.2)
        r=210+index*40
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(220,152,75,13),width=2)
    return im

bg=atmosphere();bg.save(MEDIA/'background.jpg',quality=86,optimize=True)
hero=atmosphere((1280,720))
ImageDraw.Draw(hero,'RGBA').polygon([(530,720),(960,20),(1240,85),(1000,720)], fill=(209,134,75,52))
hero.save(MEDIA/'hero-placeholder.jpg',quality=86,optimize=True)

focus=Image.new('RGBA',(320,470),(0,0,0,0));dr=ImageDraw.Draw(focus)
dr.rounded_rectangle((3,3,317,466),radius=14,outline=(244,200,133,255),width=8)
focus.save(MEDIA/'focus.png')

def poster(title,subtitle,index):
    w,h=300,450
    palettes=[((20,49,65),(7,22,34),(226,162,104)),
              ((62,30,52),(15,15,34),(217,163,116)),
              ((31,55,39),(10,25,32),(171,206,165)),
              ((45,41,67),(9,18,36),(148,184,233)),
              ((73,52,30),(24,21,23),(219,185,115))]
    start,end,accent=palettes[index%len(palettes)]
    im=Image.new('RGB',(w,h));p=im.load()
    for y in range(h):
        for x in range(w):
            s=y/h
            q=0.10*math.sin((x+y)*.026)
            p[x,y]=tuple(int(max(0,min(255,start[i]*(1-s)+end[i]*s+q*35))) for i in range(3))
    d=ImageDraw.Draw(im,'RGBA')
    for j in range(8):
        cx=200+int(50*math.sin(j*1.8+index))
        cy=177+int(26*math.cos(j))
        r=67+j*18
        d.arc((cx-r,cy-r,cx+r,cy+r),210,480,fill=(*accent,30),width=3)
    d.rectangle((27,303,272,306), fill=(*accent,160))
    d.text((27,328),title,font=font(28,True),fill=(244,239,229),stroke_width=0)
    d.text((27,375),subtitle,font=font(15),fill=(*accent,255))
    return im

posters=[('UMBRELLA','YOUR CONNECTED SOURCES'),('FEN','YOUR CONNECTED SOURCES'),
         ('SEREN','YOUR CONNECTED SOURCES'),('MY LIBRARY','YOUR SAVED COLLECTION'),
         ('NO POSTER','CALLEN PRIME THEATRE')]
for i,(t,s) in enumerate(posters):
    filename=['poster-umbrella.jpg','poster-fen.jpg','poster-seren.jpg',
              'poster-library.jpg','poster-default.jpg'][i]
    poster(t,s,i).save(MEDIA/filename,quality=84,optimize=True)

icon=Image.new('RGB',(512,512),(8,20,31));d=ImageDraw.Draw(icon)
d.rounded_rectangle((42,42,470,470),radius=115,outline=(221,177,116),width=12)
d.text((90,155),'CP',font=font(156,True),fill=(238,218,179))
d.text((125,354),'THEATRE',font=font(31,True),fill=(221,177,116))
icon.save(AD/'icon.png',optimize=True)
bg.resize((1280,720),Image.Resampling.LANCZOS).save(AD/'fanart.jpg',quality=85,optimize=True)
print('Created', len(list(MEDIA.glob('*'))), 'theatre textures')
