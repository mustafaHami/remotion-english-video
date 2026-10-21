import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v3';scene=bpy.context.scene
normal_report={}
for o in list(bpy.data.objects):
    if not (o.name.startswith('V3 · Œil continu ') or o.name.startswith('V3 · Paupières intégrées ')):continue
    s=int(o.name.split(' ')[-1]);n=Vector((s*.26,-.966,.025)).normalized();bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();bad=[f for f in bm.faces if f.normal.dot(n)<0]
    if bad:bmesh.ops.reverse_faces(bm,faces=bad)
    bm.normal_update();normal_report[o.name]={'faces_corrected':len(bad),'faces':len(bm.faces),'faces_still_reversed':sum(f.normal.dot(n)<0 for f in bm.faces),'zero_area':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.to_mesh(o.data);bm.free()
scene.camera=bpy.data.objects['V3 · tête trois quarts'];scene.render.resolution_x=1000;scene.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-etude-tete-v3.blend'))
scene.render.resolution_x=1000;scene.render.resolution_y=1000
for name,cam in [('trois-quarts','V3 · tête trois quarts'),('face','V3 · tête face'),('profil','V3 · tête profil')]:
    if name=='trois-quarts' and not any(v['faces_corrected'] for v in normal_report.values()):continue
    scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/('renard-v3-tete-'+name+'.png'));bpy.ops.render.render(write_still=True)
# Preserve the requested working file with a stable full-character portrait camera.
data=bpy.data.cameras.new('V3 · contexte plein pied');full=bpy.data.objects.new('V3 · contexte plein pied',data);bpy.data.collections['04 — Studio · cameras et lumières'].objects.link(full);full.location=(-17,-12,5.0);target=Vector((-.65,.10,3.25));full.rotation_euler=(target-full.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=7.4
scene.camera=full;scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.render.filepath=str(OUT/'renard-v3-');bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'))
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.cycles.samples=24;scene.render.filepath=str(OUT/'renard-v3-contexte.png');bpy.ops.render.render(write_still=True)
report={'blender':bpy.app.version_string,'status':'étude de tête V3, apparence non validée','eye_normals':normal_report,'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest(),'rig':False,'actions':list(bpy.data.actions.keys())}
(OUT/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('V3_FINISHED',json.dumps(report,ensure_ascii=False))
