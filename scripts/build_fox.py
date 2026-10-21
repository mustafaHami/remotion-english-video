import bpy, math, json
from mathutils import Vector
from pathlib import Path
BASE=Path('D:/ai-generation-video')
OUT=BASE/'output'/'blender'
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection' and c.users==0: bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=32
scene.cycles.use_denoising=True
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.render.fps=30
scene.frame_end=150
scene.world.color=(.3,.3,.3)
scene.view_settings.view_transform='AgX'
# Linear colors keep the terracotta calm under large studio lights.
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.new(name); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
 return m
orange=mat('Terracotta | pelage',(0.52,.105,.033),.72)
cream=mat('Crème | museau poitrine queue',(.91,.75,.54),.67)
coal=mat('Anthracite | membres nez',(.033,.044,.053),.48)
sage=mat('Sauge | foulard',(.22,.31,.24),.76)
sage_dark=mat('Sauge | plis',(.15,.22,.17),.8)
ear_inner=mat('Intérieur des oreilles',(.72,.35,.20),.68)
white=mat('Ivoire | yeux',(.94,.91,.82),.24)
amber=mat('Ambre | iris',(.57,.255,.035),.23)
black=mat('Brun profond | pupilles',(.018,.012,.009),.19)
highlight=mat('Reflets des yeux',(1,1,1),.12)
background=mat('Fond ivoire',(.84,.79,.70),.9)
textmat=mat('Texte anthracite',(.048,.06,.067),.8)
root=bpy.data.objects.new('RENARD | racine',None); scene.collection.objects.link(root)
parts=[]
def finish(ob,name,material=None,parent=True,smooth=True):
 ob.name=name
 if material: ob.data.materials.append(material)
 if ob.type=='MESH' and smooth:
  for p in ob.data.polygons: p.use_smooth=True
 if parent: ob.parent=root; parts.append(ob)
 return ob

def ell(name,loc,scale,material,segments=48,rings=24):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
 ob=finish(bpy.context.object,name,material); ob.scale=scale
 return ob

def mesh(name,verts,faces,materials,sub=1):
 me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
 ob=bpy.data.objects.new(name,me); scene.collection.objects.link(ob)
 finish(ob,name)
 for material in materials: me.materials.append(material)
 if sub:
  mod=ob.modifiers.new('Surface continue','SUBSURF'); mod.levels=sub; mod.render_levels=sub
 return ob

def rings_z(name,rows,material,sub=2,n=32):
 verts=[]
 for z,x,y,rx,ry in rows:
  for i in range(n):
   a=2*math.pi*i/n; verts.append((x+rx*math.cos(a),y+ry*math.sin(a),z))
 faces=[tuple(reversed(range(n)))]
 for j in range(len(rows)-1):
  for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.append(tuple((len(rows)-1)*n+i for i in range(n)))
 return mesh(name,verts,faces,[material],sub)

def tube(name,points,radii,material,n=20,sub=2,flat=1):
 # Closely spaced support rings prevent detached-looking rounded caps.
 if len(points)>1:
  a=Vector(points[0]); b=Vector(points[1]); c=Vector(points[-1]); d=Vector(points[-2])
  points=[points[0],tuple(a+(b-a).normalized()*.008)]+list(points[1:-1])+[tuple(c+(d-c).normalized()*.008),points[-1]]
  radii=[radii[0],radii[0]]+list(radii[1:-1])+[radii[-1],radii[-1]]
 verts=[]
 for j,p in enumerate(points):
  p=Vector(p)
  tangent=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
  tangent.normalize(); axis=tangent.cross(Vector((0,1,0)))
  if axis.length<.1: axis=tangent.cross(Vector((1,0,0)))
  axis.normalize(); other=tangent.cross(axis).normalized()
  for i in range(n):
   a=2*math.pi*i/n
   v=p+axis*math.cos(a)*radii[j]+other*math.sin(a)*radii[j]*flat
   verts.append(tuple(v))
 faces=[tuple(reversed(range(n)))]
 for j in range(len(points)-1):
  for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 faces.append(tuple((len(points)-1)*n+i for i in range(n)))
 return mesh(name,verts,faces,[material],sub)

def curve(name,coords,radius,material):
 cu=bpy.data.curves.new(name,'CURVE'); cu.dimensions='3D'; cu.resolution_u=20
 sp=cu.splines.new('BEZIER'); sp.bezier_points.add(len(coords)-1)
 for p,co in zip(sp.bezier_points,coords): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
 cu.bevel_depth=radius; cu.bevel_resolution=4
 ob=bpy.data.objects.new(name,cu); scene.collection.objects.link(ob); finish(ob,name,material)
 return ob
