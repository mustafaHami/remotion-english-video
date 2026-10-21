import bpy,math,json,hashlib,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v4';OUT.mkdir(parents=True,exist_ok=True)
base=bpy.data.collections.get('01 — Renard · volumes');facecol=bpy.data.collections.get('02 — Visage · regard et expression');clothcol=bpy.data.collections.get('03 — Foulard');studio=bpy.data.collections.get('04 — Studio · cameras et lumières');construct=bpy.data.collections.get('90 — Construction · volumes sources');COL=base
for o in list(facecol.objects):bpy.data.objects.remove(o,do_unlink=True)
for o in list(base.objects):
    if o.name not in ['Renard · corps continu et mains','Queue · longue silhouette']:bpy.data.objects.remove(o,do_unlink=True)
def move(o,c=None):
    c=c or COL
    for a in list(o.users_collection):a.objects.unlink(o)
    c.objects.link(o); return o
def rgb(h):
    v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)
def mat(n,h,rough=.8):
    m=bpy.data.materials.new(n); m.diffuse_color=(*rgb(h),1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb(h),1);p.inputs['Roughness'].default_value=rough;p.inputs['Specular IOR Level'].default_value=.22;return m
orange=mat('Pelage · terracotta chaud','C94E29'); cream=mat('Pelage · crème','F7E5CD'); black=mat('Pelage · anthracite','30363C'); inner=mat('Oreilles · pêche','EFAE83'); sage=mat('Foulard · sauge','788C7D'); sageDark=mat('Foulard · creux','66796B'); white=mat('Yeux · ivoire','FFF4E5',.42); amber=mat('Iris · ambre','B7782C',.4); amberLight=mat('Iris · ambre doré','E2A94B',.4); pupil=mat('Pupilles','191F22',.3); glint=mat('Reflets mesurés','FFFFFF',.25)
def mesh(n,v,f,m,c=None):
    me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);(c or COL).objects.link(o);o.data.materials.append(m)
    for p in me.polygons:p.use_smooth=True
    return o
def sub(o,lev=2):
    mod=o.modifiers.new('Surface continue','SUBSURF');mod.levels=lev;mod.render_levels=lev;return o
def ell(n,loc,scale,m,c=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=loc);o=bpy.context.object;o.name=n;move(o,c);o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
# Catmull-Rom interpolation makes continuous anatomical sections.
def interpolate(secs,steps=4):
    out=[]
    for i in range(len(secs)-1):
        a=secs[max(0,i-1)];b=secs[i];c=secs[i+1];d=secs[min(len(secs)-1,i+2)]
        for k in range(steps):
            t=k/steps;out.append([.5*((2*b[j])+(-a[j]+c[j])*t+(2*a[j]-5*b[j]+4*c[j]-d[j])*t*t+(-a[j]+3*b[j]-3*c[j]+d[j])*t*t*t) for j in range(len(b))])
    return out+[secs[-1]]
def tube(n,secs,m,segments=32,steps=4,c=None):
    ss=interpolate(secs,steps);v=[];f=[]
    for i,s in enumerate(ss):
        pos=Vector(s[:3]);tangent=Vector(ss[min(i+1,len(ss)-1)][:3])-Vector(ss[max(0,i-1)][:3]);tangent.normalize()
        side=Vector((1,0,0))
        if abs(tangent.dot(side))>.95:side=Vector((0,1,0))
        a=(side-tangent*side.dot(tangent)).normalized();b=tangent.cross(a).normalized()
        for k in range(segments):
            t=2*math.pi*k/segments;v.append(pos+a*max(.003,s[3])*math.cos(t)+b*max(.003,s[4])*math.sin(t))
    for i in range(len(ss)-1):
        for k in range(segments):f.append((i*segments+k,i*segments+(k+1)%segments,(i+1)*segments+(k+1)%segments,(i+1)*segments+k))
    f.append(tuple(reversed(range(segments))));f.append(tuple((len(ss)-1)*segments+k for k in range(segments)));return mesh(n,v,f,m,c)
