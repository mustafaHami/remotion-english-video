"""Generate cached voice clips, trim only surrounding silence, and validate every cue."""
from pathlib import Path
import asyncio,sys,json,subprocess,array,math,hashlib,wave,io
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.npm-cache/audio-python'))
import edge_tts
SRC=ROOT/'src/archive/experiments/options-v3'
OUT=ROOT/'public/audio/options-v3';OUT.mkdir(exist_ok=True,parents=True)
BIN=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
jobs=json.loads((SRC/'narration-jobs.json').read_text(encoding='utf-8'))
voice='en-GB-SoniaNeural';rate='-5%'
manifest={};metadata={}
async def main():
    for i,job in enumerate(jobs):
        text=job['text'].replace('\u2019',"'")
        assert not any(bad in text for bad in ['\ufffd','Ã','â€']),f'Invalid text encoding: {text!r}'
        key=hashlib.sha256((voice+rate+text).encode()).hexdigest()[:16]
        mp3=OUT/f'{key}.mp3';wav=OUT/f'{key}.wav'
        if not wav.exists():
            if not mp3.exists() or mp3.stat().st_size==0:
                for attempt in range(3):
                    try:
                        await edge_tts.Communicate(text,voice=voice,rate=rate).save(str(mp3));break
                    except Exception:
                        if attempt==2:raise
                        await asyncio.sleep(2)
            decoded=subprocess.run([str(BIN),'-v','error','-i',str(mp3),'-c:a','pcm_s16le','-f','wav','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
            reader=wave.open(io.BytesIO(decoded),'rb');samples=array.array('h',reader.readframes(reader.getnframes()))
            # Keep 150ms on each side of all audible blocks, including quiet consonants.
            block=240
            audible=[j for j in range(0,len(samples),block) if math.sqrt(sum(v*v for v in samples[j:j+block])/max(1,len(samples[j:j+block])))>120]
            if not audible:raise ValueError(f'Silent generated clip: {text}')
            first=max(0,audible[0]-3600);last=min(len(samples),audible[-1]+block+3600)
            with wave.open(str(wav),'wb') as dest:
                dest.setnchannels(1);dest.setsampwidth(2);dest.setframerate(24000);dest.writeframes(samples[first:last].tobytes())
        with wave.open(str(wav),'rb') as reader:
            pcm=array.array('h',reader.readframes(reader.getnframes()));duration=len(pcm)/24000
        peaks=[]
        for j in range(60):
            a=pcm[j*len(pcm)//60:(j+1)*len(pcm)//60]
            peaks.append(math.sqrt(sum(v*v for v in a)/max(1,len(a))))
        peak=max(peaks)
        clip={'start':job['start'],'duration':math.ceil(duration*30),'src':f'audio/options-v3/{key}.wav','text':text,'peaks':[round(v/peak,4) for v in peaks]}
        manifest.setdefault(str(job['option']),[]).append(clip)
        metadata[key]={'text':text,'voice':voice,'rate':rate,'seconds':duration,'peak':max(abs(v) for v in pcm)/32768,'sha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'modification':'150ms margins retained around audible blocks; surrounding silence trimmed.'}
        print(f'{i+1}/{len(jobs)} option {job["option"]}: {duration:.2f}s {text}',flush=True)
    config=json.loads((SRC/'render-config.json').read_text(encoding='utf-8'))
    for n,clips in manifest.items():
        end=next(c['frames'] for c in config if c['key']==n)
        clips.sort(key=lambda c:c['start'])
        for a,b in zip(clips,clips[1:]):
            assert a['start']+a['duration']<=b['start'],f'Overlapping narration: {n}: {a["text"]} / {b["text"]}'
        assert clips[-1]['start']+clips[-1]['duration']<=end
    (SRC/'voice-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    (OUT/'provenance.json').write_text(json.dumps({'generator':'edge-tts','voiceStatus':'Provisional voice, not a final narrator selection. No paid service used.','clips':metadata},indent=2,ensure_ascii=False),encoding='utf-8')
    print('All narration cues fit their timelines, without overlaps.')
asyncio.run(main())
