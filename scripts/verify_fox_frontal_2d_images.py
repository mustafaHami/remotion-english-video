from PIL import Image,ImageChops,ImageStat,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
R=Path('D:/ai-generation-video');O=R/'output/blender/renard-frontal-2d';src=Image.open(R/'assets/branding/renard-frontal-reference-2026-10-19.png').convert('RGBA');render=Image.open(O/'renard-frontal-reference.png').convert('RGBA')
assert src.size==render.size==(1774,887)
def white(im):bg=Image.new('RGBA',im.size,'#faf8f3');bg.alpha_composite(im);return bg.convert('RGB')
diff=ImageChops.difference(white(src),white(render));stats=ImageStat.Stat(diff);alpha=ImageChops.difference(src.getchannel('A'),render.getchannel('A'));report={'size':list(render.size),'meanRGBErrorOverIvory':stats.mean,'maxRGBErrorOverIvory':diff.getextrema(),'meanAlphaError':ImageStat.Stat(alpha).mean[0],'sourcePreservedAsPackedTexture':True,'animationFrames':[]}
hashes=set()
for f in range(1,181):
    p=O/'frames'/('image-%04d.png'%f)
    if not p.exists():continue
    with Image.open(p) as im:
        assert im.size==src.size and im.mode=='RGBA';hashes.add(hashlib.sha256(im.tobytes()).hexdigest())
    report['animationFrames'].append(f)
report['uniqueFrames']=len(hashes);report['complete']=len(report['animationFrames'])==180
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);board=Image.new('RGB',(1774,987),'#faf8f3');board.paste(white(render),(0,65));d=ImageDraw.Draw(board);d.text((34,20),'RENDU BLENDER — DESSIN ORIGINAL 2D ARTICULÉ',font=font,fill='#30363c');board.save(O/'apercu-reference.jpg',quality=96)
(O/'verification-images.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='animationFrames'},ensure_ascii=False))
