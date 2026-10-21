import bpy,math,json,time
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene
COL=bpy.data.collections.new('05 — Articulation · contrôles');s.collection.children.link(COL)
route=bpy.data.objects.new('TRAJECTOIRE · déplacement indépendant',None);COL.objects.link(route);route.empty_display_type='ARROWS';route.empty_display_size=.7
ad=bpy.data.armatures.new('Renard · squelette déformant');rig=bpy.data.objects.new('RIG · Renard',ad);COL.objects.link(rig);rig.parent=route;rig.show_in_front=True
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(n,h,t,p=None,deform=True,connect=False):
    b=ad.edit_bones.new(n);b.head=h;b.tail=t;b.use_deform=deform
    if p:b.parent=ad.edit_bones[p];b.use_connect=connect
    return b
bone('CTRL_global',(0,0,0),(0,0,.35),deform=False)
bone('CTRL_corps',(0,.02,2.75),(0,.02,3.2),'CTRL_global')
bone('CTRL_colonne',(0,.02,3.2),(0,.02,3.85),'CTRL_corps')
bone('CTRL_poitrine',(0,.02,3.85),(0,.02,4.65),'CTRL_colonne')
bone('CTRL_cou',(0,.04,4.65),(0,.04,5.15),'CTRL_poitrine')
bone('CTRL_tete',(0,.04,5.15),(0,.04,5.70),'CTRL_cou')
bone('CTRL_regard',(0,-2,5.55),(0,-2,5.8),'CTRL_global',False)
for side in [-1,1]:
    tag='G' if side<0 else 'D'
    shoulder=(side*.48,.02,4.4);elbow=(side*.75,-.04,3.65);wrist=(side*.885,-.17,2.95);hand=(side*.89,-.26,2.56)
    hip=(side*.29,.02,2.85);knee=(side*.4,-.02,1.65);ankle=(side*.4,.03,.24);toe=(side*.4,-.36,.12)
    bone('D_bras.'+tag,shoulder,elbow,'CTRL_poitrine');bone('D_avant_bras.'+tag,elbow,wrist,'D_bras.'+tag,True,True);bone('D_main.'+tag,wrist,hand,'D_avant_bras.'+tag,True,True)
    bone('D_cuisse.'+tag,hip,knee,'CTRL_corps');bone('D_jambe.'+tag,knee,ankle,'D_cuisse.'+tag,True,True);bone('D_pied.'+tag,ankle,toe,'D_jambe.'+tag,True,True)
    bone('CTRL_main.'+tag,wrist,hand,'CTRL_global',False);bone('CTRL_pied.'+tag,ankle,toe,'CTRL_global',False)
    bone('CTRL_coude.'+tag,(side*.8,1.4,3.7),(side*.8,1.4,3.95),'CTRL_global',False);bone('CTRL_genou.'+tag,(side*.4,-1.7,1.5),(side*.4,-1.7,1.75),'CTRL_global',False)
    for j,length in enumerate([.25,.32,.30,.24]):
        x=side*(.796+j*.062);h=(x,-.195,2.74);mid=(x+side*.005,-.235,2.74-length*.5);end=(x+side*.008,-.28,2.74-length)
        bone('D_doigt%dA.%s'%(j,tag),h,mid,'D_main.'+tag);bone('D_doigt%dB.%s'%(j,tag),mid,end,'D_doigt%dA.%s'%(j,tag),True,True)
    bone('D_pouceA.'+tag,(side*.80,-.20,2.89),(side*.747,-.275,2.79),'D_main.'+tag);bone('D_pouceB.'+tag,(side*.747,-.275,2.79),(side*.783,-.314,2.65),'D_pouceA.'+tag,True,True)
    bone('CTRL_oreille.'+tag,(side*.335,.12,5.65),(side*.46,.15,5.98),'CTRL_tete');bone('D_oreille_pointe.'+tag,(side*.46,.15,5.98),(side*.557,.18,6.19),'CTRL_oreille.'+tag,True,True)
