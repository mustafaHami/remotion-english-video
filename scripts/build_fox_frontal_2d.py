"""Faithful image-based 2D puppets in Blender, with real deforming meshes and bones."""
import bpy,math,json,time,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
R=Path('D:/ai-generation-video');O=R/'output/blender/renard-frontal-2d';O.mkdir(parents=True,exist_ok=True)
SOURCE=R/'assets/branding/renard-frontal-reference-2026-10-19.png';W,H=1774,887;S=.01
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection' and c.users==0:bpy.data.collections.remove(c)
s=bpy.context.scene;s.name='Renard frontal · dessin 2D articulé';base=bpy.data.collections.get('Collection');base.name='00 · Caméras et référence'
def coll(n):c=bpy.data.collections.new(n);s.collection.children.link(c);return c
def point(x,y,depth=0):return Vector((x*S,depth,(H-y)*S))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def inside(x,y,poly):
    ok=False;j=len(poly)-1
    for i in range(len(poly)):
        ax,ay=poly[i];bx,by=poly[j]
        if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:ok=not ok
        j=i
    return ok
image=bpy.data.images.load(str(SOURCE),check_existing=True);image.name='RÉFÉRENCE ORIGINALE · deux poses frontales';image.alpha_mode='STRAIGHT';image.colorspace_settings.name='sRGB';image.pack()
mat=bpy.data.materials.new('Dessin original · couleurs et transparence conservées');mat.use_nodes=True;mat.diffuse_color=(1,1,1,1)
nt=mat.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';tex.extension='CLIP';tex.label='Image utilisateur, non redessinée';nt.nodes.active=tex
uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='Pixels de la référence';nt.links.new(uv.outputs['UV'],tex.inputs['Vector'])
em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;nt.links.new(tex.outputs['Color'],em.inputs['Color'])
tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(tex.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
if hasattr(mat,'surface_render_method'):mat.surface_render_method='BLENDED'
if hasattr(mat,'use_transparent_shadow'):mat.use_transparent_shadow=False
mat.use_backface_culling=False
headpoly=[(498,203),(500,174),(525,128),(526,58),(542,7),(568,35),(598,76),(628,76),(657,37),(685,7),(705,39),(709,111),(722,151),(738,177),(723,176),(739,202),(703,205),(676,227),(640,240),(603,240),(565,224),(542,205)]
tailpoly=[(552,521),(510,540),(446,575),(389,607),(338,644),(304,683),(289,725),(286,771),(299,797),(333,774),(388,758),(441,730),(492,695),(548,650),(554,591)]
armpoly=[(550,269),(570,301),(546,385),(523,469),(506,534),(518,580),(521,604),(503,626),(483,617),(467,592),(462,556),(471,508),(474,443),(495,352),(518,293)]
reports=[];rigs=[]
def create_puppet(label,offset,half,cheer=False):
    c=coll(label);ad=bpy.data.armatures.new(label+' · squelette');rig=bpy.data.objects.new(label+' · RIG',ad);c.objects.link(rig);rig.show_in_front=True;ad.display_type='STICK';bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    bones={}
    def bone(n,a,b,parent=None):
        e=ad.edit_bones.new(n);e.head=point(a[0]+offset,a[1]);e.tail=point(b[0]+offset,b[1]);e.use_deform=True
        if parent:e.parent=ad.edit_bones[parent]
        bones[n]=(a,b)
    bone('GLOBAL',(620,872),(620,820));bone('Corps · respiration',(620,565),(620,300),'GLOBAL');bone('Tête · inclinaison',(620,239),(620,100),'Corps · respiration')
    for side,px in [('G',555),('D',682)]:bone('Oreille.'+side,(px,98),(px,22),'Tête · inclinaison')
    eyecentres=[(583,141),(655,141)] if not cheer else [(587,143),(656,143)]
    for side,(x,y) in zip(['G','D'],eyecentres):bone('Œil · clignement.'+side,(x,y),(x,y-12),'Tête · inclinaison')
    elbow=(785,350) if not cheer else (781,360);wrist=(794,274) if not cheer else (783,309)
    bone('Bras levé',(694,294),elbow,'Corps · respiration');bone('Avant-bras levé · geste',elbow,wrist,'Bras levé');bone('Main levée',wrist,(wrist[0],wrist[1]-65),'Avant-bras levé · geste')
    bone('Bras bas',(552,292),(502,455),'Corps · respiration');bone('Avant-bras bas',(502,455),(490,552),'Bras bas');bone('Main basse',(490,552),(495,610),'Avant-bras bas')
    bone('Queue · base',(552,620),(425,710),'Corps · respiration');bone('Queue · pointe',(425,710),(303,777),'Queue · base');bone('Foulard',(578,282),(589,440),'Corps · respiration')
    for side,hip,knee,ankle,foot in [('G',(580,576),(566,726),(548,845),(520,862)),('D',(663,576),(670,726),(686,845),(726,863))]:
        bone('Cuisse.'+side,hip,knee,'GLOBAL');bone('Jambe.'+side,knee,ankle,'Cuisse.'+side);bone('Pied.'+side,ankle,foot,'Jambe.'+side)
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    # A dense continuous plane retains the exact source UVs and bends at the joints.
    xs=sorted(set(list(range(half[0],half[1]+1,4))+[half[1]]+list(range(offset+550,offset+691,2))));ys=sorted(set(list(range(0,H+1,4))+[H]+list(range(110,172,2))))
    verts=[tuple(point(x,y)) for y in ys for x in xs];nx=len(xs);faces=[]
    for j in range(len(ys)-1):
        for i in range(nx-1):a=j*nx+i;faces.append((a,a+nx,a+nx+1,a+1))
    me=bpy.data.meshes.new(label+' · maillage 2D déformable');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(label+' · dessin articulé',me);c.objects.link(ob);me.materials.append(mat)
    uv=me.uv_layers.new(name='Pixels de la référence')
    for loop in me.loops:
        v=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(v.x/(W*S),v.z/(H*S))
    groups={n:ob.vertex_groups.new(name=n) for n in bones};buckets={}
    def replace(w,n,f):
        f=max(0,min(1,f));z={k:v*(1-f) for k,v in w.items()};z[n]=z.get(n,0)+f;return z
    for j,y in enumerate(ys):
        for i,gx in enumerate(xs):
            x=gx-offset;idx=j*nx+i;body=ease((y-200)/70)*(1-ease((y-595)/110));w={'GLOBAL':1-body,'Corps · respiration':body}
            if 535<x<710 and y>565:
                side='G' if x<620 else 'D';k=ease((y-580)/55);w=replace(w,'Cuisse.'+side,k)
                if y>692:w=replace(w,'Jambe.'+side,ease((y-692)/68))
                if y>826:w=replace(w,'Pied.'+side,ease((y-826)/30))
            if inside(x,y,tailpoly):
                f=1-ease((x-515)/42);w=replace(w,'Queue · base',f)
                if x<430:w=replace(w,'Queue · pointe',(1-ease((x-365)/65))*f)
            if inside(x,y,armpoly):
                w=replace(w,'Bras bas',1)
                if y>430:w=replace(w,'Avant-bras bas',ease((y-430)/50))
                if y>539:w=replace(w,'Main basse',ease((y-539)/30))
            # Raised-arm weighting stops at the elbow, and never drags the face.
            if x>686 and 145<y<432:
                arm=ease((x-686)/42)*(1-ease((y-399)/33));w=replace(w,'Bras levé',arm)
                fore=arm*ease((x-733)/25)*(1-ease((y-347)/43));w=replace(w,'Avant-bras levé · geste',fore)
                wrist_y=274 if not cheer else 309;hand=fore*(1-ease((y-(wrist_y-6))/30));w=replace(w,'Main levée',hand)
            if 495<x<742 and y<250:
                f=1-ease((y-213)/35);w=replace(w,'Tête · inclinaison',f)
                for side,px in [('G',555),('D',682)]:
                    if abs(x-px)<63 and y<105:w=replace(w,'Oreille.'+side,(1-ease((y-64)/39))*f)
                for side,(cx,cy) in zip(['G','D'],eyecentres):
                    r=math.hypot((x-cx)/19,(y-cy)/16);fac=1-ease((r-1)/.42)
                    if fac>0:w=replace(w,'Œil · clignement.'+side,fac*f)
            if 551<x<619 and 283<y<462:w=replace(w,'Foulard',ease((y-289)/62)*(1-ease((x-607)/12)))
            vals={n:round(v*128) for n,v in w.items() if v>.001};total=sum(vals.values())
            for n,v in vals.items():
                if v:buckets.setdefault((n,round(v/total,6)),[]).append(idx)
    for (n,w),ids in buckets.items():groups[n].add(ids,w,'REPLACE')
    mod=ob.modifiers.new('Articulation 2D · maillage continu','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=False;ob.parent=rig
    for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
    def angle(n,degrees):
        pb=rig.pose.bones[n];axis=ad.bones[n].matrix_local.to_quaternion().inverted()@Vector((0,1,0));pb.rotation_quaternion=Quaternion(axis,math.radians(degrees))
    for f in range(1,181):
        u=(f-1)/179
        for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_quaternion=(1,0,0,0);pb.scale=(1,1,1)
        rig.pose.bones['Corps · respiration'].location=ad.bones['Corps · respiration'].matrix_local.to_quaternion().inverted()@Vector((0,0,.009*(1-math.cos(math.tau*u))))
        angle('Queue · base',1.8*math.sin(math.tau*u));angle('Queue · pointe',.6*math.sin(math.tau*u));angle('Tête · inclinaison',.65*math.sin(math.tau*u))
        for side in ['G','D']:angle('Oreille.'+side,.6*math.sin(math.tau*u))
        if not cheer:
            env=ease((f-5)/12)*(1-ease((f-87)/16));wave=5.5*math.sin(math.tau*(f-1)/34)*env;angle('Avant-bras levé · geste',wave);angle('Main levée',wave*.23)
        else:
            env=ease((f-65)/14)*(1-ease((f-137)/18));angle('Tête · inclinaison',2*math.sin(math.tau*(f-65)/38)*env);angle('Avant-bras levé · geste',1.8*math.sin(math.tau*(f-65)/50)*env)
        blink=max(0,1-abs(f-(47 if not cheer else 113))/3)
        for side in ['G','D']:rig.pose.bones['Œil · clignement.'+side].scale.y=1-.94*blink
        for pb in rig.pose.bones:
            for attr in ['location','rotation_quaternion','scale']:pb.keyframe_insert(attr,frame=f)
    action=rig.animation_data.action;action.name='2D · '+('Salut et clignement' if not cheer else 'Approbation et clignement');action.use_fake_user=True
    rigs.append(rig);reports.append({'pose':label,'rig':rig.name,'mesh':ob.name,'bones':len(ad.bones),'vertices':len(me.vertices),'faces':len(me.polygons),'action':action.name,'half':half,'missingWeights':sum(not v.groups for v in me.vertices)})
    print('PUPPET_BUILT',label,len(me.vertices),flush=True)
create_puppet('01 · Salut',0,(0,887));create_puppet('02 · Pouce levé',620,(887,1774),True)
def camera(name,centre,w,h):
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);base.objects.link(ob);ob.location=point(centre[0],centre[1],-20);target=point(centre[0],centre[1]);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=max(w,h)*S;d.lens=50;return ob
cam=camera('CAM · Les deux poses · référence exacte',(W/2,H/2),W,H);camera('CAM · Salut seul',(443.5,H/2),887,H);camera('CAM · Pouce levé seul',(1330.5,H/2),887,H);s.camera=cam
reference=bpy.data.objects.new('RÉFÉRENCE · image originale non modifiée',None);base.objects.link(reference);reference.empty_display_type='IMAGE';reference.data=image;reference.empty_display_size=17.74;reference.hide_render=True;reference.hide_set(True)
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=35;s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_persistent_data=True;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=32
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1;s.frame_start=1;s.frame_end=180;s.frame_set(1)
for n,f in [('Référence exacte · pose neutre',1),('Salut',20),('Clignement gauche',47),('Approbation',90),('Clignement droit',113),('Retour référence',180)]:s.timeline_markers.new(n,frame=f)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='MATERIAL';sp.overlay.show_overlays=False
            if sp.region_3d:sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_camera_zoom=0;sp.region_3d.view_camera_offset=(0,0)
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=rigs[0];rigs[0].select_set(True)
s['méthode']='Dessin 2D articulé : texture originale, UV inchangés, maillages continus et armatures. Pas un modèle 3D volumétrique.';s['source']=str(SOURCE);s['utilisation']='Espace : lire 6 secondes. Image 1 : référence. Activer les superpositions pour voir les os.'
t=bpy.data.texts.new('LIRE MOI · renard frontal 2D');t.write(s['méthode']+'\n\n'+s['utilisation']+'\nDeux rig indépendants, caméras séparées, texture incorporée. Les actions restent modifiables. Aucun fichier Remotion modifié.')
path=R/'blender/renard-frontal-2d-articule.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
report={'source':str(SOURCE),'sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'blenderFile':str(path),'format':'Dessin 2D articulé, pas volume 3D','resolution':[W,H],'fps':30,'frames':180,'seconds':6,'packedImage':bool(image.packed_file),'puppets':reports}
(O/'construction.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('SOURCE_SAVED',json.dumps(report,ensure_ascii=False),flush=True)
s.render.filepath=str(O/'renard-frontal-reference.png');bpy.ops.render.render(write_still=True);print('REFERENCE_RENDERED',flush=True)
s.render.filepath=str(O/'frames/image-');(O/'frames').mkdir(exist_ok=True);bpy.ops.render.render(animation=True);print('ANIMATION_RENDERED',flush=True)
