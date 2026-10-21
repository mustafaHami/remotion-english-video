import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {Card, Decor, Icon, SafeContent, Sheet, Stage, Tag} from '../components/LessonPrimitives';
import {Options, Sentence, SentenceData, Timer} from '../components/QuizComponents';
import {EndCard, TipColumns, TipColumnData} from '../components/TipAndEnd';
import {color} from '../design/tokens';
import {loadDesignFonts, type} from '../design/typography';
import {progress, reveal, swipe} from '../design/motion';

export type GapQuizData = {
  tag: string; hookLines: readonly string[]; hookLead: string; topicLines: readonly string[];
  sentence: SentenceData; choices: readonly string[]; hintLines: readonly string[]; feedbackLines: readonly string[];
  tipTag: string; tipTitleLines: readonly string[]; tipColumns: readonly TipColumnData[]; tipNoteLines: readonly string[];
  endLines: readonly string[]; endLeadLines: readonly string[]; next: {meta: string; teaser: string};
  timing: {question: number; timer: number; answer: number; success: number; tip: number; end: number};
};
const Lines: React.FC<{lines: readonly string[]}> = ({lines}) => <>{lines.map((line,i)=><React.Fragment key={line}>{i>0?<br/>:null}{line}</React.Fragment>)}</>;

export const GapQuiz: React.FC<{data: GapQuizData}> = ({data}) => {
  loadDesignFonts();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const firstSwipe = swipe(frame,data.timing.tip,fps), lastSwipe = swipe(frame,data.timing.end,fps);
  const hookOut = 1-progress(frame,52,6);
  return <Stage>
    {firstSwipe<1 ? <Card background={color.lavender} y={-640*firstSwipe}>
      <Decor frame={frame} circle={frame<60?[322,112,64,.22]:[330,96,58,.22]} sparks={frame<60?[[300,230,16],[28,265,11]]:frame<150?[[320,198,13]]:frame>=240?[[320,202,16]]:[]}/>
      <Sheet top={330-140*swipe(frame,data.timing.question,fps)}/>
      <SafeContent offset={-640*firstSwipe}>
      <Tag>{data.tag}</Tag>
      {frame<60 ? <div style={{opacity:hookOut, transform:`translateY(${-8*(1-hookOut)}px)`}}>
        <div style={{position:'absolute',left:20,top:96,width:320,...type.hookTitle}}>{data.hookLines.map((line,i)=><div data-safe={`hook-${i}`} key={line} style={reveal(frame,i*4)}>{line}</div>)}</div>
        <div data-safe="hook-lead" style={{position:'absolute',left:20,top:189,...type.lead,...reveal(frame,10,8)}}>{data.hookLead}</div>
        <div data-safe="hook-pair" style={{position:'absolute',left:20,top:370,width:280,display:'flex',alignItems:'center',justifyContent:'space-between',...reveal(frame,18,10)}}>
          <span style={type.tipHeading}>make</span><span style={type.coverJoin}>ou</span><span style={type.tipHeading}>do ?</span>
        </div>
      </div> : <>
        <div data-safe="quiz-topic" style={{...type.hookTitle, position:'absolute',left:20,top:98,width:206,...reveal(frame,60)}}><Lines lines={data.topicLines}/></div>
        <Sentence frame={frame} data={data.sentence} answerAt={data.timing.answer}/>
        <div data-safe="translation" style={{...type.translation,position:'absolute',left:20,top:316,width:280,...reveal(frame,76,8)}}><Lines lines={data.sentence.translationLines}/></div>
        <Options frame={frame} choices={data.choices} answer={data.sentence.answer} successAt={data.timing.success}/>
        {frame>=data.timing.timer && frame<data.timing.answer+6 ? <Timer frame={frame} start={data.timing.timer} end={240}/> : null}
        {frame>=160 && frame<246 ? <div data-safe="hint" style={{position:'absolute',left:20,top:470,width:280,display:'flex',alignItems:'flex-start',gap:8,...reveal(frame,160,8),opacity:progress(frame,160,8)*(1-progress(frame,240,6))}}><Icon name="comment" size={18}/><div style={type.hint}><Lines lines={data.hintLines}/></div></div> : null}
        {frame>=256 ? <div data-safe="feedback" style={{...type.feedback,position:'absolute',left:20,top:470,width:280,display:'flex',alignItems:'flex-start',gap:8,...reveal(frame,256,8)}}><Icon name="check" size={18} stroke={3.4} tint={color.success}/><div><Lines lines={data.feedbackLines}/></div></div> : null}
      </>}
      </SafeContent>
    </Card> : null}
    {frame>=data.timing.tip && lastSwipe<1 ? <Card background={color.lemon} y={640*(1-firstSwipe)-640*lastSwipe}>
      <Decor frame={frame} circle={[326,92,60,.3]} sparks={[[306,189,13]]}/>
      <Sheet top={230}/><SafeContent offset={640*(1-firstSwipe)-640*lastSwipe}><Tag>{data.tipTag}</Tag>
      <div data-safe="tip-title" style={{...type.hookTitle,position:'absolute',left:20,top:104,width:280}}><Lines lines={data.tipTitleLines}/></div>
      <TipColumns frame={frame} columns={data.tipColumns}/>
      <div data-safe="tip-note" style={{...type.meta,position:'absolute',left:20,top:194,width:280,...reveal(frame,358,6)}}><Lines lines={data.tipNoteLines}/></div>
      </SafeContent>
    </Card> : null}
    {frame>=data.timing.end ? <Card background={color.mint} y={640*(1-lastSwipe)}>
      <Decor frame={frame} circle={[318,250,70,.22]} sparks={[[304,126,16],[30,250,11]]}/>
      <Sheet top={300}/>
      <SafeContent offset={640*(1-lastSwipe)}>
      <div style={{...type.endTitle,position:'absolute',left:20,top:56,width:320}}>{data.endLines.map((line,i)=><div key={line} data-safe={`end-title-${i}`} style={reveal(frame,420+i*4)}>{line}</div>)}</div>
      <div data-safe="end-lead" style={{...type.leadEnd,position:'absolute',left:20,top:158,width:280,...reveal(frame,430,8)}}><Lines lines={data.endLeadLines}/></div>
      <EndCard frame={frame} {...data.next}/>
      </SafeContent>
    </Card> : null}
  </Stage>;
};
