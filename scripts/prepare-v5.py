"""Adapt the supplied vector reference and prepare three mascot test timelines."""
from pathlib import Path
import re,json,asyncio,importlib.util,math
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('C:/Users/Hami/Downloads/Planche de la mascotte-html')
DEST=ROOT/'src/archive/experiments/options-v5';DEST.mkdir(parents=True,exist_ok=True)
html=(SOURCE/'Fox.dc.html').read_text(encoding='utf-8')
svg=re.search(r'<svg\b.*?</svg>',html,re.S).group()
svg=re.sub(r'<animate\b.*?</animate>','',svg,flags=re.S)
motions=['FLOAT','TAIL','WAVE','POINT']
for motion in motions:
    match=re.search(r'<animateTransform\b.*?</animateTransform>',svg,re.S)
    before=svg[:match.start()];parent=before.rfind('<g')
    # Transform the same source group, using only the Remotion frame.
    before=before[:parent]+before[parent:].replace('<g',f'<g transform="__{motion}__"',1)
    svg=before+svg[match.end():]
svg=svg.replace('{{label}}','Renard').replace('{{vb}}','0 0 210 240').replace('{{flipT}}','translate(0 0)')
poses={}
for pose in ['salut','bravo']:
    visible={'ground','tail','wave','rightDown','eyesOpen','mouthOpen'} if pose=='salut' else {'ground','tail','cheer','eyesHappy','mouthOpen','stars'}
    poses[pose]=re.sub(r'{{d\.(\w+)}}',lambda m:'inline' if m[1] in visible else 'none',svg)
assert not any('{{' in s or '<animate' in s for s in poses.values())
(DEST/'fox-vectors.json').write_text(json.dumps(poses,ensure_ascii=False,indent=2),encoding='utf-8')
spec=importlib.util.spec_from_file_location('voice_helpers',ROOT/'scripts/generate-v4-audio.py')
voice=importlib.util.module_from_spec(spec);spec.loader.exec_module(voice)
voice.OUT=ROOT/'public/audio/options-v5';voice.OUT.mkdir(parents=True,exist_ok=True)
voice.metadata=[]
async def main():
    outro=await voice.clip('Bravo, tu as terminé cet exercice ! À bientôt !','fr-FR-DeniseNeural',12)
    config=[];manifest={}
    titles={'1':'Présent, passé, futur.','4':'Quel verbe manque ?','9':'Un échange au travail.'}
    scripts={'1':'Présent, passé, futur. Tu es prêt ?','4':'Quel verbe manque ? Choisis la bonne réponse.','9':'Un échange au travail. Tu es prêt ?'}
    for key in ['1','4','9']:
        intro=await voice.clip(scripts[key],'fr-FR-DeniseNeural',6)
        opening=math.ceil((intro['start']+intro['duration']+24)/30)*30
        ending=max(210,math.ceil((outro['start']+outro['duration']+36)/30)*30)
        body=1950 if key=='1' else 1260
        manifest[key]=[intro,dict(outro,start=opening+body+outro['start'])]
        config.append(dict(key=key,option=int(key),id=f'TestOption{key}V5',title=titles[key],introFrames=opening,bodyFrames=body,outroFrames=ending,frames=opening+body+ending,captures=[45,opening-15,opening+120,opening+body-30,opening+body+65,opening+body+ending-35]))
    for name,value in [('render-config.json',config),('voice-manifest.json',manifest)]:
        (DEST/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (voice.OUT/'provenance.json').write_text(json.dumps(dict(generator='edge-tts',clips=voice.metadata,mascotReference=str(SOURCE)),ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
