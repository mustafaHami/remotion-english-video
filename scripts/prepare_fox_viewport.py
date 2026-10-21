import bpy
from mathutils import Vector
scene=bpy.context.scene
camera=scene.camera
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active
   space.shading.type='SOLID'; space.shading.color_type='MATERIAL'; space.shading.light='STUDIO'
   space.shading.show_shadows=True; space.shading.show_cavity=True
   space.region_3d.view_rotation=camera.rotation_euler.to_quaternion()
   space.region_3d.view_location=Vector((0,0,2.1)); space.region_3d.view_distance=7
   space.region_3d.view_perspective='CAMERA'
bpy.ops.object.select_all(action='DESELECT')
root=bpy.data.objects['RENARD | racine']; root.select_set(True); bpy.context.view_layer.objects.active=root
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print('EDITABLE_PROJECT_READY')