# A tapering torso instead of stacked spherical volumes.
body=rings_z('Corps | silhouette élancée',[(1.32,0,.04,.12,.12),(1.48,0,.03,.26,.23),(1.72,0,.02,.33,.29),(2.05,0,0,.30,.25),(2.40,0,0,.31,.25),(2.65,0,.015,.36,.25),(2.83,0,.02,.32,.22),(3.0,0,0,.15,.15),(3.08,0,0,.10,.10)],orange)
# Cream breast uses a continuous fitted parametric surface with dense control rings.
profile=[(1.32,.12,.12,.04),(1.48,.26,.23,.03),(1.72,.33,.29,.02),(2.05,.30,.25,0),(2.40,.31,.25,0),(2.65,.36,.25,.015),(2.83,.32,.22,.02),(3.0,.15,.15,0)]
def body_profile(z):
 for i in range(len(profile)-1):
  lo,hi=profile[i],profile[i+1]
  if lo[0]<=z<=hi[0]:
   t=(z-lo[0])/(hi[0]-lo[0]); return tuple(lo[k]+t*(hi[k]-lo[k]) for k in (1,2,3))
 return (.2,.2,0)
bpy.context.view_layer.update()
body_eval=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
verts=[]; nz=40; nx=24
for j in range(nz):
 z=1.49+(2.88-1.49)*j/(nz-1)
 rx,ry,cy=body_profile(z)
 taper=math.sin(math.pi*j/(nz-1))**.38
 w=.21*taper+.003
 for i in range(nx):
  x=w*(i/(nx-1)*2-1)
  y=cy-ry*math.sqrt(max(.02,1-(x/rx)**2))
  hit,location,normal,face_index=body_eval.ray_cast(Vector((x,-3,z)),Vector((0,1,0)))
  if hit: y=location.y-.012
  verts.append((x,y,z))
faces=[]
for j in range(nz-1):
 for i in range(nx-1): faces.append((j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i))
chest=mesh('Poitrine | panneau crème',verts,faces,[cream],2)
# Long legs with dark stockings, a slight natural bend, and flat contact soles.
for side in (-1,1):
 s='G' if side<0 else 'D'
 tube('Cuisse '+s,[(side*.20,.02,1.72),(side*.23,.02,1.54),(side*.25,.02,1.22),(side*.24,-.025,.91),(side*.24,-.025,.69)],[.12,.145,.125,.085,.077],orange)
 tube('Jambe anthracite '+s,[(side*.24,-.025,.80),(side*.24,-.025,.68),(side*.235,.00,.41),(side*.24,-.015,.135)],[.084,.080,.065,.055],coal)
 ell('Pied '+s,(side*.24,-.09,.10),(.105,.21,.075),coal)
# Arms / paws relaxed, one open gesture. Separated at joints for future rigging.
for side in (-1,1):
 s='G' if side<0 else 'D'
 shoulder=(side*.32,.01,2.72)
 if side<0:
  elbow=(side*.49,-.015,2.14); wrist=(side*.52,-.14,1.66); palm=(side*.53,-.15,1.60)
 else:
  elbow=(side*.58,-.06,2.22); wrist=(side*.84,-.25,2.52); palm=(side*.93,-.29,2.57)
 mid=tuple((a+b)/2 for a,b in zip(shoulder,elbow))
 tube('Bras '+s,[shoulder,mid,elbow],[.11,.105,.085],orange)
 fore=tuple(elbow[i]+(wrist[i]-elbow[i])*.5 for i in range(3))
 tube('Avant-bras '+s,[elbow,fore,wrist],[.087,.077,.051],coal)
 hand=ell('Paume '+s,palm,(.09,.058,.12) if side<0 else (.13,.065,.068),coal)
 if side<0:
  for i in range(3):
   x=palm[0]+(i-1)*.038
   tube('Doigt '+s+str(i),[(x,-.15,1.57),(x,-.16,1.48),(x+.007,-.17,1.44)],[.023,.019,.008],coal,12,1)
  tube('Pouce '+s,[(palm[0]+.06,-.16,1.63),(palm[0]+.105,-.19,1.57),(palm[0]+.09,-.20,1.54)],[.027,.023,.008],coal,12,1)
 else:
  for i in range(3):
   y=palm[1]+(i-1)*.045
   tube('Doigt '+s+str(i),[(.97,y,2.58),(1.055,y-.015,2.62),(1.09,y-.02,2.66)],[.025,.021,.008],coal,12,1)
  tube('Pouce '+s,[(.88,-.345,2.58),(.89,-.38,2.68),(.93,-.37,2.71)],[.032,.026,.01],coal,12,1)
