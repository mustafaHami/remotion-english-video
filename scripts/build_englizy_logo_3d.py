import bpy, json, math, sys, time
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ai-generation-video/output/englizy/3d')
BLEND=Path('D:/ai-generation-video/blender/englizy-logo-relief-v1.blend')
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for mat in list(bpy.data.materials):bpy.data.materials.remove(mat)
s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
s.render.resolution_x=1080;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.fps=30;s.frame_start=1;s.frame_end=180
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.render.film_transparent=True
s.view_settings.view_transform='Standard'
s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
s.world.color=(.25,.25,.25)
# Physical rendering with soft lighting, matte sides and restrained sheen.
def linear(rgb):
    return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)
def material(name,h,rough=.48,emission=.12):
    m=bpy.data.materials.new(name);m.diffuse_color=(*linear(tuple(int(h[i:i+2],16)/255 for i in [0,2,4])),1)
    m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=m.diffuse_color
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=0
    p.inputs['Emission Color'].default_value=m.diffuse_color;p.inputs['Emission Strength'].default_value=emission
    return m
lav=material('Lavande · fond mat','A99BFF',.5,.18)
cream=material('Crème · support','FFFDF8',.55,.1)
ink=material('Encre · lettres','1E1B3A',.37,.04)
foxside=material('Tranche renard · terre cuite','B54A25',.55,.07)
bubbleside=material('Tranche dialogue · violet encre','454067',.5,.08)
texmat=bpy.data.materials.new('Illustration originale · projection fidèle');texmat.use_nodes=True
nt=texmat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.65
bs.inputs['Specular IOR Level'].default_value=.18
texture=nt.nodes.new('ShaderNodeTexImage');texture.image=bpy.data.images.load(str(ROOT/'logo-reference.png'));texture.interpolation='Linear';texture.extension='EXTEND'
nt.links.new(texture.outputs['Color'],bs.inputs['Base Color'])
nt.links.new(texture.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.08
rig=bpy.data.objects.new('LOGO · contrôle général',None);s.collection.objects.link(rig)
rig['description']='Logo de référence extrudé en bas-relief. Boucle de 6 secondes, lettres et illustration indépendantes.'
def parent(o):o.parent=rig
def cylinder(name,px,py,r,z,depth,mat,bevel=.04):
    bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=r,depth=depth,location=((px-627)/125.4,(627-py)/125.4,z))
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);parent(o)
    bevelmod=o.modifiers.new('Bord arrondi','BEVEL');bevelmod.width=bevel;bevelmod.segments=4
    o.modifiers.new('Normales pondérées','WEIGHTED_NORMAL')
    return o
base=cylinder('01 · Médaillon lavande',627,627,4.75,-.14,.30,lav,.065)
disc=cylinder('02 · Disque crème',610,534,2.85,.10,.14,cream,.035)
contours=json.loads((ROOT/'contours.json').read_text())
def relief(name,loops,z,depth,side,textured=True,bevel=.018):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='2D';c.resolution_u=5;c.fill_mode='BOTH';c.extrude=depth/2;c.bevel_depth=bevel;c.bevel_resolution=3
    for pts in loops:
        sp=c.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
        for p,(x,y) in zip(sp.bezier_points,pts):
            p.co=((x-627)/125.4,(627-y)/125.4,0);p.handle_left_type='AUTO';p.handle_right_type='AUTO'
        sp.use_cyclic_u=True
    o=bpy.data.objects.new(name,c);s.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    for other in bpy.context.selected_objects:
        if other!=o:other.select_set(False)
    bpy.ops.object.convert(target='MESH')
    o=bpy.context.object
    o.data.materials.append(texmat if textured else ink);o.data.materials.append(side)
    uv=o.data.uv_layers.new(name='Projection du logo original');uv.active_render=True;o.data.uv_layers.active=uv
    for poly in o.data.polygons:
        poly.material_index=0 if poly.normal.z>.85 else 1
        poly.use_smooth=abs(poly.normal.z)<.85
        for li in poly.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(v.x/10+.5,v.y/10+.5)
    o.location.z=z;parent(o);o.select_set(False)
    return o
fox=relief('03 · Renard fidèle en relief',contours['fox'],.36,.24,foxside,True,.012)
bubbles=relief('04 · Dialogue FR EN et drapeau',contours['languages'],.60,.22,bubbleside,True,.012)
letters=[]
for idx,char in enumerate('Englizy'):
    o=relief('05 · Lettre '+str(idx+1)+' · '+char,contours['letter_'+char],.29,.30,ink,False,.018)
    letters.append(o)
# A complete seamless forward/back motion. No scaling of shapes or text.
for frame in range(1,182):
    t=(frame-1)/180;theta=2*math.pi*t
    rig.rotation_euler=(math.radians(4)*math.sin(theta),math.radians(10)*math.sin(theta+.25),math.radians(1)*math.sin(theta))
    rig.keyframe_insert('rotation_euler',frame=frame)
    for obj,basez,amp,phase in [(fox,.36,.55,0),(bubbles,.60,.58,-.55)]+[(o,.29,.60,-.24*i) for i,o in enumerate(letters)]:
        obj.location.z=basez+amp*(.5-.5*math.cos(theta+phase))
        obj.keyframe_insert('location',frame=frame)
# Front camera sees the original logo; gentle rocking reveals real extrusions.
bpy.ops.object.camera_add(location=(0,0,17))
cam=bpy.context.object;cam.name='CAMERA · logo frontal';cam.rotation_euler=(0,0,0)
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='PERSP';cam.data.lens=55;s.camera=cam
def area(name,loc,energy,size):
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
area('Lumière douce · haut gauche',(-4,5,8),300,6)
area('Remplissage · droite',(5,1,6),160,5)
area('Liseré · haut',(1,6,3),130,4)
# Packed file is self-contained.
for img in bpy.data.images:
    if img.source=='FILE':img.pack()
s.frame_set(46)
s.render.filepath=str(ROOT/'englizy-logo-3d.png')
# Saved viewport in camera rendered/material mode.
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA'
            ar.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
print('BLEND_SAVED',str(BLEND),flush=True)
bpy.ops.render.render(write_still=True)
print('PREVIEW_DONE',flush=True)