def curve(n,points,r,m,c=None):
    cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.resolution_u=24;cu.bevel_depth=r;cu.bevel_resolution=4;s=cu.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for b,p in zip(s.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(n,cu);(c or COL).objects.link(o);o.data.materials.append(m);return o
def weld(name,objects,voxel=.04):
    # Preserve editable source volumes outside the rendered collections.
    for o in objects:
        cp=o.copy();cp.data=o.data.copy();construct.objects.link(cp);cp.name='Source · '+o.name
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    r=o.modifiers.new('Fusion anatomique','REMESH');r.mode='VOXEL';r.voxel_size=voxel;r.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=r.name)
    sm=o.modifiers.new('Lissage des raccords','SMOOTH');sm.factor=.6;sm.iterations=10
    if name=='Renard · corps continu et mains':
        group=o.vertex_groups.new(name='Lissage · protéger les doigts')
        for vert in o.data.vertices:
            x,y,z=vert.co;weight=max(0,min(1,(z-2.96)/.25)) if abs(x)>.66 and z<3.25 else 1
            group.add([vert.index],weight,'REPLACE')
        sm.vertex_group=group.name
    bpy.ops.object.modifier_apply(modifier=sm.name);sub(o,1);return o

def masked_material(n, masks, colors):
    m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.82;p.inputs['Specular IOR Level'].default_value=.15
    current=None
    for index,(att,color) in enumerate(zip(masks,colors[1:])):
        a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name=att
        cmp=nt.nodes.new('ShaderNodeMath');cmp.operation='GREATER_THAN';cmp.inputs[1].default_value=0;nt.links.new(a.outputs['Fac'],cmp.inputs[0])
        mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';nt.links.new(cmp.outputs[0],mix.inputs[0]);mix.inputs[1].default_value=(*rgb(colors[0]),1)
        if current:nt.links.new(current,mix.inputs[1])
        mix.inputs[2].default_value=(*rgb(color),1);current=mix.outputs[0]
    nt.links.new(current,p.inputs['Base Color']);return m
def attribute(o,n,fn):
    a=o.data.attributes.new(n,'FLOAT','POINT')
    for i,v in enumerate(o.data.vertices):a.data[i].value=fn(*v.co)


# The original body remains a context for this focused head study.
body=bpy.data.objects.get('Renard · corps continu et mains')
# New palette / shading: diffuse illustrated surfaces, no shiny toy highlights.
PALETTE={'terracotta':'CC5B38','cream':'FAE6CC','charcoal':'30363C','sage':'7B8E7E','ear':'E9AB85'}
for m in [orange,cream,black,inner,sage,sageDark]:
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Specular IOR Level'].default_value=.05;p.inputs['Roughness'].default_value=.9
orange.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*rgb(PALETTE['terracotta']),1)
cream.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*rgb(PALETTE['cream']),1)
# Broader, gently flattened cranium; slim forward muzzle. Two small integrated cheek points only.
headparts=[tube('Crâne et museau · surface continue',[(0,.34,5.49,.025,.06),(0,.23,5.50,.27,.285),(0,.05,5.52,.405,.33),(0,-.12,5.52,.425,.31),(0,-.28,5.50,.37,.235),(0,-.43,5.49,.285,.155),(0,-.64,5.51,.175,.087),(0,-.84,5.56,.075,.040),(0,-.905,5.585,.020,.020)],orange,segments=64,steps=6)]
for s in [-1,1]:
    headparts.append(tube('Joue · décroché court '+str(s),[(s*.20,.06,5.38,.14,.115),(s*.30,.18,5.30,.105,.075),(s*.43,.30,5.245,.004,.004)],orange,segments=32,steps=5))
    headparts.append(tube('Joue · petite pointe basse '+str(s),[(s*.18,.06,5.27,.13,.105),(s*.275,.16,5.23,.095,.060),(s*.415,.29,5.17,.004,.004)],orange,segments=32,steps=5))
headparts.append(tube('Cou · raccord intégré',[(0,.045,4.77,.205,.195),(0,.05,4.98,.215,.205),(0,.06,5.20,.235,.215)],orange,segments=48,steps=5))
head=weld('Renard · tête et museau sculptés',headparts,.010)
# Flatten the crown gently; preserve the side planes supporting the eyes.
for vert in head.data.vertices:
    if vert.co.z>5.70:vert.co.z=5.70+(vert.co.z-5.70)*.72
# Shape a recessed frontal plane with smooth transitions into the muzzle.
def smooth01(t):
    t=max(0,min(1,t));return t*t*(3-2*t)
for vert in head.data.vertices:
    x,y,z=vert.co
    if y<-.22 and 5.50<z<5.84 and abs(x)<.40:
        weight=smooth01((z-5.50)/.055)*smooth01((5.84-z)/.10)*smooth01((.40-abs(x))/.055)*smooth01((y+.70)/.18)
        target=-.355+.10*(abs(x)/.40)**4
        vert.co.y=y+weight*max(0,target-y)
