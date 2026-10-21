import React from 'react';
import {GapQuiz} from '../../../templates/GapQuiz';
import {testStyleV1} from './data';
import {QualityProbe} from './QualityProbe';

/** Expérience non validée. Aucun épisode destiné à la publication. */
export const TestStyleV1: React.FC = () => <><GapQuiz data={testStyleV1}/><QualityProbe/></>;
