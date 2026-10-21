import bpy,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];walk=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));pres=next(a for a in bpy.data.actions if a.name.startswith('TEST_02'));wr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_01'));pr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_02'));rig.animation_data.action=walk;route.animation_data.action=wr
objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and any(m.type=='ARMATURE' for m in o.modifiers)];points=[]
for frame in range(1,181):
    s.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    for o in objs:
        eo=o.evaluated_get(dg);points.extend(eo.matrix_world@Vector(v) for v in eo.bound_box)
    if frame%45==0:print('BOUNDS',frame,flush=True)
report={}
for name,aspect in [('RIG · contrôle trois quarts',16/9),('RIG · contrôle profil',16/9),('EXPORT · portrait 1080x1920',9/16)]:
    cam=bpy.data.objects[name];inv=cam.matrix_world.inverted();pp=[inv@p for p in points];x0=min(p.x for p in pp);x1=max(p.x for p in pp);y0=min(p.y for p in pp);y1=max(p.y for p in pp);cam.location+=cam.matrix_world.to_3x3()@Vector(((x0+x1)/2,(y0+y1)/2,0));s.render.resolution_x=1600 if aspect>1 else 900;s.render.resolution_y=900 if aspect>1 else 1600;cam.data.ortho_scale=1;vf=cam.data.view_frame(scene=s);fw=max(p.x for p in vf)-min(p.x for p in vf);fh=max(p.y for p in vf)-min(p.y for p in vf);cam.data.ortho_scale=max((y1-y0)/fh,(x1-x0)/fw)*1.12;report[name]={'ortho_scale':cam.data.ortho_scale,'location':list(cam.location),'tested_frames':180}
s.render.resolution_x=1080;s.render.resolution_y=1920;s.frame_end=180;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · portrait 1080x1920'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
rig.animation_data.action=pres;route.animation_data.action=pr;s.frame_end=150;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · présentation portrait'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-presentation-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));(OUT/'verification-cadrage-camera.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('CAMERAS_FITTED',json.dumps(report),flush=True)
