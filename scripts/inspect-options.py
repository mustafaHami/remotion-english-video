"""Verify delivered encodings and build contact sheets from decoded MP4 frames."""
from pathlib import Path
import json,subprocess,sys,array,math,wave,io
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BIN=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc'
config=json.loads((ROOT/'src/archive/experiments/options/render-config.json').read_text())
selection=next((list(map(int,a.split('=')[1].split(','))) for a in sys.argv if a.startswith('--options=')),None)
stills='--stills-only' in sys.argv
summaries=[]
for item in config:
    n=item['option']
    if selection and n not in selection:continue
    out=ROOT/f'output/tests/test-option-{n}'
    frames=item['captures']
    if stills:
        images=[Image.open(out/f'captures/frame-{f:03}.png').convert('RGB').resize((270,480)) for f in frames]
    else:
        video=out/f'test-option-{n}.mp4'
        meta=json.loads(subprocess.run([str(BIN/'ffprobe.exe'),'-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,check=True).stdout)
        stream=next(s for s in meta['streams'] if s['codec_type']=='video')
        assert (stream['codec_name'],stream['width'],stream['height'],stream['r_frame_rate'],stream['pix_fmt'])==('h264',1080,1920,'30/1','yuv420p')
        assert int(stream['nb_frames'])==item['frames']
        assert abs(float(stream['duration'])-item['frames']/30)<.02
        assert stream['color_space']=='bt709'
        raw=subprocess.run([str(BIN/'ffmpeg.exe'),'-v','error','-xerror','-i',str(video),'-an','-vf','scale=270:480','-c:v','rawvideo','-f','image2pipe','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
        size=270*480*3
        assert len(raw)==size*item['frames']
        images=[Image.frombytes('RGB',(270,480),raw[f*size:(f+1)*size]) for f in frames]
        # Dense frame sampling around each main change is a separate motion review sheet.
        motion_frames=sorted(set(max(0,min(item['frames']-1,f+delta)) for f in [210,270,300,item['completeAt']] for delta in [-8,-4,0,4,8,16]))
        motion=Image.new('RGB',(6*184,((len(motion_frames)+5)//6)*344),'#E9E7ED')
        draw=ImageDraw.Draw(motion)
        for j,f in enumerate(motion_frames):
            im=Image.frombytes('RGB',(270,480),raw[f*size:(f+1)*size]).resize((180,320))
            x=(j%6)*184+2;y=(j//6)*344+20
            motion.paste(im,(x,y));draw.text((x,y-16),f'{f/30:.2f}s',fill='#1E1B3A')
        qa=out/'qa';qa.mkdir(exist_ok=True)
        motion.save(qa/'motion.jpg',quality=92)
        (qa/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        records=json.loads((out/'layout-qa.json').read_text())
        assert len(records)==item['frames']
        assert not any(r['violations'] or not all(r['fonts']) for r in records)
        summary={'option':n,'seconds':item['frames']/30,'frames':len(records),'layoutErrors':0,'fullDecode':True,'centerErrorPx':round(max(r['centerError'] for r in records)*3,5),'bytes':video.stat().st_size}
        if n==8:
            # The original correction briefly faded out the entire sentence.
            # Verify that sentence ink stays present throughout the revised motion.
            def sentence_ink(f):
                im=Image.frombytes('RGB',(270,480),raw[f*size:(f+1)*size]).crop((27,184,243,224))
                return sum(r<90 and g<160 and b<140 for r,g,b in im.getdata())
            reference=max(1,sentence_ink(350))
            ratios=[sentence_ink(f)/reference for f in range(210,330)]
            continuity={'framesChecked':120,'minimumInkRatio':round(min(ratios),4),'blankFrames':sum(r<.45 for r in ratios)}
            (qa/'correction-continuity.json').write_text(json.dumps(continuity,indent=2),encoding='utf-8')
            assert continuity['blankFrames']==0
            summary['correctionContinuity']=continuity
        if n==10:
            assert any(s['codec_type']=='audio' and s['codec_name']=='aac' for s in meta['streams'])
            result=subprocess.run([str(BIN/'ffmpeg.exe'),'-v','error','-i',str(video),'-vn','-c:a','pcm_s16le','-f','wav','-ac','1','-ar','16000','-'],capture_output=True,check=True)
            reader=wave.open(io.BytesIO(result.stdout),'rb');samples=array.array('h',reader.readframes(reader.getnframes()))
            def rms(start,end):
                a=samples[int(start*16000):int(end*16000)]
                return math.sqrt(sum(v*v for v in a)/max(1,len(a)))/32768
            audio_report={'firstListenRms':rms(3,5.2),'repeatSilenceRms':rms(7,14),'secondListenRms':rms(14,16.2),'peak':max(abs(v) for v in samples)/32768,'syntheticVoice':'en-GB-SoniaNeural','auditoryReview':False}
            assert audio_report['firstListenRms']>.01 and audio_report['secondListenRms']>.01
            assert audio_report['repeatSilenceRms']<.0001 and audio_report['peak']<.99
            (qa/'audio-qa.json').write_text(json.dumps(audio_report,indent=2),encoding='utf-8')
            summary['audio']=audio_report
        summaries.append(summary)
        print(json.dumps(summary))
    board=Image.new('RGB',(840,1020),'#E9E7ED');draw=ImageDraw.Draw(board)
    for j,(im,f) in enumerate(zip(images,frames)):
        x=(j%3)*280+5;y=(j//3)*510+24;board.paste(im,(x,y));draw.text((x,y-18),f'Option {n} / {f/30:.1f}s',fill='#1E1B3A')
    board.save(out/('planche-captures.jpg' if stills else f'planche-test-option-{n}.jpg'),quality=94)
if summaries:
    (ROOT/'output/tests/options-render-summary.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
