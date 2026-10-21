import React from 'react';
import {useCurrentFrame} from 'remotion';
import {OptionScene,Text,Tile,Pause,Arrow,Translation,bodyStyle} from '../components/OptionPrimitives';
import {color} from '../design/tokens';
import {progress,reveal,tween} from '../design/motion';
import {optionData as d} from '../archive/experiments/options/data';

export const PronounBoard=()=>{
  const f=useCurrentFrame();const done=f>=650;
  return <OptionScene title="To be, au présent." completeAt={650} guide={f<210?'Associe chaque pronom à sa forme.':done?'Sept pronoms, trois formes.':'Suis les flèches, une à une.'}>
    <Tile x={24} y={18} w={104} h={30} fill={color.lavender} name="pronoun-label" size={15}>Pronom</Tile>
    <Tile x={208} y={18} w={104} h={30} fill={color.lemon} name="verb-label" size={15}>To be</Tile>
    {d.pronouns.map((row,i)=>{
      const start=210+i*60;const y=61+i*35;const tint=row.verb==='am'?color.lavender:row.verb==='is'?color.lemon:color.mint;
      return <React.Fragment key={row.subject}>
        <Tile x={24} y={y} w={104} h={28} fill={tint} start={30+i*3} size={17} name={`subject-${i}`}>{row.subject}</Tile>
        <Arrow x={140} y={y+5} w={56} start={start}/>
        {f<start+16?<div style={{position:'absolute',left:248,top:y+16,width:24,borderTop:`2px solid ${color.line}`}}/>:null}
        <Tile x={208} y={y} w={104} h={28} fill={tint} start={start+16} size={17} name={`form-${i}`}>{row.verb}</Tile>
      </React.Fragment>;
    })}
    <Pause start={60} end={210}/>
  </OptionScene>;
};

export const OppositeBoard=()=>{
  const f=useCurrentFrame();return <OptionScene title="Trouve les opposés." completeAt={940} guide={f<210?'Cherche les dix mots manquants.':f<940?'Un mot, puis son contraire.':'Relis les dix paires.'}>
    <Tile x={20} y={18} w={126} h={30} fill={color.lavender} size={15} name="left-label">Un mot</Tile>
    <Tile x={190} y={18} w={126} h={30} fill={color.mint} size={15} name="right-label">Son opposé</Tile>
    <div style={{position:'absolute',left:20,top:60,width:126,height:250,borderRadius:12,background:color.lavender,opacity:.12}}/>
    <div style={{position:'absolute',left:190,top:60,width:126,height:250,borderRadius:12,background:color.mint,opacity:.2}}/>
    {d.opposites.map(([a,b],i)=>{
      const start=210+i*78;const active=f>=start&&f<start+78&&f<940;
      return <React.Fragment key={a}>
        <div style={{position:'absolute',left:20,top:60+i*25,width:296,height:25,borderRadius:8,background:color.lemon,opacity:active?.4:0}}/>
        <Text x={20} y={60+i*25} w={126} h={25} size={17} start={25+i*2} name={`opposite-a-${i}`}>{a}</Text>
        <Arrow x={154} y={64+i*25} w={28} start={start} double/>
        <Text x={190} y={60+i*25} w={126} h={25} size={17} start={start+12} name={`opposite-b-${i}`}>{b}</Text>
        {f<start+12?<div style={{position:'absolute',left:241,top:76+i*25,width:24,height:2,background:color.line}}/>:null}
      </React.Fragment>;
    })}
    <Pause start={60} end={210}/>
  </OptionScene>;
};

export const ContrastBoard=()=>{
  const f=useCurrentFrame();return <OptionScene title="Say ou tell ?" completeAt={600} guide={f<300?'Observe les deux constructions.':f<600?'Avec tell, on nomme ici la personne.':'Retiens ces deux usages.'}>
    <Tile x={24} y={22} w={104} h={30} fill={color.lavender} name="say-label" size={17}>say</Tile>
    <Text y={66} size={25} display start={60} name="said-phrase">She <span style={{background:color.lavender,borderRadius:7,padding:'0 5px'}}>said</span> hello.</Text>
    <Translation text={d.contrast.firstFr} y={107} start={100} name="said-fr"/>
    <div style={{position:'absolute',left:24,right:24,top:153,height:1,background:color.line}}/>
    <Tile x={24} y={174} w={104} h={30} fill={color.lemon} start={210} name="tell-label" size={17}>tell</Tile>
    <Text y={219} size={24} display start={250} name="told-phrase">She told <span style={{borderRadius:7,padding:'0 5px',background:f>=360?color.lemon:'transparent'}}>me</span> a story.</Text>
    <Translation text={d.contrast.secondFr} y={262} start={300} name="told-fr"/>
    <Text y={301} h={22} size={13} tint={color.ink2} start={390} name="recipient">me = la personne à qui elle raconte</Text>
    <svg width="336" height="342" style={{position:'absolute',inset:0,pointerEvents:'none'}} aria-hidden><path d="M105 248V253H199V248" fill="none" stroke={color.ink} strokeWidth="1.5" pathLength="1" strokeDasharray="1" strokeDashoffset={1-tween(f,360,22)} opacity={progress(f,360,8)}/></svg>
  </OptionScene>;
};

