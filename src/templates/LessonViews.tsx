import React from 'react';
import {Sequence,useCurrentFrame} from 'remotion';
import {Text,Tile,Arrow,Pause,Translation,Receipt,SoundIcon,PairConnector} from '../components/OptionPrimitives';
import {Icon} from '../components/LessonPrimitives';
import {color} from '../design/tokens';
import {progress,tween,reveal} from '../design/motion';
import {useLessonContent} from '../content/LessonContent';

const fills=[color.lavender,color.lemon,color.mint];
export const PageMotion:React.FC<React.PropsWithChildren<{duration:number}>>=({duration,children})=>{
  const f=useCurrentFrame();return <div style={{position:'absolute',inset:0,opacity:Math.min(progress(f,0,9),1-progress(f,duration-8,8)),transform:`translateY(${6*(1-tween(f,0,10))}px)`}}>{children}</div>;
};
export const Pages:React.FC<{count?:number;duration?:number;children:(index:number)=>React.ReactNode}>=({count=3,duration=420,children})=><>{Array.from({length:count},(_,i)=><Sequence key={i} from={i*duration} durationInFrames={duration} layout="none"><PageMotion duration={duration}>{children(i)}</PageMotion></Sequence>)}</>;
const Count=({i,total=3}:{i:number;total?:number})=><Tile x={132} y={18} w={72} h={28} fill={fills[i%3]} name="page-counter" size={14}>{String(i+1).padStart(2,'0')} / {String(total).padStart(2,'0')}</Tile>;

type Gap={before:string;after:string;answer:string;choices:string[];en:string;fr:string;note:string};
export const GapPage=({item,i,thinkingDelay=0,timing}:{item:Gap;i:number;thinkingDelay?:number;timing?:{answerAt:number;pauseAt:number;choicesAt:number;noteAt:number}})=>{
  const answerAt=timing?.answerAt??210+thinkingDelay;
  const f=useCurrentFrame();const answered=f>=answerAt;
  return <><Count i={i}/><Text y={67} size={14} tint={color.inkMuted} name="question-heading">Quel mot complète la phrase ?</Text>
    <Text y={117} h={38} size={19} start={12} name="gap-sentence">{item.before}<span style={{display:'inline-block',minWidth:55,margin:'0 5px',padding:'0 3px',lineHeight:'32px',textAlign:'center',borderRadius:10,border:`2px ${answered?'solid':'dashed'} ${answered?color.success:color.coral}`,color:answered?color.success:color.ink,background:answered?color.successBg:'transparent'}}>{answered?item.answer:'…'}</span>{item.after}</Text>
    <Translation text={item.fr} y={173} start={28} name="gap-translation" size={14.5}/>
    {item.choices.map((choice,j)=><Tile key={choice} x={34+j*140} y={226} w={128} h={44} start={(timing?.choicesAt??40)+j*7} correct={answered&&choice===item.answer} muted={answered&&choice!==item.answer} name={`choice-${j}`} size={20}>{choice}</Tile>)}
    <Text y={291} h={22} size={14} tint={color.ink2} start={timing?.noteAt??240+thinkingDelay} name="gap-note">{item.note}</Text><Pause start={timing?.pauseAt??60+thinkingDelay} end={answerAt}/>
  </>;
};

export const SituationPage=({i}:{i:number})=>{
  const content=useLessonContent();
  const f=useCurrentFrame(),item=content.situation[i],answered=f>=210;
  return <><Count i={i}/><Receipt y={47} scale={.57}/><Text y={139} size={16} start={12} name="situation-context">{item.context}</Text>
    {item.choices.map((choice,j)=><Tile key={choice} x={24} y={184+j*53} w={288} h={40} start={35+j*6} size={18.5} name={`situation-${j}`} correct={answered&&j===item.answer} muted={answered&&j!==item.answer}>{choice}</Tile>)}
    <Translation text={item.fr} y={281} start={235} name="situation-fr" size={14}/><Pause start={60} end={210}/>
  </>;
};

