"""Build reusable Blender actions. No Remotion source is changed."""
import bpy, math, json, time
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view
R=Path('D:/ai-generation-video'); O=R/'output/blender/mouvements-v2'; O.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene; rig=bpy.data.objects['RIG · Renard']; route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant']; ad=rig.data
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
rig.animation_data_create();rig.animation_data.action=None;route.animation_data_clear();route.location=(0,0,0);route.rotation_euler=(0,0,0);route.scale=(1,1,1)
for a in list(bpy.data.actions):
    if a.name.startswith(('MVT_','ACC_')):bpy.data.actions.remove(a)
ctrls=[p for p in rig.pose.bones if p.name.startswith('CTRL_') or p.name.startswith('D_oreille_pointe')]
for p in ctrls:p.rotation_mode='QUATERNION'
for tag in ['G','D']:
    for prop,val in [('pouce_'+tag,0.),('index_'+tag,1.)]:rig[prop]=val;rig.id_properties_ui(prop).update(min=0,max=1)
    for pb in rig.pose.bones:
        if pb.name.endswith('.'+tag) and pb.name.startswith(('D_pouce','D_doigt0')):
            try:pb.driver_remove('rotation_euler',0)
            except:pass
            d=pb.driver_add('rotation_euler',0).driver
            if pb.name.startswith('D_pouce'):
                d.expression='-v*.7';v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["pouce_'+tag+'"]'
            else:
                d.expression='-v*k*1.25'
                for n,prop in [('v','doigts_'+tag),('k','index_'+tag)]:v=d.variables.new();v.name=n;v.targets[0].id=rig;v.targets[0].data_path='["'+prop+'"]'

