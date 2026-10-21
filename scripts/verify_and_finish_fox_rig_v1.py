import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];ad=rig.data
walk=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));pres=next(a for a in bpy.data.actions if a.name.startswith('TEST_02'));wr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_01'));pr=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_02'))
mods=[m for o in bpy.data.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
rig.animation_data.action=walk;route.animation_data.action=wr
for frame in range(1,181):
    s.frame_set(frame);t=frame-1;q=t if t<108 else 108+36*(((t-108)/36)-((t-108)/36)**2/2) if t<144 else 126;phase=q/36*math.tau;u=max(0,min(1,(t-108)/36));walkfactor=1-u*u*(3-2*u);pb=rig.pose.bones['CTRL_corps'];pb.matrix=Matrix.Translation(Vector((.018*math.sin(phase),.8,2.01+.018*math.cos(phase*2)*walkfactor)))@Matrix.Rotation(math.radians(105+.6*math.sin(phase*2)*walkfactor),4,'X')@ad.bones[pb.name].matrix_local.to_3x3().to_4x4();pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
    bpy.context.view_layer.update();pb=rig.pose.bones['CTRL_queue_0'];pos=pb.matrix.translation.copy();t=frame-1;q=t if t<108 else 108+36*(((t-108)/36)-((t-108)/36)**2/2) if t<144 else 126;phase=q/36*math.tau;u=max(0,min(1,(t-108)/36));u=u*u*(3-2*u);v=max(0,min(1,(t-148)/22));v=v*v*(3-2*v);rot=Quaternion((0,0,1),.04*math.sin(phase-.4)*(1-u)+.025*v)@Vector((-2.53,.6,-2.09)).rotation_difference(Vector((-.55,3.1,-.65)));pb.matrix=Matrix.Translation(pos)@rot.to_matrix().to_4x4()@ad.bones[pb.name].matrix_local.to_3x3().to_4x4();pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
report={'blender':bpy.app.version_string,'bones':len(ad.bones),'actions':[a.name for a in bpy.data.actions],'body_vertices':len(bpy.data.objects['Renard · corps continu et mains'].data.vertices),'clips':{},'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest(),'reference_packed':any(i.packed_file for i in bpy.data.images)}
for label,action,ra,end in [('marche',walk,wr,180),('presentation',pres,pr,150)]:
    rig.animation_data.action=action;route.animation_data.action=ra;maxerr=0
    for f in range(1,end+1):
        s.frame_set(f);bpy.context.view_layer.update();er=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for tag in ['G','D']:
            for deform,goal in [('D_avant_bras.','CTRL_main.'),('D_jambe.','CTRL_pied.')]:maxerr=max(maxerr,(er.pose.bones[deform+tag].tail-er.pose.bones[goal+tag].head).length)
    report['clips'][label]={'frames':end,'fps':30,'seconds':end/30,'max_ik_error':maxerr}
for m in mods:m.show_viewport=True
body=bpy.data.objects['Renard · corps continu et mains'];report['weights_missing']=sum(not v.groups for v in body.data.vertices);report['weight_sum_max_error']=max(abs(sum(g.weight for g in v.groups)-1) for v in body.data.vertices)
# Check the deformed body at a few important poses, without viewport subdivision.
submods=[m for m in body.modifiers if m.type=='SUBSURF']
for m in submods:m.show_viewport=False
report['deformation_samples']=[]
for label,action,ra,frames in [('marche',walk,wr,[1,20,70,120,175]),('presentation',pres,pr,[1,65,120])]:
    rig.animation_data.action=action;route.animation_data.action=ra
    for f in frames:
        s.frame_set(f);bpy.context.view_layer.update();eo=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=eo.to_mesh();zs=[(eo.matrix_world@v.co).z for v in me.vertices];report['deformation_samples'].append({'clip':label,'frame':f,'min_body_z':min(zs),'max_body_z':max(zs)});eo.to_mesh_clear()
for m in submods:m.show_viewport=True
rig.animation_data.action=walk;route.animation_data.action=wr;s.frame_end=180;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · portrait 1080x1920'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
rig.animation_data.action=pres;route.animation_data.action=pr;s.frame_end=150;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · présentation portrait'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-presentation-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'))
(OUT/'verification-rig-finale.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('RIG_VERIFIED',json.dumps(report),flush=True)
