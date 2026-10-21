import React from 'react';
import {Sequence} from 'remotion';
import {OptionScene} from '../../../components/OptionPrimitives';
import {GapPage,PageMotion} from '../options-v3/Views';
import {NarrationTrack} from '../options-v3/Composition';
import {FrontalFoxMascot} from '../../../components/FrontalFoxMascot';
import {Bookend} from '../options-v5/Composition';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import content from '../options-v3/content.json';
import config from './render-config.json';
import manifest from './voice-manifest.json';
export const FastGapLesson:React.FC<{item:typeof config[0];clips:typeof manifest['4'];refinedMascot?:boolean}>=({item,clips,refinedMascot=false})=>{
 const end=item.introFrames+item.bodyFrames;
 return <>
  <Sequence durationInFrames={item.introFrames}><Bookend title={item.title} staticMascot={refinedMascot} mascot={refinedMascot?<FrontalFoxMascot refinedMotion/>:undefined}/></Sequence>
  <Sequence from={item.introFrames} durationInFrames={item.bodyFrames}>
   <OptionScene title="Trois phrases à compléter." guide="Cherche, puis écoute la réponse." completeAt={item.bodyFrames-60} success quietDecor>
    {content.gap.map((gap,i)=><Sequence key={i} from={i*item.pageFrames} durationInFrames={item.pageFrames} layout="none"><PageMotion duration={item.pageFrames}><GapPage i={i} item={gap} timing={{answerAt:item.answerAt,pauseAt:item.pauseAt,choicesAt:18,noteAt:item.answerAt+6}}/></PageMotion></Sequence>)}
   </OptionScene>
  </Sequence>
  <Sequence from={end} durationInFrames={item.outroFrames}><Bookend title={item.title} end farewellAt={90} staticMascot={refinedMascot} mascot={refinedMascot?<FrontalFoxMascot end refinedMotion/>:undefined}/></Sequence>
  <NarrationTrack clips={clips}/>
  <QualityProbe top={64} bottom={516} right={348} swipeStarts={[]}/>
 </>;
};

export const CourseV6:React.FC<{testKey:string}>=()=> <FastGapLesson item={config[0]} clips={manifest['4']}/>;
