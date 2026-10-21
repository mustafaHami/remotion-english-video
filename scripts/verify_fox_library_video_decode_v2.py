import bpy,json
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';s=bpy.context.scene;s.render.use_sequencer=True;s.render.use_compositing=False;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.sequencer_colorspace_settings.name='sRGB';s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.resolution_percentage=100;s.render.fps=30;st=s.sequence_editor_create().strips;report=[]
def load(path,w,h):
    for strip in list(st):st.remove(strip)
    st.new_movie(name='Vidéo réellement livrée',filepath=str(path),channel=1,frame_start=1);s.render.resolution_x=w;s.render.resolution_y=h
load(O/'renard-bibliotheque-mouvements-v2.mp4',768,768)
for id,f in [('marche',258),('se-lever',378),('presenter-haut',693),('decouvrir',903),('examiner-loupe',1008),('bravo',1113),('ecouter',1293),('saluer',1473)]:
    s.frame_set(f);out=O/('lecture-video-'+id+'.png');s.render.filepath=str(out);bpy.ops.render.render(write_still=True);report.append({'video':'renard-bibliotheque-mouvements-v2.mp4','frame':f,'image':out.name})
load(O/'reference-verticale-1080x1920.mp4',1080,1920);s.frame_set(267);s.render.filepath=str(O/'lecture-video-verticale.png');bpy.ops.render.render(write_still=True);report.append({'video':'reference-verticale-1080x1920.mp4','frame':267,'image':'lecture-video-verticale.png'})
(O/'verification-decodage-videos.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('REAL_VIDEO_DECODE_DONE',flush=True)
