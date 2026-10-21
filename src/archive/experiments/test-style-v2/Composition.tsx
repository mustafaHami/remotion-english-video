import React from 'react';
import {DeclicLesson} from '../../../templates/DeclicLesson';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import {declicData,Platform} from './data';

export const TestStyleV2:React.FC<{platform:Platform}> = ({platform})=><><DeclicLesson data={declicData} platform={platform}/><QualityProbe swipeStarts={[300,450,600]} top={64} bottom={508}/></>;
