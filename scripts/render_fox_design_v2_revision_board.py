from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v2/retouches-01'
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
bg=(250,249,245);ink=(46,54,58);mute=(102,116,106)
# Side-by-side full character, at comparable character height.
board=Image.new('RGB',(1560,1180),bg);d=ImageDraw.Draw(board)
d.text((55,30),'RENARD / RETOUCHES 01',fill=ink,font=font(42,True));d.text((55,90),'Référence approuvée et proposition Blender corrigée',fill=mute,font=font(25));d.line((55,139,1505,139),fill=(216,220,211),width=2)
ref=Image.open(ROOT/'output/design/renard-expressions-v2-regard.png').convert('RGB').crop((503,140,1017,811));ref=ref.resize((round(ref.width*850/ref.height),850),Image.Resampling.LANCZOS);board.paste(ref,(45+(700-ref.width)//2,195+(850-ref.height)//2))
im=Image.open(OUT/'renard-v2-trois-quarts.png').convert('RGBA');bb=im.getchannel('A').getbbox();im=im.crop((max(0,bb[0]-20),max(0,bb[1]-20),min(im.width,bb[2]+20),min(im.height,bb[3]+20)));im.thumbnail((680,850),Image.Resampling.LANCZOS);board.paste(im,(805+(700-im.width)//2,195+(850-im.height)//2),im)
d.text((80,155),'RÉFÉRENCE VALIDÉE',fill=ink,font=font(24,True));d.text((845,155),'PROPOSITION 3D RETOUCHÉE',fill=ink,font=font(24,True));d.line((780,165,780,1060),fill=(218,221,214),width=2)
d.text((55,1090),'Yeux plus compacts · museau affiné · oreilles redessinées · mains reprises',fill=mute,font=font(23));d.text((55,1125),'Pose de contrôle avec bras relâchés. Apparence à examiner ; modèle sans animation.',fill=mute,font=font(22));board.save(OUT/'renard-v2-comparaison-reference.png')
# Four standard views plus a dedicated hand close-up.
board=Image.new('RGB',(2800,1040),bg);d=ImageDraw.Draw(board);d.text((55,28),'RENARD / RETOUCHES 01',fill=ink,font=font(44,True));d.text((55,92),'Vues de contrôle Blender',fill=mute,font=font(27));d.line((55,150,2745,150),fill=(216,220,211),width=2)
views=[('face','01  FACE'),('profil','02  PROFIL'),('trois-quarts','03  TROIS QUARTS'),('visage','04  VISAGE'),('mains','05  MAIN')];checks={}
for k,(name,label) in enumerate(views):
    im=Image.open(OUT/('renard-v2-'+name+'.png'));checks[name]={'size':list(im.size),'mode':im.mode,'alpha_range':list(im.getchannel('A').getextrema()),'alpha_bbox':list(im.getchannel('A').getbbox())};im.thumbnail((520,690),Image.Resampling.LANCZOS);x=25+k*557;board.paste(im,(x+(520-im.width)//2,182+(690-im.height)//2),im);d.text((x+20,904),label,fill=ink,font=font(25,True))
    if k<4:d.line((x+536,210,x+536,927),fill=(222,224,217),width=1)
d.line((55,954,2745,954),fill=(216,220,211),width=2);d.text((55,980),'Proposition d’apparence · squelette et animations après examen du design',fill=mute,font=font(24));board.save(OUT/'renard-v2-planche.png');(OUT/'verification-images.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps(checks))
