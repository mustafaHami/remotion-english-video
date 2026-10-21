import React from 'react';
import {FastGapLesson} from '../options-v6/Composition';
import config from './render-config.json';
import manifest from './voice-manifest.json';
export const CourseV11:React.FC<{testKey:string}>=()=> <FastGapLesson item={config[0]} clips={manifest['4']} refinedMascot/>;
