import React from 'react';
import {Sequence,useCurrentFrame} from 'remotion';
import {OptionScene} from '../../../components/OptionPrimitives';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import {NarrationTrack} from '../options-v3/Composition';
import {Pages,PageMotion,GapPage,DialoguePage} from '../options-v3/Views';
import content from '../options-v3/content.json';
import config from './render-config.json';
import manifest from './voice-manifest.json';

export const CourseV4:React.FC<{testKey:string;probe?:boolean}>=({testKey,probe=true})=>{
  const f=useCurrentFrame();
  const item=config.find(c=>c.key===testKey);
  if(!item)throw new Error(`Unknown voice test: ${testKey}`);
  const isGap=item.option===4;
  const clips=testKey==='4'?manifest['4']:manifest['9'];
  return <><OptionScene title={item.title} completeAt={item.completeAt} success={isGap} quietDecor
    guide={isGap?(f<item.introEnd?'Écoute la consigne, puis choisis.':'Cherche, puis écoute la réponse.'):'Deux voix, huit répliques au travail.'}>
    {isGap?content.gap.map((gap,i)=>{
      const delay=i===0?item.questionDelay:0;
      const duration=420+delay;
      return <Sequence key={i} from={i*420+(i>0?item.questionDelay:0)} durationInFrames={duration} layout="none"><PageMotion duration={duration}><GapPage item={gap} i={i} thinkingDelay={delay}/></PageMotion></Sequence>;
    }):<Pages count={4} duration={315}>{i=><DialoguePage i={i}/>}</Pages>}
  </OptionScene><NarrationTrack clips={clips}/>{probe?<QualityProbe swipeStarts={[]} top={64} bottom={516} right={348}/>:null}</>;
};
