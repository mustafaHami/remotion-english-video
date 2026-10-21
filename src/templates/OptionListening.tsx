import React from 'react';
import {Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {OptionScene,Text,Tile,Translation,Pause,SoundIcon} from '../components/OptionPrimitives';
import {color} from '../design/tokens';
import {optionData as d} from '../archive/experiments/options/data';
import wave from '../archive/experiments/options/audio-wave.json';

export const ListeningExercise=()=>{
  const f=useCurrentFrame();const speaking=d.listen.starts.find(start=>f>=start&&f<start+Math.ceil(wave.duration*30));
  const phase=f<210?0:f<420?1:2;
  const labels=['Écoute','À toi','Réécoute'];
  const playhead=speaking===undefined?0:(f-speaking)/(wave.duration*30);
  return <OptionScene title="Écoute, puis répète." completeAt={530} guide={phase===0?'Écoute la phrase une première fois.':phase===1?'Répète à voix haute.':'Compare avec la seconde écoute.'}>
    <div style={{position:'absolute',top:29,left:154}}><SoundIcon/></div>
    <Text y={96} size={31} display start={35} name="listen-phrase">{d.listen.phrase}</Text>
    <Translation text={d.listen.translation} y={146} start={65} name="listen-fr" size={16}/>
    <svg width="272" height="55" viewBox="0 0 272 55" style={{position:'absolute',left:32,top:197}} aria-hidden>
      {wave.peaks.map((v,i)=>{const h=4+v*45;return <rect key={i} x={i*4.5} y={(55-h)/2} width="2.5" height={h} rx="1.25" fill={speaking!==undefined&&i/60<=playhead?color.violet:color.line}/>;})}
      {speaking!==undefined?<path d={`M${Math.min(270,playhead*270)} 0V55`} stroke={color.violet} strokeWidth="1"/>:null}
    </svg>
    {labels.map((label,i)=><Tile key={label} x={20+i*101} y={277} w={94} h={33} fill={phase===i?color.lemon:color.surface} muted={phase!==i} name={`listen-step-${i}`} size={14}>{label}</Tile>)}
    <Pause start={210} end={420}/>
    {d.listen.starts.map(start=><Sequence key={start} from={start} durationInFrames={Math.ceil(wave.duration*30)} layout="none"><Audio src={staticFile(d.listen.audio)} volume={.85}/></Sequence>)}
  </OptionScene>;
};
