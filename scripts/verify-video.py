"""Inspect production MP4s and exported frame/audio measurements on Windows or Linux."""
from pathlib import Path
import argparse,json,subprocess,array,math,wave,io,shutil,sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
def executable(name):
 found=shutil.which(name)
 if found:return found
 suffix='.exe' if sys.platform=='win32' else ''
 return str(next(p for p in (ROOT/'node_modules/@remotion').glob('compositor-*/'+name+suffix) if ('win32' in str(p))==(sys.platform=='win32')))
def inspect(folder):
 lesson=json.loads((folder/'lesson.json').read_text(encoding='utf-8'));n=lesson['option'];t=lesson['timing'];frames=t['introFrames']+t['bodyFrames']+t['outroFrames'];video=folder/f'option-{n}.mp4'
 meta=json.loads(subprocess.run([executable('ffprobe'),'-v','error','-show_streams','-of','json',str(video)],capture_output=True,check=True).stdout)
 v=next(s for s in meta['streams'] if s['codec_type']=='video');assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264',1080,1920,'30/1',frames)
 assert v['color_space']=='bt709' and any(s['codec_type']=='audio' and s['codec_name']=='aac' for s in meta['streams'])
 raw=subprocess.run([executable('ffmpeg'),'-v','error','-xerror','-i',str(video),'-an','-vf','scale=180:320','-c:v','rawvideo','-f','image2pipe','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
 size=180*320*3;assert len(raw)==frames*size
 board=Image.new('RGB',(840,1020),'#E9E7ED');draw=ImageDraw.Draw(board)
 for j,f in enumerate(json.loads((folder/'captures.json').read_text(encoding='utf-8'))):
  im=Image.frombytes('RGB',(180,320),raw[f*size:(f+1)*size]).resize((270,480));x=j%3*280+5;y=j//3*510+24;board.paste(im,(x,y));draw.text((x,y-17),f'Option {n}: {f/30:.1f}s',fill='#1E1B3A')
 board.save(folder/'preview.jpg',quality=94)
 audio=subprocess.run([executable('ffmpeg'),'-v','error','-xerror','-i',str(video),'-vn','-c:a','pcm_s16le','-f','wav','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout
 with wave.open(io.BytesIO(audio),'rb') as r:pcm=array.array('h',r.readframes(r.getnframes()))
 def rms(a,b):
  samples=pcm[round(a*16000):round(b*16000)];return math.sqrt(sum(v*v for v in samples)/max(1,len(samples)))/32768
 clips=lesson['narration'];checks=[]
 for c in clips:
  energy=rms(c['start']/30,(c['start']+c['duration'])/30);assert energy>.005,f'Missing voice: {c["text"]}';checks.append(dict(text=c['text'],rms=energy))
 for a,b in zip(clips,clips[1:]):
  start=(a['start']+a['duration'])/30+.12;end=b['start']/30-.12
  if end-start>.3:assert rms(start,end)<.001,'Unexpected sound between voice clips'
 quiet=[]
 if n in [4,5,6,8,11,12]:
  for i in range(3):
   if n==12 and i==0:continue
   a=(t['introFrames']+i*t['pageFrames']+45)/30;b=a+4;assert rms(a,b)<.001;quiet.append([a,b])
 if n==3:assert rms((t['introFrames']+30)/30,(t['introFrames']+150)/30)<.001
 if n==10:
  for i in range(3):assert rms((t['introFrames']+i*420+150)/30,(t['introFrames']+i*420+310)/30)<.001
 peak=max(abs(v) for v in pcm)/32768;assert peak<.99
 qa=json.loads((folder/'layout-qa.json').read_text(encoding='utf-8'));assert len(qa)==frames and all(not r['violations'] and all(r['fonts']) for r in qa)
 result=dict(option=n,seconds=frames/30,frames=frames,videoDecoded=True,audioDecoded=True,layoutErrors=0,centerErrorPx=max(r['centerError'] for r in qa)*3,voiceCues=len(clips),silentSearchWindows=quiet,peak=round(peak,5),auditoryReview=False)
 (folder/'inspection.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--option',type=int);p.add_argument('--folder',type=Path);args=p.parse_args()
 folders=[args.folder] if args.folder else [ROOT/f'output/options/option-{n}' for n in range(1,15) if args.all or args.option==n]
 if not folders:p.error('Use --all, --option=N or --folder=PATH')
 for folder in folders:inspect(folder.resolve())