def ease(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def lerp(a,b,t):return a+(b-a)*t
def mix(a,b,t):return Vector(a).lerp(Vector(b),t)
def Q(x=0,y=0,z=0):return Quaternion((0,0,1),math.radians(z))@Quaternion((0,1,0),math.radians(y))@Quaternion((1,0,0),math.radians(x))
def place(n,pos,q=None):
    p=rig.pose.bones[n];p.matrix=Matrix.Translation(Vector(pos))@(q or Q()).to_matrix().to_4x4()@ad.bones[n].matrix_local.to_3x3().to_4x4()
def rot(n,x=0,y=0,z=0):rig.pose.bones[n].rotation_quaternion=Q(x,y,z)
def gesture(u):return ease(u/.24)*(1-ease((u-.73)/.27))

# Independent, editable accessory collections, all in the same camera space.
acc=bpy.data.collections.new('09 — Accessoires animés · indépendants');s.collection.children.link(acc)
def material(n,c,emission=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.55
    if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
    return m
def lin(h):
    c=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)
gold=material('Ampoule · ambre lumineux',lin('FFD274'),.8);metal=material('Accessoires · anthracite',lin('30363C'));sage=material('Loupe · sauge',lin('7B8E7E'));lightmat=material('Ampoule · reflet crème',lin('FFF7DF'),.2)
def empty(n):o=bpy.data.objects.new(n,None);acc.objects.link(o);return o
bulb=empty('ACCESSOIRE · Ampoule');magnifier=empty('ACCESSOIRE · Loupe')
def moveacc(o,parent,mat):
    for c in list(o.users_collection):c.objects.unlink(o)
    acc.objects.link(o);o.parent=parent;o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=True
    return o
def uvball(n,pos,scale,parent,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=pos);o=bpy.context.object;o.name=n;o.scale=scale;return moveacc(o,parent,mat)
uvball('Ampoule · globe',(0,0,.31),(.20,.20,.25),bulb,gold)
uvball('Ampoule · culot',(0,0,.04),(.12,.12,.10),bulb,metal)
uvball('Ampoule · reflet',(-.055,-.176,.39),(.037,.02,.075),bulb,lightmat)
bpy.ops.mesh.primitive_torus_add(major_radius=.32,minor_radius=.038,major_segments=40,minor_segments=10,location=(0,0,.65),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='Loupe · cerclage';moveacc(o,magnifier,sage)
uvball('Loupe · manche',(0,0,.21),(.055,.055,.24),magnifier,metal)
uvball('Loupe · jonction',(0,0,.38),(.067,.055,.07),magnifier,sage)
# The open centre intentionally keeps lesson text readable when used as an overlay.
props=[bulb,magnifier]
propkeys=['clignement','sourire','curieux','regard_horizontal','regard_vertical','doigts_G','doigts_D','pouce_G','pouce_D','index_G','index_D']

def reset():
    for p in ctrls:p.matrix_basis.identity()
    for k in propkeys:rig[k]=.35 if k=='sourire' else 1 if k.startswith('index_') else 0
    rig['regard_horizontal']=.015;rig['regard_vertical']=.005
    for p in props:p.location=(0,0,0);p.rotation_euler=(0,0,0);p.scale=(0,0,0)

def pose_base(t,quad=0,phase=0,amp=0,still=False):
    reset();breath=0 if still else .007*math.sin(t*math.tau/4)
    place('CTRL_corps',mix((0,.02,2.75+breath),(0,.67,1.44+breath),quad),Q(88*quad))
    rot('CTRL_cou',-79*quad);rot('CTRL_tete',-9*quad)
    bpy.context.view_layer.update()
    # Footfalls: diagonal pairs with 64% stance. Root translation stays out of the sprites.
    for side in [-1,1]:
        tag='G' if side<0 else 'D'
        for kind in ['main','pied']:
            ph=(phase+{('main','G'):.25,('pied','G'):0,('main','D'):.75,('pied','D'):.5}[(kind,tag)])%1
            if ph<.64:y=-.3456+.6912*ph/.64;z=0;sw=0
            else:u=(ph-.64)/.36;y=.3456-.6912*ease(u);z=(.14 if kind=='main' else .17)*math.sin(math.pi*u);sw=math.sin(math.pi*u)
            y*=amp;z*=amp
            stand=(side*.885,-.17,2.95) if kind=='main' else (side*.4,.03,.24)
            four=(side*.59,-1.03+y,.15+z) if kind=='main' else (side*.42,.85+y,.24+z)
            target=mix(stand,four,quad)
            if kind=='main' and 0<quad<1:
                root0=Vector((side*.48,.02,4.4));root1=Vector((side*.48,.67-1.65*math.sin(math.radians(88)),1.44+1.65*math.cos(math.radians(88))))
                actual=rig.pose.bones['D_bras.'+tag].head.copy();actual.z-=breath
                target+=actual-root0.lerp(root1,quad)
            place('CTRL_'+kind+'.'+tag,target,Q((-65+6*sw*amp)*quad if kind=='main' else -3*sw*amp*quad))
        place('CTRL_coude.'+tag,mix((side*.8,1.4,3.7),(side*.77,.65,1.1),quad))
        place('CTRL_genou.'+tag,mix((side*.4,-1.7,1.5),(side*.42,-1.25,1.2),quad))
        a=0 if still else 1.4*(math.sin(t*math.tau/4+side*.4)-math.sin(side*.4))
        rot('CTRL_oreille.'+tag,a);rot('D_oreille_pointe.'+tag,a*.3)
    bpy.context.view_layer.update()
    p=rig.pose.bones['CTRL_queue_0'];pos=p.matrix.translation.copy();tq=Vector((-2.53,.60,-2.09)).rotation_difference(Vector((-.55,3.1,-.85)))
    place('CTRL_queue_0',pos,Q(z=(0 if still else 1.4*math.sin(t*math.tau/4)))@Q().slerp(tq,quad))
    for j in range(1,6):rot('CTRL_queue_%d'%j,y=0 if still else 1.4*(math.sin(t*math.tau/4-j*.45)-math.sin(-j*.45)))
    p=rig.pose.bones['CTRL_foulard'];place(p.name,p.matrix.translation,Q(-22*quad));rot('CTRL_foulard_pointe',0 if still else .5*math.sin(t*math.tau/4))

clips=[]
def add(id,title,n=90,loop=False,entry='debout',exit='debout',accessory=None):clips.append(dict(id=id,title=title,frames=n,loop=loop,entry=entry,exit=exit,accessory=accessory))
add('attente','Attente vivante',120,True)
add('attente-quatre-pattes','Attente à quatre pattes',120,True,'quadrupede','quadrupede')
add('marche','Marche sur place',36,True,'marche-phase-0','marche-phase-0')
add('demarrer-marche','Démarrage de marche',36,False,'quadrupede','marche-phase-0')
add('arreter-marche','Arrêt de marche',36,False,'marche-phase-0','quadrupede')
add('se-lever','Quatre pattes vers debout',60,False,'quadrupede','debout')
add('se-baisser','Debout vers quatre pattes',60,False,'debout','quadrupede')
for side in ['gauche','droite','haut']:add('presenter-'+side,'Présentation vers '+side)
add('reflechir','Réflexion et regard vers les choix',120)
add('decouvrir','Découverte avec ampoule',90,accessory='ampoule')
add('examiner-loupe','Examen avec loupe',120,accessory='loupe')
add('bravo','Réponse correcte et pouce levé')
add('encourager','Surprise douce puis encouragement')
add('ecouter','Invitation à écouter')
add('a-toi','Invitation à répéter')
add('saluer','Salut et au revoir')
add('retrait','Anticipation de disparition',36,False,'debout','retrait')
add('reapparaitre','Retour après réapparition',36,False,'retrait','debout')
add('regarder-haut','Regard vers un élément en haut')

def frame_pose(c,frame):
    id=c['id'];n=c['frames'];u=(frame-1)/(n-1);t=(frame-1)/30;g=gesture(u);loop=c['loop']
    quad=1 if id in ['attente-quatre-pattes','marche','demarrer-marche','arreter-marche'] else 1-ease(u) if id=='se-lever' else ease(u) if id=='se-baisser' else 0
    phase=(frame-1)/36;amp=1 if id=='marche' else ease(u) if id=='demarrer-marche' else 1-ease(u) if id=='arreter-marche' else 0
    # Transition endpoints are identical to canonical still poses; cyclic idle motion fades at gesture boundaries.
    pose_base(((frame-1)/36*4 if id=='marche' else t) if loop else 4*ease(u),quad,phase,amp,still=not loop)
    if not loop:
        for tag in ['G','D']:rot('CTRL_oreille.'+tag,1.5*math.sin(u*math.tau)*g)
        for j in range(1,6):rot('CTRL_queue_%d'%j,y=2*math.sin(u*math.tau-j*.35)*g)
    if id in ['se-lever','se-baisser']:
        # Staggered hind-foot repositioning, lifted in the middle of each short step.
        rise=1 if id=='se-lever' else 0;v=u if rise else 1-u
        for side in [-1,1]:
            tag='G' if side<0 else 'D';z=.24+.13*math.sin(math.pi*max(0,min(1,(v-(.15 if side<0 else .38))/.35)))
            k=ease((v-(.15 if side<0 else .38))/.35);place('CTRL_pied.'+tag,(side*lerp(.42,.4,k),lerp(.85,.03,k),z))
    elif id.startswith('presenter-'):
        side=1 if id.endswith('droite') else -1;tag='D' if side>0 else 'G';target=(side*1.25,-.42,4.2) if not id.endswith('haut') else (-.94,-.32,5.65)
        handrot=Q(-5*g,y=180*g,z=-20*g) if id.endswith('haut') else Q(-85*g,z=side*34*g)
        place('CTRL_main.'+tag,mix((side*.885,-.17,2.95),target,g),handrot);place('CTRL_coude.'+tag,mix((side*.8,1.4,3.7),(side*1.4,.15,3.8),g))
        rot('CTRL_tete',y=side*5*g,z=-side*6*g);rig['regard_horizontal']=.015+side*.018*g;rig['regard_vertical']=.005+(.02 if id.endswith('haut') else .005)*g;rig['sourire']=.35+.3*g
    elif id=='reflechir':
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-.15,-.65,4.72),g),Q(-10*g,y=190*g,z=-15*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.25,.5,4.1),g));rig['doigts_G']=.65*g;rig['pouce_G']=.35*g;rig['index_G']=1-g
        rot('CTRL_tete',y=-6*g,z=4*g);rig['curieux']=.7*g;rig['regard_horizontal']=.015-.022*g+.009*math.sin(u*math.tau*2)*g
    elif id=='decouvrir':
        look=ease(u/.32)*(1-ease((u-.64)/.3));rot('CTRL_tete',x=-5*look,y=-7*look,z=3*look);rig['regard_horizontal']=.015-.025*look;rig['regard_vertical']=.005+.026*look;rig['curieux']=.85*look;rig['sourire']=.35+.5*g
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-1.12,-.48,4.36),g),Q(-85*g,z=-30*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.35,.4,3.8),g))
        pop=ease((u-.17)/.12)*(1-ease((u-.72)/.16));bulb.location=(-1.38,-.45,6.2);bulb.scale=(pop,)*3
    elif id=='examiner-loupe':
        sweep=math.sin((u-.2)*math.pi*1.5);target=(-.95+.18*sweep,-.75,4.15+.1*math.cos(u*math.tau));hand=mix((-.885,-.17,2.95),target,g)
        place('CTRL_main.G',hand,Q(-12*g,z=-10*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.45,.4,3.75),g));rig['doigts_G']=.85*g;rig['pouce_G']=.7*g;rig['curieux']=.5*g
        rot('CTRL_tete',y=-5*g,z=3*g);rig['regard_horizontal']=.015-.025*g;rig['regard_vertical']=.005-.012*g
        magnifier.location=hand+Vector((0,-.13,-.34));magnifier.scale=(g,)*3;magnifier.rotation_euler=(0,.12*sweep*g,.08*sweep*g)
    elif id=='bravo':
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-.95,-.48,4.3),g),Q(y=180*g,z=-12*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.4,.4,3.8),g));rig['doigts_G']=.95*g;rig['pouce_G']=0
        rot('CTRL_tete',x=5*math.sin(u*math.tau*2)*g);rig['sourire']=.35+.6*g
    elif id=='encourager':
        surprise=ease(u/.13)*(1-ease((u-.23)/.16));comfort=ease((u-.24)/.2)*(1-ease((u-.73)/.27));rig['curieux']=.8*surprise+.2*comfort;rig['sourire']=.35+.35*comfort
        rot('CTRL_tete',x=-3*surprise+3*math.sin(u*math.tau*2)*comfort,y=-4*comfort)
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-1.0,-.45,4.02),comfort),Q(-75*comfort,z=-25*comfort));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.3,.4,3.7),comfort))
    elif id=='ecouter':
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-.42,-.12,5.30),g),Q(-5*g,y=200*g,z=-10*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.5,.4,4.1),g));rot('CTRL_tete',y=-5*g,z=-3*g);rig['curieux']=.35*g
    elif id=='a-toi':
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-.65,-.95,4.02),g),Q(-85*g,z=-15*g));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.2,.4,3.7),g));rot('CTRL_tete',x=3*math.sin(u*math.pi*2)*g);rig['sourire']=.35+.3*g
    elif id=='saluer':
        wave=math.sin(u*math.tau*3)*g
        place('CTRL_main.G',mix((-.885,-.17,2.95),(-1.1,-.25,5.15),g),Q(-5*g,y=180*g,z=-25*g+12*wave));place('CTRL_coude.G',mix((-.8,1.4,3.7),(-1.4,.5,4.1),g));rig['sourire']=.35+.4*g
    elif id in ['retrait','reapparaitre']:
        k=ease(u if id=='retrait' else 1-u);place('CTRL_corps',(0,.02,2.75-.26*k),Q(5*k));rot('CTRL_cou',-5*k);rig['clignement']=.25*k
        for tag,side in [('G',-1),('D',1)]:place('CTRL_main.'+tag,(side*(.885-.12*k),-.17-.09*k,2.95+.08*k));rot('CTRL_oreille.'+tag,-8*k)
    elif id=='regarder-haut':rot('CTRL_tete',x=-7*g,y=-4*g);rig['regard_vertical']=.005+.028*g;rig['curieux']=.35*g
    # Gentle, brief blinks; no blink on a neutral join.
    if id not in ['retrait','reapparaitre']:
        centers=[int(n*.29),int(n*.76)] if n>=90 else []
        rig['clignement']=max([0]+[max(0,1-abs(frame-c)/2.5) for c in centers])
    bpy.context.view_layer.update()

