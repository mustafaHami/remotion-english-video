from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
r=Path('D:/ai-generation-video/output/englizy/3d')
files=sorted((r/'frames').glob('frame-*.png'))
alpha_boxes=[];hashes=set()
for f in files:
    im=Image.open(f).convert('RGBA')
    a=im.getchannel('A');box=a.getbbox()
    assert box and box[0]>0 and box[1]>0 and box[2]<im.width and box[3]<im.height,f'Content clipped: {f}'
    assert a.getextrema()[0]==0, f'Alpha missing: {f}'
    hashes.add(hashlib.md5(im.tobytes()).hexdigest())
    alpha_boxes.append(box)
assert len(files)==180,len(files)
assert len(hashes)>170,len(hashes)
tiles=[]
for frame in [1,31,61,91,121,151]:
    im=Image.open(r/'frames'/f'frame-{frame:04d}.png').convert('RGBA')
    bg=Image.new('RGBA',im.size,'#EAE5FF');bg.alpha_composite(im);bg=bg.convert('RGB').resize((360,360),Image.Resampling.LANCZOS)
    tile=Image.new('RGB',(360,388),'#EAE5FF');tile.paste(bg,(0,0));ImageDraw.Draw(tile).text((14,368),f'{(frame-1)/30:.0f} s',fill='#1E1B3A');tiles.append(tile)
board=Image.new('RGB',(1080,776),'#EAE5FF')
for i,t in enumerate(tiles):board.paste(t,((i%3)*360,(i//3)*388))
board.save(r/'controle-animation.jpg',quality=92)
(r/'images-qa.json').write_text(json.dumps({'frames':len(files),'unique_frames':len(hashes),'resolution':list(im.size),'alpha_transparency':True,'all_frames_uncropped':True},indent=2))
print('QA_OK',len(files),len(hashes))