export const AssociationPage=({i}:{i:number})=>{
  const content=useLessonContent();
  const f=useCurrentFrame(),item=content.associations[i],join=tween(f,85,24);
  return <><Count i={i}/><Text y={74} size={15} tint={color.inkMuted} name="association-heading">Apprends le groupe complet.</Text>
    <Tile x={26+18*join} y={132} w={112} h={52} fill={fills[i]} name="associate-verb" size={26}>{item.verb}</Tile>
    <Tile x={198-18*join} y={132} w={112} h={52} name="associate-object" size={24}>{item.rest}</Tile>
    <Text x={140} y={141} w={56} h={32} size={23} name="plus" style={{opacity:1-join}}>+</Text>
    <div style={{position:'absolute',left:156,top:151,width:24,height:14,borderRadius:99,background:fills[i],border:`2px solid ${color.ink}`,boxSizing:'border-box',opacity:join}}/>
    <Translation text={item.fr} y={207} start={110} name="association-fr" size={17}/>
    <Text y={269} size={22} display start={210} name="association-example">{item.en}</Text>
  </>;
};

export const CorrectionPage=({i}:{i:number})=>{
  const content=useLessonContent();
  const f=useCurrentFrame(),item=content.corrections[i];
  return <><Count i={i}/><Text y={67} size={15} tint={color.inkMuted} name="correction-instruction">Comment corriger cette phrase ?</Text>
    <div style={{opacity:f>=210?.38:1}}><Text y={117} size={27} display start={15} name="before-correction">{item.before}</Text>
      <div style={{position:'absolute',left:45,top:135,width:246*tween(f,210,16),height:2,background:color.ink,opacity:progress(f,210,8)}}/>
    </div>
    <Tile x={20} y={184} w={296} h={53} size={24} start={222} correct name="corrected">{item.en}</Tile>
    <Translation text={item.fr} y={252} start={245} name="correction-fr" size={16}/>
    <Text y={296} h={22} size={14} start={270} name="correction-note" tint={color.ink2}>{item.note}</Text>
    <Pause start={60} end={210}/>
  </>;
};

export const DialoguePage=({i}:{i:number})=>{
  const content=useLessonContent();
  const f=useCurrentFrame();return <><Count i={i} total={4}/>
    {content.dialogue.slice(i*2,i*2+2).map((item,j)=>{
      const top=72+j*133,start=j===0?10:160;
      return <React.Fragment key={item.en}>
        <div style={{position:'absolute',left:18,top,width:300,height:53,borderRadius:j===0?'19px 19px 19px 5px':'19px 19px 5px 19px',background:j===0?color.lavender:color.lemon,boxShadow:`0 3px 0 ${color.ledge}`,...reveal(f,start,8,12)}}/>
        <Text x={22} w={292} y={top+12} size={18} start={start+2} name={`dialogue-line-${j}`}>{item.en}</Text>
        <Translation text={item.fr} y={top+64} start={start+25} name={`dialogue-fr-${j}`} size={13.5}/>
      </React.Fragment>;
    })}
  </>;
};

export const RecallPage=({i,transfer=false}:{i:number;transfer?:boolean})=>{
  const content=useLessonContent();
  const f=useCurrentFrame();const item=transfer?content.transfer[i]:content.recall[i];const model=transfer&&i===0;const answer=f>=(model?65:210);
  return <><Count i={i}/><Text y={72} size={14} tint={color.inkMuted} name="recall-heading">{model?'Retiens d’abord ce groupe.':'Trouve une formulation, sans choix.'}</Text>
    <Text y={123} size={22} display tint={color.violet} start={15} name="recall-prompt">{transfer?content.transfer[i].prompt:item.fr}</Text>
    {answer?<Tile x={18} y={193} w={300} h={58} size={22} correct start={model?65:210} name="recall-answer">{item.en}</Tile>:<div style={{position:'absolute',left:28,top:193,width:280,height:58,borderRadius:18,border:`2px dashed ${color.coral}`,boxSizing:'border-box'}}/>}
    <Text y={280} size={14} tint={transfer?color.violet:color.inkMuted} start={model?90:240} name="recall-note">{transfer?item.fr:'Une réponse possible.'}</Text>
    {!model?<Pause start={60} end={210}/>:null}
  </>;
};