metrics={'max_ik_error':0,'clips':[]};mods=[m for o in s.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
for c in clips:
    rig.animation_data.action=None
    for p in props:p.animation_data_clear()
    for f in range(1,c['frames']+1):
        s.frame_set(f);frame_pose(c,f)
        for pb in ctrls:
            for data in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data,frame=f)
        for k in propkeys:rig.keyframe_insert(data_path='["'+k+'"]',frame=f)
        for p in props:
            for data in ['location','rotation_euler','scale']:p.keyframe_insert(data,frame=f)
        er=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
        for tag in ['G','D']:
            for deform,goal in [('D_avant_bras.','CTRL_main.'),('D_jambe.','CTRL_pied.')]:metrics['max_ik_error']=max(metrics['max_ik_error'],(er.pose.bones[deform+tag].tail-er.pose.bones[goal+tag].head).length)
    a=rig.animation_data.action;a.name='MVT_'+c['id'];a.use_fake_user=True;c['action']=a.name;c['accessoryActions']={}
    for p in props:
        a=p.animation_data.action;a.name='ACC_'+c['id']+'_'+('ampoule' if p==bulb else 'loupe');a.use_fake_user=True;c['accessoryActions'][p.name]=a.name
    c.update(fps=30,seconds=c['frames']/30,width=768,height=768,firstFrame=1,lastFrame=c['frames'],pattern='frames/'+c['id']+'/image-%04d.png',direction='droite',rootMotion=False)
    if c['id']=='marche':c['rootTravelPerCycle']=1.08;c['cycleFrames']=36;c['screenTravelPerCyclePixelsAtNativeScale']=None
    print('ACTION_BUILT',c['id'],c['frames'],flush=True)
