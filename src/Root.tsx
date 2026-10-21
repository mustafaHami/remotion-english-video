import React from 'react';
import {Composition,Folder} from 'remotion';
import {ProductionLesson} from './options/ProductionLesson';
import {lessons} from './options/catalog';
export const Root:React.FC=()=> <Folder name="Options">
 {lessons.map(lesson=><Composition key={lesson.option} id={`Option${lesson.option}`} component={ProductionLesson} defaultProps={{lesson}} durationInFrames={lesson.timing.introFrames+lesson.timing.bodyFrames+lesson.timing.outroFrames} calculateMetadata={({props})=>({durationInFrames:props.lesson.timing.introFrames+props.lesson.timing.bodyFrames+props.lesson.timing.outroFrames})} fps={30} width={1080} height={1920}/>)}
</Folder>;
