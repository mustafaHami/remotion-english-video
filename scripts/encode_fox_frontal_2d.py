import bpy,json
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/renard-frontal-2d';s=bpy.context.scene;s.render.resolution_x=1774;s.render.resolution_y=888;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.use_sequencer=True;s.render.use_compositing=False;s.render.film_transparent=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.sequencer_colorspace_settings.name='sRGB';s.frame_start=1;s.frame_end=180
st=s.sequence_editor_create().strips;bg=st.new_effect(name='Fond aperçu ivoire',type='COLOR',channel=1,frame_start=1,length=180);bg.color=(.956,.948,.913);im=st.new_image(name='Animation 2D réellement rendue dans Blender',filepath=str(O/'frames/image-0001.png'),channel=2,frame_start=1)
for f in range(2,181):im.elements.append('image-%04d.png'%f)
im.frame_final_duration=180;im.blend_type='ALPHA_OVER';im.transform.offset_y=.5;s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';s.render.filepath=str(O/'renard-frontal-2d-exemple.mp4');bpy.ops.render.render(animation=True)
clip=bpy.data.movieclips.load(s.render.filepath);assert clip.frame_duration==180 and tuple(clip.size)==(1774,888);report={'file':s.render.filepath,'frames':clip.frame_duration,'size':list(clip.size),'fps':clip.fps,'seconds':6,'previewPadding':'one ivory row for H.264; original transparent PNGs remain 1774x887'};assert abs(clip.fps-30)<.01
# Decode a frame from the actual MP4 for visual QA.
for x in list(st):st.remove(x)
st.new_movie(name='Aperçu encodé',filepath=s.render.filepath,channel=1,frame_start=1);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(47);s.render.filepath=str(O/'lecture-video-clignement.png');bpy.ops.render.render(write_still=True)
(O/'verification-video.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('VIDEO_VERIFIED',json.dumps(report),flush=True)
