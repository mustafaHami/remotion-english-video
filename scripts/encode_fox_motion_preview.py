import bpy,json,sys,argparse
from pathlib import Path
ROOT=Path('D:/ai-generation-video/output/blender/rig-v1');p=argparse.ArgumentParser();p.add_argument('--clip',default='presentation');args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);name=args.clip;w,h,n=(540,960,150) if name=='presentation' else (1280,720,180)
s=bpy.context.scene;s.frame_start=1;s.frame_end=n;s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.use_sequencer=True;s.render.use_compositing=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.film_transparent=False;s.sequencer_colorspace_settings.name='sRGB'
ed=s.sequence_editor_create();strips=ed.strips if hasattr(ed,'strips') else ed.sequences;bg=strips.new_effect(name='Fond ivoire',type='COLOR',channel=1,frame_start=1,length=n);bg.color=(.956,.948,.913);folder=ROOT/(name+'-frames');im=strips.new_image(name='Rendu Blender',filepath=str(folder/'image-0001.png'),channel=2,frame_start=1)
for f in range(2,n+1):im.elements.append('image-%04d.png'%f)
im.blend_type='ALPHA_OVER'
if hasattr(im,'frame_final_duration'):im.frame_final_duration=n
elif hasattr(im,'length'):im.length=n
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='NONE';s.render.filepath=str(ROOT/('renard-'+name+'-test-v1.mp4'));s.render.threads_mode='FIXED';s.render.threads=4
print('ENCODE_START',name,flush=True);bpy.ops.render.render(animation=True);print('ENCODE_DONE',name,flush=True)
clip=bpy.data.movieclips.load(s.render.filepath);report={'path':s.render.filepath,'frames':clip.frame_duration,'size':list(clip.size),'fps':30,'seconds':clip.frame_duration/30,'bytes':Path(s.render.filepath).stat().st_size};(ROOT/('verification-video-'+name+'.json')).write_text(json.dumps(report,indent=2),encoding='utf8');assert clip.frame_duration==n,report;assert tuple(clip.size)==(w,h),report;print('VIDEO_VERIFIED',json.dumps(report),flush=True)
