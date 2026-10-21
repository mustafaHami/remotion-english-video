import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';man=json.loads((O/'manifest.json').read_text(encoding='utf8'));s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];props=[bpy.data.objects[n] for n in ['ACCESSOIRE · Ampoule','ACCESSOIRE · Loupe']]
for o in s.objects:
    if o.type=='MESH':
        for m in o.modifiers:
            if m.type=='ARMATURE':m.show_viewport=False
report={'clips':[],'joins':[],'drivers':len(rig.animation_data.drivers),'root_location':list(bpy.data.objects['TRAJECTOIRE · déplacement indépendant'].location)};poses={}
def sample():return {p.name:(p.matrix.copy(),p.location.copy(),p.rotation_quaternion.copy()) for p in rig.pose.bones if p.name.startswith('CTRL_')}
for c in man['clips']:
    rig.animation_data.action=bpy.data.actions[c['action']]
    for p in props:p.animation_data.action=bpy.data.actions[c['accessoryActions'][p.name]]
    mx=(0,0,'');mins=100
    for f in range(1,c['frames']+1):
        s.frame_set(f);bpy.context.view_layer.update()
        for tag in ['G','D']:
            for deform,goal in [('D_avant_bras.','CTRL_main.'),('D_jambe.','CTRL_pied.')]:
                er=(rig.pose.bones[deform+tag].tail-rig.pose.bones[goal+tag].head).length
                if er>mx[0]:mx=(er,f,deform+tag)
        if f in [1,c['frames']]:poses[(c['id'],f==1)]=sample()
    report['clips'].append({'id':c['id'],'frames':c['frames'],'max_ik_error':mx[0],'worst_frame':mx[1],'worst_bone':mx[2]})
    print('IK',c['id'],mx,flush=True)
    if c['loop']:
        if c['id']=='marche':
            # The next virtual frame is evaluated separately by the generator test.
            pass
        else:pass
for a,b in [('arreter-marche','se-lever'),('se-lever','presenter-gauche'),('presenter-gauche','attente'),('attente','se-baisser'),('se-baisser','demarrer-marche'),('retrait','reapparaitre')]:
    p=poses[(a,False)];q=poses[(b,True)];mx=max((p[n][0].translation-q[n][0].translation).length for n in p);angle=max(math.degrees(p[n][2].rotation_difference(q[n][2]).angle) for n in p)
    report['joins'].append({'from':a,'to':b,'max_control_position_delta':mx,'max_rotation_delta_degrees':angle})
report['max_ik_error']=max(x['max_ik_error'] for x in report['clips']);(O/'verification-rig.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('QA_RIG_DONE',flush=True)
