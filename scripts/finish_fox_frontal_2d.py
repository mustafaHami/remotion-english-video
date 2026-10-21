import bpy,math,json
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/renard-frontal-2d';s=bpy.context.scene;W,H=1774,887;S=.01
def pos(x,y,depth):return (x*S,depth,(H-y)*S)
image=bpy.data.images['RÉFÉRENCE ORIGINALE · deux poses frontales']
for node in bpy.data.materials['Dessin original · couleurs et transparence conservées'].node_tree.nodes:
    if node.type=='TEX_IMAGE':node.interpolation='Linear'
col=bpy.data.collections.new('03 · Paupières · clignements seulement');s.collection.children.link(col)
def alpha_material(name,rig,bone,textured=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');out=nt.nodes.new('ShaderNodeOutputMaterial')
    if textured:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';nt.links.new(tex.outputs['Color'],em.inputs['Color'])
    else:
        rgb=[int('30363C'[i:i+2],16)/255 for i in (0,2,4)];rgb=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb];em.inputs['Color'].default_value=(*rgb,1)
    nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);d=mix.inputs[0].driver_add('default_value').driver;d.expression='max(0,min(1,(.65-v)/.50))';v=d.variables.new();v.name='v';v.targets[0].id=rig;v.targets[0].data_path='pose.bones["'+bone+'"].scale[1]'
    m.surface_render_method='BLENDED';return m
def mesh(name,verts,faces,uvcoords,mat,rig):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);col.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='UV du dessin')
    for loop in me.loops:uv.data[loop.index].uv=uvcoords[loop.vertex_index]
    vg=ob.vertex_groups.new(name='Tête · inclinaison');vg.add(list(range(len(verts))),1,'REPLACE');m=ob.modifiers.new('Suit la tête, sans écraser la paupière','ARMATURE');m.object=rig;ob.parent=rig;return ob
for label,offset,centres in [('01 · Salut',0,[(583,141),(655,141)]),('02 · Pouce levé',620,[(587,143),(656,143)])]:
    rig=bpy.data.objects[label+' · RIG']
    for side,(cx,cy) in zip(['G','D'],centres):
        bone='Œil · clignement.'+side;cx+=offset
        verts=[pos(cx,cy,-.02)];uvs=[(cx/W,1-(cy-24)/H)]
        for j in range(40):
            a=math.tau*j/40;x=cx+21*math.cos(a);y=cy+4.5*math.sin(a);verts.append(pos(x,y,-.02));uvs.append((x/W,1-(cy-24)/H))
        faces=[(0,1+j,1+(j+1)%40) for j in range(40)];mat=alpha_material(label+' · voile paupière '+side,rig,bone,True);mesh(label+' · peau paupière '+side,verts,faces,uvs,mat,rig)
        verts=[];uvs=[];n=24
        for j in range(n+1):
            t=j/n;x=cx-15+30*t;y=cy+1+1.5*math.sin(math.pi*t)
            for d in [-.8,.8]:verts.append(pos(x,y+d,-.03));uvs.append((0,0))
        faces=[(2*j,2*j+1,2*j+3,2*j+2) for j in range(n)];mat=alpha_material(label+' · trait paupière '+side,rig,bone);mesh(label+' · ligne œil fermé '+side,verts,faces,uvs,mat,rig)
s.frame_set(1);s.render.filepath=str(O/'frames/image-');s['clignements']='Paupières 2D visibles uniquement pendant la fermeture ; dessin original inchangé au repos.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'blender/renard-frontal-2d-articule.blend'))
s.render.filepath=str(O/'renard-frontal-reference.png');bpy.ops.render.render(write_still=True)
s.render.filepath=str(O/'frames/image-');s.frame_start=1;s.frame_end=180;bpy.ops.render.render(animation=True);print('FINAL_2D_RENDER_DONE',flush=True)
