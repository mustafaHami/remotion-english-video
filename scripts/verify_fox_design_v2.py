import bpy,json,hashlib,bmesh
from collections import Counter
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v2';s=bpy.context.scene
report={'opened_file':bpy.data.filepath,'blender':bpy.app.version_string,'saved_settings':{'resolution':[s.render.resolution_x,s.render.resolution_y],'fps':s.render.fps,'transparent':s.render.film_transparent,'format':s.render.image_settings.file_format,'channels':s.render.image_settings.color_mode,'active_camera':s.camera.name,'output_path':s.render.filepath},'armatures':len([o for o in s.objects if o.type=='ARMATURE']),'actions':list(bpy.data.actions.keys()),'packed_images':[i.name for i in bpy.data.images if i.packed_file],'source_sha256':hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest(),'meshes':{}}
for name in ['Renard · corps continu et mains','Renard · tête et museau sculptés','Queue · longue silhouette']:
    o=bpy.data.objects.get(name);me=o.data;parent=list(range(len(me.vertices)))
    def root(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    for e in me.edges:
        a,b=e.vertices;parent[root(a)]=root(b)
    counts=Counter(root(i) for i in range(len(parent)));bm=bmesh.new();bm.from_mesh(me)
    report['meshes'][name]={'vertices':len(me.vertices),'connected_components':len(counts),'component_sizes':sorted(counts.values(),reverse=True)[:10],'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-9 for f in bm.faces)};bm.free()
(OUT/'verification-reouverture.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
s.render.resolution_x=512;s.render.resolution_y=624;s.cycles.samples=24;s.render.filepath=str(OUT/'renard-v2-verification-reouverture.png');bpy.ops.render.render(write_still=True)
print('AUDIT_COMPLETE',json.dumps(report,ensure_ascii=False))
