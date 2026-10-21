import bpy,json,math
from mathutils import Vector
from pathlib import Path
s=bpy.context.scene;ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1'
body=bpy.data.objects['Renard · corps continu et mains']
for m in list(body.modifiers):
    if m.type=='CORRECTIVE_SMOOTH':body.modifiers.remove(m)
def rgb(h):return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def srgb(c):return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)
orange=srgb(rgb('CC5B38'));cream=srgb(rgb('FAE6CC'));black=srgb(rgb('30363C'));sage=srgb(rgb('7B8E7E'));inner=srgb(rgb('E9AB85'))
for o in bpy.data.objects:
    if o.type!='MESH' or not any(m.type=='ARMATURE' for m in o.modifiers):continue
    mesh=o.data;attr=mesh.color_attributes.get('Aperçu articulation') or mesh.color_attributes.new(name='Aperçu articulation',type='FLOAT_COLOR',domain='POINT');mesh.color_attributes.active_color=attr
    at=mesh.attributes
    uv=mesh.uv_layers.get('Regard');uvv={}
    if uv:
        for l in mesh.loops:uvv[l.vertex_index]=uv.data[l.index].uv.copy()
    for v in mesh.vertices:
        col=orange;n=o.name
        if 'corps continu' in n:
            if at['bib'].data[v.index].value>0:col=cream
            if at['gloves_boots'].data[v.index].value>0:col=black
        elif 'tête et museau' in n:col=cream if at['jaw'].data[v.index].value>0 else orange
        elif 'Queue' in n:col=cream if at['tail_tip'].data[v.index].value>0 else orange
        elif 'Oreille' in n:
            col=inner if at['inner'].data[v.index].value>0 else orange
            if at['rim'].data[v.index].value>0:col=black
        elif 'Œil' in n:
            u,w=uvv[v.index];du=u-.024;dv=w-.008;r=math.hypot(du,dv)/.064;col=srgb(rgb('FFF7E8')) if r>1 else srgb(rgb('DEA047')) if r>.66 else srgb(rgb('1D2427'))
            if ((du+.018)/.0065)**2+((dv-.025)/.008)**2<1:col=srgb(rgb('FFFDF3'))
        elif 'Foulard' in n:col=sage
        else:col=black
        attr.data[v.index].color=(*col,1)
s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.5;sh.color_type='VERTEX';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='WORLD';sh.curvature_ridge_factor=.9;sh.curvature_valley_factor=.5;sh.show_specular_highlight=False;sh.background_type='WORLD';s.world.color=(.92,.91,.88)
s.render.film_transparent=True;s.render.resolution_x=960;s.render.resolution_y=540;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'));print('SAVED_RIG_PREVIEW',flush=True)
for label,cam in [('quadrupede','RIG · contrôle trois quarts'),('profil','RIG · contrôle profil')]:
    s.camera=bpy.data.objects[cam];s.render.filepath=str(OUT/('controle-'+label+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',label,flush=True)
rig=bpy.data.objects['RIG · Renard'];report={'bones':len(rig.data.bones),'body_vertices':len(body.data.vertices),'weights_missing':sum(not v.groups for v in body.data.vertices),'engine':s.render.engine,'pose':{pb.name:list(pb.head) for pb in rig.pose.bones if pb.name.startswith(('CTRL_main.','CTRL_pied.','D_jambe.','D_avant_bras.'))}}
(OUT/'rig-inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('CHECK_COMPLETE',flush=True)
