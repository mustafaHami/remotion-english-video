"""Generate a provisional short voice test; no Windows SAPI/Zira voice."""
from pathlib import Path
import asyncio,sys,json,subprocess,array,math,hashlib,wave,io
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.npm-cache/audio-python'))
import edge_tts
dest=ROOT/'public/audio/options/the-bill-please.mp3'
dest.parent.mkdir(parents=True,exist_ok=True)
async def main():
    await edge_tts.Communicate('The bill, please.',voice='en-GB-SoniaNeural',rate='-10%').save(str(dest))
if not dest.exists() or dest.stat().st_size==0:asyncio.run(main())
ffmpeg=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
result=subprocess.run([str(ffmpeg),'-v','error','-i',str(dest),'-c:a','pcm_s16le','-f','wav','-ac','1','-ar','16000','-'],capture_output=True)
if result.returncode:raise RuntimeError(result.stderr.decode())
reader=wave.open(io.BytesIO(result.stdout),'rb')
samples=array.array('h',reader.readframes(reader.getnframes()))
bins=[]
for i in range(60):
    segment=samples[i*len(samples)//60:(i+1)*len(samples)//60]
    bins.append(math.sqrt(sum(v*v for v in segment)/max(1,len(segment)))/32768)
peak=max(bins)
wave={'duration':len(samples)/16000,'peaks':[round(v/peak,4) for v in bins],'author':'Microsoft Edge en-GB-SoniaNeural','kind':'Provisional synthetic neural voice','status':'Voice test; final voice not selected'}
(ROOT/'src/archive/experiments/options/audio-wave.json').write_text(json.dumps(wave,indent=2),encoding='utf-8')
(dest.parent/'the-bill-please-source.json').write_text(json.dumps({'text':'The bill, please.','voice':'en-GB-SoniaNeural','rate':'-10%','generator':'edge-tts','sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'status':'Provisional voice test; user has not selected a final voice. No paid service used.'},indent=2),encoding='utf-8')
print('Prepared',wave['duration'],'seconds; peak',peak)
