import bpy,json
from pathlib import Path
ROOT=Path('D:/ai-generation-video');OUT=ROOT/'output/blender/v3'
def rgb(h):
    v=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)
def tune():
    for m in bpy.data.materials:
        if not m.name.startswith('V3 · Œil · regard '):continue
        for n in m.node_tree.nodes:
            if n.type!='VALTORGB':continue
            entries=[(0,'1D2427'),(.61,'1D2427'),(.64,'603C1E'),(.67,'C27A21'),(.86,'DEA047'),(.95,'A45D1E'),(.985,'493825'),(1,'FFF7E8')]
            for e,(pos,col) in zip(list(n.color_ramp.elements),entries):e.position=pos;e.color=(*rgb(col),1)
tune();s=bpy.context.scene;s.camera=bpy.data.objects['V3 · tête trois quarts'];bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-etude-tete-v3.blend'));s.cycles.samples=32
for name,cam in [('trois-quarts','V3 · tête trois quarts'),('face','V3 · tête face'),('profil','V3 · tête profil')]:
    s.camera=bpy.data.objects[cam];s.render.resolution_x=1000;s.render.resolution_y=1000;s.render.filepath=str(OUT/('renard-v3-tete-'+name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));tune();bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/renard-design-v2.blend'));s=bpy.context.scene;s.render.resolution_x=540;s.render.resolution_y=960;s.cycles.samples=24;s.render.filepath=str(OUT/'renard-v3-contexte.png');bpy.ops.render.render(write_still=True)
print('EYES_TUNED')
