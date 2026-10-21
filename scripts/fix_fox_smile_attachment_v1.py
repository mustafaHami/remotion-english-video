import bpy,json
from mathutils import Vector
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];head=bpy.data.objects['Renard · tête et museau sculptés']
proxy=bpy.data.objects.get('Support interne · sourire sur le visage')
if proxy is None:
    proxy=head.copy();proxy.data=head.data.copy();proxy.name='Support interne · sourire sur le visage';bpy.data.collections['90 — Construction · volumes sources'].objects.link(proxy)
for m in list(proxy.modifiers):
    if m.type!='SUBSURF':proxy.modifiers.remove(m)
proxy.hide_render=True;proxy.hide_set(True)
for side in [-1,1]:
    o=bpy.data.objects['V5 · Sourire chaleureux '+str(side)];m=o.modifiers.get('Sourire · contact avec la joue') or o.modifiers.new('Sourire · contact avec la joue','SHRINKWRAP');m.target=proxy;m.wrap_method='NEAREST_SURFACEPOINT';m.wrap_mode='ABOVE_SURFACE';m.offset=.004;bpy.context.view_layer.objects.active=o
    while o.modifiers.find(m.name)>0:bpy.ops.object.modifier_move_up(modifier=m.name)
walk=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));pres=next(a for a in bpy.data.actions if a.name.startswith('TEST_02'));wr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_01'));pr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_02'))
rig.animation_data.action=walk;route.animation_data.action=wr;s.frame_end=180;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · portrait 1080x1920'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
rig.animation_data.action=pres;route.animation_data.action=pr;s.frame_end=150;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · présentation portrait'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-presentation-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));print('MOUTH_ATTACHMENT_SAVED',flush=True)
s.frame_set(65);s.camera=bpy.data.objects['V4 · tête trois quarts'];s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=10;s.render.resolution_x=800;s.render.resolution_y=800;s.render.filepath=str(OUT/'controle-sourire-articule.png');bpy.ops.render.render(write_still=True);print('MOUTH_ATTACHMENT_RENDERED',flush=True)
