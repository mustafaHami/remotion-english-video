# HISTORIQUE REJETE — cette proposition a ete refusee.
# Reprise actuelle : scripts/sculpt_fox_head_v3.py et docs/renard-etude-tete-v3.md.
import bpy, math, json, hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
ROOT=Path('D:/ai-generation-video'); OUT=ROOT/'output/blender/v2/retouches-01'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection': bpy.data.collections.remove(c)
base=bpy.data.collections.get('Collection'); base.name='01 — Renard · volumes'
def coll(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c
facecol=coll('02 — Visage · regard et expression'); clothcol=coll('03 — Foulard'); studio=coll('04 — Studio · cameras et lumières'); construct=coll('90 — Construction · volumes sources'); construct.hide_render=True; construct.hide_viewport=True
reference=coll('99 — Référence approuvée'); reference.hide_render=True; reference.hide_viewport=True
COL=base
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
    sm=o.modifiers.new('Lissage des raccords','SMOOTH');sm.factor=.6;sm.iterations=5
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

# Proportions: long legs, lean torso, modest head. Front is -Y.
parts=[]
parts.append(tube('Buste et cou',[(0,.08,2.4,.28,.23),(0,.07,2.8,.48,.34),(0,.03,3.3,.49,.34),(0,0,3.8,.45,.31),(0,0,4.25,.50,.34),(0,.035,4.55,.48,.30),(0,.07,4.8,.25,.23),(0,.07,5.10,.24,.22)],orange))
for sign in [-1,1]:
    parts.append(tube('Jambe '+str(sign),[(sign*.20,.055,3.34,.10,.11),(sign*.24,.055,3.13,.18,.19),(sign*.28,.055,2.98,.22,.23),(sign*.34,.06,2.6,.27,.28),(sign*.38,.02,2.08,.23,.23),(sign*.40,-.02,1.65,.185,.18),(sign*.40,.04,1.25,.15,.15),(sign*.40,.07,.75,.115,.12),(sign*.40,.03,.24,.11,.12)],orange))
    parts.append(tube('Pied '+str(sign),[(sign*.40,.12,.14,.105,.12),(sign*.40,0,.13,.13,.13),(sign*.40,-.24,.115,.16,.115),(sign*.40,-.39,.10,.12,.08),(sign*.40,-.45,.10,.015,.03)],orange,steps=4))
    parts.append(tube('Bras '+str(sign),[(sign*.30,.02,4.51,.15,.15),(sign*.50,.02,4.35,.23,.215),(sign*.61,.02,4.18,.215,.20),(sign*.72,-.02,3.85,.18,.175),(sign*.78,-.06,3.56,.15,.15),(sign*.85,-.12,3.22,.12,.13),(sign*.88,-.18,2.96,.095,.10)],orange))
    # Slender palm, individual tapered and relaxed fingers, integrated into the body.
    parts.append(tube('Paume '+str(sign),[(sign*.872,-.14,3.16,.095,.10),(sign*.883,-.175,3.04,.093,.087),(sign*.89,-.19,2.90,.11,.075),(sign*.89,-.195,2.76,.118,.066),(sign*.89,-.21,2.68,.083,.055)],orange,segments=32))
    for j,length in enumerate([.25,.32,.30,.24]):
        x=sign*(.796+j*.062);z=2.74
        parts.append(tube('Doigt '+str(sign)+' '+str(j),[(x,-.195,z,.026,.026),(x+sign*.005,-.21,z-.105,.021,.023),(x+sign*.010,-.265,z-length*.72,.020,.022),(x+sign*.008,-.28,z-length+.037,.020,.021),(x+sign*.008,-.28,z-length+.013,.015,.016),(x+sign*.008,-.28,z-length,.003,.004)],orange,segments=24,steps=4))
    parts.append(tube('Pouce '+str(sign),[(sign*.80,-.20,2.89,.042,.038),(sign*.747,-.275,2.79,.034,.033),(sign*.75,-.323,2.69,.027,.027),(sign*.776,-.319,2.65,.017,.017),(sign*.783,-.314,2.65,.003,.004)],orange,segments=24,steps=4))
body=weld('Renard · corps continu et mains',parts,.009)
attribute(body,'bib',lambda x,y,z: min(-.045-y, (.30 if z>4.4 else .40*math.sqrt(max(0,1-((z-3.5)/1.2)**2)))-abs(x),z-2.30,5.20-z))
attribute(body,'gloves_boots',lambda x,y,z:max(1.30+.026*math.sin(x*57+y*22)-z, min(abs(x)-.66,3.44+.028*math.sin(x*62+y*28)-z)))
body.data.materials.clear();body.data.materials.append(masked_material('Corps · marques continues',['bib','gloves_boots'],['C94E29','F7E5CD','30363C']))
# Head: welded tapered snout, jaw, cheek volumes. No stack of spheres remains visible.
# One longitudinal head surface; the jaw and snout no longer create a ledge.
headparts=[tube('Tête · sections longitudinales',[(0,.48,5.51,.035,.05),(0,.37,5.53,.27,.37),(0,.15,5.52,.46,.54),(0,-.05,5.51,.49,.50),(0,-.22,5.50,.42,.39),(0,-.40,5.455,.30,.235),(0,-.60,5.455,.21,.133),(0,-.78,5.48,.125,.071),(0,-.905,5.505,.035,.032)],orange,segments=64,steps=6)]
for s in [-1,1]:
    headparts.append(tube('Joue effilée '+str(s),[(s*.34,.08,5.43,.12,.16),(s*.43,.18,5.25,.105,.13),(s*.57,.29,5.10,.037,.040),(s*.68,.35,5.075,.004,.004)],orange,segments=24))
    headparts.append(tube('Mèche basse '+str(s),[(s*.34,.13,5.22,.10,.12),(s*.45,.21,5.11,.08,.07),(s*.61,.28,5.035,.004,.004)],orange,segments=24))
head=weld('Renard · tête et museau sculptés',headparts,.014)
attribute(head,'jaw',lambda x,y,z:min(max(5.29+.14*math.sqrt(max(0,1-((y+.20)/.47)**2)),5.35+.225*max(0,-y-.25))-z, max(-.14+.095*math.sqrt(max(0,1-((z-5.29)/.16)**2))-y,min(5.20-z,.245-abs(x),-.01-y))))
head.data.materials.clear();head.data.materials.append(masked_material('Tête · masque crème continu',['jaw'],['C94E29','F7E5CD']))
# Three-dimensional ears, thick roots and tapered pointed rims.
COL=base
def ear(s):
    # Closed, gently cupped ear. Narrow triangular silhouette and a thin outer dark rim.
    secs=[(s*.31,.13,5.88,.15,.09),(s*.36,.14,6.07,.195,.105),(s*.425,.15,6.28,.157,.085),(s*.49,.16,6.52,.090,.055),(s*.53,.17,6.70,.032,.026),(s*.541,.174,6.78,.002,.003)]
    ss=interpolate(secs,6);v=[];f=[];N=64
    for cx,cy,z,w,depth in ss:
        for k in range(N):
            a=2*math.pi*k/N;u=math.cos(a);si=math.sin(a)
            yy=cy+depth*(.42*si*si if si<0 else si)
            v.append((cx+w*u,yy,z))
    for i in range(len(ss)-1):
        for k in range(N):a=i*N+k;b=i*N+(k+1)%N;f.append((a,b,b+N,a+N))
    f.append(tuple(reversed(range(N))));f.append(tuple((len(ss)-1)*N+k for k in range(N)))
    o=mesh('Oreille '+('G' if s<0 else 'D'),v,f,orange);sub(o,2)
    attribute(o,'ear_rim',lambda x,y,z:z-6.702)
    o.data.materials.clear();o.data.materials.append(masked_material('Oreille · pointe sombre '+str(s),['ear_rim'],['C94E29','30363C']))
    # Interior follows the concavity and is inset within the orange rim.
    v=[];f=[];M=14;Q=22
    for i in range(Q+1):
        t=i/Q;z=6.09+t*.59
        # smooth interpolation across the ear's original cross sections
        a=min(range(len(ss)),key=lambda k:abs(ss[k][2]-z));cx,cy,zz,w,dep=ss[a]
        width=w*.72*math.sin(math.pi*(.13+.87*t))**.35
        for j in range(M+1):
            u=-1+2*j/M;xu=u*width;relative=xu/max(w,.001)
            yy=cy+dep*.42*(1-relative*relative)-.006
            v.append((cx+xu,yy,z))
    for i in range(Q):
        for j in range(M):a=i*(M+1)+j;f.append((a,a+1,a+M+2,a+M+1))
    q=mesh('Oreille · intérieur '+str(s),v,f,inner);attribute(q,'ear_light',lambda x,y,z:6.21-z);q.data.materials.clear();q.data.materials.append(masked_material('Oreille · intérieur chaud '+str(s),['ear_light'],['EFAE83','F7E5CD']))
    sol=q.modifiers.new('Épaisseur de la conque','SOLIDIFY');sol.thickness=.012;sub(q,2)
    rim=[]
    for sec in secs[1:]:cx,cy,z,w,dep=sec;rim.append((cx+s*w,cy-.006,z))
    q=curve('Oreille · liseré extérieur '+str(s),rim,.020,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.65,1,1,.85,.4]):b.radius=r
