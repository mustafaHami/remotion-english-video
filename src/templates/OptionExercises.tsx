import React from 'react';
import {useCurrentFrame} from 'remotion';
import {OptionScene,Text,Tile,Pause,Translation,Receipt,displayStyle} from '../components/OptionPrimitives';
import {Icon} from '../components/LessonPrimitives';
import {color} from '../design/tokens';
import {progress,reveal,tween} from '../design/motion';
import {optionData as d} from '../archive/experiments/options/data';

export const GapExercise=()=>{
  const f=useCurrentFrame();const answer=f>=300;
  return <OptionScene title="Un mot change tout." completeAt={470} success guide={f<300?'Prends le temps de choisir.':f<470?'L’expression : do someone a favor.':'do a favor = rendre un service'}>
    <Text y={26} size={14} tint={color.inkMuted} name="gap-instruction">Quel verbe complète la phrase ?</Text>
    <Text y={99} h={38} size={20} start={35} name="gap-phrase">Can you <span style={{display:'inline-block',width:54,textAlign:'center',borderRadius:10,background:answer?color.successBg:'transparent',color:answer?color.success:color.ink,border:`2px ${answer?'solid':'dashed'} ${answer?color.success:color.coral}`,margin:'0 4px',lineHeight:'32px'}}>{answer?'do':'…'}</span> me a favor?</Text>
    <Translation text={d.gap.translation} y={154} start={65} name="gap-fr"/>
    {d.gap.choices.map((choice,i)=><Tile key={choice} x={34+i*140} y={222} w={128} h={46} start={85+i*8} correct={answer&&i===1} muted={answer&&i===0} name={`gap-choice-${i}`} size={21}>{choice}</Tile>)}
    <Pause start={120} end={300}/>
  </OptionScene>;
};

export const SituationExercise=()=>{
  const f=useCurrentFrame();const answer=f>=315;
  return <OptionScene title="L’addition, en anglais ?" completeAt={520} success guide={f<315?'Tu as fini ton repas. Que dis-tu ?':f<520?'The bill, please.':'bill = l’addition, au restaurant'}>
    <Receipt y={18} scale={.8}/>
    <Text y={116} size={16} start={40} name="situation-instruction">Choisis la phrase naturelle.</Text>
    {d.restaurant.choices.map((phrase,i)=><Tile key={phrase} x={26} y={168+i*62} w={284} h={46} start={65+i*10} correct={answer&&i===0} muted={answer&&i===1} name={`situation-choice-${i}`} size={20}>{phrase}</Tile>)}
    <Translation text={d.restaurant.translation} y={291} start={350} name="situation-fr"/>
    <Pause start={135} end={315}/>
  </OptionScene>;
};

export const CorrectionExercise=()=>{
  const f=useCurrentFrame();const moving=tween(f,240,32);const closing=tween(f,272,24);const check=tween(f,296,14);
  return <OptionScene title="Une petite correction." completeAt={400} success guide={f<240?'Un mot est en trop. Lequel ?':f<400?'agree est déjà un verbe.':'I agree. = Je suis d’accord.'}>
    <Text y={27} size={14} tint={color.inkMuted} name="correction-instruction">Repère le mot à retirer.</Text>
    <Text y={112} h={48} size={36} display start={35} name="correction-phrase" tint={f>=310?color.success:color.ink}>
      <span style={{display:'inline-flex',alignItems:'center'}}>
        <span style={{display:'inline-flex',alignItems:'center',width:34*check,overflow:'hidden',opacity:check}}><Icon name="check" size={24} tint={color.success} stroke={3}/></span>
        <span style={{marginRight:8}}>I</span>
        <span style={{display:'inline-block',width:68*(1-closing),opacity:1-moving,transform:`translateY(${-24*moving}px)`,overflow:'hidden',whiteSpace:'nowrap',lineHeight:'42px',borderBottom:`2px dashed ${color.coral}`,boxSizing:'border-box'}}>am</span>
        <span>agree.</span>
      </span>
    </Text>
    <Translation text={d.correction.translation} y={187} start={330} name="correction-fr" size={18}/>
    <Text y={268} size={15} tint={color.ink2} start={350} name="agree-explanation">Pas besoin de am avec agree.</Text>
    <Pause start={90} end={240}/>
  </OptionScene>;
};

