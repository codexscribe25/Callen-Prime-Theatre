"""Generate compact, fixed 1080i Kodi dialog layouts with remote navigation."""
from pathlib import Path
from xml.etree import ElementTree as ET

BASE=Path(__file__).resolve().parents[1]/'addon/plugin.video.callenprime/resources/skins/Default/1080i'
BASE.mkdir(parents=True,exist_ok=True)


def label(id,left,top,width,height,value,size='font13',color='FFEBEBEB',align='left'):
    return f'''<control type="label" id="{id}"><left>{left}</left><top>{top}</top><width>{width}</width><height>{height}</height><font>{size}</font><textcolor>{color}</textcolor><align>{align}</align><label>{value}</label></control>'''

def textbox(id,left,top,width,height,value):
    return f'''<control type="textbox" id="{id}"><left>{left}</left><top>{top}</top><width>{width}</width><height>{height}</height><font>font13</font><textcolor>FFE0E0E0</textcolor><autoscroll delay="5000" time="2500" repeat="5000">false</autoscroll><label>{value}</label></control>'''

def button(id,left,top,width,height,text,left_target,right_target,up_target,down_target):
    return f'''<control type="button" id="{id}"><left>{left}</left><top>{top}</top><width>{width}</width><height>{height}</height><font>font13</font><textcolor>FFB5BEC8</textcolor><focusedcolor>FFFFF0D8</focusedcolor><texturefocus border="12">focus.png</texturefocus><texturenofocus>-</texturenofocus><align>center</align><label>{text}</label><onleft>{left_target}</onleft><onright>{right_target}</onright><onup>{up_target}</onup><ondown>{down_target}</ondown></control>'''

def poster_list(id,top,up,down):
    # Layouts keep Kodi's own selected-item focus handling, with no timed animation.
    def subfocus(focused):
        border='''<control type="image"><left>2</left><top>0</top><width>170</width><height>186</height><texture>focus.png</texture></control>''' if focused else ''
        return f'''<control type="image"><left>12</left><top>6</top><width>149</width><height>174</height><aspectratio align="center">scale</aspectratio><texture fallback="poster-default.jpg">$INFO[ListItem.Art(poster)]</texture></control>{border}<control type="label"><left>6</left><top>185</top><width>165</width><height>23</height><font>font13</font><textcolor>{'FFFFE7C0' if focused else 'FFD4DCE4'}</textcolor><align>center</align><label>$INFO[ListItem.Label]</label></control>'''
    return f'''<control type="list" id="{id}"><left>70</left><top>{top}</top><width>1776</width><height>218</height><orientation>horizontal</orientation><scrolltime>120</scrolltime><pagecontrol>0</pagecontrol><onup>{up}</onup><ondown>{down}</ondown><onleft>{id}</onleft><onright>{id}</onright><itemlayout width="176" height="215">{subfocus(False)}</itemlayout><focusedlayout width="176" height="215">{subfocus(True)}</focusedlayout></control>'''

nav=[('HOME',100),('MOVIES',101),('SERIES',102),('ANIME',103),('MY LIST',104),('SEARCH',105),('SOURCES',106),('SETTINGS',107),('EXIT',108)]
main=['''<?xml version="1.0" encoding="UTF-8"?>
<window type="dialog"><defaultcontrol always="true">100</defaultcontrol><allowoverlay>no</allowoverlay><controls>
<control type="image"><left>0</left><top>0</top><width>1920</width><height>1080</height><texture>background.jpg</texture></control>
<control type="image"><left>1030</left><top>145</top><width>760</width><height>388</height><aspectratio>scale</aspectratio><texture fallback="hero-placeholder.jpg">$INFO[Window.Property(cp.heroart)]</texture></control>
<control type="image"><left>0</left><top>0</top><width>1920</width><height>1080</height><colordiffuse>10000000</colordiffuse><texture>background.jpg</texture></control>
''']
main.append(label(10,70,32,600,65,'CALLEN  PRIME','font16','FFF1C994'))
main.append(label(11,1390,46,460,34,'$INFO[Window.Property(cp.profile)]','font13','FFC2B6A7','right'))
for index,(name,cid) in enumerate(nav):
    x=60+index*194
    main.append(button(cid,x,104,185,50,name,nav[index-1][1] if index else 100,nav[index+1][1] if index<len(nav)-1 else 108,100,120))
main.extend([
    label(20,70,222,1050,63,'$INFO[Window.Property(cp.title)]','font16','FFFAF1DF'),
    label(21,70,288,1040,38,'$INFO[Window.Property(cp.eyebrow)]','font13','FFF1C994'),
    textbox(22,70,333,950,85,'$INFO[Window.Property(cp.plot)]'),
    button(120,70,445,235,62,'DETAILS',120,121,100,301),
    button(121,325,445,275,62,'BROWSE SOURCES',120,121,100,301),
    label(30,70,570,1300,37,'$INFO[Window.Property(cp.row0)]','font14','FFF5EDE2'),
    label(31,70,796,1300,37,'$INFO[Window.Property(cp.row1)]','font14','FFF5EDE2'),
    label(32,1540,575,320,36,'$INFO[Window.Property(cp.page)]','font13','FF99AAB4','right'),
    poster_list(301,607,120,302),
    poster_list(302,832,301,302),
    label(33,1450,36,400,25,'$INFO[Window.Property(cp.mode)]','font13','FF9CB2C4','right'),
    '</controls></window>'
])
(BASE/'CallenPrimeTheatre.xml').write_text('\n'.join(main),encoding='utf-8')

info=['''<?xml version="1.0" encoding="UTF-8"?>
<window type="dialog"><defaultcontrol always="true">501</defaultcontrol><allowoverlay>no</allowoverlay><controls>
<control type="image"><left>0</left><top>0</top><width>1920</width><height>1080</height><texture>background.jpg</texture></control>
<control type="image"><left>1120</left><top>160</top><width>620</width><height>780</height><aspectratio>keep</aspectratio><texture fallback="poster-default.jpg">$INFO[Window.Property(cp.details.art)]</texture></control>''',
    label(490,70,70,1060,80,'CALLEN PRIME  /  DETAILS','font14','FFF1C994'),
    label(491,70,190,1030,90,'$INFO[Window.Property(cp.details.title)]','font16','FFF9E6C5'),
    label(492,70,292,1010,48,'$INFO[Window.Property(cp.details.meta)]','font13','FFDEBB8D'),
    textbox(493,70,365,990,270,'$INFO[Window.Property(cp.details.plot)]'),
    button(501,70,713,315,75,'$INFO[Window.Property(cp.details.play)]',503,502,501,501),
    button(502,407,713,325,75,'$INFO[Window.Property(cp.details.save)]',501,503,502,502),
    button(503,755,713,230,75,'BACK',502,501,503,503),
    label(494,70,897,920,60,'Select PLAY to hand control to Kodi. Press Back to return.','font13','FF98A7B8'),
    '</controls></window>'
]
(BASE/'CallenPrimeDetails.xml').write_text('\n'.join(info),encoding='utf-8')
for path in BASE.glob('*.xml'):
    ET.parse(path)
    print(path.name, 'XML VALID',path.stat().st_size)
