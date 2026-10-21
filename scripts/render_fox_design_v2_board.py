from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v2'
def font(size,bold=False):return ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf',size)
W,H=2400,1040;bg=(249,248,244);board=Image.new('RGB',(W,H),bg);d=ImageDraw.Draw(board)
d.text((64,35),'RENARD / DESIGN V2',fill=(47,54,58),font=font(47,True))
d.text((64,100),'Proposition 3D · revue d’apparence',fill=(98,112,104),font=font(28))
d.line((64,154,W-64,154),fill=(215,219,211),width=2)
views=[('face','01  FACE'),('profil','02  PROFIL'),('trois-quarts','03  TROIS QUARTS'),('visage','04  VISAGE')];checks={}
for k,(name,label) in enumerate(views):
    im=Image.open(OUT/('renard-v2-'+name+'.png'));checks[name]={'size':list(im.size),'mode':im.mode,'alpha_range':list(im.getchannel('A').getextrema()),'alpha_bbox':list(im.getchannel('A').getbbox())};im.thumbnail((548,700),Image.Resampling.LANCZOS)
    x=42+k*588;y=188;board.paste(im,(x+(548-im.width)//2,y+(700-im.height)//2),im)
    d.text((x+22,897),label,fill=(47,54,58),font=font(26,True))
    if k<3:d.line((x+566,205,x+566,925),fill=(225,226,221),width=1)
d.line((64,953,W-64,953),fill=(215,219,211),width=2)
d.text((64,980),'Modèle statique · articulation et animations après revue du design',fill=(104,113,108),font=font(25))
board.save(OUT/'renard-v2-planche.png');(OUT/'verification-images.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(checks))
