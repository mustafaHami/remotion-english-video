import bpy,math,time,json
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant']
# Add the visible gaze control to the animated shader sliders.
for side in [-1,1]:
    eye=bpy.data.objects['V5 · Œil '+str(side)]
    for nodeName,prop,transform in [('Regard horizontal','regard_horizontal','LOC_X'),('Regard vertical','regard_vertical','LOC_Y')]:
        socket=eye.data.materials[0].node_tree.nodes[nodeName].outputs[0];socket.driver_remove('default_value');d=socket.driver_add('default_value').driver;d.expression='v+t*.04';v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["'+prop+'"]';v=d.variables.new();v.name='t';v.type='TRANSFORMS';v.targets[0].id=rig;v.targets[0].bone_target='CTRL_regard';v.targets[0].transform_type=transform;v.targets[0].transform_space='LOCAL_SPACE'
for f in rig.animation_data.drivers:
    if 'D_doigt' in f.data_path or 'D_pouce' in f.data_path:f.driver.expression='-v*.7'
walk=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));pres=next(a for a in bpy.data.actions if a.name.startswith('TEST_02'));walkroute=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_01'));presroute=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_02'))
s.render.engine='CYCLES';s.cycles.samples=32;s.render.fps=30;s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.film_transparent=True;s.render.image_settings.color_mode='RGBA';s.render.image_settings.file_format='PNG'
rig.animation_data.action=walk;route.animation_data.action=walkroute;s.frame_end=180;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · portrait 1080x1920'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
studio=bpy.data.collections['04 — Studio · cameras et lumières'];d=bpy.data.cameras.new('EXPORT · présentation portrait');cam=bpy.data.objects.new('EXPORT · présentation portrait',d);studio.objects.link(cam);cam.location=(-17,-12,5);cam.rotation_euler=(Vector((-.65,.1,3.25))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=7.4
rig.animation_data.action=pres;route.animation_data.action=presroute;s.frame_end=150;s.frame_set(2);s.frame_set(1);s.camera=cam;s['statut']='EXPRESSION V5 + TESTS D’ARTICULATION — non validés';s['actions']='TEST_01 Marche 6 s ; TEST_02 Présentation 5 s ; trajectoires séparées';s.render.filepath=str(OUT/'export/presentation-')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-presentation-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));print('FILES_SAVED',flush=True)
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=540;s.render.resolution_y=960;s.render.filepath=str(OUT/'test-natif/image-');s.frame_start=1;s.frame_end=12
if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=8
s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_persistent_data=True
print('NATIVE_RENDER_START',flush=True);tm=time.monotonic();bpy.ops.render.render(animation=True);print('NATIVE_RENDER_DONE_SECONDS',time.monotonic()-tm,flush=True)
