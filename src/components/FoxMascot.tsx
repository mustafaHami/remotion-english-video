import React from 'react';
import {useCurrentFrame} from 'remotion';
import vectors from '../archive/experiments/options-v5/fox-vectors.json';

/** Exact supplied paths; autonomous SVG animation replaced by frame-based motion. */
export const FoxMascot=({pose='salut',size=166}:{pose?:'salut'|'bravo';size?:number})=>{
  const f=useCurrentFrame();
  const svg=vectors[pose]
    .replace('__FLOAT__',`translate(0 ${-2+2*Math.cos(2*Math.PI*f/90)})`)
    .replace('__TAIL__',`rotate(${2.5-2.5*Math.cos(2*Math.PI*f/78)} 130 200)`)
    .replace('__WAVE__',`rotate(${1+7*Math.sin(2*Math.PI*f/30)} 66 164)`)
    .replace('__POINT__','translate(0 0)');
  return <div style={{width:size,height:size*240/210}} dangerouslySetInnerHTML={{__html:svg}}/>;
};
