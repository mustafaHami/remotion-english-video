import bpy,json
from pathlib import Path
ROOT=Path('D:/ai-generation-video/output/blender/rig-v1');s=bpy.context.scene;s.render.use_sequencer=True;s.render.use_compositing=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.sequencer_colorspace_settings.name='sRGB';s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.resolution_percentage=100;s.render.fps=30;ed=s.sequence_editor_create();strips=ed.strips
for name,w,h,f in [('presentation',540,960,65),('marche',1280,720,175)]:
    for strip in list(strips):strips.remove(strip)
    strip=strips.new_movie(name='Vidéo livrée',filepath=str(ROOT/('renard-'+name+'-test-v1.mp4')),channel=1,frame_start=1);s.render.resolution_x=w;s.render.resolution_y=h;s.frame_set(f);s.render.filepath=str(ROOT/('lecture-video-'+name+'.png'));bpy.ops.render.render(write_still=True);print('VIDEO_DECODED',name,flush=True)
