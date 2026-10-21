"""Decode the voiced test exports and verify both narration and pause timing."""
from pathlib import Path
import json,subprocess,sys,array,math,wave,io
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/tests'
BIN=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc'
revision=11 if '--revision=11' in sys.argv else 10 if '--revision=10' in sys.argv else 9 if '--revision=9' in sys.argv else 8 if '--revision=8' in sys.argv else 7 if '--revision=7' in sys.argv else 6 if '--revision=6' in sys.argv else 5 if '--revision=5' in sys.argv else 4 if '--revision=4' in sys.argv else 3
config=json.loads((ROOT/f'src/archive/experiments/options-v{revision}/render-config.json').read_text(encoding='utf-8'))
voice=json.loads((ROOT/f'src/archive/experiments/options-v{revision}/voice-manifest.json').read_text(encoding='utf-8'))
if revision==5:
    v3=json.loads((ROOT/'src/archive/experiments/options-v3/voice-manifest.json').read_text(encoding='utf-8'))
    v4=json.loads((ROOT/'src/archive/experiments/options-v4/voice-manifest.json').read_text(encoding='utf-8'))
    for item in config:
        key=item['key'];source=v4[key] if key=='9' else v3[key]
        voice[key]=sorted(voice[key]+[dict(c,start=c['start']+item['introFrames']) for c in source],key=lambda c:c['start'])
for text in [c['title'] for c in config]+[c['text'] for clips in voice.values() for c in clips]:
    assert not any(bad in text for bad in ['\ufffd','Ã','â€']),f'Invalid text encoding: {text!r}'
