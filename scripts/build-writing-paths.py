"""Build deterministic pen trajectories from the project's actual Nunito font."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.npm-cache/qa-python'))
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

FONT = ROOT/'public/fonts/Nunito-Variable.ttf'
font=instantiateVariableFont(TTFont(FONT),{'wght':800},inplace=True)
glyphs=font.getGlyphSet(); cmap=font.getBestCmap()
size=16.5; scale=size/font['head'].unitsPerEm; baseline=19

class Samples(BasePen):
    def __init__(self,glyphset):
        super().__init__(glyphset); self.contours=[]; self.current=[]
    def _moveTo(self,p):
        self.current=[p]
    def _lineTo(self,p):
        self.current.append(p)
    def _qCurveToOne(self,c,p):
        a=self.current[-1]
        for i in range(1,13):
            t=i/12;s=1-t
            self.current.append((s*s*a[0]+2*s*t*c[0]+t*t*p[0],s*s*a[1]+2*s*t*c[1]+t*t*p[1]))
    def _curveToOne(self,c,d,p):
        a=self.current[-1]
        for i in range(1,17):
            t=i/16;s=1-t
            self.current.append((s**3*a[0]+3*s*s*t*c[0]+3*s*t*t*d[0]+t**3*p[0],s**3*a[1]+3*s*s*t*c[1]+3*s*t*t*d[1]+t**3*p[1]))
    def _closePath(self):
        self.current.append(self.current[0]);self.contours.append(self.current);self.current=[]
    def _endPath(self):
        self.contours.append(self.current);self.current=[]

def phrase(text):
    x=0;filled=[];strokes=[];total=0
    for char in text:
        glyph=glyphs[cmap[ord(char)]]
        path=SVGPathPen(glyphs,ntos=lambda n: str(round(n,4)))
        glyph.draw(TransformPen(path,(scale,0,0,-scale,x,baseline)))
        filled.append(path.getCommands())
        pen=Samples(glyphs);glyph.draw(pen)
        for contour in pen.contours:
            pts=[[round(x+px*scale,4),round(baseline-py*scale,4)] for px,py in contour]
            length=sum(math.dist(a,b) for a,b in zip(pts,pts[1:]))
            if length<.01:continue
            d='M'+' L'.join(f'{px} {py}' for px,py in pts)
            strokes.append({'d':d,'points':pts,'length':round(length,4),'start':round(total,4)})
            total+=length
        x+=glyph.width*scale
    xs=[point[0] for stroke in strokes for point in stroke['points']]
    return {'text':text,'width':round(x,4),'inkCenter':round((min(xs)+max(xs))/2,4),'height':24,'path':' '.join(filled),'length':round(total,4),'strokes':strokes}

import argparse
parser=argparse.ArgumentParser();parser.add_argument('--content',type=Path);args=parser.parse_args()
lesson=json.loads(args.content.read_text(encoding='utf-8-sig')) if args.content else None
rows=lesson['lessonData']['rows'] if lesson else json.loads((ROOT/'src/archive/experiments/test-option-1/rows.json').read_text(encoding='utf-8'))
texts=[row[key] for row in rows for key in ('present','past','future')]
result={text:phrase(text) for text in texts}
target=args.content if args.content else ROOT/'src/options/option-1/writing-paths.json'
target.parent.mkdir(parents=True,exist_ok=True)
if lesson:
    lesson['writingPaths']=result
    target.write_text(json.dumps(lesson,ensure_ascii=False,indent=2),encoding='utf-8')
else:target.write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
print('Nunito 800 outlines and trajectories:',target)
print({text:data['width'] for text,data in result.items()})