type Clip={start:number;duration:number;peaks:number[]};
export const ListenPage=({i,clips}:{i:number;clips:Clip[]})=>{
  const content=useLessonContent();
  const f=useCurrentFrame(),item=content.listen[i];const local=clips.filter(c=>c.start>=i*420&&c.start<(i+1)*420).map(c=>({...c,start:c.start-i*420}));
  const active=local.find(c=>f>=c.start&&f<c.start+c.duration);const phase=f<150?0:f<310?1:2;const played=active?(f-active.start)/active.duration:0;const wave=active?.peaks??local[0]?.peaks??[];
  return <><Count i={i}/><div style={{position:'absolute',left:154,top:69}}><SoundIcon/></div>
    <Text y={118} size={26} display start={12} name="listen-en">{item.en}</Text><Translation text={item.fr} y={163} start={24} name="listen-fr" size={15}/>
    <svg width="272" height="48" viewBox="0 0 272 48" style={{position:'absolute',left:32,top:211}} aria-hidden>{wave.map((v,k)=>{const h=3+v*42;return <rect key={k} x={k*4.5} y={(48-h)/2} width="2.5" height={h} rx="1.2" fill={active&&k/60<played?color.violet:color.line}/>;})}</svg>
    {['Écoute','À toi','Réécoute'].map((label,j)=><Tile key={label} x={20+j*101} y={283} w={94} h={30} fill={phase===j?color.lemon:color.surface} name={`listen-phase-${j}`} size={14} muted={phase!==j}>{label}</Tile>)}
    <Pause start={150} end={310}/>
  </>;
};

export const VerbView=({verb}:{verb:string})=>{
  const content=useLessonContent();
  const family=content.verbSeries.find(v=>v.verb===verb)!;const examples=family.examples??content.verbExamples;
  return <><Sequence from={0} durationInFrames={450} layout="none"><PageMotion duration={450}>
    <Tile x={24} y={18} w={104} h={30} fill={color.lavender} name="subject-label" size={15}>Pronom</Tile><Tile x={208} y={18} w={104} h={30} fill={color.lemon} name="verb-label" size={15}>{family.label}</Tile>
    {family.forms.map((form,i)=>{const [subject,...words]=form.split(' '),start=48+i*48,y=61+i*35;const tint=words[0]==='is'||words[0]==='has'?color.lemon:words[0]==='are'?color.mint:color.lavender;return <React.Fragment key={form}>
      <Tile x={24} y={y} w={104} h={28} fill={tint} name={`subject-${i}`} size={17}>{subject}</Tile><Arrow x={140} y={y+5} w={56} start={start} duration={10}/><Tile x={208} y={y} w={104} h={28} fill={tint} start={start+12} name={`verb-${i}`} size={17}>{words.join(' ')}</Tile>
    </React.Fragment>;})}
  </PageMotion></Sequence>
  {examples.map((item,i)=><Sequence key={item.en} from={450+i*270} durationInFrames={270} layout="none"><PageMotion duration={270}><Count i={i}/><Text y={81} size={14} name="verb-use-heading" tint={color.inkMuted}>Le verbe dans une vraie phrase.</Text><Text y={137} h={40} size={item.en.length>21?26:30} display start={15} name="verb-example">{item.en}</Text><Translation text={item.fr} y={202} start={40} name="verb-example-fr" size={17}/><Text y={272} size={15} start={125} name="verb-note" tint={color.ink2}>{item.note}</Text></PageMotion></Sequence>)}
  </>;
};

