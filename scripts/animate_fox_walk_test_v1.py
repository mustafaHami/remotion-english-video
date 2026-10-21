import bpy,math,json,time
from mathutils import Vector,Matrix,Quaternion
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];ad=rig.data;route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant']
rig.animation_data_clear();route.animation_data_clear();s.render.fps=30;s.frame_start=1;s.frame_end=180
mods=[m for o in bpy.data.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
ctrls=[p for p in rig.pose.bones if p.name.startswith('CTRL_')]
for p in ctrls:p.rotation_mode='QUATERNION'
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def placeQ(name,pos,q):
    p=rig.pose.bones[name];p.matrix=Matrix.Translation(Vector(pos))@q.to_matrix().to_4x4()@ad.bones[name].matrix_local.to_3x3().to_4x4()
def place(name,pos,rx=0):placeQ(name,pos,Quaternion((1,0,0),math.radians(rx)))
def progress(t):
    if t<108:return t
    if t<144:u=(t-108)/36;return 108+36*(u-u*u/2)
    return 126
T=36;speed=.012;duty=.64;half=speed*T*duty/2
phases={('main','G'):.25,('pied','G'):0,('main','D'):.75,('pied','D'):.5}
def gait(q,kind,tag):
    phase=(q/T+phases[(kind,tag)])%1
    if phase<duty:y=-half+2*half*phase/duty;z=0;swing=0
    else:u=(phase-duty)/(1-duty);y=half-2*half*ease(u);z=(.14 if kind=='main' else .18)*math.sin(math.pi*u);swing=math.sin(math.pi*u)
    return y,z,swing,phase<duty
metrics={'max_ik_error':0,'max_stance_displacement':0,'contacts':{},'frames':180,'fps':30,'duration':6}
previous={};terminal={}
for frame in range(1,181):
    s.frame_set(frame);t=frame-1;q=progress(t);phase=q/T*math.tau;walk=max(0,1-ease((t-108)/36));look=ease((t-148)/22)
    route.location=(0,-speed*q,0);route.keyframe_insert('location',frame=frame)
    place('CTRL_corps',(.018*math.sin(phase),.8,1.86+.018*math.cos(phase*2)*walk),100+.6*math.sin(phase*2)*walk)
    rig.pose.bones['CTRL_colonne'].rotation_quaternion=Quaternion((0,1,0),math.radians(1.2*math.sin(phase)*walk))
    rig.pose.bones['CTRL_poitrine'].rotation_quaternion=Quaternion((0,0,1),math.radians(.6*math.sin(phase)*walk))
    rig.pose.bones['CTRL_cou'].rotation_quaternion=Quaternion((1,0,0),math.radians(-85-.4*math.sin(phase*2)*walk))
    rig.pose.bones['CTRL_tete'].rotation_quaternion=Quaternion((1,0,0),math.radians(-8-3*look))@Quaternion((0,1,0),math.radians(-17*look))@Quaternion((0,0,1),math.radians(2*look))
    bpy.context.view_layer.update()
    for side in [-1,1]:
        tag='G' if side<0 else 'D'
        for kind in ['main','pied']:
            y,z,swing,stance=gait(q,kind,tag)
            if t>=144:
                if (kind,tag) not in terminal:terminal[(kind,tag)]=(y,z,swing)
                y,z0,sw=terminal[(kind,tag)];z=z0*(1-ease((t-144)/12));swing=sw*(1-ease((t-144)/12));stance=t>=156 or z0==0
            baseY=-1 if kind=='main' else .9;baseZ=.15 if kind=='main' else .24;baseX=.59 if kind=='main' else .42
            place('CTRL_'+kind+'.'+tag,(side*baseX,baseY+y,baseZ+z),(-65+8*swing) if kind=='main' else -5*swing)
            key=(kind,tag);world=Vector((side*baseX,baseY+y-speed*q,baseZ+z))
            if stance and previous.get(key,(False,None))[0]:metrics['max_stance_displacement']=max(metrics['max_stance_displacement'],(world-previous[key][1]).length)
            previous[key]=(stance,world)
        place('CTRL_coude.'+tag,(side*.7,.8,1.1));place('CTRL_genou.'+tag,(side*.42,-1.4,1.1))
        rig.pose.bones['CTRL_oreille.'+tag].rotation_quaternion=Quaternion((1,0,0),math.radians(2.5*math.sin(phase+.6*side)*walk+2*look*side))
        rig.pose.bones['D_oreille_pointe.'+tag].rotation_quaternion=Quaternion((1,0,0),math.radians(1.0*math.sin(phase+.8*side)*walk))
    bpy.context.view_layer.update()
    pos=rig.pose.bones['CTRL_queue_0'].matrix.translation.copy();tailQ=Vector((-2.53,.60,-2.09)).rotation_difference(Vector((-.55,3.1,-.65)));tailQ=Quaternion((0,0,1),.04*math.sin(phase-.4)*walk+.025*look)@tailQ;placeQ('CTRL_queue_0',pos,tailQ)
    for j in range(1,6):rig.pose.bones['CTRL_queue_%d'%j].rotation_quaternion=Quaternion((0,1,0),.035*math.sin(phase-j*.5)*walk+.02*math.sin(t*.1-j*.4)*(1-walk))
    pos=rig.pose.bones['CTRL_foulard'].matrix.translation.copy();place('CTRL_foulard',pos,1.2*math.sin(phase-.3)*walk);rig.pose.bones['CTRL_foulard_pointe'].rotation_quaternion=Quaternion((1,0,0),math.radians(2*math.sin(phase-.7)*walk))
    blink=max(max(0,1-abs(frame-c)/3) for c in [26,86,152]);rig['clignement']=blink;rig['sourire']=.35+.35*look;rig['curieux']=.22*look;rig['regard_horizontal']=.024-.042*look;rig['regard_vertical']=.008+.004*look
    for prop in ['clignement','sourire','curieux','regard_horizontal','regard_vertical']:rig.keyframe_insert(data_path='["'+prop+'"]',frame=frame)
    for pb in ctrls:
        pb.keyframe_insert('location',frame=frame);pb.keyframe_insert('rotation_quaternion',frame=frame);pb.keyframe_insert('scale',frame=frame)
    # Ear tips have small independent bends.
    for tag in ['G','D']:rig.pose.bones['D_oreille_pointe.'+tag].keyframe_insert('rotation_quaternion',frame=frame)
    bpy.context.view_layer.update();er=rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
    for tag in ['G','D']:
        for deform,goal in [('D_avant_bras.','CTRL_main.'),('D_jambe.','CTRL_pied.')]:metrics['max_ik_error']=max(metrics['max_ik_error'],(er.pose.bones[deform+tag].tail-er.pose.bones[goal+tag].head).length)
    if frame%30==0:print('BAKED',frame,flush=True)
walk_action=rig.animation_data.action;walk_action.name='TEST_01 · Marche quadrupède, arrêt, regard';walk_action.use_fake_user=True
route.animation_data.action.name='TRAJET_01 · Avancée indépendante';route.animation_data.action.use_fake_user=True
for m in mods:m.show_viewport=True
# Preserve reusable action and a stable portrait export preset.
studio=bpy.data.collections['04 — Studio · cameras et lumières'];d=bpy.data.cameras.new('EXPORT · portrait 1080x1920');cam=bpy.data.objects.new('EXPORT · portrait 1080x1920',d);studio.objects.link(cam);cam.location=(-12,-8,6);target=Vector((0,-.1,1.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=13.8
s.camera=cam;s.frame_set(1);s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.fps=30;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(OUT/'export/renard-')
s['statut']='EXPRESSION V5 + TEST ARTICULATION V1 — non validé';s['rig']='Poids sur corps continu, IK sans étirement, doigts, queue, oreilles, foulard, regard, clignements, sourire';s['actions']='TEST_01 : 180 images, 30 i/s, 6 secondes ; trajectoire sur objet indépendant'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-rig-v1.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'))
metrics['bones']=len(ad.bones);metrics['unweighted_body_vertices']=sum(not v.groups for v in bpy.data.objects['Renard · corps continu et mains'].data.vertices);metrics['actions']=[a.name for a in bpy.data.actions];(OUT/'verification-animation.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False),encoding='utf8');print('ANIMATION_SAVED',json.dumps(metrics),flush=True)
# Low-cost motion preview: vertex colours retain the character markings.
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='OFF';s.display.shading.show_shadows=False;s.display.shading.show_cavity=False;s.display.shading.color_type='VERTEX';s.render.resolution_x=640;s.render.resolution_y=360;s.camera=bpy.data.objects['RIG · contrôle trois quarts']
for frame in [1,20,80,150,175]:s.frame_set(frame);s.render.filepath=str(OUT/('pose-%03d.png'%frame));tm=time.monotonic();bpy.ops.render.render(write_still=True);print('POSE',frame,'SECONDS',time.monotonic()-tm,flush=True)
