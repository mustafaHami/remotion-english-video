import React from 'react';
import {Audio,Sequence,staticFile,useCurrentFrame} from 'remotion';
import {OptionScene} from '../../../components/OptionPrimitives';
import {TenseWorksheet} from '../../../templates/TenseWorksheet';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import {optionOne,WritingEvent} from '../test-option-1/data';
import paths from '../test-option-1/writing-paths.json';
import rawManifest from './voice-manifest.json';
import config from './render-config.json';
import content from './content.json';
import {Pages,GapPage,SituationPage,AssociationPage,CorrectionPage,DialoguePage,RecallPage,ListenPage,VerbView,OppositeView,MemoView,PhrasalPage} from './Views';

type VoiceClip={start:number;duration:number;src:string;text:string;peaks:number[]};
const manifest=rawManifest as Record<string,VoiceClip[]>;
const voicedWorksheet={...optionOne,events:[
  ...optionOne.rows.map((row,i):WritingEvent=>({column:1,row:i,text:row.past,start:210+i*75,duration:36})),
  ...optionOne.rows.map((row,i):WritingEvent=>({column:2,row:i,text:row.future,start:1140+i*60,duration:44})),
],waits:[{start:60,end:210},{start:990,end:1140}],futureAt:990,completeAt:1770,duration:1950};

export const NarrationTrack=({clips}:{clips:VoiceClip[]})=><>{clips.map((clip,i)=><Sequence key={i} from={clip.start} durationInFrames={clip.duration} layout="none"><Audio src={staticFile(clip.src)} volume={.85}/></Sequence>)}</>;

export const CourseV3:React.FC<{testKey:string;probe?:boolean}>=({testKey,probe=true})=>{
  const f=useCurrentFrame(),item=config.find(c=>c.key===testKey)!;const n=item.option;const clips=manifest[testKey]??[];
  let view:React.ReactNode;let title=item.title;let guide='Cherche, puis écoute la réponse.';let success=false;
  switch(n){
    case 1:view=<TenseWorksheet data={voicedWorksheet} paths={paths}/>;break;
    case 2:view=<VerbView verb={item.verb}/>;title=item.verb==='be'?'To be, en pratique.':item.verb==='have'?'To have, en pratique.':item.verb==='can'?'Can, en pratique.':'Could, dans le passé.';guide=f<450?'Un pronom, une forme. Écoute.':'Trois exemples pour l’utiliser.';break;
    case 3:view=<OppositeView/>;guide=f<210?'Trouve les dix mots manquants.':'Un mot, son contraire, leur prononciation.';break;
    case 4:view=<Pages>{i=><GapPage i={i} item={content.gap[i]}/>}</Pages>;title='Trois phrases à compléter.';success=true;break;
    case 5:view=<Pages>{i=><SituationPage i={i}/>}</Pages>;title='Trois phrases au restaurant.';success=true;break;
    case 6:view=<Pages>{i=><GapPage i={i} item={content.contrast[i]}/>}</Pages>;title='Say ou tell ? Trois usages.';success=true;break;
    case 7:view=<Pages>{i=><AssociationPage i={i}/>}</Pages>;title='Trois groupes à retenir.';guide='Les mots s’associent, puis se prononcent.';break;
    case 8:view=<Pages>{i=><CorrectionPage i={i}/>}</Pages>;title='Trois erreurs à corriger.';success=true;break;
    case 9:view=<Pages count={4} duration={315}>{i=><DialoguePage i={i}/>}</Pages>;title='Un échange au travail.';guide='Écoute un échange de huit répliques.';break;
    case 10:view=<Pages>{i=><ListenPage i={i} clips={clips}/>}</Pages>;title='Trois phrases à prononcer.';guide=f%420<150?'Écoute la phrase.':f%420<310?'Répète à voix haute.':'Réécoute pour comparer.';break;
    case 11:view=<Pages>{i=><RecallPage i={i}/>}</Pages>;title='Trois phrases à retrouver.';success=true;break;
    case 12:view=<Pages>{i=><RecallPage i={i} transfer/>}</Pages>;title='Un modèle, deux essais.';guide=f<420?'D’abord le modèle, puis à toi.':'Réutilise do dans un autre groupe.';success=true;break;
    case 13:view=<MemoView/>;title='Trois expressions à garder.';guide='Lis, écoute, puis réutilise ces groupes.';break;
    case 14:view=<Pages>{i=><PhrasalPage i={i}/>}</Pages>;title='Un petit mot change le sens.';guide='Trois verbes à particule en contexte.';break;
    default:throw new Error('Unknown V3 option');
  }
  return <>{n===1?view:<OptionScene title={title} guide={guide} completeAt={item.completeAt} success={success} quietDecor>{view}</OptionScene>}<NarrationTrack clips={clips}/>{probe?<QualityProbe swipeStarts={[]} top={64} bottom={516} right={348}/>:null}</>;
};
