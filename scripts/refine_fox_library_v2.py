"""Rebake only updated actions, then evaluate joins and loops in the saved library."""
import bpy,math,json,ast,sys
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from bpy_extras.object_utils import world_to_camera_view
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];ad=rig.data;route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant']
ctrls=[p for p in rig.pose.bones if p.name.startswith('CTRL_') or p.name.startswith('D_oreille_pointe')];bulb=bpy.data.objects['ACCESSOIRE · Ampoule'];magnifier=bpy.data.objects['ACCESSOIRE · Loupe'];props=[bulb,magnifier]
propkeys=['clignement','sourire','curieux','regard_horizontal','regard_vertical','doigts_G','doigts_D','pouce_G','pouce_D','index_G','index_D']
tree=ast.parse((R/'scripts/build_fox_motion_library_v2.py').read_text(encoding='utf8'));defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['ease','lerp','mix','Q','place','rot','gesture','reset','pose_base','frame_pose']];exec(compile(ast.Module(body=defs,type_ignores=[]),'<motion functions>','exec'))
man=json.loads((O/'manifest.json').read_text(encoding='utf8'));mods=[m for o in s.objects if o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE']
for m in mods:m.show_viewport=False
for pb in rig.pose.bones:
    if not pb.name.startswith(('D_doigt','D_pouce')):continue
    tag=pb.name[-1];pb.rotation_mode='XYZ'
    try:pb.driver_remove('rotation_euler',0)
    except:pass
    d=pb.driver_add('rotation_euler',0).driver;isthumb=pb.name.startswith('D_pouce');isindex=pb.name.startswith('D_doigt0')
    d.expression='-v*.7' if isthumb else '-v*k*1.25' if isindex else '-v*1.25'
    v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["'+('pouce_' if isthumb else 'doigts_')+tag+'"]'
    if isindex:v=d.variables.new();v.name='k';v.targets[0].id=rig;v.targets[0].data_path='["index_'+tag+'"]'
selected=sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else ['attente','attente-quatre-pattes','marche','demarrer-marche','arreter-marche','se-lever','se-baisser','bravo']
for c in man['clips']:
    if c['id'] not in selected:continue
    rig.animation_data.action=bpy.data.actions[c['action']]
    for p in props:p.animation_data.action=bpy.data.actions[c['accessoryActions'][p.name]]
    for f in range(1,c['frames']+1):
        s.frame_set(f);frame_pose(c,f)
        for pb in ctrls:
            for data in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data,frame=f)
        for k in propkeys:rig.keyframe_insert(data_path='["'+k+'"]',frame=f)
    print('REFINED',c['id'],flush=True)
for m in mods:m.show_viewport=True
cam=s.camera;man['anchorPx']=[world_to_camera_view(s,cam,Vector((0,.03,0))).x*768,(1-world_to_camera_view(s,cam,Vector((0,.03,0))).y)*768]
p1=world_to_camera_view(s,cam,Vector((0,0,0)));p2=world_to_camera_view(s,cam,Vector((0,-1.08,0)));travel=[(p2.x-p1.x)*768,-(p2.y-p1.y)*768]
for c in man['clips']:
    if c['id']=='marche':c['rootTravelPerCycle']=1.08;c['screenTravelPerCyclePixelsAtNativeScale']=travel
    c['anchorPx']=man['anchorPx']
man['renderEngine']='pending';man['notes']=['Trajectoire absente des PNG : Remotion place le personnage.','Les disparitions et réapparitions demandent une animation de position/opacité dans Remotion.','Le fichier .blend contient les matériaux Cycles et toutes les actions.']
(O/'manifest.json').write_text(json.dumps(man,indent=2,ensure_ascii=False),encoding='utf8')
rig.animation_data.action=bpy.data.actions['MVT_attente']
for p in props:p.animation_data.action=bpy.data.actions['ACC_attente_'+('ampoule' if p==bulb else 'loupe')]
s.frame_start=1;s.frame_end=120;s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/renard-bibliotheque-v2.blend'));print('REFINEMENTS_SAVED',flush=True)
