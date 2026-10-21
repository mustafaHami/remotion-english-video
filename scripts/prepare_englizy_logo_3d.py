from PIL import Image, ImageDraw, ImageFilter
import numpy as np,json,math
from pathlib import Path
root=Path('D:/ai-generation-video/output/englizy/3d')
im=Image.open('D:/ai-generation-video/output/englizy/englizy-logo-rond.png').convert('RGBA')
W,H=im.size
rgb=np.array(im)[:,:,:3].astype(float)
r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
Y,X=np.mgrid[:H,:W]
def polygon(points):
    m=Image.new('L',(W,H));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
# Character contour preserves projected identity while excluding its cream backdrop.
fox_outline=[(302,558),(334,508),(357,469),(360,417),(358,363),(364,300),(377,240),(389,188),(402,164),(419,176),(480,242),(541,316),(574,318),(616,256),(670,194),(716,151),(724,146),(735,157),(748,214),(754,275),(754,319),(746,351),(756,380),(766,418),(785,444),(811,465),(848,484),(871,491),(908,492),(930,496),(938,504),(934,516),(918,540),(896,551),(872,571),(847,591),(816,609),(781,625),(742,640),(700,656),(670,672),(677,690),(685,708),(695,736),(707,760),(704,794),(690,821),(666,839),(632,851),(588,852),(544,847),(500,839),(458,825),(426,808),(407,787),(391,760),(381,735),(375,706),(379,677),(389,656),(408,645),(437,644),(461,653),(454,630),(422,620),(376,611),(310,616),(350,579),(302,558)]
# Use the reference texture on the exact outline; refine foreground's outer orange and dark boundaries.
foxmask=polygon(fox_outline)
cream=(r>215)&(g>190)&(b>155)
neck=polygon([(535,607),(700,620),(687,651),(663,679),(663,707),(596,707),(577,665),(554,639)])
foxmask &= ~(cream & (((Y>625)&(X<450))|(Y>710)))
# Exchange bubbles: include their cream edge exactly, using background hue rejection.
bubble_roi=polygon([(737,640),(771,617),(811,607),(854,607),(887,615),(915,632),(936,641),(958,624),(992,621),(1031,627),(1065,640),(1094,667),(1105,703),(1104,792),(1096,823),(1082,842),(1095,860),(1080,878),(1052,870),(1018,848),(1004,838),(974,845),(934,842),(905,833),(876,817),(850,824),(819,822),(799,833),(753,823),(730,822),(727,806),(741,775),(728,751),(719,727),(719,687),(728,657)])
lav=(b>r*1.15)&(b>g*1.15)&(r>90)
bubblemask=bubble_roi & (~lav)
# Brand letters are reconstructed as separate extruded contour solids, not replaced by a font.
letters=(Y>=868)&(Y<1110)&(X>240)&(X<1040)&(r<75)&(g<70)&(b<115)&(np.array(im)[:,:,3]>200)
# Trace binary raster boundaries to closed vector loops with holes.
def simplify(points,tol=1.4):
    if len(points)<4:return points
    def rdp(p):
        if len(p)<3:return p
        a=np.array(p[0]);z=np.array(p[-1]);v=z-a
        ar=np.array(p);d=np.abs(np.cross(v,ar-a))/max(np.linalg.norm(v),1e-8)
        idx=int(np.argmax(d))
        return rdp(p[:idx+1])[:-1]+rdp(p[idx:]) if d[idx]>tol else [p[0],p[-1]]
    k=len(points)//2
    return rdp(points[:k+1])[:-1]+rdp(points[k:]+[points[0]])[:-1]
def trace(mask):
    # One pixel per two source pixels is enough for smooth logo contours with bevels.
    m=np.array(Image.fromarray((mask*255).astype('uint8')).resize((627,627),Image.Resampling.NEAREST))>0
    h,w=m.shape
    edges={}
    def add(a,b):edges.setdefault(a,[]).append(b)
    for y,x in zip(*np.where(m)):
        if y==0 or not m[y-1,x]:add((x,y),(x+1,y))
        if x==w-1 or not m[y,x+1]:add((x+1,y),(x+1,y+1))
        if y==h-1 or not m[y+1,x]:add((x+1,y+1),(x,y+1))
        if x==0 or not m[y,x-1]:add((x,y+1),(x,y))
    out=[]
    while edges:
        start=next(iter(edges));p=start;loop=[]
        while True:
            loop.append(p);targets=edges[p];q=targets.pop()
            if not targets:del edges[p]
            p=q
            if p==start:break
            if p not in edges:break
        if len(loop)>12:
            area=sum(loop[i][0]*loop[(i+1)%len(loop)][1]-loop[(i+1)%len(loop)][0]*loop[i][1] for i in range(len(loop)))/2
            if abs(area)>8:out.append([[float(x*2),float(y*2)] for x,y in simplify(loop)])
    return out
layers={'fox':trace(foxmask),'languages':trace(bubblemask)}
# Isolate seven letters by x spans; dot of i belongs to i.
spans=[('E',268,403),('n',403,527),('g',527,661),('l',661,720),('i',720,778),('z',778,893),('y',893,1035)]
for name,left,right in spans:layers['letter_'+name]=trace(letters&(X>=left)&(X<right))
(root/'contours.json').write_text(json.dumps(layers))
im.save(root/'logo-reference.png')
# Inspect masks aligned with original, for native Blender texture extraction QA.
out=Image.new('RGBA',(W,H),(169,155,255,255))
for mask in [foxmask,bubblemask,letters]:
    layer=im.copy();layer.putalpha(Image.fromarray((mask*255).astype('uint8')));out.alpha_composite(layer)
out.save(root/'contours-preview.png')
print({k:len(v) for k,v in layers.items()})