selection=next((a.split('=')[1].split(',') for a in sys.argv if a.startswith('--keys=')),None)
stills='--stills-only' in sys.argv
for item in config:
    key=item['key'];n=item['option']
    if selection and key not in selection:continue
    suffix=f'-v{revision}'+('-'+item['verb'] if '-' in key else '')
    folder=OUT/f'test-option-{n}';qa=folder/('qa'+suffix);qa.mkdir(exist_ok=True)
    captures=folder/('captures'+suffix)
    if stills:
        images=[Image.open(captures/f'frame-{f:03}.png').convert('RGB').resize((270,480)) for f in item['captures']]
    else:
        video=folder/f'test-option-{n}{suffix}.mp4'
        meta=json.loads(subprocess.run([str(BIN/'ffprobe.exe'),'-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,check=True).stdout)
        stream=next(s for s in meta['streams'] if s['codec_type']=='video')
        assert (stream['codec_name'],stream['width'],stream['height'],stream['r_frame_rate'],stream['pix_fmt'])==('h264',1080,1920,'30/1','yuv420p')
        assert int(stream['nb_frames'])==item['frames'] and stream['color_space']=='bt709'
        assert revision in [6,7,11] or item['frames']/30>=40
        assert any(s['codec_type']=='audio' and s['codec_name']=='aac' for s in meta['streams'])
        raw=subprocess.run([str(BIN/'ffmpeg.exe'),'-v','error','-xerror','-i',str(video),'-an','-vf','scale=180:320','-c:v','rawvideo','-f','image2pipe','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
        size=180*320*3;assert len(raw)==size*item['frames']
        def frame_image(f):return Image.frombytes('RGB',(180,320),raw[f*size:(f+1)*size])
        images=[frame_image(f).resize((270,480)) for f in item['captures']]
        centers=[450,720,990] if n==2 else [420,840] if n not in [1,3,9,13] else [315,630,945] if n==9 else [210,990,1140] if n==1 else [210,480,930]
        if revision==4 and n==4:centers=[c+item['questionDelay'] for c in [210,420,840]]
        if revision in [5,6,7,8,9,10,11]:centers=[item['introFrames'],item['introFrames']+item['bodyFrames']]
        if revision in [6,7,11]:centers += [item['introFrames']+i*item['pageFrames'] for i in [1,2]]
        motion_frames=sorted(set(max(0,min(item['frames']-1,f+d)) for f in centers for d in [-9,-5,-1,0,1,5,9,14]))
        board=Image.new('RGB',(8*184,((len(motion_frames)+7)//8)*344),'#E9E7ED');draw=ImageDraw.Draw(board)
        for j,f in enumerate(motion_frames):
            x=(j%8)*184+2;y=(j//8)*344+20;board.paste(frame_image(f),(x,y));draw.text((x,y-16),f'{f/30:.2f}s',fill='#1E1B3A')
        board.save(qa/'transitions.jpg',quality=92)
        # Decode final AAC, then compare audible and silent windows with the frozen cue manifest.
        audio=subprocess.run([str(BIN/'ffmpeg.exe'),'-v','error','-xerror','-i',str(video),'-vn','-c:a','pcm_s16le','-f','wav','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout
        reader=wave.open(io.BytesIO(audio),'rb');pcm=array.array('h',reader.readframes(reader.getnframes()))
        def rms(a,b):
            samples=pcm[round(a*16000):round(b*16000)]
            return math.sqrt(sum(v*v for v in samples)/max(1,len(samples)))/32768
        clips=voice[key];audio_checks=[]
        for i,clip in enumerate(clips):
            start=clip['start']/30;end=(clip['start']+clip['duration'])/30
            energy=rms(start,end);assert energy>.005,f'Missing narration {key}: {clip["text"]}'
            if n==9 and revision<5:assert clip['start']+clip['duration']<=(i//2+1)*315-8,'A dialogue turn extends into the page transition'
            audio_checks.append({'text':clip['text'],'start':start,'end':end,'rms':round(energy,6)})
        repetition=[]
        if revision in [8,9,10]:
            assert len(clips)==12 and rms(0,1)>.005
            offset=item['introFrames']
            assert rms((offset+30)/30,(offset+150)/30)<.001
            for i,c in enumerate(clips[1:11]):
                assert c['start']==offset+150+i*90+18
                assert c['start']+c['duration']<=offset+150+(i+1)*90
            assert item['rowFrames']==90
        if revision in [6,7,11]:
            assert rms(0,1)>.005
            offset=item['introFrames'];page=item['pageFrames'];answer=item['answerAt']
            assert page-answer==(90 if revision in [7,11] else 60), 'Incorrect answer hold duration'
            for i,c in enumerate(clips[1:4]):
                assert c['start']+c['duration']<=offset+(i+1)*page
                assert rms((offset+i*page+item['pauseAt'])/30,(offset+i*page+answer)/30)<.001
            assert len(clips)==5
        if revision==5:
            assert rms(0,1)>.005,'Missing opening voice'
            offset=item['introFrames'];body_end=offset+item['bodyFrames']
            assert clips[0]['start']+clips[0]['duration']<offset
            assert clips[-1]['start']>=body_end
            if n==9:
                dialogue=[c for c in clips if offset<=c['start']<body_end]
                assert [c['voice'] for c in dialogue]==['en-GB-SoniaNeural','en-GB-RyanNeural']*4
                for i,c in enumerate(dialogue):assert c['start']+c['duration']<=offset+(i//2+1)*315-8
            if n==4:
                for start in [60,480,900]:assert rms((offset+start)/30,(offset+start+150)/30)<.001
        if revision==4:
            if n==4:
                assert clips[0]['voice']=='fr-FR-DeniseNeural' and rms(0,1)>.005
                delay=item['questionDelay']
                for start in [60+delay,480+delay,900+delay]:
                    assert rms(start/30,(start+150)/30)<.001,'Reflection must remain silent for five seconds'
            if n==9:
                assert [c['voice'] for c in clips]==['en-GB-SoniaNeural','en-GB-RyanNeural']*4
        if n==10:
            for i in range(3):
                start=(420*i+150)/30;end=(420*i+310)/30;energy=rms(start,end)
                assert energy<.001,'The repetition period must stay silent'
                repetition.append({'start':start,'end':end,'rms':energy})
        pauses=[]
        for a,b in zip(clips,clips[1:]):
            start=(a['start']+a['duration'])/30+.12;end=b['start']/30-.12
            if end-start>.3:
                energy=rms(start,end);assert energy<.001,f'Unexpected audio between clips: {key}, {start}'
                pauses.append({'start':round(start,3),'end':round(end,3),'rms':round(energy,7)})
        tail_start=(clips[-1]['start']+clips[-1]['duration'])/30+.12
        if item['frames']/30-tail_start>.4:
            assert rms(tail_start,item['frames']/30-.1)<.001,'Unexpected narration after the last scheduled clip'
        peak=max(abs(v) for v in pcm)/32768;assert peak<.99
        records=json.loads((folder/f'layout-qa{suffix}.json').read_text(encoding='utf-8'))
        assert len(records)==item['frames'] and not any(r['violations'] or not all(r['fonts']) for r in records)
        result={'key':key,'seconds':item['frames']/30,'frames':item['frames'],'fullVideoDecode':True,'fullAudioDecode':True,'layoutErrors':0,'centerErrorPx':max(r['centerError'] for r in records)*3,'voiceCues':len(clips),'peak':round(peak,5),'bytes':video.stat().st_size,'auditoryReview':False}
        (qa/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        (qa/'audio-qa.json').write_text(json.dumps({'cues':audio_checks,'silentWindows':pauses,'repetitionWindows':repetition,'dialogueEndsBeforePageFade':n==9,'peak':peak,'auditoryReview':False},indent=2,ensure_ascii=False),encoding='utf-8')
        (qa/'inspection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(result),flush=True)
    board=Image.new('RGB',(840,1020),'#E9E7ED');draw=ImageDraw.Draw(board)
    for j,(im,f) in enumerate(zip(images,item['captures'])):
        x=(j%3)*280+5;y=(j//3)*510+24;board.paste(im,(x,y));draw.text((x,y-18),f'{key} / {f/30:.1f}s',fill='#1E1B3A')
    board.save(folder/(f'planche-captures{suffix}.jpg' if stills else f'planche-test-option-{n}{suffix}.jpg'),quality=94)
