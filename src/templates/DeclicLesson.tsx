import React from 'react';
import {useCurrentFrame,useVideoConfig} from 'remotion';
import {Card,Decor,Icon,SafeContent,Stage} from '../components/LessonPrimitives';
import {ChapterRail,CompactOptions,CountdownStrip,InlineSentence,LessonTicket,PairRow,SingleLine} from '../components/DeclicComponents';
import {color} from '../design/tokens';
import {editorial as e} from '../design/editorial';
import {loadDesignFonts,type} from '../design/typography';
import {progress,reveal,swipe} from '../design/motion';
import {DeclicData,Platform,platformCopy} from '../archive/experiments/test-style-v2/data';

const Section:React.FC<React.PropsWithChildren<{background:string;offset:number;frame:number;step:number;tag:string}>>=({background,offset,frame,step,tag,children})=><Card background={background} y={offset}>
  <Decor frame={frame} circle={[334,154,78,.2]} sparks={[[316,106,11]]}/>
  <SafeContent offset={offset} top={64} bottom={508}>
    <SingleLine name="declic-tag" style={{...type.tag,position:'absolute',left:20,top:64,borderRadius:999,background:color.ink,padding:'6px 11px',fontSize:11,letterSpacing:'.04em'}}>LE DÉCLIC · {tag}</SingleLine>
    {children}<ChapterRail active={step} frame={frame}/>
  </SafeContent>
</Card>;

