import bpy,json,math,ast
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];ad=rig.data;route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];man=json.loads((O/'manifest.json').read_text(encoding='utf8'));body=bpy.data.objects['Renard · corps continu et mains'];props=[bpy.data.objects[n] for n in ['ACCESSOIRE · Ampoule','ACCESSOIRE · Loupe']];bulb,magnifier=props
ctrls=[p for p in rig.pose.bones if p.name.startswith('CTRL_') or p.name.startswith('D_oreille_pointe')];propkeys=['clignement','sourire','curieux','regard_horizontal','regard_vertical','doigts_G','doigts_D','pouce_G','pouce_D','index_G','index_D']
tree=ast.parse((R/'scripts/build_fox_motion_library_v2.py').read_text(encoding='utf8'));defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['ease','lerp','mix','Q','place','rot','gesture','reset','pose_base','frame_pose']];exec(compile(ast.Module(body=defs,type_ignores=[]),'<motion functions>','exec'))
def snapshot():return {p.name:p.matrix.copy() for p in ctrls}
report={'loops':[],'stanceControlMotion':None,'meshGroundSamples':[],'clothMinimumZ':[]}
for c in man['clips']:
    if not c['loop']:continue
    rig.animation_data.action=None
    frame_pose(c,1);a=snapshot();frame_pose(c,c['frames']+1);b=snapshot();dp=max((a[n].translation-b[n].translation).length for n in a);dr=max(math.degrees(a[n].to_quaternion().rotation_difference(b[n].to_quaternion()).angle) for n in a)
    report['loops'].append({'id':c['id'],'virtualNextFramePositionError':dp,'virtualNextFrameAngleErrorDegrees':dr});assert dp<.00001 and dr<.1,(c['id'],dp,dr)
# Rigid-contact controls in a constant-speed cycle must stay still in world space.
c=next(c for c in man['clips'] if c['id']=='marche');rig.animation_data.action=bpy.data.actions[c['action']];prev={};mx=0
phases={('main','G'):.25,('pied','G'):0,('main','D'):.75,('pied','D'):.5}
for f in range(1,37):
    s.frame_set(f)
    for kind,tag in phases:
        ph=((f-1)/36+phases[kind,tag])%1;stance=ph<.64;world=rig.pose.bones['CTRL_'+kind+'.'+tag].head+Vector((0,-1.08*(f-1)/36,0));key=(kind,tag)
        if stance and key in prev and prev[key][0]:mx=max(mx,(world-prev[key][1]).length)
        prev[key]=(stance,world.copy())
report['stanceControlMotion']=mx;assert mx<.00001,mx
for mod in body.modifiers:
    if mod.type=='SUBSURF':mod.show_viewport=False
groups={('main',tag):[v.index for v in body.data.vertices if (v.co.x<0)==(tag=='G') and abs(v.co.x)>.67 and v.co.z<2.8] for tag in ['G','D']}
for tag in ['G','D']:groups['pied',tag]=[v.index for v in body.data.vertices if (v.co.x<0)==(tag=='G') and v.co.z<.25]
for f in [1,10,19,28]:
    s.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dg);me=ev.to_mesh()
    for key,ids in groups.items():
        z=min((ev.matrix_world@me.vertices[i].co).z for i in ids);report['meshGroundSamples'].append({'frame':f,'member':key,'minZ':z})
    ev.to_mesh_clear()
    for ob in bpy.data.collections['03 — Foulard'].objects:
        if ob.type!='MESH' or ob.hide_render:continue
        ev=ob.evaluated_get(dg);me=ev.to_mesh();z=min((ev.matrix_world@v.co).z for v in me.vertices);report['clothMinimumZ'].append({'frame':f,'object':ob.name,'minZ':z});ev.to_mesh_clear()
(O/'verification-boucles-appuis.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('LOOPS_CONTACTS',json.dumps(report,ensure_ascii=False),flush=True)
