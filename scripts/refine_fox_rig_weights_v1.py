import bpy,math,json,time
from mathutils import Vector,Matrix,Quaternion
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];ad=rig.data
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def blend(a,b,t):t=smooth(t);return {a:1-t,b:t}
def mixweights(a,b,t):
    out={k:v*(1-t) for k,v in a.items()}
    for k,v in b.items():out[k]=out.get(k,0)+v*t
    return out
def skin(o,fn):
    o.vertex_groups.clear();buckets={}
    for v in o.data.vertices:
        weights={k:round(max(0,w)*64) for k,w in fn(v.co).items() if w>.001};total=sum(weights.values())
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
# Reorient the tail toward the rear, with a slight downward arc.
pb=rig.pose.bones['CTRL_queue_0'];pos=pb.matrix.translation.copy();q=Vector((-2.53,.60,-2.09)).rotation_difference(Vector((-.55,3.1,-.65)));pb.matrix=Matrix.Translation(pos)@q.to_matrix().to_4x4()@ad.bones[pb.name].matrix_local.to_3x3().to_4x4();bpy.context.view_layer.update()
for name,target in [('RIG · contrôle trois quarts',(0,.65,1.45)),('RIG · contrôle profil',(0,.7,1.45))]:
    cam=bpy.data.objects[name];cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=5.5
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='OFF';sh=s.display.shading;sh.light='STUDIO';sh.color_type='VERTEX';sh.show_shadows=False;sh.show_cavity=False;sh.show_specular_highlight=False
try:sh.studio_light='paint.sl'
except:pass
s.render.resolution_x=640;s.render.resolution_y=360;s.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'));print('REBIND_SAVED',flush=True)
for label,cam in [('trois-quarts','RIG · contrôle trois quarts'),('profil','RIG · contrôle profil')]:
    s.camera=bpy.data.objects[cam];s.render.filepath=str(OUT/('raccord-'+label+'.png'));tm=time.monotonic();bpy.ops.render.render(write_still=True);print('FAST_RENDER_SECONDS',time.monotonic()-tm,flush=True)