for m in mods:m.show_viewport=True

cam=bpy.data.objects.get('Bibliothèque · caméra fixe')
if not cam:
    d=bpy.data.cameras.new('Bibliothèque · caméra fixe');cam=bpy.data.objects.new(d.name,d);s.collection.objects.link(cam)
cam.location=(-11,-17,7);cam.rotation_euler=(Vector((-.1,0,3.15))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.6;s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.07;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=1
s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=35;s.render.use_sequencer=False;s.render.use_compositing=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=6
anchor=world_to_camera_view(s,cam,Vector((0,.03,0)));p1=world_to_camera_view(s,cam,Vector((0,0,0)));p2=world_to_camera_view(s,cam,Vector((0,-1.08,0)))
travel=[(p2.x-p1.x)*768,-(p2.y-p1.y)*768]
for c in clips:
    c['anchorPx']=[anchor.x*768,(1-anchor.y)*768]
    if c['id']=='marche':c['screenTravelPerCyclePixelsAtNativeScale']=travel
manifest={'version':2,'status':'Bibliothèque de test Blender, à évaluer dans la composition finale','blenderFile':'D:/ai-generation-video/blender/renard-bibliotheque-v2.blend','fps':30,'canvas':[768,768],'alpha':True,'camera':cam.name,'anchorPx':[anchor.x*768,(1-anchor.y)*768],'defaultDirection':'droite','sourceFrameIndex':'1-based files, 0-based integration: file index = localFrame + 1','clips':clips,'accessories':{'ampoule':{'clip':'decouvrir','pattern':'accessoires/ampoule/image-%04d.png'},'loupe':{'clip':'examiner-loupe','pattern':'accessoires/loupe/image-%04d.png'}},'mirrorRule':'Both character and accessory must be mirrored about the same full canvas. Anchor x becomes 768-anchorX.'}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8');(O/'verification-construction.json').write_text(json.dumps(metrics,indent=2),encoding='utf8')
rig.animation_data.action=bpy.data.actions['MVT_attente']
for p in props:p.animation_data.action=bpy.data.actions['ACC_attente_'+('ampoule' if p==bulb else 'loupe')]
s.frame_start=1;s.frame_end=120;s.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='VERTEX';sp.overlay.show_overlays=False
            if sp.region_3d:sp.region_3d.view_perspective='CAMERA'
s['bibliotheque']='21 actions, 30 i/s, caméra fixe, trajectoire séparée, accessoires indépendants';s['statut']='Test pour intégration option 1 ; aucune validation esthétique implicite'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/renard-bibliotheque-v2.blend'));print('LIBRARY_SAVED',len(clips),'IK_MAX',metrics['max_ik_error'],flush=True)