export const DeclicLesson:React.FC<{data:DeclicData;platform:Platform}>=({data,platform})=>{
  loadDesignFonts();
  const f=useCurrentFrame(),{fps}=useVideoConfig(),t=data.timing,copy=platformCopy[platform];
  const toContrast=swipe(f,t.contrast,fps),toRecall=swipe(f,t.recall,fps),toEnd=swipe(f,t.end,fps);
  const isAnswer=f>=t.answer;
  return <Stage>
    {toContrast<1?<Section background={color.lavender} offset={-640*toContrast} frame={f} step={isAnswer?1:0} tag={isAnswer?'LA RÉPONSE':'LE DÉFI'}>
      <SingleLine name="v2-title" style={{...e.title,position:'absolute',left:20,top:105,...reveal(f,0,10)}}>{isAnswer?'Le bon duo.':copy.hook}</SingleLine>
      <SingleLine name="v2-lead" style={{...e.body,position:'absolute',left:20,top:150,...reveal(f,6,8)}}>{isAnswer?'Un verbe + une expression.':copy.lead}</SingleLine>
      <LessonTicket frame={f} start={10} label={isAnswer?'01 / DÉCLIC':'01 / COMPLÈTE LA PHRASE'}>
        <SingleLine name="v2-context" style={{...e.label,position:'absolute',left:16,top:29}}>ANGLAIS DU QUOTIDIEN</SingleLine>
        <div style={{position:'absolute',left:16,top:60}}><InlineSentence frame={f} answerAt={t.answer+2} before={data.challenge.before} after={data.challenge.after} answer={data.answer} name="v2-sentence"/></div>
        <SingleLine name="v2-translation" style={{...e.translation,position:'absolute',left:16,top:105}}>{data.challenge.translation}</SingleLine>
        <CompactOptions frame={f} start={26} answerAt={t.answer+4} choices={data.choices} answer={data.answer}/>
        {f>=t.countdown&&!isAnswer?<CountdownStrip frame={f} start={t.countdown} end={t.answer}/>:null}
        {f<t.countdown?<SingleLine name="v2-prompt" style={{...e.body,position:'absolute',left:16,top:208,...reveal(f,42,8)}}>Choisis, puis dis-le à voix haute.</SingleLine>:null}
        {isAnswer?<div style={{position:'absolute',left:16,top:208,display:'flex',gap:7,alignItems:'center',...reveal(f,t.answer+18,8)}}><Icon name="check" size={17} stroke={3.4} tint={color.success}/><SingleLine name="v2-feedback" style={{...e.body,color:color.success}}>On dit : do a favor.</SingleLine></div>:null}
      </LessonTicket>
    </Section>:null}
    {f>=t.contrast&&toRecall<1?<Section background={color.lemon} offset={640*(1-toContrast)-640*toRecall} frame={f} step={1} tag="LE REPÈRE">
      <SingleLine name="contrast-title" style={{...e.title,position:'absolute',left:20,top:105}}>Deux duos utiles.</SingleLine>
      <SingleLine name="contrast-subtitle" style={{...e.body,position:'absolute',left:20,top:150}}>Des mots qui vont ensemble.</SingleLine>
      <LessonTicket frame={f} start={t.contrast+12} label="02 / DEUX DUOS À RETENIR" top={216} height={234}>
        <div style={{position:'absolute',left:16,top:30}}><PairRow frame={f} start={t.contrast+20} verb="do" noun="a favor" correct/></div>
        <div style={{position:'absolute',left:16,top:111}}><PairRow frame={f} start={t.contrast+34} verb="make" noun="a cake"/></div>
        <div style={{position:'absolute',left:16,top:99,width:248,borderTop:`1px dashed ${color.line}`}}/>
        <SingleLine name="contrast-note" style={{...type.meta,fontSize:12,position:'absolute',left:16,top:194,...reveal(f,t.contrast+48,6)}}>Apprends ces expressions en bloc.</SingleLine>
      </LessonTicket>
    </Section>:null}
    {f>=t.recall&&toEnd<1?<Section background={color.mint} offset={640*(1-toRecall)-640*toEnd} frame={f} step={2} tag="LE NOUVEL ESSAI">
      <SingleLine name="recall-title" style={{...e.title,position:'absolute',left:20,top:105}}>À toi, sans les choix.</SingleLine>
      <SingleLine name="recall-lead" style={{...e.body,position:'absolute',left:20,top:150}}>Même réflexe, autre situation.</SingleLine>
      <LessonTicket frame={f} start={t.recall+12} label="03 / RETROUVE LE VERBE">
        <SingleLine name="recall-context" style={{...e.label,position:'absolute',left:16,top:29}}>LES DEVOIRS</SingleLine>
        <div style={{position:'absolute',left:16,top:60}}><InlineSentence frame={f} answerAt={t.recallAnswer} before={data.recall.before} after={data.recall.after} answer={data.answer} name="recall-sentence"/></div>
        <SingleLine name="recall-translation" style={{...e.translation,position:'absolute',left:16,top:105}}>{data.recall.translation}</SingleLine>
        {f<t.recallAnswer?<>
          <SingleLine name="recall-instruction" style={{...e.body,position:'absolute',left:16,top:156}}>Dis la phrase complète.</SingleLine>
          <div style={{position:'absolute',left:16,top:205,width:248,height:5,background:color.track,borderRadius:999}}><div style={{height:'100%',background:color.coral,borderRadius:999,width:`${100*(1-progress(f,t.recall+30,t.recallAnswer-t.recall-30))}%`}}/></div>
        </>:<div style={{position:'absolute',left:16,top:155,...reveal(f,t.recallAnswer+8,8)}}>
          <div data-safe="recall-result" style={{...type.teaser,fontSize:26,display:'flex',gap:8,alignItems:'center',color:color.success}}><Icon name="check" size={20} stroke={3.4} tint={color.success}/>do my homework</div>
          <SingleLine name="recall-feedback" style={{...e.body,position:'absolute',left:0,top:48}}>Un nouveau duo à réutiliser.</SingleLine>
        </div>}
      </LessonTicket>
    </Section>:null}
    {f>=t.end?<Section background={color.mint} offset={640*(1-toEnd)} frame={f} step={2} tag="LE MÉMO">
      <SingleLine name="end-title-v2" style={{...e.title,fontSize:30,position:'absolute',left:20,top:110}}>{copy.end}</SingleLine>
      <SingleLine name="end-lead-v2" style={{...e.body,position:'absolute',left:20,top:156}}>{copy.cta}</SingleLine>
      <div style={{position:'absolute',left:20,top:230,width:280,padding:'22px 16px',boxSizing:'border-box',...e.panel}}>
        <SingleLine name="memo-do" style={{...type.teaser,fontSize:28,color:color.success}}>do a favor</SingleLine>
        <SingleLine name="memo-make" style={{...type.teaser,fontSize:28,marginTop:16}}>make a cake</SingleLine>
        <div style={{height:1,background:color.line,margin:'20px 0 14px'}}/>
        <SingleLine name="next-label-v2" style={{...type.meta,fontSize:12}}>Le prochain déclic</SingleLine>
        <SingleLine name="next-subject-v2" style={{...type.teaser,fontSize:25,marginTop:6}}>say ou tell ?</SingleLine>
      </div>
    </Section>:null}
  </Stage>;
};