# Curved fox tail; alternating angular cream border, not a spherical pompom.
tailpoints=[(0,.19,1.57),(-.12,.42,1.47),(-.43,.55,1.38),(-.79,.57,1.47),(-1.11,.52,1.68),(-1.31,.45,1.93),(-1.38,.38,2.16),(-1.37,.35,2.34)]
tailr=[.105,.17,.28,.34,.29,.21,.12,.012]
tail=tube('Queue | courbe volumique',tailpoints,tailr,orange,n=32,sub=2,flat=.73)
tail.data.materials.append(cream)
for face in tail.data.polygons:
 c=face.center
 # assign by ring index; boundary alternates to recall graphic points
 if len(face.vertices)==4:
  ring=min(face.vertices)//32; angle=min(face.vertices)%32
  if ring>=6: face.material_index=1
 elif len(face.vertices)>4 and max(face.vertices)>64: face.material_index=1
# Head built around a narrower adult muzzle.
head=ell('Tête | crâne',(0,-.035,3.36),(.405,.345,.395),orange)
# Side cheeks retain pointed fox outline.
for side in (-1,1):
 tube('Joue effilée '+str(side),[(side*.26,-.01,3.34),(side*.38,.005,3.21),(side*.46,.04,3.10)],[.14,.11,.008],orange,n=20,sub=1,flat=.7)
# Tapered snout with orange upper bridge and cream underneath.
n=40; rows=[(-.23,3.31,.30,.20),(-.37,3.29,.31,.18),(-.58,3.29,.245,.13),(-.81,3.31,.13,.083),(-.94,3.33,.075,.048)]
verts=[]
for y,z,rx,rz in rows:
 for i in range(n):
  a=2*math.pi*i/n; verts.append((rx*math.cos(a),y,z+rz*math.sin(a)))
faces=[tuple(reversed(range(n)))]
for j in range(len(rows)-1):
 for i in range(n): faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
faces.append(tuple((len(rows)-1)*n+i for i in range(n)))
muzzle=mesh('Museau | pont terracotta dessous crème',verts,faces,[orange,cream],2)
for poly in muzzle.data.polygons:
 if sum(muzzle.data.vertices[i].co.z for i in poly.vertices)/len(poly.vertices)<3.345: poly.material_index=1
ell('Menton crème',(0,-.39,3.135),(.23,.235,.11),cream)
nose=ell('Nez',(0,-.965,3.345),(.092,.07,.057),coal)
# Eyes with almond upper rims and restrained amber irises.
for side in (-1,1):
 x=side*.235
 eye=ell('Œil blanc '+str(side),(x,-.276,3.51),(.102,.041,.086),white)
 iris=ell('Iris ambré '+str(side),(x+.009,-.310,3.507),(.045,.014,.051),amber)
 pupil=ell('Pupille '+str(side),(x+.012,-.323,3.508),(.020,.009,.034),black)
 ell('Reflet principal '+str(side),(x-.001,-.334,3.530),(.011,.005,.013),highlight,24,12)
 ell('Reflet secondaire '+str(side),(x+.025,-.333,3.490),(.004,.003,.005),highlight,16,8)
 curve('Paupière supérieure '+str(side),[(x-.095,-.282,3.53),(x-.055,-.297,3.58),(x+.02,-.299,3.59),(x+.091,-.278,3.55)],.009,coal)
 bpy.context.view_layer.update()
 head_eval=head.evaluated_get(bpy.context.evaluated_depsgraph_get())
 brow=[]
 for bx,bz in [(side*.145,3.635),(side*.235,3.645),(side*.315,3.605)]:
  inv=head.matrix_world.inverted()
  hit,local,normal,index=head_eval.ray_cast(inv @ Vector((bx,-3,bz)),Vector((0,1,0)))
  by=(head.matrix_world @ local).y-.011 if hit else -.10
  brow.append((bx,by,bz))
 curve('Sourcil '+str(side),brow,.014,coal)
# Gentle mouth line on both sides of the snout.
for side in (-1,1):
 curve('Sourire '+str(side),[(side*.075,-.882,3.281),(side*.155,-.723,3.24),(side*.245,-.507,3.205),(side*.265,-.358,3.23)],.009,coal)