for s in [-1,1]:
    before=set(base.objects);ear(s);created=set(base.objects)-before
    angle=math.radians(-22 if s<0 else 6);pivot=Vector((s*.31,.13,5.88))
    def rotate_ear(p):
        q=Vector(p)-pivot;return pivot+Vector((q.x*math.cos(angle)-q.y*math.sin(angle),q.x*math.sin(angle)+q.y*math.cos(angle),q.z))
    for o in created:
        if o.type=='MESH':
            for v in o.data.vertices:v.co=rotate_ear(v.co)
        elif o.type=='CURVE':
            for spl in o.data.splines:
                for b in spl.bezier_points:b.co=rotate_ear(b.co);b.handle_left_type='AUTO';b.handle_right_type='AUTO'

# Tail is a single swept surface with serrated cream marking, not a detached cap.
tail=tube('Queue · longue silhouette',[(0,.29,2.69,.18,.19),(-.35,.66,2.48,.26,.24),(-.85,.94,2.15,.40,.35),(-1.36,1.08,1.77,.53,.42),(-1.86,1.08,1.30,.48,.34),(-2.23,1.0,.93,.31,.22),(-2.49,.90,.65,.10,.085),(-2.53,.89,.60,.006,.008)],orange,segments=48,steps=6);sub(tail,2);tail.data.materials.append(cream)
attribute(tail,'tail_tip',lambda x,y,z:-1.73+.18*(2*abs(((z*2.4+y*.7)%1)-.5)-.5)-x)
tail.data.materials.clear();tm=masked_material('Queue · pointe crème dentelée',['tail_tip'],['C94E29','F7E5CD']);tail.data.materials.append(tm)
nt=tm.node_tree;geo=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],xyz.inputs[0])
def mathnode(op,a,b=None):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    if isinstance(a,(float,int)):n.inputs[0].default_value=a
    else:nt.links.new(a,n.inputs[0])
    if b is not None:
        if isinstance(b,(float,int)):n.inputs[1].default_value=b
        else:nt.links.new(b,n.inputs[1])
    return n.outputs[0]
