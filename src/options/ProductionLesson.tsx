import React from 'react';
import {Audio,Sequence,Freeze,staticFile,useCurrentFrame,interpolate} from 'remotion';
import {OptionScene} from '../components/OptionPrimitives';
import {Bookend} from '../components/MascotBookend';
import {QualityProbe} from '../components/RenderQualityProbe';
import {LessonContentContext,defaults,useLessonContent} from '../content/LessonContent';
import {TenseWorksheet} from '../templates/TenseWorksheet';
import * as Views from '../templates/LessonViews';
import defaultPaths from './option-1/writing-paths.json';
import type {LessonInput} from './types';

const QuizPage=({index,option}:{index:number;option:number})=>{
 const f=useCurrentFrame(),data=useLessonContent();
 const mapped=interpolate(f,[0,45,165,255],[0,60,210,420],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 let view:React.ReactNode;
 switch(option){
  case 5:view=<Views.SituationPage i={index}/>;break;
  case 6:view=<Views.GapPage i={index} item={data.contrast[index]}/>;break;
  case 7:view=<Views.AssociationPage i={index}/>;break;
  case 8:view=<Views.CorrectionPage i={index}/>;break;
  case 11:view=<Views.RecallPage i={index}/>;break;
  case 12:view=<Views.RecallPage i={index} transfer/>;break;
  case 14:view=<Views.PhrasalPage i={index}/>;break;
  default:throw new Error(`Unsupported quiz option ${option}`);
 }
 return <Freeze frame={mapped}>{view}</Freeze>;
};
const LessonBody=({lesson}:{lesson:LessonInput})=>{
 const data=useLessonContent(),f=useCurrentFrame(),n=lesson.option,t=lesson.timing;
 const localClips=lesson.narration.filter(c=>c.role==='lesson').map(c=>({...c,start:c.start-t.introFrames}));
 if(n===1){
  const rows=data.rows;
  const events=[...rows.map((r,i)=>({column:1 as const,row:i,text:r.past,start:210+i*75,duration:36})),...rows.map((r,i)=>({column:2 as const,row:i,text:r.future,start:1140+i*60,duration:44}))];
  return <TenseWorksheet data={{title:lesson.title,columns:['Présent','Passé','Futur'],rows,events,waits:[{start:60,end:210},{start:990,end:1140}],futureAt:990,completeAt:1770,duration:1950}} paths={lesson.writingPaths??defaultPaths}/>;
 }
 let view:React.ReactNode;let guide='Cherche, puis écoute la réponse.';
 if(n===2){view=<Views.VerbView verb={lesson.verb??'be'}/>;guide='Un pronom, une forme, puis trois exemples.';}
 else if(n===3){view=<Views.OppositeView firstReveal={150} rowFrames={90} pauseAt={30} answerDelay={0} centeredConnectors/>;guide='Trouve, puis écoute chaque paire.';}
 else if(n===4)view=<Views.Pages duration={t.pageFrames}>{i=><Views.GapPage i={i} item={data.gap[i]} timing={{answerAt:165,pauseAt:45,choicesAt:18,noteAt:171}}/>}</Views.Pages>;
 else if(n===9){view=<Views.Pages count={4} duration={315}>{i=><Views.DialoguePage i={i}/>}</Views.Pages>;guide='Deux voix, huit répliques au travail.';}
 else if(n===10){view=<Views.Pages>{i=><Views.ListenPage i={i} clips={localClips}/>}</Views.Pages>;guide=f%420<150?'Écoute la phrase.':f%420<310?'Répète à voix haute.':'Réécoute pour comparer.';}
 else if(n===13){view=<Views.MemoView/>;guide='Lis, écoute, puis réutilise ces groupes.';}
 else view=<Views.Pages duration={255}>{i=><QuizPage index={i} option={n}/>}</Views.Pages>;
 return <OptionScene title={lesson.title} guide={guide} completeAt={t.bodyFrames-(n===3?90:90)} success={[4,5,6,8,11,12].includes(n)} quietDecor>{view}</OptionScene>;
};
export const ProductionLesson:React.FC<{lesson:LessonInput}>=({lesson})=>{
 const t=lesson.timing,end=t.introFrames+t.bodyFrames;
 return <LessonContentContext.Provider value={{...defaults,...lesson.lessonData}}>
  <Sequence durationInFrames={t.introFrames}><Bookend title={lesson.option===9?lesson.title:lesson.introText} farewellAt={90}/></Sequence>
  <Sequence from={t.introFrames} durationInFrames={t.bodyFrames}><LessonBody lesson={lesson}/></Sequence>
  <Sequence from={end} durationInFrames={t.outroFrames}><Bookend title={lesson.title} end farewellAt={90}/></Sequence>
  {lesson.narration.map((clip,i)=><Sequence key={i} from={clip.start} durationInFrames={clip.duration} layout="none"><Audio src={staticFile(clip.src)} volume={.85}/></Sequence>)}
  <QualityProbe top={64} bottom={516} right={348} swipeStarts={[]}/>
 </LessonContentContext.Provider>;
};
