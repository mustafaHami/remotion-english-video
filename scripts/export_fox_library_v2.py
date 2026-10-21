import bpy, json, sys, argparse, math, time
from pathlib import Path
R=Path('D:/ai-generation-video');O=R/'output/blender/mouvements-v2';manifest=json.loads((O/'manifest.json').read_text(encoding='utf8'))
p=argparse.ArgumentParser();p.add_argument('--engine',default='CYCLES');p.add_argument('--size',type=int,default=768);p.add_argument('--samples',type=int,default=8);p.add_argument('--only',default='');p.add_argument('--poses',action='store_true');p.add_argument('--start',type=int,default=1);p.add_argument('--end',type=int,default=0);p.add_argument('--accessories',action='store_true');p.add_argument('--all-accessories',action='store_true');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;rig=bpy.data.objects['RIG · Renard'];props=[bpy.data.objects[n] for n in ['ACCESSOIRE · Ampoule','ACCESSOIRE · Loupe']]
s.render.engine=args.engine;s.render.resolution_x=args.size;s.render.resolution_y=args.size;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.image_settings.compression=35;s.render.use_sequencer=False;s.render.use_compositing=False;s.render.use_persistent_data=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.threads_mode='FIXED';s.render.threads=6;s.frame_start=1;s.render.fps=30
if args.engine=='CYCLES':s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.1
elif args.engine=='BLENDER_WORKBENCH':
    s.display.render_aa='FXAA';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='VERTEX';sh.show_shadows=False;sh.show_cavity=False;sh.show_specular_highlight=False
    # Recompute iris colours every frame in the Workbench check only.
    def linear(h):
        a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
    eyes=[]
    for side in [-1,1]:
        o=bpy.data.objects['V5 · Œil '+str(side)];uv=o.data.uv_layers['Regard'];uvs={l.vertex_index:uv.data[l.index].uv.copy() for l in o.data.loops};eyes.append((o,uvs))
    def refresh(scene,depsgraph=None):
        for o,uvs in eyes:
            a=o.data.color_attributes['Aperçu articulation']
            for v in o.data.vertices:
                u,w=uvs[v.index];du=u-rig.get('regard_horizontal',.015);dv=w-rig.get('regard_vertical',.005);r=math.hypot(du,dv)/.064;c=linear('FFF7E8') if r>=1 else linear('DEA047') if r>.64 else linear('1D2427')
                if ((du+.018)/.0065)**2+((dv-.025)/.008)**2<1:c=linear('FFFDF3')
                a.data[v.index].color=(*c,1)
    bpy.app.handlers.frame_change_post.append(refresh)
    # Accessories get the same vertex-colour preview convention as the character.
    for o in bpy.data.collections['09 — Accessoires animés · indépendants'].objects:
        if o.type!='MESH':continue
        a=o.data.color_attributes.get('Aperçu articulation') or o.data.color_attributes.new(name='Aperçu articulation',type='FLOAT_COLOR',domain='POINT');o.data.color_attributes.active_color=a
        for v in a.data:v.color=o.data.materials[0].diffuse_color

def select(c):
    rig.animation_data.action=bpy.data.actions[c['action']]
    for ob in props:ob.animation_data.action=bpy.data.actions[c['accessoryActions'][ob.name]]
    s.frame_start=1;s.frame_end=c['frames'];s.frame_set(1)
charobjects=[o for o in s.objects if o.type=='MESH' and o.name not in bpy.data.collections['09 — Accessoires animés · indépendants'].objects and not o.hide_render]
accobjects=[o for o in bpy.data.collections['09 — Accessoires animés · indépendants'].objects if o.type=='MESH']
clips=[c for c in manifest['clips'] if not args.only or c['id'] in args.only.split(',')]
if args.poses:
    for c in clips:
        select(c);folder=O/'poses';folder.mkdir(exist_ok=True)
        for f in sorted(set([1,max(1,round(c['frames']*.27)),round(c['frames']*.5),round(c['frames']*.74),c['frames']])):
            s.frame_set(f);s.render.filepath=str(folder/(c['id']+'-%04d.png'%f));print('POSE',c['id'],f,flush=True);bpy.ops.render.render(write_still=True)
else:
    for c in clips:
        select(c)
        for ob in charobjects:ob.hide_render=args.accessories
        for ob in accobjects:ob.hide_render=not args.accessories
        if args.accessories and not c['accessory']:continue
        folder=O/('accessoires/'+c['accessory'] if args.accessories else 'frames/'+c['id']);folder.mkdir(parents=True,exist_ok=True)
        s.frame_start=args.start;s.frame_end=min(c['frames'],args.end) if args.end else c['frames'];s.render.filepath=str(folder/'image-');tm=time.monotonic();print('EXPORT_START',c['id'],s.frame_start,s.frame_end,args.engine,flush=True)
        bpy.ops.render.render(animation=True);print('EXPORT_DONE',c['id'],'SECONDS',time.monotonic()-tm,flush=True)
if args.all_accessories:
    for c in manifest['clips']:
        if not c['accessory']:continue
        select(c)
        for ob in charobjects:ob.hide_render=True
        for ob in accobjects:ob.hide_render=False
        folder=O/'accessoires'/c['accessory'];folder.mkdir(parents=True,exist_ok=True);s.frame_start=1;s.frame_end=c['frames'];s.render.filepath=str(folder/'image-');print('ACCESSORY_START',c['accessory'],flush=True);bpy.ops.render.render(animation=True);print('ACCESSORY_DONE',c['accessory'],flush=True)
print('EXPORT_ALL_DONE',flush=True)