w=mathnode('ADD',mathnode('MULTIPLY',xyz.outputs['Z'],2.4),mathnode('MULTIPLY',xyz.outputs['Y'],.7));w=mathnode('FRACT',w);w=mathnode('ABSOLUTE',mathnode('SUBTRACT',w,.5));w=mathnode('SUBTRACT',mathnode('MULTIPLY',w,2),.5);w=mathnode('ADD',mathnode('MULTIPLY',w,.29),-1.74);w=mathnode('SUBTRACT',w,xyz.outputs['X'])
for n in nt.nodes:
    if n.type=='MATH' and n.operation=='GREATER_THAN':nt.links.new(w,n.inputs[0]);break

# Compact eyes: restrained sclera, one warm iris, relaxed tapered lids.
COL=facecol
bpy.context.view_layer.update();bvh=BVHTree.FromObject(head,bpy.context.evaluated_depsgraph_get())
for s in [-1,1]:
    normal=Vector((s*.56,-.83,.04)).normalized();right=Vector((.83,s*.56,0)).normalized();up=normal.cross(right).normalized();center=Vector((s*.366,-.32,5.65))
    def pt(u,v,d=.008):
        ray=center+right*u+up*v+normal*2;hit,n,idx,dist=bvh.ray_cast(ray,-normal,4)
        return hit+n*d if hit is not None else center+right*u+up*v+normal*d
    N=64;v=[pt(0,0,.026)];f=[]
    def ocular(u,v):return .010+.016*max(0,1-(u/.105)**2-(v/.074)**2)
    for r in range(1,7):
        t=r/6
        for i in range(N):
            a=2*math.pi*i/N;u=t*.104*math.cos(a);vv=t*(.072 if math.sin(a)>0 else .058)*math.sin(a)*(.74+.26*abs(math.sin(a)))+.022*u
            v.append(pt(u,vv,ocular(u,vv)))
    for i in range(N):f.append((0,i+1,(i+1)%N+1))
    for r in range(5):
        for i in range(N):a=1+r*N+i;b=1+r*N+(i+1)%N;f.append((a,b,b+N,a+N))
    mesh('Œil · blanc intégré '+str(s),v,f,white)
    # Gaze toward the reference's direction, with convergent optical axes.
    iu=-.008-s*.038;iv=.003
    def disk(n,r,m,extra):
        vv=[pt(iu,iv,ocular(iu,iv)+extra)];ff=[]
        for j in range(1,5):
            rr=r*j/4
            for k in range(N):
                a=2*math.pi*k/N;u=iu+rr*math.cos(a);v=iv+rr*math.sin(a)
                # Clip iris to the eyelid aperture so there are no exposed circular bulges.
                available=(.072 if v>0 else .058)*max(0,1-(u/.104)**2)**.52
                v=max(-available+.002,min(available-.002,v));vv.append(pt(u,v,ocular(u,v)+extra))
        for k in range(N):ff.append((0,k+1,(k+1)%N+1))
        for j in range(3):
            for k in range(N):a=1+j*N+k;b=1+j*N+(k+1)%N;ff.append((a,b,b+N,a+N))
        return mesh(n,vv,ff,m)
    disk('Iris · contour fin '+str(s),.061,black,.003)
    iris=disk('Iris · ambre '+str(s),.057,amber,.005)
    disk('Pupille '+str(s),.029,pupil,.008)
    h=pt(iu-.018,iv+.025,ocular(iu-.018,iv+.025)+.012);ell('Reflet principal '+str(s),h,(.010,.006,.010),glint)
    top=[];bottom=[]
    for k in range(13):
        a=math.pi*k/12;u=.104*math.cos(a);vv=math.sin(a)*(.74+.26*math.sin(a));top.append(pt(u,.072*vv+.022*u,.012));bottom.append(pt(u,-.058*vv+.022*u,.010))
    q=curve('Paupière supérieure '+str(s),top,.011,black)
    for k,b in enumerate(q.data.splines[0].bezier_points):b.radius=.25+.75*math.sin(math.pi*k/12)
    curve('Paupière inférieure '+str(s),bottom,.0045,orange)
    q=curve('Sourcil mobile '+str(s),[pt(-.105,.107,.009),pt(-.055,.14,.009),pt(.018,.144,.009),pt(.07,.126,.009)],.014,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.15,.8,1,.25]):b.radius=r
