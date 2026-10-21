import bpy,sys,time,json,math
from pathlib import Path
root=Path('D:/ai-generation-video/output/englizy/3d')
s=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.render.use_persistent_data=True
# Prefer an available GPU, while retaining CPU compatibility.
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    for device_type in ['OPTIX','CUDA']:
        try:
            prefs.compute_device_type=device_type;prefs.get_devices()
            gpu=[d for d in prefs.devices if d.type!='CPU']
            if gpu:
                for d in prefs.devices:d.use=d.type!='CPU'
                s.cycles.device='GPU';print('GPU',device_type,[d.name for d in gpu],flush=True);break
        except Exception:pass
except Exception:pass
(root/'frames').mkdir(exist_ok=True)
s.render.filepath=str(root/'frames'/'frame-')
s.frame_start=int(args[0]) if args else 1;s.frame_end=int(args[1]) if len(args)>1 else 180

from bpy_extras.object_utils import world_to_camera_view
render_meshes=[o for o in s.objects if o.type=='MESH']
bounds=[1,1,0,0]
for frame in range(1,182):
    s.frame_set(frame)
    for o in render_meshes:
        for corner in o.bound_box:
            p=world_to_camera_view(s,s.camera,o.matrix_world @ __import__('mathutils').Vector(corner))
            bounds=[min(bounds[0],p.x),min(bounds[1],p.y),max(bounds[2],p.x),max(bounds[3],p.y)]
s.frame_set(1);start={o.name:list(o.matrix_world) for o in render_meshes}
s.frame_set(181);loop_error=max(abs(a-b) for o in render_meshes for row1,row2 in zip(start[o.name],o.matrix_world) for a,b in zip(row1,row2))
(root/'scene-qa.json').write_text(json.dumps({'objects':len(render_meshes),'all_frame_screen_bounds':bounds,'seamless_loop_matrix_error':loop_error,'frame_count':180,'fps':30,'duration_seconds':6,'resolution':[900,900]},indent=2))
print('SCENE_QA',bounds,loop_error,flush=True)

print('ANIMATION_START',s.frame_start,s.frame_end,flush=True)
bpy.ops.render.render(animation=True)
print('ANIMATION_COMPLETE',flush=True)
