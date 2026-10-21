import React from 'react';
import {TenseWorksheet} from '../../../templates/TenseWorksheet';
import {QualityProbe} from '../test-style-v1/QualityProbe';
import {optionOne} from './data';
import paths from './writing-paths.json';

/** Approved style base; the original option 1 remains available for comparison. */
export const TestOptionOne:React.FC=()=><><TenseWorksheet data={optionOne} paths={paths}/><QualityProbe swipeStarts={[]} top={64} bottom={516} right={336}/></>;
