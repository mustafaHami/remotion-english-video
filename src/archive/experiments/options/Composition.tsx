import React from 'react';
import {PronounBoard,OppositeBoard,ContrastBoard,AssociationBoard,DialogueBoard,MemoBoard} from '../../../templates/OptionBoards';
import {GapExercise,SituationExercise,CorrectionExercise,RecallExercise,TransferExercise,PhrasalExercise} from '../../../templates/OptionExercises';
import {ListeningExercise} from '../../../templates/OptionListening';
import {QualityProbe} from '../test-style-v1/QualityProbe';

const views:Record<number,React.FC>={2:PronounBoard,3:OppositeBoard,4:GapExercise,5:SituationExercise,6:ContrastBoard,7:AssociationBoard,8:CorrectionExercise,9:DialogueBoard,10:ListeningExercise,11:RecallExercise,12:TransferExercise,13:MemoBoard,14:PhrasalExercise};
/** Style base approved; these individual exercises remain test compositions. */
export const OptionComposition:React.FC<{option:number}>=({option})=>{
  const View=views[option];if(!View)throw new Error(`Unknown test option ${option}`);
  return <><View/><QualityProbe swipeStarts={[]} top={64} bottom={516} right={348}/></>;
};