tailpoints=[(0,.29,2.69),(-.35,.66,2.48),(-.85,.94,2.15),(-1.36,1.08,1.77),(-1.86,1.08,1.30),(-2.23,1,.93),(-2.53,.89,.60)]
for j in range(6):bone('CTRL_queue_%d'%j,tailpoints[j],tailpoints[j+1],'CTRL_corps' if j==0 else 'CTRL_queue_%d'%(j-1),True,j>0)
bone('CTRL_foulard',(-.23,-.39,4.68),(-.25,-.43,3.98),'CTRL_cou');bone('CTRL_foulard_pointe',(-.25,-.43,3.98),(-.27,-.40,3.13),'CTRL_foulard',True,True)
bpy.ops.object.mode_set(mode='OBJECT');ad.display_type='OCTAHEDRAL'
controls=ad.collections.new('Contrôles');deforms=ad.collections.new('Déformation');deforms.is_visible=False
for b in ad.bones:(controls if b.name.startswith('CTRL_') else deforms).assign(b)
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION';pb.ik_stretch=0
for tag in ['G','D']:
    for lower,goal,pole in [('D_avant_bras.','CTRL_main.','CTRL_coude.'),('D_jambe.','CTRL_pied.','CTRL_genou.')]:
        c=rig.pose.bones[lower+tag].constraints.new('IK');c.name='Appui IK · sans étirement';c.target=rig;c.subtarget=goal+tag;c.pole_target=rig;c.pole_subtarget=pole+tag;c.chain_count=2;c.use_stretch=False
    for deform,goal in [('D_main.','CTRL_main.'),('D_pied.','CTRL_pied.')]:
        c=rig.pose.bones[deform+tag].constraints.new('COPY_ROTATION');c.target=rig;c.subtarget=goal+tag;c.target_space='WORLD';c.owner_space='WORLD'
# Weights are assigned over the continuous mesh, with smooth joint transitions.
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
body=bpy.data.objects['Renard · corps continu et mains'];bpy.context.view_layer.objects.active=body;bpy.ops.object.select_all(action='DESELECT');body.select_set(True)
dec=body.modifiers.new('Allègement pour articulation','DECIMATE');dec.ratio=.30
while body.modifiers.find(dec.name)>0:bpy.ops.object.modifier_move_up(modifier=dec.name)
bpy.ops.object.modifier_apply(modifier=dec.name);skin(body,bodyweights)
head=bpy.data.objects['Renard · tête et museau sculptés'];skin(head,lambda p:blend('CTRL_cou','CTRL_tete',(p.z-5.02)/.20))
for side in [-1,1]:
    tag='G' if side<0 else 'D';ear=bpy.data.objects['V4 · Oreille '+tag]
    skin(ear,lambda p,t=tag:mixweights({'CTRL_tete':1},blend('CTRL_oreille.'+t,'D_oreille_pointe.'+t,(p.z-5.9)/.15),smooth((p.z-5.65)/.16)))
tail=bpy.data.objects['Queue · longue silhouette']
def tailweights(p):
    ds=sorted((segdist(p,Vector(tailpoints[j]),Vector(tailpoints[j+1])),j) for j in range(6))[:2];ww={('CTRL_queue_%d'%j):1/max(.12,d)**4 for d,j in ds};tot=sum(ww.values());return {k:v/tot for k,v in ww.items()}
skin(tail,tailweights)
# Tail colour follows its mesh rather than world coordinates while moving.
nt=tail.data.materials[0].node_tree;att=nt.nodes.new('ShaderNodeAttribute');att.attribute_name='tail_tip'
for n in nt.nodes:
    if n.type=='MATH' and n.operation=='GREATER_THAN':nt.links.new(att.outputs['Fac'],n.inputs[0]);break
faceobjects=list(bpy.data.collections['02 — Visage · regard et expression'].objects)
clothobjects=list(bpy.data.collections['03 — Foulard'].objects)
for o in faceobjects+clothobjects:
    if o.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object
    if o in faceobjects or o.name.startswith(('V4','V5')):skin(o,lambda p:{'CTRL_tete':1})
    elif 'col' in o.name:skin(o,lambda p:{'CTRL_cou':1})
    else:skin(o,lambda p:blend('CTRL_foulard_pointe','CTRL_foulard',(p.z-3.8)/.35))
