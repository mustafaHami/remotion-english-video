import bpy,json,sys,argparse
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';m=json.loads((O/'manifest.json').read_text(encoding='utf8'));s=bpy.context.scene
s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.use_sequencer=True;s.render.use_compositing=False;s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.sequencer_colorspace_settings.name='sRGB';s.render.threads_mode='FIXED';s.render.threads=4
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE'
ed=s.sequence_editor_create();st=ed.strips
def clear():
    for x in list(st):st.remove(x)
def images(name,folder,n,start,channel):
    im=st.new_image(name=name,filepath=str(folder/'image-0001.png'),channel=channel,frame_start=start)
    for i in range(2,n+1):im.elements.append('image-%04d.png'%i)
    im.frame_final_duration=n;im.blend_type='ALPHA_OVER';return im
def back(n):bg=st.new_effect(name='Fond aperçu ivoire',type='COLOR',channel=1,frame_start=1,length=n);bg.color=(.956,.948,.913)
def title(text,start,n):
    c=next(c for c in m['clips'] if c['title']==text);x=st.new_image(name=text,filepath=str(O/'titres'/(c['id']+'.png')),channel=4,frame_start=start);x.frame_final_duration=n;x.blend_type='ALPHA_OVER'
def add(c,start):
    images(c['id'],O/'frames'/c['id'],c['frames'],start,2)
    if c['accessory']:images(c['accessory'],O/'accessoires'/c['accessory'],c['frames'],start,3)
    title(c['title'],start,c['frames'])
def render(path,n):
    s.frame_start=1;s.frame_end=n;s.render.filepath=str(path);bpy.ops.render.render(animation=True);clip=bpy.data.movieclips.load(str(path));assert clip.frame_duration==n,(path,clip.frame_duration,n);assert tuple(clip.size)==(s.render.resolution_x,s.render.resolution_y);fps=getattr(clip,'fps',30);assert abs(fps-30)<.01,(path,fps);return {'path':str(path),'frames':clip.frame_duration,'size':list(clip.size),'fps':fps,'bytes':path.stat().st_size}
videos=O/'apercus';videos.mkdir(exist_ok=True);report=[]
for c in m['clips']:
    clear();back(c['frames']);add(c,1);path=videos/(c['id']+'.mp4');report.append(render(path,c['frames']));print('VIDEO_VERIFIED',c['id'],flush=True)
clear();n=sum(c['frames'] for c in m['clips']);back(n);start=1
for c in m['clips']:add(c,start);start+=c['frames']
report.append(render(O/'renard-bibliotheque-mouvements-v2.mp4',n))
# Vertical reference, without a lesson: body clips are unchanged, merely centred by the VSE.
clear();s.render.resolution_x=1080;s.render.resolution_y=1920;chosen=[next(c for c in m['clips'] if c['id']==id) for id in ['marche','arreter-marche','se-lever','presenter-gauche','decouvrir','bravo','saluer']];n=sum(c['frames'] for c in chosen);back(n);start=1
for c in chosen:add(c,start);start+=c['frames']
report.append(render(O/'reference-verticale-1080x1920.mp4',n));(O/'verification-videos.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('VIDEOS_ALL_DONE',flush=True)
