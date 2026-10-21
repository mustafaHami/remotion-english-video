import bpy,json,hashlib
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];man=json.loads((O/'manifest.json').read_text(encoding='utf8'));loupe=bpy.data.objects['ACCESSOIRE · Loupe']
# Centre the handle inside the animated palm rather than at the wrist.
if not s.get('loupe_grip_v2_corrected',False):
    loupe.animation_data.action=bpy.data.actions['ACC_examiner-loupe_loupe']
    for f in range(1,121):s.frame_set(f);loupe.location.z-=.22;loupe.keyframe_insert('location',frame=f)
    s['loupe_grip_v2_corrected']=True
for o in bpy.data.collections['09 — Accessoires animés · indépendants'].objects:
    if o.type!='MESH':continue
    a=o.data.color_attributes.get('Aperçu articulation') or o.data.color_attributes.new(name='Aperçu articulation',type='FLOAT_COLOR',domain='POINT');o.data.color_attributes.active_color=a
    for v in a.data:v.color=o.data.materials[0].diffuse_color
for fc in rig.animation_data.drivers:
    if fc.array_index==0 and 'rotation_euler' in fc.data_path:
        if 'D_pouce' in fc.data_path:fc.driver.expression='-v*.7'
        elif 'D_doigt0' in fc.data_path:fc.driver.expression='-v*k*1.25'
        elif 'D_doigt' in fc.data_path:fc.driver.expression='-v*1.25'
for tag in ['G','D']:
    for part in ['A','B']:
        pb=rig.pose.bones['D_pouce'+part+'.'+tag]
        try:pb.driver_remove('scale',1)
        except:pass
        d=pb.driver_add('scale',1).driver;d.expression='1+.40*max(0,min(1,(v-.85)/.10))';v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='["doigts_'+tag+'"]'
rig.animation_data.action=bpy.data.actions['MVT_attente']
for name in ['ACCESSOIRE · Ampoule','ACCESSOIRE · Loupe']:
    ob=bpy.data.objects[name];ob.animation_data.action=bpy.data.actions['ACC_attente_'+('ampoule' if 'Ampoule' in name else 'loupe')]
s.frame_start=1;s.frame_end=120;s.frame_set(1);s.camera=bpy.data.objects[man['camera']];s.render.engine='BLENDER_EEVEE';s.render.resolution_x=768;s.render.resolution_y=768;s.render.resolution_percentage=100;s.render.fps=30;s.render.fps_base=1;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(O/'reexport/image-')
for mk in list(s.timeline_markers):s.timeline_markers.remove(mk)
s.timeline_markers.new('ATTENTE · boucle 4 secondes',frame=1)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='POSE')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            sp=area.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='VERTEX';sp.shading.light='STUDIO';sp.shading.studio_light='paint.sl';sp.shading.show_shadows=False;sp.shading.show_cavity=False;sp.shading.show_specular_highlight=False;sp.overlay.show_overlays=False
            if sp.region_3d:sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_camera_zoom=0;sp.region_3d.view_camera_offset=(0,0)
t=bpy.data.texts.get('00 · LIRE MOI — bibliothèque V2') or bpy.data.texts.new('00 · LIRE MOI — bibliothèque V2');t.clear();t.write((R/'docs/renard-bibliotheque-mouvements-v2.md').read_text(encoding='utf8'))
s['bibliotheque']='21 actions MVT_ · clips sur place · 30 i/s · PNG RGBA 768 carrés';s['documentation']='D:/ai-generation-video/docs/renard-bibliotheque-mouvements-v2.md';s['passation']='D:/ai-generation-video/docs/prompt-expert-remotion-renard-option-1.md'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/renard-bibliotheque-v2.blend'))
# Reopen the saved source, so this report checks the actual deliverable.
bpy.ops.wm.open_mainfile(filepath=str(R/'blender/renard-bibliotheque-v2.blend'));rig=bpy.data.objects['RIG · Renard'];s=bpy.context.scene
report={'file':bpy.data.filepath,'actions':[a.name for a in bpy.data.actions if a.name.startswith('MVT_')],'bones':len(rig.data.bones),'fingerDrivers':len(rig.animation_data.drivers),'defaultAction':rig.animation_data.action.name,'camera':s.camera.name,'resolution':[s.render.resolution_x,s.render.resolution_y],'engine':s.render.engine,'fps':s.render.fps,'rgba':s.render.image_settings.color_mode,'transparent':s.render.film_transparent,'sourceUntitledSHA256':hashlib.sha256((R/'blender/Untitled.blend').read_bytes()).hexdigest(),'loupeGripCorrected':s['loupe_grip_v2_corrected'],'packedReference':any(im.packed_file for im in bpy.data.images)}
assert len(report['actions'])==21 and report['fingerDrivers']==24 and report['bones']==59
assert report['sourceUntitledSHA256']=='c07ea3121d866f07eed5303e23f599d163f3c1616e09beb519b5cf53928df4df'
(O/'verification-source.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8');print('SOURCE_REOPENED_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
