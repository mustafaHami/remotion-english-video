"""Decode the delivered MP4 and build visual inspection boards from real frames."""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
variant = next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--variant=')),None)
option = next((arg.split('=',1)[1] for arg in sys.argv if arg.startswith('--option=')),None)
if option not in (None,'1'):
    raise ValueError('Only option 1 has a produced video at this stage.')
slug = 'test-option-1' if option=='1' else f'test-style-v2-{variant}' if variant else 'test-style-v1'
option_config=json.loads((ROOT/'src/archive/experiments/test-option-1/render-config.json').read_text(encoding='utf-8')) if option=='1' else None
count = option_config['durationInFrames'] if option_config else 660 if variant else 480
OUT = ROOT / 'output/tests' / slug
BIN = ROOT / 'node_modules/@remotion/compositor-win32-x64-msvc'
VIDEO = OUT / (option_config['filename'] if option_config else f'{slug}.mp4')
QA = OUT / (option_config['qaDirectory'] if option_config else 'qa')
CAPTURES=OUT/(option_config['capturesDirectory'] if option_config else 'captures')
QA.mkdir(exist_ok=True)

probe = subprocess.run([str(BIN/'ffprobe.exe'), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(VIDEO)], capture_output=True, check=True)
metadata = json.loads(probe.stdout)
stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
assert (stream['codec_name'], stream['width'], stream['height'], stream['r_frame_rate'], stream['pix_fmt']) == ('h264',1080,1920,'30/1','yuv420p')
assert int(stream['nb_frames']) == count
assert abs(float(metadata['format']['duration'])-count/30) < .01
(QA/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
frames = subprocess.run([str(BIN/'ffmpeg.exe'),'-v','error','-xerror','-i',str(VIDEO),'-vf','scale=180:320','-c:v','rawvideo','-f','image2pipe','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
size = 180*320*3
assert len(frames) == size*count
def frame_image(frame):
    return Image.frombytes('RGB',(180,320),frames[frame*size:(frame+1)*size])
def board(name, indices, columns=8):
    rows=(len(indices)+columns-1)//columns
    result=Image.new('RGB',(columns*184,rows*342),'#E9E7ED')
    draw=ImageDraw.Draw(result)
    for i,frame in enumerate(indices):
        x=(i%columns)*184+2;y=(i//columns)*342+20
        result.paste(frame_image(frame),(x,y))
        draw.text((x,y-15),f'f{frame:03} / {frame/30:.2f}s',fill='#1E1B3A')
    result.save(QA/name)
if option=='1':
    board('overview.png',option_config['overview'])
    board('writing-past.png',list(range(208,251,3)))
    board('writing-future.png',list(range(868,919,3)))
    board('writing-last-row.png',list(range(1354,1407,3)))
    board('completion.png',list(range(1398,1433,3)))
    # Regression check for the observed disappearance during live SVG masking.
    # Measure actual dark text pixels in every completed cell of the decoded MP4.
    def ink_count(frame,row,col):
        left=round((24+104*col)*.5);right=round((24+104*(col+1))*.5)
        top=round((191.5+27*row)*.5);bottom=round((191.5+27*row+24)*.5)
        crop=frame_image(frame).crop((left,top,right,bottom))
        return sum(r<90 and g<90 and b<120 for r,g,b in crop.getdata())
    reference={(row,col):ink_count(count-1,row,col) for row in range(10) for col in range(3)}
    missing=[];checked=0;minimum_ratio=1.0
    for frame in range(60,count):
        for row in range(10):
            for col in range(3):
                completed_at=60 if col==0 else 210+row*48+36 if col==1 else 870+row*54+44
                if frame<completed_at:continue
                ratio=ink_count(frame,row,col)/max(1,reference[(row,col)])
                minimum_ratio=min(minimum_ratio,ratio);checked+=1
                if ratio<.55:missing.append({'frame':frame,'row':row,'column':col,'ratio':round(ratio,3)})
    report={'checkedCompletedCells':checked,'minimumInkRatio':round(minimum_ratio,4),'missing':missing}
    (QA/'visibility-qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert not missing, f'{len(missing)} completed text cells missing during playback'
elif variant:
    board('overview.png',[30,105,160,230,375,510,580,659])
    board('answer-motion.png',list(range(178,213,2)))
    board('swipe-tip.png',list(range(298,317)))
    board('swipe-recall.png',list(range(448,467)))
    board('recall-answer.png',list(range(553,582,2)))
    board('swipe-end.png',list(range(598,617)))
else:
    board('overview.png',[30,105,175,200,230,270,375,479])
    board('reorganization.png',list(range(52,101,4)))
    board('answer-motion.png',list(range(238,271,2)))
    board('swipe-tip.png',list(range(298,317)))
    board('swipe-end.png',list(range(418,437)))
    board('bell.png',list(range(454,471,2)))

# An accessible six-pose board at a more comfortable reading size.
result=Image.new('RGB',(1080,1320),'#E9E7ED')
for i,frame in enumerate(option_config['planche'] if option_config else [105,160,230,375,510,659] if variant else [30,105,200,270,375,479]):
    source=Image.open(CAPTURES/f'frame-{frame:03}.png').convert('RGB')
    source.thumbnail((350,622))
    x=(i%3)*360+5;y=(i//3)*660+25
    result.paste(source,(x,y))
    ImageDraw.Draw(result).text((x,y-18),f'{frame/30:.1f}s',fill='#1E1B3A')
result.save(OUT/(option_config['plancheFilename'] if option_config else f'planche-{slug}.jpg'),quality=94)
if variant or option=='1':
    # Schematic occlusion preview. Not a screenshot of the current platform UI.
    source=Image.open(CAPTURES/(f'frame-{count-1:03}.png' if option=='1' else 'frame-230.png')).convert('RGBA')
    overlay=Image.new('RGBA',source.size,(0,0,0,0));draw=ImageDraw.Draw(overlay)
    draw.rectangle((0,0,1080,192),fill=(30,27,58,70))
    draw.rectangle((900,870,1080,1524),fill=(30,27,58,70))
    draw.rectangle((0,1524,1080,1920),fill=(30,27,58,70))
    draw.line((60,192,60,1524),fill=(19,122,75,255),width=3)
    draw.text((72,1600),f'{(variant or "MOBILE").upper()} - SCHEMATIC SAFE AREA / NOT A LIVE UI',fill='white')
    Image.alpha_composite(source,overlay).convert('RGB').save(OUT/('apercu-mobile-v2.jpg' if option_config else 'apercu-zones-sures.jpg'),quality=94)
print(f'MP4: H.264, 1080 x 1920, 30 fps, {count} frames, {count/30:g} s; full decode OK.')
print('Visual boards:', QA)