export const AssociationBoard=()=>{
  const f=useCurrentFrame();return <OptionScene title="Ces mots vont ensemble." completeAt={620} guide={f<210?'Retiens les groupes complets.':f<510?'Les mots se rejoignent.':'Deux associations à mémoriser.'}>
    {d.collocations.map((item,i)=>{
      const top=54+i*151,start=i===0?150:420;const joined=tween(f,start,24);const base=i===0?color.lavender:color.lemon;
      return <React.Fragment key={item.verb}>
        <Text y={top-31} size={13} tint={color.inkMuted} start={i===0?30:300} name={`association-number-${i}`}>0{i+1}</Text>
        <Tile x={30+18*joined} y={top} w={108} h={48} start={i===0?40:310} fill={base} name={`association-verb-${i}`} size={24}>{item.verb}</Tile>
        <Tile x={198-18*joined} y={top} w={108} h={48} start={i===0?65:335} name={`association-rest-${i}`} size={23}>{item.rest}</Tile>
        <Text x={142} y={top+8} w={52} h={32} size={23} start={i===0?80:350} name={`association-plus-${i}`} style={{opacity:progress(f,i===0?80:350,10)*(1-joined)}}>+</Text>
        <div style={{position:'absolute',left:156,top:top+18,width:24,height:13,borderRadius:99,background:base,border:`2px solid ${color.ink}`,boxSizing:'border-box',opacity:joined}}/>
        <Translation text={item.translation} y={top+63} start={start+30} name={`association-fr-${i}`}/>
      </React.Fragment>;
    })}
  </OptionScene>;
};

export const DialogueBoard=()=>{
  const f=useCurrentFrame();return <OptionScene title="Une demande, une réponse." completeAt={500} guide={f<270?'Imagine une réponse naturelle.':f<500?'Lis la réponse dans son contexte.':'Un échange prêt à réutiliser.'}>
    <Text y={22} size={14} tint={color.inkMuted} name="dialogue-label">Demander un service</Text>
    {d.dialogue.map((line,i)=>{
      const start=i===0?45:270;const top=75+i*128;
      return <React.Fragment key={line.en}>
        <div style={{position:'absolute',left:20,top,width:296,height:54,borderRadius:i===0?'19px 19px 19px 5px':'19px 19px 5px 19px',background:i===0?color.lavender:color.lemon,boxShadow:`0 3px 0 ${color.ledge}`,...reveal(f,start,10,14)}}/>
        <Text x={24} w={288} y={top+12} size={19} start={start+4} name={`dialogue-${i}`}>{line.en}</Text>
        <Translation text={line.fr} y={top+64} size={14} start={start+36} name={`dialogue-fr-${i}`}/>
      </React.Fragment>;
    })}
    <Pause start={105} end={270}/>
  </OptionScene>;
};

const MemoIcon:React.FC<{kind:'favor'|'cake';x:number;y:number;start:number}>=({kind,x,y,start})=>{
  const f=useCurrentFrame();return <svg width="58" height="58" viewBox="0 0 58 58" style={{position:'absolute',left:x,top:y,...reveal(f,start,8,12)}} fill="none" stroke={color.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
    <circle cx="29" cy="29" r="27" fill={kind==='favor'?color.lavender:color.lemon} stroke="none"/>
    {kind==='cake'?<><path d="M14 28H44V43H14Z" fill={color.sheet}/><path d="M14 31Q19 38 24 31Q29 38 34 31Q39 38 44 31M29 28V19"/><path d="M29 12Q22 18 29 19Q36 18 29 12Z" fill={color.coral}/></>:<><path d="M12 33H19L25 25Q30 21 31 26L28 31H42Q47 31 45 35L40 43H24L19 40H12Z" fill={color.sheet}/><path d="M12 31V43M29 13V18M17 17L21 21M41 17L37 21"/></>}
  </svg>;
};

export const MemoBoard=()=>{
  const f=useCurrentFrame();return <OptionScene title="Deux expressions à garder." completeAt={540} guide={f<540?'Une fiche qui se construit sous tes yeux.':'Garde les expressions complètes.'}>
    <Text y={18} size={14} tint={color.inkMuted} name="memo-heading">Un petit mémo utile</Text>
    {d.collocations.map((item,i)=>{
      const start=i===0?60:300;const top=73+i*139;
      return <React.Fragment key={item.verb}>
        <div style={{position:'absolute',left:20,top:top-12,width:296,height:110,borderRadius:18,border:`1px solid ${color.line}`,background:color.surface,...reveal(f,start,10,12)}}/>
        <MemoIcon kind={i===0?'favor':'cake'} x={32} y={top+8} start={start+12}/>
        <Text x={100} y={top+5} w={204} size={25} display start={start+30} name={`memo-en-${i}`}>{item.verb} {item.rest}</Text>
        <Text x={100} y={top+43} w={204} size={15} tint={color.violet} start={start+65} name={`memo-fr-${i}`}>{item.translation}</Text>
      </React.Fragment>;
    })}
  </OptionScene>;
};