bpy.context.view_layer.objects.active=head
sm=head.modifiers.new('Transitions des plans du visage','SMOOTH');sm.factor=.45;sm.iterations=8
bpy.ops.object.modifier_apply(modifier=sm.name)
# The old neck end is tucked inside the scarf; the new neck belongs to the head mesh.
for vert in body.data.vertices:
    if vert.co.z>4.83:vert.co.z=4.83+.15*(vert.co.z-4.83)

def jawmark(x,y,z):
    cheek=(1-((y+.20)/.31)**2-((z-5.305)/.17)**2)*.12
    muzzle=min(-.24-y,5.415+.15*max(0,-y-.42)-z)
    neck=min(.23-abs(x),5.23-z,-.025-y)
    return max(cheek,muzzle,neck)
attribute(head,'jaw',jawmark);head.data.materials.clear();head.data.materials.append(masked_material('V4 · masque crème arrondi',['jaw'],[PALETTE['terracotta'],PALETTE['cream']]))
# Ears: shorter triangles, widest at the root; one closed mesh per ear, no detached pink plates.
def ear(s):
    secs=[(s*.28,.12,5.68,.095,.085),(s*.335,.12,5.875,.205,.095),(s*.388,.13,6.02,.185,.090),(s*.455,.15,6.225,.126,.067),(s*.525,.17,6.42,.052,.035),(s*.557,.18,6.505,.002,.003)]
    ss=interpolate(secs,7);N=64;v=[];f=[];ts=[];masks=[];rims=[]
    for i,(cx,cy,z,w,dep) in enumerate(ss):
        t=(z-5.875)/(.630)
        z=5.740+(z-5.875)*.70
        for k in range(N):
            a=2*math.pi*k/N;u=math.cos(a);sn=math.sin(a);yy=cy+dep*(.35*sn*sn if sn<0 else sn)
            v.append((cx+w*u,yy,z));ts.append(t)
            masks.append(min(t-.12,.91-t,.77-abs(u),-sn-.20))
            rims.append(max(t-.80,min(t-.08,max(s*u-.75,abs(u)-.94))))
    for j in range(len(ss)-1):
        for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
    f.append(tuple(reversed(range(N))));f.append(tuple((len(ss)-1)*N+k for k in range(N)))
    o=mesh('V4 · Oreille '+('G' if s<0 else 'D'),v,f,orange)
    for name,values in [('inner',masks),('rim',rims),('height',ts)]:
        attr=o.data.attributes.new(name,'FLOAT','POINT')
        for datum,value in zip(attr.data,values):datum.value=value
    nt=bpy.data.materials.new('V4 · Oreille · couleur intégrée '+str(s));nt.use_nodes=True;nodes=nt.node_tree.nodes;links=nt.node_tree.links;p=nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.95;p.inputs['Specular IOR Level'].default_value=.03
    a=nodes.new('ShaderNodeAttribute');a.attribute_name='height';r=nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.1;r.color_ramp.elements[0].color=(*rgb('FAE3C7'),1);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(*rgb('EAA17C'),1);links.new(a.outputs['Fac'],r.inputs[0])
    def attmask(name):
        a=nodes.new('ShaderNodeAttribute');a.attribute_name=name;c=nodes.new('ShaderNodeMath');c.operation='GREATER_THAN';c.inputs[1].default_value=0;links.new(a.outputs['Fac'],c.inputs[0]);return c.outputs[0]
    mix=nodes.new('ShaderNodeMixRGB');links.new(attmask('inner'),mix.inputs[0]);mix.inputs[1].default_value=(*rgb(PALETTE['terracotta']),1);links.new(r.outputs[0],mix.inputs[2]);mix2=nodes.new('ShaderNodeMixRGB');links.new(attmask('rim'),mix2.inputs[0]);links.new(mix.outputs[0],mix2.inputs[1]);mix2.inputs[2].default_value=(*rgb(PALETTE['charcoal']),1);links.new(mix2.outputs[0],p.inputs['Base Color']);o.data.materials.clear();o.data.materials.append(nt)
    angle=math.radians(-22 if s<0 else 6);pivot=Vector((s*.335,.12,5.740))
    for vert in o.data.vertices:
        q=vert.co-pivot;vert.co=pivot+Vector((q.x*math.cos(angle)-q.y*math.sin(angle),q.x*math.sin(angle)+q.y*math.cos(angle),q.z))
    sub(o,2)
    # Consistent normals on the closed shell.
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
for s in [-1,1]:ear(s)
# One eye surface with a procedural iris; no separate circular geometry in front of the white.
COL=facecol;bpy.context.view_layer.update();bvh=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
def eye_material(s):
    m=bpy.data.materials.new('V4 · Œil · regard '+str(s));m.use_nodes=True;nt=m.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.55;p.inputs['Specular IOR Level'].default_value=.10
    uv=n.new('ShaderNodeUVMap');uv.uv_map='Regard';sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0]);u=sep.outputs['X'];v=sep.outputs['Y']
    def mathn(op,a,b=None):
        x=n.new('ShaderNodeMath');x.operation=op
        if isinstance(a,(float,int)):x.inputs[0].default_value=a
        else:l.new(a,x.inputs[0])
        if b is not None:
            if isinstance(b,(float,int)):x.inputs[1].default_value=b
            else:l.new(b,x.inputs[1])
        return x.outputs[0]
    # Named values are future gaze controls, not animated yet.
    gx=n.new('ShaderNodeValue');gx.name='Regard horizontal';gx.outputs[0].default_value=.019
    gy=n.new('ShaderNodeValue');gy.name='Regard vertical';gy.outputs[0].default_value=.006
    du=mathn('SUBTRACT',u,gx.outputs[0]);dv=mathn('SUBTRACT',v,gy.outputs[0]);d=mathn('SQRT',mathn('ADD',mathn('MULTIPLY',du,du),mathn('MULTIPLY',dv,dv)));norm=mathn('DIVIDE',d,.052)
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='LINEAR';rr=ramp.color_ramp
    rr.elements.remove(rr.elements[1]);rr.elements[0].position=0;rr.elements[0].color=(*rgb('1D2427'),1)
    for pos,col in [(.61,'1D2427'),(.64,'603C1E'),(.67,'C27A21'),(.86,'DEA047'),(.95,'A45D1E'),(.985,'493825'),(1,'FFF7E8')]:rr.elements.new(pos).color=(*rgb(col),1)
    l.new(norm,ramp.inputs[0])
    # A single small painted reflection follows the iris; no floating sphere.
    hu=mathn('DIVIDE',mathn('ADD',du,.018),.0065);hv=mathn('DIVIDE',mathn('SUBTRACT',dv,.025),.008);hd=mathn('ADD',mathn('MULTIPLY',hu,hu),mathn('MULTIPLY',hv,hv));hl=mathn('LESS_THAN',hd,1)
    mix=n.new('ShaderNodeMixRGB');l.new(hl,mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=(*rgb('FFFDF3'),1);l.new(mix.outputs[0],p.inputs['Base Color']);m['controls']='Valeurs Regard horizontal / Regard vertical ; non animées';return m
for s in [-1,1]:
    center=Vector((s*.245,-.34,5.625));normal=Vector((s*.26,-.966,.025)).normalized();right=Vector((.966,s*.26,0)).normalized();up=normal.cross(right).normalized()
    hit0,nn0,idx0,dist0=bvh.ray_cast(center+normal*2,-normal,4);origin=(hit0 if hit0 is not None else center)-normal*.009
    def skin(u,v,d):
        hit,nn,idx,dist=bvh.ray_cast(origin+right*u+up*v+normal*2,-normal,4)
        return hit+nn*d if hit is not None else origin+right*u+up*v+normal*d
    def project(u,v,d):return origin+right*u+up*v+normal*d
    # A shallow inset supports a nearly flat iris without a projecting eyeball.
    for vert in head.data.vertices:
        q=vert.co-origin;uu=q.dot(right);vv=q.dot(up);dd=q.dot(normal);r2=(uu/.090)**2+(vv/.058)**2
        if r2<1.6 and -.12<dd<.12:
            t=max(0,min(1,(1.6-r2)/.55));weight=t*t*(3-2*t)
            vert.co+=normal*((min(dd,-.001)-dd)*weight)
    N=80;R=10;verts=[project(0,0,.006)];uvs=[(0,0)];faces=[]
    def boundary(a):
        u=.085*math.cos(a);si=math.sin(a);v=(.054 if si>=0 else .053)*(1 if si>=0 else -1)*abs(si)**.86+.012*u;return u,v
    for j in range(1,R+1):
        t=j/R
        for k in range(N):
            u,v=boundary(2*math.pi*k/N);u*=t;v*=t;verts.append(project(u,v,.002+.004*(1-t*t)));uvs.append((u,v))
    for k in range(N):faces.append((0,1+k,1+(k+1)%N))
    for j in range(R-1):
        for k in range(N):a=1+j*N+k;b=1+j*N+(k+1)%N;faces.append((a,a+N,b+N,b))
    eye=mesh('V4 · Œil continu '+str(s),verts,faces,eye_material(s));uv=eye.data.uv_layers.new(name='Regard')
    for poly in eye.data.polygons:
        for li in poly.loop_indices:uv.data[li].uv=uvs[eye.data.loops[li].vertex_index]
    # The sculpted socket itself forms the orange eyelid contour.
    top=[]
    for k in range(17):
        a=math.pi*k/16;u,v=boundary(a);top.append(project(u,v,.004))
    q=curve('V4 · Ligne fine paupière '+str(s),top,.0055,black)
    for k,b in enumerate(q.data.splines[0].bezier_points):b.radius=.2+.8*math.sin(math.pi*k/16)
    q=curve('V4 · Sourcil doux '+str(s),[skin(-.095,.090,.004),skin(-.042,.112,.004),skin(.025,.118,.004),skin(.07,.105,.003)],.0105,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.2,1,.9,.2]):b.radius=r
