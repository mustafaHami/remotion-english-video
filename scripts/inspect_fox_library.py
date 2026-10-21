import bpy,json,math,time
from pathlib import Path
from mathutils import Vector
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';O.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];body=bpy.data.objects['Renard · corps continu et mains']
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
print('INSPECT',json.dumps({'actions':[(a.name,list(a.frame_range)) for a in bpy.data.actions], 'mods':[(m.name,m.type) for m in body.modifiers],'lights':[(o.name,list(o.location),o.data.energy) for o in s.objects if o.type=='LIGHT'],'body_attributes':list(body.data.attributes.keys())},ensure_ascii=False),flush=True)
rig.animation_data.action=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));route.animation_data_clear();route.location=(0,0,0);s.frame_set(1)
vg=body.vertex_groups.new(name='Lissage articulations V2')
for v in body.data.vertices:
    z=v.co.z; w=max(math.exp(-((z-2.85)/.40)**2),math.exp(-((z-4.38)/.30)**2))
    if w>.01:vg.add([v.index],w,'REPLACE')
m=body.modifiers.new('Transitions articulaires · V2','SMOOTH');m.vertex_group=vg.name;m.factor=1;m.iterations=18
# Put local smoothing immediately after the armature.
while body.modifiers.find(m.name)>1:bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_move_up(modifier=m.name)
d=bpy.data.cameras.new('Bibliothèque · caméra fixe');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam);cam.location=(-11,-17,7);cam.rotation_euler=(Vector((-.1,0,3.15))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=8.6;s.camera=cam
s.render.resolution_x=384;s.render.resolution_y=384;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.use_sequencer=False;s.render.use_compositing=False;s.render.threads_mode='FIXED';s.render.threads=6
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.08;s.cycles.max_bounces=3
tm=time.monotonic();s.render.filepath=str(O/'diagnostic-cycles.png');bpy.ops.render.render(write_still=True);print('CYCLES_SECONDS',time.monotonic()-tm,flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/renard-bibliotheque-v2.blend'));print('SAVED_LIBRARY_BASE',flush=True)
