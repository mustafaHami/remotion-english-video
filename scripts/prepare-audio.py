"""Freeze local narration for any option content. No secrets or machine paths required."""
from pathlib import Path
import argparse,sys,json,hashlib,math,wave,io,array,asyncio,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
try:import edge_tts
except ImportError:
 sys.path.insert(0,str(ROOT/'.npm-cache/audio-python'));import edge_tts

def ffmpeg():
 executable=shutil.which('ffmpeg')
 if executable:return executable
 suffix='ffmpeg.exe' if sys.platform=='win32' else 'ffmpeg'
 for p in (ROOT/'node_modules/@remotion').glob('compositor-*/'+suffix):
  if ('win32' in str(p))==(sys.platform=='win32'):return str(p)
 raise RuntimeError('FFmpeg absent. Install FFmpeg (see deploy/Dockerfile).')

async def prepare(path):
 lesson=json.loads(path.read_text(encoding='utf-8-sig'));out=ROOT/'public/audio/production';out.mkdir(parents=True,exist_ok=True)
 provenance={};rate='-5%'
 for c in lesson['narration']:
  text=c['text'].replace('\u2019',"'");voice=c['voice'];key=hashlib.sha256((voice+rate+text).encode()).hexdigest()[:16];wav=out/f'{key}.wav'
  if not wav.exists():
   cached=next((p for p in (ROOT/'public/audio').rglob(key+'.wav') if p!=wav),None)
   if cached:shutil.copy2(cached,wav)
   else:
    mp3=out/f'{key}.mp3'
    for attempt in range(3):
     try:await edge_tts.Communicate(text,voice=voice,rate=rate).save(str(mp3));break
     except Exception:
      if attempt==2:raise
      await asyncio.sleep(2)
    raw=subprocess.run([ffmpeg(),'-v','error','-i',str(mp3),'-c:a','pcm_s16le','-f','wav','-ac','1','-ar','24000','-'],capture_output=True,check=True).stdout
    with wave.open(io.BytesIO(raw),'rb') as r:pcm=array.array('h',r.readframes(r.getnframes()))
    active=[j for j in range(0,len(pcm),240) if math.sqrt(sum(v*v for v in pcm[j:j+240])/max(1,len(pcm[j:j+240])))>120]
    if not active:raise ValueError('Generated voice is silent')
    with wave.open(str(wav),'wb') as w:
     w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm[max(0,active[0]-3600):min(len(pcm),active[-1]+3840)].tobytes())
  with wave.open(str(wav),'rb') as r:pcm=array.array('h',r.readframes(r.getnframes()));seconds=len(pcm)/r.getframerate()
  peaks=[math.sqrt(sum(v*v for v in pcm[j*len(pcm)//60:(j+1)*len(pcm)//60])/max(1,len(pcm)//60)) for j in range(60)]
  c.update(text=text,duration=math.ceil(seconds*30),src=wav.relative_to(ROOT/'public').as_posix(),peaks=[round(v/max(peaks),4) for v in peaks])
  provenance[key]=dict(text=text,voice=voice,rate=rate,sha256=hashlib.sha256(wav.read_bytes()).hexdigest(),seconds=seconds)
 intro=lesson['narration'][0];old=lesson['timing']['introFrames'];new=max(old,math.ceil((intro['start']+intro['duration']+9)/15)*15)
 if new!=old:
  for c in lesson['narration'][1:]:c['start']+=new-old
  lesson['timing']['introFrames']=new
 for a,b in zip(lesson['narration'],lesson['narration'][1:]):
  if a['start']+a['duration']>b['start']:raise ValueError(f'Overlapping voices: {a["text"]} / {b["text"]}. Adjust cue timing before rendering.')
 path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 meta=out/'provenance.json';existing=json.loads(meta.read_text(encoding='utf-8')) if meta.exists() else {};existing.update(provenance);meta.write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'Option {lesson["option"]}: {len(lesson["narration"])} voice clips frozen.',flush=True)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--content',type=Path);parser.add_argument('--all',action='store_true');args=parser.parse_args()
 paths=sorted((ROOT/'src/options').glob('option-*/content.json')) if args.all else [args.content] if args.content else []
 if not paths:parser.error('Use --content PATH or --all')
 async def main():
  for path in paths:await prepare(path.resolve())
 asyncio.run(main())
