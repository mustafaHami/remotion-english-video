import React from 'react';
import {color, ledge} from '../design/tokens';
import {type} from '../design/typography';
import {editorial as e} from '../design/editorial';
import {bump, curve, pop, progress, reveal, tween} from '../design/motion';
import {Icon} from './LessonPrimitives';

export const SingleLine: React.FC<React.PropsWithChildren<{name:string; style?:React.CSSProperties}>> = ({name,style,children}) =>
  <div data-safe={name} data-single-line style={{whiteSpace:'nowrap',...style}}>{children}</div>;

export const LessonTicket: React.FC<React.PropsWithChildren<{frame:number; start:number; label:string; top?:number; height?:number}>> = ({frame,start,label,top=188,height=262,children}) => <div style={{position:'absolute',left:20,top,width:280,height,...e.panel,boxSizing:'border-box',...reveal(frame,start,14,12)}}>
  <div style={{position:'absolute',top:-15,left:14,padding:'7px 11px',background:color.ink,borderRadius:999}}><SingleLine name="ticket-label" style={{...type.tag,fontSize:11}}>{label}</SingleLine></div>
  {children}
</div>;

export const ChapterRail: React.FC<{active:number; frame:number}> = ({active,frame}) => <div data-safe="chapter-rail" style={{position:'absolute',left:20,top:478,width:280,display:'flex',alignItems:'center',gap:8,...reveal(frame,16,6)}}>
  {['Choisis','Comprends','Réessaie'].map((label,i)=><React.Fragment key={label}>
    {i>0?<div style={{width:12,height:2,background:color.ink,opacity:.25}}/>:null}
    <div style={{display:'flex',alignItems:'center',gap:5,opacity:active===i?1:.5}}>
      <div style={{...type.tag,fontSize:10,width:20,height:20,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:999,background:active===i?color.ink:color.sheet,color:active===i?color.onInk:color.ink,border:`1px solid ${color.ink}`}}>{i+1}</div>
      <span style={{...type.meta,fontSize:11,color:color.ink,whiteSpace:'nowrap'}}>{label}</span>
    </div>
  </React.Fragment>)}
</div>;

export const CountdownStrip: React.FC<{frame:number; start:number; end:number}> = ({frame,start,end}) => {
  const t=progress(frame,start,end-start);
  const digit=Math.max(1,3-Math.floor((frame-start)/30));
  return <div style={{position:'absolute',left:16,top:204,width:248,...reveal(frame,start,6)}}>
    <div data-safe="countdown" style={{display:'flex',alignItems:'center',justifyContent:'space-between',marginBottom:7}}><span style={{...e.body,fontSize:13}}>Dis-le avant la réponse.</span><span style={{...type.timerDigit,fontSize:22,lineHeight:1}}>{digit}</span></div>
    <div style={{height:5,borderRadius:999,background:color.track,overflow:'hidden'}}><div style={{height:'100%',width:`${100*(1-t)}%`,background:color.coral,borderRadius:999}}/></div>
  </div>;
};

export const InlineSentence: React.FC<{frame:number; answerAt:number; before:string; after:string; answer:string; name:string}> = ({frame,answerAt,before,after,answer,name}) => {
  const p=tween(frame,answerAt,14,curve.drop);
  const answered=frame>=answerAt;
  return <SingleLine name={name} style={{...e.sentence,display:'flex',alignItems:'baseline',gap:5,width:'max-content'}}>
    <span>{before}</span><span style={{position:'relative',display:'inline-flex',verticalAlign:'baseline',alignItems:'center',justifyContent:'center',width:43,height:29,borderRadius:10,transform:'translateY(4px)',flexShrink:0}}>
      <span style={{position:'absolute',inset:0,boxSizing:'border-box',border:`2px dotted ${color.coral}`,borderRadius:10,opacity:1-progress(frame,answerAt,4),transform:`scale(${answered?1:1+.025*Math.sin(frame*Math.PI/30)})`}}/>
      <span style={{position:'absolute',inset:0,display:'flex',alignItems:'center',justifyContent:'center',background:color.successBg,color:color.success,borderRadius:10,opacity:progress(frame,answerAt,6),transform:`translateY(${-16*(1-p)}px) scale(${.8+.2*p})`}}>{answer}</span>
    </span><span>{after}</span>
  </SingleLine>;
};

export const CompactOptions: React.FC<{frame:number; start:number; answerAt:number; choices:readonly string[]; answer:string}> = ({frame,start,answerAt,choices,answer}) => <div style={{position:'absolute',left:16,top:143,width:248,display:'flex',gap:8}}>
  {choices.map((choice,i)=>{
    const selected=choice===answer, done=frame>=answerAt;
    return <div key={choice} style={{flex:1,...reveal(frame,start+i*4,10),opacity:progress(frame,start+i*4,8)*(done&&!selected?.35:1)}}>
      <div data-safe={`v2-option-${choice}`} style={{...type.option,fontSize:18,display:'flex',alignItems:'center',justifyContent:'center',gap:4,height:44,borderRadius:16,border:`2px solid ${done&&selected?color.success:color.ink}`,boxSizing:'border-box',background:done&&selected?color.successBg:color.surface,color:done&&selected?color.success:color.ink,boxShadow:done&&!selected?'none':ledge(3,done&&selected?color.success:color.ink),transform:`scale(${done&&selected?bump(frame,answerAt,16,.05):1})`}}>
        {done&&selected?<Icon name="check" size={13} stroke={3.4} tint={color.success}/>:null}{choice}
      </div>
    </div>;
  })}
</div>;

export const PairRow: React.FC<{frame:number; start:number; verb:string; noun:string; correct?:boolean}> = ({frame,start,verb,noun,correct}) => <div style={{display:'flex',gap:8,alignItems:'center',...reveal(frame,start,10)}}>
  <div data-safe={`pair-${verb}`} style={{...type.tipHeading,fontSize:30,width:90,height:58,boxSizing:'border-box',display:'flex',alignItems:'center',justifyContent:'center',gap:5,border:`2px solid ${correct?color.success:color.ink}`,borderRadius:18,background:correct?color.successBg:color.surface,color:correct?color.success:color.ink,boxShadow:ledge(4,correct?color.success:color.ink),...pop(frame,start,.9)}}>{correct?<Icon name="check" size={16} stroke={3.4} tint={color.success}/>:null}{verb}</div>
  <div data-safe={`noun-${noun}`} style={{...type.teaser,fontSize:25,whiteSpace:'nowrap'}}>{noun}</div>
</div>;
