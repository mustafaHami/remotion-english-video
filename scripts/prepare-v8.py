from pathlib import Path
import importlib.util,asyncio,json,math
ROOT=Path.cwd();SRC=ROOT/'src/archive/experiments/options-v8';SRC.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('voices',ROOT/'scripts/generate-v4-audio.py');voice=importlib.util.module_from_spec(spec);spec.loader.exec_module(voice);voice.OUT=ROOT/'public/audio/options-v8';voice.OUT.mkdir(parents=True,exist_ok=True)
async def main():
 intro=await voice.clip('Trouve les mots oppos\u00e9s.','fr-FR-DeniseNeural',3)
 opening=math.ceil((3+intro['duration']+9)/15)*15
 old=json.loads((ROOT/'src/archive/experiments/options-v3/voice-manifest.json').read_text(encoding='utf-8'))['3']
 outro=json.loads((ROOT/'src/archive/experiments/options-v5/voice-manifest.json').read_text(encoding='utf-8'))['4'][-1]
 clips=[intro]+[dict(c,start=opening+150+i*90+18) for i,c in enumerate(old)]+[dict(outro,start=opening+1050+6)]
 item=dict(key='3',option=3,id='TestOption3V8',title='Dix mots, leurs oppos\u00e9s.',introFrames=opening,bodyFrames=1050,outroFrames=165,frames=opening+1215,firstReveal=150,rowFrames=90,captures=[30,opening+90,opening+170,opening+620,opening+1020,opening+1160])
 for name,data in [('render-config.json',[item]),('voice-manifest.json',{'3':clips})]:(SRC/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 (voice.OUT/'provenance.json').write_text(json.dumps(voice.metadata,ensure_ascii=False,indent=2),encoding='utf-8')
asyncio.run(main())
