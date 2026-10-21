from pathlib import Path
import json,asyncio,importlib.util,math
ROOT=Path.cwd();SRC=ROOT/'src/archive/experiments/options-v6';SRC.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('voices',ROOT/'scripts/generate-v4-audio.py');voice=importlib.util.module_from_spec(spec);spec.loader.exec_module(voice)
voice.OUT=ROOT/'public/audio/options-v6';voice.OUT.mkdir(parents=True,exist_ok=True)
async def main():
    intro=await voice.clip('Quel verbe manque ?','fr-FR-DeniseNeural',3)
    opening=math.ceil((intro['start']+intro['duration']+9)/15)*15
    old=json.loads((ROOT/'src/archive/experiments/options-v3/voice-manifest.json').read_text(encoding='utf-8'))['4']
    ending=json.loads((ROOT/'src/archive/experiments/options-v5/voice-manifest.json').read_text(encoding='utf-8'))['4'][-1]
    clips=[intro]+[dict(c,start=opening+i*195+137) for i,c in enumerate(old)]+[dict(ending,start=opening+585+6)]
    for i,c in enumerate(clips[1:4]):assert c['start']+c['duration']<=opening+(i+1)*195
    outro=math.ceil((6+ending['duration']+12)/15)*15
    item=dict(key='4',option=4,id='TestOption4V6',title='Quel verbe manque ?',introFrames=opening,bodyFrames=585,outroFrames=outro,frames=opening+585+outro,pageFrames=195,answerAt=135,pauseAt=45,captures=[30,opening+80,opening+150,opening+345,opening+540,opening+685])
    for name,value in [('render-config.json',[item]),('voice-manifest.json',{'4':clips})]:(SRC/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
    (voice.OUT/'provenance.json').write_text(json.dumps(voice.metadata,indent=2,ensure_ascii=False),encoding='utf-8')
asyncio.run(main())