# Small nose and slim continuous mouth seam, a quiet smile rather than an oversized grin.
nose=ell('Truffe',(0,-.913,5.505),(.081,.056,.050),black)
for v in nose.data.vertices:
    if v.co.z<0:v.co.x*=.65
for s in [-1,1]:
    smile=[]
    for p in [(s*.255,-.34,5.36),(s*.225,-.49,5.33),(s*.135,-.715,5.395),(s*.038,-.875,5.483)]:
        hit,n,idx,dist=bvh.find_nearest(Vector(p));smile.append(hit+n*.007)
    q=curve('Sourire discret '+str(s),smile,.005,black)
    for b,r in zip(q.data.splines[0].bezier_points,[.35,.8,1,.25]):b.radius=r
# Cloth scarf, rolled upper edge and lower drape with actual fabric volume.
COL=clothcol
v=[];f=[];N=96;R=12
for j in range(R+1):
    t=j/R
    for k in range(N):
        a=2*math.pi*k/N;front=(1-math.sin(a))/2
        z=4.94-.39*t-.065*front*math.sin(math.pi*t)+.035*math.cos(2*a+t)
        rx=.32+.12*math.sin(math.pi*t);ry=.265+.10*math.sin(math.pi*t)
        v.append((rx*math.cos(a),.015+ry*math.sin(a),z))
for j in range(R):
    for k in range(N):a=j*N+k;b=j*N+(k+1)%N;f.append((a,b,b+N,a+N))
scarf=mesh('Foulard · col drapé',v,f,sage);sol=scarf.modifiers.new('Tissu épais','SOLIDIFY');sol.thickness=.040;sub(scarf,2)
curve('Foulard · pli du col',[(-.41,-.15,4.70),(-.30,-.30,4.61),(0,-.354,4.58),(.30,-.27,4.63),(.41,-.10,4.76)],.007,sageDark)
# Hanging asymmetric ribbon with longitudinal fold, extends in front of chest.
v=[];f=[];N=24;M=12
for i in range(N+1):
    t=i/N;z=4.68-t*1.45;cx=-.23-.045*t;w=.24-.012*t
    for j in range(M+1):
        u=-1+2*j/M;x=cx+u*w;y=-.345-.040*math.cos(u*math.pi*1.3)-.055*math.sin(t*math.pi);v.append((x,y,z+.045*math.sin(u*2.5+t)))