# A rounded triangular nose, smaller than the previous round button.
vs=[(-.074,-.942,5.621),(.074,-.942,5.641),(0,-.955,5.540),(-.057,-.888,5.610),(.057,-.888,5.630),(0,-.894,5.550)]
truffe=mesh('V4 · Truffe triangulaire',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],black);be=truffe.modifiers.new('Angles adoucis','BEVEL');be.width=.016;be.segments=4;be.affect='EDGES'
for s in [-1,1]:
    pts=[]
    for pos in [(s*.27,-.29,5.37),(s*.23,-.43,5.355),(s*.125,-.68,5.410),(s*.045,-.885,5.565)]:
        hit,nn,idx,dist=bvh.find_nearest(Vector(pos));pts.append(hit+nn*.005)
    q=curve('V4 · Sourire retenu '+str(s),pts,.004,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.45,1,.8,.18]):b.radius=r
# Matte palette, balanced neutral light and an unlit contribution to retain the illustration's warm colors.
for m in bpy.data.materials:
    if not m.use_nodes:continue
    nt=m.node_tree;p=nt.nodes.get('Principled BSDF')
    if not p:continue
    p.inputs['Roughness'].default_value=max(.7,p.inputs['Roughness'].default_value);p.inputs['Specular IOR Level'].default_value=.06
    # Existing body masks retain the palette while the new head is reviewed.
    for n in nt.nodes:
        if n.type=='MIX_RGB':
            for i in [1,2]:
                if not n.inputs[i].is_linked:
                    c=n.inputs[i].default_value
                    if abs(c[0]-rgb('C94E29')[0])<.01 and abs(c[1]-rgb('C94E29')[1])<.01:n.inputs[i].default_value=(*rgb(PALETTE['terracotta']),1)
    color=p.inputs['Base Color'];em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.80
    if color.is_linked:nt.links.new(color.links[0].from_socket,em.inputs['Color'])
    else:em.inputs['Color'].default_value=color.default_value
    out=nt.nodes.get('Material Output');mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.32;nt.links.new(p.outputs['BSDF'],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.render.threads_mode='FIXED';scene.render.threads=10
scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(1,1,1,1);bg.inputs['Strength'].default_value=.55
for o in studio.objects:
    if o.type=='LIGHT':
        o.data.color=(1,.97,.93);o.data.energy*=.55
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-.05
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.fps=30
COL=studio
def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def cam(name,loc,target,scale):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);studio.objects.link(o);data.type='ORTHO';data.ortho_scale=scale;o.location=loc;aim(o,target);return o
cams={'trois-quarts':cam('V4 · tête trois quarts',(-17,-12,6.05),(0,-.15,5.64),1.95),'face':cam('V4 · tête face',(0,-17,5.64),(0,0,5.64),1.95),'profil':cam('V4 · tête profil',(-17,-.33,5.64),(0,-.33,5.64),1.95)}
scene.camera=cams['trois-quarts'];scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.filepath=str(OUT/'renard-v4-');scene['statut']='ÉTUDE TÊTE V4 — non validée';scene['retouches']='Crâne compact et moins bombé ; museau raccourci ; yeux légèrement encastrés, contours de paupières dans le volume ; bordures anthracite élargies' ;scene['rig']='Absent — étude de design statique'
scene['eye_contour_revision']='integrated-v4'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-etude-tete-v4.blend'))
scene.render.resolution_x=1000;scene.render.resolution_y=1000
for name,c in cams.items():
    if name not in ['trois-quarts','profil']:continue
    scene.camera=c;scene.render.filepath=str(OUT/('renard-v4-tete-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('HEAD_STUDY_COMPLETE')
