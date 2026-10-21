from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
ROOT=Path('D:/ai-generation-video/output/blender/rig-v1');bg=(250,249,245);report={}
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
for name,expected,size,frames in [('presentation',150,(540,960),[1,30,55,85,117,150]),('marche',180,(1280,720),[1,18,38,72,120,175])]:
    folder=ROOT/(name+'-frames');files=sorted(folder.glob('image-*.png'));assert len(files)==expected,(name,len(files));bad=[];boxes=[];unique=set()
    for i,p in enumerate(files,1):
        assert p.name=='image-%04d.png'%i,p.name
        im=Image.open(p);assert im.size==size and im.mode=='RGBA',(p,im.size,im.mode);box=im.getchannel('A').getbbox();assert box is not None,p;boxes.append(box);unique.add(hashlib.sha256(p.read_bytes()).hexdigest())
        if box[0]==0 or box[1]==0 or box[2]==size[0] or box[3]==size[1]:bad.append(i)
    assert not bad,(name,'cadrage tronqué',bad)
    report[name]={'frames':len(files),'size':size,'mode':'RGBA','unique_frames':len(unique),'frames_touching_image_border':bad,'bbox_union':[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]}
    tw,th=(270,480) if name=='presentation' else (640,360);canvas=Image.new('RGB',(tw*3,th*2+125),bg);d=ImageDraw.Draw(canvas);d.text((20,15),'TEST D’ARTICULATION / '+name.upper(),font=font,fill=(48,54,58))
    for k,f in enumerate(frames):
        im=Image.open(folder/('image-%04d.png'%f)).convert('RGBA').resize((tw,th),Image.Resampling.LANCZOS);x=(k%3)*tw;y=60+(k//3)*(th+30);canvas.paste(im,(x,y),im);d.text((x+15,y+th),'Image '+str(f),font=font,fill=(48,54,58))
    canvas.save(ROOT/('verification-'+name+'-planche.png'))
(ROOT/'verification-images-clips.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps(report))
