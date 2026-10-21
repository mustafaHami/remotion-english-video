import bpy,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v5';scene=bpy.context.scene
head=bpy.data.objects['Renard · tête et museau sculptés'];face=bpy.data.collections['02 — Visage · regard et expression'];base=bpy.data.collections['01 — Renard · volumes']
black=bpy.data.objects['V4 · Sourire retenu -1'].data.materials[0]
for o in list(face.objects):
    if 'Sourire' in o.name or 'Ligne fine paupière' in o.name:bpy.data.objects.remove(o,do_unlink=True)
def curve(name,pts,r,mat):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=24;cu.bevel_depth=r;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
    for b,p in zip(sp.bezier_points,pts):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu);face.objects.link(o);cu.materials.append(mat);return o
# Grow the aperture while keeping the eye seated in the face.
for side in [-1,1]:
    o=bpy.data.objects['V4 · Œil continu '+str(side)];normal=Vector((side*.26,-.966,.025)).normalized();right=Vector((.966,side*.26,0)).normalized();up=normal.cross(right).normalized();origin=o.data.vertices[0].co-normal*.006
    N=80;R=10;verts=[origin+normal*.006];uvs=[(0,0)];faces=[]
    def boundary(a):
        u=.108*math.cos(a);si=math.sin(a);v=(.066 if si>=0 else .054)*(1 if si>=0 else -1)*abs(si)**.9+.018*u;return u,v
    for j in range(1,R+1):
        t=j/R
        for k in range(N):
            u,v=boundary(2*math.pi*k/N);u*=t;v*=t;verts.append(origin+right*u+up*v+normal*(.002+.004*(1-t*t)));uvs.append((u,v))
    for k in range(N):faces.append((0,k+1,(k+1)%N+1))
    for j in range(R-1):
        for k in range(N):a=1+j*N+k;b=1+j*N+(k+1)%N;faces.append((a,a+N,b+N,b))
    mat=o.data.materials[0];me=bpy.data.meshes.new('V5 · regard ambré '+str(side));me.from_pydata(verts,[],faces);me.update();me.materials.append(mat);o.data=me;o.name='V5 · Œil '+str(side)
    for p in me.polygons:p.use_smooth=True
    uv=me.uv_layers.new(name='Regard')
    for p in me.polygons:
        for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
    for n in mat.node_tree.nodes:
        if n.type=='MATH' and n.operation=='DIVIDE' and abs(n.inputs[1].default_value-.052)<.00001:n.inputs[1].default_value=.064
    mat.node_tree.nodes['Regard horizontal'].outputs[0].default_value=.024;mat.node_tree.nodes['Regard vertical'].outputs[0].default_value=.008
    for vert in head.data.vertices:
        q=vert.co-origin;u=q.dot(right);v=q.dot(up);d=q.dot(normal);r2=(u/.115)**2+(v/.071)**2
        if r2<1.6 and -.12<d<.12:
            t=max(0,min(1,(1.6-r2)/.55));w=t*t*(3-2*t);vert.co+=normal*((-.002-d)*w)
    pts=[]
    for k in range(21):
        u,v=boundary(math.pi*k/20);pts.append(origin+right*u+up*v+normal*.004)
    q=curve('V5 · Paupière supérieure '+str(side),pts,.006,black)
    for k,b in enumerate(q.data.splines[0].bezier_points):b.radius=.2+.8*math.sin(math.pi*k/20)
# Cream reaches beneath the mouth toward the nose, like the approved drawing.
a=head.data.attributes['jaw']
for i,vert in enumerate(head.data.vertices):
    x,y,z=vert.co;cheek=(1-((y+.20)/.32)**2-((z-5.32)/.18)**2)*.12;muzzle=min(-.24-y,5.44+.25*max(0,-y-.40)-z);neck=min(.23-abs(x),5.23-z,-.025-y);a.data[i].value=max(cheek,muzzle,neck)
bpy.context.view_layer.update();bvh=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
for side in [-1,1]:
    pts=[]
    for y,z in [(-.255,5.457),(-.34,5.420),(-.49,5.397),(-.70,5.432),(-.888,5.555)]:
        hit,nn,idx,d=bvh.ray_cast(Vector((side*2,y,z)),Vector((-side,0,0)),4)
        if hit is None:hit,nn,idx,d=bvh.find_nearest(Vector((side*.15,y,z)))
        pts.append(hit+nn*.004)
    q=curve('V5 · Sourire chaleureux '+str(side),pts,.0058,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.58,1,.95,.72,.12]):b.radius=r
# Symmetric small nose: the previous prism had uneven left/right heights.
nose=bpy.data.objects['V4 · Truffe triangulaire']
for v in nose.data.vertices:
    if v.co.x>0:v.co.z-=.01
    elif v.co.x<0:v.co.z+=.01
scene['statut']='EXPRESSION V5 — retouche finale avant articulation, non validée';scene['retouches']='Regard agrandi ; coin de bouche relevé ; sourire incurvé dans le masque crème'
scene.camera=bpy.data.objects['V4 · tête trois quarts'];scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.fps=30;scene.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-expression-v5.blend'))
scene.render.filepath=str(OUT/'renard-v5-expression.png');bpy.ops.render.render(write_still=True)
report={'objects':[],'engines':[(x.identifier,x.name) for x in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]}
for col in [base,face,bpy.data.collections['03 — Foulard']]:
    for o in col.objects:report['objects'].append({'name':o.name,'type':o.type,'verts':len(o.data.vertices) if o.type=='MESH' else 0,'modifiers':[(m.name,m.type) for m in o.modifiers],'bbox':[list(o.matrix_world@Vector(x)) for x in o.bound_box]})
(OUT/'inspection.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('WARM_EXPRESSION_READY')
