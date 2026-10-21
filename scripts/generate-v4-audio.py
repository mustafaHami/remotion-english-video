"""Prepare only the two requested voice experiments; preserve V3 assets."""
from pathlib import Path
import asyncio, sys, json, hashlib, subprocess, wave, io, array, math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.npm-cache/audio-python'))
import edge_tts
SRC=ROOT/'src/archive/experiments/options-v4';SRC.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'public/audio/options-v4';OUT.mkdir(parents=True,exist_ok=True)
old=json.loads((ROOT/'src/archive/experiments/options-v3/voice-manifest.json').read_text(encoding='utf-8'))
metadata=[]
async def clip(text,voice,start):
    text=text.replace('\u2019',"'");rate='-5%'
    key=hashlib.sha256((voice+rate+text).encode()).hexdigest()[:16]
    wav=OUT/f'{key}.wav';mp3=OUT/f'{key}.mp3'
    if not wav.exists():
        for attempt in range(3):
            try:
                await edge_tts.Communicate(text,voice=voice,rate=rate).save(str(mp3));break
            except Exception:
                if attempt==2:raise
                await asyncio.sleep(2)
        decoded=subprocess.run([str(ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'),'-v','error','-i',str(mp3),'-c:a','pcm_s16le','-f','wav','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
        with wave.open(io.BytesIO(decoded),'rb') as reader:pcm=array.array('h',reader.readframes(reader.getnframes()))
        audible=[j for j in range(0,len(pcm),240) if math.sqrt(sum(v*v for v in pcm[j:j+240])/len(pcm[j:j+240]))>120]
        assert audible
        with wave.open(str(wav),'wb') as dest:
            dest.setnchannels(1);dest.setsampwidth(2);dest.setframerate(24000)
            dest.writeframes(pcm[max(0,audible[0]-3600):min(len(pcm),audible[-1]+3840)].tobytes())
    with wave.open(str(wav),'rb') as reader:pcm=array.array('h',reader.readframes(reader.getnframes()))
    peaks=[math.sqrt(sum(v*v for v in pcm[j*len(pcm)//60:(j+1)*len(pcm)//60])/max(1,len(pcm[j*len(pcm)//60:(j+1)*len(pcm)//60]))) for j in range(60)]
    result=dict(start=start,duration=math.ceil(len(pcm)/24000*30),src=wav.relative_to(ROOT/'public').as_posix(),text=text,voice=voice,peaks=[round(p/max(peaks),4) for p in peaks])
    metadata.append(dict(**result,sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),rate=rate))
    print(f'{voice}: {len(pcm)/24000:.2f}s {text}',flush=True)
    return result
async def main():
    intro=await clip('Quel verbe manque ? Choisis la bonne réponse.','fr-FR-DeniseNeural',6)
    intro_end=math.ceil((intro['start']+intro['duration']+18)/30)*30
    delay=max(0,intro_end-60)
    manifest={'4':[intro]+[dict(c,start=c['start']+delay,voice='en-GB-SoniaNeural') for c in old['4']],'9':[]}
    for i,c in enumerate(old['9']):
        result=dict(c,voice='en-GB-SoniaNeural') if i%2==0 else await clip(c['text'],'en-GB-RyanNeural',c['start'])
        assert result['start']+result['duration']<=(i//2+1)*315-8
        manifest['9'].append(result)
    config=[dict(key='4',option=4,id='TestOption4V4',title='Trois phrases à compléter.',frames=1260+delay,completeAt=1170+delay,questionDelay=delay,introEnd=intro_end,captures=[45,120+delay,250+delay,540+delay,670+delay,1230+delay]),dict(key='9',option=9,id='TestOption9V4',title='Un échange au travail.',frames=1260,completeAt=1170,questionDelay=0,introEnd=0,captures=[120,280,450,595,910,1230])]
    for clips in manifest.values():
        for a,b in zip(clips,clips[1:]):assert a['start']+a['duration']<=b['start']
    for name,value in [('voice-manifest.json',manifest),('render-config.json',config)]:
        (SRC/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'provenance.json').write_text(json.dumps(dict(generator='edge-tts',clips=metadata,reusedAssets='Sonia clips reference the unchanged V3 manifest.'),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':asyncio.run(main())