for i in range(N):
    for j in range(M):a=i*(M+1)+j;f.append((a,a+1,a+M+2,a+M+1))
ribbon=mesh('Foulard · pan et plis',v,f,sage);sol=ribbon.modifiers.new('Ourlet épais','SOLIDIFY');sol.thickness=.038;sub(ribbon,2)
for k in range(9):
    x=-.49+k*.052
    curve('Foulard · frange '+str(k),[(x,-.38,3.25),(x-.008,-.39,3.13+(k%3)*.015)],.012,sage)
curve('Foulard · pli longitudinal',[(-.31,-.403,4.51),(-.29,-.45,4.10),(-.33,-.427,3.45)],.008,sageDark)
# Reference packed; disabled for rendered views.
img=bpy.data.images.load(str(ROOT/'assets/branding/renard-reference-validee.png'));img.pack();o=bpy.data.objects.new('Planche approuvée · source 2D',None);reference.objects.link(o);o.empty_display_type='IMAGE';o.data=img;o.empty_display_size=7
# Studio: stable orthographic cameras for comparison, diffuse large softboxes.
COL=studio
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.cycles.max_bounces=6;scene.render.threads_mode='FIXED';scene.render.threads=10
scene.world.color=(.25,.25,.25);scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.72,.78,.85,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.45
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8';scene.render.resolution_percentage=100;scene.render.fps=30
scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.frame_start=1;scene.frame_end=240;scene.render.filepath=str(OUT/'renard-v2-')

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def light(n,loc,power,size,color):
    data=bpy.data.lights.new(n,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color;o=bpy.data.objects.new(n,data);studio.objects.link(o);o.location=loc;aim(o,(0,0,3.5))
light('Key · softbox',(-5,-8,10),950,7,(1,.86,.72));light('Fill · large',(6,-4,6),650,6,(.77,.87,1));light('Rim · warm',(2,5,9),1300,5,(1,.87,.72))
def camera(n,loc,target,scale):
    data=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,data);studio.objects.link(o);o.location=loc;aim(o,target);data.type='ORTHO';data.ortho_scale=scale;data.lens=65;return o
cams={
'face':camera('Caméra · face',(-.55,-17,3.55),(-.55,0,3.55),8.1),
'profil':camera('Caméra · profil',(-16,0,3.55),(0,0,3.55),8.1),
'trois-quarts':camera('Caméra · trois quarts',(-16,-14,4.8),(-.5,0,3.5),8.1),
'visage':camera('Caméra · détail visage',(-16,-14,6.10),(0,-.15,5.70),2.55),
'mains':camera('Caméra · détail main',(-5,-10,3.05),(-.87,-.20,2.84),1.02)}
scene.camera=cams['trois-quarts']
# Meaningful model metadata; no animation claim.
scene['statut']='PROPOSITION 3D RETOUCHÉE 01 — apparence non validée'
scene['retouches']='Yeux compacts, museau effilé, oreilles triangulaires cuppées, mains affinées'
scene['reference_unique']='output/design/renard-expressions-v2-regard.png';scene['reference']='assets/branding/renard-reference-validee.png';scene['orientation']='Face -Y ; haut +Z ; unités arbitraires';scene['rig']='Non créé : validation du design attendue';scene['source_preservee']='blender/Untitled.blend'
body['construction']='Volume continu fusionné, mains incluses. Sources conservées dans collection 90.';head['construction']='Crâne, museau et joues soudés. Regard séparé pour futurs contrôles.'
# Set useful viewport for inspection.
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_distance=11;area.spaces.active.region_3d.view_location=Vector((0,0,3.5));area.spaces.active.shading.type='MATERIAL'
if hasattr(bpy.context.preferences.filepaths,'use_save_preview'): bpy.context.preferences.filepaths.use_save_preview=False
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'))
# Reduced review renders; saved .blend keeps requested integration settings.
scene.render.resolution_x=900;scene.render.resolution_y=1100
for name,cam in cams.items():
    scene.camera=cam;scene.render.filepath=str(OUT/('renard-v2-'+name+'.png'));bpy.ops.render.render(write_still=True)
report={'blender':bpy.app.version_string,'status':'proposition statique non validée','objects':len(bpy.data.objects),'mesh_vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('Source')),'renders':list(cams),'rig':False,'animations':[],'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
print('V2_BUILD_COMPLETE',json.dumps(report,ensure_ascii=False))
