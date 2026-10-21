import bpy,json,hashlib
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/rig-v1';report=[]
for filename in ['renard-rig-v1.blend','renard-presentation-v1.blend','renard-design-v2.blend']:
    path=ROOT/'blender'/filename;bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard']
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT');rig.hide_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='POSE')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                sp=area.spaces.active;sp.shading.type='SOLID';sp.shading.color_type='VERTEX';sp.shading.light='STUDIO';sp.shading.studio_light='paint.sl';sp.shading.show_shadows=False;sp.shading.show_cavity=False;sp.shading.show_specular_highlight=False;sp.overlay.show_overlays=False
                if sp.region_3d:sp.region_3d.view_perspective='CAMERA';sp.region_3d.view_camera_zoom=0;sp.region_3d.view_camera_offset=(0,0)
    iswalk=filename=='renard-rig-v1.blend'
    marks=[('Marche',1),('Ralentissement',109),('Arrêt',145),('Regard',157)] if iswalk else [('Repos',1),('Présentation',45),('Retour',112)]
    for name,frame in marks:
        m=s.timeline_markers.get(name) or s.timeline_markers.new(name,frame=frame);m.frame=frame
    s.frame_set(1);s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.fps=30;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
    assert rig.animation_data.action.name.startswith('TEST_01' if iswalk else 'TEST_02')
    mouths=[bpy.data.objects['V5 · Sourire chaleureux '+str(side)] for side in [-1,1]];assert all(o.modifiers[0].type=='SHRINKWRAP' for o in mouths)
    report.append({'file':str(path),'active_action':rig.animation_data.action.name,'frames':[s.frame_start,s.frame_end],'camera':s.camera.name,'resolution':[1080,1920],'fps':30,'bones':len(rig.data.bones),'mouth_attachment':True,'rgba':True,'packed_reference':any(i.packed_file for i in bpy.data.images)})
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
sha=hashlib.sha256((ROOT/'blender/Untitled.blend').read_bytes()).hexdigest();assert sha=='c07ea3121d866f07eed5303e23f599d163f3c1616e09beb519b5cf53928df4df'
(OUT/'verification-livraison-blender.json').write_text(json.dumps({'files':report,'source_sha256':sha},indent=2,ensure_ascii=False),encoding='utf8');print('WORKSPACE_VERIFIED',json.dumps(report),flush=True)