# Continuous broad ears with integrated charcoal tips.
for side in (-1,1):
 outline=[(.10,3.61),(.39,3.61),(.354,3.97),(.322,4.09),(.271,3.97)]
 verts=[]
 for y in (-.05,.075):
  for x,z in outline: verts.append((side*x,y+(z-3.61)*.10,z))
 faces=[(0,1,2,4),(4,2,3),(9,7,6,5),(8,7,9)]
 for i in range(5): faces.append((i,(i+1)%5,(i+1)%5+5,i+5))
 ear=mesh('Oreille '+str(side),verts,faces,[orange,coal],0)
 ear.data.polygons[1].material_index=1; ear.data.polygons[3].material_index=1
 for i in (6,7): ear.data.polygons[i].material_index=1
 bevel=ear.modifiers.new('Bords souples','BEVEL'); bevel.width=.006; bevel.segments=2
 ear.modifiers.new('Normales','WEIGHTED_NORMAL')
 inner=mesh('Oreille intérieure '+str(side),[(side*.157,-.074,3.68),(side*.335,-.074,3.68),(side*.309,-.044,3.972)],[(0,1,2)],[ear_inner],0)
 sol=inner.modifiers.new('Épaisseur','SOLIDIFY'); sol.thickness=.01
 bev=inner.modifiers.new('Bord intérieur','BEVEL'); bev.width=.013; bev.segments=3
# Cloth scarf rings, softly asymmetrical instead of a shiny rubber torus.
scarf=rings_z('Foulard | col souple',[(2.85,0,-.01,.26,.22),(2.87,0,-.01,.30,.27),(2.98,0,-.01,.32,.28),(3.09,0,.00,.27,.245),(3.12,0,.00,.23,.20)],sage,2)
curve('Foulard | pli du col',[(-.25,-.19,2.94),(-.10,-.28,2.91),(.10,-.29,2.94),(.26,-.17,2.98)],.012,sage_dark)
verts=[(-.14,-.30,2.91),(.01,-.31,2.91),(-.035,-.295,2.58),(.035,-.282,2.23),(-.08,-.29,2.07),(-.20,-.28,2.15),(-.18,-.30,2.47)]
flap=mesh('Foulard | pan',verts,[(0,1,2,6),(6,2,3,4,5)],[sage],2)
sol=flap.modifiers.new('Tissu','SOLIDIFY'); sol.thickness=.025
curve('Foulard | couture',[(-.11,-.324,2.81),(-.115,-.322,2.52),(-.105,-.31,2.20)],.005,sage_dark)
for i in range(5):
 x=-.175+i*.027
 curve('Frange '+str(i),[(x,-.29,2.16),(x+.01,-.30,2.06),(x+.005,-.305,2.015)],.007,sage)
# Ground, camera and large area lights.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015)); finish(bpy.context.object,'Studio | sol',background,False)
world=scene.world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.77,.83,1); world.node_tree.nodes['Background'].inputs[1].default_value=.45

def area(name,loc,power,size,color):
 data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size; data.color=color
 ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector((0,0,2))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Lumière | grande fenêtre',(-4,-6,7),650,5,(1,.91,.80))
area('Lumière | remplissage',(4,-3,5),450,4,(.81,.9,1))
area('Lumière | contour',(2,4,7),750,4,(1,.87,.70))
camera_data=bpy.data.cameras.new('Caméra'); camera=bpy.data.objects.new('Caméra',camera_data); scene.collection.objects.link(camera); scene.camera=camera
camera_data.type='ORTHO'; camera_data.lens=55

def camera_at(loc,target,scale):
 camera.location=loc; camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler(); camera_data.ortho_scale=scale
camera_at((5,-10,5.3),(0,-.05,2.1),5.35)
scene.render.resolution_x=1100; scene.render.resolution_y=1400
scene.render.filepath=str(OUT/'renard-3d-v1-trois-quarts.png')
# Source contains one character, editable named pieces, no claimed working rig yet.
scene['statut']='Première proposition 3D non validée, sans squelette ni animation.'
scene['reference']='assets/branding/renard-reference-validee.png'
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'blender'/'renard-v1.blend'))
exec((BASE/'scripts'/'prepare_fox_viewport.py').read_text(encoding='utf-8'))
bpy.ops.render.render(write_still=True)
# Three views generated from the same geometry.
root.rotation_euler[2]=0
camera_at((0,-11,4.8),(0,-.05,2.1),5.35)
scene.render.filepath=str(OUT/'renard-3d-v1-face.png'); bpy.ops.render.render(write_still=True)
root.rotation_euler[2]=-math.pi/2
scene.render.filepath=str(OUT/'renard-3d-v1-profil.png'); bpy.ops.render.render(write_still=True)
exec((BASE/'scripts'/'render_fox_board.py').read_text(encoding='utf-8'))
print('FOX_V1_COMPLETE')