export const OppositeView=({firstReveal=210,rowFrames=90,answerDelay=12,pauseAt=60,centeredConnectors=false}:{firstReveal?:number;rowFrames?:number;answerDelay?:number;pauseAt?:number;centeredConnectors?:boolean}={})=>{
  const content=useLessonContent();
  const f=useCurrentFrame();return <>
    <Tile x={20} y={18} w={126} h={30} fill={color.lavender} size={15} name="opposite-label">Un mot</Tile><Tile x={190} y={18} w={126} h={30} fill={color.mint} size={15} name="opposite-answer-label">Son opposé</Tile>
    {content.opposites.map(([a,b],i)=>{const start=firstReveal+i*rowFrames;const active=f>=start&&f<start+rowFrames;return <React.Fragment key={a}>
      <div style={{position:'absolute',left:20,top:60+i*25,width:296,height:25,borderRadius:8,background:color.lemon,opacity:active?.4:0}}/><Text x={20} y={60+i*25} w={126} h={25} size={17} name={`opposite-a-${i}`}>{a}</Text>{centeredConnectors?<PairConnector row={i} start={start}/>:<Arrow x={154} y={64+i*25} w={28} start={start} double/>}<Text x={190} y={60+i*25} w={126} h={25} size={17} start={start+answerDelay} name={`opposite-b-${i}`}>{b}</Text>
    </React.Fragment>;})}<Pause start={pauseAt} end={firstReveal}/>
  </>;
};

export const MemoView=()=>{
  const content=useLessonContent();
  const f=useCurrentFrame();return <>{content.associations.map((item,i)=>{const start=30+390*i,top=18+i*104;return <React.Fragment key={item.verb}>
    <div style={{position:'absolute',left:18,top,width:300,height:94,borderRadius:18,background:f>=start&&f<start+300?fills[i]:color.surface,border:`1px solid ${color.line}`,...reveal(f,start,8,12)}}/>
    <Text y={top+7} size={25} display start={start+15} name={`memo-en-${i}`}>{item.verb} {item.rest}</Text><Translation text={item.fr} y={top+37} start={start+40} name={`memo-fr-${i}`} size={14}/><Text y={top+69} h={22} size={15} start={start+185} name={`memo-example-${i}`}>{item.en}</Text>
  </React.Fragment>;})}</>;
};

export const PhrasalPage=({i}:{i:number})=>{
  const content=useLessonContent();
  const f=useCurrentFrame(),item=content.phrasal[i],action=tween(f,100,60);
  return <><Count i={i}/><Tile x={62} y={69} w={94} h={39} fill={color.lavender} name="phrasal-base" size={25}>{item.base}</Tile><Tile x={180} y={69} w={94} h={39} fill={color.lemon} start={55} name="phrasal-particle" size={25}>{item.particle}</Tile>
    <svg width="284" height="101" viewBox="0 0 284 101" style={{position:'absolute',left:26,top:133}} fill="none" stroke={color.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      {item.kind==='bus'?<><rect x="45" y="8" width="177" height="68" rx="14" fill={color.lemon}/><path d="M59 22H170V44H59Z" fill={color.sheet}/><path d="M96 22V44M133 22V44"/><rect x="187" y="21" width="22" height="54" rx="3" fill={color.sheet}/><circle cx="76" cy="77" r="11" fill={color.ink}/><circle cx="184" cy="77" r="11" fill={color.ink}/><path d="M199 38V92H256M248 84l8 8-8 8" stroke={color.violet} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-action}/></>:item.kind==='bag'?<><path d="M35 91H245" stroke={color.line}/><g transform={`translate(0 ${-action*38})`}><path d="M103 44H167L174 89H96Z" fill={color.lemon}/><path d="M120 44V31Q135 13 150 31V44"/></g><path d="M202 80V20M194 28l8-8 8 8" stroke={color.violet} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-action}/></>:<><path d="M47 21H88V43H129V65H170V87H225"/><path d="M109 12L228 79M218 76l10 3-3-10" stroke={color.violet} strokeWidth="3" pathLength="1" strokeDasharray="1" strokeDashoffset={1-action}/></>}
    </svg><Text y={245} size={26} display start={140} name="phrasal-expression">{item.phrase}</Text><Translation text={item.fr} y={282} start={175} name="phrasal-fr" size={17}/>
  </>;
};
