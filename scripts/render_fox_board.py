import bpy, math
from mathutils import Vector
from pathlib import Path
BASE=Path('D:/ai-generation-video')
scene=bpy.context.scene
root=bpy.data.objects['RENARD | racine']
children=list(root.children)
root.location.x=-3.1; root.rotation_euler[2]=-.55
for xpos,angle,title in [(0,0,'FACE'),(3.1,-math.pi/2,'PROFIL')]:
 r=bpy.data.objects.new('RENARD | vue '+title,None); scene.collection.objects.link(r); r.location.x=xpos; r.rotation_euler[2]=angle
 for child in children:
  copy=child.copy(); copy.data=child.data; scene.collection.objects.link(copy); copy.parent=r
cam=scene.camera; cam.location=(0,-16,5.6); cam.rotation_euler=(Vector((0,0,2.15))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=11.4
# Front facing labels as part of the actual rendered scene.
mat=bpy.data.materials.new('Planche | texte'); mat.diffuse_color=(.035,.048,.055,1); mat.use_nodes=True
p=mat.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(.035,.048,.055,1); p.inputs['Roughness'].default_value=1
fontpath=Path('C:/Windows/Fonts/segoeui.ttf'); font=bpy.data.fonts.load(str(fontpath)) if fontpath.exists() else None
def text(body,x,y,z,size):
 cu=bpy.data.curves.new(body,'FONT'); cu.body=body; cu.align_x='CENTER'; cu.size=size
 if font: cu.font=font
 ob=bpy.data.objects.new(body,cu); scene.collection.objects.link(ob); cu.materials.append(mat); ob.location=(x,y,z); ob.rotation_euler=cam.rotation_euler
text('RENARD — PREMIÈRE PROPOSITION 3D',0,0,4.72,.22)
text('Même personnage · Trois angles · Apparence à valider',0,0,4.39,.12)
for x,label in [(-3.1,'01 / TROIS QUARTS'),(0,'02 / FACE'),(3.1,'03 / PROFIL')]: text(label,x,-1.6,.04,.13)
scene.render.resolution_x=2200; scene.render.resolution_y=1200; scene.cycles.samples=32
scene.render.filepath=str(BASE/'output/blender/renard-3d-v1-planche.png')
bpy.ops.render.render(write_still=True)
print('BOARD_COMPLETE')
