import bpy,json
from pathlib import Path
R=Path('D:/ai-generation-video/output/englizy/3d')
s=bpy.context.scene;s.frame_start=1;s.frame_end=180;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1
s.render.use_sequencer=True;s.render.use_compositing=False;s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.sequencer_colorspace_settings.name='sRGB'
st=s.sequence_editor_create().strips
bg=st.new_effect(name='Fond lavande clair',type='COLOR',channel=1,frame_start=1,length=180);bg.color=(234/255,229/255,1)
im=st.new_image(name='Logo 3D',filepath=str(R/'frames/frame-0001.png'),channel=2,frame_start=1)
for f in range(2,181):im.elements.append('frame-%04d.png'%f)
im.frame_final_duration=180;im.blend_type='ALPHA_OVER'
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';s.render.threads_mode='FIXED';s.render.threads=6
s.render.filepath=str(R/'englizy-logo-3d.mp4')
bpy.ops.render.render(animation=True)
clip=bpy.data.movieclips.load(s.render.filepath)
assert clip.frame_duration==180
assert tuple(clip.size)==(900,900)
report={'path':s.render.filepath,'frames':clip.frame_duration,'size':list(clip.size),'fps':30,'seconds':6,'bytes':Path(s.render.filepath).stat().st_size}
(R/'video-qa.json').write_text(json.dumps(report,indent=2))
print('ENCODE_VERIFIED',report,flush=True)
