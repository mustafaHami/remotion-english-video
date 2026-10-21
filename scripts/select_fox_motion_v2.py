"""Blender: exec(open(...).read()) or --python ... -- --clip reflechir."""
import bpy,json,sys,argparse
from pathlib import Path
ROOT=Path('D:/ai-generation-video');folder=ROOT/'output/blender/mouvements-v2';manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
p=argparse.ArgumentParser();p.add_argument('--clip',default='attente');p.add_argument('--save',default='');args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
c=next(x for x in manifest['clips'] if x['id']==args.clip);rig=bpy.data.objects['RIG · Renard'];rig.animation_data.action=bpy.data.actions[c['action']]
for name,action in c['accessoryActions'].items():bpy.data.objects[name].animation_data.action=bpy.data.actions[action]
route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];route.animation_data_clear();route.location=(0,0,0)
s=bpy.context.scene;s.frame_start=1;s.frame_end=c['frames'];s.frame_set(1);s.camera=bpy.data.objects[manifest['camera']];s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.fps=30;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
for mark in list(s.timeline_markers):s.timeline_markers.remove(mark)
s.timeline_markers.new(c['title'],frame=1);s.timeline_markers.new('Fin / '+c['exit'],frame=c['frames'])
print('ACTIVE_CLIP',c['id'],c['frames'],flush=True)
if args.save:bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.save)))
