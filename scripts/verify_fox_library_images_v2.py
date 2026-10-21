import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';m=json.loads((O/'manifest.json').read_text(encoding='utf8'));report={'clips':[],'accessories':[]};tiles=[]
fontfile='C:/Windows/Fonts/segoeui.ttf';font=ImageFont.truetype(fontfile,22);small=ImageFont.truetype(fontfile,17)
for c in m['clips']:
    folder=O/'frames'/c['id'];files=[folder/('image-%04d.png'%f) for f in range(1,c['frames']+1)];missing=[str(p) for p in files if not p.exists()]
    assert not missing,(c['id'],missing[:3]);hashes=set();bboxes=[];bad=[];sizes=set();opaque=0
    for p in files:
        with Image.open(p) as im:
            assert im.mode=='RGBA',(p,im.mode);sizes.add(im.size);a=im.getchannel('A');box=a.getbbox();assert box,(p,'empty');bboxes.append(box);hashes.add(hashlib.sha256(im.tobytes()).hexdigest())
            if a.getextrema()[0]>0:opaque+=1
            if box[0]<=0 or box[1]<=0 or box[2]>=im.width or box[3]>=im.height:bad.append(p.name)
    assert sizes=={(768,768)},(c['id'],sizes);assert not bad,(c['id'],'clipped',bad);assert opaque==0
    union=[min(b[0] for b in bboxes),min(b[1] for b in bboxes),max(b[2] for b in bboxes),max(b[3] for b in bboxes)]
    c['boundsUnionPx']=union;c['renderEngine']='BLENDER_EEVEE';c['exportedFrames']=len(files)
    titles=O/'titres';titles.mkdir(exist_ok=True);title=Image.new('RGBA',(768,768),(0,0,0,0));td=ImageDraw.Draw(title);tf=ImageFont.truetype(fontfile,27);td.text((384,32),c['title'],font=tf,fill='#30363c',anchor='mt');title.save(titles/(c['id']+'.png'))
    report['clips'].append({'id':c['id'],'frames':len(files),'uniqueFrames':len(hashes),'bounds':union,'clippedFrames':len(bad),'rgba':True})
    frame=round(c['frames']*.5);im=Image.open(folder/('image-%04d.png'%frame)).convert('RGBA')
    if c['accessory']:
        ap=O/'accessoires'/c['accessory']/('image-%04d.png'%frame)
        if ap.exists():im.alpha_composite(Image.open(ap).convert('RGBA'))
    tile=Image.new('RGB',(420,458),'#faf8f2');thumb=im.resize((420,420),Image.Resampling.LANCZOS);tile.paste(thumb,(0,0),thumb);d=ImageDraw.Draw(tile);d.text((16,421),c['title'],font=small,fill='#30363c');tiles.append(tile)
for name,info in m['accessories'].items():
    c=next(c for c in m['clips'] if c['id']==info['clip']);paths=[O/('accessoires/'+name)/('image-%04d.png'%f) for f in range(1,c['frames']+1)];count=0
    for p in paths:
        assert p.exists(),p
        with Image.open(p) as im:assert im.mode=='RGBA' and im.size==(768,768);count+=int(bool(im.getchannel('A').getbbox()))
    report['accessories'].append({'name':name,'frames':len(paths),'nonemptyFrames':count,'rgba':True});assert count>10
cols=4;rows=math.ceil(len(tiles)/cols);board=Image.new('RGB',(cols*420,rows*458+76),'#faf8f2');d=ImageDraw.Draw(board);d.text((24,20),'RENARD — BIBLIOTHÈQUE DE MOUVEMENTS / TEST D’INTÉGRATION',font=font,fill='#30363c')
for i,im in enumerate(tiles):board.paste(im,((i%cols)*420,76+(i//cols)*458))
board.save(O/'planche-mouvements.jpg',quality=93)
m['renderEngine']='BLENDER_EEVEE';m['referenceStandingHeightPx']=m['clips'][0]['boundsUnionPx'][3]-m['clips'][0]['boundsUnionPx'][1];m['totalCharacterFrames']=sum(c['frames'] for c in m['clips']);m['totalAccessoryFrames']=sum(x['frames'] for x in report['accessories']);m['verification']='verification-exports.json'
# Both travel directions are native PNG assets; mirror all canvas pixels, never just the bounding box.
mirrorids=['attente-quatre-pattes','marche','demarrer-marche','arreter-marche','se-lever','se-baisser']
for c in m['clips']:
    if c['id'] not in mirrorids:continue
    dest=O/'frames'/('miroir-'+c['id']);dest.mkdir(exist_ok=True)
    for f in range(1,c['frames']+1):
        with Image.open(O/'frames'/c['id']/('image-%04d.png'%f)) as im:ImageOps.mirror(im).save(dest/('image-%04d.png'%f),compress_level=4)
    c['mirrorPattern']='frames/miroir-'+c['id']+'/image-%04d.png';c['mirrorAnchorPx']=[768-m['anchorPx'][0],m['anchorPx'][1]]
m['notes'].append('Les six clips de locomotion ont une copie miroir PNG. Les gestes peuvent être retournés avec leur accessoire et leur ancrage.')
(O/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf8');report['totalCharacterFrames']=m['totalCharacterFrames'];report['totalAccessoryFrames']=m['totalAccessoryFrames'];report['mirroredClips']=mirrorids;(O/'verification-exports.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
