import bpy,bmesh,json,hashlib
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v3';s=bpy.context.scene
report={'blender':bpy.app.version_string,'study_path':bpy.data.filepath,'study_settings':{'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'camera':s.camera.name,'rgba':s.render.image_settings.color_mode,'transparent':s.render.film_transparent},'meshes':{},'actions':list(bpy.data.actions.keys()),'armatures':sum(o.type=='ARMATURE' for o in bpy.data.objects),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest()}
for name in ['Renard · tête et museau sculptés','Renard · corps continu et mains','V3 · Oreille G','V3 · Oreille D']:
    o=bpy.data.objects.get(name);bm=bmesh.new();bm.from_mesh(o.data);report['meshes'][name]={'vertices':len(bm.verts),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-10 for f in bm.faces)};bm.free()
s.render.resolution_x=512;s.render.resolution_y=512;s.cycles.samples=24;s.render.filepath=str(OUT/'renard-v3-verification-reouverture.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));s=bpy.context.scene
report['main_settings']={'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'camera':s.camera.name,'rgba':s.render.image_settings.color_mode,'transparent':s.render.film_transparent}
(OUT/'verification-reouverture.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('V3_REOPEN_OK',json.dumps(report,ensure_ascii=False))