# Facial controls drive real shape keys and gaze shader coordinates.
for name,value in [('clignement',0.0),('sourire',.35),('curieux',0.0),('regard_horizontal',.024),('regard_vertical',.008),('doigts_G',0.0),('doigts_D',0.0)]:
    rig[name]=value;rig.id_properties_ui(name).update(min=-.05 if 'regard' in name else 0,max=.05 if 'regard' in name else 1)
def propdriver(target,path,prop,expression='v'):
    f=target.driver_add(path);d=f.driver;d.expression=expression;v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["'+prop+'"]'
for side in [-1,1]:
    eye=bpy.data.objects['V5 · Œil '+str(side)];eye.shape_key_add(name='Base');k=eye.shape_key_add(name='Clignement');normal=Vector((side*.26,-.966,.025)).normalized();right=Vector((.966,side*.26,0)).normalized();up=normal.cross(right).normalized();origin=eye.data.vertices[0].co-normal*.006
    for a,b in zip(eye.data.vertices,k.data):
        q=a.co-origin;b.co=origin+right*q.dot(right)+up*(q.dot(up)*.02)+normal*(-.012)
    propdriver(k,'value','clignement')
    for name,prop in [('Regard horizontal','regard_horizontal'),('Regard vertical','regard_vertical')]:propdriver(eye.data.materials[0].node_tree.nodes[name].outputs[0],'default_value',prop)
    lash=bpy.data.objects['V5 · Paupière supérieure '+str(side)];lash.shape_key_add(name='Base');k=lash.shape_key_add(name='Fermée')
    for a,b in zip(lash.data.vertices,k.data):q=a.co-origin;b.co=origin+right*q.dot(right)+up*.002+normal*.004
    propdriver(k,'value','clignement')
    mouth=bpy.data.objects['V5 · Sourire chaleureux '+str(side)];mouth.shape_key_add(name='Base');k=mouth.shape_key_add(name='Sourire')
    for a,b in zip(mouth.data.vertices,k.data):b.co.z+=.028*smooth((a.co.y+.65)/.40)
    propdriver(k,'value','sourire')
    brow=bpy.data.objects['V4 · Sourcil doux '+str(side)];brow.shape_key_add(name='Base');k=brow.shape_key_add(name='Curieux')
    for a,b in zip(brow.data.vertices,k.data):b.co.z+=.035
    propdriver(k,'value','curieux')
for pb in rig.pose.bones:
    if pb.name.startswith(('D_doigt','D_pouce')):
        tag=pb.name[-1];pb.rotation_mode='XYZ';fc=pb.driver_add('rotation_euler',0);d=fc.driver;d.expression='v*.7';v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["doigts_'+tag+'"]'
# Simple reusable widgets, hidden as scene objects.
widgets=bpy.data.collections.new('08 — Formes des contrôles');s.collection.children.link(widgets);widgets.hide_render=True
for kind in ['cercle','cube']:
    if kind=='cercle':v=[(math.cos(a*math.tau/32),math.sin(a*math.tau/32),0) for a in range(32)];edges=[(a,(a+1)%32) for a in range(32)]
    else:v=[(x,y,z) for x in [-1,1] for y in [-1,1] for z in [-1,1]];edges=[(i,j) for i in range(8) for j in range(i+1,8) if sum(v[i][k]!=v[j][k] for k in range(3))==1]
    me=bpy.data.meshes.new('Forme '+kind);me.from_pydata(v,edges,[]);ob=bpy.data.objects.new('Forme '+kind,me);widgets.objects.link(ob);ob.hide_render=True;ob.hide_set(True)
for pb in rig.pose.bones:
    if pb.name.startswith('CTRL_'):
        pb.custom_shape=bpy.data.objects['Forme '+('cube' if any(x in pb.name for x in ['main.','pied.','coude.','genou.']) else 'cercle')];pb.use_custom_shape_bone_size=False;pb.custom_shape_scale_xyz=(.16,.16,.16) if '.' in pb.name else (.35,.35,.35)
        try:pb.color.palette='THEME03' if pb.name.endswith('.G') else 'THEME04'
        except:pass
