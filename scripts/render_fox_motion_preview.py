import bpy,math,time,argparse,sys
from pathlib import Path
s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];p=argparse.ArgumentParser();p.add_argument('--end',type=int,default=150);p.add_argument('--both',action='store_true');p.add_argument('--clip',default='presentation');p.add_argument('--width',type=int,default=540);p.add_argument('--height',type=int,default=960);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path('D:/ai-generation-video/output/blender/rig-v1');out=root/(args.clip+'-frames');out.mkdir(parents=True,exist_ok=True)
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='FXAA';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='VERTEX';sh.show_shadows=False;sh.show_cavity=False;sh.show_specular_highlight=False
s.render.resolution_x=args.width;s.render.resolution_y=args.height;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.fps=30;s.frame_start=1;s.frame_end=args.end;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(out/'image-');s.render.use_compositing=False;s.render.use_sequencer=False;s.render.use_persistent_data=True
if args.clip=='marche':s.camera=bpy.data.objects['RIG · contrôle trois quarts']
def linear(h):
    a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
white=linear('FFF7E8');amber=linear('DEA047');dark=linear('1D2427');glint=linear('FFFDF3');eyes=[]
for side in [-1,1]:
    o=bpy.data.objects['V5 · Œil '+str(side)];uv=o.data.uv_layers['Regard'];uvs={}
    for loop in o.data.loops:uvs[loop.vertex_index]=uv.data[loop.index].uv.copy()
    eyes.append((o,uvs))
def refresh(scene,depsgraph=None):
    gx=rig.get('regard_horizontal',.024);gy=rig.get('regard_vertical',.008)
    for o,uvs in eyes:
        a=o.data.color_attributes['Aperçu articulation']
        for v in o.data.vertices:
            u,w=uvs[v.index];du=u-gx;dv=w-gy;r=math.hypot(du,dv)/.064;c=white if r>=1 else amber if r>.64 else dark
            if ((du+.018)/.0065)**2+((dv-.025)/.008)**2<1:c=glint
            a.data[v.index].color=(*c,1)
bpy.app.handlers.frame_change_post.append(refresh);refresh(s)
tm=time.monotonic();print('MOTION_RENDER_START',args.clip,args.end,flush=True)
bpy.ops.render.render(animation=True);print('MOTION_RENDER_COMPLETE_SECONDS',time.monotonic()-tm,flush=True)

if args.both:
    route=bpy.data.objects['TRAJECTOIRE · déplacement indépendant'];rig.animation_data.action=next(a for a in bpy.data.actions if a.name.startswith('TEST_01'));route.animation_data.action=next(a for a in bpy.data.actions if a.name.startswith('TRAJET_01'));s.frame_start=1;s.frame_end=180;s.render.resolution_x=640;s.render.resolution_y=360;s.camera=bpy.data.objects['RIG · contrôle trois quarts'];out=root/'marche-frames';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/'image-');print('WALK_RENDER_START',flush=True);tm=time.monotonic();bpy.ops.render.render(animation=True);print('WALK_RENDER_COMPLETE_SECONDS',time.monotonic()-tm,flush=True)
