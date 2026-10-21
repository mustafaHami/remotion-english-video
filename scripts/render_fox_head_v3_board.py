from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v3'
def f(s,b=False):return ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',s)
board=Image.new('RGB',(2000,970),(250,249,245));d=ImageDraw.Draw(board)
d.text((55,32),'RENARD / ÉTUDE DE TÊTE V3',font=f(44,True),fill=(46,54,58));d.text((55,96),'Reprise du regard, des oreilles et des découpes de joue',font=f(26),fill=(103,116,106));d.line((55,148,1945,148),fill=(217,220,214),width=2)
d.text((90,175),'RÉFÉRENCE APPROUVÉE',font=f(25,True),fill=(46,54,58));d.text((1090,175),'ÉTUDE BLENDER — NON VALIDÉE',font=f(25,True),fill=(46,54,58))
ref=Image.open(ROOT/'output/design/renard-expressions-v2-regard.png').convert('RGB').crop((700,145,905,306));ref=ref.resize((round(ref.width*610/ref.height),610),Image.Resampling.LANCZOS);board.paste(ref,(30+(940-ref.width)//2,245))
im=Image.open(OUT/'renard-v3-tete-trois-quarts.png').convert('RGBA').crop((100,90,995,870));im=im.resize((round(im.width*610/im.height),610),Image.Resampling.LANCZOS);board.paste(im,(1030+(940-im.width)//2,245),im)
d.line((1000,175,1000,890),fill=(219,222,215),width=2);d.line((55,896,1945,896),fill=(217,220,214),width=2);d.text((55,921),'Oreilles raccourcies · yeux sans disques rapportés · petites découpes de joue · rendu mat',font=f(24),fill=(103,116,106));board.save(OUT/'renard-v3-comparaison-tete.png')
# All three head angles, deliberately avoiding a claim of final character approval.
board=Image.new('RGB',(2400,1000),(250,249,245));d=ImageDraw.Draw(board);d.text((55,28),'RENARD / TÊTE V3 — VUES DE CONTRÔLE',font=f(42,True),fill=(46,54,58));d.line((55,120,2345,120),fill=(217,220,214),width=2)
for i,(name,label) in enumerate([('face','FACE'),('trois-quarts','TROIS QUARTS'),('profil','PROFIL')]):
    im=Image.open(OUT/('renard-v3-tete-'+name+'.png')).convert('RGBA');im=im.resize((740,740),Image.Resampling.LANCZOS);board.paste(im,(30+i*800,150),im);d.text((65+i*800,920),label,font=f(26,True),fill=(46,54,58))
board.save(OUT/'renard-v3-tete-planche.png')
import json
checks={}
for name in ['renard-v3-tete-trois-quarts.png','renard-v3-tete-face.png','renard-v3-tete-profil.png','renard-v3-contexte.png']:
    im=Image.open(OUT/name);checks[name]={'size':list(im.size),'mode':im.mode,'alpha_range':list(im.getchannel('A').getextrema()),'alpha_bbox':list(im.getchannel('A').getbbox())}
(OUT/'verification-images.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
print('BOARD_COMPLETE',json.dumps(checks))
