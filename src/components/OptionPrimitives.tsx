import React from 'react';
import {interpolateColors,useCurrentFrame} from 'remotion';
import {Stage,Icon} from './LessonPrimitives';
import {color,ledge} from '../design/tokens';
import {fonts,loadDesignFonts} from '../design/typography';
import {progress,reveal,tween} from '../design/motion';

export const bodyStyle:React.CSSProperties={fontFamily:`"${fonts.body}"`,fontWeight:800,color:color.ink};
export const displayStyle:React.CSSProperties={fontFamily:`"${fonts.display}"`,fontWeight:800,color:color.ink};

/** Same centered 336u sheet as the approved option 1; contents use local coordinates. */
export const OptionScene:React.FC<React.PropsWithChildren<{title:string;guide:string;completeAt:number;success?:boolean;quietDecor?:boolean;animateEntrance?:boolean}>>=({title,guide,completeAt,success=false,quietDecor=false,animateEntrance=true,children})=>{
  loadDesignFonts();const f=useCurrentFrame();const entrance=animateEntrance?f:10000;const done=f>=completeAt;
  return <Stage>
    <div style={{position:'absolute',inset:0,background:interpolateColors(f,[completeAt,completeAt+18],[color.lavender,color.mint])}}/>
    <svg width="360" height="640" style={{position:'absolute',inset:0}} aria-hidden><circle cx="338" cy="147" r="76" fill={color.sheet} opacity=".2"/>{!quietDecor?<path d="M316 102l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill={color.sheet}/>:null}</svg>
    <div data-center="title" style={{...displayStyle,position:'absolute',top:82,left:0,width:360,height:38,fontSize:26,lineHeight:'38px',textAlign:'center',...reveal(entrance,0,8,10)}}><span data-safe="option-title" style={{whiteSpace:'nowrap'}}>{title}</span></div>
    <div data-center="card" style={{position:'absolute',left:12,top:134,width:336,height:342,border:`2px solid ${color.ink}`,boxSizing:'border-box',borderRadius:28,background:color.sheet,boxShadow:ledge(5,color.ink),...reveal(entrance,4,12,14)}}/>
    <div style={{position:'absolute',left:12,top:134,width:336,height:342,...reveal(entrance,4,12,14)}}>{children}</div>
    <div data-center="guide" style={{...bodyStyle,position:'absolute',left:12,top:488,width:336,height:26,borderRadius:99,border:`1px solid ${done&&success?color.success:color.line}`,background:done&&success?color.successBg:color.sheet,display:'flex',alignItems:'center',justifyContent:'center',gap:6,boxSizing:'border-box',...reveal(entrance,24,5,8)}}>
      {done&&success?<Icon name="check" size={14} tint={color.success} stroke={3.4}/>:null}
      <span data-safe="option-guide" style={{fontSize:13,lineHeight:'18px',color:done&&success?color.success:color.ink2}}>{guide}</span>
    </div>
  </Stage>;
};

export const Text:React.FC<React.PropsWithChildren<{x?:number;y:number;w?:number;h?:number;size?:number;tint?:string;display?:boolean;start?:number;name:string;align?:'left'|'center';style?:React.CSSProperties}>>=({x=16,y,w=304,h=28,size=18,tint=color.ink,display=false,start=0,name,align='center',style,children})=>{
  const f=useCurrentFrame();return <div style={{position:'absolute',left:x,top:y,width:w,height:h,display:'flex',alignItems:'center',justifyContent:align==='center'?'center':'flex-start',...reveal(f,start,6,10),...style}}>
    <span data-safe={name} style={{...(display?displayStyle:bodyStyle),fontSize:size,lineHeight:`${h}px`,whiteSpace:'nowrap',color:tint}}>{children}</span>
  </div>;
};

export const Tile:React.FC<React.PropsWithChildren<{x:number;y:number;w:number;h?:number;fill?:string;start?:number;name:string;size?:number;correct?:boolean;muted?:boolean;style?:React.CSSProperties}>>=({x,y,w,h=42,fill=color.surface,start=0,name,size=18,correct=false,muted=false,style,children})=>{
  const f=useCurrentFrame();return <div style={{position:'absolute',left:x,top:y,width:w,height:h,borderRadius:14,border:`2px solid ${correct?color.success:color.line}`,boxSizing:'border-box',background:correct?color.successBg:fill,boxShadow:ledge(3,correct?color.success:color.ledge),display:'flex',alignItems:'center',justifyContent:'center',gap:6,...reveal(f,start,8,10),...style,opacity:progress(f,start,10)*(muted?.4:1)}}>
    {correct?<Icon name="check" size={15} tint={color.success} stroke={3.4}/>:null}
    <span data-safe={name} style={{...bodyStyle,fontSize:size,lineHeight:'24px',whiteSpace:'nowrap',color:correct?color.success:color.ink}}>{children}</span>
  </div>;
};

export const Pause:React.FC<{start:number;end:number;y?:number;x?:number;w?:number}>=({start,end,y=318,x=16,w=304})=>{
  const f=useCurrentFrame();return <div style={{position:'absolute',left:x,top:y,width:w,height:3,borderRadius:99,background:color.track,opacity:f>=start&&f<end?1:0}}><div style={{height:3,width:`${100*(1-progress(f,start,end-start))}%`,background:color.coral,borderRadius:99}}/></div>;
};

export const Arrow:React.FC<{x:number;y:number;w:number;start:number;duration?:number;tint?:string;double?:boolean}>=({x,y,w,start,duration=16,tint=color.ink,double=false})=>{
  const f=useCurrentFrame();const p=tween(f,start,duration);
  return <svg width={w} height="18" style={{position:'absolute',left:x,top:y,overflow:'visible',opacity:progress(f,start,6)}} viewBox={`0 0 ${w} 18`} aria-hidden>
    <path d={`M2 9H${w-5}`} pathLength="1" stroke={tint} strokeWidth="1.8" strokeDasharray="1" strokeDashoffset={1-p} fill="none"/>
    <path d={`M${w-10} 4l5 5-5 5${double?' M10 4L5 9l5 5':''}`} stroke={tint} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={p}/>
  </svg>;
};

export const Translation:React.FC<{text:string;y:number;start:number;name:string;size?:number}>=({text,y,start,name,size=15})=><Text y={y} size={size} tint={color.violet} start={start} name={name}>{text}</Text>;

/** Original vector props: objects only, no character or mascot. */
export const Receipt:React.FC<{y:number;scale?:number}>=({y,scale=1})=><svg width="96" height="96" viewBox="0 0 96 96" style={{position:'absolute',left:120,top:y,transform:`scale(${scale})`}} aria-hidden>
  <circle cx="48" cy="48" r="46" fill={color.lemon}/><path d="M29 18H67V78L60 73L54 78L48 73L42 78L36 73L29 78Z" fill={color.sheet} stroke={color.ink} strokeWidth="2" strokeLinejoin="round"/><path d="M37 32H59M37 41H59M37 50H52M37 61H59" stroke={color.ink} strokeWidth="2" strokeLinecap="round"/>
</svg>;

export const SoundIcon=()=> <svg width="28" height="28" viewBox="0 0 28 28" fill="none" stroke={color.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><path d="M4 11H9L15 6V22L9 17H4Z" fill={color.lemon}/><path d="M19 10Q23 14 19 18M22 7Q29 14 22 21"/></svg>;

/** Symmetric connector, centered at x=168 in the card; no one-sided draw phase. */
export const PairConnector=({row,start}:{row:number;start:number})=>{
 const f=useCurrentFrame();
 return <svg data-center={`pair-connector-${row}`} data-pair-connector={row} width={34} height={18} viewBox="0 0 34 18" style={{position:'absolute',left:151,top:63.5+row*25,opacity:progress(f,start,6),display:'block'}} fill="none" stroke={color.ink} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
  <path d="M4 9H30 M9 4L4 9L9 14 M25 4L30 9L25 14"/>
 </svg>;
};
