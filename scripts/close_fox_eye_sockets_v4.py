import bpy
from mathutils import Vector
s=bpy.context.scene;head=bpy.data.objects['Renard · tête et museau sculptés']
for side in [-1,1]:
    normal=Vector((side*.26,-.966,.025)).normalized();right=Vector((.966,side*.26,0)).normalized();up=normal.cross(right).normalized()
    eye=bpy.data.objects['V4 · Œil continu '+str(side)];origin=eye.data.vertices[0].co-normal*.006
    for vert in head.data.vertices:
        q=vert.co-origin;u=q.dot(right);v=q.dot(up);d=q.dot(normal);r2=(u/.09)**2+(v/.058)**2
        if r2<1.6 and -.12<d<.12:
            t=max(0,min(1,(1.6-r2)/.55));w=t*t*(3-2*t);vert.co+=normal*((-.002-d)*w)
s['eye_contact_revision']='continuous-socket-v4'
s.camera=bpy.data.objects['V4 · tête trois quarts'];s.render.resolution_x=1000;s.render.resolution_y=1000
bpy.ops.wm.save_as_mainfile(filepath='D:/ai-generation-video/output/blender/v4/candidat-raccord-yeux.blend')
s.render.resolution_x=650;s.render.resolution_y=650;s.cycles.samples=20;s.render.filepath='D:/ai-generation-video/output/blender/v4/controle-raccord-yeux.png';bpy.ops.render.render(write_still=True)
