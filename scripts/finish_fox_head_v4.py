import bpy
from mathutils import Vector
if bpy.context.scene.get('eye_contour_revision')!='integrated-v4':
    for o in list(bpy.data.objects):
        if o.name.startswith('V4 · Paupières intégrées '):bpy.data.objects.remove(o,do_unlink=True)
        elif o.name.startswith('V4 · Œil continu ') or o.name.startswith('V4 · Ligne fine paupière '):
            side=int(o.name.split(' ')[-1]);delta=Vector((side*.26,-.966,.025)).normalized()*-.005
            if o.type=='MESH':
                for v in o.data.vertices:v.co+=delta
            else:
                for spline in o.data.splines:
                    for p in spline.bezier_points:p.co+=delta;p.handle_left+=delta;p.handle_right+=delta
    bpy.context.scene['eye_contour_revision']='integrated-v4'
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v4';scene=bpy.context.scene
scene['retouches']='Crâne compact et moins bombé ; museau raccourci ; yeux encastrés et raccords d’orbites refermés ; bordures anthracite élargies'
scene['statut']='ÉTUDE TÊTE V4 — non validée'
normal_report={}
for o in list(bpy.data.objects):
    if not (o.name.startswith('V4 · Œil continu ') or o.name.startswith('V4 · Paupières intégrées ')):continue
    s=int(o.name.split(' ')[-1]);n=Vector((s*.26,-.966,.025)).normalized();bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();bad=[f for f in bm.faces if f.normal.dot(n)<0]
    if bad:bmesh.ops.reverse_faces(bm,faces=bad)
    bm.normal_update();normal_report[o.name]={'faces_corrected':len(bad),'faces':len(bm.faces),'faces_still_reversed':sum(f.normal.dot(n)<0 for f in bm.faces),'zero_area':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.to_mesh(o.data);bm.free()
scene.camera=bpy.data.objects['V4 · tête trois quarts'];scene.render.resolution_x=1000;scene.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-etude-tete-v4.blend'))
scene.render.resolution_x=1000;scene.render.resolution_y=1000
for name,cam in [('trois-quarts','V4 · tête trois quarts'),('face','V4 · tête face'),('profil','V4 · tête profil')]:
    # Render every definitive angle after the integrated-eyelid correction.
    scene.camera=bpy.data.objects[cam];scene.render.filepath=str(OUT/('renard-v4-tete-'+name+'.png'));bpy.ops.render.render(write_still=True)
# Preserve the requested working file with a stable full-character portrait camera.
data=bpy.data.cameras.new('V4 · contexte plein pied');full=bpy.data.objects.new('V4 · contexte plein pied',data);bpy.data.collections['04 — Studio · cameras et lumières'].objects.link(full);full.location=(-17,-12,5.0);target=Vector((-.65,.10,3.25));full.rotation_euler=(target-full.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=7.4
scene.camera=full;scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.render.filepath=str(OUT/'renard-v4-');bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'))
scene.render.resolution_x=540;scene.render.resolution_y=960;scene.cycles.samples=24;scene.render.filepath=str(OUT/'renard-v4-contexte.png');bpy.ops.render.render(write_still=True)
report={'blender':bpy.app.version_string,'status':'étude de tête V4, apparence non validée','eye_normals':normal_report,'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest(),'rig':False,'actions':list(bpy.data.actions.keys())}
(OUT/'verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('V4_FINISHED',json.dumps(report,ensure_ascii=False))