export const RecallExercise=()=>{
  const f=useCurrentFrame();return <OptionScene title="À toi de le dire." completeAt={430} success guide={f<300?'Cherche la phrase, sans choix proposés.':f<430?'Une formulation possible.':'Could you help me?'}>
    <Text y={27} size={14} tint={color.inkMuted} name="recall-context">Pour demander de l’aide poliment</Text>
    <Text y={91} size={24} display tint={color.violet} start={40} name="recall-prompt">{d.recall.prompt}</Text>
    {f<300?<><div style={{position:'absolute',left:32,top:170,width:272,height:64,border:`2px dashed ${color.coral}`,borderRadius:18,boxSizing:'border-box'}}/><Text y={188} size={24} name="recall-empty">…</Text></>:<Tile x={24} y={170} w={288} h={64} size={24} correct start={300} name="recall-answer">{d.recall.answer}</Tile>}
    <Text y={267} size={14} tint={color.ink2} start={350} name="recall-note">D’autres réponses sont possibles.</Text>
    <Pause start={120} end={300}/>
  </OptionScene>;
};

export const TransferExercise=()=>{
  const f=useCurrentFrame();const question=f>=270;const answer=f>=570;
  return <OptionScene title="Et dans cette phrase ?" completeAt={640} success guide={!question?'D’abord, retiens ce groupe.':!answer?'Un nouvel essai, sans choix.':'Même verbe, une autre association.'}>
    <Text y={24} size={14} tint={color.inkMuted} name="transfer-heading">{question?'À toi de réutiliser do':'Une première association'}</Text>
    <div style={{opacity:question?.45:1}}><Tile x={50} y={77} w={236} h={48} fill={color.lavender} start={45} name="transfer-seed" size={25}>{d.transfer.first}</Tile><Translation text="rendre un service" y={140} start={90} name="transfer-seed-fr"/></div>
    {question?<>
      <Text y={208} size={25} display start={280} name="transfer-question" tint={answer?color.success:color.ink}>{answer?d.transfer.answer:d.transfer.prompt}</Text>
      <Translation text={d.transfer.translation} y={254} start={310} name="transfer-fr"/>
      {answer?<Text y={296} h={22} size={14} tint={color.success} start={590} name="transfer-check"><span style={{display:'inline-flex',alignItems:'center',gap:5}}><Icon name="check" size={15} tint={color.success}/>do my homework</span></Text>:null}
    </>:null}
    <Pause start={390} end={570}/>
  </OptionScene>;
};

export const PhrasalExercise=()=>{
  const f=useCurrentFrame();const off=tween(f,180,24);const out=tween(f,270,60);
  return <OptionScene title="Get + off : un autre sens." completeAt={550} guide={f<180?'Observe ce qui change avec off.':f<550?'Apprends le groupe dans son contexte.':'get off the bus = descendre du bus'}>
    <Tile x={51+15*off} y={24} w={88} h={42} fill={color.lavender} start={25} name="get-base" size={25}>get</Tile>
    <Text x={143} y={30} w={50} size={22} start={80} name="phrasal-plus" style={{opacity:progress(f,80,10)*(1-off)}}>+</Text>
    <Tile x={197-15*off} y={24} w={88} h={42} fill={color.lemon} start={120} name="off-particle" size={25}>off</Tile>
    <svg width="300" height="132" viewBox="0 0 300 132" style={{position:'absolute',left:18,top:98}} aria-hidden>
      <path d="M8 111H292" stroke={color.line} strokeWidth="2"/>
      <rect x="48" y="12" width="202" height="83" rx="17" fill={color.lemon} stroke={color.ink} strokeWidth="2"/>
      <path d="M65 28H194V56H65Z" fill={color.sheet} stroke={color.ink} strokeWidth="2"/>
      {[105,148].map(x=><path key={x} d={`M${x} 28V56`} stroke={color.ink} strokeWidth="2"/>)}
      <rect x="207" y="30" width="27" height="63" rx="4" fill={color.sheet} stroke={color.ink} strokeWidth="2"/>
      <circle cx="85" cy="96" r="13" fill={color.ink}/><circle cx="85" cy="96" r="5" fill={color.sheet}/><circle cx="206" cy="96" r="13" fill={color.ink}/><circle cx="206" cy="96" r="5" fill={color.sheet}/>
      <path d="M221 48V109H272M265 102l7 7-7 7" fill="none" stroke={color.violet} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" pathLength="1" strokeDasharray="1" strokeDashoffset={1-out} opacity={progress(f,270,8)}/>
      <circle cx={221+51*Math.max(0,(out-.55)/.45)} cy={48+61*Math.min(1,out/.55)} r="5" fill={color.violet} opacity={progress(f,270,8)}/>
    </svg>
    <Text y={249} size={28} display start={225} name="phrasal-full">{d.phrasal.phrase}</Text>
    <Translation text={d.phrasal.translation} y={293} start={350} name="phrasal-fr" size={17}/>
  </OptionScene>;
};
