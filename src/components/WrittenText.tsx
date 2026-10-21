import React from 'react';
import {Img} from 'remotion';
import {color} from '../design/tokens';
import {progress} from '../design/motion';

export type WritingPath = {
  text:string;width:number;inkCenter?:number;height:number;path:string;length:number;
  strokes:{d:string;points:number[][];length:number;start:number}[];
};
export const pointOnWriting = (data:WritingPath,p:number):{x:number;y:number} => {
  const distance=Math.min(.999999,Math.max(0,p))*data.length;
  const stroke=data.strokes.find(s=>s.start+s.length>=distance)??data.strokes[data.strokes.length-1];
  let remaining=distance-stroke.start;
  for(let i=1;i<stroke.points.length;i++){
    const a=stroke.points[i-1],b=stroke.points[i],length=Math.hypot(b[0]-a[0],b[1]-a[1]);
    if(remaining<=length){const t=length?remaining/length:0;return{x:a[0]+(b[0]-a[0])*t,y:a[1]+(b[1]-a[1])*t};}
    remaining-=length;
  }
  const last=stroke.points[stroke.points.length-1];return{x:last[0],y:last[1]};
};

/** Reveal the actual font contours along the same path that drives the pen. */
export const WrittenText:React.FC<{data:WritingPath;frame:number;start:number;duration:number;id:string;tint?:string}>=({data,frame,start,duration,id,tint=color.ink})=>{
  const p=progress(frame,start,duration),complete=p>=1;
  // Isolate finished outlines from the live SVG mask's compositing context.
  // Remotion's Img also waits for the self-contained vector image to decode.
  if(complete){
    const source=`<svg xmlns="http://www.w3.org/2000/svg" width="${data.width+2}" height="${data.height}" viewBox="0 0 ${data.width+2} ${data.height}"><path fill="${tint}" d="${data.path}"/></svg>`;
    return <Img data-safe={id} data-writing-text={data.text} data-writing-progress={p} data-static-ink-center={data.inkCenter??data.width/2} src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(source)}`} width={data.width+2} height={data.height} style={{display:'block'}} alt={data.text}/>;
  }
  if(p<=0)return <div data-writing-text={data.text} data-writing-progress={0} style={{width:data.width+2,height:data.height,opacity:0}}/>;
  return <svg data-safe={p>0?id:undefined} data-writing-text={data.text} data-writing-progress={p} width={data.width+2} height={data.height} viewBox={`0 0 ${data.width+2} ${data.height}`} style={{display:'block',overflow:'visible',opacity:p>0?1:0}} aria-label={data.text}>
    {!complete?<defs><mask id={`write-${id}`} maskUnits="userSpaceOnUse" x="-2" y="-2" width={data.width+6} height={data.height+4}>
      {data.strokes.map((stroke,i)=>{
        const amount=Math.min(1,Math.max(0,(p*data.length-stroke.start)/stroke.length));
        return amount>0?<path key={i} d={stroke.d} fill="none" stroke="white" strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={stroke.length} strokeDashoffset={stroke.length*(1-amount)}/>:null;
      })}
    </mask></defs>:null}
    <path data-writing-ink d={data.path} fill={tint} mask={complete?undefined:`url(#write-${id})`}/>
  </svg>;
};

/** A narrow vector pen is an object, never a replacement character or mascot. */
export const WritingPen:React.FC<{x:number;y:number;opacity:number;frame:number;scale?:number}>=({x,y,opacity,frame,scale=1})=><div data-pen-tip={`${x.toFixed(3)},${y.toFixed(3)}`} style={{position:'absolute',left:x,top:y,opacity,transform:`rotate(${32+1.2*Math.sin(frame/6)}deg) scale(${scale})`,transformOrigin:'0 0',pointerEvents:'none'}}>
  <svg width="15" height="64" viewBox="-7 -61 15 64" style={{position:'absolute',left:-7,top:-61,overflow:'visible'}} aria-hidden>
    <path d="M-3 -9 L-3 -53 Q0 -59 3 -53 L3 -9 L0 0Z" fill={color.ink} opacity=".16" transform="translate(2 2)"/>
    <path d="M-3 -11V-53Q0 -59 3 -53V-11Z" fill={color.ink}/>
    <path d="M-3 -48H3V-36H-3Z" fill={color.violet}/>
    <path d="M-3 -11 L0 0 L3 -11Z" fill={color.surface} stroke={color.ink} strokeWidth=".7" strokeLinejoin="round"/>
    <path d="M-.9 -3 L0 0 L.9 -3Z" fill={color.ink}/>
    <path d="M-1.2 -33V-16" stroke={color.surface} strokeOpacity=".6" strokeWidth=".6" strokeLinecap="round"/>
  </svg>
</div>;
