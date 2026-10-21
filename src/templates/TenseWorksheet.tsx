import React from 'react';
import {interpolateColors,useCurrentFrame} from 'remotion';
import {Stage,SafeContent,Icon} from '../components/LessonPrimitives';
import {WrittenText,WritingPath,WritingPen,pointOnWriting} from '../components/WrittenText';
import {color,ledge} from '../design/tokens';
import {worksheet as w} from '../design/worksheet';
import {loadDesignFonts} from '../design/typography';
import {progress,reveal} from '../design/motion';
import type {WritingEvent,TenseRow} from './worksheet-types';

type WorksheetData={title:string;columns:readonly string[];rows:readonly TenseRow[];events:readonly WritingEvent[];waits:readonly {start:number;end:number}[];futureAt:number;completeAt:number;duration:number};
export const TenseWorksheet:React.FC<{data:WorksheetData;paths:Record<string,WritingPath>}>=({data,paths})=>{
  loadDesignFonts();const f=useCurrentFrame();
  const complete=f>=data.completeAt;
  const active=data.events.find(event=>f>=event.start&&f<event.start+event.duration);
  const targetColumn=f<data.waits[0].start?0:f<data.futureAt?1:2;
  const hold=data.waits.find(wait=>f>=wait.start&&f<wait.end);
  const bg=interpolateColors(f,[data.completeAt,data.completeAt+14],[color.lavender,color.mint]);
  const pen=active?pointOnWriting(paths[active.text],progress(f,active.start,active.duration)):null;
  const activeColumn=active?w.columns[active.column]:null;
  const activeTop=active?w.rows[active.row]:0;
  const textLeft=(text:string,column:number)=>w.columns[column].center-(paths[text].inkCenter??paths[text].width/2);
  const lastPast=data.events.filter(event=>event.column===1).reduce((end,event)=>Math.max(end,event.start+event.duration),0);
  const penOpacity=active?Math.min(1,progress(f,active.start,3)*2)*(1-progress(f,active.start+active.duration-3,3)):0;
  const status=f<data.waits[0].start?'Dix verbes à compléter.':f<data.waits[0].end?'À toi de trouver le passé.':f<lastPast?'Le passé s’écrit…':f<data.futureAt?'Lis les dix réponses.':f<data.waits[1].end?'Et au futur ?':f<data.completeAt?'Le futur s’écrit…':'Le futur ici : will + verbe.';
  return <Stage>
    <div style={{position:'absolute',inset:0,background:bg}}/>
    <svg width="360" height="640" style={{position:'absolute',inset:0}} aria-hidden>
      <circle cx="338" cy="147" r="76" fill={color.sheet} opacity=".2"/>
      <path d="M316 102l3 7 7 3-7 3-3 7-3-7-7-3 7-3z" fill={color.sheet}/>
    </svg>
    <div data-center="card" style={{position:'absolute',left:w.card.left,top:w.card.top,width:w.card.width,height:w.card.height,borderRadius:w.card.radius,background:color.sheet,border:`${w.card.border}px solid ${color.ink}`,boxShadow:ledge(5,color.ink),boxSizing:'border-box',...reveal(f,4,12,14)}}>
      {Array.from({length:data.rows.length+1},(_,index)=><div key={index} style={{position:'absolute',left:w.grid.left-w.card.left-w.card.border,right:w.grid.left-w.card.left-w.card.border,top:w.grid.top-w.card.top-w.card.border+index*w.grid.rowHeight,borderTop:`1px solid ${index===0?color.line:color.lineSoft}`}}/>)}
      {w.columns.slice(1).map(column=><div key={column.x} style={{position:'absolute',left:column.x-w.card.left-w.card.border,top:w.grid.top-w.card.top-w.card.border,height:data.rows.length*w.grid.rowHeight,borderLeft:`1px solid ${color.lineSoft}`}}/>)}
      <div data-center="wait-bar" style={{position:'absolute',left:w.grid.left-w.card.left-w.card.border,bottom:8,width:w.grid.width,height:3,borderRadius:99,background:color.track,opacity:hold?1:0}}>
        <div style={{height:'100%',width:`${hold?100*(1-progress(f,hold.start,hold.end-hold.start)):0}%`,borderRadius:99,background:color.coral}}/>
      </div>
    </div>
    <SafeContent offset={0} top={64} bottom={516} right={360}>
      <div data-center="title" data-safe="worksheet-title" style={{...w.title,position:'absolute',left:0,top:82,width:360,textAlign:'center',...reveal(f,0,8,10)}}>{data.title}</div>
      {data.columns.map((label,index)=>{
        const column=w.columns[index];const fill=[color.lavender,color.lemon,color.mint][index];
        const emphasized=complete||index===targetColumn;
        return <div data-center-column={index} data-safe={`column-${index}`} key={label} style={{...w.header,position:'absolute',left:column.center-w.headers.width/2,top:w.headers.top,width:w.headers.width,height:w.headers.height,display:'flex',alignItems:'center',justifyContent:'center',borderRadius:12,border:`1.5px solid ${color.ink}`,boxSizing:'border-box',background:fill,boxShadow:ledge(emphasized?3:1,color.ink),opacity:progress(f,10+index*3,8)*(emphasized?1:.62),transform:`translateY(${emphasized?0:2}px)`}}>{label}</div>;
      })}
      {data.rows.map((row,rowIndex)=>{
        const top=w.rows[rowIndex];
        return <React.Fragment key={row.present}>
          <div data-ink-column={0} style={{position:'absolute',left:textLeft(row.present,0),top,...reveal(f,18+rowIndex*2,6)}}><WrittenText data={paths[row.present]} frame={f} start={0} duration={1} id={`present-${rowIndex}`}/></div>
          {([1,2] as const).map(column=>{
            const event=data.events.find(item=>item.row===rowIndex&&item.column===column)!;
            const x=textLeft(event.text,column),cell=w.columns[column];
            const isActive=active===event;
            return <React.Fragment key={column}>
              <div style={{position:'absolute',left:cell.x+4,top:top-1,width:cell.width-8,height:26,borderRadius:8,background:column===1?color.lemon:color.mint,opacity:isActive?.2:0}}/>
              {f<event.start?<div style={{position:'absolute',left:cell.center-9,top:top+16,width:18,height:2,borderRadius:99,background:color.line}}/>:null}
              <div data-ink-column={column} style={{position:'absolute',left:x,top}}><WrittenText data={paths[event.text]} frame={f} start={event.start} duration={event.duration} id={`answer-${rowIndex}-${column}`}/></div>
            </React.Fragment>;
          })}
        </React.Fragment>;
      })}
      <div data-center="status" style={{position:'absolute',...w.statusBox,display:'flex',alignItems:'center',justifyContent:'center',gap:6,background:complete?color.successBg:color.sheet,borderRadius:99,border:`1px solid ${complete?color.success:color.line}`,boxSizing:'border-box',...reveal(f,24,5)}}>
        {complete?<Icon name="check" size={14} stroke={3.4} tint={color.success}/>:null}
        <span data-safe="worksheet-status" style={{...w.status,color:complete?color.success:color.ink2}}>{status}</span>
      </div>
    </SafeContent>
    {active&&pen&&activeColumn?<WritingPen x={textLeft(active.text,active.column)+pen.x} y={activeTop+pen.y} frame={f} opacity={penOpacity} scale={.62}/>:null}
  </Stage>;
};