# Pose helpers are reused by the animation script.
def place(name,pos,angleX=0):
    pb=rig.pose.bones[name];rest=ad.bones[name].matrix_local.to_3x3().to_4x4();pb.matrix=Matrix.Translation(Vector(pos))@Matrix.Rotation(math.radians(angleX),4,'X')@rest
    bpy.context.view_layer.update()
def quadruped():
    for pb in rig.pose.bones:
        if not pb.name.startswith(('D_doigt','D_pouce')):pb.matrix_basis.identity()
    place('CTRL_corps',(0,.8,1.86),100);rig.pose.bones['CTRL_cou'].rotation_quaternion=Quaternion((1,0,0),math.radians(-85));rig.pose.bones['CTRL_tete'].rotation_quaternion=Quaternion((1,0,0),math.radians(-8));bpy.context.view_layer.update()
    for side in [-1,1]:
        tag='G' if side<0 else 'D';place('CTRL_main.'+tag,(side*.59,-1,.15),-65);place('CTRL_pied.'+tag,(side*.42,.9,.24));place('CTRL_coude.'+tag,(side*.7,.8,1.1));place('CTRL_genou.'+tag,(side*.42,-1.4,1.1))
    pb=rig.pose.bones['CTRL_foulard'];pos=pb.matrix.translation.copy();place('CTRL_foulard',pos,0)
quadruped()
# Calibrate each pole against the intended elbow/knee plane.
mods=[m for o in bpy.data.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
for tag in ['G','D']:
    for upper,lower,goal,pole in [('D_bras.','D_avant_bras.','CTRL_main.','CTRL_coude.'),('D_cuisse.','D_jambe.','CTRL_pied.','CTRL_genou.')]:
        c=rig.pose.bones[lower+tag].constraints[0];best=(-2,0)
        for i in range(32):
            angle=i*math.tau/32;c.pole_angle=angle;bpy.context.view_layer.update();r=rig.evaluated_get(bpy.context.evaluated_depsgraph_get());h=r.pose.bones[upper+tag].head;t=r.pose.bones[goal+tag].head;k=r.pose.bones[lower+tag].head;p=r.pose.bones[pole+tag].head;axis=(t-h).normalized();a=k-h-axis*(k-h).dot(axis);b=p-h-axis*(p-h).dot(axis);score=a.normalized().dot(b.normalized())
            if score>best[0]:best=(score,angle)
        c.pole_angle=best[1]
for m in mods:m.show_viewport=True
quadruped();bpy.context.view_layer.update()
# Stable diagnostic cameras.
studio=bpy.data.collections['04 — Studio · cameras et lumières']
def camera(name,loc,target,scale):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=scale;return o
cam=camera('RIG · contrôle trois quarts',(-12,-8,6),(0,-.4,1.4),5.2);profile=camera('RIG · contrôle profil',(-15,-.2,3.3),(0,-.2,1.3),5.2)
s.camera=cam;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=960;s.render.resolution_y=540;s.render.fps=30;s.render.film_transparent=True
if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=24
s['rig']='Squelette déformant, IK membres, contrôles queue/oreilles/foulard et visage ; test de déformation en cours';s['statut']='EXPRESSION V5 + PREMIER RIG — non validé'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'))
# Diagnostic renders are produced separately after animation verification.
report={'bones':len(ad.bones),'body_vertices':len(body.data.vertices),'groups':len(body.vertex_groups),'objects_bound':[(o.name,len(o.data.vertices)) for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers)],'IK':{pb.name:float(pb.constraints[0].pole_angle) for pb in rig.pose.bones if pb.constraints and pb.constraints[0].type=='IK'},'weights_missing':sum(not v.groups for v in body.data.vertices),'engine':s.render.engine,'pose':{name:list(pb.head) for name,pb in rig.pose.bones.items() if name.startswith(('CTRL_main.','CTRL_pied.','D_jambe.','D_avant_bras.'))}}
(OUT/'rig-inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('RIG_READY',json.dumps(report,ensure_ascii=False))
