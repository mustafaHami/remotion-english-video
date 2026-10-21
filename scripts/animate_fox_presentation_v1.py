import bpy,math,json,time
from mathutils import Vector,Matrix,Quaternion
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];ad=rig.data;route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant']
walk=rig.animation_data.action;walkroute=route.animation_data.action;rig.animation_data.action=None;route.animation_data.action=None
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def blend(a,b,t):t=smooth(t);return {a:1-t,b:t}
def mixweights(a,b,t):
    out={k:v*(1-t) for k,v in a.items()}
    for k,v in b.items():out[k]=out.get(k,0)+v*t
    return out
def skin(o,fn):
    o.vertex_groups.clear();buckets={}
    for v in o.data.vertices:
        weights={k:round(max(0,w)*4096) for k,w in fn(v.co).items() if w>.001};total=sum(weights.values())
        if not total:raise RuntimeError('Unweighted vertex '+o.name)
        for name,w in weights.items():
            if w:buckets.setdefault((name,round(w/total,5)),[]).append(v.index)
    groups={name:o.vertex_groups.new(name=name) for name in set(k[0] for k in buckets)}
    for (name,w),ids in buckets.items():groups[name].add(ids,w,'REPLACE')
    mod=o.modifiers.new('Squelette · volumes préservés','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    bpy.context.view_layer.objects.active=o
    while o.modifiers.find(mod.name)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    o.parent=rig

def segdist(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-(a+t*d)).length
fingersegments={}
for tag in ['G','D']:
    fingersegments[tag]=[(b.name,b.head_local.copy(),b.tail_local.copy()) for b in ad.bones if b.name.endswith('.'+tag) and ('D_doigt' in b.name or 'D_pouce' in b.name)]
def bodyweights(p):
    x,y,z=p;tag='G' if x<0 else 'D';ax=abs(x)
    if z<3.05 and ax<.67:
        if z<.42:return blend('D_pied.'+tag,'D_jambe.'+tag,(z-.20)/.23)
        if z<1.9:return blend('D_jambe.'+tag,'D_cuisse.'+tag,(z-1.45)/.4)
        return mixweights({'CTRL_corps':1},blend('D_cuisse.'+tag,'CTRL_corps',(z-2.65)/.37),smooth((ax-.065)/.16))
    if z<3.35:torso={'CTRL_corps':1}
    elif z<3.85:torso=blend('CTRL_corps','CTRL_colonne',(z-3.2)/.5)
    elif z<4.35:torso=blend('CTRL_colonne','CTRL_poitrine',(z-3.65)/.45)
    else:torso=blend('CTRL_poitrine','CTRL_cou',(z-4.55)/.35)
    cutoff=(.32+.08*smooth((4.55-z)/.25)) if z>4.3 else (.40+.13*smooth((4.3-z)/1.0)) if z>3.3 else .58
    armfac=smooth((ax-cutoff)/.075)
    if armfac<=0:return torso
    if z<2.78:
        distances=sorted((segdist(p,a,b),name) for name,a,b in fingersegments[tag])[:2];vals={name:1/max(.012,d)**4 for d,name in distances};tot=sum(vals.values());fw={k:v/tot for k,v in vals.items()};limb=mixweights(fw,{'D_main.'+tag:1},smooth((z-2.68)/.12))
    elif z<3.1:limb=blend('D_main.'+tag,'D_avant_bras.'+tag,(z-2.88)/.18)
    else:limb=blend('D_avant_bras.'+tag,'D_bras.'+tag,(z-3.49)/.32)
    return mixweights(torso,limb,armfac)

body=bpy.data.objects['Renard · corps continu et mains']
for m in list(body.modifiers):
    if m.type in ['ARMATURE','CORRECTIVE_SMOOTH']:body.modifiers.remove(m)
skin(body,bodyweights)
mods=[m for o in bpy.data.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
ctrls=[p for p in rig.pose.bones if p.name.startswith('CTRL_')]
def placeQ(name,pos,q):p=rig.pose.bones[name];p.matrix=Matrix.Translation(Vector(pos))@q.to_matrix().to_4x4()@ad.bones[name].matrix_local.to_3x3().to_4x4()
def place(name,pos,rx=0):placeQ(name,pos,Quaternion((1,0,0),math.radians(rx)))

# Refine the crouch and keep the scarf above the ground.
rig.animation_data.action=walk;route.animation_data.action=walkroute
for frame in range(1,181):
    s.frame_set(frame);pb=rig.pose.bones['CTRL_corps'];pb.location.y+=.15;pb.rotation_quaternion=Quaternion((1,0,0),math.radians(5))@pb.rotation_quaternion;pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
    pb=rig.pose.bones['CTRL_cou'];pb.rotation_quaternion=Quaternion((1,0,0),math.radians(-5))@pb.rotation_quaternion;pb.keyframe_insert('rotation_quaternion',frame=frame);bpy.context.view_layer.update()
    pb=rig.pose.bones['CTRL_foulard'];pos=pb.matrix.translation.copy();place('CTRL_foulard',pos,-20);pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame)
rig.animation_data.action=None;route.animation_data.action=None

for frame in range(1,151):
    s.frame_set(frame);t=(frame-1)/30;gesture=smooth((frame-18)/30)*(1-smooth((frame-112)/28))
    for p in ctrls:p.matrix_basis.identity()
    route.location=(0,0,0);route.keyframe_insert('location',frame=frame)
    place('CTRL_corps',(0,.02,2.75+.008*math.sin(t*math.tau/3)),0)
    rig.pose.bones['CTRL_poitrine'].rotation_quaternion=Quaternion((1,0,0),math.radians(-.8*gesture))
    rig.pose.bones['CTRL_cou'].rotation_quaternion=Quaternion((1,0,0),math.radians(1.5*gesture))
    rig.pose.bones['CTRL_tete'].rotation_quaternion=Quaternion((0,1,0),math.radians(-7*gesture))@Quaternion((0,0,1),math.radians(-3*gesture))
    bpy.context.view_layer.update()
    for side in [-1,1]:
        tag='G' if side<0 else 'D';g=gesture if side<0 else 0;start=Vector((side*.885,-.17,2.95));end=Vector((-1.18,-.52,4.05));pos=start.lerp(end,g);pos.z+=.018*math.sin(t*3)*g
        handQ=Quaternion((0,0,1),math.radians(-35*g))@Quaternion((1,0,0),math.radians(-85*g));placeQ('CTRL_main.'+tag,pos,handQ)
        place('CTRL_pied.'+tag,(side*.4,.03,.24));place('CTRL_genou.'+tag,(side*.4,-1.7,1.5));place('CTRL_coude.'+tag,Vector((side*.8,1.4,3.7)).lerp(Vector((-1.5,.35,3.6)),g))
        rig.pose.bones['CTRL_oreille.'+tag].rotation_quaternion=Quaternion((1,0,0),math.radians(2*math.sin(t*2+.7*side)))
    bpy.context.view_layer.update()
    pos=rig.pose.bones['CTRL_queue_0'].matrix.translation.copy();placeQ('CTRL_queue_0',pos,Quaternion((0,0,1),.025*math.sin(t*2)))
    for j in range(1,6):rig.pose.bones['CTRL_queue_%d'%j].rotation_quaternion=Quaternion((0,1,0),.025*math.sin(t*2-j*.45))
    pos=rig.pose.bones['CTRL_foulard'].matrix.translation.copy();place('CTRL_foulard',pos,0);rig.pose.bones['CTRL_foulard_pointe'].rotation_quaternion=Quaternion((1,0,0),.01*math.sin(t*2))
    rig['clignement']=max(max(0,1-abs(frame-c)/3) for c in [38,117]);rig['sourire']=.35+.35*gesture;rig['curieux']=.14*gesture;rig['regard_horizontal']=.024-.025*gesture;rig['regard_vertical']=.008+.004*gesture
    for prop in ['clignement','sourire','curieux','regard_horizontal','regard_vertical']:rig.keyframe_insert(data_path='["'+prop+'"]',frame=frame)
    for p in ctrls:p.keyframe_insert('location',frame=frame);p.keyframe_insert('rotation_quaternion',frame=frame);p.keyframe_insert('scale',frame=frame)
    if frame%30==0:print('PRESENTATION_KEYED',frame,flush=True)
presentation=rig.animation_data.action;presentation.name='TEST_02 · Présentation souriante';presentation.use_fake_user=True;presroute=route.animation_data.action;presroute.name='TRAJET_02 · Présentation sur place';presroute.use_fake_user=True
for m in mods:m.show_viewport=True
# Keep both actions and their separate trajectory in the editable files.
rig.animation_data.action=walk;route.animation_data.action=walkroute;s.frame_end=180;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects['EXPORT · portrait 1080x1920'];s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.engine='CYCLES';s.render.fps=30;s.cycles.samples=32;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
rig.animation_data.action=presentation;route.animation_data.action=presroute;s.frame_end=150;s.frame_set(2);s.frame_set(1);s.camera=bpy.data.objects.get('V4 · contexte plein pied') or bpy.data.objects['EXPORT · portrait 1080x1920'];s['statut']='EXPRESSION V5 + TESTS D’ARTICULATION — non validés';s['actions']='TEST_01 Marche 6 s ; TEST_02 Présentation 5 s ; trajectoires séparées'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-presentation-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));print('PRESENTATION_SAVED',flush=True)
# Native animation rendering keeps the engine alive between frames.
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=540;s.render.resolution_y=960;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(OUT/'test-natif/image-');s.frame_start=1;s.frame_end=12
if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=8
s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_persistent_data=True
print('NATIVE_RENDER_START',flush=True);tm=time.monotonic();bpy.ops.render.render(animation=True);print('NATIVE_RENDER_DONE_SECONDS',time.monotonic()-tm,flush=True)
