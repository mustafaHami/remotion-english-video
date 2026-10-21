import React from 'react';
import {Sequence} from 'remotion';
import {OptionScene} from '../../../components/OptionPrimitives';
import {FrontalFoxMascot} from '../../../components/FrontalFoxMascot';
import {Bookend} from '../options-v5/Composition';
import {OppositeView} from '../options-v3/Views';
import {NarrationTrack} from '../options-v3/Composition';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import config from './render-config.json';
import manifest from './voice-manifest.json';
export const CourseV9:React.FC<{testKey:string}>=()=>{
 const item=config[0],end=item.introFrames+item.bodyFrames;
 return <><Sequence durationInFrames={item.introFrames}><Bookend title={item.title} mascot={<FrontalFoxMascot/>}/></Sequence>
  <Sequence from={item.introFrames} durationInFrames={item.bodyFrames}><OptionScene title={item.title} guide="Trouve, puis écoute chaque paire." completeAt={item.bodyFrames-90} quietDecor><OppositeView firstReveal={item.firstReveal} rowFrames={item.rowFrames} answerDelay={0} pauseAt={30} centeredConnectors/></OptionScene></Sequence>
  <Sequence from={end} durationInFrames={item.outroFrames}><Bookend title={item.title} end farewellAt={90} mascot={<FrontalFoxMascot end/>}/></Sequence>
  <NarrationTrack clips={manifest['3']}/><QualityProbe top={64} bottom={516} right={348} swipeStarts={[]}/>
 </>;
};
